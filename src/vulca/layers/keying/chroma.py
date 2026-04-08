"""Tier 1 strategies for colored content on colored canvases.

ChromaKeying: Euclidean distance in linear RGB. Fast, OK for high-contrast.
DeltaEKeying: Perceptual ΔE76 in CIE LAB. ~3× slower, used for low-contrast
              cases (e.g. gongbi color washes on cooked silk).
"""
from __future__ import annotations

import numpy as np

from vulca.layers.keying import CanvasSpec
from vulca.layers.keying._lab import srgb_to_lab


def _smoothstep(lo: float, hi: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - lo) / max(hi - lo, 1e-6), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


class ChromaKeying:
    def extract_alpha(self, rgb: np.ndarray, canvas: CanvasSpec) -> np.ndarray:
        diff = rgb.astype(np.float32) - np.array(canvas.color, dtype=np.float32)
        dist = np.sqrt(np.sum(diff * diff, axis=-1))      # 0..~441
        lo = canvas.tolerance * 441.0
        hi = 441.0 * 0.5
        alpha = _smoothstep(lo, hi, dist)
        if canvas.invert:
            alpha = 1.0 - alpha
        return alpha.astype(np.float32)


class DeltaEKeying:
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
