"""Geometry-based route selection for layer redraw."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
from PIL import Image


class RedrawRoute(str, Enum):
    DENSE_FULL_CANVAS = "dense_full_canvas"
    SPARSE_BBOX_CROP = "sparse_bbox_crop"
    SPARSE_PER_INSTANCE = "sparse_per_instance"


@dataclass(frozen=True)
class CropBox:
    x: int
    y: int
    w: int
    h: int


@dataclass(frozen=True)
class AlphaGeometry:
    area_pct: float
    bbox_fill: float
    component_count: int
    bbox: CropBox
    components: tuple[CropBox, ...]
    canvas_w: int
    canvas_h: int


@dataclass(frozen=True)
class RedrawPlan:
    route: RedrawRoute
    crop_boxes: tuple[CropBox, ...]
    warnings: tuple[str, ...] = ()


def analyze_alpha_geometry(alpha: Image.Image) -> AlphaGeometry:
    mask = np.array(alpha.convert("L")) > 0
    canvas_h, canvas_w = mask.shape
    visible = int(mask.sum())
    total = int(mask.size)
    if visible == 0 or total == 0:
        empty = CropBox(0, 0, 0, 0)
        return AlphaGeometry(0.0, 0.0, 0, empty, (), canvas_w, canvas_h)

    ys, xs = np.where(mask)
    bbox = CropBox(
        int(xs.min()),
        int(ys.min()),
        int(xs.max() - xs.min() + 1),
        int(ys.max() - ys.min() + 1),
    )
    bbox_area = bbox.w * bbox.h
    bbox_fill = visible / float(bbox_area) if bbox_area else 0.0
    components = tuple(_component_boxes(mask))
    return AlphaGeometry(
        area_pct=100.0 * visible / total,
        bbox_fill=bbox_fill,
        component_count=len(components),
        bbox=bbox,
        components=components,
        canvas_w=canvas_w,
        canvas_h=canvas_h,
    )


def choose_redraw_route(
    geom: AlphaGeometry,
    *,
    area_threshold: float = 5.0,
    bbox_fill_threshold: float = 0.5,
    pad_ratio: float = 0.35,
) -> RedrawPlan:
    if geom.component_count == 0:
        return RedrawPlan(RedrawRoute.SPARSE_BBOX_CROP, ())

    if geom.component_count > 1 and geom.bbox_fill < bbox_fill_threshold:
        return RedrawPlan(
            RedrawRoute.SPARSE_PER_INSTANCE,
            tuple(
                _pad_box(c, geom.canvas_w, geom.canvas_h, pad_ratio)
                for c in geom.components
            ),
        )

    if geom.area_pct < area_threshold or geom.bbox_fill < bbox_fill_threshold:
        return RedrawPlan(
            RedrawRoute.SPARSE_BBOX_CROP,
            (_pad_box(geom.bbox, geom.canvas_w, geom.canvas_h, pad_ratio),),
        )

    return RedrawPlan(RedrawRoute.DENSE_FULL_CANVAS, (geom.bbox,))


def _component_boxes(mask: np.ndarray) -> list[CropBox]:
    try:
        import cv2  # type: ignore
    except ImportError:
        return _projection_component_boxes(mask)

    labels_count, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask.astype("uint8"), connectivity=8
    )
    boxes: list[CropBox] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if int(area) > 0:
            boxes.append(CropBox(int(x), int(y), int(w), int(h)))
    return boxes


def _projection_component_boxes(mask: np.ndarray) -> list[CropBox]:
    """Fast fallback for common separated-object layouts.

    This is intentionally heuristic. It avoids an O(visible-pixel) Python DFS
    on 4032x3024 layers when OpenCV is unavailable, while still catching the
    row/column-separated multi-instance layouts that motivated v0.21.
    """
    col_runs = _runs(np.flatnonzero(mask.any(axis=0)))
    row_runs = _runs(np.flatnonzero(mask.any(axis=1)))

    if len(col_runs) >= len(row_runs) and len(col_runs) > 1:
        return [_box_for_col_range(mask, start, end) for start, end in col_runs]
    if len(row_runs) > 1:
        return [_box_for_row_range(mask, start, end) for start, end in row_runs]

    ys, xs = np.where(mask)
    return [CropBox(int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))]


def _runs(indices: np.ndarray) -> list[tuple[int, int]]:
    if len(indices) == 0:
        return []
    runs: list[tuple[int, int]] = []
    start = prev = int(indices[0])
    for value in indices[1:]:
        current = int(value)
        if current == prev + 1:
            prev = current
            continue
        runs.append((start, prev))
        start = prev = current
    runs.append((start, prev))
    return runs


def _box_for_col_range(mask: np.ndarray, start: int, end: int) -> CropBox:
    sub = mask[:, start : end + 1]
    ys, xs = np.where(sub)
    return CropBox(
        start + int(xs.min()),
        int(ys.min()),
        int(xs.max() - xs.min() + 1),
        int(ys.max() - ys.min() + 1),
    )


def _box_for_row_range(mask: np.ndarray, start: int, end: int) -> CropBox:
    sub = mask[start : end + 1, :]
    ys, xs = np.where(sub)
    return CropBox(
        int(xs.min()),
        start + int(ys.min()),
        int(xs.max() - xs.min() + 1),
        int(ys.max() - ys.min() + 1),
    )


def _pad_box(box: CropBox, canvas_w: int, canvas_h: int, pad_ratio: float) -> CropBox:
    pad = max(8, int(max(box.w, box.h) * pad_ratio))
    x0 = max(0, box.x - pad)
    y0 = max(0, box.y - pad)
    x1 = min(canvas_w, box.x + box.w + pad)
    y1 = min(canvas_h, box.y + box.h + pad)
    return CropBox(x0, y0, max(1, x1 - x0), max(1, y1 - y0))
