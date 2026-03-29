"""Human-readable report construction."""

from __future__ import annotations

import math

from rdf.models import ReleaseDecision, ScenarioRun


class ReportBuilder:
    """Builds short markdown summaries for fast release review."""

    @staticmethod
    def _percent(numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return (numerator / denominator) * 100.0

    @staticmethod
    def _duration_stats(values_ms: list[int]) -> dict[str, float]:
        if not values_ms:
            return {"count": 0, "avg_ms": 0.0, "p50_ms": 0.0, "p95_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0}

        ordered = sorted(values_ms)
        count = len(ordered)
        p50_idx = int(math.ceil(0.50 * count)) - 1
        p95_idx = int(math.ceil(0.95 * count)) - 1
        return {
            "count": count,
            "avg_ms": round(sum(ordered) / count, 2),
            "p50_ms": float(ordered[max(0, p50_idx)]),
            "p95_ms": float(ordered[max(0, p95_idx)]),
            "min_ms": float(ordered[0]),
            "max_ms": float(ordered[-1]),
        }

    def build_run_stats(
        self,
        scenario_runs: list[ScenarioRun],
        run_errors: list[dict] | None = None,
        total_execution_ms: int | None = None,
    ) -> dict:
        run_errors = run_errors or []
        load_errors = [e for e in run_errors if e.get("stage") == "load"]
        execution_errors = [e for e in run_errors if e.get("stage") == "execution"]

        loaded_scenarios = len(scenario_runs)
        total_inputs = loaded_scenarios + len(load_errors)

        passed = sum(1 for r in scenario_runs if r.judge_result and r.judge_result.passed)
        failed = sum(1 for r in scenario_runs if r.judge_result and not r.judge_result.passed)
        errored = sum(1 for r in scenario_runs if r.metadata.get("status") == "error")

        scenario_durations_ms = [int(r.duration_ms) for r in scenario_runs]
        turn_durations_ms: list[int] = []
        for run in scenario_runs:
            raw = run.metadata.get("turn_durations_ms", [])
            if isinstance(raw, list):
                turn_durations_ms.extend(int(v) for v in raw if isinstance(v, (int, float)))

        total_execution_sec = (total_execution_ms or 0) / 1000 if total_execution_ms else 0.0
        scenarios_per_sec = (loaded_scenarios / total_execution_sec) if total_execution_sec > 0 else 0.0
        turns_per_sec = (len(turn_durations_ms) / total_execution_sec) if total_execution_sec > 0 else 0.0

        return {
            "counts": {
                "scenario_inputs_total": total_inputs,
                "scenarios_loaded": loaded_scenarios,
                "load_errors": len(load_errors),
                "scenarios_passed": passed,
                "scenarios_failed": failed,
                "scenarios_errored": errored,
                "execution_errors": len(execution_errors),
                "turns_executed": len(turn_durations_ms),
            },
            "rates": {
                "success_rate_loaded_pct": round(self._percent(passed, loaded_scenarios), 2),
                "failure_rate_loaded_pct": round(self._percent(failed + errored, loaded_scenarios), 2),
                "load_error_rate_input_pct": round(self._percent(len(load_errors), total_inputs), 2),
                "scenarios_per_second": round(scenarios_per_sec, 4),
                "turns_per_second": round(turns_per_sec, 4),
            },
            "performance": {
                "total_execution_ms": int(total_execution_ms or 0),
                "scenario_execution_ms": self._duration_stats(scenario_durations_ms),
                "question_execution_ms": self._duration_stats(turn_durations_ms),
            },
        }

    def build_summary_markdown(
        self,
        scenario_runs: list[ScenarioRun],
        decision: ReleaseDecision,
        run_errors: list[dict] | None = None,
        total_execution_ms: int | None = None,
    ) -> str:
        """Create one-page style summary with key release metrics."""
        run_errors = run_errors or []
        stats = self.build_run_stats(
            scenario_runs=scenario_runs,
            run_errors=run_errors,
            total_execution_ms=total_execution_ms,
        )
        total = len(scenario_runs)
        passed = stats["counts"]["scenarios_passed"]
        failed = stats["counts"]["scenarios_failed"]
        high_risk_failed = sum(
            1
            for r in scenario_runs
            if r.scenario.risk_level == "high" and r.judge_result and not r.judge_result.passed
        )
        pass_rate = stats["rates"]["success_rate_loaded_pct"] / 100 if total else 0.0
        total_duration_ms = stats["performance"]["total_execution_ms"] or sum(r.duration_ms for r in scenario_runs)
        avg_duration_ms = int(stats["performance"]["scenario_execution_ms"]["avg_ms"]) if total else 0
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
            f"- Total runtime across scenarios: {int(total_duration_ms)} ms",
            f"- Average scenario duration: {avg_duration_ms} ms",
            f"- Slowest scenario: `{slowest.scenario.scenario_id}` ({slowest.duration_ms} ms)" if slowest else "- Slowest scenario: n/a",
            "",
            "## Rates",
            "",
            f"- Scenario success rate: {stats['rates']['success_rate_loaded_pct']:.2f}%",
            f"- Scenario failure rate: {stats['rates']['failure_rate_loaded_pct']:.2f}%",
            f"- Load error rate: {stats['rates']['load_error_rate_input_pct']:.2f}%",
            f"- Scenarios per second: {stats['rates']['scenarios_per_second']:.4f}",
            f"- Turns per second: {stats['rates']['turns_per_second']:.4f}",
            "",
            "## Performance",
            "",
            f"- Scenario duration p50: {stats['performance']['scenario_execution_ms']['p50_ms']:.0f} ms",
            f"- Scenario duration p95: {stats['performance']['scenario_execution_ms']['p95_ms']:.0f} ms",
            f"- Turn duration p50: {stats['performance']['question_execution_ms']['p50_ms']:.0f} ms",
            f"- Turn duration p95: {stats['performance']['question_execution_ms']['p95_ms']:.0f} ms",
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
