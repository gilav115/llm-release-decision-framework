"""Judge contract.

A judge turns completed execution artifacts into structured, machine-readable
assessment results. Judges are replaceable so the framework can evolve from
rule-based heuristics to prompt-based or model-based evaluators.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from rdf.models import AssistantResponse, ConversationScenario, ConversationTurn, JudgeResult, SystemEvent


class Judge(ABC):
    """Abstract evaluator for completed scenario runs."""

    @abstractmethod
    def evaluate(
        self,
        scenario: ConversationScenario,
        transcript: list[ConversationTurn],
        responses: list[AssistantResponse],
        system_events: list[SystemEvent],
    ) -> JudgeResult:
        """Return structured criterion-level and overall scenario evaluation."""
        raise NotImplementedError
