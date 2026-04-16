"""Edge case and boundary tests — TDD RED phase.

Each test targets a specific boundary condition that could cause
crashes, data loss, or incorrect output in production.
"""
import asyncio
import json
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork


# ===========================================================================
# 1. Manifest edge cases
# ===========================================================================

class TestManifestEdgeCases:
    """Manifest read/write boundary conditions."""

    def test_load_corrupted_json(self):
        """Corrupted manifest.json should raise, not crash."""
        from vulca.layers.manifest import load_manifest
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "manifest.json").write_text("{invalid json!!!")
            with pytest.raises((json.JSONDecodeError, ValueError)):
                load_manifest(td)

    def test_load_empty_layers_array(self):
        """Manifest with empty layers array should return empty artwork."""
        from vulca.layers.manifest import load_manifest
        with tempfile.TemporaryDirectory() as td:
            manifest = {"version": 2, "width": 100, "height": 100, "layers": []}
            (Path(td) / "manifest.json").write_text(json.dumps(manifest))
            artwork = load_manifest(td)
            assert len(artwork.layers) == 0

    def test_load_missing_layer_file(self):
        """Manifest references a layer file that doesn't exist — load should still work."""
        from vulca.layers.manifest import load_manifest
        with tempfile.TemporaryDirectory() as td:
            manifest = {
                "version": 2, "width": 100, "height": 100,
                "layers": [{"id": "x", "name": "ghost", "file": "ghost.png", "z_index": 0}],
            }
            (Path(td) / "manifest.json").write_text(json.dumps(manifest))
            # load_manifest should succeed (it doesn't validate file existence)
            artwork = load_manifest(td)
            assert len(artwork.layers) == 1
            assert not Path(artwork.layers[0].image_path).exists()

    def test_write_read_roundtrip_preserves_all_fields(self):
        """Write manifest → read → all V2 fields preserved exactly."""
        from vulca.layers.manifest import write_manifest, load_manifest
        with tempfile.TemporaryDirectory() as td:
            info = LayerInfo(
                name="test_layer", description="desc", z_index=3,
                content_type="effect", blend_mode="screen",
                dominant_colors=["#ff0000", "#00ff00"],
                regeneration_prompt="Regen this",
                visible=False, locked=True,
            )
            img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
            img.save(str(Path(td) / "test_layer.png"))
            write_manifest([info], output_dir=td, width=50, height=50,
                          source_image="orig.png", split_mode="extract")
            artwork = load_manifest(td)
            loaded = artwork.layers[0].info
            assert loaded.name == "test_layer"
            assert loaded.content_type == "effect"
            assert loaded.blend_mode == "screen"
            assert loaded.dominant_colors == ["#ff0000", "#00ff00"]
            assert loaded.regeneration_prompt == "Regen this"
            assert loaded.visible is False
            assert loaded.locked is True
            assert artwork.source_image == "orig.png"
            assert artwork.split_mode == "extract"

    def test_v1_manifest_missing_optional_fields(self):
        """V1 manifest with minimal fields should migrate gracefully."""
        from vulca.layers.manifest import load_manifest
        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
            img.save(str(Path(td) / "x.png"))
            manifest = {
                "version": 1, "width": 100, "height": 100,
                "layers": [{"name": "x", "file": "x.png"}],
            }
            (Path(td) / "manifest.json").write_text(json.dumps(manifest))
            artwork = load_manifest(td)
            layer = artwork.layers[0].info
            assert layer.z_index == 0
            assert layer.blend_mode == "normal"
            assert layer.content_type == "background"
            assert layer.visible is True


# ===========================================================================
# 2. Layer operations edge cases
# ===========================================================================

