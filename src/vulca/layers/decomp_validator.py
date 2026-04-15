"""Post-decomposition invariant checks.

Guarantees:
    coverage == 1.0 (every pixel belongs to exactly one layer)
    overlap == 0.0 (no two layers claim the same pixel)

Use this at the end of every decomposition pipeline (extract/vlm/evfsam/
tile) to fail loudly on broken masks rather than silently producing
invalid composites.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


class DecompositionValidationError(ValueError):
    """Raised when a layer decomposition violates coverage or overlap invariant."""


@dataclass
class DecompositionReport:
    coverage: float
    overlap: float
    holes: int
    overlaps: int
    canvas_size: int


def validate_decomposition(
    masks: list[np.ndarray],
    *,
    strict: bool = True,
    epsilon: float = 1e-4,
) -> DecompositionReport:
    """Validate that a set of binary masks partition the canvas perfectly.

    Args:
        masks: List of uint8 HxW arrays (values 0 or 255; threshold is > 127)
            OR bool HxW arrays. All must share the same shape.
        strict: If True, raise DecompositionValidationError on violation.
        epsilon: Tolerance for both coverage AND overlap comparisons.
            Default 1e-4 allows ~1 pixel per 10000 slack for boundary
            rounding artifacts.

    Returns:
        DecompositionReport with coverage, overlap, and counts.

    Raises:
        DecompositionValidationError: if strict=True and coverage < 1-epsilon
            or overlap > epsilon.
        ValueError: if masks list is empty or shapes don't match.
    """
    if not masks:
        raise ValueError("masks list is empty")

    first_shape = masks[0].shape
    for i, m in enumerate(masks[1:], start=1):
        if m.shape != first_shape:
            raise ValueError(
                f"mask shape mismatch: masks[0]={first_shape}, masks[{i}]={m.shape}"
            )

    h, w = first_shape
    canvas_size = h * w

    votes = np.zeros(first_shape, dtype=np.uint16)
    for m in masks:
        if m.dtype == bool:
            votes += m.astype(np.uint16)
        else:
            votes += (m > 127).astype(np.uint16)

    covered = votes >= 1
    multiply_claimed = votes >= 2
    coverage = float(covered.sum()) / canvas_size
    overlap = float(multiply_claimed.sum()) / canvas_size
    holes = int((~covered).sum())
    overlaps = int(multiply_claimed.sum())

    report = DecompositionReport(
        coverage=coverage,
        overlap=overlap,
        holes=holes,
        overlaps=overlaps,
        canvas_size=canvas_size,
    )

    if strict:
        if coverage < 1.0 - epsilon:
            raise DecompositionValidationError(
                f"coverage {coverage:.4f} below 1.0 - {epsilon} "
                f"({holes} unclaimed pixels out of {canvas_size})"
            )
        if overlap > epsilon:
            raise DecompositionValidationError(
                f"overlap {overlap:.4f} exceeds {epsilon} "
                f"({overlaps} multiply-claimed pixels out of {canvas_size})"
            )

    return report
