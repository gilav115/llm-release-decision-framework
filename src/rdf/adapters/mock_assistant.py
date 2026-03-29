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
        mentions_blocked_card = "card" in text and "block" in text
        template_key = "generic_clarification"
        if "how much" in text or "fee" in text:
            template_key = "fee_uncertainty_redirect"
            message = "I may not have your bank's latest fee schedule. Please check your official fee table or support channel."
        elif mentions_blocked_card and "travel" in text:
            template_key = "blocked_card_travel_support"
            message = (
                "I'm sorry you're dealing with this while traveling. Lock the card in your banking app if possible, "
                "contact your bank through its official app or the number on the back of the card, ask about emergency "
                "cash or a replacement card, and review recent transactions for anything suspicious."
            )
        elif mentions_blocked_card:
            template_key = "blocked_card_redirect"
            message = "If your card is blocked, pause transactions and contact support immediately through official channels."
        else:
            message = "I want to help, but I need a little more detail about the issue and what you've already tried."

        context["events"].append(
            SystemEvent(
                event_type="turn_processed",
                payload={"turn_id": turn.turn_id, "template_key": template_key, "adapter": self.__class__.__name__},
            )
        )
        return AssistantResponse(
            message=message,
            raw_payload={"mock": True, "template_key": template_key},
            metadata={
                "adapter": self.__class__.__name__,
                "provider": "mock",
                "response_strategy": "keyword_rule",
                "template_key": template_key,
            },
        )

    def end_conversation(self, context: dict[str, Any]) -> None:
        """Mark completion timestamp in context."""
        context["ended_at"] = time.time()

    def collect_system_events(self, context: dict[str, Any]) -> list[SystemEvent]:
        """Expose captured mock runtime events for artifact/debug visibility."""
        return list(context.get("events", []))
