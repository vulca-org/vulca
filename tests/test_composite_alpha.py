"""Test that composite_layers applies alpha extraction before blending."""
import pytest
import numpy as np
from PIL import Image
from pathlib import Path

from vulca.layers.types import LayerInfo, LayerResult
from vulca.layers.composite import composite_layers


class TestCompositeWithAlpha:
    def test_subject_on_white_doesnt_cover_background(self, tmp_path):
        bg = Image.new("RGB", (64, 64), (200, 180, 160))
        bg_path = str(tmp_path / "bg.png")
        bg.save(bg_path)

        fg = Image.new("RGB", (64, 64), (255, 255, 255))
        for x in range(20, 44):
            for y in range(20, 44):
                fg.putpixel((x, y), (30, 30, 30))
        fg_path = str(tmp_path / "fg.png")
        fg.save(fg_path)

        layers = [
            LayerResult(info=LayerInfo(name="bg", description="bg", z_index=0,
                                       content_type="background"), image_path=bg_path),
            LayerResult(info=LayerInfo(name="fg", description="fg", z_index=1,
                                       content_type="subject"), image_path=fg_path),
        ]

        out = str(tmp_path / "composite.png")
        composite_layers(layers, width=64, height=64, output_path=out)
        comp = np.array(Image.open(out).convert("RGB"))

        corner = comp[5, 5]
        assert corner[0] > 150, f"Corner R={corner[0]}, expected bg color not white"

        center = comp[32, 32]
        assert center[0] < 100, f"Center R={center[0]}, expected dark content"

    def test_multiply_layer_works_without_alpha_extraction(self, tmp_path):
        bg = Image.new("RGB", (64, 64), (200, 200, 200))
        bg_path = str(tmp_path / "bg.png")
        bg.save(bg_path)

        mul = Image.new("RGB", (64, 64), (255, 255, 255))
        for x in range(20, 44):
            for y in range(20, 44):
                mul.putpixel((x, y), (100, 100, 100))
        mul_path = str(tmp_path / "mul.png")
        mul.save(mul_path)

        layers = [
            LayerResult(info=LayerInfo(name="bg", description="bg", z_index=0,
                                       content_type="background"), image_path=bg_path),
            LayerResult(info=LayerInfo(name="ink", description="ink", z_index=1,
                                       content_type="atmosphere", blend_mode="multiply"),
                        image_path=mul_path),
        ]

        out = str(tmp_path / "composite.png")
        composite_layers(layers, width=64, height=64, output_path=out)
        comp = np.array(Image.open(out).convert("RGB"))

        corner = comp[5, 5]
        assert abs(int(corner[0]) - 200) < 15, f"Corner={corner[0]}, multiply white should preserve bg"

        center = comp[32, 32]
        assert center[0] < 120, f"Center={center[0]}, multiply dark should darken bg"
