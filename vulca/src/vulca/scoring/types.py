"""Scoring subsystem types -- dimension scores, critique output, critic config."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LayerID(str, Enum):
    """Standard L1-L5 dimension identifiers."""

    L1 = "visual_perception"
    L2 = "technical_analysis"
    L3 = "cultural_context"
    L4 = "critical_interpretation"
    L5 = "philosophical_aesthetic"


DIMENSIONS: list[str] = [e.value for e in LayerID]
"""Ordered list of dimension snake_case names."""


@dataclass
class DimensionScore:
    """Score for a single L1-L5 dimension."""

    layer_id: str
    score: float
    confidence: float = 1.0
    rationale: str = ""
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "score": self.score,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "evidence": self.evidence,
        }


@dataclass
class CritiqueOutput:
    """Complete critique result from the Critic agent."""

    candidate_id: str
    dimension_scores: dict[str, float]
    """Mapping of dimension name -> score (0-1)."""

    weighted_total: float
    """Weighted total score across all dimensions."""

    rationales: dict[str, str] = field(default_factory=dict)
    """Per-dimension rationales."""

    risk_flags: list[str] = field(default_factory=list)
    """Cultural risk flags detected."""

    fix_it_plan: dict[str, Any] = field(default_factory=dict)
    """Suggested fixes for weak dimensions."""

    passed: bool = False
    """Whether this candidate passed the quality threshold."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "dimension_scores": self.dimension_scores,
            "weighted_total": self.weighted_total,
            "rationales": self.rationales,
            "risk_flags": self.risk_flags,
            "fix_it_plan": self.fix_it_plan,
            "passed": self.passed,
        }


@dataclass
class CriticConfig:
    """Configuration for the Critic agent's evaluation behavior."""

    weights: dict[str, float] = field(default_factory=lambda: {
        "visual_perception": 0.15,
        "technical_analysis": 0.20,
        "cultural_context": 0.25,
        "critical_interpretation": 0.20,
        "philosophical_aesthetic": 0.20,
    })
    pass_threshold: float = 0.4
    min_dimension_score: float = 0.2
    critical_risk_blocks: bool = True
    top_k: int = 1
    use_vlm: bool = True
    enable_agentic_vision: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "weights": self.weights,
            "pass_threshold": self.pass_threshold,
            "min_dimension_score": self.min_dimension_score,
            "critical_risk_blocks": self.critical_risk_blocks,
            "top_k": self.top_k,
            "use_vlm": self.use_vlm,
            "enable_agentic_vision": self.enable_agentic_vision,
        }


@dataclass
class LayerState:
    """Dynamic state for a single L-layer during pipeline execution."""

    layer_id: str
    score: float = 0.0
    confidence: float = 0.0
    evidence_coverage: float = 0.0
    volatility: float = 0.0
    locked: bool = False
    escalated: bool = False
    cost_spent_usd: float = 0.0
    analysis_text: str = ""
    _history: list[float] = field(default_factory=list)

    def record_score(self, score: float) -> None:
        """Record a new score observation."""
        self._history.append(score)
        self.score = score
        if len(self._history) >= 2:
            mean = sum(self._history) / len(self._history)
            self.volatility = sum((s - mean) ** 2 for s in self._history) / len(self._history)

    def priority(self) -> float:
        """Higher priority = lower confidence, needs more work."""
        return (1.0 - self.confidence) * (1.0 + self.volatility)

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "score": self.score,
            "confidence": self.confidence,
            "evidence_coverage": self.evidence_coverage,
            "volatility": self.volatility,
            "locked": self.locked,
            "escalated": self.escalated,
            "cost_spent_usd": self.cost_spent_usd,
        }
