"""Scenario model re-export.

This module exists to keep a stable import path (`rdf.scenarios.models`) for
future scenario-specific model extensions.
"""

from rdf.models import ConversationScenario

__all__ = ["ConversationScenario"]
