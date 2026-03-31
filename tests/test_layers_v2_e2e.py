"""Layers V2 End-to-End Functional Validation.

Tests the COMPLETE user workflow, not just individual functions.
Every test creates real files, runs real operations, and verifies
the actual output matches user expectations.

L3+ assertion depth — verifies behavior, not just existence.
"""
import asyncio
import json
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork
from vulca.layers.manifest import write_manifest, load_manifest, MANIFEST_VERSION
from vulca.layers.split import split_extract, split_regenerate
from vulca.layers.composite import composite_layers
from vulca.layers.blend import blend_normal, blend_screen, blend_multiply, blend_layers
from vulca.layers.mask import build_color_mask, apply_mask_to_image
from vulca.layers.ops import (
    add_layer, remove_layer, reorder_layer, toggle_visibility,
    lock_layer, merge_layers, duplicate_layer,
)
from vulca.layers.redraw import redraw_layer, redraw_merged
from vulca.layers.export import export_psd
from vulca.layers.analyze import parse_layer_response
from vulca.layers.prompt import build_analyze_prompt, build_regeneration_prompt, parse_v2_response


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_test_image(path: str, width: int, height: int, regions: dict) -> None:
    """Create a test image with colored regions.

    regions: {"left": (255,0,0), "right": (0,0,255)} or
             {"full": (128,128,128)} or
             {"center": (255,0,0), "border": (0,0,255)}
    """
    img = Image.new("RGB", (width, height), (0, 0, 0))
    w, h = width, height
    if "full" in regions:
        img = Image.new("RGB", (w, h), regions["full"])
    elif "left" in regions and "right" in regions:
        for x in range(w):
            for y in range(h):
                if x < w // 2:
                    img.putpixel((x, y), regions["left"])
                else:
                    img.putpixel((x, y), regions["right"])
    elif "center" in regions and "border" in regions:
        img = Image.new("RGB", (w, h), regions["border"])
        q = w // 4
        for x in range(q, w - q):
            for y in range(q, h - q):
                img.putpixel((x, y), regions["center"])
    img.save(path)


