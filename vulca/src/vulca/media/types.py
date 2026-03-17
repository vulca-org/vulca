"""Media subsystem types -- MediaType, SubStageDef, SubStageArtifact, CreationRecipe."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MediaType(str, Enum):
    """Supported media types for creation pipelines."""

    IMAGE = "image"
    VIDEO = "video"
    MODEL_3D = "3d_model"
    SOUND = "sound"


@dataclass(frozen=True)
class SubStageDef:
    """Definition of a single sub-stage within a creation recipe.

    Sub-stages are executed in order, and each can produce an artifact
    that downstream sub-stages can consume via input_artifact_names.
    """

    name: str
    display_name: str
    description: str
    order: int
    required: bool = True
    input_artifact_names: tuple[str, ...] = ()
    output_artifact_type: str = "image"
    estimated_latency_ms: int = 5000

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "order": self.order,
            "required": self.required,
            "input_artifact_names": list(self.input_artifact_names),
            "output_artifact_type": self.output_artifact_type,
            "estimated_latency_ms": self.estimated_latency_ms,
        }


@dataclass
class SubStageArtifact:
    """Artifact produced by a single sub-stage execution."""

    stage_name: str
    artifact_type: str
    data: Any = None
    image_path: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = {
            "stage_name": self.stage_name,
            "artifact_type": self.artifact_type,
            "data": str(self.data) if self.data is not None else None,
            "metadata": self.metadata,
        }
        if self.image_path:
            d["image_path"] = self.image_path
        return d


@dataclass
class SubStageResult:
    """Result of executing a single sub-stage."""

    stage_name: str
    status: str = "pending"
    artifact: SubStageArtifact | None = None
    duration_ms: int = 0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_name": self.stage_name,
            "status": self.status,
            "artifact": self.artifact.to_dict() if self.artifact else None,
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


@dataclass(frozen=True)
class CreationRecipe:
    """A complete recipe defining sub-stages for a media type creation pipeline.

    Recipes are immutable and registered in the RECIPE_REGISTRY.
    """

    media_type: MediaType
    name: str
    display_name: str
    sub_stages: tuple[SubStageDef, ...]
    version: str = "1.0.0"

    def __post_init__(self) -> None:
        orders = [s.order for s in self.sub_stages]
        if orders != sorted(orders):
            raise ValueError(f"Sub-stages must be in ascending order, got: {orders}")
        names = [s.name for s in self.sub_stages]
        if len(names) != len(set(names)):
            raise ValueError(f"Sub-stage names must be unique, got duplicates in: {names}")

    def get_stage_by_name(self, name: str) -> SubStageDef | None:
        for stage in self.sub_stages:
            if stage.name == name:
                return stage
        return None

    def stage_names(self) -> list[str]:
        return [s.name for s in self.sub_stages]

    def to_dict(self) -> dict[str, Any]:
        return {
            "media_type": self.media_type.value,
            "name": self.name,
            "display_name": self.display_name,
            "sub_stages": [s.to_dict() for s in self.sub_stages],
            "version": self.version,
        }
