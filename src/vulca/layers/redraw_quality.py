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
) -> RedrawQualityReport:
    src = np.array(source_rgba.convert("RGBA"))
    out = np.array(output_rgba.convert("RGBA"))
    failures: list[str] = []

    src_alpha = src[..., 3] > 0
    out_alpha = out[..., 3] > 0
    src_bbox_area = _bbox_area(src_alpha)
    out_bbox_area = _bbox_area(out_alpha)
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

    return RedrawQualityReport(
        passed=not failures,
        failures=tuple(failures),
        metrics={
            "bbox_ratio": float(bbox_ratio),
            "white_pct": float(white_pct),
        },
    )


def _bbox_area(mask: np.ndarray) -> int:
    if not mask.any():
        return 0
    ys, xs = np.where(mask)
    return int((xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1))
