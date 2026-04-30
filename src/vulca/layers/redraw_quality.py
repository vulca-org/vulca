"""Local quality gates for layer redraw outputs."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class RedrawQualityReport:
    passed: bool
    failures: tuple[str, ...]
    metrics: dict[str, float]


def evaluate_redraw_quality(
    source_rgba: Image.Image,
    output_rgba: Image.Image,
    *,
    description: str = "",
    instruction: str = "",
    refinement_applied: bool = False,
    refined_child_count: int = 0,
    refined_coverage_pct: float = 0.0,
    mask_granularity_score: float = 0.0,
) -> RedrawQualityReport:
    from vulca.layers.mask_refine import infer_refinement_profile

    src = np.array(source_rgba.convert("RGBA"))
    out = np.array(output_rgba.convert("RGBA"))
    failures: list[str] = []

    src_alpha = src[..., 3] > 0
    out_alpha = out[..., 3] > 0
    src_area_pct = 100.0 * float(src_alpha.sum()) / float(max(1, src_alpha.size))
    src_bbox_area = _bbox_area(src_alpha)
    out_bbox_area = _bbox_area(out_alpha)
    src_bbox_pct = 100.0 * float(src_bbox_area) / float(max(1, src_alpha.size))
    bbox_ratio = out_bbox_area / src_bbox_area if src_bbox_area else 0.0
    if bbox_ratio > 2.5:
        failures.append("alpha_bbox_expanded")

    out_rgb = out[..., :3]
    white = (
        (out_rgb[..., 0] > 245)
        & (out_rgb[..., 1] > 245)
        & (out_rgb[..., 2] > 245)
        & out_alpha
    )
    white_pct = 100.0 * float(white.sum()) / float(max(1, out_alpha.sum()))
    if white_pct > 85.0 and int(out_alpha.sum()) > 1000:
        failures.append("large_white_component")

    profile = infer_refinement_profile(
        description=description,
        instruction=instruction,
    )
    mask_is_broad = src_area_pct > 5.0 or src_bbox_pct > 10.0
    if (
        profile is not None
        and not refinement_applied
        and refined_child_count <= 0
        and mask_is_broad
    ):
        failures.append("mask_too_broad_for_target")

    return RedrawQualityReport(
        passed=not failures,
        failures=tuple(failures),
        metrics={
            "bbox_ratio": float(bbox_ratio),
            "white_pct": float(white_pct),
            "white_like_pct": float(white_pct),
            "src_area_pct": float(src_area_pct),
            "src_bbox_pct": float(src_bbox_pct),
            "alpha_bbox_expanded": float("alpha_bbox_expanded" in failures),
            "large_white_component": float("large_white_component" in failures),
            "background_bleed": 0.0,
            "refined_child_count": float(refined_child_count),
            "refined_coverage_pct": float(refined_coverage_pct),
            "mask_granularity_score": float(mask_granularity_score),
        },
    )


def _bbox_area(mask: np.ndarray) -> int:
    if not mask.any():
        return 0
    ys, xs = np.where(mask)
    return int((xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1))
