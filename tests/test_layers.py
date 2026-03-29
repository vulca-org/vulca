from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork


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
