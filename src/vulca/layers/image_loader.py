"""Safe image loading with pre-resize for giant source images.

Used by EVF-SAM scripts and any pipeline that handles arbitrary-resolution
inputs. Las Meninas at 26065x30000 decoded to float32 is ~9 GB.

IMPORTANT LIMITATION: cv2.imread fully decodes the BGR buffer to uint8
(~2.3 GB for 26k×30k) BEFORE this helper can resize. That's large but
usually survivable on a 16+ GB machine; the ~9 GB blow-up only occurs
when a downstream caller converts to float32. This helper prevents THAT
second blow-up by capping dimensions before any downstream float
conversion. It does NOT prevent OOM during raw cv2 decode — if that
becomes a real problem, switch to PIL.Image.open + thumbnail (which
can decode-and-resize lazily) in a follow-up.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def imread_safe(
    path: str | Path,
    *,
    max_dim: int = 4096,
) -> tuple[np.ndarray, float]:
    """Read an image and resize if longest side exceeds max_dim.

    Returns (rgb_ndarray, scale) where scale is the factor applied
    (1.0 if no resize).

    Raises FileNotFoundError if the file is missing, ValueError if the
    file exists but cv2 cannot decode it (unsupported format / corrupt).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {p}")

    bgr = cv2.imread(str(p))
    if bgr is None:
        raise ValueError(f"cv2 could not decode image (unsupported or corrupt): {p}")

    h, w = bgr.shape[:2]
    longest = max(h, w)
    scale = 1.0
    if longest > max_dim:
        scale = max_dim / longest
        new_w, new_h = int(w * scale), int(h * scale)
        bgr = cv2.resize(bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)

    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return rgb, scale


def resize_to_max(arr: np.ndarray, *, max_dim: int) -> np.ndarray:
    """Resize a HxWxC ndarray so its longest side <= max_dim.

    Returns the same array if already small enough (no copy).
    """
    h, w = arr.shape[:2]
    longest = max(h, w)
    if longest <= max_dim:
        return arr
    scale = max_dim / longest
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(arr, (new_w, new_h), interpolation=cv2.INTER_AREA)
