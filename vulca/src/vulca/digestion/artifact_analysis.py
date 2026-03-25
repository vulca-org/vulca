"""ArtifactAnalysis — structured L1-L5 analysis per image artifact.

Every image (sketch, reference, concept, generation, final) gets analyzed
into these structured types. Used for signal extraction, trajectory analysis,
and cross-session evolution.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class L1Analysis:
    """Visual Perception — measurable visual structure."""
    composition_type: str = ""
    focal_points: list[dict] = field(default_factory=list)
    negative_space_ratio: float = 0.0
    depth_layers: list[str] = field(default_factory=list)
    color_dominance: list[dict] = field(default_factory=list)
    contrast_level: str = ""
    balance: str = ""
    visual_flow: str = ""


@dataclass
class L2Analysis:
    """Technical Execution — craft quality indicators."""
    stroke_style: str = ""
    pressure_variation: str = ""
    detail_level: str = ""
    medium_indicators: list[str] = field(default_factory=list)
    texture_qualities: list[str] = field(default_factory=list)
    rendering_consistency: float = 0.0
    technical_difficulty: str = ""


@dataclass
class L3Analysis:
    """Cultural Context — cultural elements and tradition alignment."""
    cultural_elements: list[dict] = field(default_factory=list)
    tradition_alignment: dict[str, float] = field(default_factory=dict)
    cultural_techniques: list[str] = field(default_factory=list)
    taboo_violations: list[str] = field(default_factory=list)
    cultural_depth: str = ""
    cultural_fusion_quality: str = ""


@dataclass
class L4Analysis:
    """Critical Interpretation — narrative and creative intent."""
    narrative_theme: str = ""
    symbols: list[dict] = field(default_factory=list)
    creative_intent: str = ""
    reference_connections: list[str] = field(default_factory=list)
    conceptual_coherence: float = 0.0
    interpretive_depth: str = ""


@dataclass
class L5Analysis:
    """Philosophical Aesthetics — emotion, atmosphere, beauty."""
    mood: str = ""
    atmosphere: str = ""
    emotional_resonance: list[str] = field(default_factory=list)
    aesthetic_philosophy: str = ""
    viewer_experience: str = ""
    beauty_type: str = ""
    emotional_intensity: float = 0.0


@dataclass
class ArtifactAnalysis:
    """Per-artifact L1-L5 structural analysis."""
    artifact_id: str = ""
    artifact_type: str = ""  # sketch | reference | concept | generation | final
    session_id: str = ""
    l1: L1Analysis = field(default_factory=L1Analysis)
    l2: L2Analysis = field(default_factory=L2Analysis)
    l3: L3Analysis = field(default_factory=L3Analysis)
    l4: L4Analysis = field(default_factory=L4Analysis)
    l5: L5Analysis = field(default_factory=L5Analysis)
    model_used: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArtifactAnalysis:
        return cls(
            artifact_id=data.get("artifact_id", ""),
            artifact_type=data.get("artifact_type", ""),
            session_id=data.get("session_id", ""),
            l1=L1Analysis(**data["l1"]) if "l1" in data else L1Analysis(),
            l2=L2Analysis(**data["l2"]) if "l2" in data else L2Analysis(),
            l3=L3Analysis(**data["l3"]) if "l3" in data else L3Analysis(),
            l4=L4Analysis(**data["l4"]) if "l4" in data else L4Analysis(),
            l5=L5Analysis(**data["l5"]) if "l5" in data else L5Analysis(),
            model_used=data.get("model_used", ""),
            created_at=data.get("created_at", ""),
        )

    @staticmethod
    def build_analysis_prompt(artifact_type: str = "", intent: str = "") -> str:
        """Build a VLM prompt for structured L1-L5 analysis of an image."""
        return (
            "Analyze this artwork image and return structured JSON with L1-L5 dimensions.\n\n"
            f"Artifact type: {artifact_type or 'unknown'}\n"
            f"Creative intent: {intent or 'not specified'}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "l1": {"composition_type": "<str>", "focal_points": [{"position":"<str>","element":"<str>"}], '
            '"negative_space_ratio": <0-1>, "depth_layers": ["<str>"], '
            '"color_dominance": [{"hex":"<str>","area_ratio":<0-1>}], '
            '"contrast_level": "<high|medium|low>", "balance": "<str>", "visual_flow": "<str>"},\n'
            '  "l2": {"stroke_style": "<str>", "detail_level": "<sketch|draft|refined|finished>", '
            '"medium_indicators": ["<str>"], "rendering_consistency": <0-1>},\n'
            '  "l3": {"cultural_elements": [{"name":"<str>","category":"<str>","tradition":"<str>"}], '
            '"tradition_alignment": {"<tradition>": <0-1>}, "cultural_depth": "<surface|integrated|deep>"},\n'
            '  "l4": {"narrative_theme": "<str>", "symbols": [{"element":"<str>","meaning":"<str>"}], '
            '"conceptual_coherence": <0-1>},\n'
            '  "l5": {"mood": "<str>", "atmosphere": "<str>", "emotional_resonance": ["<str>"], '
            '"beauty_type": "<sublime|elegant|raw|harmonious|uncanny>", "emotional_intensity": <0-1>}\n'
            "}"
        )
