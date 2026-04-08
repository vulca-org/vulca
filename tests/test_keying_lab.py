import numpy as np
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
