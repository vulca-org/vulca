"""Tests for v0.12.0 — Layer Primitives."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork


def _make_layer(name: str, z: int, **kwargs) -> LayerInfo:
    defaults = dict(
        name=name, id=f"layer_{name}", description=f"Test {name}",
        z_index=z, blend_mode="normal", content_type="subject",
        dominant_colors=[], regeneration_prompt="",
    )
    defaults.update(kwargs)
    return LayerInfo(**defaults)


def _make_red_image(w: int = 100, h: int = 100) -> Image.Image:
    return Image.new("RGBA", (w, h), (255, 0, 0, 200))


class TestSpatialFields:
    """Task 1: LayerInfo has spatial coordinates."""

    def test_default_values_are_full_canvas(self):
        info = _make_layer("test", 0)
        assert info.x == 0.0
        assert info.y == 0.0
        assert info.width == 100.0
        assert info.height == 100.0
        assert info.rotation == 0.0
        assert info.content_bbox is None

    def test_custom_spatial_values(self):
        info = _make_layer("test", 0, x=10.0, y=20.0, width=50.0, height=30.0, rotation=45.0)
        assert info.x == 10.0
        assert info.y == 20.0
        assert info.width == 50.0
        assert info.height == 30.0
        assert info.rotation == 45.0

    def test_manifest_round_trip_preserves_spatial(self):
        from vulca.layers.manifest import write_manifest, load_manifest

        info = _make_layer("spatial_test", 0, x=15.5, y=25.0, width=60.0, height=40.0, rotation=10.0, opacity=0.7)
        with tempfile.TemporaryDirectory() as td:
            Image.new("RGBA", (200, 200), (0, 0, 0, 0)).save(str(Path(td) / "spatial_test.png"))
            write_manifest([info], output_dir=td, width=200, height=200)
            artwork = load_manifest(td)
            loaded = artwork.layers[0].info
            assert loaded.x == 15.5
            assert loaded.y == 25.0
            assert loaded.width == 60.0
            assert loaded.height == 40.0
            assert loaded.rotation == 10.0
            assert loaded.opacity == 0.7

    def test_old_manifest_without_spatial_loads_with_defaults(self):
        """V2 manifests without spatial fields should load with full-canvas defaults."""
        from vulca.layers.manifest import load_manifest

        with tempfile.TemporaryDirectory() as td:
            Image.new("RGBA", (100, 100), (0, 0, 0, 0)).save(str(Path(td) / "old_layer.png"))
            manifest = {
                "version": 2, "width": 100, "height": 100,
                "layers": [{"id": "l1", "name": "old_layer", "description": "", "z_index": 0,
                            "blend_mode": "normal", "content_type": "subject", "visible": True,
                            "locked": False, "file": "old_layer.png", "dominant_colors": [],
                            "regeneration_prompt": ""}],
            }
            (Path(td) / "manifest.json").write_text(json.dumps(manifest))
            artwork = load_manifest(td)
            loaded = artwork.layers[0].info
            assert loaded.x == 0.0
            assert loaded.width == 100.0
            assert loaded.opacity == 1.0
