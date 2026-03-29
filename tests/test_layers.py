import json
from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork
from vulca.layers.analyze import analyze_layers, parse_layer_response


class TestAnalyzeLayers:
    def test_parse_layer_response_valid(self):
        raw = {
            "layers": [
                {"name": "background", "description": "sky and mountains", "bbox": {"x": 0, "y": 0, "w": 100, "h": 60}, "z_index": 0, "blend_mode": "normal"},
                {"name": "effects", "description": "mist", "bbox": {"x": 0, "y": 0, "w": 100, "h": 100}, "z_index": 3, "blend_mode": "screen"},
            ]
        }
        layers = parse_layer_response(raw)
        assert len(layers) == 2
        assert layers[0].name == "background"
        assert layers[1].blend_mode == "screen"

    def test_parse_layer_response_missing_blend(self):
        raw = {
            "layers": [
                {"name": "bg", "description": "sky", "bbox": {"x": 0, "y": 0, "w": 100, "h": 100}, "z_index": 0}
            ]
        }
        layers = parse_layer_response(raw)
        assert layers[0].blend_mode == "normal"

    def test_parse_assigns_bg_color_from_blend(self):
        raw = {
            "layers": [
                {"name": "glow", "description": "light", "bbox": {"x": 0, "y": 0, "w": 100, "h": 100}, "z_index": 1, "blend_mode": "screen"}
            ]
        }
        layers = parse_layer_response(raw)
        assert layers[0].bg_color == "black"  # screen blend → black bg


class TestLayerTypes:
    def test_layer_info_defaults(self):
        li = LayerInfo(name="background", description="sky", bbox={"x": 0, "y": 0, "w": 100, "h": 60}, z_index=0)
        assert li.blend_mode == "normal"
        assert li.bg_color == "white"
        assert li.locked is False

    def test_layer_result(self):
        info = LayerInfo(name="bg", description="sky", bbox={"x": 0, "y": 0, "w": 100, "h": 100}, z_index=0)
        lr = LayerResult(info=info, image_path="bg.png")
        assert lr.scores == {}

    def test_layered_artwork(self):
        la = LayeredArtwork(composite_path="comp.jpg", layers=[], manifest_path="manifest.json")
        assert la.brief is None

    def test_layer_info_screen_blend(self):
        li = LayerInfo(name="effects", description="glow", bbox={"x": 0, "y": 0, "w": 100, "h": 100}, z_index=3, blend_mode="screen", bg_color="black")
        assert li.blend_mode == "screen"
        assert li.bg_color == "black"


import tempfile
from pathlib import Path
from PIL import Image
from vulca.layers.split import crop_layer, chromakey_white, write_manifest
from vulca.layers.composite import composite_layers


class TestSplitLayers:
    def test_crop_layer(self):
        """Approach B: crop_layer outputs minimal-size RGBA crop, not full canvas."""
        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGB", (100, 100), "red")
            src = Path(td) / "src.png"
            img.save(str(src))
            info = LayerInfo(name="test", description="", bbox={"x": 0, "y": 0, "w": 50, "h": 50}, z_index=0)
            out = crop_layer(str(src), info, output_dir=td)
            cropped = Image.open(out)
            # Approach B: minimal crop size, NOT full canvas
            assert cropped.size == (50, 50), f"Expected minimal crop (50, 50), got {cropped.size}"
            # Must be RGBA (chromakey always converts)
            assert cropped.mode == "RGBA"
            # Content should be red
            assert cropped.getpixel((25, 25))[:3] == (255, 0, 0)

    def test_crop_layer_chromakey_white(self):
        """crop_layer with bg_color='white' removes white background."""
        with tempfile.TemporaryDirectory() as td:
            # White background with red center
            img = Image.new("RGB", (100, 100), (255, 255, 255))
            for x in range(25, 75):
                for y in range(25, 75):
                    img.putpixel((x, y), (255, 0, 0))
            src = Path(td) / "src.png"
            img.save(str(src))
            info = LayerInfo(name="test", description="", bbox={"x": 0, "y": 0, "w": 100, "h": 100},
                           z_index=0, bg_color="white")
            out = crop_layer(str(src), info, output_dir=td)
            cropped = Image.open(out)
            assert cropped.mode == "RGBA"
            # White corners should be transparent
            assert cropped.getpixel((5, 5))[3] == 0
            # Red center should be opaque
            assert cropped.getpixel((50, 50))[3] == 255

    def test_chromakey_white(self):
        # Create image with white background and red square
        img = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
        for x in range(25, 75):
            for y in range(25, 75):
                img.putpixel((x, y), (255, 0, 0, 255))
        result = chromakey_white(img, threshold=30)
        # Corners should be transparent
        assert result.getpixel((0, 0))[3] == 0
        # Center should be opaque
        assert result.getpixel((50, 50))[3] == 255


