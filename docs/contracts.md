# Contracts

This document maps implementation modules to stable contracts.

## Core contract modules

- `rdf.models`
  - canonical dataclasses and typed literals for domain objects
  - examples: `ConversationScenario`, `ScenarioRun`, `ReleaseDecision`

- `rdf.adapters.base.AssistantAdapter`
  - interface between framework and assistant under test
  - framework should depend only on this contract, not provider SDK specifics

- `rdf.judging.base.Judge`
  - evaluates completed scenario execution into structured `JudgeResult`

- `rdf.execution.runner.Runner`
  - orchestrates scenario execution and collection
  - intentionally excludes release decision logic

- `rdf.gates.release_gate.ReleaseGate`
  - converts scenario results into final release outcome

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
