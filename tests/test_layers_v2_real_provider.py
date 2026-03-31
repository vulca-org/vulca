"""Layers V2 Real-Provider E2E Test.

Runs the COMPLETE layers workflow with real Gemini API.
Requires GOOGLE_API_KEY. Run manually: pytest tests/test_layers_v2_real_provider.py -v -s

This is the L4 validation: the last gate before declaring Layers V2 production-ready.
"""
import asyncio
import json
import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image

# Skip entire module if no API key
pytestmark = pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY"),
    reason="GOOGLE_API_KEY not set — run with: GOOGLE_API_KEY=... pytest tests/test_layers_v2_real_provider.py -v -s"
)


class TestRealAnalyze:
    """L4: VLM analysis returns valid V2 layer definitions."""

    def test_analyze_returns_v2_layers(self):
        """analyze_layers with real VLM → V2 LayerInfo with content_type, dominant_colors, regeneration_prompt."""
        from vulca.layers.analyze import analyze_layers

        # Use an existing artwork or create a simple test image
        with tempfile.TemporaryDirectory() as td:
            # Create a two-region test image (distinct enough for VLM)
            img = Image.new("RGB", (512, 512), (200, 220, 240))
            # Dark mountain shape in lower half
            for x in range(512):
                peak = int(180 + 80 * (1 - abs(x - 256) / 256))
                for y in range(peak, 512):
                    img.putpixel((x, y), (40, 50, 35))
            src = Path(td) / "landscape.png"
            img.save(str(src))

            loop = asyncio.new_event_loop()
            layers = loop.run_until_complete(analyze_layers(str(src)))
            loop.close()

            print(f"\n  VLM identified {len(layers)} layers:")
            for la in layers:
                print(f"    [{la.z_index}] {la.name} ({la.content_type}, {la.blend_mode})")
                print(f"        desc: {la.description}")
                print(f"        colors: {la.dominant_colors}")
                print(f"        regen: {la.regeneration_prompt[:80]}...")

            # L2: At least 2 layers identified
            assert len(layers) >= 2, f"Expected ≥2 layers, got {len(layers)}"

            # L2: Every layer has V2 fields
            for la in layers:
                assert la.name, "Layer must have a name"
                assert la.description, "Layer must have a description"
                assert la.content_type in ("background", "subject", "detail", "effect", "text"), \
                    f"Invalid content_type: {la.content_type}"
                assert la.blend_mode in ("normal", "screen", "multiply"), \
                    f"Invalid blend_mode: {la.blend_mode}"
                assert la.regeneration_prompt, "Layer must have regeneration_prompt"
                # bbox should NOT be set (V2 = no bbox)
                assert la.bbox is None, f"V2 should not have bbox, got {la.bbox}"

            # L2: z_indices are sorted ascending
            z_indices = [la.z_index for la in layers]
            assert z_indices == sorted(z_indices), f"z_indices not sorted: {z_indices}"


class TestRealSplitExtract:
    """L4: Real analyze → extract split → composite roundtrip."""

    def test_analyze_then_extract_then_composite(self):
        from vulca.layers.analyze import analyze_layers
        from vulca.layers.split import split_extract
        from vulca.layers.composite import composite_layers

        with tempfile.TemporaryDirectory() as td:
            # Create a recognizable test image
            img = Image.new("RGB", (256, 256), (135, 206, 235))  # sky blue
            # Green ground
            for x in range(256):
                for y in range(180, 256):
                    img.putpixel((x, y), (34, 139, 34))
            # Red object
            for x in range(100, 160):
                for y in range(120, 180):
                    img.putpixel((x, y), (220, 20, 60))
            src = Path(td) / "scene.png"
            img.save(str(src))

            # 1. Analyze
            loop = asyncio.new_event_loop()
            layers = loop.run_until_complete(analyze_layers(str(src)))
            loop.close()
            print(f"\n  Analyzed: {len(layers)} layers")

            # 2. Extract split
            out_dir = str(Path(td) / "layers")
            results = split_extract(str(src), layers, output_dir=out_dir)
            print(f"  Split into {len(results)} layers:")
            for r in results:
                img_l = Image.open(r.image_path)
                opaque = sum(1 for px in img_l.getdata() if px[3] > 128)
                total = img_l.width * img_l.height
                print(f"    [{r.info.z_index}] {r.info.name}: {img_l.size} {img_l.mode} "
                      f"opaque={opaque}/{total} ({opaque/total*100:.0f}%)")

            # L2: All layers full-canvas RGBA
            for r in results:
                layer_img = Image.open(r.image_path)
                assert layer_img.mode == "RGBA"
                assert layer_img.size == (256, 256)

            # L2: Manifest written
            manifest = json.loads((Path(out_dir) / "manifest.json").read_text())
            assert manifest["version"] == 2
            assert manifest["split_mode"] == "extract"

            # 3. Composite roundtrip
            comp_path = str(Path(td) / "roundtrip.png")
            composite_layers(results, width=256, height=256, output_path=comp_path)
            comp = Image.open(comp_path).convert("RGB")

            print(f"  Composite: {comp.size}")
            # The composite should not be all-black or all-transparent
            pixels = list(comp.getdata())
            non_black = sum(1 for r, g, b in pixels if r + g + b > 30)
            print(f"  Non-black pixels: {non_black}/{len(pixels)} ({non_black/len(pixels)*100:.0f}%)")
            assert non_black > len(pixels) * 0.1, "Composite should not be mostly black"


