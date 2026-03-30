"""BrushstrokeAnalyzer — Tier 1 cultural tool for ink-wash art traditions.

Detects brushstroke texture energy, uniformity, dominant direction, and edge density.
Maps findings to tradition-specific cultural norms (chinese_xieyi, chinese_gongbi, sumi-e, etc.).

Algorithm:
1. Decode image → (H, W, C) uint8 RGB ndarray via ImageData
2. Convert to grayscale float32
3. Sobel gradients (gx, gy), magnitude = sqrt(gx² + gy²), direction = arctan2(gy, gx)
4. Texture energy = normalized mean magnitude (scale ×3 for visibility, clamp to 1.0)
5. Edge density = proportion of pixels above (mean + std) threshold
6. Uniformity: compute variance in 16×16 blocks, uniformity = 1 - normalized std-of-variances
7. Dominant direction: bin gradient directions into 4 quadrants weighted by magnitude at edge pixels
8. Cultural verdict: tradition-specific assessment (xieyi/sumi_e=expressive, gongbi=smooth, ukiyo_e=clean)
9. Annotated image: green edge overlay on detected edge pixels
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
# Tradition-specific expectations
# ---------------------------------------------------------------------------

# Maps tradition → expected stroke style
# "expressive" = high energy visible strokes (xieyi, sumi-e)
# "smooth"     = low energy fine strokes (gongbi)
# "clean"      = flat areas, minimal texture (ukiyo-e)
_TRADITION_STYLE: dict[str, str] = {
    "chinese_xieyi": "expressive",
    "chinese_gongbi": "smooth",
    "japanese_sumi_e": "expressive",
    "ukiyo_e": "clean",
}

# Energy thresholds for style classification
_STYLE_THRESHOLDS: dict[str, tuple[float, float]] = {
    # (min_energy_for_style, max_energy_for_style)
    "expressive": (0.25, 1.0),
    "smooth": (0.0, 0.35),
    "clean": (0.0, 0.30),
}

# Block size for uniformity computation
_BLOCK_SIZE: int = 16


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class BrushstrokeInput(ToolSchema):
    """Input schema for BrushstrokeAnalyzer."""

    image: bytes  # PNG-encoded image bytes
    tradition: str = ""


class BrushstrokeOutput(ToolSchema):
    """Output schema for BrushstrokeAnalyzer."""

    texture_energy: float  # 0-1 — normalized mean gradient magnitude
    uniformity: float  # 0-1 — stroke consistency across regions
    dominant_direction: str | None  # "horizontal"|"vertical"|"diagonal_rising"|"diagonal_falling"|None
    edge_density: float  # 0-1 — proportion of high-gradient pixels
    cultural_verdict: str  # human-readable cultural assessment
    evidence: VisualEvidence  # annotated image + analysis summary


# ---------------------------------------------------------------------------
# BrushstrokeAnalyzer
# ---------------------------------------------------------------------------


class BrushstrokeAnalyzer(VulcaTool):
    """Detect brushstroke texture, directionality, and energy in artwork.

    Tier 1 cultural tool — runs deterministically with cv2, no LLM required.
    Replaces L2 (Technical Mastery) in the evaluate pipeline.
    """

    name = "brushstroke_analyze"
    display_name = "Brushstroke Analyzer"
    description = (
        "Detect brushstroke texture energy, uniformity, and dominant direction in artwork. "
        "Maps findings to tradition-specific cultural norms for ink-wash and related art styles."
    )
    category = ToolCategory.CULTURAL_CHECK
    replaces: dict[str, list[str]] = {"evaluate": ["L2"]}
    max_seconds = 10

    Input = BrushstrokeInput
    Output = BrushstrokeOutput

    def execute(self, input_data: BrushstrokeInput, config: ToolConfig) -> BrushstrokeOutput:
        """Run brushstroke analysis on the input image."""
        # --- 1. Decode image ---
        img_data = ImageData.from_bytes(input_data.image)
        rgb = img_data.to_numpy()  # (H, W, 3) uint8

        h, w = rgb.shape[:2]

        # --- 2. Convert to grayscale float32 ---
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)

        # --- 3. Sobel gradients ---
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        magnitude = np.sqrt(gx ** 2 + gy ** 2)
        direction = np.arctan2(gy, gx)  # radians in [-π, π]

        # --- 4. Texture energy: normalized mean magnitude ---
        # Scale ×3 for visibility, clamp to 1.0
        # Gradient magnitudes in 8-bit images max at ~255*√2 ≈ 361
        max_possible = 255.0 * np.sqrt(2.0)
        mean_mag = float(np.mean(magnitude))
        texture_energy = min(mean_mag / max_possible * 3.0, 1.0)

        # --- 5. Edge density: proportion of pixels above (mean + std) threshold ---
        mag_mean = float(np.mean(magnitude))
        mag_std = float(np.std(magnitude))
        edge_threshold = mag_mean + mag_std
        edge_mask = magnitude > edge_threshold  # bool mask
        edge_density = float(np.sum(edge_mask)) / (h * w)

        # --- 6. Uniformity: variance in 16×16 blocks ---
        uniformity = _compute_uniformity(magnitude, _BLOCK_SIZE)

        # --- 7. Dominant direction ---
        dominant_direction = _compute_dominant_direction(direction, edge_mask)

        # --- 8. Cultural verdict ---
        tradition = input_data.tradition.strip()
        cultural_verdict = _build_verdict(texture_energy, edge_density, tradition)

        # --- 9. Confidence ---
        confidence = _compute_confidence(texture_energy, tradition)

        # --- 10. Annotated evidence image (green edge overlay) ---
        annotated = _build_annotated_image(rgb, edge_mask)
        annotated_png = _ndarray_to_png(annotated)

        evidence = VisualEvidence(
            annotated_image=annotated_png,
            summary=(
                f"Texture energy: {texture_energy:.2f}, "
                f"edge density: {edge_density:.1%}, "
                f"direction: {dominant_direction or 'none'}. "
                f"{cultural_verdict}"
            ),
            details={
                "texture_energy": texture_energy,
                "uniformity": uniformity,
                "dominant_direction": dominant_direction,
                "edge_density": edge_density,
                "tradition": tradition or "general",
                "edge_threshold": edge_threshold,
            },
            confidence=confidence,
        )

        return BrushstrokeOutput(
            texture_energy=texture_energy,
            uniformity=uniformity,
            dominant_direction=dominant_direction,
            edge_density=edge_density,
            cultural_verdict=cultural_verdict,
            evidence=evidence,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _compute_uniformity(magnitude: np.ndarray, block_size: int) -> float:
    """Compute stroke uniformity via variance-of-block-variances.

    Divides the magnitude map into block_size×block_size patches,
    computes variance of each block, then:
        uniformity = 1 - normalized std-of-variances

    High uniformity → consistent strokes across the image.
    """
    h, w = magnitude.shape
    block_variances: list[float] = []

    for row in range(0, h - block_size + 1, block_size):
        for col in range(0, w - block_size + 1, block_size):
            block = magnitude[row : row + block_size, col : col + block_size]
            block_variances.append(float(np.var(block)))

    if not block_variances:
        return 1.0

    var_array = np.array(block_variances, dtype=np.float32)
    std_of_vars = float(np.std(var_array))
    mean_of_vars = float(np.mean(var_array))

    # Normalize: divide std by mean to get coefficient of variation, clamp to [0, 1]
    if mean_of_vars < 1e-9:
        return 1.0

    cv = std_of_vars / mean_of_vars
    # CV of 0 → perfectly uniform (uniformity=1.0); CV ≥ 1 → highly non-uniform (uniformity→0)
    uniformity = max(0.0, 1.0 - min(cv, 1.0))
    return float(uniformity)


def _compute_dominant_direction(
    direction: np.ndarray,
    edge_mask: np.ndarray,
) -> str | None:
    """Bin gradient directions into 4 quadrants, weighted by magnitude at edge pixels.

    Quadrant mapping (angle in radians from arctan2):
        horizontal:        [-π/8, π/8] ∪ [7π/8, π] ∪ [-π, -7π/8]
        diagonal_rising:   [π/8, 3π/8]   (↗ direction)
        vertical:          [3π/8, 5π/8] ∪ [-5π/8, -3π/8]
        diagonal_falling:  [5π/8, 7π/8] ∪ [-3π/8, -π/8]

    Returns None if no significant edges present.
    """
    edge_directions = direction[edge_mask]
    if edge_directions.size == 0:
        return None

    # Normalize angles to [0, π) — direction only, not sign
    # arctan2 gives angle of gradient; for stroke direction we use abs mod π
    abs_angles = np.abs(edge_directions)  # [0, π]

    # Bin into 4 quadrants of size π/4
    pi = np.pi
    bins = {
        "horizontal": 0.0,
        "diagonal_rising": 0.0,
        "vertical": 0.0,
        "diagonal_falling": 0.0,
    }

    for angle in abs_angles:
        angle = angle % pi  # [0, π)
        if angle < pi / 4:
            bins["horizontal"] += 1.0
        elif angle < pi / 2:
            bins["diagonal_rising"] += 1.0
        elif angle < 3 * pi / 4:
            bins["vertical"] += 1.0
        else:
            bins["diagonal_falling"] += 1.0

    total = sum(bins.values())
    if total == 0:
        return None

    # Check if any direction has a clear plurality (> 30% of edges)
    dominant = max(bins, key=bins.__getitem__)
    dominant_fraction = bins[dominant] / total

    if dominant_fraction < 0.30:
        # No clear dominant direction
        return None

    return dominant


def _build_verdict(texture_energy: float, edge_density: float, tradition: str) -> str:
    """Build a human-readable cultural verdict string."""
    expected_style = _TRADITION_STYLE.get(tradition, "")

    energy_desc = (
        "high energy" if texture_energy > 0.5
        else "moderate energy" if texture_energy > 0.2
        else "low energy"
    )

    if not tradition or not expected_style:
        return (
            f"Brushstroke analysis: {energy_desc} (energy={texture_energy:.2f}), "
            f"edge density={edge_density:.1%}. "
            "No tradition specified — provide a tradition for cultural assessment."
        )

    style_min, style_max = _STYLE_THRESHOLDS.get(expected_style, (0.0, 1.0))

    if expected_style == "expressive":
        if texture_energy >= style_min:
            return (
                f"Brushstroke energy ({texture_energy:.2f}) aligns with {tradition}'s expressive style. "
                f"Visible, dynamic strokes are consistent with tradition expectations."
            )
        else:
            return (
                f"Brushstroke energy ({texture_energy:.2f}) is lower than expected for {tradition}. "
                f"The tradition values expressive, visible strokes — consider more dynamic brushwork."
            )

    elif expected_style == "smooth":
        if texture_energy <= style_max:
            return (
                f"Brushstroke energy ({texture_energy:.2f}) aligns with {tradition}'s refined smooth style. "
                f"Fine, controlled strokes are consistent with tradition expectations."
            )
        else:
            return (
                f"Brushstroke energy ({texture_energy:.2f}) exceeds the smooth threshold for {tradition}. "
                f"The tradition values fine, controlled strokes — consider more delicate brushwork."
            )

    elif expected_style == "clean":
        if texture_energy <= style_max:
            return (
                f"Brushstroke energy ({texture_energy:.2f}) aligns with {tradition}'s clean flat areas. "
                f"Minimal texture is consistent with tradition expectations."
            )
        else:
            return (
                f"Brushstroke energy ({texture_energy:.2f}) is higher than expected for {tradition}. "
                f"The tradition values clean, flat color areas — reduce texture for better alignment."
            )

    # Fallback
    return (
        f"Brushstroke analysis for {tradition}: {energy_desc} "
        f"(energy={texture_energy:.2f}, edge density={edge_density:.1%})."
    )


def _compute_confidence(texture_energy: float, tradition: str) -> float:
    """Compute confidence based on how clearly the energy matches the tradition's expected style.

    - Clearly matching or mismatching → higher confidence (up to 0.90)
    - Near style boundary → lower confidence (down to 0.55)
    """
    expected_style = _TRADITION_STYLE.get(tradition, "")
    if not expected_style:
        return 0.70  # moderate confidence for unknown traditions

    style_min, style_max = _STYLE_THRESHOLDS.get(expected_style, (0.0, 1.0))

    if expected_style == "expressive":
        # Clear if energy >> style_min or clearly below
        dist = abs(texture_energy - style_min)
        return min(0.55 + dist * 1.5, 0.90)

    elif expected_style in ("smooth", "clean"):
        # Clear if energy << style_max or clearly above
        dist = abs(texture_energy - style_max)
        return min(0.55 + dist * 1.5, 0.90)

    return 0.70


def _build_annotated_image(rgb: np.ndarray, edge_mask: np.ndarray) -> np.ndarray:
    """Build an annotated RGB image with green overlay on detected edge pixels."""
    annotated = rgb.copy().astype(np.float32)

    # Green overlay on edge pixels (alpha blend)
    alpha = 0.50
    annotated[edge_mask, 0] = annotated[edge_mask, 0] * (1 - alpha)          # R → darken
    annotated[edge_mask, 1] = annotated[edge_mask, 1] * (1 - alpha) + 200 * alpha  # G → green
    annotated[edge_mask, 2] = annotated[edge_mask, 2] * (1 - alpha)          # B → darken

    return np.clip(annotated, 0, 255).astype(np.uint8)


def _ndarray_to_png(arr: np.ndarray) -> bytes:
    """Convert (H, W, 3) uint8 RGB ndarray to PNG bytes."""
    pil = Image.fromarray(arr, mode="RGB")
    buf = io.BytesIO()
    pil.save(buf, format="PNG", optimize=False, compress_level=1)
    return buf.getvalue()
