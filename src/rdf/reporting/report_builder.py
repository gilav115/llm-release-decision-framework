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

        lines = [
            "# Release Decision Summary",
            "",
            f"- Scenarios evaluated: {total}",
            f"- Passed: {passed}",
            f"- Failed: {failed}",
            f"- High-risk failures: {high_risk_failed}",
            f"- Final decision: **{decision.status}**",
            f"- Summary: {decision.summary}",
        ]
        return "\n".join(lines)
