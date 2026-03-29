"""Human-readable report construction."""

from __future__ import annotations

from rdf.models import ReleaseDecision, ScenarioRun


class ReportBuilder:
    """Builds short markdown summaries for fast release review."""

    def build_summary_markdown(self, scenario_runs: list[ScenarioRun], decision: ReleaseDecision) -> str:
        """Create one-page style summary with key release metrics."""
        total = len(scenario_runs)
        passed = sum(1 for r in scenario_runs if r.judge_result and r.judge_result.passed)
        failed = total - passed
        high_risk_failed = sum(
            1
            for r in scenario_runs
            if r.scenario.risk_level == "high" and r.judge_result and not r.judge_result.passed
        )
        pass_rate = (passed / total) if total else 0.0
        total_duration_ms = sum(r.duration_ms for r in scenario_runs)
        avg_duration_ms = int(total_duration_ms / total) if total else 0
        slowest = max(scenario_runs, key=lambda run: run.duration_ms, default=None)

        lines = [
            "# Release Decision Summary",
            "",
            "## Outcome",
            "",
            f"- Final decision: **{decision.status}**",
            f"- Summary: {decision.summary}",
            f"- Policy: `{decision.metadata.get('policy_id', 'unknown')}`",
            f"- Scenarios evaluated: {total}",
            f"- Passed: {passed}",
            f"- Failed: {failed}",
            f"- Pass rate: {pass_rate:.1%}",
            f"- High-risk failures: {high_risk_failed}",
            "",
            "## Timing",
            "",
            f"- Total runtime across scenarios: {total_duration_ms} ms",
            f"- Average scenario duration: {avg_duration_ms} ms",
            f"- Slowest scenario: `{slowest.scenario.scenario_id}` ({slowest.duration_ms} ms)" if slowest else "- Slowest scenario: n/a",
        ]

        if decision.triggered_rules:
            lines.extend(["", "## Triggered Rules", ""])
            for rule in decision.triggered_rules:
                lines.append(f"- `{rule.rule_id}` ({rule.outcome}): {rule.reason}")

        lines.extend(["", "## Scenario Results", "", "| Scenario | Risk | Status | Score | Duration | Attempt | Response Source |", "| --- | --- | --- | --- | --- | --- | --- |"])
        for run in scenario_runs:
            judge_status = "pass" if run.judge_result and run.judge_result.passed else "fail"
            score = f"{run.judge_result.overall_score:.2f}" if run.judge_result else "n/a"
            attempt = run.metadata.get("attempt", "n/a")
            response_source = run.metadata.get("adapter_name", "unknown")
            lines.append(
                f"| `{run.scenario.scenario_id}` | {run.scenario.risk_level} | {judge_status} | "
                f"{score} | {run.duration_ms} ms | {attempt} | {response_source} |"
            )
        return "\n".join(lines)
