"""Pipeline context + result types."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class DetectionRecord:
    """One entity's detection outcome — always populated, never silently dropped."""

    id: int
    name: str
    label: str
    semantic_path: str
    kind: str  # "person" | "object"
    status: str = "pending"  # "detected" | "missed" | "pending"
    detector: str | None = None
    bbox: list[int] | None = None
    det_score: float | None = None
    sam_score: float | None = None
    pct: float | None = None
    attempts: list[dict] = field(default_factory=list)
    matched_phrase: str | None = None
    reason: str | None = None

    def to_dict(self) -> dict:
        out = {k: v for k, v in self.__dict__.items() if v is not None and v != []}
        return out


@dataclass
class StageTiming:
    """Wall-clock timing for a single pipeline stage."""
    name: str
    seconds: float

    def to_dict(self) -> dict:
        return {"stage": self.name, "seconds": round(self.seconds, 3)}


@dataclass
class PipelineContext:
    """Immutable-ish state threaded through all stages.

    Created at the start of run(); stages add results in-place.
    """

    # Inputs
    plan: object  # Plan (typed), but kept as object to avoid circular import
    slug: str
    image_path: Path
    output_dir: Path
    device: str

    # Loaded once
    img_pil: object = None         # PIL.Image
    img_np: np.ndarray | None = None
    W: int = 0
    H: int = 0

    # Model handles (lazily populated)
    sam_pred: object | None = None
    dino: tuple | None = None      # (proc, model)
    yolo: object | None = None
    face_parser: tuple | None = None

    # Domain-derived config
    domain_profile: dict = field(default_factory=dict)

    # Stage outputs
    yolo_persons: list[tuple] = field(default_factory=list)   # list of (bbox, conf)
    dino_objects: dict = field(default_factory=dict)          # label -> (bbox, score, phrase)
    person_detector_used: str | None = None
    person_attempts: list[tuple] = field(default_factory=list)
    layers_raw: list[dict] = field(default_factory=list)
    detection_records: list[DetectionRecord] = field(default_factory=list)

    # Observability
    stage_timings: list[StageTiming] = field(default_factory=list)

    def time_stage(self, name: str):
        """Context manager for timing a stage."""
        return _StageTimer(self, name)


class _StageTimer:
    def __init__(self, ctx: PipelineContext, name: str):
        self.ctx = ctx
        self.name = name
        self.start = 0.0

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.ctx.stage_timings.append(StageTiming(self.name, time.time() - self.start))


@dataclass
class PipelineResult:
    """Final return value — mirrors manifest but with typed fields."""

    slug: str
    status: str                # "ok" | "partial" | "error"
    layers: list[dict]         # manifest layer dicts
    detection_report: dict
    stage_timings: list[dict]
    manifest_path: Path
    output_dir: Path
    reason: str | None = None  # for status="error"

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "status": self.status,
            "layers": self.layers,
            "detection_report": self.detection_report,
            "stage_timings": self.stage_timings,
            "manifest_path": str(self.manifest_path),
            "output_dir": str(self.output_dir),
            "reason": self.reason,
        }
