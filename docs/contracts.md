# Contracts

This document lists core interfaces shared across modules.

## Core interfaces

- `rdf.models`: shared dataclasses/literals like `ConversationScenario`, `ScenarioRun`, `ReleaseDecision`.
- `rdf.adapters.base.AssistantAdapter`: interface for talking to any assistant backend.
- `rdf.judging.base.Judge`: interface that converts one scenario run into `JudgeResult`.
- `rdf.execution.runner.Runner`: interface for executing scenarios and returning `ScenarioRun` records.
- `rdf.gates.release_gate.ReleaseGate`: interface that maps runs to one `ReleaseDecision`.

## Error contracts

`rdf.errors` defines predictable failure categories:
- `ScenarioValidationError`
- `AdapterExecutionError`
- `JudgeParsingError`
- `ScenarioTimeoutError`

These error types let callers handle failures by category.

## Artifact contract

Filesystem storage writes these standard outputs:
- `run_config.json`
- `scenario_runs.json`
- `release_decision.json`
- `summary.md`
- `system_events.json`
- `run_errors.json`
- `run_stats.json`

See `docs/run-artifacts.md` for details.
