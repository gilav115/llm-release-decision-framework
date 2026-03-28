# Scenario and Policy Authoring Guide

This guide explains how to author files in `scenarios/` and `gate_policies/` for the demo.

## Scenario files

Location pattern:
- `scenarios/<domain>/<scenario_name>.yaml`

Required fields:
- `scenario_id`, `title`, `description`, `domain`, `risk_level`
- `user_profile` (`user_id`, `name`, `description`)
- `turns` (at least one turn)
- `criteria` (at least one criterion)

Validation rules enforced by loader:
- `scenario_id` unique across loaded files
- `turn_id` unique per scenario
- `criterion_id` unique per scenario
- criterion `weight` is between `0.0` and `1.0`

## Policy files

Default location:
- `gate_policies/default_policy.yaml`

Required fields:
- `policy_id`
- `rules` list

Current supported rule id:
- `high_risk_required_failure`

Behavior:
- if any required criterion fails in a high-risk scenario, gate returns `block`.

## Note on YAML format in this demo

Files are stored as JSON-formatted YAML to keep execution deterministic in environments where third-party packages cannot be installed.

- With `PyYAML`: standard YAML and JSON-formatted YAML both work.
- Without `PyYAML`: JSON-formatted YAML still works.
