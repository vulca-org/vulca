"""L3 roundtrip integrity tests for Layers V2."""
import tempfile
from pathlib import Path

from PIL import Image

from vulca.layers.types import LayerInfo, LayerResult
from vulca.layers.split import split_extract
from vulca.layers.composite import composite_layers


class TestExtractRoundtrip:
    def test_extract_composite_preserves_colors(self):
        """composite(split_extract(img)) should approximately reconstruct original."""
        with tempfile.TemporaryDirectory() as td:
            # Red left, blue right
            original = Image.new("RGB", (100, 100), (255, 0, 0))
            for x in range(50, 100):
                for y in range(100):
                    original.putpixel((x, y), (0, 0, 255))
            src = Path(td) / "original.png"
            original.save(str(src))

            layers = [
                LayerInfo(name="red", description="red half", z_index=0,
                         content_type="subject", dominant_colors=["#ff0000"]),
                LayerInfo(name="blue", description="blue half", z_index=1,
                         content_type="subject", dominant_colors=["#0000ff"]),
            ]
            results = split_extract(str(src), layers, output_dir=td)

            out = Path(td) / "roundtrip.png"
            composite_layers(results, width=100, height=100, output_path=str(out))
            comp = Image.open(str(out)).convert("RGB")

            r, g, b = comp.getpixel((25, 50))
            assert r > 200, f"Expected red, got ({r},{g},{b})"
            r2, g2, b2 = comp.getpixel((75, 50))
            assert b2 > 200, f"Expected blue, got ({r2},{g2},{b2})"

    def test_all_layers_full_canvas_rgba(self):
        """Every layer from split_extract must be full-canvas RGBA."""
        with tempfile.TemporaryDirectory() as td:
            original = Image.new("RGB", (200, 150), (128, 64, 32))
            src = Path(td) / "original.png"
            original.save(str(src))

            layers = [
                LayerInfo(name="bg", description="background", z_index=0,
                         content_type="background", dominant_colors=["#804020"]),
            ]
            results = split_extract(str(src), layers, output_dir=td)
            for r in results:
                img = Image.open(r.image_path)
                assert img.mode == "RGBA", f"Expected RGBA, got {img.mode}"
                assert img.size == (200, 150), f"Expected (200,150), got {img.size}"


class TestBlendRoundtrip:
    def test_normal_blend_full_canvas(self):
        """Full-canvas layers with normal blend compose correctly."""
        with tempfile.TemporaryDirectory() as td:
            bg = Image.new("RGBA", (100, 100), (0, 0, 255, 255))
            bg.save(str(Path(td) / "bg.png"))
            fg = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
            for x in range(25, 75):
                for y in range(25, 75):
                    fg.putpixel((x, y), (255, 0, 0, 255))
            fg.save(str(Path(td) / "fg.png"))

            layers = [
                LayerResult(info=LayerInfo(name="bg", description="blue", z_index=0),
                           image_path=str(Path(td) / "bg.png")),
                LayerResult(info=LayerInfo(name="fg", description="red square", z_index=1),
                           image_path=str(Path(td) / "fg.png")),
            ]
            out = str(Path(td) / "comp.png")
            composite_layers(layers, width=100, height=100, output_path=out)
            comp = Image.open(out)
            assert comp.getpixel((50, 50))[:3] == (255, 0, 0)
            assert comp.getpixel((5, 5))[:3] == (0, 0, 255)

    def test_screen_blend_brightens(self):
        """Screen layer produces brighter result than base."""
        with tempfile.TemporaryDirectory() as td:
            base = Image.new("RGBA", (10, 10), (100, 100, 100, 255))
            base.save(str(Path(td) / "base.png"))
            glow = Image.new("RGBA", (10, 10), (150, 150, 150, 255))
            glow.save(str(Path(td) / "glow.png"))

            layers = [
                LayerResult(info=LayerInfo(name="base", description="", z_index=0),
                           image_path=str(Path(td) / "base.png")),
                LayerResult(info=LayerInfo(name="glow", description="", z_index=1, blend_mode="screen"),
                           image_path=str(Path(td) / "glow.png")),
            ]
            out = str(Path(td) / "comp.png")
            composite_layers(layers, width=10, height=10, output_path=out)
            comp = Image.open(out)
            r, _, _, _ = comp.getpixel((5, 5))
            assert r > 150, f"Screen should brighten to ~191, got {r}"

    def test_invisible_layer_not_composited(self):
        """visible=False layer doesn't affect output."""
        with tempfile.TemporaryDirectory() as td:
            bg = Image.new("RGBA", (10, 10), (0, 0, 255, 255))
            bg.save(str(Path(td) / "bg.png"))
            fg = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
            fg.save(str(Path(td) / "fg.png"))

            layers = [
                LayerResult(info=LayerInfo(name="bg", description="", z_index=0),
                           image_path=str(Path(td) / "bg.png")),
                LayerResult(info=LayerInfo(name="fg", description="", z_index=1, visible=False),
                           image_path=str(Path(td) / "fg.png")),
            ]
            out = str(Path(td) / "comp.png")
            composite_layers(layers, width=10, height=10, output_path=out)
            comp = Image.open(out)
            assert comp.getpixel((5, 5))[:3] == (0, 0, 255)
