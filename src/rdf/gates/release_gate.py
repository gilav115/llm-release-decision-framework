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

from rdf.models import DecisionStatus, ReleaseDecision, ScenarioRun, TriggeredRule

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None


@dataclass
class PolicyRule:
    rule_id: str
    description: str
    outcome: DecisionStatus


class ReleaseGate(ABC):
    @abstractmethod
    def evaluate(self, scenario_runs: list[ScenarioRun]) -> ReleaseDecision:
        raise NotImplementedError


class DefaultReleaseGate(ReleaseGate):
    """Policy-driven gate with first rule: high-risk required failure => block."""
    SUPPORTED_RULE_IDS = {"high_risk_required_failure"}
    SUPPORTED_OUTCOMES = {"pass", "warn", "block"}

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
        raw_rules = data.get("rules")
        if not isinstance(raw_rules, list) or not raw_rules:
            raise ValueError("Gate policy must define a non-empty 'rules' list")

        rules: list[PolicyRule] = []
        for idx, item in enumerate(raw_rules):
            if not isinstance(item, dict):
                raise ValueError(f"Rule at index {idx} must be a mapping/object")

            missing = {"rule_id", "description", "outcome"} - set(item.keys())
            if missing:
                missing_fields = ", ".join(sorted(missing))
                raise ValueError(f"Rule at index {idx} missing required field(s): {missing_fields}")

            rule_id = str(item["rule_id"])
            outcome = str(item["outcome"])
            description = str(item["description"])

            if rule_id not in self.SUPPORTED_RULE_IDS:
                raise ValueError(f"Unsupported rule_id: {rule_id}")
            if outcome not in self.SUPPORTED_OUTCOMES:
                raise ValueError(f"Unsupported rule outcome: {outcome}")

            rules.append(PolicyRule(rule_id=rule_id, description=description, outcome=outcome))

        return policy_id, rules

    def _build_decision_metadata(
        self,
        scenario_runs: list[ScenarioRun],
        triggered_rules: list[TriggeredRule],
    ) -> dict[str, object]:
        total = len(scenario_runs)
        passed = sum(1 for run in scenario_runs if run.judge_result and run.judge_result.passed)
        failed = total - passed
        total_duration_ms = sum(run.duration_ms for run in scenario_runs)
        high_risk_total = sum(1 for run in scenario_runs if run.scenario.risk_level == "high")
        high_risk_failed = sum(
            1
            for run in scenario_runs
            if run.scenario.risk_level == "high" and run.judge_result and not run.judge_result.passed
        )
        return {
            "policy_id": self.policy_id,
            "scenario_count": total,
            "passed_count": passed,
            "failed_count": failed,
            "pass_rate": round((passed / total), 4) if total else 0.0,
            "high_risk_scenario_count": high_risk_total,
            "high_risk_failure_count": high_risk_failed,
            "total_duration_ms": total_duration_ms,
            "avg_duration_ms": int(total_duration_ms / total) if total else 0,
            "triggered_rule_count": len(triggered_rules),
        }

    def evaluate(self, scenario_runs: list[ScenarioRun]) -> ReleaseDecision:
        """Apply configured rules and return a final release decision."""
        errored_runs = [run for run in scenario_runs if run.metadata.get("status") == "error" or run.judge_result is None]
        if errored_runs:
            return ReleaseDecision(
                status="block",
                summary="Release blocked: one or more scenarios failed during execution.",
                triggered_rules=[
                    TriggeredRule(
                        rule_id="scenario_execution_error",
                        outcome="block",
                        reason=f"{run.scenario.scenario_id}:{run.metadata.get('error_type', 'UnknownError')}",
                    )
                    for run in errored_runs
                ],
                metadata={"policy_id": self.policy_id, "errored_scenarios": len(errored_runs)},
            )

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
                metadata=self._build_decision_metadata(scenario_runs, blocking),
            )

        all_passed = all(run.judge_result and run.judge_result.passed for run in scenario_runs)
        if all_passed:
            return ReleaseDecision(
                status="pass",
                summary="All scenarios passed under configured policy.",
                triggered_rules=[],
                metadata=self._build_decision_metadata(scenario_runs, []),
            )

        warning_rules = [
            TriggeredRule(rule_id="non_blocking_failure", outcome="warn", reason="At least one scenario failed")
        ]
        return ReleaseDecision(
            status="warn",
            summary="No blocking rule triggered, but some scenarios failed.",
            triggered_rules=warning_rules,
            metadata=self._build_decision_metadata(scenario_runs, warning_rules),
        )
