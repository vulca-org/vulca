"""Multi-modal type system and sub-stage architecture.

Provides MediaType enum, sub-stage definitions, creation recipes,
and the SubStageExecutor runtime for multi-step creation pipelines.
"""

from app.prototype.media.types import (
    CreationRecipe,
    MediaType,
    SubStageArtifact,
    SubStageDef,
    SubStageResult,
)
from app.prototype.media.recipes import (
    AVAILABLE_MEDIA_TYPES,
    RECIPE_REGISTRY,
    get_default_recipe,
    get_recipe,
)
try:
    from app.prototype.media.sub_stage_executor import SubStageExecutor
except ImportError:
    SubStageExecutor = None  # type: ignore[misc,assignment]

__all__ = [
    "CreationRecipe",
    "MediaType",
    "SubStageArtifact",
    "SubStageDef",
    "SubStageResult",
    "AVAILABLE_MEDIA_TYPES",
    "RECIPE_REGISTRY",
    "SubStageExecutor",
    "get_default_recipe",
    "get_recipe",
]
