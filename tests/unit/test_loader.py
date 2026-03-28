import pytest

from rdf.errors import ScenarioValidationError
from rdf.scenarios.loader import load_scenarios, load_scenarios_with_errors


def test_load_scenarios_from_banking_dir() -> None:
    scenarios = load_scenarios("scenarios/banking")
    assert len(scenarios) >= 2
    ids = {s.scenario_id for s in scenarios}
    assert "banking_transfer_fee_001" in ids
    assert "banking_blocked_card_001" in ids


def test_load_scenarios_raises_when_no_yaml_files(tmp_path) -> None:
    with pytest.raises(ScenarioValidationError, match="No scenario files found"):
        load_scenarios(tmp_path)


def test_load_scenarios_with_errors_collects_invalid_files(tmp_path) -> None:
    good = tmp_path / "good.yaml"
    bad = tmp_path / "bad.yaml"
    good.write_text(
        """
{
  "scenario_id": "s1",
  "title": "t",
  "description": "d",
  "domain": "banking",
  "risk_level": "low",
  "user_profile": {"user_id": "u", "name": "n", "description": "d"},
  "turns": [{"turn_id": "u1", "speaker": "user", "message": "hello"}],
  "criteria": [{"criterion_id": "c1", "name": "clarity", "description": "d", "weight": 1.0}]
}
        """.strip()
    )
    bad.write_text("{ not valid json }")

    scenarios, errors = load_scenarios_with_errors(tmp_path)
    assert len(scenarios) == 1
    assert len(errors) == 1
    assert errors[0]["stage"] == "load"
