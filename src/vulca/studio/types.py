"""Supporting data types for the Studio pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StyleWeight:
    """A weighted style reference in a Brief's style_mix."""
    tradition: str = ""
    tag: str = ""
    weight: float = 0.5


@dataclass
class Reference:
    """A reference image attached to a Brief."""
    path: str
    source: str
    query: str = ""
    prompt: str = ""
    url: str = ""
    note: str = ""


@dataclass
class Composition:
    """Composition specification within a Brief."""
    layout: str = ""
    focal_point: str = ""
    aspect_ratio: str = "1:1"
    negative_space: str = ""


@dataclass
class Palette:
    """Color palette specification within a Brief."""
    primary: list[str] = field(default_factory=list)
    accent: list[str] = field(default_factory=list)
    mood: str = ""


@dataclass
class Element:
    """A creative element to include in the artwork."""
    name: str
    category: str = ""
    note: str = ""


@dataclass
class GenerationRound:
    """Record of one generation+evaluation round."""
    round_num: int
    image_path: str
    scores: dict[str, float] = field(default_factory=dict)
    suggestions: dict[str, str] = field(default_factory=dict)
    feedback: str = ""


@dataclass
class BriefUpdate:
    """Record of a natural language update to the Brief."""
    timestamp: str
    instruction: str
    fields_changed: list[str] = field(default_factory=list)
    rollback_to: str = ""
