import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts"))
from _evfsam_common import imread_rgb  # noqa: E402


def test_imread_rgb_returns_rgb_and_scale(tmp_path):
    p = tmp_path / "small.jpg"
    Image.new("RGB", (100, 100), "red").save(p, "JPEG")
    result = imread_rgb(p)
    assert isinstance(result, tuple) and len(result) == 2
    arr, scale = result
    assert arr.shape[2] == 3
    assert scale == 1.0


def test_imread_rgb_resizes_giant(tmp_path):
    p = tmp_path / "giant.jpg"
    Image.new("RGB", (5000, 4000), "blue").save(p, "JPEG")
    arr, scale = imread_rgb(p, max_dim=1024)
    assert max(arr.shape[:2]) == 1024
