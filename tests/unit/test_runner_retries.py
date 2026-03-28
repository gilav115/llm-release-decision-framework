from rdf.adapters.base import AssistantAdapter
from rdf.errors import AdapterExecutionError
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
