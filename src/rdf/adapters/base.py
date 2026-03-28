"""Assistant adapter contracts.

This module defines the stable interface between the framework and any assistant
backend (mock, API-based, or local model). The rest of the framework should
only depend on this contract, not provider-specific SDK details.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from rdf.models import AssistantResponse, ConversationScenario, ConversationTurn, SystemEvent


class AssistantAdapter(ABC):
    """Abstract conversation adapter.

    Lifecycle:
    1. `start_conversation` creates provider/session context.
    2. `send_turn` submits one user turn and returns one assistant response.
    3. `end_conversation` performs cleanup.
    4. `collect_system_events` returns optional runtime/provider signals.

    Why this matters:
    Keeping this interface stable lets teams swap providers without changing
    runner, judge, gate, or reporting code.
    """

    @abstractmethod
    def start_conversation(self, scenario: ConversationScenario) -> Any:
        """Initialize a conversation context for a scenario.

        Args:
            scenario: Scenario metadata + planned user turns.

        Returns:
            Provider-specific context object (session id, client handle, etc.).
        """
        raise NotImplementedError

    @abstractmethod
    def send_turn(self, context: Any, turn: ConversationTurn) -> AssistantResponse:
        """Send one user turn and return the assistant response."""
        raise NotImplementedError

    @abstractmethod
    def end_conversation(self, context: Any) -> None:
        """Finalize/cleanup provider resources for this conversation."""
        raise NotImplementedError

    def collect_system_events(self, context: Any) -> list[SystemEvent]:
        """Return optional provider/runtime signals collected during execution.

        Default behavior returns an empty list so adapters can opt in when they
        have useful low-level diagnostics.
        """
        return []