class TestOpsEdgeCases:
    """Layer operation boundary conditions."""

    def _setup(self, td, n=2):
        from vulca.layers.manifest import write_manifest
        infos = []
        for i in range(n):
            name = f"layer_{i}"
            img = Image.new("RGBA", (50, 50), (i * 80, 0, 0, 255))
            img.save(str(Path(td) / f"{name}.png"))
            infos.append(LayerInfo(name=name, description=f"layer {i}", z_index=i))
        write_manifest(infos, output_dir=td, width=50, height=50)
        return td

    def test_remove_last_layer(self):
        """Removing the only remaining layer should leave empty manifest."""
        from vulca.layers.manifest import load_manifest
        from vulca.layers.ops import remove_layer
        with tempfile.TemporaryDirectory() as td:
            self._setup(td, 1)
            artwork = load_manifest(td)
            remove_layer(artwork, artwork_dir=td, layer_name="layer_0")
            artwork = load_manifest(td)
            assert len(artwork.layers) == 0

    def test_reorder_to_same_position(self):
        """Reorder to current position should be a no-op."""
        from vulca.layers.manifest import load_manifest
        from vulca.layers.ops import reorder_layer
        with tempfile.TemporaryDirectory() as td:
            self._setup(td, 3)
            artwork = load_manifest(td)
            reorder_layer(artwork, artwork_dir=td, layer_name="layer_1", new_z_index=1)
            artwork = load_manifest(td)
            z_map = {l.info.name: l.info.z_index for l in artwork.layers}
            assert z_map["layer_0"] == 0
            assert z_map["layer_1"] == 1
            assert z_map["layer_2"] == 2

    def test_merge_single_layer(self):
        """Merging a single layer should produce identical copy."""
        from vulca.layers.manifest import load_manifest
        from vulca.layers.ops import merge_layers
        with tempfile.TemporaryDirectory() as td:
            self._setup(td, 2)
            artwork = load_manifest(td)
            merged = merge_layers(artwork, artwork_dir=td,
                                 layer_names=["layer_0"], merged_name="solo")
            assert merged.info.name == "solo"
            img = Image.open(merged.image_path)
            assert img.mode == "RGBA"
            assert img.size == (50, 50)

    def test_add_layer_default_z_index_is_top(self):
        """Add layer with z_index=-1 should place it on top."""
        from vulca.layers.manifest import load_manifest
        from vulca.layers.ops import add_layer
        with tempfile.TemporaryDirectory() as td:
            self._setup(td, 3)
            artwork = load_manifest(td)
            result = add_layer(artwork, artwork_dir=td, name="top",
                              description="on top", z_index=-1)
            assert result.info.z_index == 3  # above existing 0,1,2

    def test_duplicate_preserves_content(self):
        """Duplicated layer must have identical pixel content."""
        from vulca.layers.manifest import load_manifest
        from vulca.layers.ops import duplicate_layer
        import numpy as np
        with tempfile.TemporaryDirectory() as td:
            self._setup(td, 1)
            artwork = load_manifest(td)
            dup = duplicate_layer(artwork, artwork_dir=td,
                                 layer_name="layer_0", new_name="copy")
            orig = np.array(Image.open(str(Path(td) / "layer_0.png")))
            copy = np.array(Image.open(dup.image_path))
            assert np.array_equal(orig, copy), "Pixel content must be identical"


# ===========================================================================
# 3. Blend mode edge cases
# ===========================================================================

class TestBlendEdgeCases:
    """Blend mode boundary conditions."""

    def test_blend_fully_transparent_layer(self):
        """Blending a fully transparent layer should not change the base."""
        from vulca.layers.blend import blend_normal
        base = Image.new("RGBA", (10, 10), (100, 100, 100, 255))
        top = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        result = blend_normal(base, top)
        assert result.getpixel((5, 5)) == (100, 100, 100, 255)

    def test_screen_with_white_caps_at_255(self):
        """Screen blend with white should cap at 255, not overflow."""
        from vulca.layers.blend import blend_screen
        base = Image.new("RGBA", (10, 10), (255, 255, 255, 255))
        top = Image.new("RGBA", (10, 10), (255, 255, 255, 255))
        result = blend_screen(base, top)
        r, g, b, a = result.getpixel((5, 5))
        assert r == 255 and g == 255 and b == 255

    def test_multiply_with_zero_is_black(self):
        """Multiply with black should produce black."""
        from vulca.layers.blend import blend_multiply
        base = Image.new("RGBA", (10, 10), (200, 200, 200, 255))
        top = Image.new("RGBA", (10, 10), (0, 0, 0, 255))
        result = blend_multiply(base, top)
        r, g, b, a = result.getpixel((5, 5))
        assert r == 0 and g == 0 and b == 0

    def test_blend_mismatched_sizes_resizes(self):
        """blend_layers should handle layers of different sizes."""
        from vulca.layers.blend import blend_layers
        with tempfile.TemporaryDirectory() as td:
            # Small layer
            small = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
            small.save(str(Path(td) / "small.png"))
            # Full-size layer
            full = Image.new("RGBA", (100, 100), (0, 0, 255, 255))
            full.save(str(Path(td) / "full.png"))

            layers = [
                LayerResult(info=LayerInfo(name="full", description="", z_index=0),
                           image_path=str(Path(td) / "full.png")),
                LayerResult(info=LayerInfo(name="small", description="", z_index=1),
                           image_path=str(Path(td) / "small.png")),
            ]
            result = blend_layers(layers, width=100, height=100)
            assert result.size == (100, 100)
            # Small layer gets resized to 100x100, should cover whole canvas red
            r, g, b, a = result.getpixel((50, 50))
            assert r > 200  # small layer (red) resized to full canvas


