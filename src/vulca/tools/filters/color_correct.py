"""ColorCorrect — color balance analysis and correction tool.

Tier 2 image processing filter in the VULCA Tool Protocol.

Algorithm:
1. Decode image via ImageData.from_bytes → to_numpy → (H,W,C) uint8 RGB
2. Compute per-channel means (r_mean, g_mean, b_mean)
3. Channel bias = (channel_mean - overall_mean) / 255 for each channel
4. is_biased = max_bias > 0.05
5. check  mode: return analysis only
6. fix    mode: normalize channels to balanced mean + optional brightness param
7. suggest mode: return text suggestions, no fixed_image
8. Annotated image: RGB channel mean bars at bottom of image
9. Confidence: high if clearly biased or clearly balanced, lower near boundary
"""

from __future__ import annotations

import io

import numpy as np
from PIL import Image, ImageDraw

from vulca.tools.protocol import (
    ImageData,
    ToolCategory,
    ToolConfig,
    ToolSchema,
    VisualEvidence,
    VulcaTool,
)

# Bias threshold above which a channel is considered "biased"
_BIAS_THRESHOLD = 0.05

# Confidence boundary: near this threshold confidence is lower
_CONFIDENCE_HIGH_THRESHOLD = 0.10   # max_bias > this → clearly biased (high conf)
_CONFIDENCE_BOUNDARY_LOW = 0.02     # max_bias < this → clearly balanced (high conf)


class ColorCorrectInput(ToolSchema):
    """Input for ColorCorrect tool."""

    image: bytes  # PNG-encoded image bytes
    tradition: str = ""


class ColorCorrectOutput(ToolSchema):
    """Output for ColorCorrect tool."""

    channel_bias: dict[str, float]  # {"red": 0.2, "green": -0.05, "blue": -0.15}
    brightness: float               # mean brightness 0-255
    contrast: float                 # std deviation across all channels
    fixed_image: bytes | None = None  # corrected image (fix mode only)
    suggestions: list[str] = []     # textual suggestions (suggest mode)
    evidence: VisualEvidence        # REQUIRED