class TestManifest:
    def test_write_manifest(self):
        """write_manifest creates manifest.json with bbox and layer metadata."""
        with tempfile.TemporaryDirectory() as td:
            infos = [
                LayerInfo(name="bg", description="background", bbox={"x": 0, "y": 0, "w": 100, "h": 100},
                         z_index=0, blend_mode="normal", bg_color="white"),
                LayerInfo(name="fg", description="foreground", bbox={"x": 25, "y": 25, "w": 50, "h": 50},
                         z_index=1, blend_mode="normal", bg_color="white"),
            ]
            path = write_manifest(infos, output_dir=td, width=1024, height=1024)
            assert Path(path).exists()
            manifest = json.loads(Path(path).read_text())
            assert manifest["version"] == 1
            assert manifest["width"] == 1024
            assert manifest["height"] == 1024
            assert len(manifest["layers"]) == 2
            # Sorted by z_index
            assert manifest["layers"][0]["name"] == "bg"
            assert manifest["layers"][1]["name"] == "fg"
            # bbox preserved as percentages
            assert manifest["layers"][1]["bbox"] == {"x": 25, "y": 25, "w": 50, "h": 50}
            # bg_color included
            assert manifest["layers"][0]["bg_color"] == "white"
            # file field points to PNG
            assert manifest["layers"][0]["file"] == "bg.png"


class TestCompositeLayers:
    def test_composite_two_layers(self):
        with tempfile.TemporaryDirectory() as td:
            # Background: blue
            bg = Image.new("RGBA", (100, 100), (0, 0, 255, 255))
            bg_path = Path(td) / "bg.png"
            bg.save(str(bg_path))

            # Foreground: red square with alpha
            fg = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
            for x in range(25, 75):
                for y in range(25, 75):
                    fg.putpixel((x, y), (255, 0, 0, 255))
            fg_path = Path(td) / "fg.png"
            fg.save(str(fg_path))

            bg_info = LayerInfo(name="bg", description="", bbox={"x": 0, "y": 0, "w": 100, "h": 100}, z_index=0)
            fg_info = LayerInfo(name="fg", description="", bbox={"x": 0, "y": 0, "w": 100, "h": 100}, z_index=1)
            layers = [
                LayerResult(info=bg_info, image_path=str(bg_path)),
                LayerResult(info=fg_info, image_path=str(fg_path)),
            ]
            out = Path(td) / "composite.png"
            composite_layers(layers, width=100, height=100, output_path=str(out))
            comp = Image.open(str(out))
            # Center should be red (foreground)
            assert comp.getpixel((50, 50))[:3] == (255, 0, 0)
            # Corner should be blue (background)
            assert comp.getpixel((5, 5))[:3] == (0, 0, 255)

    def test_composite_offset_layers(self):
        """Approach B: composite pastes cropped layers at bbox offset positions."""
        with tempfile.TemporaryDirectory() as td:
            # Background: full-size blue (100x100, bbox covers entire canvas)
            bg = Image.new("RGBA", (100, 100), (0, 0, 255, 255))
            bg_path = Path(td) / "bg.png"
            bg.save(str(bg_path))

            # Foreground: small red crop (50x50, placed at center)
            fg = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
            fg_path = Path(td) / "fg.png"
            fg.save(str(fg_path))

            bg_info = LayerInfo(name="bg", description="", bbox={"x": 0, "y": 0, "w": 100, "h": 100}, z_index=0)
            fg_info = LayerInfo(name="fg", description="", bbox={"x": 25, "y": 25, "w": 50, "h": 50}, z_index=1)
            layers = [
                LayerResult(info=bg_info, image_path=str(bg_path)),
                LayerResult(info=fg_info, image_path=str(fg_path)),
            ]
            out = Path(td) / "composite.png"
            composite_layers(layers, width=100, height=100, output_path=str(out))
            comp = Image.open(str(out))
            # Center should be red (foreground at offset 25,25)
            assert comp.getpixel((50, 50))[:3] == (255, 0, 0)
            # Corner should be blue (background, untouched by fg)
            assert comp.getpixel((5, 5))[:3] == (0, 0, 255)
            # Edge at (24, 24) should still be blue (just outside fg bbox)
            assert comp.getpixel((24, 24))[:3] == (0, 0, 255)


from vulca.layers.generate import build_layer_prompt, infer_bg_color


