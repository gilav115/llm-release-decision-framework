# Scenarios Directory

This folder contains conversation scenarios used for evaluation runs.

## File format

Files use `.yaml` extension and are authored as JSON-formatted YAML for compatibility.

## Field walkthrough

- `scenario_id`: stable identifier for tracking and comparisons.
- `title`: short human-readable scenario name.
- `description`: what behavior this scenario is testing.
- `domain`: business/product domain (for grouping/filtering later).
- `risk_level`: `low`, `medium`, or `high`.
- `user_profile`: persona context attached to the scenario.
- `turns`: ordered user turns to send through adapter.
- `criteria`: judge criteria with weight + required flag.
- `expected_behaviour_notes`: optional evaluator guidance.
- `tags`: optional labels for search and grouping.
