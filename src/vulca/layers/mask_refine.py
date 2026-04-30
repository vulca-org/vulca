from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class TargetRefinementProfile:
    kind: Literal["bright_small_subject"]
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class MaskRefinementResult:
    applied: bool
    reason: str
    strategy: str
    child_masks: tuple[Image.Image, ...]
    metrics: dict[str, float]


_BRIGHT_SMALL_SUBJECT_KEYWORDS = (
    "flower",
    "wildflower",
    "blossom",
    "petal",
    "white",
    "tiny",
    "small",
    "daisy",
    "aster",
)


def infer_refinement_profile(
    *,
    description: str = "",
    instruction: str = "",
) -> TargetRefinementProfile | None:
    text = f"{description} {instruction}".lower()
    matches = tuple(
        keyword for keyword in _BRIGHT_SMALL_SUBJECT_KEYWORDS if keyword in text
    )
    if not matches:
        return None
    return TargetRefinementProfile(kind="bright_small_subject", keywords=matches)


def refine_mask_for_target(
    source: Image.Image,
    alpha: Image.Image,
    *,
    description: str = "",
    instruction: str = "",
    min_component_area: int = 24,
    merge_distance_px: int = 10,
    max_children: int = 12,
) -> MaskRefinementResult:
    profile = infer_refinement_profile(
        description=description,
        instruction=instruction,
    )
    if profile is None:
        return MaskRefinementResult(
            applied=False,
            reason="no_target_profile",
            strategy="none",
            child_masks=(),
            metrics={},
        )

    child_masks, metrics = _extract_bright_small_subject_masks(
        source,
        alpha,
        min_component_area=min_component_area,
        merge_distance_px=merge_distance_px,
        max_children=max_children,
    )
    if not child_masks:
        return MaskRefinementResult(
            applied=False,
            reason="no_child_masks",
            strategy=profile.kind,
            child_masks=(),
            metrics=metrics,
        )

    return MaskRefinementResult(
        applied=True,
        reason="target_evidence_components",
        strategy=profile.kind,
        child_masks=child_masks,
        metrics=metrics,
    )


def _extract_bright_small_subject_masks(
    source: Image.Image,
    alpha: Image.Image,
    *,
    min_component_area: int,
    merge_distance_px: int,
    max_children: int,
) -> tuple[tuple[Image.Image, ...], dict[str, float]]:
    rgb = np.asarray(source.convert("RGB"))
    parent = np.asarray(alpha.convert("L")) > 0
    if rgb.shape[:2] != parent.shape:
        raise ValueError("source and alpha sizes must match")

    red = rgb[:, :, 0].astype(np.int16)
    green = rgb[:, :, 1].astype(np.int16)
    blue = rgb[:, :, 2].astype(np.int16)
    channel_spread = np.maximum.reduce((red, green, blue)) - np.minimum.reduce(
        (red, green, blue)
    )

    white_like = (red > 185) & (green > 185) & (blue > 170) & (channel_spread < 70)
    yellow_center = (red > 170) & (green > 130) & (blue < 120)
    evidence_raw = parent & (white_like | yellow_center)
    evidence = _dilate(evidence_raw, radius=2) & parent

    component_seed = _open(evidence_raw, radius=1) & parent
    if not component_seed.any():
        component_seed = evidence_raw

    components = _connected_component_boxes(component_seed, min_area=min_component_area)
    boxes = _merge_nearby_boxes(components, distance_px=merge_distance_px)
    boxes = sorted(boxes, key=_box_area, reverse=True)[:max_children]

    height, width = parent.shape
    child_masks: list[Image.Image] = []
    for box in boxes:
        left, top, right, bottom = _expand_box(box, width, height, padding=6)
        child = np.zeros(parent.shape, dtype=np.uint8)
        local_evidence = evidence_raw[top:bottom, left:right]
        local_child = _dilate(local_evidence, radius=4) & parent[top:bottom, left:right]
        child[top:bottom, left:right] = local_child * 255
        if np.any(child):
            child_masks.append(Image.fromarray(child, mode="L"))

    parent_area = int(parent.sum())
    evidence_area = int(evidence.sum())
    child_area = sum(int(np.asarray(child).astype(bool).sum()) for child in child_masks)
    metrics = {
        "parent_area_px": float(parent_area),
        "evidence_area_px": float(evidence_area),
        "evidence_ratio": float(evidence_area / parent_area) if parent_area else 0.0,
        "child_count": float(len(child_masks)),
        "refined_coverage_pct": float(child_area / parent_area) if parent_area else 0.0,
        "mask_granularity_score": float(len(child_masks)),
    }
    return tuple(child_masks), metrics


