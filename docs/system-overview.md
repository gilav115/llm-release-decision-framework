# System Overview

The framework evaluates conversational assistants via realistic multi-turn scenarios, then returns a release decision (`pass`, `warn`, `block`).

## Pipeline

1. Load and validate scenarios.
2. Run each scenario with an assistant adapter.
3. Judge each completed conversation.
4. Aggregate scenario outcomes.
5. Apply gate policy for final decision.
6. Persist artifacts for auditability.

## Responsibilities by layer

- Scenario loader: parse files, enforce required schema checks, return typed scenario objects.
- Adapter: send scenario turns to the assistant under test and return normalized responses.
- Runner: orchestrate retries, timeout behavior, and concurrency.
- Judge: convert transcript/response data into criterion-level pass/fail + score output.
- Gate: apply policy rules to scenario results and produce final `pass`/`warn`/`block`.
- Storage/reporting: write machine-readable artifacts and human-readable summary output.

## Current demo boundaries

- Adapter in default CLI flow is `MockAssistantAdapter`, which returns deterministic keyword-based responses.
- Judge in default CLI flow is `RuleBasedJudge`, which applies deterministic text heuristics and does not call a model API.
- Gate in default CLI flow has explicit logic for `high_risk_required_failure`; unknown rule ids in policy are ignored.

## Practical read path after a run

1. `summary.md`: quick human snapshot.
2. `release_decision.json`: final status and triggered rules.
3. `scenario_runs.json`: per-scenario transcript, scoring, and retry metadata.
