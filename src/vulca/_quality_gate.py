"""Internal transparency-gate logic for the orchestrated decompose pipeline.

Underscore-prefixed module name marks this as decompose-internal: the four
threshold constants below (0.05 / 0.70 / 0.30 / 0.60) are calibration
implementation detail, not a public API. Downstream code SHOULD NOT import
these values; downstream code SHOULD NOT depend on the function being
re-export-stable across versions.

The function lives here (rather than in `scripts/claude_orchestrated_pipeline.py`
where its callers are) for one reason only: `cop.py` does top-level
`import torch`, and CI deliberately does not install torch (~2GB wheel).
Hosting the pure helper inside the package lets the regression suite collect
and run without torch — see `tests/test_quality_gate.py`.

Calibration history and the actual threshold reasoning live in the function
docstring below and in `tests/test_quality_gate.py`.
"""
from __future__ import annotations


def compute_quality_flags(
    *,
    pct: float,
    sam_score: float,
    bbox_fill: float,
    inside_ratio: float,
) -> tuple[list[str], str]:
    """v0.17.13/14 transparency gate for DINO-object segmentation results.

    Mirrors the hint-path gate into a pure helper so the DINO-object loop
    and the person loop can apply the same suspect/detected logic.
    Pre-v0.17.13 the DINO branch silently wrote `status: "detected"` even
    when SAM was low-confidence, leading to silent "the lanterns layer
    captured building structure" failures (γ Scottish iter 0 lanterns:
    sam_score 0.609, bbox_fill 0.256 → suspect).

    DINO-tier thresholds: looser than hint-path (0.05) because DINO bboxes
    are model-supplied and tend wider. Calibrated against γ Scottish
    9-entity baseline (8 clean entities pass at sam>=0.93 / fill>=0.55,
    lanterns gets flagged).

    Returns:
        (quality_flags, status) — flags is a list of triggered conditions;
        status is "suspect" if any flag fired, else "detected".
    """
    flags: list[str] = []
    if pct < 0.05:
        flags.append("empty_mask")
    if sam_score < 0.70:
        flags.append("low_sam_score")
    if bbox_fill < 0.30:
        flags.append("low_bbox_fill")
    if inside_ratio < 0.60:
        flags.append("mask_outside_bbox")
    status = "suspect" if flags else "detected"
    return flags, status
