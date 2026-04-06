"""Layer data types for VULCA layered artwork."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field


def _default_layer_id() -> str:
    return "layer_" + uuid.uuid4().hex[:8]


@dataclass
class LayerInfo:
    """Definition of a single semantic layer."""
    name: str
    description: str
    z_index: int
    id: str = field(default_factory=_default_layer_id)
    content_type: str = "background"   # free-form: VLM assigns label based on image content
    dominant_colors: list[str] = field(default_factory=list)  # hex strings
    regeneration_prompt: str = ""
    visible: bool = True
    blend_mode: str = "normal"         # "normal", "screen", "multiply"
    bg_color: str = "white"            # generation background: "white", "black", "gray"
    locked: bool = False
    bbox: dict | None = None           # {"x": int, "y": int, "w": int, "h": int} — V1 compat only
    # Spatial transform (v0.12 — percentage-based, resolution-independent)
    x: float = 0.0                     # Canvas position X (0-100%)
    y: float = 0.0                     # Canvas position Y (0-100%)
    width: float = 100.0               # Layer width (0-100% of canvas)
    height: float = 100.0              # Layer height (0-100% of canvas)
    rotation: float = 0.0              # Rotation in degrees (clockwise)
    content_bbox: dict | None = None   # Auto-computed: {"x": px, "y": px, "w": px, "h": px}
    # V3 fields (Artifact V3 structured creation)
    tradition_role: str = ""               # Cultural layer role e.g. "远景淡墨"
    opacity: float = 1.0                   # Layer opacity 0.0-1.0
    status: str = ""                       # "accepted" | "rerun" | "failed" | ""
    weakness: str = ""                     # Actionable feedback from DecideNode
    generation_round: int = 0              # Which round produced this layer


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
    brief: object | None = None        # Brief if from Studio
    source_image: str = ""             # V2: origin image path (img2img / decompose)
    split_mode: str = ""               # V2: how layers were split ("vlm_semantic", "depth", etc.)
