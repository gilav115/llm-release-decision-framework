"""Scenario loading and validation.

Educational intent:
- Keep parsing logic easy to read.
- Keep validation explicit and localized.
- Make error messages actionable for scenario authors.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rdf.errors import ScenarioValidationError
from rdf.models import ConversationScenario, ConversationTurn, EvaluationCriterion, UserProfile

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None


def _parse_structured_text(raw: str) -> dict[str, Any]:
    """Parse YAML when available, otherwise parse JSON-formatted YAML.

    Note:
    JSON is a valid subset of YAML, so demo files can remain portable.
    """
    if yaml is not None:
        data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            raise ScenarioValidationError("Scenario file must contain a mapping/object at root")
        return data

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ScenarioValidationError(
            "PyYAML is not installed, and scenario content is not JSON-compatible YAML."
        ) from exc
    if not isinstance(data, dict):
        raise ScenarioValidationError("Scenario file must contain a mapping/object at root")
    return data


def _validate_unique(items: list[str], label: str) -> None:
    """Ensure identifiers are unique within their scope."""
    if len(items) != len(set(items)):
        raise ScenarioValidationError(f"Duplicate {label} values detected")


def _from_dict(data: dict[str, Any]) -> ConversationScenario:
    """Convert validated raw dictionary into typed scenario model."""
    turns = [ConversationTurn(**t) for t in data.get("turns", [])]
    criteria = [EvaluationCriterion(**c) for c in data.get("criteria", [])]

    if not turns:
        raise ScenarioValidationError("Scenario must contain at least one turn")
    if not criteria:
        raise ScenarioValidationError("Scenario must contain at least one criterion")

    _validate_unique([t.turn_id for t in turns], "turn_id")
    _validate_unique([c.criterion_id for c in criteria], "criterion_id")

    for c in criteria:
        if not (0.0 <= c.weight <= 1.0):
            raise ScenarioValidationError(f"Criterion weight out of range [0,1]: {c.criterion_id}")

    return ConversationScenario(
        scenario_id=data["scenario_id"],
        title=data["title"],
        description=data["description"],
        domain=data["domain"],
        risk_level=data["risk_level"],
        user_profile=UserProfile(**data["user_profile"]),
        turns=turns,
        criteria=criteria,
        expected_behaviour_notes=data.get("expected_behaviour_notes", ""),
        tags=data.get("tags", []),
        metadata=data.get("metadata", {}),
    )


def load_scenarios(path: str | Path) -> list[ConversationScenario]:
    """Load and validate all `.yaml` scenarios under a directory tree."""
    root = Path(path)
    files = sorted(root.rglob("*.yaml"))
    if not files:
        raise ScenarioValidationError(f"No scenario files found under: {root}")

    scenarios: list[ConversationScenario] = []
    seen_ids: set[str] = set()

    for file in files:
        payload = _parse_structured_text(file.read_text())
        scenario = _from_dict(payload)
        if scenario.scenario_id in seen_ids:
            raise ScenarioValidationError(f"Duplicate scenario_id: {scenario.scenario_id}")
        seen_ids.add(scenario.scenario_id)
        scenarios.append(scenario)

    return scenarios
