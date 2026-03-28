"""Deterministic mock assistant adapter used for demos and tests.

The mock adapter provides stable, non-random responses so educational runs are
repeatable and CI-friendly.
"""

from __future__ import annotations

import time
from typing import Any

from rdf.adapters.base import AssistantAdapter
from rdf.models import AssistantResponse, ConversationScenario, ConversationTurn, SystemEvent


class MockAssistantAdapter(AssistantAdapter):
    """Simple deterministic assistant used to exercise framework flow.

    Response heuristics are intentionally lightweight. The goal is not model
    quality, but predictable execution behavior for framework validation.
    """

    def start_conversation(self, scenario: ConversationScenario) -> dict[str, Any]:
        """Create in-memory context and start event timeline."""
        return {"scenario_id": scenario.scenario_id, "started_at": time.time(), "events": []}

    def send_turn(self, context: dict[str, Any], turn: ConversationTurn) -> AssistantResponse:
        """Generate deterministic response based on message keyword heuristics."""
        text = turn.message.lower()
        if "how much" in text or "fee" in text:
            message = "I may not have your bank's latest fee schedule. Please check your official fee table or support channel."
        elif "blocked card" in text:
            message = "If your card is blocked, pause transactions and contact support immediately through official channels."
        else:
            message = f"I understand. You said: {turn.message}"

        context["events"].append(SystemEvent(event_type="turn_processed", payload={"turn_id": turn.turn_id}))
        return AssistantResponse(message=message, raw_payload={"mock": True})

    def end_conversation(self, context: dict[str, Any]) -> None:
        """Mark completion timestamp in context."""
        context["ended_at"] = time.time()

    def collect_system_events(self, context: dict[str, Any]) -> list[SystemEvent]:
        """Expose captured mock runtime events for artifact/debug visibility."""
        return list(context.get("events", []))
