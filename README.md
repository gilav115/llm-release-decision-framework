# Release Decision Framework

This repo helps you test a chatbot feature before release.

It is a **demo implementation**: good for learning and pilot runs, not full production hardening.

## Start here

If this is your first time here:

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

## What this repo does

For each scenario file:
- The runner sends each authored turn to an adapter.
- The adapter returns an assistant message.
- The judge scores the conversation against scenario criteria.
- The gate applies policy rules and returns `pass`, `warn`, or `block`.
- Artifacts are written to `run_history/<timestamp>_run-001/`.

Default demo components:
- Adapter: `MockAssistantAdapter` (deterministic keyword-based responses).
- Judge: `RuleBasedJudge` in `src/rdf/judging/llm_judge.py` (heuristics, no LLM API call).
- Gate: `DefaultReleaseGate` with rule support for `high_risk_required_failure`.

Current runtime behavior:
- Scenario turns should be user turns (`speaker: "user"`).
- Assistant turns are generated during execution and appended to transcript.
- Per-scenario timeout is enforced, including around blocking `send_turn(...)` calls.
- `end_conversation(...)` is always attempted in a `finally` block.
- If a scenario fails after retries, the run records that scenario as an error and continues with other scenarios.
- Run artifacts are still written, including both successful and failed scenario records.

## What a decision means

- `pass`: all scenarios passed and no blocking policy rule triggered.
- `warn`: no blocking policy rule triggered, but at least one scenario failed.
- `block`: at least one blocking rule triggered.

If no scenario `.yaml` files are found, CLI records a load error in `run_errors.json` and final decision is blocked.

## What gets produced

- `run_config.json` — exact runtime configuration.
- `scenario_runs.json` — full per-scenario execution records.
- `release_decision.json` — final decision and triggered rules.
- `summary.md` — human-readable one-minute summary.
- `system_events.json` — flattened optional runtime events.
- `run_errors.json` — load-time and execution-time errors captured during the run.
- `run_stats.json` — structured performance and rate metrics for the run.

Recent artifact improvements:
- each response now includes status, response id, latency, provenance, and basic quality hints in `responses[].metadata`
- each scenario run now includes explicit run status, start/end timestamps, response counts, and aggregate latency metrics
- `release_decision.json` now includes pass/fail counts, pass rate, and duration rollups

See `docs/run-artifacts.md` for field-level detail.

## Common failure modes

- Wrong scenario path: CLI records load errors and blocks final decision.
- Invalid scenario schema: invalid files are recorded as load errors; valid files still run.
- Invalid CLI values: argument parser rejects bad values (`--max-concurrency <= 0`, `--scenario-timeout-sec <= 0`, `--max-retries < 0`).
- Adapter/runtime issues: runner retries up to `--max-retries`, then records scenario error if still failing.
- Timeout: scenario exceeding `--scenario-timeout-sec` is recorded as scenario error.
- Policy typo: unsupported `rule_id` or `outcome` now fails fast during policy load with `ValueError`.

## Scenario/policy file format

Scenario and policy files use `.yaml`, but this demo stores them as JSON-formatted YAML for compatibility.

If `PyYAML` is installed, the loader accepts standard YAML syntax too.

## From demo to production

1. Replace `MockAssistantAdapter` with a real provider adapter.
2. Replace `RuleBasedJudge` with a robust evaluation method.
3. Add artifact redaction/data retention controls for sensitive content.
4. Persist artifacts even when policy loading fails.
5. Add CI checks and regression trend tracking.

## Repository docs

- `docs/system-overview.md`
- `docs/contracts.md`
- `docs/repo-structure.md`
- `docs/run-artifacts.md`
- `docs/scenario-and-policy-authoring.md`
- `docs/examples/sample-report.md`
