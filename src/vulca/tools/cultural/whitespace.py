"""WhitespaceAnalyzer — Tier 1 cultural tool for ink-wash art traditions.

Detects whitespace ratio and spatial distribution in artwork images.
Maps findings to tradition-specific cultural norms (chinese_xieyi, sumi-e, etc.).

Algorithm:
1. Decode image → (H, W, C) uint8 RGB ndarray via ImageData
2. Convert to grayscale
3. Threshold at `config.params["threshold"]` (default 200) → binary mask
4. Compute whitespace ratio = white_pixels / total_pixels
5. Find connected components → filter by min area (1% of image) → bounding boxes
6. Classify spatial distribution (top/bottom/left/right/center/balanced/scattered)
7. Generate tradition-specific cultural verdict
8. Build annotated evidence image (semi-transparent blue overlay + red bboxes)
"""

from __future__ import annotations

import io
from typing import Any

import cv2
import numpy as np
from PIL import Image

from vulca.tools.protocol import (
    ImageData,
    ToolCategory,
    ToolConfig,
    ToolSchema,
    VisualEvidence,
    VulcaTool,
)

# ---------------------------------------------------------------------------
# Tradition-specific whitespace ratio ranges (min, max) for "ideal" range
# ---------------------------------------------------------------------------

_TRADITION_RANGES: dict[str, tuple[float, float]] = {
    "chinese_xieyi": (0.30, 0.55),
    "chinese_gongbi": (0.10, 0.30),
    "japanese_sumi_e": (0.35, 0.60),
    "ukiyo_e": (0.05, 0.25),
}
_DEFAULT_RANGE: tuple[float, float] = (0.15, 0.50)

