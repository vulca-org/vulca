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


class TestOpacityBlend:
    """Task 2: opacity field actually affects compositing."""

    def test_full_opacity_unchanged(self):
        from vulca.layers.blend import blend_layers

        with tempfile.TemporaryDirectory() as td:
            bg = Image.new("RGBA", (50, 50), (255, 255, 255, 255))
            fg = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
            bg_path = str(Path(td) / "bg.png"); bg.save(bg_path)
            fg_path = str(Path(td) / "fg.png"); fg.save(fg_path)

            layers = [
                LayerResult(info=_make_layer("bg", 0, opacity=1.0), image_path=bg_path),
                LayerResult(info=_make_layer("fg", 1, opacity=1.0), image_path=fg_path),
            ]
            result = blend_layers(layers, width=50, height=50)
            px = result.getpixel((25, 25))
            assert px[0] == 255 and px[1] == 0 and px[2] == 0, f"Full opacity should be red, got {px}"

    def test_half_opacity_blends(self):
        from vulca.layers.blend import blend_layers

        with tempfile.TemporaryDirectory() as td:
            bg = Image.new("RGBA", (50, 50), (255, 255, 255, 255))
            fg = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
            bg_path = str(Path(td) / "bg.png"); bg.save(bg_path)
            fg_path = str(Path(td) / "fg.png"); fg.save(fg_path)

            layers = [
                LayerResult(info=_make_layer("bg", 0, opacity=1.0), image_path=bg_path),
                LayerResult(info=_make_layer("fg", 1, opacity=0.5), image_path=fg_path),
            ]
            result = blend_layers(layers, width=50, height=50)
            px = result.getpixel((25, 25))
            # 50% red over white = ~(255, 128, 128)
            assert 100 < px[1] < 160, f"Half opacity should blend, got G={px[1]}"

    def test_zero_opacity_invisible(self):
        from vulca.layers.blend import blend_layers

        with tempfile.TemporaryDirectory() as td:
            bg = Image.new("RGBA", (50, 50), (0, 255, 0, 255))
            fg = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
            bg_path = str(Path(td) / "bg.png"); bg.save(bg_path)
            fg_path = str(Path(td) / "fg.png"); fg.save(fg_path)

            layers = [
                LayerResult(info=_make_layer("bg", 0, opacity=1.0), image_path=bg_path),
                LayerResult(info=_make_layer("fg", 1, opacity=0.0), image_path=fg_path),
            ]
            result = blend_layers(layers, width=50, height=50)
            px = result.getpixel((25, 25))
            assert px[1] == 255 and px[0] == 0, f"Zero opacity should show bg green, got {px}"