# ===========================================================================
# 4. Mask edge cases
# ===========================================================================

class TestMaskEdgeCases:
    """Color mask boundary conditions."""

    def test_invalid_hex_color_skipped(self):
        """Invalid hex color in dominant_colors should not crash."""
        from vulca.layers.mask import build_color_mask
        img = Image.new("RGB", (10, 10), (128, 128, 128))
        info = LayerInfo(name="x", description="", z_index=0,
                        content_type="subject", dominant_colors=["not_a_color", "#xyz"])
        # Should not raise
        mask = build_color_mask(img, info)
        assert mask.mode == "L"
        assert mask.size == (10, 10)

    def test_single_pixel_image(self):
        """1x1 pixel image should work without crash."""
        from vulca.layers.mask import build_color_mask, apply_mask_to_image
        img = Image.new("RGB", (1, 1), (255, 0, 0))
        info = LayerInfo(name="x", description="", z_index=0,
                        content_type="subject", dominant_colors=["#ff0000"])
        mask = build_color_mask(img, info)
        assert mask.size == (1, 1)
        result = apply_mask_to_image(img, mask)
        assert result.mode == "RGBA"
        assert result.size == (1, 1)

    def test_rgba_input_image(self):
        """RGBA input (not RGB) should be handled correctly."""
        from vulca.layers.mask import build_color_mask
        img = Image.new("RGBA", (10, 10), (255, 0, 0, 128))
        info = LayerInfo(name="x", description="", z_index=0,
                        content_type="subject", dominant_colors=["#ff0000"])
        mask = build_color_mask(img, info)
        assert mask.mode == "L"


# ===========================================================================
# 5. Split edge cases
# ===========================================================================

class TestSplitEdgeCases:
    """Split boundary conditions."""

    def test_extract_with_no_layers(self):
        """split_extract with empty layer list should produce empty result + manifest."""
        from vulca.layers.split import split_extract
        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGB", (50, 50), (128, 128, 128))
            img.save(str(Path(td) / "src.png"))
            results = split_extract(str(Path(td) / "src.png"), [], output_dir=td)
            assert results == []
            assert (Path(td) / "manifest.json").exists()

    def test_extract_non_square_image(self):
        """Non-square image produces correct non-square layers."""
        from vulca.layers.split import split_extract
        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGB", (200, 100), (255, 0, 0))
            img.save(str(Path(td) / "wide.png"))
            layers = [LayerInfo(name="bg", description="", z_index=0,
                               content_type="background", dominant_colors=["#ff0000"])]
            results = split_extract(str(Path(td) / "wide.png"), layers, output_dir=td)
            layer_img = Image.open(results[0].image_path)
            assert layer_img.size == (200, 100)  # preserves aspect ratio


# ===========================================================================
# 6. Composite edge cases
# ===========================================================================

class TestCompositeEdgeCases:
    """Composite boundary conditions."""

    def test_composite_empty_layers(self):
        """Composite with no layers should produce transparent canvas."""
        from vulca.layers.composite import composite_layers
        with tempfile.TemporaryDirectory() as td:
            out = str(Path(td) / "empty.png")
            composite_layers([], width=50, height=50, output_path=out)
            img = Image.open(out)
            assert img.size == (50, 50)
            assert img.getpixel((25, 25))[3] == 0  # transparent

    def test_composite_single_layer(self):
        """Single layer composite should equal the layer itself."""
        from vulca.layers.composite import composite_layers
        with tempfile.TemporaryDirectory() as td:
            layer = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
            layer.save(str(Path(td) / "only.png"))
            layers = [LayerResult(
                info=LayerInfo(name="only", description="", z_index=0),
                image_path=str(Path(td) / "only.png"),
            )]
            out = str(Path(td) / "comp.png")
            composite_layers(layers, width=50, height=50, output_path=out)
            comp = Image.open(out)
            assert comp.getpixel((25, 25))[:3] == (255, 0, 0)


