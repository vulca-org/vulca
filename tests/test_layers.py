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
