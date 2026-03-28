# System Overview

The framework evaluates conversational assistants via realistic multi-turn scenarios, then returns a release decision (`pass`, `warn`, `block`).

Pipeline:
1. Load and validate scenarios.
2. Run each scenario with an assistant adapter.
3. Judge each completed conversation.
4. Aggregate scenario outcomes.
5. Apply gate policy for final decision.
6. Persist artifacts for auditability.
