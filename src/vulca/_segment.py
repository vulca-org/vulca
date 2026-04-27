"""Internal segmentation helpers (pure stdlib) for the orchestrated decompose pipeline.

Underscore-prefixed module name marks this as decompose-internal: the helpers
below (_iou, _nms_bboxes) are detection-layer implementation detail, not a
public API. Downstream code SHOULD NOT import these and SHOULD NOT depend on
them being re-export-stable across versions.

The helpers live here (rather than in `scripts/claude_orchestrated_pipeline.py`
where their callers are) for one reason only: `cop.py` does top-level
`import torch`, and CI deliberately does not install torch (~2GB wheel).
Hosting the pure helpers inside the package lets unit tests collect and run
without torch — see `tests/test_layers_v2_split.py::TestMultiInstanceDetection`.

Mirrors the pattern established by `vulca._quality_gate` in v0.17.13/14.
"""
from __future__ import annotations


def _iou(a, b):
    """Axis-aligned bbox IoU on [x1, y1, x2, y2] tuples."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    if inter == 0:
        return 0.0
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return inter / (area_a + area_b - inter)


def _nms_bboxes(detections, iou_threshold=0.5, keep_n=None):
    """Non-max suppression on (bbox, score, phrase) tuples.

    Keeps higher-score detections; removes lower-score ones that overlap >threshold.
    If `keep_n` is given, caps result to top-N (after NMS dedup). `keep_n=None`
    preserves the pre-v0.18 behaviour of returning all dedup'd detections.

    v0.18 added `keep_n` to support the opt-in multi-instance return shape in
    `detect_all_bboxes`: multi-instance labels pass `keep_n=max_n` to bound
    fan-out per label; single-instance callers pass `keep_n=1` and unwrap the
    sole survivor as the (bbox, score, phrase) tuple.

    `keep_n` is clamped to a minimum of 1: passing `keep_n=0` (or negative) is
    treated as `keep_n=1`, NOT as "return empty list". Callers wanting an empty
    result should not call `_nms_bboxes` at all.
    """
    if keep_n is not None:
        keep_n = max(1, int(keep_n))
    detections = sorted(detections, key=lambda d: -d[1])
    kept = []
    for d in detections:
        bbox, score, phrase = d
        is_dup = False
        for k in kept:
            if _iou(bbox, k[0]) > iou_threshold:
                is_dup = True
                break
        if not is_dup:
            kept.append(d)
            if keep_n is not None and len(kept) >= keep_n:
                break
    return kept