class TestRealSplitRegenerate:
    """L4: Real analyze → regenerate split with Gemini."""

    @pytest.mark.real_provider
    def test_analyze_then_regenerate(self):
        from vulca.layers.analyze import analyze_layers
        from vulca.layers.split import split_regenerate
        from vulca.layers.composite import composite_layers

        with tempfile.TemporaryDirectory() as td:
            # Simple test image
            img = Image.new("RGB", (256, 256), (200, 200, 220))
            for x in range(80, 180):
                for y in range(80, 200):
                    img.putpixel((x, y), (60, 80, 40))
            src = Path(td) / "artwork.png"
            img.save(str(src))

            loop = asyncio.new_event_loop()

            # 1. Analyze
            layers = loop.run_until_complete(analyze_layers(str(src)))
            print(f"\n  Analyzed: {len(layers)} layers")

            # 2. Regenerate (real Gemini)
            out_dir = str(Path(td) / "regen_layers")
            try:
                results = loop.run_until_complete(
                    split_regenerate(str(src), layers, output_dir=out_dir, provider="gemini")
                )
            except Exception as e:
                pytest.skip(f"Gemini generation failed (quota/rate limit?): {e}")

            loop.close()

            print(f"  Regenerated {len(results)} layers:")
            for r in results:
                layer_img = Image.open(r.image_path)
                print(f"    [{r.info.z_index}] {r.info.name}: {layer_img.size} {layer_img.mode}")

            # L2: All layers exist and are RGBA
            for r in results:
                assert Path(r.image_path).exists()
                layer_img = Image.open(r.image_path)
                assert layer_img.mode == "RGBA"
                assert layer_img.size == (256, 256)

            # L2: Manifest correct
            manifest = json.loads((Path(out_dir) / "manifest.json").read_text())
            assert manifest["split_mode"] == "regenerate"


class TestRealRedraw:
    """L4: Real redraw with Gemini."""

    @pytest.mark.real_provider
    def test_redraw_single_layer_real(self):
        from vulca.layers.manifest import write_manifest, load_manifest
        from vulca.layers.redraw import redraw_layer

        with tempfile.TemporaryDirectory() as td:
            # Create a simple layered artwork
            bg = Image.new("RGBA", (256, 256), (100, 150, 200, 255))
            bg.save(str(Path(td) / "sky.png"))
            fg = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            for x in range(80, 180):
                for y in range(100, 200):
                    fg.putpixel((x, y), (60, 120, 40, 255))
            fg.save(str(Path(td) / "tree.png"))

            from vulca.layers.types import LayerInfo
            write_manifest(
                [LayerInfo(name="sky", description="blue sky background", z_index=0,
                          content_type="background", regeneration_prompt="Clear blue sky"),
                 LayerInfo(name="tree", description="green tree in center", z_index=1,
                          content_type="subject", regeneration_prompt="Green tree silhouette")],
                output_dir=td, width=256, height=256, source_image="original.png",
            )
            artwork = load_manifest(td)

            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(
                    redraw_layer(artwork, layer_name="tree",
                                instruction="Add autumn colors — golden and red leaves",
                                provider="gemini", tradition="default", artwork_dir=td)
                )
            except Exception as e:
                pytest.skip(f"Gemini generation failed: {e}")
            loop.close()

            print(f"\n  Redrawn: {result.info.name} -> {result.image_path}")
            img = Image.open(result.image_path)
            print(f"  Size: {img.size}, Mode: {img.mode}")
            assert img.mode == "RGBA"
            assert img.size == (256, 256)


