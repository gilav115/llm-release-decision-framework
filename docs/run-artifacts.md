# Run Artifacts

This document explains what each run artifact means and why it exists.

## Folder naming

Runs are written under:

`run_history/<UTC timestamp>_run-001/`

Example:

`run_history/2026-03-27T09-55-52Z_run-001/`

## Files

### `run_config.json`
Records runtime inputs for reproducibility.

Typical fields:
- `scenario_path`
- `policy_path`
- `max_concurrency`
- `scenario_timeout_sec`
- `max_retries`

### `scenario_runs.json`
Contains one object per scenario execution.

Key sections:
- `scenario`: source scenario metadata and criteria.
- `transcript`: user + assistant turns captured during execution.
- `responses`: adapter response objects.
- `system_events`: optional adapter/runtime signals.
- `duration_ms`: runtime duration.
- `judge_result`: structured scoring and pass/fail output.
- `metadata`: execution annotations (for example retry attempt).

### `release_decision.json`
Final release outcome from the gate.

Fields:
- `status` (`pass`/`warn`/`block`)
- `summary`
- `triggered_rules`
- `metadata` (for example policy id)

### `summary.md`
Short, human-readable run summary for quick sharing.

### `system_events.json`
Flattened event stream across all scenario runs.
Useful for debugging adapter/runtime behavior.
