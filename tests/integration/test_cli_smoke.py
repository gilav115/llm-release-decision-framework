from rdf.adapters.mock_assistant import MockAssistantAdapter
from rdf.execution.runner import DefaultRunner
from rdf.judging.llm_judge import RuleBasedJudge
from rdf.scenarios.loader import load_scenarios


def test_runner_smoke() -> None:
    scenarios = load_scenarios("scenarios/banking")
    runs = DefaultRunner(adapter=MockAssistantAdapter(), judge=RuleBasedJudge(), max_concurrency=2).run(scenarios)
    assert len(runs) == len(scenarios)
    assert all(r.judge_result is not None for r in runs)
