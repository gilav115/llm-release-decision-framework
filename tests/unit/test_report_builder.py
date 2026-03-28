from rdf.models import (
    ConversationScenario,
    ConversationTurn,
    CriterionResult,
    EvaluationCriterion,
    JudgeResult,
    ReleaseDecision,
    ScenarioRun,
    UserProfile,
)
from rdf.reporting.report_builder import ReportBuilder


def _scenario(scenario_id: str) -> ConversationScenario:
    return ConversationScenario(
        scenario_id=scenario_id,
        title="t",
        description="d",
        domain="banking",
        risk_level="low",
        user_profile=UserProfile(user_id="u", name="n", description="d"),
        turns=[ConversationTurn(turn_id="u1", speaker="user", message="hello")],
        criteria=[EvaluationCriterion(criterion_id="c1", name="clarity", description="", weight=1.0, required=True)],
    )


def test_build_run_stats_includes_performance_and_rates() -> None:
    passed_run = ScenarioRun(
        run_id="r1",
        scenario=_scenario("s1"),
        transcript=[],
        responses=[],
        system_events=[],
        duration_ms=100,
        judge_result=JudgeResult(
            scenario_id="s1",
            overall_score=1.0,
            passed=True,
            reasoning="",
            criterion_results=[CriterionResult(criterion_id="c1", score=1.0, passed=True, reasoning="")],
        ),
        metadata={"status": "completed", "turn_durations_ms": [50]},
    )
    failed_run = ScenarioRun(
        run_id="r1",
        scenario=_scenario("s2"),
        transcript=[],
        responses=[],
        system_events=[],
        duration_ms=200,
        judge_result=JudgeResult(
            scenario_id="s2",
            overall_score=0.0,
            passed=False,
            reasoning="",
            criterion_results=[CriterionResult(criterion_id="c1", score=0.0, passed=False, reasoning="")],
        ),
        metadata={"status": "completed", "turn_durations_ms": [70]},
    )
    error_run = ScenarioRun(
        run_id="r1",
        scenario=_scenario("s3"),
        transcript=[],
        responses=[],
        system_events=[],
        duration_ms=300,
        judge_result=None,
        metadata={"status": "error", "error_type": "ScenarioTimeoutError", "turn_durations_ms": []},
    )

    builder = ReportBuilder()
    stats = builder.build_run_stats(
        scenario_runs=[passed_run, failed_run, error_run],
        run_errors=[{"stage": "load", "file": "bad.yaml", "error_message": "bad"}],
        total_execution_ms=1000,
    )

    assert stats["counts"]["scenarios_loaded"] == 3
    assert stats["counts"]["load_errors"] == 1
    assert stats["counts"]["scenarios_passed"] == 1
    assert stats["counts"]["scenarios_failed"] == 1
    assert stats["counts"]["scenarios_errored"] == 1
    assert stats["performance"]["scenario_execution_ms"]["count"] == 3
    assert stats["performance"]["question_execution_ms"]["count"] == 2


def test_summary_includes_stats_sections() -> None:
    run = ScenarioRun(
        run_id="r1",
        scenario=_scenario("s1"),
        transcript=[],
        responses=[],
        system_events=[],
        duration_ms=100,
        judge_result=JudgeResult(
            scenario_id="s1",
            overall_score=1.0,
            passed=True,
            reasoning="",
            criterion_results=[CriterionResult(criterion_id="c1", score=1.0, passed=True, reasoning="")],
        ),
        metadata={"status": "completed", "turn_durations_ms": [60]},
    )
    decision = ReleaseDecision(status="pass", summary="ok", triggered_rules=[], metadata={})
    markdown = ReportBuilder().build_summary_markdown([run], decision, run_errors=[], total_execution_ms=200)

    assert "## Rates" in markdown
    assert "## Performance" in markdown
