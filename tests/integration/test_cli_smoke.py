from rdf.adapters.mock_assistant import MockAssistantAdapter
from rdf.execution.runner import DefaultRunner
from rdf.judging.llm_judge import RuleBasedJudge
from rdf.scenarios.loader import load_scenarios


def test_runner_smoke() -> None:
    scenarios = load_scenarios("scenarios/banking")
    runs = DefaultRunner(adapter=MockAssistantAdapter(), judge=RuleBasedJudge(), max_concurrency=2).run(scenarios)
    assert len(runs) == len(scenarios)
    assert all(r.judge_result is not None for r in runs)
    assert all(r.status == "completed" for r in runs)
    assert all(r.started_at_utc and r.completed_at_utc for r in runs)
    assert all(r.metadata["response_count"] == len(r.responses) for r in runs)
    assert all(r.responses[0].response_id for r in runs)
    assert all("latency_ms" in r.responses[0].metadata for r in runs)
