"""CriticConfig — L1-L5 weights, gate thresholds, and risk policy."""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "CriticConfig",
    "DIMENSIONS",
]


# L1-L5 dimension IDs (canonical order)
DIMENSIONS: list[str] = [
    "visual_perception",        # L1
    "technical_analysis",       # L2
    "cultural_context",         # L3
    "critical_interpretation",  # L4
    "philosophical_aesthetic",  # L5
]


def _default_weights() -> dict[str, float]:
    return {
        "visual_perception": 0.15,
        "technical_analysis": 0.20,
        "cultural_context": 0.25,         # highest — VULCA cross-cultural focus
        "critical_interpretation": 0.20,
        "philosophical_aesthetic": 0.20,
    }


@dataclass
class CriticConfig:
    """Configuration for the Critic Agent scoring and gating."""

    weights: dict[str, float] = field(default_factory=_default_weights)
    pass_threshold: float = 0.4           # weighted total >= 0.4 to pass
    min_dimension_score: float = 0.2      # any dimension < 0.2 is hard reject
    critical_risk_blocks: bool = True     # critical risk tag → auto reject
    top_k: int = 1                        # select top-k passing candidates
    use_vlm: bool = True                   # use VLM scoring if available (False = CLIP only)
    enable_agentic_vision: bool = False    # deep Think→Act→Observe analysis (L1/L3/L5)

    def __post_init__(self) -> None:
        total = sum(self.weights.values())
        if abs(total - 1.0) > 1e-6:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def to_dict(self) -> dict:
        return {
            "weights": self.weights,
            "pass_threshold": self.pass_threshold,
            "min_dimension_score": self.min_dimension_score,
            "critical_risk_blocks": self.critical_risk_blocks,
            "top_k": self.top_k,
            "use_vlm": self.use_vlm,
            "enable_agentic_vision": self.enable_agentic_vision,
        }
