"""Hand-rolled sRGB → CIE LAB. No scikit-image dependency.

Reference: https://en.wikipedia.org/wiki/SRGB and CIE LAB D65 white point.
"""
from __future__ import annotations

import numpy as np

# D65 reference white point
_XN, _YN, _ZN = 0.95047, 1.0, 1.08883


def srgb_to_linear(c: np.ndarray) -> np.ndarray:
    """sRGB → linear RGB. Accepts float in [0,1]. Public helper so other
    keying strategies can linearize before computing distances."""
    out = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return out


# Backwards-compatible private alias.
_srgb_to_linear = srgb_to_linear


def _xyz_to_lab_f(t: np.ndarray) -> np.ndarray:
    delta = 6.0 / 29.0
    return np.where(
        t > delta ** 3,
        np.cbrt(t),
        t / (3 * delta ** 2) + 4.0 / 29.0,
    )


def srgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """Convert H×W×3 uint8 sRGB to H×W×3 float32 CIE LAB (D65).

    L in [0, 100], a/b roughly in [-128, 127].
    """
    if rgb.dtype != np.uint8:
        raise ValueError(f"expected uint8, got {rgb.dtype}")
    if rgb.ndim != 3 or rgb.shape[-1] != 3:
        raise ValueError(f"expected H×W×3, got {rgb.shape}")

    c = rgb.astype(np.float32) / 255.0
    lin = _srgb_to_linear(c)
    R, G, B = lin[..., 0], lin[..., 1], lin[..., 2]

    X = 0.4124564 * R + 0.3575761 * G + 0.1804375 * B
    Y = 0.2126729 * R + 0.7151522 * G + 0.0721750 * B
    Z = 0.0193339 * R + 0.1191920 * G + 0.9503041 * B

    fx = _xyz_to_lab_f(X / _XN)
    fy = _xyz_to_lab_f(Y / _YN)
    fz = _xyz_to_lab_f(Z / _ZN)

    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)

    return np.stack([L, a, b], axis=-1).astype(np.float32)
