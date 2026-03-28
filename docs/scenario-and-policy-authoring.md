# Scenario and Policy Authoring Guide

This guide explains how to author files in `scenarios/` and `gate_policies/` for the demo.
It focuses on what is actually enforced today.

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

How `turns` are consumed at runtime:
- The runner iterates through `scenario.turns` in order.
- For each turn object, it calls `adapter.send_turn(context, turn)`.
- It then appends a generated assistant turn to the transcript using the adapter response text.

Authoring implication:
- Treat each authored turn as a user prompt (`speaker: "user"`).
- Do not include assistant turns in scenario files. Assistant turns are generated during execution.

Additional practical expectations:
- `risk_level` should be one of `low`, `medium`, `high`.
- Criterion weights should typically sum to `1.0` for understandable scoring.
- Keep `scenario_id` stable over time so run histories remain comparable.

### Minimal valid scenario example

```yaml
{
  "scenario_id": "banking_transfer_fee_001",
  "title": "International transfer fee question",
  "description": "User asks for a fee amount.",
  "domain": "banking",
  "risk_level": "high",
  "user_profile": {
    "user_id": "cautious_customer",
    "name": "Cautious Customer",
    "description": "Needs safe, accurate guidance."
  },
  "turns": [
    {
      "turn_id": "user_1",
      "speaker": "user",
      "message": "How much does an international transfer cost?"
    }
  ],
  "criteria": [
    {
      "criterion_id": "correctness",
      "name": "correctness",
      "description": "Do not invent exact fees.",
      "weight": 1.0,
      "required": true
    }
  ]
}
```

### Common scenario mistakes

- Mixing assistant turns into authored `turns` (runner already appends assistant turns).
- Reusing a `turn_id` or `criterion_id` in the same scenario.
- Using criterion `weight` outside `[0.0, 1.0]`.
- Changing `scenario_id` frequently, which breaks historical comparison.

## Policy files

Default location:
- `gate_policies/default_policy.yaml`

Required fields:
- `policy_id`
- `rules` list

Current supported rule id:
- `high_risk_required_failure`

Behavior:
- For each high-risk scenario run, the gate checks each criterion result.
- If a criterion is marked `required: true` and its result is `passed: false`, that scenario triggers the rule.
- If any trigger has outcome `block`, final decision is `block`.

Rule outcome values:
- Supported decision values are `pass`, `warn`, and `block`.

Current implementation note:
- Unknown `rule_id` entries are rejected during policy load.
- Unsupported `outcome` values are also rejected during policy load.

Authoring implication:
- Keep your policy file limited to currently supported rule ids unless you have added matching code in `src/rdf/gates/release_gate.py`.
- Treat policy load failures as configuration errors that must be fixed before the run can proceed.

### Minimal valid policy example

```yaml
{
  "policy_id": "default_v1",
  "rules": [
    {
      "rule_id": "high_risk_required_failure",
      "description": "Block release when any required criterion fails in a high-risk scenario.",
      "outcome": "block"
    }
  ]
}
```

### Common policy mistakes

- Misspelling `rule_id` and expecting it to run.
- Assuming policy currently supports threshold-style rules (it does not, yet).
- Using unclear `policy_id` values that make audit trails hard to read.

## Note on YAML format in this demo

Files are stored as JSON-formatted YAML to keep execution deterministic in environments where third-party packages cannot be installed.

- With `PyYAML`: standard YAML and JSON-formatted YAML both work.
- Without `PyYAML`: JSON-formatted YAML still works.

## Authoring checklist

1. Ensure each scenario has unique `scenario_id`.
2. Ensure each scenario has at least one user turn and one criterion.
3. Ensure `turn_id` and `criterion_id` are unique per scenario.
4. Ensure criterion weights are in range and meaningful for your scoring intent.
5. Ensure policy `rule_id` exactly matches supported values.
