# Release Decision Framework

This system helps teams decide whether a conversational feature is ready to release.

This repository is intentionally a **demo and educational implementation**. It keeps the architecture clean and modular so teams can understand the flow quickly, then replace components (adapter, judge, gate) as their production needs evolve.

## Why this exists

Shipping conversational features without realistic evaluation is risky. This framework gives teams a simple, auditable path from:

1. **Scenario definitions** (realistic multi-turn user interactions),
2. to **Assistant execution**,
3. to **Structured judging**,
4. to a **release decision** (`pass`, `warn`, `block`).

## Core design principles

- **Conversation-first evaluation**: scenarios are multi-turn, not single prompts.
- **Replaceable components**: adapters and judges are interfaces, not hardcoded vendors.
- **Decision-oriented outputs**: every run ends with an explicit release status.
- **Auditability**: run artifacts are persisted for inspection and history.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m rdf.cli.main \
  --scenarios scenarios/banking \
  --policy gate_policies/default_policy.yaml \
  --max-concurrency 4 \
  --scenario-timeout-sec 30 \
  --max-retries 1 \
  --output run_history
```

## What gets produced

Each run writes a timestamped folder under `run_history/`:

- `run_config.json` — exact runtime configuration.
- `scenario_runs.json` — full per-scenario execution records.
- `release_decision.json` — final decision and triggered rules.
- `summary.md` — human-readable one-minute summary.
- `system_events.json` — flattened optional runtime events.

See `docs/run-artifacts.md` for field-level detail.

## How to understand scenario and policy files

Because this demo is designed to run in restricted environments, scenario/policy `.yaml` files are currently authored in **JSON-formatted YAML** (JSON is valid YAML).

- `scenarios/README.md` explains every scenario field.
- `gate_policies/README.md` explains every policy field.

If `PyYAML` is installed, the loader accepts standard YAML syntax too.

## Repository docs

- `docs/system-overview.md`
- `docs/contracts.md`
- `docs/repo-structure.md`
- `docs/run-artifacts.md`
- `docs/scenario-and-policy-authoring.md`
- `docs/examples/sample-report.md`
