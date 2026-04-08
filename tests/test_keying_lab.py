import numpy as np
import pytest
from vulca.layers.keying._lab import srgb_to_lab

def test_pure_white_maps_to_L100():
    rgb = np.array([[[255, 255, 255]]], dtype=np.uint8)
    lab = srgb_to_lab(rgb)
    L, a, b = lab[0, 0]
    assert abs(L - 100.0) < 0.5
    assert abs(a) < 0.5
    assert abs(b) < 0.5

def test_pure_black_maps_to_L0():
    rgb = np.array([[[0, 0, 0]]], dtype=np.uint8)
    lab = srgb_to_lab(rgb)
    assert abs(lab[0, 0, 0]) < 0.5

def test_mid_gray_L_around_53():
    rgb = np.array([[[128, 128, 128]]], dtype=np.uint8)
    L = srgb_to_lab(rgb)[0, 0, 0]
    assert 52.0 < L < 55.0

def test_pure_red_chroma():
    rgb = np.array([[[255, 0, 0]]], dtype=np.uint8)
    L, a, b = srgb_to_lab(rgb)[0, 0]
    assert L > 50 and L < 60
    assert a > 50           # red has positive a
    assert b > 30           # and positive b

def test_shape_preserved():
    rgb = np.zeros((4, 5, 3), dtype=np.uint8)
    out = srgb_to_lab(rgb)
    assert out.shape == (4, 5, 3)
    assert out.dtype == np.float32

def test_pure_red_reference_values():
    # Reference values from colour-science / skimage srgb2lab([255,0,0])
    lab = srgb_to_lab(np.array([[[255, 0, 0]]], dtype=np.uint8))[0, 0]
    assert np.allclose(lab, [53.24, 80.09, 67.20], atol=0.5)

def test_wrong_dtype_raises():
    rgb = np.zeros((2, 2, 3), dtype=np.float32)
    with pytest.raises(ValueError, match="uint8"):
        srgb_to_lab(rgb)

def test_wrong_shape_raises():
    rgb = np.zeros((2, 2, 4), dtype=np.uint8)
    with pytest.raises(ValueError, match="H×W×3|3"):
        srgb_to_lab(rgb)
