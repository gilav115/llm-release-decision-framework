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
        total = len(scenario_runs)
        high_risk_failed = sum(
            1
            for r in scenario_runs
            if r.scenario.risk_level == "high" and r.judge_result and not r.judge_result.passed
        )
        stats = self.build_run_stats(
            scenario_runs=scenario_runs,
            run_errors=run_errors,
            total_execution_ms=total_execution_ms,
        )
        counts = stats["counts"]
        rates = stats["rates"]
        perf = stats["performance"]
        scenario_perf = perf["scenario_execution_ms"]
        question_perf = perf["question_execution_ms"]

        lines = [
            "# Release Decision Summary",
            "",
            f"- Scenarios evaluated: {total}",
            f"- Passed: {counts['scenarios_passed']}",
            f"- Failed: {counts['scenarios_failed']}",
            f"- Errored: {counts['scenarios_errored']}",
            f"- Load errors: {counts['load_errors']}",
            f"- High-risk failures: {high_risk_failed}",
            "",
            "## Rates",
            f"- Success rate (loaded scenarios): {rates['success_rate_loaded_pct']}%",
            f"- Failure rate (loaded scenarios): {rates['failure_rate_loaded_pct']}%",
            f"- Load error rate (all scenario inputs): {rates['load_error_rate_input_pct']}%",
            f"- Scenario throughput: {rates['scenarios_per_second']} scenarios/sec",
            f"- Question throughput: {rates['turns_per_second']} questions/sec",
            "",
            "## Performance",
            f"- Total execution time: {perf['total_execution_ms']} ms",
            f"- Conversation execution (avg/p50/p95): {scenario_perf['avg_ms']} / {scenario_perf['p50_ms']} / {scenario_perf['p95_ms']} ms",
            f"- Question execution (avg/p50/p95): {question_perf['avg_ms']} / {question_perf['p50_ms']} / {question_perf['p95_ms']} ms",
            f"- Final decision: **{decision.status}**",
            f"- Summary: {decision.summary}",
        ]
        return "\n".join(lines)