# Distribution labels
_DISTRIBUTIONS = (
    "balanced",
    "top_heavy",
    "bottom_heavy",
    "left_heavy",
    "right_heavy",
    "center",
    "scattered",
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class WhitespaceInput(ToolSchema):
    """Input schema for WhitespaceAnalyzer."""

    image: bytes  # PNG-encoded image bytes
    tradition: str = ""


class WhitespaceOutput(ToolSchema):
    """Output schema for WhitespaceAnalyzer."""

    ratio: float  # whitespace ratio 0.0–1.0
    distribution: str  # one of _DISTRIBUTIONS
    regions: list[dict[str, int]]  # [{x, y, w, h}] bounding boxes
    cultural_verdict: str  # human-readable cultural assessment
    evidence: VisualEvidence  # REQUIRED


# ---------------------------------------------------------------------------
# WhitespaceAnalyzer
# ---------------------------------------------------------------------------


class WhitespaceAnalyzer(VulcaTool):
    """Detect whitespace ratio and spatial distribution in artwork.

    Tier 1 cultural tool — runs deterministically with cv2, no LLM required.
    Replaces L1 (Cultural Authenticity) in the evaluate pipeline.
    """

    name = "whitespace_analyze"
    display_name = "Whitespace Analyzer"
    description = (
        "Detect whitespace ratio and spatial distribution in artwork. "
        "Maps findings to tradition-specific cultural norms for ink-wash and related art styles."
    )
    category = ToolCategory.CULTURAL_CHECK
    replaces: dict[str, list[str]] = {"evaluate": ["L1"]}
    max_seconds = 10

    Input = WhitespaceInput
    Output = WhitespaceOutput

    # --- Default threshold ---
    _DEFAULT_THRESHOLD: int = 200
    _MIN_AREA_FRACTION: float = 0.01  # 1% of image area

    def execute(self, input_data: WhitespaceInput, config: ToolConfig) -> WhitespaceOutput:
        """Run whitespace analysis on the input image."""
        # --- 1. Decode image ---
        img_data = ImageData.from_bytes(input_data.image)
        rgb = img_data.to_numpy()  # (H, W, 3) uint8

        h, w = rgb.shape[:2]
        total_pixels = h * w

        # --- 2. Convert to grayscale ---
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

        # --- 3. Threshold → binary mask (white = 1) ---
        threshold = int(config.params.get("threshold", self._DEFAULT_THRESHOLD))
        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

        # --- 4. Whitespace ratio ---
        white_pixels = int(np.sum(binary == 255))
        ratio = white_pixels / total_pixels

        # --- 5. Connected components → bounding boxes ---
        min_area = total_pixels * self._MIN_AREA_FRACTION
        num_labels, _labels, stats, _centroids = cv2.connectedComponentsWithStats(
            binary, connectivity=8
        )

        regions: list[dict[str, int]] = []
        for label_idx in range(1, num_labels):  # skip background (label 0)
            area = int(stats[label_idx, cv2.CC_STAT_AREA])
            if area < min_area:
                continue
            x = int(stats[label_idx, cv2.CC_STAT_LEFT])
            y = int(stats[label_idx, cv2.CC_STAT_TOP])
            bw = int(stats[label_idx, cv2.CC_STAT_WIDTH])
            bh = int(stats[label_idx, cv2.CC_STAT_HEIGHT])
            regions.append({"x": x, "y": y, "w": bw, "h": bh})

        # --- 6. Classify spatial distribution ---
        distribution = _classify_distribution(binary, w, h)

        # --- 7. Cultural verdict ---
        tradition = input_data.tradition.strip()
        # User thresholds override tradition defaults
        if "ratio_min" in config.thresholds and "ratio_max" in config.thresholds:
            r_min = config.thresholds["ratio_min"]
            r_max = config.thresholds["ratio_max"]
            verdict_tradition = f"custom ({r_min:.2f}–{r_max:.2f})"
        else:
            r_min, r_max = _TRADITION_RANGES.get(tradition, _DEFAULT_RANGE)
            verdict_tradition = tradition or "general"

        cultural_verdict = _build_verdict(ratio, r_min, r_max, verdict_tradition, distribution)

        # --- 8. Confidence ---
        confidence = _compute_confidence(ratio, r_min, r_max)

        # --- 9. Annotated evidence image ---
        annotated = _build_annotated_image(rgb, binary, regions)
        annotated_png = _ndarray_to_png(annotated)

        evidence = VisualEvidence(
            annotated_image=annotated_png,
            summary=(
                f"Whitespace ratio: {ratio:.1%} ({distribution}). "
                f"{cultural_verdict}"
            ),
            details={
                "ratio": ratio,
                "distribution": distribution,
                "threshold": threshold,
                "tradition": tradition or "general",
                "ideal_range": [r_min, r_max],
                "region_count": len(regions),
            },
            confidence=confidence,
        )

        return WhitespaceOutput(
            ratio=ratio,
            distribution=distribution,
            regions=regions,
            cultural_verdict=cultural_verdict,
            evidence=evidence,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _classify_distribution(binary: np.ndarray, w: int, h: int) -> str:
    """Classify the spatial distribution of whitespace into one of 7 labels.

    Compares white pixel density across top/bottom/left/right/center quadrants.
    """
    half_h = h // 2
    half_w = w // 2
    q_h = h // 4
    q_w = w // 4

    def density(region: np.ndarray) -> float:
        total = region.size
        if total == 0:
            return 0.0
        return float(np.sum(region == 255)) / total

    top_d = density(binary[:half_h, :])
    bottom_d = density(binary[half_h:, :])
    left_d = density(binary[:, :half_w])
    right_d = density(binary[:, half_w:])
    center_d = density(binary[q_h : h - q_h, q_w : w - q_w])

    # Threshold for "significantly heavier"
    eps = 0.12

    # Check center dominance
    periphery_d = (top_d + bottom_d + left_d + right_d) / 4
    if center_d > periphery_d + eps:
        return "center"

    # Check top/bottom imbalance
    if top_d > bottom_d + eps:
        return "top_heavy"
    if bottom_d > top_d + eps:
        return "bottom_heavy"

    # Check left/right imbalance
    if left_d > right_d + eps:
        return "left_heavy"
    if right_d > left_d + eps:
        return "right_heavy"

    # Check balanced vs scattered
    # "balanced" = relatively uniform density across quadrants
    densities = [top_d, bottom_d, left_d, right_d]
    spread = max(densities) - min(densities)
    if spread > 0.30:
        return "scattered"

    return "balanced"


def _build_verdict(
    ratio: float,
    r_min: float,
    r_max: float,
    tradition_label: str,
    distribution: str,
) -> str:
    """Build a human-readable cultural verdict string."""
    pct = f"{ratio:.1%}"
    range_str = f"{r_min:.0%}–{r_max:.0%}"

    if ratio < r_min:
        gap = r_min - ratio
        return (
            f"Whitespace ({pct}) is below the {tradition_label} ideal range ({range_str}). "
            f"Consider opening up {gap:.0%} more negative space; "
            f"distribution is {distribution}."
        )
    elif ratio > r_max:
        excess = ratio - r_max
        return (
            f"Whitespace ({pct}) exceeds the {tradition_label} ideal range ({range_str}). "
            f"The composition may feel too sparse — reduce empty space by {excess:.0%}; "
            f"distribution is {distribution}."
        )
    else:
        return (
            f"Whitespace ({pct}) is within the {tradition_label} ideal range ({range_str}). "
            f"The {distribution} distribution aligns well with tradition expectations."
        )


def _compute_confidence(ratio: float, r_min: float, r_max: float) -> float:
    """Compute confidence based on how clearly within or outside the ideal range.

    - Clearly inside/outside range → higher confidence (up to 0.95)
    - Near range boundaries → lower confidence (down to 0.50)
    """
    range_width = max(r_max - r_min, 1e-9)
    boundary_zone = range_width * 0.20  # 20% of range width = "near boundary"

    if r_min <= ratio <= r_max:
        # Inside range — distance from nearest boundary
        dist_from_boundary = min(ratio - r_min, r_max - ratio)
        if dist_from_boundary >= boundary_zone:
            return 0.90
        # Linear interpolation from 0.55 to 0.90 across boundary_zone
        return 0.55 + 0.35 * (dist_from_boundary / boundary_zone)
    else:
        # Outside range — distance beyond boundary
        if ratio < r_min:
            dist_beyond = r_min - ratio
        else:
            dist_beyond = ratio - r_max
        if dist_beyond >= boundary_zone:
            return 0.90
        return 0.55 + 0.35 * (dist_beyond / boundary_zone)


def _build_annotated_image(
    rgb: np.ndarray,
    binary: np.ndarray,
    regions: list[dict[str, int]],
) -> np.ndarray:
    """Build an annotated RGB image showing whitespace overlay + region bboxes.

    - Semi-transparent blue overlay on whitespace pixels
    - Red bounding boxes around connected-component regions
    """
    annotated = rgb.copy().astype(np.float32)

    # Semi-transparent blue overlay on whitespace (binary == 255)
    mask = binary == 255
    alpha = 0.35
    annotated[mask, 0] = annotated[mask, 0] * (1 - alpha) + 100 * alpha
    annotated[mask, 1] = annotated[mask, 1] * (1 - alpha) + 149 * alpha
    annotated[mask, 2] = annotated[mask, 2] * (1 - alpha) + 237 * alpha

    annotated = np.clip(annotated, 0, 255).astype(np.uint8)

    # Red bounding boxes around regions (cv2 expects BGR for drawing but we'll
    # draw directly to avoid color-space confusion — draw in RGB as red)
    red = (220, 38, 38)
    for region in regions:
        x, y, bw, bh = region["x"], region["y"], region["w"], region["h"]
        annotated = cv2.rectangle(annotated, (x, y), (x + bw, y + bh), red, 2)

    return annotated


def _ndarray_to_png(arr: np.ndarray) -> bytes:
    """Convert (H, W, 3) uint8 RGB ndarray to PNG bytes."""
    pil = Image.fromarray(arr, mode="RGB")
    buf = io.BytesIO()
    pil.save(buf, format="PNG", optimize=False, compress_level=1)
    return buf.getvalue()
