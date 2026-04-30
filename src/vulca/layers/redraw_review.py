"""Product-level review contract for redraw results."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping

ReviewState = Literal[
    "ready_for_review",
    "technical_preview",
    "unknown_quality_preview",
    "layer_only_result",
    "pasteback_warning",
]


@dataclass(frozen=True)
class RedrawReview:
    state: ReviewState
    primary_after_path: str
    layer_asset_path: str
    source_pasteback_path: str
    source_pasteback_error: str
    show_as_final: bool
    quality_gate_passed: bool | None
    warnings: tuple[str, ...]
    refinement_applied: bool | None = None
    refined_child_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "state": self.state,
            "primary_after_path": self.primary_after_path,
            "layer_asset_path": self.layer_asset_path,
            "source_pasteback_path": self.source_pasteback_path,
            "source_pasteback_error": self.source_pasteback_error,
            "show_as_final": self.show_as_final,
            "quality_gate_passed": self.quality_gate_passed,
            "warnings": list(self.warnings),
        }
        if self.refinement_applied is not None:
            payload["refinement_applied"] = self.refinement_applied
        if self.refined_child_count is not None:
            payload["refined_child_count"] = self.refined_child_count
        return payload


def _quality_failures(payload: Mapping[str, Any]) -> tuple[str, ...]:
    raw = payload.get("quality_failures") or ()
    if isinstance(raw, str):
        return (raw,)
    return tuple(str(item) for item in raw)


def _optional_bool(payload: Mapping[str, Any], key: str) -> bool | None:
    if key not in payload:
        return None
    value = payload.get(key)
    return value if isinstance(value, bool) else None


def _optional_int(payload: Mapping[str, Any], key: str) -> int | None:
    value = payload.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def classify_redraw_review(payload: Mapping[str, Any]) -> RedrawReview:
    layer_asset = str(payload.get("file") or "")
    source_pasteback = str(payload.get("source_pasteback_path") or "")
    source_error = str(payload.get("source_pasteback_error") or "")
    quality = _optional_bool(payload, "quality_gate_passed")
    refinement_applied = _optional_bool(payload, "refinement_applied")
    refined_child_count = _optional_int(payload, "refined_child_count")

    if source_error and not source_pasteback:
        return RedrawReview(
            state="pasteback_warning",
            primary_after_path=layer_asset,
            layer_asset_path=layer_asset,
            source_pasteback_path="",
            source_pasteback_error=source_error,
            show_as_final=False,
            quality_gate_passed=quality,
            warnings=(f"source_pasteback_error: {source_error}",),
            refinement_applied=refinement_applied,
            refined_child_count=refined_child_count,
        )

    if source_pasteback:
        if quality is True:
            state: ReviewState = "ready_for_review"
            warnings: tuple[str, ...] = ()
        elif quality is False:
            state = "technical_preview"
            failures = ", ".join(_quality_failures(payload)) or "unknown"
            warnings = (f"quality_gate_failed: {failures}",)
        else:
            state = "unknown_quality_preview"
            warnings = ("quality_gate_missing",)
        return RedrawReview(
            state=state,
            primary_after_path=source_pasteback,
            layer_asset_path=layer_asset,
            source_pasteback_path=source_pasteback,
            source_pasteback_error="",
            show_as_final=True,
            quality_gate_passed=quality,
            warnings=warnings,
            refinement_applied=refinement_applied,
            refined_child_count=refined_child_count,
        )

    return RedrawReview(
        state="layer_only_result",
        primary_after_path=layer_asset,
        layer_asset_path=layer_asset,
        source_pasteback_path="",
        source_pasteback_error="",
        show_as_final=False,
        quality_gate_passed=quality,
        warnings=("source_pasteback_path_missing",),
        refinement_applied=refinement_applied,
        refined_child_count=refined_child_count,
    )
