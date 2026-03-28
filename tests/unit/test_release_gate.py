from rdf.gates.release_gate import DefaultReleaseGate
from rdf.models import (
    ConversationScenario,
    ConversationTurn,
    CriterionResult,
    EvaluationCriterion,
    JudgeResult,
    ScenarioRun,
    UserProfile,
)


def _scenario() -> ConversationScenario:
    return ConversationScenario(
        scenario_id="s1",
        title="t",
        description="d",
        domain="banking",
        risk_level="high",
        user_profile=UserProfile(user_id="u", name="U", description="D"),
        turns=[ConversationTurn(turn_id="u1", speaker="user", message="hello")],
        criteria=[EvaluationCriterion(criterion_id="c1", name="correctness", description="", weight=1.0, required=True)],
    )


def test_block_on_high_risk_required_failure() -> None:
    scenario = _scenario()
    run = ScenarioRun(
        run_id="r1",
        scenario=scenario,
        transcript=[],
        responses=[],
        system_events=[],
        duration_ms=1,
        judge_result=JudgeResult(
            scenario_id="s1",
            overall_score=0.0,
            passed=False,
            reasoning="",
            criterion_results=[CriterionResult(criterion_id="c1", score=0.0, passed=False, reasoning="")],
        ),
    )
    decision = DefaultReleaseGate(policy_path="gate_policies/default_policy.yaml").evaluate([run])
    assert decision.status == "block"
    assert decision.metadata["policy_id"] == "default_v1"
