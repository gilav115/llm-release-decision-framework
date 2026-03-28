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

Use this first when a run result looks suspicious. It confirms what inputs were actually used.

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

What to inspect quickly:
- `judge_result.passed` and `judge_result.overall_score`
- any required criteria with `passed: false`
- `metadata.attempt` to see whether retries were used

### `release_decision.json`
Final release outcome from the gate.

Fields:
- `status` (`pass`/`warn`/`block`)
- `summary`
- `triggered_rules`
- `metadata` (for example policy id)

`triggered_rules` is the best place to understand why a decision became `block` or `warn`.

### `summary.md`
Short, human-readable run summary for quick sharing.

This is useful for status updates, but debugging should use the JSON artifacts above.

### `system_events.json`
Flattened event stream across all scenario runs.
Useful for debugging adapter/runtime behavior.

## Artifact interpretation caveats

- If the run crashes before persistence, artifact files may be missing.
- A `pass` decision does not always mean your setup was meaningful; verify scenario count and scenario quality.
- `summary.md` is derived from artifacts and should not be treated as the source of truth.
