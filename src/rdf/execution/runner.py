"""Runner orchestration for scenario execution.

Educational intent:
- Show clear separation between orchestration and decision logic.
- Keep retry/timeout behavior explicit and configurable.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

from rdf.adapters.base import AssistantAdapter
from rdf.errors import AdapterExecutionError, ScenarioTimeoutError
from rdf.judging.base import Judge
from rdf.models import AssistantResponse, ConversationScenario, ConversationTurn, ScenarioRun


class Runner(ABC):
    @abstractmethod
    def run(self, scenarios: list[ConversationScenario]) -> list[ScenarioRun]:
        raise NotImplementedError


class DefaultRunner(Runner):
    """Bounded-concurrency runner with timeout and retry controls."""

    def __init__(
        self,
        adapter: AssistantAdapter,
        judge: Judge,
        max_concurrency: int = 4,
        scenario_timeout_sec: float = 30.0,
        max_retries: int = 1,
    ):
        self.adapter = adapter
        self.judge = judge
        self.max_concurrency = max_concurrency
        self.scenario_timeout_sec = scenario_timeout_sec
        self.max_retries = max_retries

    def _send_turn_with_timeout(
        self,
        context: object,
        turn: ConversationTurn,
        remaining_sec: float,
        scenario_id: str,
    ) -> AssistantResponse:
        """Execute adapter turn call with a hard timeout boundary.

        We run adapter calls in a daemon thread so a blocked provider call
        cannot stall scenario execution forever.
        """
        if remaining_sec <= 0:
            raise ScenarioTimeoutError(
                f"Scenario {scenario_id} exceeded timeout of {self.scenario_timeout_sec}s"
            )

        outcome: Queue[tuple[str, object]] = Queue(maxsize=1)

        def _worker() -> None:
            try:
                response = self.adapter.send_turn(context, turn)
            except Exception as exc:  # pragma: no cover - behavior asserted via caller.
                outcome.put(("error", exc))
                return
            outcome.put(("ok", response))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        thread.join(timeout=remaining_sec)

        if thread.is_alive():
            raise ScenarioTimeoutError(
                f"Scenario {scenario_id} exceeded timeout of {self.scenario_timeout_sec}s"
            )

        status, payload = outcome.get()
        if status == "error":
            raise payload  # type: ignore[misc]
        return payload  # type: ignore[return-value]

    def _run_single(self, run_id: str, scenario: ConversationScenario) -> ScenarioRun:
        """Execute one scenario exactly once (no retries)."""
        start = time.perf_counter()
        context: object | None = None
        primary_exc: Exception | None = None
        try:
            context = self.adapter.start_conversation(scenario)
            transcript: list[ConversationTurn] = []
            responses = []

            for turn in scenario.turns:
                elapsed = time.perf_counter() - start
                if elapsed > self.scenario_timeout_sec:
                    raise ScenarioTimeoutError(
                        f"Scenario {scenario.scenario_id} exceeded timeout of {self.scenario_timeout_sec}s"
                    )

                transcript.append(turn)
                remaining = self.scenario_timeout_sec - elapsed
                response = self._send_turn_with_timeout(
                    context=context,
                    turn=turn,
                    remaining_sec=remaining,
                    scenario_id=scenario.scenario_id,
                )
                responses.append(response)

                # We capture assistant messages as synthetic transcript turns so
                # judges and reports can reason over full conversation history.
                transcript.append(
                    ConversationTurn(
                        turn_id=f"assistant_{turn.turn_id}",
                        speaker="assistant",
                        message=response.message,
                    )
                )

            events = self.adapter.collect_system_events(context)
            judge_result = self.judge.evaluate(scenario, transcript, responses, events)
            duration_ms = int((time.perf_counter() - start) * 1000)

            return ScenarioRun(
                run_id=run_id,
                scenario=scenario,
                transcript=transcript,
                responses=responses,
                system_events=events,
                duration_ms=duration_ms,
                judge_result=judge_result,
                metadata={"attempt": 1},
            )
        except ScenarioTimeoutError as exc:
            primary_exc = exc
            raise
        except Exception as exc:
            primary_exc = exc
            raise AdapterExecutionError(f"Scenario {scenario.scenario_id} failed during execution") from exc
        finally:
            if context is not None:
                try:
                    self.adapter.end_conversation(context)
                except Exception as exc:
                    if primary_exc is None:
                        raise AdapterExecutionError(
                            f"Scenario {scenario.scenario_id} failed during cleanup"
                        ) from exc

    def _run_with_retries(self, run_id: str, scenario: ConversationScenario) -> ScenarioRun:
        """Retry transient adapter failures up to `max_retries` times."""
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 2):
            try:
                run = self._run_single(run_id, scenario)
                run.metadata["attempt"] = attempt
                return run
            except ScenarioTimeoutError as exc:
                # Timeout is treated as terminal for determinism and faster feedback.
                last_exc = exc
                break
            except AdapterExecutionError as exc:
                last_exc = exc
                if attempt > self.max_retries:
                    break
        assert last_exc is not None
        raise last_exc

    def run(self, scenarios: list[ConversationScenario]) -> list[ScenarioRun]:
        """Run scenarios in parallel with bounded worker count."""
        run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        results: list[ScenarioRun] = []
        with ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
            futures = [executor.submit(self._run_with_retries, run_id, s) for s in scenarios]
            for future in as_completed(futures):
                results.append(future.result())
        return sorted(results, key=lambda r: r.scenario.scenario_id)