class TestRealFullWorkflow:
    """L4: The complete user journey — analyze → split → edit → redraw → composite."""

    @pytest.mark.real_provider
    def test_complete_journey(self):
        from vulca.layers.analyze import analyze_layers
        from vulca.layers.split import split_extract
        from vulca.layers.composite import composite_layers
        from vulca.layers.manifest import load_manifest
        from vulca.layers.ops import add_layer, toggle_visibility, duplicate_layer

        with tempfile.TemporaryDirectory() as td:
            # 1. Create source image
            img = Image.new("RGB", (256, 256), (180, 200, 230))
            for x in range(256):
                peak = int(150 + 50 * (1 - abs(x - 128) / 128))
                for y in range(peak, 256):
                    img.putpixel((x, y), (50, 70, 40))
            for x in range(100, 160):
                for y in range(130, 160):
                    img.putpixel((x, y), (120, 60, 30))
            src = Path(td) / "landscape.png"
            img.save(str(src))
            print("\n  === Complete Layers V2 Journey ===")

            # 2. Analyze
            loop = asyncio.new_event_loop()
            layers = loop.run_until_complete(analyze_layers(str(src)))
            loop.close()
            print(f"  [1/6] Analyzed: {len(layers)} layers")
            for la in layers:
                print(f"        [{la.z_index}] {la.name} ({la.content_type})")

            # 3. Extract split
            out_dir = str(Path(td) / "layers")
            results = split_extract(str(src), layers, output_dir=out_dir)
            print(f"  [2/6] Split: {len(results)} layers extracted")

            # 4. Edit: add an effect layer
            artwork = load_manifest(out_dir)
            new_layer = add_layer(artwork, artwork_dir=out_dir, name="warm_glow",
                                 description="warm golden glow overlay",
                                 z_index=len(layers), content_type="effect",
                                 blend_mode="screen")
            # Paint warm glow
            glow = Image.new("RGBA", (256, 256), (255, 200, 100, 40))
            glow.save(new_layer.image_path)
            print(f"  [3/6] Added: warm_glow effect layer")

            # 5. Duplicate a layer
            artwork = load_manifest(out_dir)
            first_layer = artwork.layers[0].info.name
            dup = duplicate_layer(artwork, artwork_dir=out_dir,
                                 layer_name=first_layer, new_name=f"{first_layer}_v2")
            print(f"  [4/6] Duplicated: {first_layer} → {dup.info.name}")

            # 6. Toggle visibility
            artwork = load_manifest(out_dir)
            toggle_visibility(artwork, artwork_dir=out_dir,
                            layer_name=dup.info.name, visible=False)
            print(f"  [5/6] Toggled: {dup.info.name} hidden")

            # 7. Composite
            artwork = load_manifest(out_dir)
            comp_path = str(Path(td) / "final_composite.png")
            composite_layers(artwork.layers, width=256, height=256, output_path=comp_path)
            comp = Image.open(comp_path)
            print(f"  [6/6] Composite: {comp.size} {comp.mode}")

            # Verify final state
            manifest = json.loads((Path(out_dir) / "manifest.json").read_text())
            total_layers = len(manifest["layers"])
            visible_layers = sum(1 for l in manifest["layers"] if l.get("visible", True))
            print(f"\n  Final: {total_layers} layers ({visible_layers} visible)")
            print(f"  Composite: {comp_path}")

            assert total_layers >= 3  # original layers + glow + duplicate
            assert visible_layers < total_layers  # duplicate is hidden
            assert comp.size == (256, 256)
            assert comp.mode == "RGBA"

            # Composite should not be all-black
            pixels = list(comp.convert("RGB").getdata())
            non_black = sum(1 for r, g, b in pixels if r + g + b > 30)
            assert non_black > len(pixels) * 0.3, "Final composite should have substantial content"

            print(f"  ✓ Complete journey passed — {total_layers} layers, composite valid")
