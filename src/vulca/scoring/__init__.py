"""VULCA scoring subsystem -- VLM critic, rules engine.

Public API::

    from vulca.scoring import CriticConfig, CritiqueOutput
    from vulca.scoring.vlm import score_image
"""

from vulca.scoring.types import (
    CriticConfig,
    CritiqueOutput,
    DimensionScore,
    LayerID,
    LayerState,
    DIMENSIONS,
)

__all__ = [
    "CriticConfig",
    "CritiqueOutput",
    "DimensionScore",
    "DIMENSIONS",
    "LayerID",
    "LayerState",
]
