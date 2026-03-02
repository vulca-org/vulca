"""Draft Agent data types — DraftInput, DraftCandidate, DraftOutput."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.prototype.agents.draft_config import DraftConfig

__all__ = [
    "DraftCandidate",
    "DraftInput",
    "DraftOutput",
]


@dataclass
class DraftInput:
    """Input for the Draft Agent — derived from Intent Card + Scout Evidence."""

    task_id: str                      # Intent Card task_id
    subject: str                      # evaluation subject
    cultural_tradition: str           # cultural tradition key
    evidence: dict                    # ScoutEvidence.to_dict() output
    config: DraftConfig = field(default_factory=DraftConfig)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "subject": self.subject,
            "cultural_tradition": self.cultural_tradition,
            "evidence": self.evidence,
            "config": self.config.to_dict(),
        }


@dataclass
class DraftCandidate:
    """A single draft image candidate with full traceability metadata."""

    candidate_id: str       # "draft-{task_id}-{index}"
    prompt: str             # full prompt sent to model
    negative_prompt: str    # negative prompt
    seed: int               # random seed (fixed for reproducibility)
    width: int              # requested pixel width
    height: int             # requested pixel height
    steps: int              # sampling steps
    sampler: str            # sampler name
    model_ref: str          # model identifier
    image_path: str         # output image path (relative to checkpoints/draft/)

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "seed": self.seed,
            "width": self.width,
            "height": self.height,
            "steps": self.steps,
            "sampler": self.sampler,
            "model_ref": self.model_ref,
            "image_path": self.image_path,
        }


@dataclass
class DraftOutput:
    """Output of the Draft Agent — all candidates plus run metadata."""

    task_id: str
    candidates: list[DraftCandidate] = field(default_factory=list)
    created_at: str = ""              # ISO 8601
    latency_ms: int = 0               # total elapsed time
    model_ref: str = ""               # provider identifier
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "candidates": [c.to_dict() for c in self.candidates],
            "created_at": self.created_at,
            "latency_ms": self.latency_ms,
            "model_ref": self.model_ref,
            "success": self.success,
            "error": self.error,
        }
