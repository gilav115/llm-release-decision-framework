# Gate Policies Directory

This folder contains release gate policy definitions.

## File format

Policies use `.yaml` extension and are authored as JSON-formatted YAML for compatibility.

## Default policy fields

- `policy_id`: policy version/name for audit trails.
- `rules`: list of gate rules.
  - `rule_id`: supported rule identifier.
  - `description`: human-readable explanation.
  - `outcome`: decision outcome when triggered.

## Current rule support in demo

- `high_risk_required_failure`
  - Blocks release when any required criterion fails in a high-risk scenario.
