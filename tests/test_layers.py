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
from vulca.layers.split import crop_layer, chromakey_white
from vulca.layers.composite import composite_layers


class TestSplitLayers:
    def test_crop_layer(self):
        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGB", (100, 100), "red")
            src = Path(td) / "src.png"
            img.save(str(src))
            info = LayerInfo(name="test", description="", bbox={"x": 0, "y": 0, "w": 50, "h": 50}, z_index=0)
            out = crop_layer(str(src), info, output_dir=td)
            cropped = Image.open(out)
            assert cropped.size == (50, 50)

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
    def test_export_creates_psd(self):
        with tempfile.TemporaryDirectory() as td:
            # Create two layer PNGs
            bg = Image.new("RGBA", (100, 100), (0, 0, 255, 255))
            bg_path = Path(td) / "bg.png"
            bg.save(str(bg_path))

            fg = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
            fg_path = Path(td) / "fg.png"
            fg.save(str(fg_path))

            layers = [
                LayerResult(
                    info=LayerInfo(name="background", description="blue", bbox={"x": 0, "y": 0, "w": 100, "h": 100}, z_index=0),
                    image_path=str(bg_path),
                ),
                LayerResult(
                    info=LayerInfo(name="foreground", description="red", bbox={"x": 0, "y": 0, "w": 100, "h": 100}, z_index=1),
                    image_path=str(fg_path),
                ),
            ]
            psd_path = Path(td) / "output.psd"
            export_psd(layers, width=100, height=100, output_path=str(psd_path))
            assert psd_path.exists()
            assert psd_path.stat().st_size > 0


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
