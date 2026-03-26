"""VULCA scoring subsystem -- VLM critic, rules engine, model routing.

Public API::

    from vulca.scoring import CriticConfig, CritiqueOutput, ModelRouter
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
from vulca.scoring.model_router import ModelRouter, ModelSpec
from vulca.scoring.sparse import BriefIndexer, DimensionActivation

__all__ = [
    "CriticConfig",
    "CritiqueOutput",
    "DimensionScore",
    "DIMENSIONS",
    "LayerID",
    "LayerState",
    "ModelRouter",
    "ModelSpec",
    "BriefIndexer",
    "DimensionActivation",
]
