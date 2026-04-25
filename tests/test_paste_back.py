"""v0.17.14 — layers_paste_back glue verb tests.

Patch 3 contract: composite an edited RGBA layer onto a foreign RGB source
image using the layer's alpha (or an explicit mask). Distinct from
layers_composite (manifest-stack flatten).
"""
from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


def _write_rgb(p: Path, *, size=(100, 100), color=(50, 50, 50)) -> str:
    Image.new("RGB", size, color).save(str(p))
    return str(p)


def _write_layer_with_alpha_square(p: Path, *, size=(100, 100)) -> str:
    """Layer: red square 25-75 fully opaque, rest fully transparent."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    for y in range(25, 75):
        for x in range(25, 75):
            img.putpixel((x, y), (255, 0, 0, 255))
    img.save(str(p))
    return str(p)


class TestAlphaMode:
    def test_alpha_mode_preserves_source_outside_mask(self, tmp_path):
        from vulca.layers.paste_back import paste_back

        src = _write_rgb(tmp_path / "src.png", color=(20, 20, 20))
        layer = _write_layer_with_alpha_square(tmp_path / "layer.png")

        result = paste_back(src, layer, blend_mode="alpha")
        out = Image.open(result["output_path"]).convert("RGB")

        # Inside mask → red layer
        assert out.getpixel((50, 50)) == (255, 0, 0)
        # Outside mask → original gray
        assert out.getpixel((0, 0)) == (20, 20, 20)
        assert out.getpixel((90, 90)) == (20, 20, 20)


class TestFeatheredMode:
    def test_feathered_softens_edges(self, tmp_path):
        """Feathered should differ from hard near the alpha boundary.

        After the v0.17.14 RGB-clamp fix, "feather" softens transitions
        inside the layer's alpha region (where layer_alpha=255 but the
        blurred applied_mask is intermediate), not outside it. Outside
        the boundary the layer's alpha=0 region is clamped to source —
        intentional, prevents the codex-flagged black bleed. So we check
        a pixel JUST INSIDE (26,50) where the soft transition lives.
        """
        from vulca.layers.paste_back import paste_back

        src = _write_rgb(tmp_path / "src.png", color=(0, 255, 0))
        layer = _write_layer_with_alpha_square(tmp_path / "layer.png")

        feathered = paste_back(
            src, layer, blend_mode="feathered", feather_px=6,
            output_path=str(tmp_path / "feathered.png"),
        )
        hard = paste_back(
            src, layer, blend_mode="hard",
            output_path=str(tmp_path / "hard.png"),
        )

        f_img = Image.open(feathered["output_path"]).convert("RGB")
        h_img = Image.open(hard["output_path"]).convert("RGB")

        # Center stays red in both modes
        assert f_img.getpixel((50, 50))[0] > 200
        assert h_img.getpixel((50, 50))[0] > 200

        # Just inside the alpha boundary (26,50): hard is full red; feathered
        # is partially mixed because blurred mask is below 255 here.
        f_inside = f_img.getpixel((26, 50))
        h_inside = h_img.getpixel((26, 50))
        assert h_inside == (255, 0, 0), (
            f"hard should keep pure red just inside boundary, got {h_inside}"
        )
        assert f_inside != h_inside, (
            f"feathered must differ from hard near boundary, got "
            f"f={f_inside} h={h_inside}"
        )
        assert f_inside[1] > 0, (
            f"feathered green should leak into red region near edge, got {f_inside}"
        )


class TestHardMode:
    def test_hard_threshold_no_partial_pixels(self, tmp_path):
        """Hard mode: every pixel is either source-color or layer-color, never blended."""
        from vulca.layers.paste_back import paste_back

        src = _write_rgb(tmp_path / "src.png", color=(0, 0, 255))
        # Build a layer whose alpha has soft edges
        layer_img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        for y in range(40, 60):
            for x in range(40, 60):
                # Inner 100% alpha
                layer_img.putpixel((x, y), (255, 0, 0, 255))
        # Add a fuzzy edge
        for y in (39, 60):
            for x in range(40, 60):
                layer_img.putpixel((x, y), (255, 0, 0, 100))  # mid-alpha
        layer_p = tmp_path / "layer.png"
        layer_img.save(str(layer_p))

        result = paste_back(
            str(_write_rgb(tmp_path / "src.png", color=(0, 0, 255))),
            str(layer_p),
            blend_mode="hard",
        )
        out = Image.open(result["output_path"]).convert("RGB")

        # Inner: pure red
        assert out.getpixel((50, 50)) == (255, 0, 0)
        # Mid-alpha edge under hard mode: thresholded — alpha 100 < 127 → drops to source
        assert out.getpixel((50, 39)) == (0, 0, 255)


class TestExplicitMaskOverride:
    def test_explicit_mask_overrides_alpha(self, tmp_path):
        """mask_path replaces the layer's alpha channel."""
        from vulca.layers.paste_back import paste_back

        src = _write_rgb(tmp_path / "src.png", color=(50, 50, 50))
        # Layer alpha covers center 25-75
        layer = _write_layer_with_alpha_square(tmp_path / "layer.png")
        # External mask covers ONLY top-left quadrant
        mask = Image.new("L", (100, 100), 0)
        for y in range(0, 50):
            for x in range(0, 50):
                mask.putpixel((x, y), 255)
        mask_p = tmp_path / "mask.png"
        mask.save(str(mask_p))

        result = paste_back(
            src, layer, mask_path=str(mask_p), blend_mode="alpha"
        )
        out = Image.open(result["output_path"]).convert("RGB")

        # Top-left center (25,25) — covered by external mask AND layer alpha → red
        assert out.getpixel((25, 25)) == (255, 0, 0)
        # Bottom-right (75,75) — outside external mask → source
        assert out.getpixel((75, 75)) == (50, 50, 50)


