"""B-path mask softening: feather + (optional) guided filter + despill.

No new mandatory dependency. Uses cv2.ximgproc.guidedFilter when [tools]
extra is installed; otherwise falls back to a numpy box-filter feather.
"""
from __future__ import annotations

import numpy as np


def _box_blur(arr: np.ndarray, radius: int) -> np.ndarray:
    """Vectorized box blur via separable cumulative-sum slicing.

    O(HW) numpy ops, no Python per-pixel loop. For a box of size k = 2r+1
    the sum over any window is just the difference between two integral
    values at shifted offsets — numpy slicing handles the whole frame at
    once.
    """
    if radius <= 0:
        return arr.astype(np.float32)
    r = int(radius)
    k = r * 2 + 1
    pad = np.pad(arr.astype(np.float32), r, mode="edge")
    # Integral image with a zero row/col on top/left so every window sum
    # is s[y+k, x+k] - s[y, x+k] - s[y+k, x] + s[y, x].
    s = np.zeros((pad.shape[0] + 1, pad.shape[1] + 1), dtype=np.float32)
    s[1:, 1:] = pad.cumsum(axis=0).cumsum(axis=1)
    H, W = arr.shape
    total = (
        s[k:k + H, k:k + W]
        - s[0:H,   k:k + W]
        - s[k:k + H, 0:W]
        + s[0:H,   0:W]
    )
    return total / (k * k)


def _try_guided_filter(mask: np.ndarray, rgb: np.ndarray, radius: int) -> np.ndarray | None:
    try:
        import cv2  # noqa: F401
        from cv2 import ximgproc
    except Exception:
        return None
    guide = rgb.astype(np.float32) / 255.0
    src = mask.astype(np.float32)
    return ximgproc.guidedFilter(guide=guide, src=src, radius=radius, eps=1e-3)


def _despill(
    alpha: np.ndarray,
    rgb: np.ndarray,
    bg_color=(255, 255, 255),
    *,
    edge_band: tuple[float, float] = (0.02, 0.98),
    strength: float = 0.5,
) -> np.ndarray:
    """Attenuate alpha on background-colored edge pixels.

    Previous v0.13 implementation multiplied EVERY pixel's alpha by a
    factor derived from its distance to bg, which eroded legitimate
    light edges on solid interior. The new version is gated:

    1. Only pixels in the soft-edge band (edge_band[0] < alpha < edge_band[1])
       are touched — solid interior and fully-transparent background pass
       through unchanged.
    2. Within the edge band, pixels close to the background color lose
       alpha proportional to their similarity to bg. Pure subject-colored
       edge pixels keep their alpha.

    This is still a heuristic (true despill would operate on RGB spill
    components), but it no longer dims legitimate highlights.
    """
    bg = np.array(bg_color, dtype=np.float32)
    max_dist = float(np.sqrt(3.0) * 255.0)  # sRGB cube diagonal
    dist = np.linalg.norm(rgb.astype(np.float32) - bg, axis=-1)
    similarity = np.clip(1.0 - dist / max_dist, 0.0, 1.0)  # 1 = identical to bg

    in_band = (alpha > edge_band[0]) & (alpha < edge_band[1])
    penalty = similarity * float(strength)  # up to `strength` alpha loss
    out = np.where(in_band, alpha * (1.0 - penalty), alpha)
    return np.clip(out, 0.0, 1.0).astype(np.float32)


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
