"""Typed segmentation plan with Pydantic validation.

Plans are authored by Claude (or an API client) and describe *what* entities
to extract from an image. The pipeline consumes this plan and routes each
entity through detector → SAM → (optional) face-parsing.
"""
from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


DEFAULT_PLAN_VERSION = 1
DETECTOR_VALUES = {"yolo", "dino", "auto"}
DEVICE_VALUES = {"cpu", "mps", "cuda"}


def _sanitize_name(raw: str) -> str:
    """Strip path-traversal characters from a plan-controlled name.

    Layer names become filenames; `../` / `/` / null bytes / shell chars
    MUST be removed. Keep alphanum, underscore, dash, dot, bracket (for
    semantic path like `person[0]` — brackets are FS-safe).
    """
    clean = re.sub(r"[^A-Za-z0-9._\[\]-]", "_", raw)
    clean = clean.strip("._-")
    if not clean:
        return "unnamed"
    return clean[:80]  # hard cap


class PlanEntity(BaseModel):
    """One entity the pipeline should try to detect + segment."""

    model_config = {"extra": "forbid"}  # reject unknown keys — catch typos

    name: str = Field(..., description="Short identifier used as filename stem")
    label: str = Field(..., description="Natural-language description for detectors")
    semantic_path: str = Field("", description="Dot-notation path e.g. subject.person[0]")
    detector: Literal["yolo", "dino", "auto"] = "auto"
    order: int | None = Field(None, description="Left-to-right rank for person matching")
    threshold: float | None = Field(None, ge=0.0, le=1.0,
                                     description="Override detection threshold")

    @field_validator("name", mode="before")
    @classmethod
    def _sanitize_name_field(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("name must be a string")
        sanitized = _sanitize_name(v)
        if sanitized != v:
            # Fail loud on suspicious input rather than silently rewrite
            raise ValueError(
                f"name {v!r} contains unsafe characters; use only alphanum/./_/-/[]"
            )
        return v

    @field_validator("semantic_path")
    @classmethod
    def _check_sp(cls, v: str) -> str:
        if v and not re.match(r"^[A-Za-z0-9._\[\]-]+$", v):
            raise ValueError(f"semantic_path {v!r} has invalid characters")
        return v


class Plan(BaseModel):
    """Full segmentation plan for one image."""

    model_config = {"extra": "forbid"}

    plan_version: int = Field(DEFAULT_PLAN_VERSION,
                              description="Schema version; bumped on breaking changes")
    slug: str | None = None
    domain: str = Field("", description="e.g. renaissance_painting, historical_bw_photo")
    device: Literal["cpu", "mps", "cuda"] = "mps"
    notes: str = ""

    # Runtime tuning
    threshold_hint: float = Field(0.20, ge=0.0, le=1.0)
    expand_face_parts: bool = True
    soften_edges: bool = True

    # The actual work list
    entities: list[PlanEntity] = Field(..., min_length=1)

    @field_validator("slug", mode="before")
    @classmethod
    def _sanitize_slug(cls, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("slug must be a string")
        clean = _sanitize_name(v)
        if clean != v:
            raise ValueError(f"slug {v!r} has unsafe characters")
        return v

    @model_validator(mode="after")
    def _unique_entity_names(self):
        names = [e.name for e in self.entities]
        if len(names) != len(set(names)):
            dups = [n for n in names if names.count(n) > 1]
            raise ValueError(f"duplicate entity names: {set(dups)}")
        return self

    @classmethod
    def from_file(cls, path) -> "Plan":
        import json
        from pathlib import Path
        return cls.model_validate(json.loads(Path(path).read_text()))
