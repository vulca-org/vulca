"""Tier 0 default: alpha = 1 - (L / L_canvas).

Optimal for traditions where dark content sits on a light canvas
(ink wash, calligraphy, line art, sketch). Ink darkness physically
equals alpha, so flying-white and ink gradients become soft alpha
for free — no halos, no hard edges.
"""
from __future__ import annotations

import numpy as np

from vulca.layers.keying import CanvasSpec


def _luma(rgb: np.ndarray) -> np.ndarray:
    """Rec. 601 luma in [0, 255]."""
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


class LuminanceKeying:
    cache_version: int = 1

    def extract_alpha(self, rgb: np.ndarray, canvas: CanvasSpec) -> np.ndarray:
        if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[-1] != 3:
            raise ValueError(f"expected H×W×3 uint8, got {rgb.shape} {rgb.dtype}")

        L = _luma(rgb.astype(np.float32))
        L_canvas = float(_luma(np.array(canvas.color, dtype=np.float32)[None, None, :])[0, 0])

        if canvas.invert:
            L = 255.0 - L
            L_canvas = 255.0 - L_canvas

        if L_canvas <= 1.0:
            # Black-canvas case: brightness directly maps to alpha
            alpha = L / 255.0
        else:
            # Light-canvas case: darkness (relative to canvas) maps to alpha
            alpha = 1.0 - (L / L_canvas)

        return np.clip(alpha, 0.0, 1.0).astype(np.float32)
