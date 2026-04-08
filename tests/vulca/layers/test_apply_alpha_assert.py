"""v0.13.2 P2: _apply_alpha must assert shape match, not silently resize."""
from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image

from vulca.layers.layered_generate import _apply_alpha


def _png_bytes(w: int, h: int) -> bytes:
    img = Image.new("RGB", (w, h), (128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_apply_alpha_matching_shape_ok():
    rgb = _png_bytes(8, 8)
    alpha = np.ones((8, 8), dtype=np.float32)
    out = _apply_alpha(rgb, alpha)
    assert out.size == (8, 8)
    assert out.mode == "RGBA"


def test_apply_alpha_shape_mismatch_raises():
    rgb = _png_bytes(8, 8)
    alpha = np.ones((4, 4), dtype=np.float32)
    with pytest.raises(AssertionError, match="alpha shape"):
        _apply_alpha(rgb, alpha)