# ===========================================================================
# 7. Redraw edge cases
# ===========================================================================

class TestRedrawEdgeCases:
    """Redraw boundary conditions."""

    def test_redraw_nonexistent_layer(self):
        """Redraw with invalid layer name should raise ValueError."""
        from vulca.layers.manifest import write_manifest, load_manifest
        from vulca.layers.redraw import redraw_layer
        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
            img.save(str(Path(td) / "bg.png"))
            write_manifest(
                [LayerInfo(name="bg", description="", z_index=0)],
                output_dir=td, width=50, height=50,
            )
            artwork = load_manifest(td)
            loop = asyncio.new_event_loop()
            with pytest.raises(ValueError, match="not found"):
                loop.run_until_complete(
                    redraw_layer(artwork, layer_name="nonexistent",
                                instruction="change", provider="mock", artwork_dir=td)
                )
            loop.close()

    def test_merge_redraw_empty_list(self):
        """Merge redraw with empty layer list should raise."""
        from vulca.layers.manifest import write_manifest, load_manifest
        from vulca.layers.redraw import redraw_merged
        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
            img.save(str(Path(td) / "bg.png"))
            write_manifest(
                [LayerInfo(name="bg", description="", z_index=0)],
                output_dir=td, width=50, height=50,
            )
            artwork = load_manifest(td)
            loop = asyncio.new_event_loop()
            with pytest.raises((ValueError, KeyError)):
                loop.run_until_complete(
                    redraw_merged(artwork, layer_names=[],
                                 instruction="test", provider="mock", artwork_dir=td)
                )
            loop.close()


# ===========================================================================
# 8. Gemini provider edge cases
# ===========================================================================

class TestGeminiEdgeCases:
    """Gemini provider mapping edge cases."""

    def test_zero_dimensions(self):
        """0x0 dimensions should map to smallest tier."""
        from vulca.providers.gemini import _pixels_to_image_size
        assert _pixels_to_image_size(0) == "512"

    def test_negative_dimensions(self):
        """Negative dimensions should still return a valid tier."""
        from vulca.providers.gemini import _pixels_to_image_size
        result = _pixels_to_image_size(-100)
        assert result == "512"

    def test_aspect_ratio_very_wide(self):
        """Extremely wide aspect ratio (e.g. 10:1) maps to closest."""
        from vulca.providers.gemini import _dims_to_aspect_ratio
        result = _dims_to_aspect_ratio(10000, 1000)
        assert result in ("8:1", "21:9")  # closest supported

    def test_aspect_ratio_very_tall(self):
        """Extremely tall ratio maps to closest."""
        from vulca.providers.gemini import _dims_to_aspect_ratio
        result = _dims_to_aspect_ratio(100, 1000)
        assert result in ("1:8", "1:4", "9:16")


# ===========================================================================
# 9. Export edge cases
# ===========================================================================

class TestExportEdgeCases:
    """Export boundary conditions."""

    def test_export_to_directory_path(self):
        """export_psd with directory path (not .psd) should work."""
        from vulca.layers.export import export_psd
        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
            img.save(str(Path(td) / "bg.png"))
            layers = [LayerResult(
                info=LayerInfo(name="bg", description="", z_index=0),
                image_path=str(Path(td) / "bg.png"),
            )]
            out_dir = str(Path(td) / "export_dir")
            export_psd(layers, width=50, height=50, output_path=out_dir)
            assert (Path(out_dir) / "00_bg.png").exists()
            assert (Path(out_dir) / "manifest.json").exists()

    def test_export_empty_layers(self):
        """Export with empty layer list should create directory with just manifest."""
        from vulca.layers.export import export_psd
        with tempfile.TemporaryDirectory() as td:
            out_dir = str(Path(td) / "empty_export")
            export_psd([], width=50, height=50, output_path=out_dir)
            assert (Path(out_dir) / "manifest.json").exists()


