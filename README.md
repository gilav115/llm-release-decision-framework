# Release Decision Framework

This system helps teams decide whether a conversational feature is ready to release.

This repository is intentionally a **demo and educational implementation**. It keeps the architecture clean and modular so teams can understand the flow quickly, then replace components (adapter, judge, gate) as their production needs evolve.

## Start here

If you are new to this repo, this is the shortest path:

1. Run the quickstart command.
2. Open the newest folder under `run_history/`.
3. Read `summary.md` for the one-minute result.
4. Inspect `scenario_runs.json` for per-scenario details.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python3 -m rdf.cli.main \
  --scenarios scenarios/banking \
  --policy gate_policies/default_policy.yaml \
  --max-concurrency 4 \
  --scenario-timeout-sec 30 \
  --max-retries 1 \
  --output run_history
```

## What this demo does today

This repo is intentionally minimal. It is useful for architecture and workflow learning, but not yet production-ready evaluation quality.

- The CLI constructs `MockAssistantAdapter` (`src/rdf/adapters/mock_assistant.py`), which returns hardcoded responses based on simple keyword matching.
- The CLI constructs `RuleBasedJudge` from `src/rdf/judging/llm_judge.py`. Despite the filename, this class does not call an LLM API; it uses deterministic string heuristics.
- The release gate logic (`DefaultReleaseGate`) only has explicit behavior for one configured rule id: `high_risk_required_failure`.
- During execution, the runner loops through every authored item in `scenario.turns` and sends each one to `adapter.send_turn(...)`. For that reason, authored turns should be user messages.
- After each adapter response, the runner appends a synthetic assistant turn to the transcript so judging/reporting can inspect full dialogue history.
- If a scenario still fails after retries, the exception is raised and the run exits; the current flow does not persist partial successful scenario outputs.

## What a decision means

- `pass`: all scenarios passed and no blocking policy rule triggered.
- `warn`: no blocking policy rule triggered, but at least one scenario failed.
- `block`: at least one blocking rule triggered.

Important edge case:
- If zero scenarios are loaded, current logic can still return `pass`. Treat this as a configuration problem, not a real success.

## What gets produced

- `run_config.json` — exact runtime configuration.
- `scenario_runs.json` — full per-scenario execution records.
- `release_decision.json` — final decision and triggered rules.
- `summary.md` — human-readable one-minute summary.
- `system_events.json` — flattened optional runtime events.

See `docs/run-artifacts.md` for field-level detail.

## Common failure modes

- Wrong scenario path: loader finds no files and you may get a misleading `pass`.
- Invalid scenario schema: loader raises `ScenarioValidationError` (for example duplicate ids or missing required fields).
- Adapter/runtime issues: runner retries up to `--max-retries`, then fails the run.
- Timeout: scenario exceeding `--scenario-timeout-sec` fails immediately (no further retries for that scenario).
- Policy typo: unknown `rule_id` is ignored by current demo gate behavior.

## Scenario/policy file format

Scenario and policy files use `.yaml`, but this demo stores them as JSON-formatted YAML for compatibility.

If `PyYAML` is installed, the loader accepts standard YAML syntax too.

## From demo to production checklist

1. Replace `MockAssistantAdapter` with a real provider adapter.
2. Replace `RuleBasedJudge` with a robust evaluation method.
3. Add stricter policy validation (reject unknown rule ids).
4. Add CI checks for scenario/policy linting.
5. Add regression baselines and trend tracking.

## Repository docs

- `docs/system-overview.md`
- `docs/contracts.md`
- `docs/repo-structure.md`
- `docs/run-artifacts.md`
- `docs/scenario-and-policy-authoring.md`
- `docs/examples/sample-report.md`
