import time

from rdf.adapters.base import AssistantAdapter
from rdf.errors import AdapterExecutionError, ScenarioTimeoutError
from rdf.execution.runner import DefaultRunner
from rdf.judging.llm_judge import RuleBasedJudge
from rdf.models import AssistantResponse, ConversationScenario, ConversationTurn, EvaluationCriterion, UserProfile


class FlakyAdapter(AssistantAdapter):
    def __init__(self) -> None:
        self.calls = 0

    def start_conversation(self, scenario: ConversationScenario):
        return {}

    def send_turn(self, context, turn: ConversationTurn) -> AssistantResponse:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("temporary infra failure")
        return AssistantResponse(message="safe response")

    def end_conversation(self, context) -> None:
        return None


class HangingAdapter(AssistantAdapter):
    def start_conversation(self, scenario: ConversationScenario):
        return {}

    def send_turn(self, context, turn: ConversationTurn) -> AssistantResponse:
        time.sleep(0.5)
        return AssistantResponse(message="late response")

    def end_conversation(self, context) -> None:
        return None


class CleanupTrackingAdapter(AssistantAdapter):
    def __init__(self) -> None:
        self.ended = False

    def start_conversation(self, scenario: ConversationScenario):
        return {}

    def send_turn(self, context, turn: ConversationTurn) -> AssistantResponse:
        raise RuntimeError("send failure")

    def end_conversation(self, context) -> None:
        self.ended = True


def _scenario() -> ConversationScenario:
    return ConversationScenario(
        scenario_id="s_retry",
        title="retry",
        description="retry test",
        domain="banking",
        risk_level="low",
        user_profile=UserProfile(user_id="u", name="n", description="d"),
        turns=[ConversationTurn(turn_id="u1", speaker="user", message="hello")],
        criteria=[EvaluationCriterion(criterion_id="c1", name="clarity", description="", weight=1.0, required=True)],
    )


def test_runner_retries_adapter_failure() -> None:
    adapter = FlakyAdapter()
    runner = DefaultRunner(adapter=adapter, judge=RuleBasedJudge(), max_retries=1, scenario_timeout_sec=10)
    runs = runner.run([_scenario()])
    assert len(runs) == 1
    assert runs[0].metadata["attempt"] == 2


def test_runner_raises_when_retries_exhausted() -> None:
    adapter = FlakyAdapter()
    runner = DefaultRunner(adapter=adapter, judge=RuleBasedJudge(), max_retries=0, scenario_timeout_sec=10)
    try:
        runner.run([_scenario()])
        assert False, "Expected AdapterExecutionError"
    except AdapterExecutionError:
        assert True


def test_runner_times_out_blocking_turn_call() -> None:
    adapter = HangingAdapter()
    runner = DefaultRunner(adapter=adapter, judge=RuleBasedJudge(), max_retries=0, scenario_timeout_sec=0.1)
    try:
        runner.run([_scenario()])
        assert False, "Expected ScenarioTimeoutError"
    except ScenarioTimeoutError:
        assert True


def test_runner_always_calls_end_conversation_on_failure() -> None:
    adapter = CleanupTrackingAdapter()
    runner = DefaultRunner(adapter=adapter, judge=RuleBasedJudge(), max_retries=0, scenario_timeout_sec=10)
    try:
        runner.run([_scenario()])
        assert False, "Expected AdapterExecutionError"
    except AdapterExecutionError:
        assert adapter.ended is True
