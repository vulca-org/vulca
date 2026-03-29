"""Layer data types for VULCA layered artwork."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LayerInfo:
    """Definition of a single semantic layer."""
    name: str
    description: str
    bbox: dict  # {"x": int, "y": int, "w": int, "h": int} percentages
    z_index: int
    blend_mode: str = "normal"  # "normal", "screen", "multiply"
    bg_color: str = "white"     # generation background: "white", "black", "gray"
    locked: bool = False


@dataclass
class LayerResult:
    """A generated or decomposed layer with optional scores."""
    info: LayerInfo
    image_path: str
    scores: dict[str, float] = field(default_factory=dict)


@dataclass
class LayeredArtwork:
    """Complete layered artwork output."""
    composite_path: str
    layers: list[LayerResult]
    manifest_path: str
    brief: object | None = None  # Brief if from Studio
