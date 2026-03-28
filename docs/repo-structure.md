# Repository Structure

This repository is organized for clarity and teaching value.

## Top-level intent

- `src/rdf/`: framework code with single-responsibility modules.
- `scenarios/`: conversation scenarios (inputs).
- `gate_policies/`: release gate policies (decision rules).
- `run_history/`: generated run artifacts.
- `docs/`: explanatory documentation for users and contributors.
- `tests/`: unit and integration checks.

## Code module responsibilities

- `adapters/`: how the framework talks to assistants.
- `scenarios/`: scenario loading and validation.
- `judging/`: conversion of run outputs into structured evaluation.
- `execution/`: orchestration of scenario runs.
- `gates/`: release policy evaluation.
- `reporting/`: human-readable summaries.
- `storage/`: persistence of run artifacts.
- `cli/`: top-level entrypoint.

## Documentation responsibilities

- `system-overview.md`: architecture and flow.
- `contracts.md`: stable interfaces and models.
- `run-artifacts.md`: persisted output schema and intent.
- `scenario-and-policy-authoring.md`: how to write inputs.
- `examples/sample-report.md`: expected summary style.
