# Scenarios Directory

This folder contains scenario files used as test inputs.

## File format

Files use `.yaml` extension and are authored as JSON-formatted YAML for compatibility.

## Field walkthrough

- `scenario_id` (required): stable identifier used in artifacts and historical comparisons.
- `title` (required): short human-readable scenario name.
- `description` (required): behavior this scenario is testing.
- `domain` (required): business/product grouping label.
- `risk_level` (required): expected values are `low`, `medium`, or `high`.
- `user_profile` (required): object with `user_id`, `name`, and `description`.
- `turns` (required): ordered list of user prompts to send to the adapter.
- `criteria` (required): list of criterion objects with `criterion_id`, `name`, `description`, `weight`, and optional `required`.
- `expected_behaviour_notes` (optional): evaluator guidance text.
- `tags` (optional): labels for search and grouping.

## Important runtime behavior

- The runner sends each authored turn to the adapter as an input message.
- The runner then appends the returned assistant message to transcript automatically.
- Do not author assistant turns in scenario files.
