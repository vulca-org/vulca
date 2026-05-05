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
    src_rgb = src[..., :3]
    white = (
        (out_rgb[..., 0] > 245)
        & (out_rgb[..., 1] > 245)
        & (out_rgb[..., 2] > 245)
        & out_alpha
    )
    white_pct = 100.0 * float(white.sum()) / float(max(1, out_alpha.sum()))
    if white_pct > 85.0 and int(out_alpha.sum()) > 1000:
        failures.append("large_white_component")

    visible_count = int(out_alpha.sum())
    dark_artifact = (
        (out_rgb[..., 0] < 35)
        & (out_rgb[..., 1] < 35)
        & (out_rgb[..., 2] < 35)
        & (out_rgb.max(axis=2) < 50)
        & out_alpha
    )
    dark_artifact_pct = 100.0 * float(dark_artifact.sum()) / float(
        max(1, visible_count)
    )
    olive_fill = (
        (out_rgb[..., 0] > 45)
        & (out_rgb[..., 0] < 120)
        & (out_rgb[..., 1] > 55)
        & (out_rgb[..., 1] < 135)
        & (out_rgb[..., 2] > 25)
        & (out_rgb[..., 2] < 95)
        & (out_rgb[..., 1] >= out_rgb[..., 0] - 10)
        & out_alpha
    )
    olive_fill_pct = 100.0 * float(olive_fill.sum()) / float(max(1, visible_count))

    profile = infer_refinement_profile(
        description=description,
        instruction=instruction,
    )
    if profile is not None and refinement_applied and visible_count > 100:
        if dark_artifact_pct > 8.0:
            failures.append("dark_artifact_visible")
        if olive_fill_pct > 30.0:
            failures.append("olive_fill_visible")

    mask_is_broad = src_area_pct > 5.0 or src_bbox_pct > 10.0
    if (
        profile is not None
        and not refinement_applied
        and refined_child_count <= 0
        and mask_is_broad
    ):
        failures.append("mask_too_broad_for_target")

    overlap = src_alpha & out_alpha
    if overlap.any():
        src_luma = _luma(src_rgb)[overlap]
        out_luma = _luma(out_rgb)[overlap]
        src_luma_mean = float(src_luma.mean())
        out_luma_mean = float(out_luma.mean())
        output_luma_delta_pct = (
            100.0 * (out_luma_mean - src_luma_mean) / max(1.0, src_luma_mean)
        )
    else:
        src_luma_mean = 0.0
        out_luma_mean = 0.0
        output_luma_delta_pct = 0.0

    if (
        profile is None
        and is_texture_redraw_request(description=description, instruction=instruction)
        and not refinement_applied
        and refined_child_count <= 0
        and mask_is_broad
        and output_luma_delta_pct < -25.0
    ):
        failures.append("broad_texture_repaint")

    return RedrawQualityReport(
        passed=not failures,
        failures=tuple(failures),
        metrics={
            "bbox_ratio": float(bbox_ratio),
            "white_pct": float(white_pct),
            "white_like_pct": float(white_pct),
            "dark_artifact_pct": float(dark_artifact_pct),
            "olive_fill_pct": float(olive_fill_pct),
            "src_area_pct": float(src_area_pct),
            "src_bbox_pct": float(src_bbox_pct),
            "alpha_bbox_expanded": float("alpha_bbox_expanded" in failures),
            "large_white_component": float("large_white_component" in failures),
            "dark_artifact_visible": float("dark_artifact_visible" in failures),
            "olive_fill_visible": float("olive_fill_visible" in failures),
            "broad_texture_repaint": float("broad_texture_repaint" in failures),
            "background_bleed": 0.0,
            "refined_child_count": float(refined_child_count),
            "refined_coverage_pct": float(refined_coverage_pct),
            "mask_granularity_score": float(mask_granularity_score),
            "source_luma_mean": float(src_luma_mean),
            "output_luma_mean": float(out_luma_mean),
            "output_luma_delta_pct": float(output_luma_delta_pct),
        },
    )


def _bbox_area(mask: np.ndarray) -> int:
    if not mask.any():
        return 0
    ys, xs = np.where(mask)
    return int((xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1))


def _luma(rgb: np.ndarray) -> np.ndarray:
    rgb_float = rgb.astype(np.float32)
    return (
        0.2126 * rgb_float[..., 0]
        + 0.7152 * rgb_float[..., 1]
        + 0.0722 * rgb_float[..., 2]
    )


def is_texture_redraw_request(*, description: str, instruction: str) -> bool:
    text = f"{description} {instruction}".lower()
    texture_terms = (
        "texture",
        "leaf",
        "leaves",
        "leafy",
        "hedge",
        "ivy",
        "foliage",
        "grass",
    )
    return any(term in text for term in texture_terms)
