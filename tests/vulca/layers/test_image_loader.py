# tests/vulca/layers/test_image_loader.py
import numpy as np
from pathlib import Path
from PIL import Image
from vulca.layers.image_loader import imread_safe, resize_to_max


def test_imread_safe_returns_rgb_ndarray(tmp_path):
    p = tmp_path / "small.jpg"
    Image.new("RGB", (100, 200), "red").save(p, "JPEG")
    arr, scale = imread_safe(p, max_dim=1024)
    assert arr.shape == (200, 100, 3)
    assert arr.dtype == np.uint8
    assert scale == 1.0


def test_imread_safe_resizes_giant_images(tmp_path):
    p = tmp_path / "giant.jpg"
    Image.new("RGB", (5000, 3000), "blue").save(p, "JPEG")
    arr, scale = imread_safe(p, max_dim=1024)
    assert max(arr.shape[:2]) == 1024
    assert scale == 1024 / 5000


def test_imread_safe_raises_on_missing_file(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        imread_safe(tmp_path / "nonexistent.jpg")


def test_resize_to_max_keeps_aspect_ratio():
    arr = np.zeros((3000, 5000, 3), dtype=np.uint8)
    resized = resize_to_max(arr, max_dim=1000)
    assert resized.shape == (600, 1000, 3)


def test_resize_to_max_noop_when_smaller():
    arr = np.zeros((100, 100, 3), dtype=np.uint8)
    resized = resize_to_max(arr, max_dim=1000)
    assert resized.shape == (100, 100, 3)
    assert resized is arr
