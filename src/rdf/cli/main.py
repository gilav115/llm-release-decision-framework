"""CLI entrypoint for demo evaluation runs.

The CLI is orchestration-only by design: it wires components together,
executes a run, and writes artifacts. It does not contain decision logic.
"""

from __future__ import annotations

import argparse
import time

from rdf.adapters.mock_assistant import MockAssistantAdapter
from rdf.execution.runner import DefaultRunner
from rdf.gates.release_gate import DefaultReleaseGate
from rdf.judging.llm_judge import RuleBasedJudge
from rdf.models import ReleaseDecision, TriggeredRule
from rdf.reporting.report_builder import ReportBuilder
from rdf.scenarios.loader import load_scenarios_with_errors
from rdf.storage.filesystem import FilesystemStorage


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return parsed


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be zero or greater")
    return parsed


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def parse_args() -> argparse.Namespace:
    """Parse runtime configuration for an evaluation run."""
    parser = argparse.ArgumentParser(description="Release Decision Framework CLI")
    parser.add_argument("--scenarios", default="scenarios", help="Scenario directory")
    parser.add_argument("--output", default="run_history", help="Run history output directory")
    parser.add_argument("--policy", default="gate_policies/default_policy.yaml", help="Policy file path")
    parser.add_argument("--max-concurrency", type=_positive_int, default=4)
    parser.add_argument("--scenario-timeout-sec", type=_positive_float, default=30.0)
    parser.add_argument("--max-retries", type=_non_negative_int, default=1)
    return parser.parse_args()


def main() -> None:
    run_started = time.perf_counter()
    args = parse_args()

    # 1) Load scenarios from disk in tolerant mode.
    scenarios, load_errors = load_scenarios_with_errors(args.scenarios)

    # 2) Build execution stack (adapter + judge + runner).
    adapter = MockAssistantAdapter()
    judge = RuleBasedJudge()
    runner = DefaultRunner(
        adapter=adapter,
        judge=judge,
        max_concurrency=args.max_concurrency,
        scenario_timeout_sec=args.scenario_timeout_sec,
        max_retries=args.max_retries,
    )

    # 3) Execute scenarios.
    scenario_runs = runner.run(scenarios)
    execution_errors = [
        {
            "stage": "execution",
            "scenario_id": run.scenario.scenario_id,
            "error_type": run.metadata.get("error_type", "UnknownError"),
            "error_message": run.metadata.get("error_message", ""),
            "attempt": run.metadata.get("attempt", 1),
        }
        for run in scenario_runs
        if run.metadata.get("status") == "error"
    ]
    run_errors = [*load_errors, *execution_errors]

    # 4) Evaluate release gate.
    gate = DefaultReleaseGate(policy_path=args.policy)
    decision = gate.evaluate(scenario_runs)
    if load_errors:
        load_trigger = TriggeredRule(
            rule_id="scenario_load_error",
            outcome="block",
            reason=f"{len(load_errors)} scenario file(s) failed to load",
        )
        if decision.status == "block":
            decision.triggered_rules.append(load_trigger)
            decision.summary = f"{decision.summary} Scenario load errors detected."
            decision.metadata["load_errors"] = len(load_errors)
        else:
            decision = ReleaseDecision(
                status="block",
                summary="Release blocked: one or more scenario files failed to load.",
                triggered_rules=[load_trigger],
                metadata={**decision.metadata, "load_errors": len(load_errors)},
            )

    # 5) Build human-readable summary.
    builder = ReportBuilder()
    total_execution_ms = int((time.perf_counter() - run_started) * 1000)
    run_stats = builder.build_run_stats(
        scenario_runs=scenario_runs,
        run_errors=run_errors,
        total_execution_ms=total_execution_ms,
    )
    summary = builder.build_summary_markdown(
        scenario_runs,
        decision,
        run_errors=run_errors,
        total_execution_ms=total_execution_ms,
    )

    # 6) Persist run artifacts.
    storage = FilesystemStorage()
    run_dir = storage.create_run_dir(args.output)
    storage.write_run_artifacts(
        run_dir=run_dir,
        run_config={
            "scenario_path": args.scenarios,
            "policy_path": args.policy,
            "max_concurrency": args.max_concurrency,
            "scenario_timeout_sec": args.scenario_timeout_sec,
            "max_retries": args.max_retries,
            "adapter": adapter.__class__.__name__,
            "judge": judge.__class__.__name__,
            "runner": runner.__class__.__name__,
        },
        scenario_runs=scenario_runs,
        release_decision=decision,
        summary_markdown=summary,
        run_errors=run_errors,
        run_stats=run_stats,
    )

    print(f"Run complete. Decision: {decision.status}")
    print(f"Artifacts: {run_dir}")


if __name__ == "__main__":
    main()