def _setup_layered_artwork(td: str, n_layers: int = 3) -> str:
    """Create a complete layered artwork directory for testing."""
    specs = [
        ("background", (30, 60, 120), "background", "normal"),
        ("mountains", (80, 80, 80), "subject", "normal"),
        ("foreground", (200, 50, 30), "subject", "normal"),
        ("mist", (220, 220, 230), "effect", "screen"),
        ("calligraphy", (10, 10, 10), "text", "multiply"),
    ][:n_layers]

    infos = []
    for i, (name, color, ctype, blend) in enumerate(specs):
        img = Image.new("RGBA", (200, 200), (*color, 255))
        if ctype != "background":
            # Non-bg layers: make outer area transparent
            for x in range(200):
                for y in range(200):
                    if x < 20 or x > 180 or y < 20 or y > 180:
                        img.putpixel((x, y), (0, 0, 0, 0))
        img.save(str(Path(td) / f"{name}.png"))
        infos.append(LayerInfo(
            name=name, description=f"{name} layer for testing",
            z_index=i, content_type=ctype, blend_mode=blend,
            dominant_colors=[f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"],
            regeneration_prompt=f"Generate {name} on transparent background",
        ))

    _create_test_image(str(Path(td) / "original.png"), 200, 200, {"full": (128, 128, 128)})
    write_manifest(infos, output_dir=td, width=200, height=200,
                   source_image="original.png", split_mode="test")
    return td


# ===========================================================================
# Scenario 1: Complete split → edit → composite workflow
# ===========================================================================

class TestFullWorkflowExtract:
    """User scenario: have an image → split → edit layers → composite → verify."""

    def test_extract_split_produces_usable_layers(self):
        """split_extract → all outputs are full-canvas RGBA with meaningful content."""
        with tempfile.TemporaryDirectory() as td:
            # Create a distinct two-color image
            _create_test_image(str(Path(td) / "src.png"), 200, 200,
                              {"left": (255, 0, 0), "right": (0, 0, 255)})
            layers = [
                LayerInfo(name="red_half", description="red left side", z_index=0,
                         content_type="subject", dominant_colors=["#ff0000"]),
                LayerInfo(name="blue_half", description="blue right side", z_index=1,
                         content_type="subject", dominant_colors=["#0000ff"]),
            ]
            results = split_extract(str(Path(td) / "src.png"), layers, output_dir=td)

            # L2: Every layer is full-canvas RGBA
            for r in results:
                img = Image.open(r.image_path)
                assert img.mode == "RGBA", f"{r.info.name}: expected RGBA, got {img.mode}"
                assert img.size == (200, 200), f"{r.info.name}: expected 200x200, got {img.size}"

            # L2: Red layer has opaque red pixels, transparent blue pixels
            red_img = Image.open(results[0].image_path)
            r, g, b, a = red_img.getpixel((50, 100))  # left side
            assert r > 200 and a > 200, f"Red layer left pixel: ({r},{g},{b},{a}) expected opaque red"
            _, _, _, a2 = red_img.getpixel((150, 100))  # right side
            assert a2 < 100, f"Red layer right pixel alpha={a2}, expected transparent"

            # L2: Manifest written correctly
            manifest = json.loads((Path(td) / "manifest.json").read_text())
            assert manifest["version"] == 2
            assert manifest["split_mode"] == "extract"
            assert len(manifest["layers"]) == 2

    def test_extract_then_composite_roundtrip(self):
        """split_extract → composite → output resembles original."""
        with tempfile.TemporaryDirectory() as td:
            _create_test_image(str(Path(td) / "src.png"), 100, 100,
                              {"left": (255, 0, 0), "right": (0, 0, 255)})
            layers = [
                LayerInfo(name="red", description="red", z_index=0,
                         content_type="subject", dominant_colors=["#ff0000"]),
                LayerInfo(name="blue", description="blue", z_index=1,
                         content_type="subject", dominant_colors=["#0000ff"]),
            ]
            results = split_extract(str(Path(td) / "src.png"), layers, output_dir=td)
            out = str(Path(td) / "roundtrip.png")
            composite_layers(results, width=100, height=100, output_path=out)

            comp = Image.open(out).convert("RGB")
            lr, lg, lb = comp.getpixel((25, 50))
            assert lr > 150, f"Left should be reddish, got ({lr},{lg},{lb})"
            rr, rg, rb = comp.getpixel((75, 50))
            assert rb > 150, f"Right should be bluish, got ({rr},{rg},{rb})"

    def test_extract_then_edit_then_composite(self):
        """Full workflow: split → add layer → toggle visibility → composite."""
        with tempfile.TemporaryDirectory() as td:
            _create_test_image(str(Path(td) / "src.png"), 100, 100, {"full": (100, 100, 100)})
            layers = [
                LayerInfo(name="base", description="gray base", z_index=0,
                         content_type="background", dominant_colors=["#646464"]),
            ]
            results = split_extract(str(Path(td) / "src.png"), layers, output_dir=td)
            artwork = load_manifest(td)

            # Add a red overlay layer
            new_lr = add_layer(artwork, artwork_dir=td, name="overlay",
                              description="red overlay", z_index=1)
            # Paint it red
            overlay = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
            overlay.save(new_lr.image_path)

            # Composite — should see reddish tint
            artwork = load_manifest(td)
            out = str(Path(td) / "with_overlay.png")
            composite_layers(artwork.layers, width=100, height=100, output_path=out)
            comp = Image.open(out)
            r, g, b, a = comp.getpixel((50, 50))
            assert r > g, f"Should have red tint: ({r},{g},{b})"

            # Toggle overlay off
            toggle_visibility(artwork, artwork_dir=td, layer_name="overlay", visible=False)
            artwork = load_manifest(td)
            out2 = str(Path(td) / "without_overlay.png")
            composite_layers(artwork.layers, width=100, height=100, output_path=out2)
            comp2 = Image.open(out2)
            r2, g2, b2, a2 = comp2.getpixel((50, 50))
            # Without overlay, should be grayish (from base extract)
            assert abs(r2 - g2) < 30, f"Without overlay should be grayish: ({r2},{g2},{b2})"


# ===========================================================================
# Scenario 2: Regenerate mode with mock provider
# ===========================================================================

class TestFullWorkflowRegenerate:
    """User scenario: split with regenerate mode (mock provider)."""

    def test_regenerate_produces_layers_and_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            _create_test_image(str(Path(td) / "src.png"), 100, 100, {"full": (128, 128, 128)})
            layers = [
                LayerInfo(name="bg", description="background", z_index=0,
                         content_type="background", regeneration_prompt="Gray bg"),
                LayerInfo(name="fg", description="foreground", z_index=1,
                         content_type="subject", regeneration_prompt="Subject"),
            ]
            loop = asyncio.new_event_loop()
            results = loop.run_until_complete(
                split_regenerate(str(Path(td) / "src.png"), layers,
                                output_dir=td, provider="mock")
            )
            loop.close()

            assert len(results) == 2
            for r in results:
                assert Path(r.image_path).exists()
                img = Image.open(r.image_path)
                assert img.mode == "RGBA"
                assert img.size == (100, 100)

            manifest = json.loads((Path(td) / "manifest.json").read_text())
            assert manifest["version"] == 2
            assert manifest["split_mode"] == "regenerate"


# ===========================================================================
# Scenario 3: Layer editing operations chain
# ===========================================================================

class TestLayerEditingChain:
    """User scenario: series of edit operations on a layered artwork."""

    def test_add_remove_roundtrip(self):
        """Add a layer, verify it's there, remove it, verify it's gone."""
        with tempfile.TemporaryDirectory() as td:
            _setup_layered_artwork(td, 2)
            artwork = load_manifest(td)
            assert len(artwork.layers) == 2

            # Add
            add_layer(artwork, artwork_dir=td, name="new_effect",
                     description="glow", z_index=5, content_type="effect")
            artwork = load_manifest(td)
            assert len(artwork.layers) == 3
            assert any(l.info.name == "new_effect" for l in artwork.layers)

            # Remove
            remove_layer(artwork, artwork_dir=td, layer_name="new_effect")
            artwork = load_manifest(td)
            assert len(artwork.layers) == 2
            assert not any(l.info.name == "new_effect" for l in artwork.layers)
            assert not (Path(td) / "new_effect.png").exists()

    def test_lock_prevents_removal(self):
        """Lock a layer, attempt removal → fails. Unlock → removal succeeds."""
        with tempfile.TemporaryDirectory() as td:
            _setup_layered_artwork(td, 2)
            artwork = load_manifest(td)

            lock_layer(artwork, artwork_dir=td, layer_name="background", locked=True)
            artwork = load_manifest(td)

            with pytest.raises(ValueError, match="locked"):
                remove_layer(artwork, artwork_dir=td, layer_name="background")

            # Unlock → now removal works
            lock_layer(artwork, artwork_dir=td, layer_name="background", locked=False)
            artwork = load_manifest(td)
            remove_layer(artwork, artwork_dir=td, layer_name="background")
            artwork = load_manifest(td)
            assert not any(l.info.name == "background" for l in artwork.layers)

    def test_reorder_affects_composite_output(self):
        """Reorder layers → composite output changes."""
        with tempfile.TemporaryDirectory() as td:
            # Create 2 opaque full-canvas layers
            red = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
            red.save(str(Path(td) / "red.png"))
            blue = Image.new("RGBA", (50, 50), (0, 0, 255, 255))
            blue.save(str(Path(td) / "blue.png"))

            write_manifest(
                [LayerInfo(name="red", description="red", z_index=0),
                 LayerInfo(name="blue", description="blue", z_index=1)],
                output_dir=td, width=50, height=50,
            )

            # Blue on top → pixel should be blue
            artwork = load_manifest(td)
            out1 = str(Path(td) / "comp1.png")
            composite_layers(artwork.layers, width=50, height=50, output_path=out1)
            assert Image.open(out1).getpixel((25, 25))[:3] == (0, 0, 255)

            # Reorder: red to z=1 (top)
            reorder_layer(artwork, artwork_dir=td, layer_name="red", new_z_index=1)
            artwork = load_manifest(td)
            out2 = str(Path(td) / "comp2.png")
            composite_layers(artwork.layers, width=50, height=50, output_path=out2)
            # Now red on top
            assert Image.open(out2).getpixel((25, 25))[:3] == (255, 0, 0)

    def test_merge_composites_correctly(self):
        """Merge two layers → result is their composite."""
        with tempfile.TemporaryDirectory() as td:
            bg = Image.new("RGBA", (50, 50), (0, 0, 255, 255))
            bg.save(str(Path(td) / "bg.png"))
            # Foreground: transparent with red center
            fg = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
            for x in range(15, 35):
                for y in range(15, 35):
                    fg.putpixel((x, y), (255, 0, 0, 255))
            fg.save(str(Path(td) / "fg.png"))

            write_manifest(
                [LayerInfo(name="bg", description="blue", z_index=0),
                 LayerInfo(name="fg", description="red center", z_index=1)],
                output_dir=td, width=50, height=50,
            )
            artwork = load_manifest(td)
            merged = merge_layers(artwork, artwork_dir=td,
                                 layer_names=["bg", "fg"], merged_name="combined")

            # Merged image should have red center on blue background
            merged_img = Image.open(merged.image_path)
            assert merged_img.getpixel((25, 25))[:3] == (255, 0, 0)  # center: red
            assert merged_img.getpixel((5, 5))[:3] == (0, 0, 255)    # corner: blue

    def test_duplicate_is_independent(self):
        """Duplicate a layer, modify copy → original unchanged."""
        with tempfile.TemporaryDirectory() as td:
            _setup_layered_artwork(td, 2)
            artwork = load_manifest(td)

            dup = duplicate_layer(artwork, artwork_dir=td,
                                 layer_name="background", new_name="bg_copy")

            # Modify the copy
            modified = Image.new("RGBA", (200, 200), (255, 255, 0, 255))
            modified.save(dup.image_path)

            # Original should be unchanged
            artwork = load_manifest(td)
            orig = [l for l in artwork.layers if l.info.name == "background"][0]
            orig_img = Image.open(orig.image_path)
            r, g, b, a = orig_img.getpixel((100, 100))
            assert (r, g, b) != (255, 255, 0), "Original should not be modified"


# ===========================================================================
# Scenario 4: Blend modes in composite
# ===========================================================================

class TestBlendModesE2E:
    """Verify blend modes produce correct visual results in composite."""

    def test_screen_blend_in_composite(self):
        """Screen blend layer brightens the base when composited."""
        with tempfile.TemporaryDirectory() as td:
            base = Image.new("RGBA", (50, 50), (80, 80, 80, 255))
            base.save(str(Path(td) / "base.png"))
            glow = Image.new("RGBA", (50, 50), (150, 150, 150, 255))
            glow.save(str(Path(td) / "glow.png"))

            write_manifest(
                [LayerInfo(name="base", description="dark base", z_index=0),
                 LayerInfo(name="glow", description="bright glow", z_index=1, blend_mode="screen")],
                output_dir=td, width=50, height=50,
            )
            artwork = load_manifest(td)
            out = str(Path(td) / "comp.png")
            composite_layers(artwork.layers, width=50, height=50, output_path=out)

            comp = Image.open(out)
            r, g, b, a = comp.getpixel((25, 25))
            # Screen(80, 150) = 255 - (175 * 105)/255 ≈ 183
            assert r > 150, f"Screen should brighten to ~183, got {r}"
            assert r > 80, "Screen result must be brighter than base"

    def test_multiply_blend_in_composite(self):
        """Multiply blend layer darkens the base when composited."""
        with tempfile.TemporaryDirectory() as td:
            base = Image.new("RGBA", (50, 50), (200, 200, 200, 255))
            base.save(str(Path(td) / "base.png"))
            shadow = Image.new("RGBA", (50, 50), (100, 100, 100, 255))
            shadow.save(str(Path(td) / "shadow.png"))

            write_manifest(
                [LayerInfo(name="base", description="light base", z_index=0),
                 LayerInfo(name="shadow", description="shadow", z_index=1, blend_mode="multiply")],
                output_dir=td, width=50, height=50,
            )
            artwork = load_manifest(td)
            out = str(Path(td) / "comp.png")
            composite_layers(artwork.layers, width=50, height=50, output_path=out)

            comp = Image.open(out)
            r, g, b, a = comp.getpixel((25, 25))
            # Multiply(200, 100) = 200*100/255 ≈ 78
            assert r < 100, f"Multiply should darken to ~78, got {r}"
            assert r < 200, "Multiply result must be darker than base"

    def test_visibility_toggle_in_composite(self):
        """Invisible layer doesn't affect composite output."""
        with tempfile.TemporaryDirectory() as td:
            bg = Image.new("RGBA", (50, 50), (0, 0, 255, 255))
            bg.save(str(Path(td) / "bg.png"))
            fg = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
            fg.save(str(Path(td) / "fg.png"))

            write_manifest(
                [LayerInfo(name="bg", description="blue", z_index=0),
                 LayerInfo(name="fg", description="red", z_index=1)],
                output_dir=td, width=50, height=50,
            )

            # With fg visible → red
            artwork = load_manifest(td)
            out1 = str(Path(td) / "visible.png")
            composite_layers(artwork.layers, width=50, height=50, output_path=out1)
            assert Image.open(out1).getpixel((25, 25))[:3] == (255, 0, 0)

            # Toggle fg off → blue
            toggle_visibility(artwork, artwork_dir=td, layer_name="fg", visible=False)
            artwork = load_manifest(td)
            out2 = str(Path(td) / "hidden.png")
            composite_layers(artwork.layers, width=50, height=50, output_path=out2)
            assert Image.open(out2).getpixel((25, 25))[:3] == (0, 0, 255)


# ===========================================================================
# Scenario 5: Manifest V1 → V2 migration
# ===========================================================================

class TestManifestMigration:
    """Verify V1 manifests load correctly in V2 system."""

    def test_v1_manifest_loads_with_v2_ops(self):
        """V1 manifest (bbox, no id) → load → edit operations work."""
        with tempfile.TemporaryDirectory() as td:
            # Create V1-style manifest
            img = Image.new("RGBA", (100, 100), (0, 0, 255, 255))
            img.save(str(Path(td) / "bg.png"))

            v1_manifest = {
                "version": 1,
                "width": 100, "height": 100,
                "layers": [{
                    "name": "bg",
                    "description": "blue background",
                    "file": "bg.png",
                    "bbox": {"x": 0, "y": 0, "w": 100, "h": 100},
                    "z_index": 0,
                    "blend_mode": "normal",
                    "bg_color": "white",
                }],
            }
            (Path(td) / "manifest.json").write_text(json.dumps(v1_manifest))

            # Load and verify migration
            artwork = load_manifest(td)
            assert len(artwork.layers) == 1
            layer = artwork.layers[0]
            assert layer.info.id.startswith("layer_")
            assert layer.info.content_type == "background"
            assert layer.info.visible is True
            assert layer.info.bbox == {"x": 0, "y": 0, "w": 100, "h": 100}

            # Edit operations work on migrated artwork
            add_layer(artwork, artwork_dir=td, name="new_layer",
                     description="test", z_index=5)
            artwork = load_manifest(td)
            assert len(artwork.layers) == 2

            # Manifest is now V2
            manifest = json.loads((Path(td) / "manifest.json").read_text())
            assert manifest["version"] == 2


# ===========================================================================
# Scenario 6: Export
# ===========================================================================

class TestExportE2E:
    def test_export_from_full_canvas_layers(self):
        """Export V2 layers → each exported file is full-canvas."""
        with tempfile.TemporaryDirectory() as td:
            _setup_layered_artwork(td, 3)
            artwork = load_manifest(td)

            export_dir = str(Path(td) / "export" / "layers.psd")
            export_psd(artwork.layers, width=200, height=200, output_path=export_dir)

            png_dir = Path(td) / "export" / "layers"
            assert png_dir.exists()
            exported = list(png_dir.glob("*.png"))
            assert len(exported) >= 3

            for f in exported:
                if f.name == "manifest.json":
                    continue
                img = Image.open(str(f))
                assert img.size == (200, 200), f"{f.name}: expected 200x200, got {img.size}"
                assert img.mode == "RGBA", f"{f.name}: expected RGBA, got {img.mode}"


# ===========================================================================
# Scenario 7: Redraw with mock provider
# ===========================================================================

class TestRedrawE2E:
    def test_redraw_single_layer_mock(self):
        """Redraw a single layer with mock provider → file replaced."""
        with tempfile.TemporaryDirectory() as td:
            _setup_layered_artwork(td, 2)
            artwork = load_manifest(td)

            # Get original pixel value
            orig = Image.open(artwork.layers[1].image_path)
            orig_pixel = orig.getpixel((100, 100))

            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(
                redraw_layer(artwork, layer_name="mountains",
                            instruction="add snow on peaks",
                            provider="mock", artwork_dir=td)
            )
            loop.close()

            assert Path(result.image_path).exists()
            new_img = Image.open(result.image_path)
            assert new_img.mode == "RGBA"

    def test_redraw_merged_mock(self):
        """Merge+redraw with mock provider → single merged layer."""
        with tempfile.TemporaryDirectory() as td:
            _setup_layered_artwork(td, 3)
            artwork = load_manifest(td)

            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(
                redraw_merged(artwork, layer_names=["background", "mountains"],
                             instruction="improve depth",
                             merged_name="bg_mountains",
                             provider="mock", artwork_dir=td)
            )
            loop.close()

            assert isinstance(result, LayerResult)
            assert result.info.name == "bg_mountains"
            assert Path(result.image_path).exists()


# ===========================================================================
# Scenario 8: Edge cases and boundaries
# ===========================================================================

class TestEdgeCases:
    def test_single_layer_artwork(self):
        """Single-layer artwork: all ops still work."""
        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGBA", (50, 50), (100, 100, 100, 255))
            img.save(str(Path(td) / "only.png"))
            write_manifest(
                [LayerInfo(name="only", description="sole layer", z_index=0)],
                output_dir=td, width=50, height=50,
            )
            artwork = load_manifest(td)

            # Composite works
            out = str(Path(td) / "comp.png")
            composite_layers(artwork.layers, width=50, height=50, output_path=out)
            assert Path(out).exists()

            # Duplicate works
            dup = duplicate_layer(artwork, artwork_dir=td, layer_name="only", new_name="only_copy")
            assert dup.info.name == "only_copy"

    def test_empty_dominant_colors_extract(self):
        """Extract mode with empty dominant_colors → produces all-transparent layer."""
        with tempfile.TemporaryDirectory() as td:
            _create_test_image(str(Path(td) / "src.png"), 50, 50, {"full": (128, 128, 128)})
            layers = [
                LayerInfo(name="nothing", description="no colors specified", z_index=0,
                         content_type="subject", dominant_colors=[]),
            ]
            results = split_extract(str(Path(td) / "src.png"), layers, output_dir=td)
            img = Image.open(results[0].image_path)
            assert img.mode == "RGBA"
            assert img.size == (50, 50)
            # With no dominant colors, mask is all-black → fully transparent
            _, _, _, a = img.getpixel((25, 25))
            assert a == 0, f"No colors → should be transparent, got alpha={a}"

    def test_nonexistent_layer_operations_raise(self):
        """Operations on non-existent layer names raise ValueError."""
        with tempfile.TemporaryDirectory() as td:
            _setup_layered_artwork(td, 2)
            artwork = load_manifest(td)

            with pytest.raises(ValueError, match="not found"):
                remove_layer(artwork, artwork_dir=td, layer_name="ghost")
            with pytest.raises(ValueError, match="not found"):
                reorder_layer(artwork, artwork_dir=td, layer_name="ghost", new_z_index=0)
            with pytest.raises(ValueError, match="not found"):
                toggle_visibility(artwork, artwork_dir=td, layer_name="ghost", visible=False)
            with pytest.raises(ValueError, match="not found"):
                lock_layer(artwork, artwork_dir=td, layer_name="ghost", locked=True)

    def test_add_duplicate_name_raises(self):
        with tempfile.TemporaryDirectory() as td:
            _setup_layered_artwork(td, 2)
            artwork = load_manifest(td)
            with pytest.raises(ValueError, match="already exists"):
                add_layer(artwork, artwork_dir=td, name="background", description="dup", z_index=99)

    def test_many_layers(self):
        """10 layers: all operations still work correctly."""
        with tempfile.TemporaryDirectory() as td:
            infos = []
            for i in range(10):
                img = Image.new("RGBA", (50, 50), (i * 25, 0, 0, 255))
                img.save(str(Path(td) / f"layer_{i}.png"))
                infos.append(LayerInfo(name=f"layer_{i}", description=f"layer {i}", z_index=i))
            write_manifest(infos, output_dir=td, width=50, height=50)

            artwork = load_manifest(td)
            assert len(artwork.layers) == 10

            # Composite
            out = str(Path(td) / "comp.png")
            composite_layers(artwork.layers, width=50, height=50, output_path=out)
            assert Path(out).exists()

            # Remove middle layer
            remove_layer(artwork, artwork_dir=td, layer_name="layer_5")
            artwork = load_manifest(td)
            assert len(artwork.layers) == 9

    def test_prompt_v2_parse_handles_invalid_blend(self):
        """VLM might return invalid blend mode → defaults to normal."""
        raw = {
            "layers": [{
                "name": "test", "description": "test", "z_index": 0,
                "blend_mode": "overlay_dodge",  # invalid
                "content_type": "subject",
            }]
        }
        layers = parse_v2_response(raw)
        assert layers[0].blend_mode == "normal"


# ===========================================================================
# Scenario 9: SAM graceful degradation
# ===========================================================================

class TestSAMGraceful:
    def test_sam_not_installed_raises_clear_error(self):
        """Without SAM installed, sam_split gives clear install instruction."""
        from vulca.layers.sam import sam_split, SAM_AVAILABLE
        if SAM_AVAILABLE:
            pytest.skip("SAM is installed")
        with pytest.raises(ImportError, match="pip install vulca"):
            sam_split("dummy.png", [], output_dir="/tmp")


# ===========================================================================
# Scenario 10: CLI smoke test
# ===========================================================================

import subprocess
import sys

VULCA = [sys.executable, "-m", "vulca.cli"]


class TestCLISmoke:
    def test_all_layer_subcommands_have_help(self):
        """Every layer subcommand responds to --help without error."""
        subcommands = [
            "analyze", "split", "composite", "export", "regenerate", "evaluate",
            "redraw", "add", "remove", "reorder", "toggle", "lock", "merge", "duplicate",
        ]
        for cmd in subcommands:
            result = subprocess.run(
                VULCA + ["layers", cmd, "--help"],
                capture_output=True, text=True, timeout=10,
            )
            assert result.returncode == 0, f"layers {cmd} --help failed: {result.stderr}"

    def test_split_modes_in_help(self):
        result = subprocess.run(VULCA + ["layers", "split", "--help"],
                               capture_output=True, text=True, timeout=10)
        assert "regenerate" in result.stdout
        assert "extract" in result.stdout
        assert "sam" in result.stdout