class TestLayerGeneration:
    def test_infer_bg_color_solid(self):
        assert infer_bg_color("normal") == "white"

    def test_infer_bg_color_screen(self):
        assert infer_bg_color("screen") == "black"

    def test_infer_bg_color_multiply(self):
        assert infer_bg_color("multiply") == "gray"

    def test_build_layer_prompt(self):
        info = LayerInfo(name="pavilion", description="ancient Chinese pavilion", bbox={"x": 20, "y": 30, "w": 60, "h": 50}, z_index=1, bg_color="white")
        prompt = build_layer_prompt(info, tradition="chinese_xieyi")
        assert "pavilion" in prompt
        assert "white background" in prompt.lower() or "solid white" in prompt.lower()
        assert "transparent" in prompt.lower() or "isolated" in prompt.lower()

    def test_build_layer_prompt_screen(self):
        info = LayerInfo(name="glow", description="neon glow effects", bbox={"x": 0, "y": 0, "w": 100, "h": 100}, z_index=3, blend_mode="screen", bg_color="black")
        prompt = build_layer_prompt(info, tradition="default")
        assert "black background" in prompt.lower()


from vulca.layers.regenerate import build_regenerate_prompt


class TestRegenerate:
    def test_build_regenerate_prompt(self):
        prompt = build_regenerate_prompt(tradition="chinese_xieyi")
        assert "reference" in prompt.lower()
        assert "unified" in prompt.lower() or "consistent" in prompt.lower()
        assert "chinese" in prompt.lower() or "xieyi" in prompt.lower()

    def test_build_regenerate_prompt_default(self):
        prompt = build_regenerate_prompt()
        assert "reference" in prompt.lower()


from vulca.layers.export import export_psd


class TestExportPSD:
    def test_export_creates_png_directory(self):
        """Export creates PNG directory with full-canvas layers + manifest."""
        with tempfile.TemporaryDirectory() as td:
            # Create two minimal crop layers (Approach B)
            bg = Image.new("RGBA", (100, 100), (0, 0, 255, 255))
            bg_path = Path(td) / "bg.png"
            bg.save(str(bg_path))

            fg = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
            fg_path = Path(td) / "fg.png"
            fg.save(str(fg_path))

            layers = [
                LayerResult(
                    info=LayerInfo(name="bg", description="", bbox={"x": 0, "y": 0, "w": 100, "h": 100}, z_index=0),
                    image_path=str(bg_path),
                ),
                LayerResult(
                    info=LayerInfo(name="fg", description="", bbox={"x": 25, "y": 25, "w": 50, "h": 50}, z_index=1),
                    image_path=str(fg_path),
                ),
            ]

            out_dir = Path(td) / "export"
            export_psd(layers, width=100, height=100, output_path=str(out_dir / "layers.psd"))

            # PNG directory should exist with full-canvas expanded layers
            png_dir = out_dir / "layers"
            assert png_dir.exists()
            exported_bg = Image.open(str(png_dir / "00_bg.png"))
            exported_fg = Image.open(str(png_dir / "01_fg.png"))
            # Both exported as full-canvas (100x100)
            assert exported_bg.size == (100, 100)
            assert exported_fg.size == (100, 100)
            # fg layer: transparent at corner, opaque at center
            assert exported_fg.getpixel((5, 5))[3] == 0      # outside bbox: transparent
            assert exported_fg.getpixel((50, 50))[3] == 255   # inside bbox: opaque red
            # Manifest written
            assert (png_dir / "manifest.json").exists()

    def test_export_psd_format_no_fake_file(self):
        """--format psd must NOT write fake PSD placeholder."""
        with tempfile.TemporaryDirectory() as td:
            bg = Image.new("RGBA", (10, 10), (0, 0, 255, 255))
            bg_path = Path(td) / "bg.png"
            bg.save(str(bg_path))
            layers = [
                LayerResult(
                    info=LayerInfo(name="bg", description="", bbox={"x": 0, "y": 0, "w": 100, "h": 100}, z_index=0),
                    image_path=str(bg_path),
                ),
            ]
            psd_path = Path(td) / "output.psd"
            export_psd(layers, width=10, height=10, output_path=str(psd_path))
            # Must NOT write fake PSD placeholder
            if psd_path.exists():
                content = psd_path.read_bytes()
                assert content != b"PSD_PLACEHOLDER", "Must not write fake PSD file"


