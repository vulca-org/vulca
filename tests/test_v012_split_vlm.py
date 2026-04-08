"""Tests for v0.12.0 — split_vlm + generate_vlm_mask custom prompt."""
from __future__ import annotations

import asyncio
import base64
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
from PIL import Image

from vulca.layers.types import LayerInfo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_layer(
    name: str,
    z: int,
    content_type: str = "subject",
    dominant_colors: list | None = None,
    **kwargs,
) -> LayerInfo:
    defaults = dict(
        name=name,
        id=f"layer_{name}",
        description=f"Test {name}",
        z_index=z,
        blend_mode="normal",
        content_type=content_type,
        dominant_colors=dominant_colors or [],
        regeneration_prompt="",
    )
    defaults.update(kwargs)
    return LayerInfo(**defaults)


def _image_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _white_top_half_mask(w: int = 100, h: int = 100) -> Image.Image:
    """Non-degenerate mask: white top half, black bottom half."""
    mask = Image.new("L", (w, h), 0)
    pixels = mask.load()
    for y in range(h // 2):
        for x in range(w):
            pixels[x, y] = 255
    return mask


def _white_bottom_half_mask(w: int = 100, h: int = 100) -> Image.Image:
    """Non-degenerate mask: black top half, white bottom half."""
    mask = Image.new("L", (w, h), 0)
    pixels = mask.load()
    for y in range(h // 2, h):
        for x in range(w):
            pixels[x, y] = 255
    return mask


def _degenerate_mask(w: int = 100, h: int = 100) -> Image.Image:
    """Degenerate mask: all 128 — std < 10."""
    return Image.new("L", (w, h), 128)


def _make_mock_provider(mask: Image.Image) -> MagicMock:
    mock_result = MagicMock()
    mock_result.image_b64 = _image_to_b64(mask)
    mock_provider = MagicMock()
    mock_provider.generate = AsyncMock(return_value=mock_result)
    return mock_provider


def _make_test_image(w: int = 100, h: int = 100) -> Image.Image:
    img = Image.new("RGB", (w, h), (200, 150, 100))
    return img


# ---------------------------------------------------------------------------
# Task 1: generate_vlm_mask custom prompt
# ---------------------------------------------------------------------------

class TestGenerateVlmMaskCustomPrompt:
    """Verify that custom prompt is forwarded to the VLM provider."""

    def test_custom_prompt_is_forwarded(self):
        """When prompt= is given, the provider receives that prompt (not the default)."""
        from vulca.layers.vlm_mask import generate_vlm_mask

        mask = _white_top_half_mask()
        mock_result = MagicMock()
        mock_result.image_b64 = _image_to_b64(mask)
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value=mock_result)

        content_img = _make_test_image()
        content_b64 = _image_to_b64(content_img)
        custom_prompt = "Custom segmentation: white = sky, black = ground"

        with patch("vulca.providers.get_image_provider", return_value=mock_provider):
            result = asyncio.run(
                generate_vlm_mask(content_b64, prompt=custom_prompt)
            )

        # The provider must have been called with the custom prompt
        call_args = mock_provider.generate.call_args
        assert call_args is not None
        assert call_args[0][0] == custom_prompt

    def test_default_prompt_used_when_no_prompt_given(self):
        """When prompt= is empty/omitted, the default VLM_MASK_PROMPT is used."""
        from vulca.layers.vlm_mask import generate_vlm_mask, VLM_MASK_PROMPT

        mask = _white_top_half_mask()
        mock_result = MagicMock()
        mock_result.image_b64 = _image_to_b64(mask)
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value=mock_result)

        content_img = _make_test_image()
        content_b64 = _image_to_b64(content_img)

        with patch("vulca.providers.get_image_provider", return_value=mock_provider):
            asyncio.run(
                generate_vlm_mask(content_b64)
            )

        call_args = mock_provider.generate.call_args
        assert call_args[0][0] == VLM_MASK_PROMPT

    def test_empty_string_uses_default_prompt(self):
        """Explicit prompt='' also falls back to VLM_MASK_PROMPT."""
        from vulca.layers.vlm_mask import generate_vlm_mask, VLM_MASK_PROMPT

        mask = _white_top_half_mask()
        mock_result = MagicMock()
        mock_result.image_b64 = _image_to_b64(mask)
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value=mock_result)

        content_img = _make_test_image()
        content_b64 = _image_to_b64(content_img)

        with patch("vulca.providers.get_image_provider", return_value=mock_provider):
            asyncio.run(
                generate_vlm_mask(content_b64, prompt="")
            )

        call_args = mock_provider.generate.call_args
        assert call_args[0][0] == VLM_MASK_PROMPT

    def test_returns_grayscale_image_with_custom_prompt(self):
        """Result is a grayscale PIL Image when a custom prompt is provided."""
        from vulca.layers.vlm_mask import generate_vlm_mask

        mask = _white_top_half_mask()
        mock_result = MagicMock()
        mock_result.image_b64 = _image_to_b64(mask)
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value=mock_result)

        content_b64 = _image_to_b64(_make_test_image())

        with patch("vulca.providers.get_image_provider", return_value=mock_provider):
            result = asyncio.run(
                generate_vlm_mask(content_b64, prompt="white = foreground object")
            )

        assert result is not None
        assert result.mode == "L"


