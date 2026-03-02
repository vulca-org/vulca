"""FixItPlan — structured repair protocol between Critic and Draft.

Layer 1b: Critic outputs a targeted FixItPlan when scores are low,
Draft consumes it during rerun to make precise corrections instead
of blind re-generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "FixItem",
    "FixItPlan",
]


@dataclass
class FixItem:
    """A single targeted repair instruction."""

    target_layer: str  # e.g. "L2", "L3"
    issue: str  # what's wrong
    prompt_delta: str  # what to add/change in the prompt
    mask_region_hint: str  # "full"(L1), "centre"(L2), "foreground"(L3), "upper"(L4), "diffuse"(L5)
    reference_suggestion: str  # optional reference for improvement
    priority: int  # 1=highest
    strength: float = 1.0  # mask opacity [0.0, 1.0] for this layer

    def to_dict(self) -> dict:
        return {
            "target_layer": self.target_layer,
            "issue": self.issue,
            "prompt_delta": self.prompt_delta,
            "mask_region_hint": self.mask_region_hint,
            "reference_suggestion": self.reference_suggestion,
            "priority": self.priority,
            "strength": round(self.strength, 2),
        }

    @classmethod
    def from_dict(cls, d: dict) -> FixItem:
        return cls(
            target_layer=d["target_layer"],
            issue=d.get("issue", ""),
            prompt_delta=d.get("prompt_delta", ""),
            mask_region_hint=d.get("mask_region_hint", ""),
            reference_suggestion=d.get("reference_suggestion", ""),
            priority=d.get("priority", 5),
            strength=d.get("strength", 1.0),
        )


@dataclass
class FixItPlan:
    """Aggregated repair plan from Critic to Draft.

    Contains ordered fix items and an overall strategy recommendation.
    """

    items: list[FixItem] = field(default_factory=list)
    overall_strategy: str = "targeted_inpaint"  # "targeted_inpaint" | "full_regenerate"
    estimated_improvement: float = 0.0  # estimated score delta
    source_scores: dict[str, float] = field(default_factory=dict)  # layer -> score

    def to_prompt_delta(self) -> str:
        """Merge all fix items into a single prompt enhancement string."""
        sorted_items = sorted(self.items, key=lambda x: x.priority)
        deltas = [item.prompt_delta for item in sorted_items if item.prompt_delta]
        return ", ".join(deltas) if deltas else ""

    def get_mask_hint(self) -> str:
        """Return the mask region hint from the highest-priority fix item."""
        if not self.items:
            return ""
        sorted_items = sorted(self.items, key=lambda x: x.priority)
        for item in sorted_items:
            if item.mask_region_hint:
                return item.mask_region_hint
        return ""

    def get_negative_additions(self) -> list[str]:
        """Extract issue descriptions that should be avoided."""
        return [item.issue for item in self.items if item.issue]

    def to_dict(self) -> dict:
        return {
            "items": [item.to_dict() for item in self.items],
            "overall_strategy": self.overall_strategy,
            "estimated_improvement": round(self.estimated_improvement, 4),
            "source_scores": {k: round(v, 4) for k, v in self.source_scores.items()},
        }

    @classmethod
    def from_dict(cls, d: dict) -> FixItPlan:
        return cls(
            items=[FixItem.from_dict(i) for i in d.get("items", [])],
            overall_strategy=d.get("overall_strategy", "targeted_inpaint"),
            estimated_improvement=d.get("estimated_improvement", 0.0),
            source_scores=d.get("source_scores", {}),
        )