def _connected_component_boxes(
    mask: np.ndarray,
    *,
    min_area: int,
) -> list[tuple[int, int, int, int]]:
    height, width = mask.shape
    visited = np.zeros(mask.shape, dtype=bool)
    boxes: list[tuple[int, int, int, int]] = []

    for start_y, start_x in np.argwhere(mask):
        if visited[start_y, start_x]:
            continue
        stack = [(int(start_x), int(start_y))]
        visited[start_y, start_x] = True
        area = 0
        min_x = max_x = int(start_x)
        min_y = max_y = int(start_y)

        while stack:
            x, y = stack.pop()
            area += 1
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

            for ny in range(max(0, y - 1), min(height, y + 2)):
                for nx in range(max(0, x - 1), min(width, x + 2)):
                    if visited[ny, nx] or not mask[ny, nx]:
                        continue
                    visited[ny, nx] = True
                    stack.append((nx, ny))

        if area >= min_area:
            boxes.append((min_x, min_y, max_x + 1, max_y + 1))

    return boxes


def _merge_nearby_boxes(
    boxes: list[tuple[int, int, int, int]],
    *,
    distance_px: int,
) -> list[tuple[int, int, int, int]]:
    merged = list(boxes)
    changed = True
    while changed:
        changed = False
        next_boxes: list[tuple[int, int, int, int]] = []
        while merged:
            box = merged.pop()
            match_index = next(
                (
                    index
                    for index, candidate in enumerate(merged)
                    if _boxes_are_near(box, candidate, distance_px)
                ),
                None,
            )
            if match_index is None:
                next_boxes.append(box)
                continue
            candidate = merged.pop(match_index)
            merged.append(_union_box(box, candidate))
            changed = True
        merged = next_boxes
    return merged


def _dilate(mask: np.ndarray, *, radius: int) -> np.ndarray:
    if radius <= 0:
        return mask
    padded = np.pad(mask, radius, mode="constant", constant_values=False)
    result = np.zeros(mask.shape, dtype=bool)
    for dy in range(0, radius * 2 + 1):
        for dx in range(0, radius * 2 + 1):
            result |= padded[dy : dy + mask.shape[0], dx : dx + mask.shape[1]]
    return result


def _erode(mask: np.ndarray, *, radius: int) -> np.ndarray:
    if radius <= 0:
        return mask
    padded = np.pad(mask, radius, mode="constant", constant_values=False)
    result = np.ones(mask.shape, dtype=bool)
    for dy in range(0, radius * 2 + 1):
        for dx in range(0, radius * 2 + 1):
            result &= padded[dy : dy + mask.shape[0], dx : dx + mask.shape[1]]
    return result


def _open(mask: np.ndarray, *, radius: int) -> np.ndarray:
    return _dilate(_erode(mask, radius=radius), radius=radius)


def _boxes_are_near(
    first: tuple[int, int, int, int],
    second: tuple[int, int, int, int],
    distance_px: int,
) -> bool:
    return not (
        first[2] + distance_px < second[0]
        or second[2] + distance_px < first[0]
        or first[3] + distance_px < second[1]
        or second[3] + distance_px < first[1]
    )


def _union_box(
    first: tuple[int, int, int, int],
    second: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
    return (
        min(first[0], second[0]),
        min(first[1], second[1]),
        max(first[2], second[2]),
        max(first[3], second[3]),
    )


def _expand_box(
    box: tuple[int, int, int, int],
    width: int,
    height: int,
    *,
    padding: int,
) -> tuple[int, int, int, int]:
    return (
        max(0, box[0] - padding),
        max(0, box[1] - padding),
        min(width, box[2] + padding),
        min(height, box[3] + padding),
    )


def _box_area(box: tuple[int, int, int, int]) -> int:
    return (box[2] - box[0]) * (box[3] - box[1])