class TestSizeMismatch:
    def test_size_mismatch_raises(self, tmp_path):
        from vulca.layers.paste_back import paste_back

        src = _write_rgb(tmp_path / "src.png", size=(100, 100))
        layer_p = tmp_path / "layer.png"
        Image.new("RGBA", (50, 50), (255, 0, 0, 255)).save(str(layer_p))

        with pytest.raises(ValueError, match="size"):
            paste_back(src, str(layer_p))

    def test_explicit_mask_size_mismatch_raises(self, tmp_path):
        from vulca.layers.paste_back import paste_back

        src = _write_rgb(tmp_path / "src.png", size=(100, 100))
        layer = _write_layer_with_alpha_square(tmp_path / "layer.png")
        mask_p = tmp_path / "mask.png"
        Image.new("L", (60, 60), 255).save(str(mask_p))

        with pytest.raises(ValueError, match="mask size"):
            paste_back(src, layer, mask_path=str(mask_p))


class TestRgbClampOnAlphaZero:
    def test_alpha_zero_rgb_does_not_bleed(self, tmp_path):
        """Codex P1: decompose-output layers commonly store BLACK (0,0,0)
        in alpha=0 regions. Pre-fix Image.composite(layer_rgb, src, mask)
        would mix black RGB with source at semi-transparent edges,
        darkening fringes. Post-fix the layer's RGB is clamped to source
        wherever the layer's alpha is 0, eliminating the bleed."""
        from vulca.layers.paste_back import paste_back

        # Source: bright red
        src = _write_rgb(tmp_path / "src.png", color=(255, 0, 0))

        # Layer: opaque green square in center 25-75; alpha=0 black elsewhere
        layer_img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        for y in range(25, 75):
            for x in range(25, 75):
                layer_img.putpixel((x, y), (0, 255, 0, 255))
        layer_p = tmp_path / "layer.png"
        layer_img.save(str(layer_p))

        # External mask covers the entire canvas (so alpha-zero RGB would
        # leak into the composite if not clamped)
        mask_p = tmp_path / "mask.png"
        Image.new("L", (100, 100), 255).save(str(mask_p))

        result = paste_back(
            src, str(layer_p), mask_path=str(mask_p), blend_mode="alpha"
        )
        out = Image.open(result["output_path"]).convert("RGB")

        # Inside layer's opaque region: green
        assert out.getpixel((50, 50)) == (0, 255, 0)
        # Outside layer's opaque region but inside the external mask:
        # source (red) MUST show through despite the mask saying "edit here"
        assert out.getpixel((0, 0)) == (255, 0, 0), (
            "alpha=0 region in layer must not bleed black into composite"
        )


class TestDefaults:
    def test_default_output_name(self, tmp_path):
        """Default output: <src_dir>/<src_stem>_with_<layer_stem>.png."""
        from vulca.layers.paste_back import paste_back

        src = _write_rgb(tmp_path / "iter0.png")
        layer = _write_layer_with_alpha_square(tmp_path / "lanterns.png")

        result = paste_back(src, layer)
        assert Path(result["output_path"]).name == "iter0_with_lanterns.png"
        assert Path(result["output_path"]).exists()

    def test_unknown_blend_mode_raises(self, tmp_path):
        from vulca.layers.paste_back import paste_back

        src = _write_rgb(tmp_path / "src.png")
        layer = _write_layer_with_alpha_square(tmp_path / "layer.png")
        with pytest.raises(ValueError, match="blend_mode"):
            paste_back(src, layer, blend_mode="rainbow")

    def test_missing_source_raises(self, tmp_path):
        from vulca.layers.paste_back import paste_back

        layer = _write_layer_with_alpha_square(tmp_path / "layer.png")
        with pytest.raises(FileNotFoundError, match="source_image"):
            paste_back(str(tmp_path / "missing.png"), layer)

    def test_missing_layer_raises(self, tmp_path):
        from vulca.layers.paste_back import paste_back

        src = _write_rgb(tmp_path / "src.png")
        with pytest.raises(FileNotFoundError, match="layer_image"):
            paste_back(src, str(tmp_path / "missing.png"))
