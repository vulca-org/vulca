"""DSA-inspired sparse evaluation: determine which L-dimensions to score.

Inspired by DeepSeek's Dynamic Sparse Attention Lightning Indexer.
Uses deterministic keyword matching (zero LLM cost) to determine
which L1-L5 dimensions are relevant to a given Brief.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DimensionActivation:
    """Which dimensions to evaluate and why."""
    active: dict[str, float] = field(default_factory=dict)
    skipped: dict[str, str] = field(default_factory=dict)
    method: str = "brief_indexed"


_PADDING_PRIORITY = ["L1", "L3", "L5", "L2", "L4"]
_PAD_CONFIDENCE = 0.3
_FORCED_L3_CONFIDENCE = 0.9


class BriefIndexer:
    """DSA Lightning Indexer for VULCA: determine active L-dimensions."""

    DIMENSION_SIGNALS: dict[str, list[str]] = {
        "L1": ["构图", "composition", "布局", "layout", "留白", "色彩", "对比", "balance", "focal", "空间"],
        "L2": ["笔法", "technique", "笔触", "stroke", "肌理", "texture", "工笔", "写意", "媒介", "rendering"],
        "L3": ["文化", "cultural", "传统", "tradition", "符号", "symbol", "禁忌", "taboo", "仪式", "ritual"],
        "L4": ["叙事", "narrative", "故事", "story", "象征", "意境", "conceptual", "allegory", "寓意"],
        "L5": ["情感", "emotion", "氛围", "mood", "atmosphere", "意趣", "韵味", "感染力", "beauty"],
    }

    def index(self, brief_text: str, tradition: str = "", min_dimensions: int = 3) -> DimensionActivation:
        text_lower = brief_text.lower()
        scores: dict[str, float] = {}

        for dim, signals in self.DIMENSION_SIGNALS.items():
            matched = sum(1 for s in signals if s.lower() in text_lower)
            if matched > 0:
                scores[dim] = matched / len(signals)

        if tradition:
            if "L3" not in scores:
                scores["L3"] = _FORCED_L3_CONFIDENCE
            else:
                scores["L3"] = max(scores["L3"], _FORCED_L3_CONFIDENCE)

        if len(scores) < min_dimensions:
            for dim in _PADDING_PRIORITY:
                if dim not in scores:
                    scores[dim] = _PAD_CONFIDENCE
                if len(scores) >= min_dimensions:
                    break

        all_dims = {"L1", "L2", "L3", "L4", "L5"}
        active = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
        skipped = {dim: "no_signal" for dim in sorted(all_dims - set(active))}

        return DimensionActivation(active=active, skipped=skipped, method="brief_indexed")