class TestRoundtripIntegrity:
    """L3: composite(split(img)) approx img — roundtrip integrity for Approach B."""

    def test_crop_outputs_minimal_rgba(self):
        """Approach B: each layer is a minimal-size RGBA crop."""
        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGB", (100, 100), "red")
            for x in range(50, 100):
                for y in range(100):
                    img.putpixel((x, y), (0, 0, 255))
            src = Path(td) / "src.png"
            img.save(str(src))

            info = LayerInfo(name="left", description="", bbox={"x": 0, "y": 0, "w": 50, "h": 100}, z_index=0)
            out = crop_layer(str(src), info, output_dir=td)
            cropped = Image.open(out)

            assert cropped.mode == "RGBA"
            # Approach B: minimal crop (50x100), NOT full canvas (100x100)
            assert cropped.size == (50, 100), (
                f"Approach B: layer should be minimal crop (50, 100), got {cropped.size}"
            )

    def test_split_composite_roundtrip_full_bbox(self):
        """Approach B: single full-canvas layer roundtrip (no bbox offset needed)."""
        with tempfile.TemporaryDirectory() as td:
            # Single layer with full bbox — no offset, roundtrip should preserve content
            original = Image.new("RGBA", (100, 100), (0, 0, 255, 255))
            for x in range(25, 75):
                for y in range(25, 75):
                    original.putpixel((x, y), (255, 0, 0, 255))
            src = Path(td) / "original.png"
            original.save(str(src))

            # Full-canvas layer (bbox covers entire image — crop == full image)
            bg_info = LayerInfo(name="bg", description="full canvas",
                              bbox={"x": 0, "y": 0, "w": 100, "h": 100}, z_index=0)
            bg_path = crop_layer(str(src), bg_info, output_dir=td)
            bg_crop = Image.open(bg_path)

            # Approach B: full-bbox crop is same size as original
            assert bg_crop.size == (100, 100)
            assert bg_crop.mode == "RGBA"

            layers = [LayerResult(info=bg_info, image_path=bg_path)]
            out = Path(td) / "roundtrip.png"
            composite_layers(layers, width=100, height=100, output_path=str(out))
            result = Image.open(str(out)).convert("RGBA")

            # Full-canvas layer: composite should preserve content
            center = result.getpixel((50, 50))
            assert center[:3] == (255, 0, 0), f"Center should be red, got {center[:3]}"
            corner = result.getpixel((5, 5))
            assert corner[:3] == (0, 0, 255), f"Corner should be blue, got {corner[:3]}"

    def test_split_composite_roundtrip(self):
        """L3: composite(split(img)) should approximately reconstruct the original."""
        with tempfile.TemporaryDirectory() as td:
            # Blue canvas with red center square
            original = Image.new("RGBA", (100, 100), (0, 0, 255, 255))
            for x in range(25, 75):
                for y in range(25, 75):
                    original.putpixel((x, y), (255, 0, 0, 255))
            src = Path(td) / "original.png"
            original.save(str(src))

            bg_info = LayerInfo(name="bg", description="blue background",
                              bbox={"x": 0, "y": 0, "w": 100, "h": 100}, z_index=0)
            fg_info = LayerInfo(name="fg", description="red square",
                              bbox={"x": 25, "y": 25, "w": 50, "h": 50}, z_index=1)

            bg_path = crop_layer(str(src), bg_info, output_dir=td)
            fg_path = crop_layer(str(src), fg_info, output_dir=td)

            # Verify minimal crop sizes (Approach B)
            assert Image.open(bg_path).size == (100, 100)
            assert Image.open(fg_path).size == (50, 50)

            layers = [
                LayerResult(info=bg_info, image_path=bg_path),
                LayerResult(info=fg_info, image_path=fg_path),
            ]
            out = Path(td) / "roundtrip.png"
            composite_layers(layers, width=100, height=100, output_path=str(out))
            result = Image.open(str(out)).convert("RGBA")

            # L3: roundtrip pixel integrity
            center = result.getpixel((50, 50))
            assert center[:3] == (255, 0, 0), f"Center should be red, got {center[:3]}"
            corner = result.getpixel((5, 5))
            assert corner[:3] == (0, 0, 255), f"Corner should be blue, got {corner[:3]}"


import subprocess
import sys

VULCA = [sys.executable, "-m", "vulca.cli"]


class TestLayersCLI:
    def test_layers_analyze_help(self):
        result = subprocess.run(VULCA + ["layers", "--help"], capture_output=True, text=True, timeout=10)
        assert result.returncode == 0
        assert "analyze" in result.stdout

    def test_layers_in_main_help(self):
        result = subprocess.run(VULCA + ["--help"], capture_output=True, text=True, timeout=10)
        assert "layers" in result.stdout
