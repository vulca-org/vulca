"""Tests for vulca.layers.split — V2 split modes (extract + regenerate)."""
from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from vulca.layers.split import split_extract, split_regenerate
from vulca.layers.types import LayerInfo, LayerResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_red_blue_image(size: int = 100) -> Image.Image:
    """Create a 100×100 RGB image: left half red, right half blue."""
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    arr[:, : size // 2] = (220, 30, 30)   # red
    arr[:, size // 2 :] = (30, 30, 220)   # blue
    return Image.fromarray(arr, mode="RGB")


def _save_temp(img: Image.Image, path: Path) -> str:
    img.save(str(path))
    return str(path)


# ---------------------------------------------------------------------------
# TestSplitExtract
# ---------------------------------------------------------------------------

class TestSplitExtract:

    def test_produces_full_canvas_rgba(self):
        """split_extract → both layers are full-canvas RGBA images."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_red_blue_image(100)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="red_layer",
                    description="red subject",
                    z_index=0,
                    content_type="subject",
                    dominant_colors=["#DC1E1E"],
                ),
                LayerInfo(
                    name="blue_layer",
                    description="blue subject",
                    z_index=1,
                    content_type="subject",
                    dominant_colors=["#1E1EDC"],
                ),
            ]

            results = split_extract(str(src), layers, output_dir=td, tolerance=30)

            assert len(results) == 2

            for result in results:
                assert isinstance(result, LayerResult), "Each result must be a LayerResult"
                layer_img = Image.open(result.image_path)
                # Full-canvas: same size as original
                assert layer_img.size == (100, 100), (
                    f"Layer {result.info.name} must be full-canvas 100×100, got {layer_img.size}"
                )
                # Must be RGBA
                assert layer_img.mode == "RGBA", (
                    f"Layer {result.info.name} must be RGBA, got {layer_img.mode}"
                )

    def test_extract_red_layer_has_red_opaque(self):
        """Red-dominant layer: red pixels should be opaque, blue pixels transparent."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_red_blue_image(100)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="red_layer",
                    description="red subject",
                    z_index=0,
                    content_type="subject",
                    dominant_colors=["#DC1E1E"],  # close to (220, 30, 30)
                ),
            ]

            results = split_extract(str(src), layers, output_dir=td, tolerance=30)
            assert len(results) == 1

            layer_img = Image.open(results[0].image_path)
            arr = np.array(layer_img)  # H × W × 4 (RGBA)

            # Left half (red region) — alpha should be substantially opaque
            left_alpha = arr[:, :50, 3].astype(float)
            # Right half (blue region) — alpha should be substantially transparent
            right_alpha = arr[:, 50:, 3].astype(float)

            assert left_alpha.mean() > right_alpha.mean() + 30, (
                f"Red region (mean alpha={left_alpha.mean():.1f}) should be more opaque "
                f"than blue region (mean alpha={right_alpha.mean():.1f})"
            )

    def test_writes_manifest(self):
        """split_extract must create manifest.json in output_dir."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_red_blue_image(100)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="bg",
                    description="background",
                    z_index=0,
                    content_type="background",
                    dominant_colors=["#DC1E1E"],
                ),
            ]

            split_extract(str(src), layers, output_dir=td)

            manifest_path = Path(td) / "manifest.json"
            assert manifest_path.exists(), "manifest.json must be created in output_dir"

            manifest = json.loads(manifest_path.read_text())
            # V2 manifest
            assert manifest.get("version") == 3
            assert manifest.get("width") == 100
            assert manifest.get("height") == 100
            assert len(manifest.get("layers", [])) == 1
            assert manifest["layers"][0]["name"] == "bg"

    def test_sorted_by_z_index(self):
        """Results must be sorted by z_index ascending."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_red_blue_image(100)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="top",
                    description="top layer",
                    z_index=2,
                    content_type="subject",
                    dominant_colors=["#DC1E1E"],
                ),
                LayerInfo(
                    name="bottom",
                    description="bottom layer",
                    z_index=0,
                    content_type="background",
                    dominant_colors=["#1E1EDC"],
                ),
            ]

            results = split_extract(str(src), layers, output_dir=td)
            z_indices = [r.info.z_index for r in results]
            assert z_indices == sorted(z_indices), "Results must be sorted by z_index"


# ---------------------------------------------------------------------------
# TestSplitRegenerate
# ---------------------------------------------------------------------------

class TestSplitRegenerate:

    def test_split_regenerate_mock(self):
        """Mock provider: 1 layer file created + LayerResult returned."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_red_blue_image(100)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="background",
                    description="background layer",
                    z_index=0,
                    content_type="background",
                    dominant_colors=["#DC1E1E"],
                    regeneration_prompt="background layer on transparent canvas",
                ),
            ]

            results = asyncio.run(
                split_regenerate(
                    str(src),
                    layers,
                    output_dir=td,
                    provider="mock",
                    tradition="chinese_xieyi",
                )
            )

            # At least 1 result returned
            assert len(results) == 1, f"Expected 1 LayerResult, got {len(results)}"

            result = results[0]
            assert isinstance(result, LayerResult), "Result must be LayerResult"

            # File must exist on disk
            assert Path(result.image_path).exists(), (
                f"Layer file {result.image_path} must exist"
            )

            # Saved image must be RGBA and full-canvas
            layer_img = Image.open(result.image_path)
            assert layer_img.mode == "RGBA", f"Layer must be RGBA, got {layer_img.mode}"
            assert layer_img.size == (100, 100), (
                f"Layer must be full-canvas 100×100, got {layer_img.size}"
            )

    def test_split_regenerate_writes_manifest(self):
        """Mock provider: manifest.json is written after regeneration."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_red_blue_image(100)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="sky",
                    description="sky layer",
                    z_index=0,
                    content_type="background",
                    dominant_colors=["#1E1EDC"],
                ),
            ]

            asyncio.run(
                split_regenerate(
                    str(src),
                    layers,
                    output_dir=td,
                    provider="mock",
                )
            )

            manifest_path = Path(td) / "manifest.json"
            assert manifest_path.exists(), "manifest.json must be written by split_regenerate"

            manifest = json.loads(manifest_path.read_text())
            assert manifest.get("split_mode") == "regenerate"
            assert manifest.get("version") == 3
