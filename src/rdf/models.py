"""Core domain models for the Release Decision Framework.

These dataclasses are shared contracts across loader, runner, judge, gate,
reporting, and storage. Keeping them centralized makes behavior explicit and
reduces integration drift.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

RiskLevel = Literal["low", "medium", "high"]
Speaker = Literal["user", "assistant"]
DecisionStatus = Literal["pass", "warn", "block"]


@dataclass
class UserProfile:
    """Persona context attached to a scenario."""

    user_id: str
    name: str
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationTurn:
    """One conversational turn in a transcript."""

    turn_id: str
    speaker: Speaker
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationCriterion:
    """One scoring criterion used by judges."""

    criterion_id: str
    name: str
    description: str
    weight: float
    required: bool = True


@dataclass
class ConversationScenario:
    """Scenario definition used as the primary evaluation unit."""

    scenario_id: str
    title: str
    description: str
    domain: str
    risk_level: RiskLevel
    user_profile: UserProfile
    turns: list[ConversationTurn]
    criteria: list[EvaluationCriterion]
    expected_behaviour_notes: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssistantResponse:
    """Normalized assistant output returned by adapters."""

    message: str
    raw_payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemEvent:
    """Optional runtime signal captured during scenario execution."""

    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class CriterionResult:
    """Judge output for one criterion."""

    criterion_id: str
    score: float
    passed: bool
    reasoning: str


@dataclass
class JudgeResult:
    """Judge output for one scenario."""

    scenario_id: str
    overall_score: float
    passed: bool
    reasoning: str
    criterion_results: list[CriterionResult]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScenarioRun:
    """Complete execution record for one scenario in one run."""

    run_id: str
    scenario: ConversationScenario
    transcript: list[ConversationTurn]
    responses: list[AssistantResponse]
    system_events: list[SystemEvent]
    duration_ms: int
    judge_result: JudgeResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TriggeredRule:
    """A release gate rule triggered during evaluation."""

    rule_id: str
    outcome: DecisionStatus
    reason: str


@dataclass
class ReleaseDecision:
    """Final release readiness decision for a run."""

    status: DecisionStatus
    summary: str
    triggered_rules: list[TriggeredRule]
    metadata: dict[str, Any] = field(default_factory=dict)