class ColorCorrect(VulcaTool):
    """Analyze color balance (channel bias, brightness, contrast)."""

    name = "color_correct"
    display_name = "Color Correct"
    description = (
        "Analyze color balance (channel bias, brightness, contrast). "
        "In fix mode, normalizes channel balance and applies optional brightness adjustment. "
        "In suggest mode, returns textual recommendations."
    )
    category = ToolCategory.FILTER
    replaces: dict = {}
    max_seconds = 10

    Input = ColorCorrectInput
    Output = ColorCorrectOutput

    # -----------------------------------------------------------------------
    # Main execute
    # -----------------------------------------------------------------------

    def execute(self, input_data: ColorCorrectInput, config: ToolConfig) -> ColorCorrectOutput:
        """Run color correction analysis (and optionally apply correction)."""
        # 1. Decode image
        img_data = ImageData.from_bytes(input_data.image)
        arr = img_data.to_numpy().astype(np.float32)  # (H, W, 3) float32 RGB

        # 2. Per-channel means
        r_mean = float(np.mean(arr[:, :, 0]))
        g_mean = float(np.mean(arr[:, :, 1]))
        b_mean = float(np.mean(arr[:, :, 2]))
        overall_mean = (r_mean + g_mean + b_mean) / 3.0

        # 3. Channel bias = (channel_mean - overall_mean) / 255
        channel_bias = {
            "red":   (r_mean - overall_mean) / 255.0,
            "green": (g_mean - overall_mean) / 255.0,
            "blue":  (b_mean - overall_mean) / 255.0,
        }

        # 4. Derived stats
        max_abs_bias = max(abs(v) for v in channel_bias.values())
        is_biased = max_abs_bias > _BIAS_THRESHOLD

        brightness = float(np.mean(arr))  # overall mean brightness 0-255
        contrast = float(np.std(arr))     # std deviation across all channels

        # 5. Dispatch by mode
        fixed_image: bytes | None = None
        suggestions: list[str] = []

        if config.mode == "fix":
            fixed_image = self._apply_correction(arr, channel_bias, config)

        elif config.mode == "suggest":
            suggestions = self._build_suggestions(channel_bias, is_biased, brightness)

        # 6. Build annotated image (channel bar chart at bottom)
        annotated_png = self._build_annotated_image(
            arr,
            r_mean=r_mean,
            g_mean=g_mean,
            b_mean=b_mean,
        )

        # 7. Compute confidence
        confidence = self._compute_confidence(max_abs_bias)

        # 8. Build dominant-cast label for summary
        dominant = _dominant_cast(channel_bias)
        if is_biased:
            summary = f"Color cast detected: {dominant} bias (max bias {max_abs_bias:.3f})."
        else:
            summary = f"Color balance is acceptable (max bias {max_abs_bias:.3f})."

        evidence = VisualEvidence(
            annotated_image=annotated_png,
            summary=summary,
            details={
                "channel_bias": channel_bias,
                "is_biased": is_biased,
                "max_abs_bias": round(max_abs_bias, 4),
                "dominant_cast": dominant,
                "r_mean": round(r_mean, 2),
                "g_mean": round(g_mean, 2),
                "b_mean": round(b_mean, 2),
                "overall_mean": round(overall_mean, 2),
            },
            confidence=confidence,
        )

        return ColorCorrectOutput(
            channel_bias=channel_bias,
            brightness=brightness,
            contrast=contrast,
            fixed_image=fixed_image,
            suggestions=suggestions,
            evidence=evidence,
        )

    # -----------------------------------------------------------------------
    # Fix: normalize channels to balanced mean + optional brightness scaling
    # -----------------------------------------------------------------------

    def _apply_correction(
        self,
        arr: np.ndarray,
        channel_bias: dict[str, float],
        config: ToolConfig,
    ) -> bytes:
        """Return PNG bytes of the corrected image."""
        corrected = arr.copy()

        # Normalize each channel toward the overall mean
        r_mean = float(np.mean(corrected[:, :, 0]))
        g_mean = float(np.mean(corrected[:, :, 1]))
        b_mean = float(np.mean(corrected[:, :, 2]))
        target_mean = (r_mean + g_mean + b_mean) / 3.0

        for ch_idx, ch_mean in enumerate([r_mean, g_mean, b_mean]):
            if ch_mean > 0:
                corrected[:, :, ch_idx] = corrected[:, :, ch_idx] * (target_mean / ch_mean)

        # Optional brightness adjustment
        brightness_scale = float(config.params.get("brightness", 1.0))
        if brightness_scale != 1.0:
            corrected = corrected * brightness_scale

        # Clamp to [0, 255] and convert to uint8
        corrected = np.clip(corrected, 0, 255).astype(np.uint8)

        pil = Image.fromarray(corrected, mode="RGB")
        buf = io.BytesIO()
        pil.save(buf, format="PNG", optimize=False, compress_level=1)
        return buf.getvalue()

    # -----------------------------------------------------------------------
    # Suggest: build textual recommendations
    # -----------------------------------------------------------------------

    def _build_suggestions(
        self,
        channel_bias: dict[str, float],
        is_biased: bool,
        brightness: float,
    ) -> list[str]:
        suggestions: list[str] = []

        if not is_biased:
            suggestions.append(
                "Color balance is acceptable — no correction required."
            )
            return suggestions

        # Identify which channels are over/under-represented
        for channel, bias in channel_bias.items():
            if bias > _BIAS_THRESHOLD:
                suggestions.append(
                    f"Reduce the {channel} channel (bias +{bias:.3f}): "
                    f"use a {_complement(channel)} wash or adjust white balance."
                )
            elif bias < -_BIAS_THRESHOLD:
                suggestions.append(
                    f"Boost the {channel} channel (bias {bias:.3f}): "
                    f"add more {channel} tones or adjust white balance."
                )

        if brightness < 40:
            suggestions.append(
                "Image is very dark (brightness {:.1f}/255). "
                "Consider increasing exposure.".format(brightness)
            )
        elif brightness > 220:
            suggestions.append(
                "Image is very bright (brightness {:.1f}/255). "
                "Consider reducing exposure.".format(brightness)
            )

        return suggestions

    # -----------------------------------------------------------------------
    # Annotated image: RGB channel mean bars at bottom
    # -----------------------------------------------------------------------

    def _build_annotated_image(
        self,
        arr: np.ndarray,
        r_mean: float,
        g_mean: float,
        b_mean: float,
    ) -> bytes:
        """Draw channel mean bars on a copy of the original image."""
        h, w, _ = arr.shape
        bar_height = max(16, h // 8)
        bar_width = max(w, 60)

        # Canvas = original + bar strip at bottom
        canvas_h = h + bar_height
        canvas = np.full((canvas_h, bar_width, 3), 30, dtype=np.uint8)  # dark bg
        # Paste original (may need padding if w < bar_width)
        canvas[:h, :w, :] = arr.astype(np.uint8)

        # Draw 3 coloured bars proportional to channel mean (0-255)
        third = bar_width // 3
        # Red bar
        red_end = int(third * r_mean / 255.0)
        canvas[h:, 0:red_end, 0] = 220
        canvas[h:, 0:red_end, 1] = 50
        canvas[h:, 0:red_end, 2] = 50

        # Green bar
        green_end = int(third * g_mean / 255.0)
        canvas[h:, third:third + green_end, 0] = 50
        canvas[h:, third:third + green_end, 1] = 200
        canvas[h:, third:third + green_end, 2] = 50

        # Blue bar
        blue_end = int(third * b_mean / 255.0)
        canvas[h:, 2 * third:2 * third + blue_end, 0] = 50
        canvas[h:, 2 * third:2 * third + blue_end, 1] = 80
        canvas[h:, 2 * third:2 * third + blue_end, 2] = 220

        pil = Image.fromarray(canvas, mode="RGB")
        buf = io.BytesIO()
        pil.save(buf, format="PNG", optimize=False, compress_level=1)
        return buf.getvalue()

    # -----------------------------------------------------------------------
    # Confidence computation
    # -----------------------------------------------------------------------

    @staticmethod
    def _compute_confidence(max_abs_bias: float) -> float:
        """Return confidence in [0.6, 0.95].

        High confidence when clearly biased (>0.10) or clearly balanced (<0.02).
        Lower confidence near the decision boundary (0.05 threshold).
        """
        if max_abs_bias > _CONFIDENCE_HIGH_THRESHOLD:
            return 0.95
        if max_abs_bias < _CONFIDENCE_BOUNDARY_LOW:
            return 0.90
        # Linear interpolation: boundary region [0.02, 0.10] → [0.60, 0.95]
        t = (max_abs_bias - _CONFIDENCE_BOUNDARY_LOW) / (
            _CONFIDENCE_HIGH_THRESHOLD - _CONFIDENCE_BOUNDARY_LOW
        )
        # Near 0.05 threshold → lowest confidence (~0.60)
        # We use a tent function: confidence dips at the threshold
        distance_from_threshold = abs(max_abs_bias - _BIAS_THRESHOLD)
        normalized_dist = distance_from_threshold / (_CONFIDENCE_HIGH_THRESHOLD - _BIAS_THRESHOLD + 1e-9)
        return max(0.60, min(0.90, 0.60 + 0.30 * normalized_dist))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _dominant_cast(channel_bias: dict[str, float]) -> str:
    """Return the name of the most biased channel, or 'none' if balanced."""
    max_ch = max(channel_bias, key=lambda k: abs(channel_bias[k]))
    if abs(channel_bias[max_ch]) <= _BIAS_THRESHOLD:
        return "none"
    direction = "warm" if channel_bias[max_ch] > 0 and max_ch == "red" else max_ch
    return f"{max_ch} ({'+' if channel_bias[max_ch] > 0 else ''}{channel_bias[max_ch]:.3f})"


def _complement(channel: str) -> str:
    """Return the complementary color name for a given channel."""
    return {"red": "cyan", "green": "magenta", "blue": "yellow"}.get(channel, channel)
