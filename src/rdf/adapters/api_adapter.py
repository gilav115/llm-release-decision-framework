"""Template adapter for real provider integration.

This class is intentionally a skeleton. It documents where production teams
should connect authentication, request/response mapping, retry behavior,
and telemetry collection for their specific assistant provider.
"""

from __future__ import annotations

from typing import Any

from rdf.adapters.base import AssistantAdapter
from rdf.models import AssistantResponse, ConversationScenario, ConversationTurn


class ApiAssistantAdapter(AssistantAdapter):
    """Base implementation scaffold for provider-backed assistants.

    Typical production responsibilities:
    - map `ConversationScenario` to provider session metadata
    - transform `ConversationTurn` to provider request payload
    - normalize provider response into `AssistantResponse`
    - expose runtime telemetry/events via `collect_system_events`
    """

    def start_conversation(self, scenario: ConversationScenario) -> Any:
        """Create a provider conversation/session context."""
        raise NotImplementedError("Implement provider-specific conversation/session creation")

    def send_turn(self, context: Any, turn: ConversationTurn) -> AssistantResponse:
        """Submit a user turn to provider and normalize returned response."""
        raise NotImplementedError("Implement provider-specific turn dispatch")

    def end_conversation(self, context: Any) -> None:
        """Close/cleanup provider-side resources for this session."""
        raise NotImplementedError("Implement provider-specific cleanup")
