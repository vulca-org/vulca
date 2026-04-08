"""Cultural subsystem types -- tradition configs, terminology, taboos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TermEntry:
    """A cultural terminology entry."""

    term: str
    term_zh: str = ""
    definition: str | dict[str, str] = ""
    category: str = ""
    l_levels: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "term": self.term,
            "term_zh": self.term_zh,
            "definition": self.definition,
            "category": self.category,
            "l_levels": self.l_levels,
            "aliases": self.aliases,
            "source": self.source,
        }


@dataclass
class TabooEntry:
    """A cultural taboo rule."""

    rule: str
    severity: str = "medium"
    l_levels: list[str] = field(default_factory=list)
    trigger_patterns: list[str] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "l_levels": self.l_levels,
            "trigger_patterns": self.trigger_patterns,
            "explanation": self.explanation,
        }


@dataclass
class PipelineConfig:
    """Pipeline variant configuration for a tradition."""

    variant: str = "default"
    overrides: dict[str, Any] = field(default_factory=dict)


@dataclass
class TraditionConfig:
    """Complete definition of a cultural tradition.

    Loaded from YAML files in cultural/data/traditions/.
    """

    name: str
    display_name: dict[str, str] = field(default_factory=lambda: {"en": "", "zh": ""})
    weights_l: dict[str, float] = field(default_factory=lambda: {
        "L1": 0.15, "L2": 0.20, "L3": 0.25, "L4": 0.20, "L5": 0.20,
    })
    terminology: list[TermEntry] = field(default_factory=list)
    taboos: list[TabooEntry] = field(default_factory=list)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    examples: list[dict[str, str]] = field(default_factory=list)
    extra_dimensions: list[dict] = field(default_factory=list)

    # Layered generation config (v0.13)
    layerability: str = "split"
    canvas_color: str = "#ffffff"
    canvas_description: str = ""
    key_strategy: str = "luminance"
    style_keywords: str = ""

    # Dimension name mapping: L-code -> snake_case
    _L_TO_DIM: dict[str, str] = field(default_factory=dict, repr=False, init=False)

    def __post_init__(self) -> None:
        self._L_TO_DIM = {
            "L1": "visual_perception",
            "L2": "technical_analysis",
            "L3": "cultural_context",
            "L4": "critical_interpretation",
            "L5": "philosophical_aesthetic",
        }

    @property
    def weights_dim(self) -> dict[str, float]:
        """Return weights keyed by dimension snake_case name."""
        return {
            self._L_TO_DIM.get(k, k): v
            for k, v in self.weights_l.items()
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "weights_l": self.weights_l,
            "terminology": [t.to_dict() for t in self.terminology],
            "taboos": [t.to_dict() for t in self.taboos],
            "pipeline": {"variant": self.pipeline.variant, "overrides": self.pipeline.overrides},
            "examples": self.examples,
        }