class TestSpatialTransform:
    """Task 3: Spatial transform engine."""

    def test_compute_content_bbox(self):
        from vulca.layers.transform import compute_content_bbox

        img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        for y in range(30, 70):
            for x in range(20, 80):
                img.putpixel((x, y), (255, 0, 0, 255))

        bbox = compute_content_bbox(img)
        assert bbox is not None
        assert bbox["x"] == 20
        assert bbox["y"] == 30
        assert bbox["w"] == 60
        assert bbox["h"] == 40

    def test_compute_content_bbox_empty_image(self):
        from vulca.layers.transform import compute_content_bbox

        img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        assert compute_content_bbox(img) is None

    def test_apply_transform_identity(self):
        """Default transform (full canvas) should not change the image."""
        from vulca.layers.transform import apply_spatial_transform

        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        info = _make_layer("test", 0)
        result = apply_spatial_transform(img, info, canvas_width=100, canvas_height=100)
        assert result.size == (100, 100)
        assert result.getpixel((50, 50)) == (255, 0, 0, 128)

    def test_apply_transform_half_size_centered(self):
        """50% size layer positioned at 25%, 25% should occupy center."""
        from vulca.layers.transform import apply_spatial_transform

        img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
        info = _make_layer("test", 0, x=25.0, y=25.0, width=50.0, height=50.0)
        result = apply_spatial_transform(img, info, canvas_width=200, canvas_height=200)
        assert result.size == (200, 200)
        px_center = result.getpixel((100, 100))
        assert px_center[0] == 255 and px_center[3] == 255
        px_corner = result.getpixel((10, 10))
        assert px_corner[3] == 0

    def test_needs_transform_false_for_defaults(self):
        from vulca.layers.transform import needs_transform

        info = _make_layer("test", 0)
        assert needs_transform(info) is False

    def test_needs_transform_true_for_moved(self):
        from vulca.layers.transform import needs_transform

        info = _make_layer("test", 0, x=10.0)
        assert needs_transform(info) is True

    def test_blend_layers_applies_transform(self):
        """blend_layers should apply spatial transform when layer has non-default position."""
        from vulca.layers.blend import blend_layers

        with tempfile.TemporaryDirectory() as td:
            bg = Image.new("RGBA", (100, 100), (0, 255, 0, 255))
            fg = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
            bg_path = str(Path(td) / "bg.png"); bg.save(bg_path)
            fg_path = str(Path(td) / "fg.png"); fg.save(fg_path)

            layers = [
                LayerResult(info=_make_layer("bg", 0), image_path=bg_path),
                LayerResult(info=_make_layer("fg", 1, x=0.0, y=0.0, width=50.0, height=50.0),
                           image_path=fg_path),
            ]
            result = blend_layers(layers, width=100, height=100)
            px_tl = result.getpixel((10, 10))
            assert px_tl[0] == 255 and px_tl[1] == 0, f"Top-left should be red, got {px_tl}"
            px_br = result.getpixel((75, 75))
            assert px_br[1] == 255 and px_br[0] == 0, f"Bottom-right should be green, got {px_br}"


class TestBlendModes:
    """Task 4: Additional blend modes."""

    def _blend_pair(self, mode, bot_color=(100, 100, 100, 255), top_color=(200, 200, 200, 255)):
        from vulca.layers.blend import blend_layers
        with tempfile.TemporaryDirectory() as td:
            bg = Image.new("RGBA", (10, 10), bot_color)
            fg = Image.new("RGBA", (10, 10), top_color)
            bg_path = str(Path(td) / "bg.png"); bg.save(bg_path)
            fg_path = str(Path(td) / "fg.png"); fg.save(fg_path)
            layers = [
                LayerResult(info=_make_layer("bg", 0), image_path=bg_path),
                LayerResult(info=_make_layer("fg", 1, blend_mode=mode), image_path=fg_path),
            ]
            result = blend_layers(layers, width=10, height=10)
            return result.getpixel((5, 5))

    def test_overlay_exists(self):
        px = self._blend_pair("overlay")
        assert px[3] == 255

    def test_overlay_math(self):
        px = self._blend_pair("overlay", (100, 100, 100, 255), (200, 200, 200, 255))
        assert 150 < px[0] < 165, f"Overlay expected ~157, got {px[0]}"

    def test_soft_light_exists(self):
        px = self._blend_pair("soft_light")
        assert px[3] == 255

    def test_darken_takes_minimum(self):
        px = self._blend_pair("darken", (100, 200, 150, 255), (200, 50, 100, 255))
        assert px[0] == 100
        assert px[1] == 50
        assert px[2] == 100

    def test_lighten_takes_maximum(self):
        px = self._blend_pair("lighten", (100, 200, 150, 255), (200, 50, 250, 255))
        assert px[0] == 200
        assert px[1] == 200
        assert px[2] == 250

    def test_color_dodge_exists(self):
        px = self._blend_pair("color_dodge")
        assert px[3] == 255

    def test_color_burn_exists(self):
        px = self._blend_pair("color_burn")
        assert px[3] == 255

    def test_unknown_mode_falls_back_to_normal(self):
        px = self._blend_pair("nonexistent_mode", (0, 255, 0, 255), (255, 0, 0, 255))
        assert px[0] == 255 and px[1] == 0


