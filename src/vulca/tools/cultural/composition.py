"""CompositionAnalyzer — Tier 1 cultural tool for composition analysis.

Analyzes visual weight distribution, rule-of-thirds alignment, and balance
in artwork images. Maps findings to tradition-specific cultural norms.

Algorithm:
1. Convert to grayscale, invert (dark subjects = high weight)
2. Compute visual center of mass via weighted average of pixel coordinates
3. Center weight: weight in center third / total weight
4. Thirds alignment: proximity of visual center to nearest thirds intersection
5. Balance: compare left/right and top/bottom halves
6. Detected rules: center_composition if center_weight > 0.4, rule_of_thirds
   if alignment > 0.6, etc.
7. Cultural verdict based on tradition preferences:
   - chinese_xieyi: prefers asymmetric
   - chinese_gongbi: prefers balanced
   - japanese_sumi_e: prefers asymmetric
   - ukiyo_e: prefers dynamic diagonals
8. Annotated image: green thirds grid + red circle at visual center
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
# Tradition preferences
# ---------------------------------------------------------------------------

_TRADITION_PREFERENCES: dict[str, str] = {
    "chinese_xieyi": "asymmetric",
    "chinese_gongbi": "balanced",
    "japanese_sumi_e": "asymmetric",
    "ukiyo_e": "dynamic_diagonals",
}

# Balance labels (returned in output.balance)
_BALANCE_LABELS = (
    "balanced",
    "left_heavy",
    "right_heavy",
    "top_heavy",
    "bottom_heavy",
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class CompositionInput(ToolSchema):
    """Input schema for CompositionAnalyzer."""

    image: bytes  # PNG-encoded image bytes
    tradition: str = ""


class CompositionOutput(ToolSchema):
    """Output schema for CompositionAnalyzer."""

    center_weight: float          # 0-1, visual weight in center third
    thirds_alignment: float       # 0-1, alignment to rule-of-thirds grid
    visual_center: dict[str, float]  # {x: 0-1, y: 0-1} — normalised coords
    balance: str                  # one of _BALANCE_LABELS
    detected_rules: list[str]     # e.g. ["rule_of_thirds", "center_composition"]
    cultural_verdict: str         # human-readable cultural assessment
    evidence: VisualEvidence      # annotated image + summary


# ---------------------------------------------------------------------------
# CompositionAnalyzer
# ---------------------------------------------------------------------------


class CompositionAnalyzer(VulcaTool):
    """Detect composition structure and cultural alignment in artwork.

    Tier 1 cultural tool — runs deterministically with cv2/numpy, no LLM.
    Replaces L1 (Cultural Authenticity) in the evaluate pipeline.
    """

    name = "composition_analyze"
    display_name = "Composition Analyzer"
    description = (
        "Detect visual weight distribution, rule-of-thirds alignment, and compositional "
        "balance in artwork. Maps findings to tradition-specific cultural norms."
    )
    category = ToolCategory.COMPOSITION
    replaces: dict[str, list[str]] = {"evaluate": ["L1"]}
    max_seconds = 10
    is_concurrent_safe = True
    is_read_only = True
    search_hint = "composition balance rule thirds visual weight"

    Input = CompositionInput
    Output = CompositionOutput

    # Thresholds
    _CENTER_WEIGHT_THRESHOLD: float = 0.40   # > this → center_composition
    _THIRDS_ALIGN_THRESHOLD: float = 0.60    # > this → rule_of_thirds
    _BALANCE_EPS: float = 0.08               # difference fraction triggering imbalance

    def execute(self, input_data: CompositionInput, config: ToolConfig) -> CompositionOutput:
        """Run composition analysis on the input image."""
        # --- 1. Decode image ---
        img_data = ImageData.from_bytes(input_data.image)
        rgb = img_data.to_numpy()  # (H, W, 3) uint8

        h, w = rgb.shape[:2]

        # --- 2. Grayscale + invert → subject weight map ---
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
        # Invert: dark pixels (subjects) get high weight
        weight_map = 255.0 - gray  # (H, W) float32, range [0, 255]

        total_weight = float(np.sum(weight_map))

        # --- 3. Visual center of mass ---
        if total_weight < 1e-6:
            # Uniform image — default to geometric center
            cx_norm, cy_norm = 0.5, 0.5
        else:
            ys, xs = np.mgrid[0:h, 0:w]
            cx = float(np.sum(xs * weight_map)) / total_weight
            cy = float(np.sum(ys * weight_map)) / total_weight
            cx_norm = cx / w
            cy_norm = cy / h

        visual_center = {"x": cx_norm, "y": cy_norm}

        # --- 4. Center weight: weight inside center third of image ---
        # Center third: cols [w/3, 2w/3], rows [h/3, 2h/3]
        col_lo = w // 3
        col_hi = w - w // 3
        row_lo = h // 3
        row_hi = h - h // 3
        center_region_weight = float(np.sum(weight_map[row_lo:row_hi, col_lo:col_hi]))
        center_weight = center_region_weight / total_weight if total_weight > 1e-6 else 0.5

        # --- 5. Thirds alignment ---
        # Four intersection points at (1/3, 1/3), (2/3, 1/3), (1/3, 2/3), (2/3, 2/3)
        thirds_points = [
            (1 / 3, 1 / 3),
            (2 / 3, 1 / 3),
            (1 / 3, 2 / 3),
            (2 / 3, 2 / 3),
        ]
        # Max possible distance from any point to any intersection (approx √2/2 ≈ 0.707)
        max_possible_dist = (2**0.5) / 2.0
        min_dist = min(
            ((cx_norm - tx) ** 2 + (cy_norm - ty) ** 2) ** 0.5
            for tx, ty in thirds_points
        )
        # Alignment: 1.0 = perfectly on an intersection, 0.0 = furthest possible
        thirds_alignment = max(0.0, 1.0 - min_dist / max_possible_dist)

        # --- 6. Balance: compare halves ---
        left_w = float(np.sum(weight_map[:, : w // 2]))
        right_w = float(np.sum(weight_map[:, w // 2 :]))
        top_w = float(np.sum(weight_map[: h // 2, :]))
        bottom_w = float(np.sum(weight_map[h // 2 :, :]))

        half_total_lr = left_w + right_w
        half_total_tb = top_w + bottom_w

        eps = self._BALANCE_EPS
        balance = "balanced"
        if half_total_lr > 1e-6:
            lr_diff = (left_w - right_w) / half_total_lr
            if lr_diff > eps:
                balance = "left_heavy"
            elif lr_diff < -eps:
                balance = "right_heavy"
        if balance == "balanced" and half_total_tb > 1e-6:
            tb_diff = (top_w - bottom_w) / half_total_tb
            if tb_diff > eps:
                balance = "top_heavy"
            elif tb_diff < -eps:
                balance = "bottom_heavy"

        # --- 7. Detected rules ---
        detected_rules: list[str] = []
        center_weight_thresh = float(
            config.params.get("center_weight_threshold", self._CENTER_WEIGHT_THRESHOLD)
        )
        thirds_align_thresh = float(
            config.params.get("thirds_align_threshold", self._THIRDS_ALIGN_THRESHOLD)
        )
        if center_weight > center_weight_thresh:
            detected_rules.append("center_composition")
        if thirds_alignment > thirds_align_thresh:
            detected_rules.append("rule_of_thirds")
        if balance != "balanced":
            detected_rules.append("asymmetric_balance")

        # --- 8. Cultural verdict ---
        tradition = input_data.tradition.strip()
        cultural_verdict = _build_verdict(
            tradition=tradition,
            center_weight=center_weight,
            thirds_alignment=thirds_alignment,
            balance=balance,
            detected_rules=detected_rules,
        )

        # --- 9. Evidence image: thirds grid + visual center marker ---
        annotated = _build_annotated_image(rgb, cx_norm, cy_norm, w, h)
        annotated_png = _ndarray_to_png(annotated)

        # Confidence: higher when compositional signals are unambiguous
        confidence = _compute_confidence(center_weight, thirds_alignment)

        evidence = VisualEvidence(
            annotated_image=annotated_png,
            summary=(
                f"Visual center at ({cx_norm:.2f}, {cy_norm:.2f}); "
                f"center_weight={center_weight:.2f}, thirds_alignment={thirds_alignment:.2f}; "
                f"balance={balance}. "
                + (f"Rules: {', '.join(detected_rules)}." if detected_rules else "No strong compositional rules detected.")
            ),
            details={
                "center_weight": center_weight,
                "thirds_alignment": thirds_alignment,
                "visual_center": visual_center,
                "balance": balance,
                "detected_rules": detected_rules,
                "tradition": tradition or "general",
            },
            confidence=confidence,
        )

        return CompositionOutput(
            center_weight=center_weight,
            thirds_alignment=thirds_alignment,
            visual_center=visual_center,
            balance=balance,
            detected_rules=detected_rules,
            cultural_verdict=cultural_verdict,
            evidence=evidence,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_verdict(
    tradition: str,
    center_weight: float,
    thirds_alignment: float,
    balance: str,
    detected_rules: list[str],
) -> str:
    """Build a human-readable cultural verdict based on tradition preferences."""
    pref = _TRADITION_PREFERENCES.get(tradition, "general")

    composition_desc = []
    if "center_composition" in detected_rules:
        composition_desc.append("centered composition")
    if "rule_of_thirds" in detected_rules:
        composition_desc.append("rule-of-thirds alignment")
    if "asymmetric_balance" in detected_rules:
        composition_desc.append(f"{balance} asymmetry")
    if not composition_desc:
        composition_desc.append("neutral composition")

    comp_str = ", ".join(composition_desc)

    if pref == "asymmetric":
        if "asymmetric_balance" in detected_rules or "rule_of_thirds" in detected_rules:
            return (
                f"The {comp_str} aligns well with {tradition or 'this tradition'}'s preference "
                f"for asymmetric, dynamic arrangements. "
                f"Thirds alignment: {thirds_alignment:.2f}; balance: {balance}."
            )
        else:
            return (
                f"The {comp_str} may feel too static for {tradition or 'this tradition'}, "
                f"which favors asymmetric placement and negative-space play. "
                f"Consider shifting the visual center away from the geometric center."
            )

    elif pref == "balanced":
        if balance == "balanced":
            return (
                f"The {comp_str} is well-balanced, which suits "
                f"{tradition or 'this tradition'}'s preference for harmonious symmetry. "
                f"Center weight: {center_weight:.2f}."
            )
        else:
            return (
                f"The {comp_str} shows {balance} imbalance, which may conflict with "
                f"{tradition or 'this tradition'}'s preference for harmonious balance. "
                f"Consider rebalancing the visual weight."
            )

    elif pref == "dynamic_diagonals":
        if "asymmetric_balance" in detected_rules:
            return (
                f"The {comp_str} creates dynamic tension that suits "
                f"{tradition or 'this tradition'}'s aesthetic of movement and energy. "
                f"Thirds alignment: {thirds_alignment:.2f}."
            )
        else:
            return (
                f"The {comp_str} may lack the diagonal energy preferred by "
                f"{tradition or 'this tradition'}. "
                f"Consider introducing stronger directional movement."
            )

    else:  # general
        return (
            f"Composition: {comp_str}. "
            f"Visual center at ({center_weight:.2f} center weight), "
            f"thirds alignment {thirds_alignment:.2f}, {balance} balance."
        )


def _compute_confidence(center_weight: float, thirds_alignment: float) -> float:
    """Confidence based on strength of detected compositional signals."""
    # Strong signal: clearly center-heavy or clearly on thirds
    max_signal = max(center_weight, thirds_alignment)
    if max_signal > 0.75:
        return 0.90
    if max_signal > 0.50:
        return 0.75
    # Weak signal: ambiguous composition
    return 0.60


def _build_annotated_image(
    rgb: np.ndarray,
    cx_norm: float,
    cy_norm: float,
    w: int,
    h: int,
) -> np.ndarray:
    """Build annotated image: green thirds grid + red circle at visual center.

    Args:
        rgb: (H, W, 3) uint8 RGB ndarray.
        cx_norm: Visual center x, normalised to [0, 1].
        cy_norm: Visual center y, normalised to [0, 1].
        w: Image width in pixels.
        h: Image height in pixels.

    Returns:
        Annotated (H, W, 3) uint8 RGB ndarray.
    """
    annotated = rgb.copy()

    # --- Green thirds grid lines ---
    green = (34, 197, 94)  # RGB
    thickness = max(1, min(w, h) // 150)

    # Vertical lines at x = w/3 and x = 2w/3
    x1 = w // 3
    x2 = w - w // 3
    cv2.line(annotated, (x1, 0), (x1, h - 1), green, thickness)
    cv2.line(annotated, (x2, 0), (x2, h - 1), green, thickness)

    # Horizontal lines at y = h/3 and y = 2h/3
    y1 = h // 3
    y2 = h - h // 3
    cv2.line(annotated, (0, y1), (w - 1, y1), green, thickness)
    cv2.line(annotated, (0, y2), (w - 1, y2), green, thickness)

    # --- Red circle at visual center ---
    red = (220, 38, 38)  # RGB
    cx_px = int(cx_norm * w)
    cy_px = int(cy_norm * h)
    radius = max(5, min(w, h) // 20)
    cv2.circle(annotated, (cx_px, cy_px), radius, red, thickness + 1)
    # Small filled dot at exact center
    cv2.circle(annotated, (cx_px, cy_px), max(2, radius // 4), red, -1)

    return annotated


def _ndarray_to_png(arr: np.ndarray) -> bytes:
    """Convert (H, W, 3) uint8 RGB ndarray to PNG bytes."""
    pil = Image.fromarray(arr, mode="RGB")
    buf = io.BytesIO()
    pil.save(buf, format="PNG", optimize=False, compress_level=1)
    return buf.getvalue()
