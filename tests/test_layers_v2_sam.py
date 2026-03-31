"""Tests for vulca.layers.sam — SAM2 optional integration."""
from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from vulca.layers.sam import SAM_AVAILABLE, sam_split
from vulca.layers.types import LayerInfo, LayerResult


# Module-level skip marker for SAM-dependent tests
_sam_skip = pytest.mark.skipif(not SAM_AVAILABLE, reason="SAM2 not installed")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_solid_image(size: int = 256, color: tuple = (128, 64, 32)) -> Image.Image:
    """Create a solid-color RGB image."""
    arr = np.full((size, size, 3), color, dtype=np.uint8)
    return Image.fromarray(arr, mode="RGB")


def _save_temp(img: Image.Image, path: Path) -> str:
    img.save(str(path))
    return str(path)


# ---------------------------------------------------------------------------
# TestSAMImportGuard — always runs (no skipif marker)
# ---------------------------------------------------------------------------

class TestSAMImportGuard:
    """Import-guard tests — run regardless of SAM2 installation."""

    def test_sam_available_flag(self):
        """SAM_AVAILABLE must be a bool."""
        assert isinstance(SAM_AVAILABLE, bool), (
            f"SAM_AVAILABLE must be bool, got {type(SAM_AVAILABLE)}"
        )

    def test_sam_split_without_sam_raises(self):
        """If SAM2 is not installed, sam_split must raise ImportError mentioning 'SAM'."""
        if SAM_AVAILABLE:
            pytest.skip("SAM2 is installed — import guard test not applicable")

        layers = [
            LayerInfo(
                name="bg",
                description="background",
                z_index=0,
                content_type="background",
            )
        ]

        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            _make_solid_image().save(str(src))

            with pytest.raises(ImportError, match="SAM"):
                sam_split(str(src), layers, output_dir=td)


# ---------------------------------------------------------------------------
# TestSAMSplit — skipped if SAM2 not installed
# ---------------------------------------------------------------------------

@_sam_skip
class TestSAMSplit:
    """Functional tests for sam_split — require SAM2 to be installed."""

    def test_sam_produces_full_canvas_rgba(self):
        """sam_split → all layers are full-canvas RGBA images."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_solid_image(256)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="subject",
                    description="main subject",
                    z_index=1,
                    content_type="subject",
                ),
                LayerInfo(
                    name="background",
                    description="background",
                    z_index=0,
                    content_type="background",
                ),
            ]

            results = sam_split(str(src), layers, output_dir=td)

            assert len(results) == len(layers), (
                f"Expected {len(layers)} LayerResults, got {len(results)}"
            )

            for result in results:
                assert isinstance(result, LayerResult), "Each result must be a LayerResult"
                layer_img = Image.open(result.image_path)
                # Full-canvas: same dimensions as source
                assert layer_img.size == (256, 256), (
                    f"Layer '{result.info.name}' must be 256×256, got {layer_img.size}"
                )
                # Must be RGBA
                assert layer_img.mode == "RGBA", (
                    f"Layer '{result.info.name}' must be RGBA, got {layer_img.mode}"
                )

    def test_sam_results_sorted_by_z_index(self):
        """sam_split results must be sorted by z_index ascending."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_solid_image(256)
            img.save(str(src))

            layers = [
                LayerInfo(name="top", description="top", z_index=5, content_type="subject"),
                LayerInfo(name="mid", description="mid", z_index=3, content_type="subject"),
                LayerInfo(name="bg", description="bg", z_index=0, content_type="background"),
            ]

            results = sam_split(str(src), layers, output_dir=td)
            z_indices = [r.info.z_index for r in results]
            assert z_indices == sorted(z_indices), (
                f"Results must be sorted ascending by z_index, got {z_indices}"
            )

    def test_sam_writes_manifest(self):
        """sam_split must write manifest.json with split_mode='sam'."""
        import json

        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_solid_image(256)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="layer0",
                    description="only layer",
                    z_index=0,
                    content_type="background",
                ),
            ]

            sam_split(str(src), layers, output_dir=td)

            manifest_path = Path(td) / "manifest.json"
            assert manifest_path.exists(), "manifest.json must be created by sam_split"

            manifest = json.loads(manifest_path.read_text())
            assert manifest.get("split_mode") == "sam"
            assert manifest.get("version") == 2
            assert manifest.get("width") == 256
            assert manifest.get("height") == 256
