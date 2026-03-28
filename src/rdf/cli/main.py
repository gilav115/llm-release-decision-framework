"""CLI entrypoint for demo evaluation runs.

The CLI is orchestration-only by design: it wires components together,
executes a run, and writes artifacts. It does not contain decision logic.
"""

from __future__ import annotations

import argparse

from rdf.adapters.mock_assistant import MockAssistantAdapter
from rdf.execution.runner import DefaultRunner
from rdf.gates.release_gate import DefaultReleaseGate
from rdf.judging.llm_judge import RuleBasedJudge
from rdf.reporting.report_builder import ReportBuilder
from rdf.scenarios.loader import load_scenarios
from rdf.storage.filesystem import FilesystemStorage


def parse_args() -> argparse.Namespace:
    """Parse runtime configuration for an evaluation run."""
    parser = argparse.ArgumentParser(description="Release Decision Framework CLI")
    parser.add_argument("--scenarios", default="scenarios", help="Scenario directory")
    parser.add_argument("--output", default="run_history", help="Run history output directory")
    parser.add_argument("--policy", default="gate_policies/default_policy.yaml", help="Policy file path")
    parser.add_argument("--max-concurrency", type=int, default=4)
    parser.add_argument("--scenario-timeout-sec", type=float, default=30.0)
    parser.add_argument("--max-retries", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # 1) Load scenarios from disk.
    scenarios = load_scenarios(args.scenarios)

    # 2) Build execution stack (adapter + judge + runner).
    adapter = MockAssistantAdapter()
    judge = RuleBasedJudge()
    runner = DefaultRunner(
        adapter=adapter,
        judge=judge,
        max_concurrency=args.max_concurrency,
        scenario_timeout_sec=args.scenario_timeout_sec,
        max_retries=args.max_retries,
    )

    # 3) Execute scenarios.
    scenario_runs = runner.run(scenarios)

    # 4) Evaluate release gate.
    gate = DefaultReleaseGate(policy_path=args.policy)
    decision = gate.evaluate(scenario_runs)

    # 5) Build human-readable summary.
    builder = ReportBuilder()
    summary = builder.build_summary_markdown(scenario_runs, decision)

    # 6) Persist run artifacts.
    storage = FilesystemStorage()
    run_dir = storage.create_run_dir(args.output)
    storage.write_run_artifacts(
        run_dir=run_dir,
        run_config={
            "scenario_path": args.scenarios,
            "policy_path": args.policy,
            "max_concurrency": args.max_concurrency,
            "scenario_timeout_sec": args.scenario_timeout_sec,
            "max_retries": args.max_retries,
        },
        scenario_runs=scenario_runs,
        release_decision=decision,
        summary_markdown=summary,
    )

    print(f"Run complete. Decision: {decision.status}")
    print(f"Artifacts: {run_dir}")


if __name__ == "__main__":
    main()
