import numpy as np
from vulca.layers.keying import CanvasSpec
from vulca.layers.keying.luminance import LuminanceKeying

def _make_image(rgb_tuple, h=4, w=4):
    img = np.full((h, w, 3), rgb_tuple, dtype=np.uint8)
    return img

def test_pure_white_canvas_pure_white_image_alpha_zero():
    canvas = CanvasSpec.from_hex("#ffffff")
    img = _make_image((255, 255, 255))
    alpha = LuminanceKeying().extract_alpha(img, canvas)
    assert alpha.shape == (4, 4)
    assert alpha.dtype == np.float32
    assert (alpha < 0.01).all()

def test_dense_ink_on_white_alpha_high():
    canvas = CanvasSpec.from_hex("#ffffff")
    img = _make_image((30, 30, 30))
    alpha = LuminanceKeying().extract_alpha(img, canvas)
    assert 0.85 < alpha.mean() < 0.92

def test_pale_ink_alpha_soft():
    canvas = CanvasSpec.from_hex("#ffffff")
    img = _make_image((180, 180, 180))
    alpha = LuminanceKeying().extract_alpha(img, canvas)
    assert 0.25 < alpha.mean() < 0.33

def test_flying_white_alpha_very_low():
    canvas = CanvasSpec.from_hex("#ffffff")
    img = _make_image((240, 240, 240))
    alpha = LuminanceKeying().extract_alpha(img, canvas)
    assert 0.04 < alpha.mean() < 0.08

def test_alpha_clipped_to_unit_interval():
    canvas = CanvasSpec.from_hex("#ffffff")
    img = np.array([[[10, 10, 10], [255, 255, 255]]], dtype=np.uint8)
    alpha = LuminanceKeying().extract_alpha(img, canvas)
    assert (alpha >= 0).all() and (alpha <= 1).all()

def test_invert_for_dark_canvas():
    canvas = CanvasSpec(color=(0, 0, 0), invert=True)
    img = _make_image((255, 255, 255))
    alpha = LuminanceKeying().extract_alpha(img, canvas)
    assert (alpha > 0.95).all()
