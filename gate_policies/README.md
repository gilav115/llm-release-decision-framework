# Gate Policies Directory

This folder contains release gate policy definitions.

## File format

Policies use `.yaml` extension and are authored as JSON-formatted YAML for compatibility.

## Default policy fields

- `policy_id` (required): policy version/name recorded in `release_decision.json`.
- `rules` (required): list of rule objects.
- `rule_id` (required): rule identifier that must match logic implemented in `src/rdf/gates/release_gate.py`.
- `description` (required): human-readable explanation of rule intent.
- `outcome` (required): decision status to emit when the rule triggers (`pass`, `warn`, or `block`).

## Current rule support in demo

- `high_risk_required_failure`
  - Blocks release when any required criterion fails in a high-risk scenario.

## Important implementation behavior

- If a `rule_id` in policy does not match a supported rule in code, policy load fails with `ValueError`.
- If `outcome` is not one of `pass`, `warn`, `block`, policy load fails with `ValueError`.
