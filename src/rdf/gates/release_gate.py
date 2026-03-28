"""Policy-driven release gate.

Educational intent:
- Keep gate logic easy to inspect and reason about.
- Make policy effects explicit through triggered rules.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from rdf.models import ReleaseDecision, ScenarioRun, TriggeredRule

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None


@dataclass
class PolicyRule:
    rule_id: str
    description: str
    outcome: str


class ReleaseGate(ABC):
    @abstractmethod
    def evaluate(self, scenario_runs: list[ScenarioRun]) -> ReleaseDecision:
        raise NotImplementedError


class DefaultReleaseGate(ReleaseGate):
    """Policy-driven gate with first rule: high-risk required failure => block."""

    def __init__(self, policy_path: str = "gate_policies/default_policy.yaml") -> None:
        self.policy_path = policy_path
        self.policy_id, self.rules = self._load_policy(policy_path)

    def _load_policy(self, policy_path: str) -> tuple[str, list[PolicyRule]]:
        """Load policy from YAML (or JSON-formatted YAML fallback)."""
        raw = Path(policy_path).read_text()
        data = yaml.safe_load(raw) if yaml is not None else json.loads(raw)

        if not isinstance(data, dict):
            raise ValueError("Gate policy must be a mapping/object")

        policy_id = str(data.get("policy_id", "default_v1"))
        rules = [PolicyRule(**item) for item in data.get("rules", [])]
        return policy_id, rules

    def evaluate(self, scenario_runs: list[ScenarioRun]) -> ReleaseDecision:
        """Apply configured rules and return a final release decision."""
        triggered: list[TriggeredRule] = []

        for rule in self.rules:
            if rule.rule_id == "high_risk_required_failure":
                for run in scenario_runs:
                    if run.judge_result is None or run.scenario.risk_level != "high":
                        continue
                    for result in run.judge_result.criterion_results:
                        criterion = next(c for c in run.scenario.criteria if c.criterion_id == result.criterion_id)
                        if criterion.required and not result.passed:
                            triggered.append(
                                TriggeredRule(
                                    rule_id=rule.rule_id,
                                    outcome=rule.outcome,
                                    reason=f"{run.scenario.scenario_id}:{criterion.criterion_id}",
                                )
                            )

        blocking = [t for t in triggered if t.outcome == "block"]
        if blocking:
            return ReleaseDecision(
                status="block",
                summary="Release blocked by policy rule trigger(s).",
                triggered_rules=blocking,
                metadata={"policy_id": self.policy_id},
            )

        all_passed = all(run.judge_result and run.judge_result.passed for run in scenario_runs)
        if all_passed:
            return ReleaseDecision(
                status="pass",
                summary="All scenarios passed under configured policy.",
                triggered_rules=[],
                metadata={"policy_id": self.policy_id},
            )

        return ReleaseDecision(
            status="warn",
            summary="No blocking rule triggered, but some scenarios failed.",
            triggered_rules=[
                TriggeredRule(rule_id="non_blocking_failure", outcome="warn", reason="At least one scenario failed")
            ],
            metadata={"policy_id": self.policy_id},
        )
