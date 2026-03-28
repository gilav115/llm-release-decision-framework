# Contracts

This document maps implementation modules to stable interfaces the rest of the system depends on.

## Core contract modules

- `rdf.models`
  - canonical dataclasses and typed literals used across modules
  - examples: `ConversationScenario`, `ScenarioRun`, `ReleaseDecision`

- `rdf.adapters.base.AssistantAdapter`
  - interface between framework runtime and assistant implementation
  - runner should call this interface rather than provider-specific SDK code

- `rdf.judging.base.Judge`
  - converts one completed scenario run into a structured `JudgeResult`

- `rdf.execution.runner.Runner`
  - orchestrates scenario execution and collects `ScenarioRun` records
  - does not contain release decision policy logic

- `rdf.gates.release_gate.ReleaseGate`
  - converts scenario run results into final `ReleaseDecision`

## Error contracts

`rdf.errors` defines predictable failure categories:
- `ScenarioValidationError`
- `AdapterExecutionError`
- `JudgeParsingError`
- `ScenarioTimeoutError`

These keep failures explicit and machine-actionable.

## Artifact contract

The filesystem storage layer writes stable run outputs:
- `run_config.json`
- `scenario_runs.json`
- `release_decision.json`
- `summary.md`
- `system_events.json`

See `docs/run-artifacts.md` for details.
