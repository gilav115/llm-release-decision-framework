# Run Artifacts

This document explains each output file from one run and how to use it.

## Folder naming

Runs are written under:

`run_history/<UTC timestamp>_run-001/`

Example:

`run_history/2026-03-27T09-55-52Z_run-001/`

## Files

### `run_config.json`
Records runtime inputs.

Typical fields:
- `scenario_path`
- `policy_path`
- `max_concurrency`
- `scenario_timeout_sec`
- `max_retries`

Use this first when results look wrong. It tells you exactly which inputs were used.

### `scenario_runs.json`
Contains one object per scenario.

Main sections:
- `scenario`: source scenario metadata and criteria.
- `transcript`: user + assistant turns captured during execution.
- `responses`: adapter response objects, each with `response_id`, `status`, and execution metadata such as latency and adapter provenance.
- `system_events`: optional adapter/runtime signals.
- `duration_ms`: runtime duration.
- `status`: scenario execution status.
- `started_at_utc` / `completed_at_utc`: scenario execution window.
- `judge_result`: structured scoring and pass/fail output.
- `metadata`: execution annotations (for example retry attempt, response counts, and latency rollups).

Quick checks:
- `judge_result.passed` and `judge_result.overall_score`
- any required criteria with `passed: false`
- `metadata.attempt` to see whether retries were used
- `responses[*].metadata.latency_ms` to find slow turns
- `responses[*].metadata.adapter_name` / `raw_payload.template_key` to identify where a response came from

### `release_decision.json`
Final run decision from gate policy logic.

Fields:
- `status` (`pass`/`warn`/`block`)
- `summary`
- `triggered_rules`
- `metadata` (for example policy id, pass/fail counts, pass rate, and duration rollups)

`triggered_rules` is the first place to look when decision is `block` or `warn`.

### `summary.md`
Short, human-readable run summary for quick sharing.

It now includes:
- outcome and policy context
- pass/fail counts and pass rate
- timing rollups
- triggered rules
- a per-scenario results table

This is useful for status updates, but debugging should use the JSON artifacts above.

### `system_events.json`
Flattened event stream across all scenario runs.
Useful for debugging adapter/runtime behavior.

### `run_errors.json`
List of non-fatal errors captured during run:
- scenario file load errors
- scenario execution errors

This file is useful for understanding partial-failure runs.

### `run_stats.json`
Structured run metrics used by callers for monitoring and comparisons.

Top-level sections:
- `counts`
- `rates`
- `performance`

`counts` fields:
- `scenario_inputs_total`: loaded scenarios + load-error files
- `scenarios_loaded`
- `load_errors`
- `scenarios_passed`
- `scenarios_failed`
- `scenarios_errored`
- `execution_errors`
- `turns_executed`

`rates` fields:
- `success_rate_loaded_pct`: `scenarios_passed / scenarios_loaded * 100`
- `failure_rate_loaded_pct`: `(scenarios_failed + scenarios_errored) / scenarios_loaded * 100`
- `load_error_rate_input_pct`: `load_errors / scenario_inputs_total * 100`
- `scenarios_per_second`: `scenarios_loaded / total_execution_seconds`
- `turns_per_second`: `turns_executed / total_execution_seconds`

`performance` fields:
- `total_execution_ms`: wall-clock runtime for the CLI evaluation flow
- `scenario_execution_ms`: summary stats for per-scenario duration (`avg/p50/p95/min/max`)
- `question_execution_ms`: summary stats for per-turn execution time (`avg/p50/p95/min/max`)

## Artifact interpretation caveats

- If policy loading fails before run setup completes, artifact files may be missing.
- A `pass` means policy conditions were satisfied. It does not prove scenario quality.
- `summary.md` is derived output, not source-of-truth data.
- Question execution metrics are measured from adapter turn dispatch start to response return.
