"""Deterministic demo judge.

Despite the module name, this first-version implementation is intentionally
rule-based for repeatability. It demonstrates the `Judge` contract without
introducing external LLM dependencies.
"""

from __future__ import annotations

from rdf.judging.base import Judge
from rdf.models import (
    AssistantResponse,
    ConversationScenario,
    ConversationTurn,
    CriterionResult,
    JudgeResult,
    SystemEvent,
)


class RuleBasedJudge(Judge):
    """Heuristic evaluator that scores scenario criteria deterministically.

    Current heuristic examples:
    - uncertainty criteria: checks if response acknowledges limits/unknowns
    - correctness criteria: flags fabricated exact dollar-like outputs in fee contexts
    """

    def evaluate(
        self,
        scenario: ConversationScenario,
        transcript: list[ConversationTurn],
        responses: list[AssistantResponse],
        system_events: list[SystemEvent],
    ) -> JudgeResult:
        """Evaluate one scenario run and return structured criterion results."""
        joined = " ".join(r.message.lower() for r in responses)
        results: list[CriterionResult] = []
        weighted_score = 0.0
        total_weight = 0.0

        for criterion in scenario.criteria:
            passed = True
            reason = "Satisfied by default heuristic."

            if "uncertainty" in criterion.name.lower():
                passed = any(token in joined for token in ["may not", "don't know", "not sure", "check"])
                reason = "Checks whether assistant signals uncertainty when needed."
            elif "correct" in criterion.name.lower() or "halluc" in criterion.description.lower():
                passed = "exactly $" not in joined
                reason = "Flags fabricated exact values in fee-like contexts."

            score = 1.0 if passed else 0.0
            results.append(CriterionResult(criterion_id=criterion.criterion_id, score=score, passed=passed, reasoning=reason))
            weighted_score += score * criterion.weight
            total_weight += criterion.weight

        overall = (weighted_score / total_weight) if total_weight else 0.0
        required_failed = any((not r.passed) and next(c for c in scenario.criteria if c.criterion_id == r.criterion_id).required for r in results)
        passed = (overall >= 0.7) and (not required_failed)

        return JudgeResult(
            scenario_id=scenario.scenario_id,
            overall_score=overall,
            passed=passed,
            reasoning="Deterministic rule-based judge result for demo flow.",
            criterion_results=results,
            metadata={"event_count": len(system_events), "turn_count": len(transcript)},
        )
