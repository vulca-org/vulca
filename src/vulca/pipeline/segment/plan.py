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
# Note: "sam_bbox" added in plan_version 1 (same version, extra value allowed).
# Old plans without this value still validate. "auto" remains the default.
DETECTOR_VALUES = {"yolo", "dino", "auto", "sam_bbox"}
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
    detector: Literal["yolo", "dino", "auto", "sam_bbox"] = "auto"
    order: int | None = Field(None, description="Left-to-right rank for person matching")
    threshold: float | None = Field(None, ge=0.0, le=1.0,
                                     description="Override detection threshold")
    # A+B: spatial hint for stylized/silhouette content where detectors fail.
    # Normalized [x1, y1, x2, y2] in [0, 1]. If detector="sam_bbox", used as
    # direct SAM bbox (skips YOLO/DINO). Else: fallback after detector chain.
    bbox_hint_pct: list[float] | None = Field(
        None,
        description="Rough spatial hint [x1_pct, y1_pct, x2_pct, y2_pct] in [0,1]. "
                    "Used as SAM bbox when detector='sam_bbox' or as fallback."
    )
    # v0.18.0 (Q2 in design spec): opt-in to per-instance detection. When True,
    # the orchestrator routes this entity through DINO with a list-form
    # response (up to 8 bboxes per Q4 cap) instead of the legacy top-1 tuple.
    # Absent or False preserves legacy single-instance behavior; no plan
    # version bump required.
    multi_instance: bool = Field(
        False,
        description="If True, detect up to 8 instances of this label and emit "
                    "one layer per instance. Default False (legacy top-1)."
    )

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

    @field_validator("bbox_hint_pct")
    @classmethod
    def _check_bbox_hint(cls, v):
        if v is None:
            return v
        if not isinstance(v, list) or len(v) != 4:
            raise ValueError("bbox_hint_pct must be a 4-element list [x1, y1, x2, y2]")
        x1, y1, x2, y2 = v
        for name, val in (("x1", x1), ("y1", y1), ("x2", x2), ("y2", y2)):
            if not isinstance(val, (int, float)):
                raise ValueError(f"bbox_hint_pct.{name} must be numeric, got {type(val).__name__}")
            if not (0.0 <= float(val) <= 1.0):
                raise ValueError(f"bbox_hint_pct.{name}={val} must be in [0.0, 1.0]")
        if x1 >= x2 or y1 >= y2:
            raise ValueError(
                f"bbox_hint_pct invalid: x1={x1} must be < x2={x2}, y1={y1} must be < y2={y2}"
            )
        if (x2 - x1) * (y2 - y1) < 0.001:  # < 0.1% of image area
            raise ValueError(
                f"bbox_hint_pct area {(x2-x1)*(y2-y1):.4f} is too small (<0.1% of image)"
            )
        return [float(x) for x in v]

    @model_validator(mode="after")
    def _sam_bbox_requires_hint(self):
        if self.detector == "sam_bbox" and self.bbox_hint_pct is None:
            raise ValueError(
                f"entity {self.name!r}: detector='sam_bbox' requires bbox_hint_pct"
            )
        return self


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
    # Phase 1.6: hierarchical resolve emits a synthetic `residual` layer when
    # unclaimed pixels exceed this percentage of the canvas. Threshold floor
    # 2.0% chosen to avoid MPS nondeterminism flap at the 0.5% boundary (edge
    # feathering can shift SAM mask by ±0.1-0.3% run-to-run). Lower it for
    # finer-grained residual reporting; higher it to suppress noise.
    unclaimed_threshold_pct: float = Field(2.0, ge=0.0, le=50.0)

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

    @model_validator(mode="after")
    def _unique_semantic_paths(self):
        """Hierarchical layer model relies on semantic_path → parent mapping.
        Duplicates would make parent_layer_id resolution ambiguous (first-wins
        today, which could silently mis-link children). Empty paths are allowed
        (catch-all entities)."""
        paths = [e.semantic_path for e in self.entities if e.semantic_path]
        if len(paths) != len(set(paths)):
            dups = sorted({p for p in paths if paths.count(p) > 1})
            raise ValueError(f"duplicate semantic_path across entities: {dups}")
        return self

    @model_validator(mode="after")
    def _unique_labels_when_multi_instance(self):
        """Reject plans where 2+ multi_instance entities share the same label.

        DINO returns one bbox-list per label, so two multi_instance entities
        with the same label would each iterate the same N detections and emit
        identical bbox/mask pairs under different filenames — silently masking
        the duplication as N×2 seemingly-distinct layers. Single-instance
        duplicate labels are allowed (caller may want to model two entities
        the detector sees as one bbox).
        """
        multi_labels = [e.label for e in self.entities if e.multi_instance]
        seen: set[str] = set()
        duplicates: set[str] = set()
        for lbl in multi_labels:
            if lbl in seen:
                duplicates.add(lbl)
            seen.add(lbl)
        if duplicates:
            raise ValueError(
                f"multi_instance entities must have unique labels; "
                f"duplicate labels found: {sorted(duplicates)}. "
                f"DINO returns one bbox-list per label, so 2+ multi_instance "
                f"entities with the same label would emit identical masks N times."
            )
        return self

    @model_validator(mode="after")
    def _reserved_names_and_paths(self):
        """Phase 1.9: `residual` is a pipeline-synthesized synthetic layer
        (emitted at z=1 for plan-uncovered pixels). User plans must not
        reuse this name or semantic_path — they would collide with the
        synthetic layer's PNG filename and parent lookup."""
        RESERVED = {"residual"}
        for e in self.entities:
            if e.name in RESERVED:
                raise ValueError(f"entity name {e.name!r} is reserved for pipeline-synthesized layers")
            if e.semantic_path in RESERVED:
                raise ValueError(f"semantic_path {e.semantic_path!r} is reserved")
        return self

    @classmethod
    def from_file(cls, path) -> "Plan":
        import json
        from pathlib import Path
        return cls.model_validate(json.loads(Path(path).read_text()))