class TestTransformLayerOp:
    """Task 5: transform_layer operation."""

    def _setup_artwork(self, td):
        from vulca.layers.manifest import write_manifest, load_manifest
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
        img.save(str(Path(td) / "test_layer.png"))
        info = _make_layer("test_layer", 0)
        write_manifest([info], output_dir=td, width=100, height=100)
        return load_manifest(td)

    def test_transform_moves(self):
        from vulca.layers.ops import transform_layer
        with tempfile.TemporaryDirectory() as td:
            artwork = self._setup_artwork(td)
            transform_layer(artwork, artwork_dir=td, layer_name="test_layer", dx=10.0, dy=20.0)
            assert artwork.layers[0].info.x == 10.0
            assert artwork.layers[0].info.y == 20.0

    def test_transform_scales(self):
        from vulca.layers.ops import transform_layer
        with tempfile.TemporaryDirectory() as td:
            artwork = self._setup_artwork(td)
            transform_layer(artwork, artwork_dir=td, layer_name="test_layer", scale=0.5)
            assert artwork.layers[0].info.width == 50.0
            assert artwork.layers[0].info.height == 50.0

    def test_transform_rotates(self):
        from vulca.layers.ops import transform_layer
        with tempfile.TemporaryDirectory() as td:
            artwork = self._setup_artwork(td)
            transform_layer(artwork, artwork_dir=td, layer_name="test_layer", rotate=45.0)
            assert artwork.layers[0].info.rotation == 45.0

    def test_transform_set_opacity(self):
        from vulca.layers.ops import transform_layer
        with tempfile.TemporaryDirectory() as td:
            artwork = self._setup_artwork(td)
            transform_layer(artwork, artwork_dir=td, layer_name="test_layer", set_opacity=0.5)
            assert artwork.layers[0].info.opacity == 0.5

    def test_transform_locked_raises(self):
        from vulca.layers.ops import transform_layer
        from vulca.layers.manifest import write_manifest, load_manifest
        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
            img.save(str(Path(td) / "locked.png"))
            info = _make_layer("locked", 0, locked=True)
            write_manifest([info], output_dir=td, width=100, height=100)
            artwork = load_manifest(td)
            with pytest.raises(ValueError, match="locked"):
                transform_layer(artwork, artwork_dir=td, layer_name="locked", dx=10.0)

    def test_transform_not_found_raises(self):
        from vulca.layers.ops import transform_layer
        with tempfile.TemporaryDirectory() as td:
            artwork = self._setup_artwork(td)
            with pytest.raises(ValueError, match="not found"):
                transform_layer(artwork, artwork_dir=td, layer_name="nonexistent", dx=10.0)

    def test_transform_persists_to_manifest(self):
        from vulca.layers.ops import transform_layer
        from vulca.layers.manifest import load_manifest
        with tempfile.TemporaryDirectory() as td:
            artwork = self._setup_artwork(td)
            transform_layer(artwork, artwork_dir=td, layer_name="test_layer", dx=15.0, set_opacity=0.8)
            # Reload from disk to verify persistence
            reloaded = load_manifest(td)
            assert reloaded.layers[0].info.x == 15.0
            assert reloaded.layers[0].info.opacity == 0.8


class TestDuplicateSpatialGuard:
    """Guard: duplicate_layer must copy v0.12 spatial fields."""

    def test_duplicate_preserves_spatial_fields(self):
        from vulca.layers.ops import duplicate_layer
        from vulca.layers.manifest import write_manifest, load_manifest

        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
            img.save(str(Path(td) / "src.png"))
            info = _make_layer("src", 0, x=25.0, y=30.0, width=50.0, height=60.0,
                               rotation=45.0, opacity=0.7)
            write_manifest([info], output_dir=td, width=100, height=100)
            artwork = load_manifest(td)

            result = duplicate_layer(artwork, artwork_dir=td, layer_name="src", new_name="src_copy")

            assert result.info.x == 25.0
            assert result.info.y == 30.0
            assert result.info.width == 50.0
            assert result.info.height == 60.0
            assert result.info.rotation == 45.0
            assert result.info.opacity == 0.7
