import numpy as np
from PIL import Image

from vulca.layers.vlm_mask import apply_vlm_mask


def _binary_disc_mask(h=64, w=64, r=20):
    yy, xx = np.ogrid[:h, :w]
    cy, cx = h // 2, w // 2
    arr = ((yy - cy) ** 2 + (xx - cx) ** 2 <= r * r).astype(np.uint8) * 255
    return Image.fromarray(arr, mode="L")


def _content(h=64, w=64, r=20):
    img = np.full((h, w, 3), 255, dtype=np.uint8)
    yy, xx = np.ogrid[:h, :w]
    cy, cx = h // 2, w // 2
    inside = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
    img[inside] = (40, 40, 40)
    return Image.fromarray(img, mode="RGB")


def test_apply_vlm_mask_softens_edges():
    """The B-path VLM mask path should produce soft alpha at edges, not pure 0/255."""
    mask = _binary_disc_mask()
    content = _content()
    rgba = apply_vlm_mask(content, mask)
    a = np.array(rgba)[:, :, 3]
    intermediates = ((a > 10) & (a < 245)).sum()
    assert intermediates >= 16, f"expected soft edge pixels, got {intermediates}"
