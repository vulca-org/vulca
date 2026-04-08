"""B-path mask softening: feather + (optional) guided filter + despill.

No new mandatory dependency. Uses cv2.ximgproc.guidedFilter when [tools]
extra is installed; otherwise falls back to a numpy box-filter feather.
"""
from __future__ import annotations

import numpy as np


def _box_blur(arr: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 0:
        return arr.astype(np.float32)
    k = radius * 2 + 1
    pad = np.pad(arr.astype(np.float32), radius, mode="edge")
    # Integral image with a zero row/col on top/left for inclusive sums.
    s = np.zeros((pad.shape[0] + 1, pad.shape[1] + 1), dtype=np.float32)
    s[1:, 1:] = pad.cumsum(axis=0).cumsum(axis=1)
    H, W = arr.shape
    out = np.zeros_like(arr, dtype=np.float32)
    for y in range(H):
        for x in range(W):
            y0, y1 = y, y + k
            x0, x1 = x, x + k
            total = s[y1, x1] - s[y0, x1] - s[y1, x0] + s[y0, x0]
            out[y, x] = total / (k * k)
    return out


def _try_guided_filter(mask: np.ndarray, rgb: np.ndarray, radius: int) -> np.ndarray | None:
    try:
        import cv2  # noqa: F401
        from cv2 import ximgproc
    except Exception:
        return None
    guide = rgb.astype(np.float32) / 255.0
    src = mask.astype(np.float32)
    return ximgproc.guidedFilter(guide=guide, src=src, radius=radius, eps=1e-3)


def _despill(rgba_alpha: np.ndarray, rgb: np.ndarray, bg_color=(255, 255, 255)) -> np.ndarray:
    """Reduce background color contamination at edges (cheap heuristic)."""
    bg = np.array(bg_color, dtype=np.float32)
    diff = np.linalg.norm(rgb.astype(np.float32) - bg, axis=-1) / 441.0
    return np.clip(rgba_alpha * (0.5 + 0.5 * diff), 0.0, 1.0)


def soften_mask(
    mask: np.ndarray,
    rgb: np.ndarray,
    *,
    feather_px: int = 2,
    guided: bool = True,
    despill: bool = True,
) -> np.ndarray:
    if mask.dtype == np.bool_:
        mask = mask.astype(np.uint8)

    soft: np.ndarray | None = None
    if guided:
        soft = _try_guided_filter(mask, rgb, radius=max(feather_px, 4))
    if soft is None:
        soft = _box_blur(mask, feather_px)

    soft = soft.astype(np.float32)
    soft = np.clip(soft, 0.0, 1.0)

    if despill:
        soft = _despill(soft, rgb)
    return soft.astype(np.float32)
