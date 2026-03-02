"""LayerState — L1-L5 dynamic state model for v2 cognitive engine.

Each layer maintains its own state machine (score, confidence, evidence_coverage,
volatility, locked, escalated, cost). The priority formula drives dynamic scheduling:

    priority_d = w_d * (1 - score_d) * (1 - confidence_d) * risk_d

Budget allocation uses softmax over priorities to tilt resources toward
low-score / low-confidence / high-risk layers.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

from app.prototype.agents.critic_config import DIMENSIONS

__all__ = [
    "CrossLayerSignal",
    "IntentCardV2",
    "LayerID",
    "LayerState",
    "LocalRerunRequest",
    "SignalType",
    "compute_budget_allocation",
    "init_layer_states",
]


# ---------------------------------------------------------------------------
# Layer identifiers
# ---------------------------------------------------------------------------

class LayerID(str, Enum):
    """Canonical L1-L5 identifiers (match DIMENSIONS in critic_config)."""

    L1 = "visual_perception"
    L2 = "technical_analysis"
    L3 = "cultural_context"
    L4 = "critical_interpretation"
    L5 = "philosophical_aesthetic"


# ---------------------------------------------------------------------------
# LayerState
# ---------------------------------------------------------------------------

@dataclass
class LayerState:
    """Dynamic state for a single L-layer within a pipeline run.

    Fields
    ------
    score : float
        Current layer score [0, 1].
    confidence : float
        Assessment confidence [0, 1].  Low confidence → likely escalation.
    evidence_coverage : float
        Fraction of required evidence retrieved [0, 1].
    volatility : float
        Cross-round score fluctuation [0, 1].  High → unstable.
    locked : bool
        Whether the user (HITL) has confirmed this layer's result.
    escalated : bool
        Whether this layer has been upgraded to LLM evaluation.
    cost_spent_usd : float
        Cumulative cost spent on this layer so far.
    """

    score: float = 0.0
    confidence: float = 0.0
    evidence_coverage: float = 0.0
    volatility: float = 0.0
    locked: bool = False
    escalated: bool = False
    cost_spent_usd: float = 0.0
    analysis_text: str = ""  # v2: Agent's textual analysis for cross-layer reading

    # --- History for volatility tracking ---
    _score_history: list[float] = field(default_factory=list, repr=False)

    def record_score(self, new_score: float) -> None:
        """Record a new score and update volatility."""
        self._score_history.append(new_score)
        self.score = new_score
        if len(self._score_history) >= 2:
            diffs = [
                abs(self._score_history[i] - self._score_history[i - 1])
                for i in range(1, len(self._score_history))
            ]
            self.volatility = min(1.0, sum(diffs) / len(diffs))

    def priority(self, weight: float, risk: float = 1.0) -> float:
        """Compute scheduling priority for this layer.

        Higher priority → more budget / earlier escalation.
        """
        return weight * (1.0 - self.score) * (1.0 - self.confidence) * risk

    def should_escalate(
        self,
        tau_priority: float = 0.15,
        tau_coverage: float = 0.3,
        weight: float = 0.2,
    ) -> bool:
        """Determine whether this layer should escalate to LLM evaluation."""
        if self.locked or self.escalated:
            return False
        # Never escalate layers that haven't been scored yet
        if not self._score_history:
            return False
        if self.priority(weight) > tau_priority:
            return True
        if self.evidence_coverage < tau_coverage:
            return True
        return False

    def to_dict(self) -> dict:
        d = {
            "score": round(self.score, 4),
            "confidence": round(self.confidence, 4),
            "evidence_coverage": round(self.evidence_coverage, 4),
            "volatility": round(self.volatility, 4),
            "locked": self.locked,
            "escalated": self.escalated,
            "cost_spent_usd": round(self.cost_spent_usd, 6),
        }
        if self.analysis_text:
            d["analysis_text"] = self.analysis_text[:500]
        return d

    def get_accumulated_context(
        self,
        all_states: dict[str, "LayerState"] | None = None,
        up_to: str | None = None,
    ) -> str:
        """Build accumulated analysis context from prior layers.

        Parameters
        ----------
        all_states : dict mapping dim_id -> LayerState
        up_to : dim_id — include all layers before this one in L1→L5 order

        Returns accumulated text from completed prior layers.
        """
        if all_states is None:
            return ""

        _ORDER = [
            "visual_perception",
            "technical_analysis",
            "cultural_context",
            "critical_interpretation",
            "philosophical_aesthetic",
        ]
        _LABELS = {
            "visual_perception": "L1",
            "technical_analysis": "L2",
            "cultural_context": "L3",
            "critical_interpretation": "L4",
            "philosophical_aesthetic": "L5",
        }

        parts: list[str] = []
        for dim in _ORDER:
            if dim == up_to:
                break
            ls = all_states.get(dim)
            if ls and ls.analysis_text:
                parts.append(
                    f"### {_LABELS.get(dim, dim)} Analysis (score={ls.score:.3f}, confidence={ls.confidence:.3f})\n"
                    f"{ls.analysis_text}"
                )
        return "\n\n".join(parts) if parts else ""


# ---------------------------------------------------------------------------
# IntentCardV2
# ---------------------------------------------------------------------------

@dataclass
class IntentCardV2:
    """Front-loaded intent analysis output from Queen-Intent stage.

    Determines the target profile, mandatory layers, budget plan,
    and pipeline variant before any generation begins.
    """

    target_profile: dict[str, float] = field(default_factory=dict)
    must_pass_layers: list[str] = field(default_factory=list)
    budget_plan: dict[str, float] = field(default_factory=dict)
    pipeline_variant: str = "default"  # "default" | "chinese_xieyi" | "western_academic"

    def to_dict(self) -> dict:
        return {
            "target_profile": self.target_profile,
            "must_pass_layers": self.must_pass_layers,
            "budget_plan": {k: round(v, 6) for k, v in self.budget_plan.items()},
            "pipeline_variant": self.pipeline_variant,
        }


# ---------------------------------------------------------------------------
# CrossLayerSignal
# ---------------------------------------------------------------------------

class SignalType(str, Enum):
    """Types of cross-layer information flow."""

    REINTERPRET = "reinterpret"       # Higher layer asks lower layer to re-evaluate
    EVIDENCE_GAP = "evidence_gap"     # Layer lacks evidence → Scout should expand
    CONFLICT = "conflict"             # Two judges disagree on this layer
    CONFIRMATION = "confirmation"     # Higher layer confirms lower layer finding


@dataclass
class CrossLayerSignal:
    """A signal passed between layers during the cognitive pipeline."""

    source_layer: str          # e.g. "L5"
    target_layer: str          # e.g. "L1"
    signal_type: SignalType
    message: str = ""
    strength: float = 1.0      # [0, 1] — how strongly to weight this signal

    def to_dict(self) -> dict:
        return {
            "source_layer": self.source_layer,
            "target_layer": self.target_layer,
            "signal_type": self.signal_type.value,
            "message": self.message,
            "strength": round(self.strength, 4),
        }


# ---------------------------------------------------------------------------
# LocalRerunRequest
# ---------------------------------------------------------------------------

@dataclass
class LocalRerunRequest:
    """Request for a targeted local rerun (vs full re-generation)."""

    base_candidate_id: str
    target_layers: list[str] = field(default_factory=list)
    preserve_layers: list[str] = field(default_factory=list)
    mask_specs: list[dict] = field(default_factory=list)
    prompt_delta: str = ""
    negative_delta: str = ""
    structure_constraints: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "base_candidate_id": self.base_candidate_id,
            "target_layers": self.target_layers,
            "preserve_layers": self.preserve_layers,
            "mask_specs": self.mask_specs,
            "prompt_delta": self.prompt_delta,
            "negative_delta": self.negative_delta,
            "structure_constraints": self.structure_constraints,
        }


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def init_layer_states() -> dict[str, LayerState]:
    """Create a fresh set of L1-L5 LayerState objects."""
    return {dim: LayerState() for dim in DIMENSIONS}


def compute_budget_allocation(
    layer_states: dict[str, LayerState],
    weights: dict[str, float],
    remaining_budget: float,
    alpha: float = 2.0,
    business_weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """Allocate remaining budget across layers using softmax over priorities.

    Parameters
    ----------
    layer_states : dict mapping dimension ID → LayerState
    weights : dict mapping dimension ID → base weight
    remaining_budget : float in USD
    alpha : float — temperature for softmax (higher = more concentrated)
    business_weights : optional per-layer business importance multiplier

    Returns
    -------
    dict mapping dimension ID → allocated budget in USD
    """
    bw = business_weights or {}
    priorities: dict[str, float] = {}

    for dim, ls in layer_states.items():
        w = weights.get(dim, 0.2)
        b = bw.get(dim, 1.0)
        priorities[dim] = ls.priority(w) * b

    # Softmax normalization
    max_p = max(priorities.values()) if priorities else 0.0
    exp_p = {dim: math.exp(alpha * (p - max_p)) for dim, p in priorities.items()}
    total_exp = sum(exp_p.values())

    if total_exp < 1e-12:
        # Uniform allocation
        n = len(layer_states)
        return {dim: remaining_budget / n for dim in layer_states}

    return {
        dim: remaining_budget * (exp_p[dim] / total_exp)
        for dim in layer_states
    }
