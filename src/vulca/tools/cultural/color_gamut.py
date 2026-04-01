"""ColorGamutChecker — Tier 1 cultural tool for tradition-specific saturation analysis.

Detects out-of-gamut pixels whose HSV saturation exceeds tradition-specific thresholds.
Supports fix mode (desaturate) and generates annotated evidence images with red overlay.

Algorithm:
1. Decode image → (H, W, C) uint8 RGB ndarray via ImageData
2. Convert to HSV (cv2.COLOR_RGB2HSV)
3. Extract mean saturation from the S channel
4. Apply tradition-specific max saturation threshold:
   - chinese_xieyi:  max_sat=60   (low saturation ink wash)
   - chinese_gongbi: max_sat=120
   - japanese_sumi_e: max_sat=50
   - ukiyo_e:        max_sat=160
   - default:        max_sat=180
5. out_of_gamut_pct = fraction of pixels with S > max_sat
6. compliance = 1.0 - out_of_gamut_pct
7. Dominant colors via cv2.kmeans (k=5, subsampled to ≤10000 pixels)
8. Fix mode: desaturate out-of-gamut pixels to max_sat
9. Annotated evidence: red overlay on out-of-gamut pixels
10. User thresholds: config.thresholds["max_saturation"] overrides tradition default
"""

from __future__ import annotations

import io

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
# Tradition-specific max saturation thresholds (HSV S channel, 0-255 scale)
# ---------------------------------------------------------------------------

_TRADITION_MAX_SAT: dict[str, int] = {
    "chinese_xieyi": 60,
    "chinese_gongbi": 120,
    "japanese_sumi_e": 50,
    "ukiyo_e": 160,
}
_DEFAULT_MAX_SAT: int = 180

# Number of dominant colors to extract via k-means
_KMEANS_K: int = 5
_KMEANS_MAX_PIXELS: int = 10_000


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ColorGamutInput(ToolSchema):
    """Input schema for ColorGamutChecker."""

    image: bytes  # PNG-encoded image bytes
    tradition: str = ""


class ColorGamutOutput(ToolSchema):
    """Output schema for ColorGamutChecker."""

    compliance: float               # 0-1, fraction of pixels within gamut
    mean_saturation: float          # 0-255, mean HSV S channel value
    dominant_colors: list[list[int]]  # [[R, G, B], ...] dominant palette
    out_of_gamut_pct: float         # 0-1, fraction of pixels exceeding max_sat
    cultural_verdict: str           # human-readable assessment
    fixed_image: bytes | None = None  # PNG bytes of desaturated image (fix mode only)
    evidence: VisualEvidence        # annotated image + analysis summary


# ---------------------------------------------------------------------------
# ColorGamutChecker
# ---------------------------------------------------------------------------


