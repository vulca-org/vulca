import numpy as np

from vulca.layers.matting import soften_mask


def _binary_disc(h=64, w=64, r=20):
    yy, xx = np.ogrid[:h, :w]
    cy, cx = h // 2, w // 2
    return ((yy - cy) ** 2 + (xx - cx) ** 2 <= r * r).astype(np.uint8)


def _rgb_for_disc(h=64, w=64, r=20):
    img = np.full((h, w, 3), 255, dtype=np.uint8)
    yy, xx = np.ogrid[:h, :w]
    cy, cx = h // 2, w // 2
    inside = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
    img[inside] = (40, 40, 40)
    return img


def test_soften_returns_float_in_unit_range():
    mask = _binary_disc()
    rgb = _rgb_for_disc()
    out = soften_mask(mask, rgb)
    assert out.dtype == np.float32
    assert out.shape == mask.shape
    assert (out >= 0).all() and (out <= 1).all()


def test_soften_blurs_hard_edges():
    mask = _binary_disc()
    rgb = _rgb_for_disc()
    out = soften_mask(mask, rgb, feather_px=3, guided=False)
    intermediates = ((out > 0.05) & (out < 0.95)).sum()
    assert intermediates > 0


def test_despill_preserves_solid_interior():
    """v0.13.1 NTH #3: _despill must NOT erode alpha on solid interior pixels.

    Old heuristic multiplied every pixel by (0.5 + 0.5 * distance_to_bg),
    so even subject-colored (e.g. dark ink) fully-opaque pixels took a
    hit. New version only touches the soft-edge band.
    """
    from vulca.layers.matting import _despill

    # Solid interior: alpha=1 everywhere, rgb is subject color (far from white).
    alpha = np.ones((16, 16), dtype=np.float32)
    rgb = np.full((16, 16, 3), (40, 40, 40), dtype=np.uint8)
    out = _despill(alpha, rgb)
    assert (out >= 0.999).all(), f"solid interior must stay opaque, got min {out.min()}"

    # Fully transparent background pixels also untouched.
    alpha2 = np.zeros((16, 16), dtype=np.float32)
    rgb2 = np.full((16, 16, 3), (255, 255, 255), dtype=np.uint8)
    out2 = _despill(alpha2, rgb2)
    assert (out2 <= 0.001).all()

    # Soft-edge bg-colored pixels DO get attenuated.
    alpha3 = np.full((16, 16), 0.5, dtype=np.float32)
    rgb3 = np.full((16, 16, 3), (250, 250, 250), dtype=np.uint8)  # near white
    out3 = _despill(alpha3, rgb3)
    assert out3.mean() < 0.4, f"bg-colored edge pixels should lose alpha, got {out3.mean()}"


def test_box_blur_matches_reference_and_is_fast():
    """v0.13.1 NTH #2: _box_blur must still match the naive reference output
    (within float tolerance) AND run in well under a second on 512x512.
    """
    import time

    from vulca.layers.matting import _box_blur

    rng = np.random.default_rng(0)
    arr = rng.random((512, 512)).astype(np.float32)

    t0 = time.monotonic()
    out = _box_blur(arr, radius=3)
    elapsed = time.monotonic() - t0
    assert elapsed < 0.5, f"_box_blur took {elapsed:.3f}s on 512x512, expected < 0.5s"
    assert out.shape == arr.shape
    assert out.dtype == np.float32

    # Compare against a simple reference on a tiny patch.
    small = rng.random((9, 9)).astype(np.float32)
    got = _box_blur(small, radius=1)
    expected = np.zeros_like(small)
    pad = np.pad(small, 1, mode="edge")
    for y in range(9):
        for x in range(9):
            expected[y, x] = pad[y:y + 3, x:x + 3].mean()
    assert np.allclose(got, expected, atol=1e-5)


def test_soften_disabled_returns_close_to_input():
    mask = _binary_disc()
    rgb = _rgb_for_disc()
    out = soften_mask(mask, rgb, feather_px=0, guided=False, despill=False)
    diff = np.abs(out - mask.astype(np.float32)).mean()
    assert diff < 0.05
