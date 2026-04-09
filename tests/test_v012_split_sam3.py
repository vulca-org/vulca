"""Tests for v0.12.0 — split_sam3 (SAM3 text-prompted segmentation)."""
from __future__ import annotations

import pytest
pytest.importorskip("torch", reason="torch is an optional dependency for SAM3 segmentation")

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
from PIL import Image

from vulca.layers.types import LayerInfo
import vulca.layers.sam3 as sam3_module
from vulca.layers.sam3 import sam3_split


def _make_layer(name, z, content_type="subject", description="", **kw):
    defaults = dict(
        name=name,
        id=f"layer_{name}",
        description=description or f"Test {name}",
        z_index=z,
        blend_mode="normal",
        content_type=content_type,
        dominant_colors=[],
        regeneration_prompt="",
    )
    defaults.update(kw)
    return LayerInfo(**defaults)


def _make_test_image(w=100, h=100):
    return Image.new("RGB", (w, h), (200, 150, 100))


def _top_half_mask(h=100, w=100):
    m = np.zeros((h, w), dtype=bool)
    m[: h // 2, :] = True
    return m


def _bottom_half_mask(h=100, w=100):
    m = np.zeros((h, w), dtype=bool)
    m[h // 2 :, :] = True
    return m


def _setup_sam3_mocks(masks_per_call):
    """Create mock model + processor that return masks in order."""
    call_idx = [0]
    captured_texts = []

    # Mock processor instance
    mock_proc_instance = MagicMock()

    # processor(images=..., text=...) returns inputs
    mock_inputs = MagicMock()
    mock_inputs.to = MagicMock(return_value=mock_inputs)

    def _proc_call(*args, **kwargs):
        text = kwargs.get("text", "")
        captured_texts.append(text)
        return mock_inputs

    mock_proc_instance.side_effect = _proc_call
    mock_proc_instance._captured_texts = captured_texts

    # post_process returns masks in sequence
    def _post_process(outputs, threshold=0.5, **kw):
        idx = call_idx[0]
        call_idx[0] += 1
        if idx < len(masks_per_call):
            return [{"masks": [masks_per_call[idx]], "scores": [0.95]}]
        return [{"masks": [], "scores": []}]

    mock_proc_instance.post_process_instance_segmentation = MagicMock(
        side_effect=_post_process
    )

    # Mock model instance
    mock_model_instance = MagicMock()
    mock_model_instance.to = MagicMock(return_value=mock_model_instance)
    mock_model_instance.eval = MagicMock(return_value=mock_model_instance)
    mock_outputs = MagicMock()
    mock_model_instance.return_value = mock_outputs

    # Mock classes (Sam3Model, Sam3Processor)
    mock_model_cls = MagicMock()
    mock_model_cls.from_pretrained = MagicMock(return_value=mock_model_instance)

    mock_proc_cls = MagicMock()
    mock_proc_cls.from_pretrained = MagicMock(return_value=mock_proc_instance)

    return mock_model_cls, mock_proc_cls, mock_model_instance, mock_proc_instance


# ---------------------------------------------------------------------------
# Test 1: sam3_split returns RGBA layers
# ---------------------------------------------------------------------------

def test_sam3_returns_rgba_layers(tmp_path):
    """Two layers (fg+bg), mock returns top-half mask for fg → both RGBA 100x100."""
    img = _make_test_image(100, 100)
    img_path = str(tmp_path / "source.png")
    img.save(img_path)

    fg = _make_layer("fg", z=1, content_type="subject", description="foreground subject")
    bg = _make_layer("bg", z=0, content_type="background", description="background sky")

    mask_fg = _top_half_mask()
    mock_model_cls, mock_proc_cls, _, _ = _setup_sam3_mocks([mask_fg])

    with patch.object(sam3_module, "Sam3Model", mock_model_cls), \
         patch.object(sam3_module, "Sam3Processor", mock_proc_cls), \
         patch.object(sam3_module, "SAM3_AVAILABLE", True), \
         patch("torch.cuda.is_available", return_value=False):
        results = sam3_split(img_path, [fg, bg], output_dir=str(tmp_path))

    assert len(results) == 2

    for r in results:
        out_img = Image.open(r.image_path)
        assert out_img.mode == "RGBA"
        assert out_img.size == (100, 100)


# ---------------------------------------------------------------------------
# Test 2: sam3_split uses info.description as text prompt
# ---------------------------------------------------------------------------

def test_sam3_uses_description_as_text_prompt(tmp_path):
    """Verify mock processor was called with info.description as text."""
    img = _make_test_image(100, 100)
    img_path = str(tmp_path / "source.png")
    img.save(img_path)

    fg = _make_layer("fg", z=1, content_type="subject", description="a red mountain peak")
    bg = _make_layer("bg", z=0, content_type="background")

    mask_fg = _top_half_mask()
    mock_model_cls, mock_proc_cls, _, mock_proc_instance = _setup_sam3_mocks([mask_fg])

    with patch.object(sam3_module, "Sam3Model", mock_model_cls), \
         patch.object(sam3_module, "Sam3Processor", mock_proc_cls), \
         patch.object(sam3_module, "SAM3_AVAILABLE", True), \
         patch("torch.cuda.is_available", return_value=False):
        sam3_split(img_path, [fg, bg], output_dir=str(tmp_path))

    captured = mock_proc_instance._captured_texts
    assert "a red mountain peak" in captured


# ---------------------------------------------------------------------------
# Test 3: exclusive assignment — z=2 wins top half when both claim it
# ---------------------------------------------------------------------------

def test_sam3_exclusive_assignment(tmp_path):
    """Two fg layers both claim top half; higher z_index layer wins."""
    img = _make_test_image(100, 100)
    img_path = str(tmp_path / "source.png")
    img.save(img_path)

    fg_high = _make_layer("high", z=2, content_type="subject", description="high priority")
    fg_low = _make_layer("low", z=1, content_type="subject", description="low priority")

    # Both mocks return top-half mask; high z processed first, low z gets nothing
    top = _top_half_mask()
    mock_model_cls, mock_proc_cls, _, _ = _setup_sam3_mocks([top, top])

    with patch.object(sam3_module, "Sam3Model", mock_model_cls), \
         patch.object(sam3_module, "Sam3Processor", mock_proc_cls), \
         patch.object(sam3_module, "SAM3_AVAILABLE", True), \
         patch("torch.cuda.is_available", return_value=False):
        results = sam3_split(img_path, [fg_high, fg_low], output_dir=str(tmp_path))

    # high layer: top half should be opaque
    high_result = next(r for r in results if r.info.name == "high")
    high_img = Image.open(high_result.image_path).convert("RGBA")
    alpha_top = np.array(high_img)[:50, :, 3]
    assert alpha_top.mean() > 200, "high z_index layer should own the top half"

    # low layer: top half claimed by high, should be transparent there
    low_result = next(r for r in results if r.info.name == "low")
    low_img = Image.open(low_result.image_path).convert("RGBA")
    alpha_low_top = np.array(low_img)[:50, :, 3]
    assert alpha_low_top.mean() == 0, "low z_index layer loses pixels to high z_index"


# ---------------------------------------------------------------------------
# Test 4: background gets unclaimed pixels
# ---------------------------------------------------------------------------

def test_background_gets_unclaimed(tmp_path):
    """Foreground claims top half → background gets bottom half."""
    img = _make_test_image(100, 100)
    img_path = str(tmp_path / "source.png")
    img.save(img_path)

    fg = _make_layer("fg", z=1, content_type="subject", description="foreground obj")
    bg = _make_layer("bg", z=0, content_type="background")

    mask_fg = _top_half_mask()
    mock_model_cls, mock_proc_cls, _, _ = _setup_sam3_mocks([mask_fg])

    with patch.object(sam3_module, "Sam3Model", mock_model_cls), \
         patch.object(sam3_module, "Sam3Processor", mock_proc_cls), \
         patch.object(sam3_module, "SAM3_AVAILABLE", True), \
         patch("torch.cuda.is_available", return_value=False):
        results = sam3_split(img_path, [fg, bg], output_dir=str(tmp_path))

    bg_result = next(r for r in results if r.info.name == "bg")
    bg_img = Image.open(bg_result.image_path).convert("RGBA")
    bg_arr = np.array(bg_img)

    # Bottom half should be opaque (claimed by bg)
    alpha_bottom = bg_arr[50:, :, 3]
    assert alpha_bottom.mean() > 200, "background should own bottom half"

    # Top half should be transparent (claimed by fg)
    alpha_top = bg_arr[:50, :, 3]
    assert alpha_top.mean() == 0, "background should not have top half pixels"


# ---------------------------------------------------------------------------
# Test 5: not installed raises ImportError
# ---------------------------------------------------------------------------

def test_sam3_not_installed_raises_import_error(tmp_path):
    """When SAM3_AVAILABLE is False, sam3_split raises ImportError."""
    img = _make_test_image()
    img_path = str(tmp_path / "source.png")
    img.save(img_path)

    fg = _make_layer("fg", z=1, content_type="subject")

    with patch.object(sam3_module, "SAM3_AVAILABLE", False):
        with pytest.raises(ImportError, match="sam3"):
            sam3_split(img_path, [fg], output_dir=str(tmp_path))


# ---------------------------------------------------------------------------
# Test 6: manifest split_mode is "sam3"
# ---------------------------------------------------------------------------

def test_manifest_split_mode_sam3(tmp_path):
    """Manifest JSON written by sam3_split has split_mode='sam3'."""
    img = _make_test_image(100, 100)
    img_path = str(tmp_path / "source.png")
    img.save(img_path)

    fg = _make_layer("fg", z=1, content_type="subject", description="subject")
    bg = _make_layer("bg", z=0, content_type="background")

    mask_fg = _top_half_mask()
    mock_model_cls, mock_proc_cls, _, _ = _setup_sam3_mocks([mask_fg])

    with patch.object(sam3_module, "Sam3Model", mock_model_cls), \
         patch.object(sam3_module, "Sam3Processor", mock_proc_cls), \
         patch.object(sam3_module, "SAM3_AVAILABLE", True), \
         patch("torch.cuda.is_available", return_value=False):
        sam3_split(img_path, [fg, bg], output_dir=str(tmp_path))

    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["split_mode"] == "sam3"


# ---------------------------------------------------------------------------
# Test 7: model is NOT called for background layers
# ---------------------------------------------------------------------------

def test_no_model_call_for_background(tmp_path):
    """Model forward pass is called only for non-background layers."""
    img = _make_test_image(100, 100)
    img_path = str(tmp_path / "source.png")
    img.save(img_path)

    fg = _make_layer("fg", z=1, content_type="subject", description="subject")
    bg = _make_layer("bg", z=0, content_type="background")

    mask_fg = _top_half_mask()
    mock_model_cls, mock_proc_cls, mock_model_instance, mock_proc_instance = _setup_sam3_mocks(
        [mask_fg]
    )

    with patch.object(sam3_module, "Sam3Model", mock_model_cls), \
         patch.object(sam3_module, "Sam3Processor", mock_proc_cls), \
         patch.object(sam3_module, "SAM3_AVAILABLE", True), \
         patch("torch.cuda.is_available", return_value=False):
        sam3_split(img_path, [fg, bg], output_dir=str(tmp_path))

    # processor was called once (for fg), not twice
    assert len(mock_proc_instance._captured_texts) == 1
    # model forward was called once
    assert mock_model_instance.call_count == 1


# ---------------------------------------------------------------------------
# Test 8: SAM3_AVAILABLE is a bool
# ---------------------------------------------------------------------------

def test_sam3_available_is_bool():
    """SAM3_AVAILABLE must be a boolean (not truthy/falsy accident)."""
    assert isinstance(sam3_module.SAM3_AVAILABLE, bool)


class TestSam3Export:
    """sam3_split is importable from vulca.layers."""

    def test_import_from_layers_package(self):
        from vulca.layers import sam3_split
        assert callable(sam3_split)

    def test_sam3_available_exported(self):
        from vulca.layers import SAM3_AVAILABLE
        assert isinstance(SAM3_AVAILABLE, bool)


class TestSam3CLI:
    """CLI --mode sam3 is wired up."""

    def test_sam3_mode_in_cli_help(self):
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, "-m", "vulca", "layers", "split", "--help"],
            capture_output=True, text=True, timeout=30,
        )
        assert "sam3" in result.stdout, f"'sam3' not in CLI help:\n{result.stdout}"


class TestSam3MCP:
    """MCP layers_split supports mode='sam3'."""

    def test_mcp_docstring_mentions_sam3(self):
        from vulca.mcp_server import layers_split
        assert "sam3" in layers_split.__doc__
