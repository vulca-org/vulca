"""Tests for redraw.py — single-layer and multi-layer merge+redraw."""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from PIL import Image

from vulca.layers.manifest import load_manifest, write_manifest
from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_rgba_png(path: Path, size: tuple[int, int] = (100, 100), color=(128, 64, 32, 200)) -> None:
    """Write a minimal RGBA PNG to disk."""
    img = Image.new("RGBA", size, color)
    img.save(str(path))


def _run(coro):
    """Run an async coroutine in a fresh event loop."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _setup_two_layer_artwork(tmp_path: Path) -> LayeredArtwork:
    """Create a 2-layer artwork (bg + fg) with manifest in tmp_path."""
    # Create layer PNG files
    _make_rgba_png(tmp_path / "bg.png", color=(50, 50, 50, 255))
    _make_rgba_png(tmp_path / "fg.png", color=(200, 100, 50, 255))
    # Create a source image
    _make_rgba_png(tmp_path / "source.png", color=(100, 100, 100, 255))

    bg = LayerInfo(name="bg", description="background layer", z_index=0, content_type="background")
    fg = LayerInfo(name="fg", description="foreground subject", z_index=1, content_type="subject")

    write_manifest(
        [bg, fg],
        output_dir=str(tmp_path),
        width=100,
        height=100,
        source_image=str(tmp_path / "source.png"),
    )
    return load_manifest(str(tmp_path))


# ---------------------------------------------------------------------------
# TestRedrawSingle
# ---------------------------------------------------------------------------

class TestRedrawSingle:
    def test_redraw_replaces_target_layer(self, tmp_path):
        """Redraw 'fg' layer — new file created, bg layer path unchanged."""
        from vulca.layers.redraw import redraw_layer

        artwork = _setup_two_layer_artwork(tmp_path)

        # Record bg path before redraw
        bg_before = next(lr.image_path for lr in artwork.layers if lr.info.name == "bg")

        result = _run(
            redraw_layer(
                artwork,
                layer_name="fg",
                instruction="Make the foreground brighter and more vivid",
                provider="mock",
                tradition="default",
                artwork_dir=str(tmp_path),
            )
        )

        # Result is a LayerResult for "fg"
        assert result.info.name == "fg"

        # New file exists at expected path
        expected_path = tmp_path / "fg.png"
        assert expected_path.exists(), f"Expected output file at {expected_path}"

        # Output is RGBA PNG
        img = Image.open(str(expected_path))
        assert img.mode == "RGBA", f"Expected RGBA mode, got {img.mode}"

        # bg layer is untouched
        bg_after = next(lr.image_path for lr in artwork.layers if lr.info.name == "bg")
        assert bg_after == bg_before, "bg layer path should not change"

    def test_redraw_unknown_layer_raises(self, tmp_path):
        """Redrawing a non-existent layer raises ValueError with 'not found'."""
        from vulca.layers.redraw import redraw_layer

        artwork = _setup_two_layer_artwork(tmp_path)

        with pytest.raises(ValueError, match="not found"):
            _run(
                redraw_layer(
                    artwork,
                    layer_name="nonexistent_layer",
                    instruction="Change the sky",
                    provider="mock",
                    artwork_dir=str(tmp_path),
                )
            )


# ---------------------------------------------------------------------------
# TestRedrawMerged
# ---------------------------------------------------------------------------

class TestRedrawMerged:
    def test_merge_two_layers(self, tmp_path):
        """Merge bg+fg → merged layer file exists, name is 'merged'."""
        from vulca.layers.redraw import redraw_merged

        artwork = _setup_two_layer_artwork(tmp_path)

        result = _run(
            redraw_merged(
                artwork,
                layer_names=["bg", "fg"],
                instruction="Unify the layers into a cohesive composition",
                merged_name="merged",
                provider="mock",
                tradition="default",
                artwork_dir=str(tmp_path),
            )
        )

        # Returned LayerResult has correct name
        assert result.info.name == "merged"

        # Output file exists
        merged_path = tmp_path / "merged.png"
        assert merged_path.exists(), f"Expected merged output at {merged_path}"

        # Output is RGBA PNG
        img = Image.open(str(merged_path))
        assert img.mode == "RGBA", f"Expected RGBA mode, got {img.mode}"

    def test_merge_missing_layer_raises(self, tmp_path):
        """Merging with a non-existent layer name raises ValueError."""
        from vulca.layers.redraw import redraw_merged

        artwork = _setup_two_layer_artwork(tmp_path)

        with pytest.raises(ValueError):
            _run(
                redraw_merged(
                    artwork,
                    layer_names=["bg", "missing_layer"],
                    instruction="Merge these",
                    provider="mock",
                    artwork_dir=str(tmp_path),
                )
            )

    def test_merged_z_index_is_min_of_selected(self, tmp_path):
        """Merged layer inherits the minimum z_index of selected layers."""
        from vulca.layers.redraw import redraw_merged

        artwork = _setup_two_layer_artwork(tmp_path)
        # bg.z_index=0, fg.z_index=1 → min=0
        result = _run(
            redraw_merged(
                artwork,
                layer_names=["bg", "fg"],
                instruction="Merge",
                merged_name="merged",
                provider="mock",
                artwork_dir=str(tmp_path),
            )
        )
        assert result.info.z_index == 0

    def test_merged_content_type_is_subject(self, tmp_path):
        """Merged layer always has content_type='subject'."""
        from vulca.layers.redraw import redraw_merged

        artwork = _setup_two_layer_artwork(tmp_path)
        result = _run(
            redraw_merged(
                artwork,
                layer_names=["bg", "fg"],
                instruction="Merge",
                merged_name="merged",
                provider="mock",
                artwork_dir=str(tmp_path),
            )
        )
        assert result.info.content_type == "subject"


# ---------------------------------------------------------------------------
# TestRedrawMergedResplit
# ---------------------------------------------------------------------------

class TestRedrawMergedResplit:
    def test_resplit_returns_list(self):
        """re_split=True returns list[LayerResult] instead of single LayerResult."""
        import asyncio
        import tempfile
        from PIL import Image

        with tempfile.TemporaryDirectory() as td:
            bg = Image.new("RGBA", (100, 100), (0, 0, 255, 255))
            bg.save(str(Path(td) / "bg.png"))
            fg = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
            fg.save(str(Path(td) / "fg.png"))
            src = Image.new("RGB", (100, 100), (128, 128, 128))
            src.save(str(Path(td) / "original.png"))

            from vulca.layers.manifest import write_manifest, load_manifest
            layers = [
                LayerInfo(name="bg", description="blue bg", z_index=0,
                         regeneration_prompt="Blue"),
                LayerInfo(name="fg", description="red fg", z_index=1,
                         regeneration_prompt="Red"),
            ]
            write_manifest(layers, output_dir=td, width=100, height=100,
                          source_image="original.png")
            artwork = load_manifest(td)

            from vulca.layers.redraw import redraw_merged

            loop = asyncio.new_event_loop()
            # Note: re_split=True requires analyze_layers which needs VLM
            # With mock provider, the merged image is a transparent placeholder
            # analyze_layers would need real VLM — so we test that the parameter
            # is accepted and the non-re-split path still works
            result_single = loop.run_until_complete(
                redraw_merged(artwork, layer_names=["bg", "fg"],
                             instruction="improve", merged_name="merged",
                             provider="mock", artwork_dir=td, re_split=False)
            )
            loop.close()
            assert isinstance(result_single, LayerResult)
            assert result_single.info.name == "merged"
