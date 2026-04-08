"""Per-layer post-generation validation: spatial sanity checks.

Defense layer 2 of the plan/generation consistency strategy. Cheap, offline,
no provider calls. Reports drifts as warnings; only emptiness is hard-failure.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np


@dataclass
class ValidationWarning:
    kind: str
    message: str
    detail: dict = field(default_factory=dict)


@dataclass
class ValidationReport:
    ok: bool
    warnings: list[ValidationWarning] = field(default_factory=list)
    coverage_actual: float = 0.0
    position_iou: float = 0.0


def parse_coverage(text: str) -> tuple[float, float]:
    if not text:
        return (0.0, 1.0)
    m = re.match(r"\s*(\d+)\s*-\s*(\d+)\s*%", text)
    if m:
        return (int(m.group(1)) / 100.0, int(m.group(2)) / 100.0)
    m = re.match(r"\s*(\d+)\s*%", text)
    if m:
        v = int(m.group(1)) / 100.0
        return (v, v)
    return (0.0, 1.0)


def parse_position(text: str) -> dict[str, float]:
    if not text:
        return {"top": 0.0, "bottom": 1.0, "left": 0.0, "right": 1.0}
    t = text.lower()
    m = re.search(r"upper\s+(\d+)\s*%", t)
    if m:
        return {"top": 0.0, "bottom": int(m.group(1)) / 100.0, "left": 0.0, "right": 1.0}
    m = re.search(r"lower\s+(\d+)\s*%", t)
    if m:
        return {"top": 1.0 - int(m.group(1)) / 100.0, "bottom": 1.0, "left": 0.0, "right": 1.0}
    if "center" in t:
        return {"top": 0.25, "bottom": 0.75, "left": 0.25, "right": 0.75}
    if "corner" in t:
        return {"top": 0.0, "bottom": 0.30, "left": 0.0, "right": 0.30}
    return {"top": 0.0, "bottom": 1.0, "left": 0.0, "right": 1.0}


def _alpha_bbox_iou(alpha: np.ndarray, region: dict[str, float], threshold: float = 0.05) -> float:
    h, w = alpha.shape
    mask = alpha > threshold
    if not mask.any():
        return 0.0

    rows = mask.any(axis=1)
    cols = mask.any(axis=0)
    row_idx = np.where(rows)[0]
    col_idx = np.where(cols)[0]
    y0, y1 = int(row_idx[0]), int(row_idx[-1]) + 1
    x0, x1 = int(col_idx[0]), int(col_idx[-1]) + 1

    rt, rb = int(region["top"] * h), int(region["bottom"] * h)
    rl, rr = int(region["left"] * w), int(region["right"] * w)

    ix0, iy0 = max(x0, rl), max(y0, rt)
    ix1, iy1 = min(x1, rr), min(y1, rb)
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    a1 = (x1 - x0) * (y1 - y0)
    a2 = (rr - rl) * (rb - rt)
    return inter / max(a1 + a2 - inter, 1)


def validate_layer_alpha(
    alpha: np.ndarray,
    *,
    position: str = "",
    coverage: str = "",
    alpha_threshold: float = 0.05,
    position_iou_threshold: float = 0.30,
    coverage_factor: float = 2.0,
) -> ValidationReport:
    rep = ValidationReport(ok=True)
    h, w = alpha.shape
    canvas_area = h * w

    nonzero = (alpha > alpha_threshold).sum()
    rep.coverage_actual = float(nonzero) / canvas_area

    if nonzero < canvas_area * 0.001:
        rep.ok = False
        rep.warnings.append(ValidationWarning(
            "empty_layer",
            "alpha is essentially empty (< 0.1% of canvas)",
            {"nonzero": int(nonzero), "canvas_area": canvas_area},
        ))
        return rep

    lo, hi = parse_coverage(coverage)
    lo_tol, hi_tol = lo / coverage_factor, hi * coverage_factor
    if rep.coverage_actual < lo_tol or rep.coverage_actual > hi_tol:
        rep.warnings.append(ValidationWarning(
            "coverage_drift",
            f"coverage {rep.coverage_actual:.0%} outside tolerated [{lo_tol:.0%}, {hi_tol:.0%}]",
            {"actual": rep.coverage_actual, "expected": coverage},
        ))

    region = parse_position(position)
    rep.position_iou = _alpha_bbox_iou(alpha, region, alpha_threshold)
    if rep.position_iou < position_iou_threshold:
        rep.warnings.append(ValidationWarning(
            "position_drift",
            f"alpha bbox IoU with expected region = {rep.position_iou:.2f}",
            {"iou": rep.position_iou, "expected": position},
        ))

    return rep
