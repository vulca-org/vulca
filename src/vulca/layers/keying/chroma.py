"""Tier 1 strategies for colored content on colored canvases.

ChromaKeying: Euclidean distance in LINEAR RGB. Gamma-decode before
              computing distance so the smoothstep behaves perceptually
              in low luminance the way the docstring promises.
DeltaEKeying: Perceptual ΔE76 in CIE LAB. ~3× slower, used for low-contrast
              cases (e.g. gongbi color washes on cooked silk).
"""
from __future__ import annotations

import numpy as np

from vulca.layers.keying import CanvasSpec
from vulca.layers.keying._lab import srgb_to_lab, srgb_to_linear

# Maximum possible distance in the linear [0,1]^3 cube: sqrt(3).
_MAX_LINEAR_DIST = float(np.sqrt(3.0))


def _smoothstep(lo: float, hi: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - lo) / max(hi - lo, 1e-6), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


class ChromaKeying:
    # Bumped to 2 in v0.13.1: distance math moved from gamma sRGB to linear RGB
    # (commit b7a4472). Any cached PNG keyed with version 1 is incorrect for
    # colored-on-colored traditions and must be regenerated on upgrade.
    cache_version: int = 2

    def extract_alpha(self, rgb: np.ndarray, canvas: CanvasSpec) -> np.ndarray:
        # Linearize pixels AND canvas color before computing distance.
        rgb_lin = srgb_to_linear(rgb.astype(np.float32) / 255.0)
        canvas_lin = srgb_to_linear(
            np.array(canvas.color, dtype=np.float32) / 255.0
        )
        diff = rgb_lin - canvas_lin
        dist = np.sqrt(np.sum(diff * diff, axis=-1))  # 0..sqrt(3)
        lo = canvas.tolerance * _MAX_LINEAR_DIST
        hi = _MAX_LINEAR_DIST * 0.5
        alpha = _smoothstep(lo, hi, dist)
        if canvas.invert:
            alpha = 1.0 - alpha
        return alpha.astype(np.float32)


class DeltaEKeying:
    cache_version: int = 1

    def extract_alpha(self, rgb: np.ndarray, canvas: CanvasSpec) -> np.ndarray:
        lab = srgb_to_lab(rgb)
        canvas_arr = np.array(canvas.color, dtype=np.uint8).reshape(1, 1, 3)
        canvas_lab = srgb_to_lab(canvas_arr)[0, 0]
        diff = lab - canvas_lab
        delta_e = np.sqrt(np.sum(diff * diff, axis=-1))
        lo = canvas.tolerance * 100.0
        hi = 50.0
        alpha = _smoothstep(lo, hi, delta_e)
        if canvas.invert:
            alpha = 1.0 - alpha
        return alpha.astype(np.float32)
