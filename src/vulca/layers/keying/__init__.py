"""Per-tradition alpha extraction from images on canonical canvases."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class CanvasSpec:
    """Canonical empty-canvas description for a tradition."""
    color: tuple[int, int, int]
    tolerance: float = 0.05
    invert: bool = False

    @classmethod
    def from_hex(cls, hex_color: str, *, tolerance: float = 0.05, invert: bool = False) -> "CanvasSpec":
        h = hex_color.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) != 6:
            raise ValueError(f"invalid hex color: {hex_color}")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return cls(color=(r, g, b), tolerance=tolerance, invert=invert)


class KeyingStrategy(Protocol):
    """Returns a float32 alpha map in [0, 1] given an RGB image and canvas."""
    def extract_alpha(self, rgb: np.ndarray, canvas: CanvasSpec) -> np.ndarray: ...
