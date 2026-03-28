# System Overview

This repo runs conversation test cases and returns one release decision: `pass`, `warn`, or `block`.

## Pipeline

1. Load scenario files and validate them.
2. Keep valid scenarios and capture load errors for invalid files.
3. Run each valid scenario through an adapter (the adapter talks to the chatbot).
4. Judge completed conversations against scenario criteria.
5. Record scenario execution errors without aborting the full run.
6. Apply gate policy rules to all scenario results.
7. Write run artifacts to disk (including error artifacts).

## Responsibilities by layer

- Loader: reads scenario files and enforces schema/ID validation.
- Adapter: sends user turns to the assistant system and returns assistant responses.
- Runner: handles retries, timeout, concurrency, and transcript building.
- Judge: turns transcript/responses into criterion results and scenario pass/fail.
- Gate: maps scenario results to final decision using policy rules.
- Storage/reporting: writes JSON artifacts and markdown summary.

## Current demo boundaries

- Adapter in default CLI flow is `MockAssistantAdapter`, which returns deterministic keyword-based responses.
- Judge in default CLI flow is `RuleBasedJudge`, which applies deterministic text heuristics and does not call a model API.
- Gate in default CLI flow has explicit logic for `high_risk_required_failure`; unsupported policy rule ids/outcomes fail during policy load.

## Practical read path after a run

1. `summary.md`: quick status view.
2. `release_decision.json`: final decision and triggered rules.
3. `scenario_runs.json`: detailed per-scenario evidence.
4. `run_stats.json`: performance and rate metrics.