# ---------------------------------------------------------------------------
# Task 2: split_vlm core
# ---------------------------------------------------------------------------

class TestSplitVlm:
    """Tests for split_vlm: VLM semantic split with exclusive assignment."""

    def test_vlm_mode_returns_rgba_layers(self):
        """split_vlm produces full-canvas RGBA images for each layer."""
        from vulca.layers.split import split_vlm

        fg = _make_layer("fg", z=1, content_type="subject")
        bg = _make_layer("bg", z=0, content_type="background")

        fg_mask = _white_top_half_mask()
        mock_provider = _make_mock_provider(fg_mask)

        with tempfile.TemporaryDirectory() as td:
            img = _make_test_image()
            img_path = str(Path(td) / "source.png")
            img.save(img_path)

            with patch("vulca.providers.get_image_provider", return_value=mock_provider):
                results = asyncio.run(
                    split_vlm(img_path, [fg, bg], output_dir=td)
                )

            assert len(results) == 2
            for r in results:
                out = Image.open(r.image_path)
                assert out.mode == "RGBA", f"Layer {r.info.name} must be RGBA"
                assert out.size == (100, 100), "Must be full-canvas size"

    def test_vlm_exclusive_assignment(self):
        """Foreground-first: pixels claimed by fg are NOT repeated in bg."""
        from vulca.layers.split import split_vlm

        # fg has z=2, bg has z=0; fg should get top-half, bg gets rest
        fg = _make_layer("fg", z=2, content_type="subject")
        bg = _make_layer("bg", z=0, content_type="background")

        fg_mask = _white_top_half_mask(100, 100)
        mock_provider = _make_mock_provider(fg_mask)

        with tempfile.TemporaryDirectory() as td:
            img = _make_test_image()
            img_path = str(Path(td) / "source.png")
            img.save(img_path)

            with patch("vulca.providers.get_image_provider", return_value=mock_provider):
                results = asyncio.run(
                    split_vlm(img_path, [fg, bg], output_dir=td)
                )

            # Collect results by name
            by_name = {r.info.name: r for r in results}
            fg_img = Image.open(by_name["fg"].image_path)
            bg_img = Image.open(by_name["bg"].image_path)

            fg_alpha = np.array(fg_img)[:, :, 3]
            bg_alpha = np.array(bg_img)[:, :, 3]

            # Where fg is opaque, bg must be transparent (exclusive assignment)
            fg_opaque = fg_alpha > 127
            bg_opaque = bg_alpha > 127
            overlap = fg_opaque & bg_opaque
            assert not overlap.any(), "fg and bg must not share opaque pixels"

    def test_background_gets_unclaimed(self):
        """Background layer receives all pixels NOT claimed by foreground layers."""
        from vulca.layers.split import split_vlm

        fg = _make_layer("fg", z=1, content_type="subject")
        bg = _make_layer("bg", z=0, content_type="background")

        # fg claims top half → bg should get bottom half
        fg_mask = _white_top_half_mask(100, 100)
        mock_provider = _make_mock_provider(fg_mask)

        with tempfile.TemporaryDirectory() as td:
            img = _make_test_image()
            img_path = str(Path(td) / "source.png")
            img.save(img_path)

            with patch("vulca.providers.get_image_provider", return_value=mock_provider):
                results = asyncio.run(
                    split_vlm(img_path, [fg, bg], output_dir=td)
                )

            by_name = {r.info.name: r for r in results}
            bg_img = Image.open(by_name["bg"].image_path)
            bg_alpha = np.array(bg_img)[:, :, 3]

            # Top half (rows 0–49): should be transparent (claimed by fg)
            top_half_alpha = bg_alpha[:50, :]
            assert top_half_alpha.max() == 0, "Background top half must be transparent"

            # Bottom half (rows 50–99): should be opaque (unclaimed)
            bottom_half_alpha = bg_alpha[50:, :]
            assert bottom_half_alpha.min() > 127, "Background bottom half must be opaque"

    def test_vlm_fallback_on_degenerate_mask(self):
        """When VLM returns a degenerate mask (std < 10), color mask fallback is used."""
        from vulca.layers.split import split_vlm

        # Layer with a recognizable dominant color for fallback
        fg = _make_layer(
            "fg", z=1, content_type="subject",
            dominant_colors=["#C89664"],  # reddish-brown
        )
        bg = _make_layer("bg", z=0, content_type="background")

        # Degenerate mask: std < 10
        degen_mask = _degenerate_mask(100, 100)
        mock_provider = _make_mock_provider(degen_mask)

        with tempfile.TemporaryDirectory() as td:
            img = _make_test_image()  # RGB 200,150,100 ~ reddish-brown
            img_path = str(Path(td) / "source.png")
            img.save(img_path)

            # Should NOT raise even when VLM mask is degenerate
            with patch("vulca.providers.get_image_provider", return_value=mock_provider):
                results = asyncio.run(
                    split_vlm(img_path, [fg, bg], output_dir=td)
                )

            # Verify results are returned (fallback to color mask doesn't crash)
            assert len(results) == 2
            for r in results:
                out = Image.open(r.image_path)
                assert out.mode == "RGBA"

    def test_manifest_written_with_vlm_mode(self):
        """split_vlm writes manifest.json with split_mode='vlm'."""
        from vulca.layers.split import split_vlm

        fg = _make_layer("fg", z=1, content_type="subject")
        bg = _make_layer("bg", z=0, content_type="background")

        fg_mask = _white_top_half_mask()
        mock_provider = _make_mock_provider(fg_mask)

        with tempfile.TemporaryDirectory() as td:
            img = _make_test_image()
            img_path = str(Path(td) / "source.png")
            img.save(img_path)

            with patch("vulca.providers.get_image_provider", return_value=mock_provider):
                asyncio.run(
                    split_vlm(img_path, [fg, bg], output_dir=td)
                )

            manifest_path = Path(td) / "manifest.json"
            assert manifest_path.exists(), "manifest.json must be written"
            manifest = json.loads(manifest_path.read_text())

        assert manifest.get("split_mode") == "vlm", (
            f"Expected split_mode='vlm', got {manifest.get('split_mode')!r}"
        )
        assert manifest.get("version") == 3

    def test_no_api_call_for_background(self):
        """Background layer does NOT trigger a VLM API call."""
        from vulca.layers.split import split_vlm

        fg = _make_layer("fg", z=1, content_type="subject")
        bg = _make_layer("bg", z=0, content_type="background")

        fg_mask = _white_top_half_mask()
        mock_provider = _make_mock_provider(fg_mask)

        with tempfile.TemporaryDirectory() as td:
            img = _make_test_image()
            img_path = str(Path(td) / "source.png")
            img.save(img_path)

            with patch("vulca.providers.get_image_provider", return_value=mock_provider):
                asyncio.run(
                    split_vlm(img_path, [fg, bg], output_dir=td)
                )

        # Only 1 API call: for the foreground layer (not for background)
        assert mock_provider.generate.call_count == 1, (
            f"Expected 1 API call (fg only), got {mock_provider.generate.call_count}"
        )

    def test_results_sorted_by_z_index(self):
        """Results are returned sorted by z_index ascending."""
        from vulca.layers.split import split_vlm

        layer_a = _make_layer("layer_a", z=2, content_type="subject")
        layer_b = _make_layer("layer_b", z=1, content_type="subject")
        bg = _make_layer("bg", z=0, content_type="background")

        # Return alternating masks to distinguish layers
        mask_a = _white_top_half_mask()
        mask_b = _white_bottom_half_mask()

        call_count = [0]
        async def _multi_mask_generate(prompt, **kwargs):
            idx = call_count[0]
            call_count[0] += 1
            result = MagicMock()
            # First call = layer_a (z=2, highest), second call = layer_b (z=1)
            result.image_b64 = _image_to_b64(mask_a if idx == 0 else mask_b)
            return result

        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(side_effect=_multi_mask_generate)

        with tempfile.TemporaryDirectory() as td:
            img = _make_test_image()
            img_path = str(Path(td) / "source.png")
            img.save(img_path)

            with patch("vulca.providers.get_image_provider", return_value=mock_provider):
                results = asyncio.run(
                    split_vlm(img_path, [layer_a, layer_b, bg], output_dir=td)
                )

        z_indices = [r.info.z_index for r in results]
        assert z_indices == sorted(z_indices), "Results must be sorted by z_index ascending"


# ---------------------------------------------------------------------------
# Task 3: Export split_vlm from vulca.layers
# ---------------------------------------------------------------------------

class TestSplitVlmExport:
    """split_vlm is importable from vulca.layers."""

    def test_import_from_layers_package(self):
        from vulca.layers import split_vlm
        assert callable(split_vlm)


# ---------------------------------------------------------------------------
# Task 4: CLI --mode vlm wiring
# ---------------------------------------------------------------------------

class TestSplitVlmCLI:
    """CLI --mode vlm is wired up."""

    def test_vlm_mode_in_cli_choices(self):
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, "-m", "vulca", "layers", "split", "--help"],
            capture_output=True, text=True,
        )
        # argparse prints the choices in the help text
        assert "vlm" in result.stdout, (
            f"Expected 'vlm' in 'layers split --help' output, got:\n{result.stdout}"
        )


# ---------------------------------------------------------------------------
# Task 5: MCP layers_split supports mode='vlm'
# ---------------------------------------------------------------------------

class TestSplitVlmMCP:
    """MCP layers_split supports mode='vlm'."""

    def test_mcp_docstring_mentions_vlm(self):
        from vulca.mcp_server import layers_split
        assert "vlm" in layers_split.__doc__