class ColorGamutChecker(VulcaTool):
    """Check color saturation compliance against tradition-specific gamut thresholds.

    Tier 1 cultural tool — runs deterministically with cv2, no LLM required.
    Replaces L3 (Creative Synthesis) in the evaluate pipeline.
    """

    name = "color_gamut_check"
    display_name = "Color Gamut Checker"
    description = (
        "Detect out-of-gamut pixels by checking HSV saturation against "
        "tradition-specific thresholds. Supports fix mode (auto-desaturate). "
        "Replaces L3 (Creative Synthesis) dimension in the evaluate pipeline."
    )
    category = ToolCategory.CULTURAL_CHECK
    replaces: dict[str, list[str]] = {"evaluate": ["L3"]}
    max_seconds = 15
    is_concurrent_safe = True
    is_read_only = True

    Input = ColorGamutInput
    Output = ColorGamutOutput

    def execute(self, input_data: ColorGamutInput, config: ToolConfig) -> ColorGamutOutput:
        """Run color gamut analysis on the input image."""
        # --- 1. Decode image ---
        img_data = ImageData.from_bytes(input_data.image)
        rgb = img_data.to_numpy()  # (H, W, 3) uint8

        # --- 2. Convert to HSV ---
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)  # H: 0-179, S: 0-255, V: 0-255
        s_channel = hsv[:, :, 1].astype(np.float32)

        # --- 3. Mean saturation ---
        mean_saturation = float(np.mean(s_channel))

        # --- 4. Tradition-specific threshold ---
        tradition = input_data.tradition.strip()
        if "max_saturation" in config.thresholds:
            max_sat = int(config.thresholds["max_saturation"])
        else:
            max_sat = _TRADITION_MAX_SAT.get(tradition, _DEFAULT_MAX_SAT)

        # --- 5. Out-of-gamut fraction ---
        h_pixels, w_pixels = rgb.shape[:2]
        total_pixels = h_pixels * w_pixels
        out_of_gamut_mask = hsv[:, :, 1] > max_sat
        out_of_gamut_count = int(np.sum(out_of_gamut_mask))
        out_of_gamut_pct = out_of_gamut_count / total_pixels

        # --- 6. Compliance ---
        compliance = 1.0 - out_of_gamut_pct

        # --- 7. Dominant colors via k-means ---
        dominant_colors = _extract_dominant_colors(rgb, k=_KMEANS_K, max_pixels=_KMEANS_MAX_PIXELS)

        # --- 8. Cultural verdict ---
        cultural_verdict = _build_verdict(
            compliance=compliance,
            out_of_gamut_pct=out_of_gamut_pct,
            mean_saturation=mean_saturation,
            max_sat=max_sat,
            tradition=tradition or "general",
        )

        # --- 9. Fix mode: desaturate out-of-gamut pixels ---
        fixed_image: bytes | None = None
        if config.mode == "fix" and out_of_gamut_count > 0:
            fixed_image = _desaturate_out_of_gamut(hsv, out_of_gamut_mask, max_sat)

        # --- 10. Annotated evidence image ---
        annotated_png = _build_annotated_image(rgb, out_of_gamut_mask)

        # Confidence: higher when clearly in or clearly out of gamut
        confidence = _compute_confidence(compliance)

        evidence = VisualEvidence(
            annotated_image=annotated_png,
            summary=(
                f"Color gamut compliance: {compliance:.1%} "
                f"({out_of_gamut_pct:.1%} out-of-gamut, "
                f"mean S={mean_saturation:.1f}/255, max_sat={max_sat}). "
                f"{cultural_verdict}"
            ),
            details={
                "compliance": compliance,
                "out_of_gamut_pct": out_of_gamut_pct,
                "mean_saturation": mean_saturation,
                "max_sat_threshold": max_sat,
                "tradition": tradition or "general",
                "dominant_color_count": len(dominant_colors),
            },
            confidence=confidence,
        )

        return ColorGamutOutput(
            compliance=compliance,
            mean_saturation=mean_saturation,
            dominant_colors=dominant_colors,
            out_of_gamut_pct=out_of_gamut_pct,
            cultural_verdict=cultural_verdict,
            fixed_image=fixed_image,
            evidence=evidence,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _extract_dominant_colors(
    rgb: np.ndarray,
    k: int = 5,
    max_pixels: int = 10_000,
) -> list[list[int]]:
    """Extract k dominant colors from an RGB image using cv2.kmeans.

    Args:
        rgb: (H, W, 3) uint8 RGB ndarray.
        k: Number of dominant colors to extract.
        max_pixels: Subsample to at most this many pixels before clustering.

    Returns:
        List of [R, G, B] integer color lists (k entries, sorted by cluster size desc).
    """
    h, w = rgb.shape[:2]
    pixels = rgb.reshape(-1, 3).astype(np.float32)  # (N, 3)

    # Subsample if needed
    n_pixels = pixels.shape[0]
    if n_pixels > max_pixels:
        idx = np.random.choice(n_pixels, size=max_pixels, replace=False)
        pixels = pixels[idx]

    # Clamp k to available pixels
    actual_k = min(k, pixels.shape[0])
    if actual_k < 1:
        return []

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    flags = cv2.KMEANS_PP_CENTERS

    try:
        _compactness, labels, centers = cv2.kmeans(
            pixels, actual_k, None, criteria, 5, flags
        )
    except cv2.error:
        # Fallback: return mean color if k-means fails
        mean_color = np.mean(pixels, axis=0).astype(np.uint8).tolist()
        return [[int(c) for c in mean_color]]

    # Sort by cluster size (descending)
    labels_flat = labels.flatten()
    cluster_sizes = np.bincount(labels_flat, minlength=actual_k)
    sorted_indices = np.argsort(cluster_sizes)[::-1]

    dominant: list[list[int]] = []
    for idx in sorted_indices:
        color = centers[idx].astype(np.uint8).tolist()
        dominant.append([int(c) for c in color])

    return dominant


def _desaturate_out_of_gamut(
    hsv: np.ndarray,
    out_of_gamut_mask: np.ndarray,
    max_sat: int,
) -> bytes:
    """Desaturate out-of-gamut pixels to max_sat and return as PNG bytes.

    Args:
        hsv: (H, W, 3) uint8 HSV image (cv2 HSV format).
        out_of_gamut_mask: (H, W) bool mask of pixels with S > max_sat.
        max_sat: Maximum allowed saturation value (0-255).

    Returns:
        PNG-encoded bytes of the fixed RGB image.
    """
    fixed_hsv = hsv.copy()
    fixed_hsv[out_of_gamut_mask, 1] = np.uint8(max_sat)

    # Convert back to RGB
    fixed_rgb = cv2.cvtColor(fixed_hsv, cv2.COLOR_HSV2RGB)

    pil = Image.fromarray(fixed_rgb, mode="RGB")
    buf = io.BytesIO()
    pil.save(buf, format="PNG", optimize=False, compress_level=1)
    return buf.getvalue()


def _build_annotated_image(
    rgb: np.ndarray,
    out_of_gamut_mask: np.ndarray,
) -> bytes:
    """Build an annotated PNG with red overlay on out-of-gamut pixels.

    Args:
        rgb: (H, W, 3) uint8 RGB ndarray.
        out_of_gamut_mask: (H, W) bool mask.

    Returns:
        PNG-encoded bytes of the annotated image.
    """
    annotated = rgb.copy().astype(np.float32)

    # Semi-transparent red overlay on out-of-gamut pixels
    if np.any(out_of_gamut_mask):
        alpha = 0.50
        annotated[out_of_gamut_mask, 0] = annotated[out_of_gamut_mask, 0] * (1 - alpha) + 220 * alpha
        annotated[out_of_gamut_mask, 1] = annotated[out_of_gamut_mask, 1] * (1 - alpha) + 38 * alpha
        annotated[out_of_gamut_mask, 2] = annotated[out_of_gamut_mask, 2] * (1 - alpha) + 38 * alpha

    annotated_uint8 = np.clip(annotated, 0, 255).astype(np.uint8)

    pil = Image.fromarray(annotated_uint8, mode="RGB")
    buf = io.BytesIO()
    pil.save(buf, format="PNG", optimize=False, compress_level=1)
    return buf.getvalue()


def _build_verdict(
    compliance: float,
    out_of_gamut_pct: float,
    mean_saturation: float,
    max_sat: int,
    tradition: str,
) -> str:
    """Build a human-readable cultural verdict string.

    Args:
        compliance: Fraction of pixels within gamut (0-1).
        out_of_gamut_pct: Fraction of pixels exceeding max_sat (0-1).
        mean_saturation: Mean HSV S channel value (0-255).
        max_sat: Maximum allowed saturation (0-255).
        tradition: Tradition label string.

    Returns:
        Human-readable cultural verdict.
    """
    if compliance >= 0.95:
        return (
            f"Excellent gamut compliance ({compliance:.1%}) for {tradition}. "
            f"Mean saturation ({mean_saturation:.1f}/255) well within the "
            f"{tradition} threshold of {max_sat}/255."
        )
    elif compliance >= 0.75:
        return (
            f"Good gamut compliance ({compliance:.1%}) for {tradition}. "
            f"{out_of_gamut_pct:.1%} of pixels exceed the saturation threshold "
            f"({max_sat}/255). Minor adjustments recommended."
        )
    elif compliance >= 0.50:
        return (
            f"Moderate gamut violations ({out_of_gamut_pct:.1%} of pixels) for {tradition}. "
            f"Mean saturation ({mean_saturation:.1f}/255) exceeds the {tradition} "
            f"threshold of {max_sat}/255. Consider desaturating vibrant areas."
        )
    else:
        return (
            f"Significant gamut violation ({out_of_gamut_pct:.1%} of pixels) for {tradition}. "
            f"Mean saturation ({mean_saturation:.1f}/255) is well above the {tradition} "
            f"threshold of {max_sat}/255. Strong desaturation required to match tradition aesthetics."
        )


def _compute_confidence(compliance: float) -> float:
    """Compute confidence score based on compliance distance from boundary (0.5).

    - Very compliant (>0.9) or very non-compliant (<0.1) → high confidence (0.90)
    - Near 0.5 boundary → lower confidence (0.55)
    """
    distance_from_boundary = abs(compliance - 0.5)
    if distance_from_boundary >= 0.40:
        return 0.90
    return 0.55 + 0.35 * (distance_from_boundary / 0.40)
