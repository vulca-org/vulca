"""v0.17.14 — native mask path for inpaint_artwork.

Patch 1 contract: ``inpaint_artwork(mask_path=...)`` routes through the
provider's edit endpoint with precision masks (SAM, layer alpha, HSV filter).
The legacy region= path stays unchanged for backward-compat.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from PIL import Image


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _write_rgb(path: Path, size=(100, 100), color=(200, 100, 50)) -> str:
    Image.new("RGB", size, color).save(str(path))
    return str(path)


def _write_mask(path: Path, size=(100, 100)) -> str:
    """Mask: outer ring alpha=255 (preserve), inner square alpha=0 (edit)."""
    mask = Image.new("RGBA", size, (0, 0, 0, 255))
    inner = Image.new("RGBA", (size[0] // 2, size[1] // 2), (0, 0, 0, 0))
    mask.paste(inner, (size[0] // 4, size[1] // 4))
    mask.save(str(path))
    return str(path)


class TestMaskPathPrecedence:
    def test_mask_path_overrides_region(self, tmp_path, caplog):
        """Both set → mask wins, warning logged. bbox reflects mask alpha=0
        region (codex P1 — was hardcoded 100x100 pre-revision)."""
        from vulca.inpaint import ainpaint

        img = _write_rgb(tmp_path / "src.png")
        # _write_mask creates inner 50x50 alpha=0 square at (25,25)
        mask = _write_mask(tmp_path / "mask.png")

        with caplog.at_level("WARNING", logger="vulca.inpaint"):
            result = _run(
                ainpaint(
                    img,
                    region="0,0,50,50",
                    mask_path=mask,
                    instruction="repaint",
                    mock=True,
                )
            )
        # bbox follows the mask's alpha=0 region, NOT the ignored region= arg
        assert result.bbox == {"x": 25, "y": 25, "w": 50, "h": 50}
        # Warning fired
        assert any(
            "mask_path and region" in rec.message
            for rec in caplog.records
        )


class TestMaskPathOpenAI:
    def test_mask_path_openai_native_mock(self, tmp_path):
        """Mock=True path: produces an output PNG without hitting OpenAI."""
        from vulca.inpaint import ainpaint

        img = _write_rgb(tmp_path / "src.png")
        mask = _write_mask(tmp_path / "mask.png")
        out = tmp_path / "out.png"

        result = _run(
            ainpaint(
                img,
                mask_path=mask,
                instruction="cinnabar lanterns",
                provider="openai",
                output_path=str(out),
                mock=True,
            )
        )
        assert result.blended == str(out)
        assert out.exists()
        # In mock mode no real cost is incurred
        assert result.cost_usd == 0.0


class TestMaskPathValidation:
    def test_mask_path_size_mismatch_raises(self, tmp_path):
        from vulca.inpaint import ainpaint

        img = _write_rgb(tmp_path / "src.png", size=(100, 100))
        mask_p = tmp_path / "mask.png"
        mask = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
        mask.save(str(mask_p))

        with pytest.raises(ValueError, match="mask size"):
            _run(
                ainpaint(
                    str(img),
                    mask_path=str(mask_p),
                    instruction="x",
                    mock=True,
                )
            )

    def test_mask_path_missing_file_raises(self, tmp_path):
        from vulca.inpaint import ainpaint

        img = _write_rgb(tmp_path / "src.png")

        with pytest.raises(FileNotFoundError, match="mask_path"):
            _run(
                ainpaint(
                    str(img),
                    mask_path=str(tmp_path / "does-not-exist.png"),
                    instruction="x",
                    mock=True,
                )
            )

    def test_image_path_missing_file_raises(self, tmp_path):
        from vulca.inpaint import ainpaint

        mask = _write_mask(tmp_path / "mask.png")
        with pytest.raises(FileNotFoundError, match="image"):
            _run(
                ainpaint(
                    str(tmp_path / "missing.png"),
                    mask_path=mask,
                    instruction="x",
                    mock=True,
                )
            )


class TestMaskPathProviderGate:
    def test_gemini_raises_with_hint(self, tmp_path):
        """Gemini fail-loud — no silent fallback to legacy crop path."""
        from vulca.inpaint import ainpaint

        img = _write_rgb(tmp_path / "src.png")
        mask = _write_mask(tmp_path / "mask.png")

        with pytest.raises(NotImplementedError, match="openai"):
            _run(
                ainpaint(
                    img,
                    mask_path=mask,
                    instruction="x",
                    provider="gemini",
                    mock=False,
                )
            )

    def test_comfyui_raises_with_hint(self, tmp_path):
        """ComfyUI fail-loud."""
        from vulca.inpaint import ainpaint

        img = _write_rgb(tmp_path / "src.png")
        mask = _write_mask(tmp_path / "mask.png")

        with pytest.raises(NotImplementedError, match="openai"):
            _run(
                ainpaint(
                    img,
                    mask_path=mask,
                    instruction="x",
                    provider="comfyui",
                    mock=False,
                )
            )


class TestLegacyRegionPath:
    def test_legacy_region_unchanged(self, tmp_path):
        """Old caller passing region= still works (mock path)."""
        from vulca.inpaint import ainpaint

        img = _write_rgb(tmp_path / "src.png")
        result = _run(
            ainpaint(
                img,
                region="0,0,50,50",
                instruction="x",
                mock=True,
            )
        )
        assert result.bbox == {"x": 0, "y": 0, "w": 50, "h": 50}
        assert result.blended  # blended path produced

    def test_neither_mask_nor_region_raises(self, tmp_path):
        from vulca.inpaint import ainpaint

        img = _write_rgb(tmp_path / "src.png")
        with pytest.raises(ValueError, match="mask_path or region"):
            _run(ainpaint(img, instruction="x", mock=True))


class TestBboxFromMask:
    def test_bbox_reflects_actual_alpha_zero_region(self, tmp_path):
        """Codex P1: bbox must come from the mask's editable region, not
        a hardcoded full-canvas {0,0,100,100}."""
        from vulca.inpaint import ainpaint

        img = _write_rgb(tmp_path / "src.png", size=(100, 100))
        # Mask: only middle 50% (25-75) is editable (alpha=0)
        mask_p = tmp_path / "mask.png"
        mask = Image.new("RGBA", (100, 100), (0, 0, 0, 255))
        for y in range(25, 75):
            for x in range(25, 75):
                mask.putpixel((x, y), (0, 0, 0, 0))
        mask.save(str(mask_p))

        result = _run(
            ainpaint(
                img, mask_path=str(mask_p),
                instruction="x", mock=True,
            )
        )
        # bbox should be roughly {x=25, y=25, w=50, h=50}, not full canvas
        assert result.bbox["x"] == 25
        assert result.bbox["y"] == 25
        assert result.bbox["w"] == 50
        assert result.bbox["h"] == 50

    def test_bbox_full_canvas_when_mask_fully_opaque(self, tmp_path):
        """Edge case: fully-opaque mask (no alpha=0 pixels) returns full
        canvas as a non-lying signal that nothing was actually editable."""
        from vulca.inpaint import ainpaint

        img = _write_rgb(tmp_path / "src.png")
        mask_p = tmp_path / "mask.png"
        Image.new("RGBA", (100, 100), (0, 0, 0, 255)).save(str(mask_p))

        result = _run(
            ainpaint(
                img, mask_path=str(mask_p),
                instruction="x", mock=True,
            )
        )
        assert result.bbox == {"x": 0, "y": 0, "w": 100, "h": 100}


class TestProviderDefaults:
    def test_legacy_region_defaults_to_gemini(self, tmp_path, monkeypatch):
        """P2.5 review: legacy region= callers must keep their pre-v0.17.14
        gemini default. Silent flip to openai would reroute billing."""
        captured: dict = {}

        # Stub phase.repaint to capture provider arg
        from vulca.studio.phases import inpaint as phase_mod

        async def stub_repaint(*args, **kwargs):
            captured["provider"] = kwargs.get("provider")
            return [str(tmp_path / "v.png")]

        monkeypatch.setattr(phase_mod.InpaintPhase, "repaint", stub_repaint)
        # Stub blend so we don't actually try to open a fake variant
        async def stub_blend(*args, **kwargs):
            return str(tmp_path / "blended.png")
        monkeypatch.setattr(phase_mod.InpaintPhase, "blend", stub_blend)

        from vulca.inpaint import ainpaint

        img = _write_rgb(tmp_path / "src.png")
        # Save a stub variant + blended to make life easy
        Image.new("RGB", (50, 50), (0, 0, 0)).save(str(tmp_path / "v.png"))
        Image.new("RGB", (50, 50), (0, 0, 0)).save(str(tmp_path / "blended.png"))

        _run(
            ainpaint(
                img, region="0,0,50,50", instruction="x",
                mock=False,  # need real branch to see resolved_provider
            )
        )
        assert captured["provider"] == "gemini"


class TestOutputPath:
    def test_output_path_not_in_place(self, tmp_path):
        """Original image file unchanged after inpaint."""
        from vulca.inpaint import ainpaint

        img = tmp_path / "src.png"
        Image.new("RGB", (100, 100), (10, 20, 30)).save(str(img))
        before = img.read_bytes()
        mask = _write_mask(tmp_path / "mask.png")

        out = tmp_path / "edited.png"
        _run(
            ainpaint(
                str(img),
                mask_path=mask,
                instruction="x",
                output_path=str(out),
                mock=True,
            )
        )
        # Original bytes preserved
        assert img.read_bytes() == before
        # Output written
        assert out.exists()
