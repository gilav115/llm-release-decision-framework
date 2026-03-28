import pytest

from rdf.errors import ScenarioValidationError
from rdf.scenarios.loader import load_scenarios


def test_load_scenarios_from_banking_dir() -> None:
    scenarios = load_scenarios("scenarios/banking")
    assert len(scenarios) >= 2
    ids = {s.scenario_id for s in scenarios}
    assert "banking_transfer_fee_001" in ids
    assert "banking_blocked_card_001" in ids


def test_load_scenarios_raises_when_no_yaml_files(tmp_path) -> None:
    with pytest.raises(ScenarioValidationError, match="No scenario files found"):
        load_scenarios(tmp_path)
