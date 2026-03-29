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
