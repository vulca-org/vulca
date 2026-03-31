"""Tests for CRITICAL gaps found by coverage audit.

All tests written RED-first — expected to FAIL before fix.
"""
import asyncio
import json
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from vulca.layers.types import LayerInfo, LayerResult
from vulca.layers.manifest import write_manifest, load_manifest
from vulca.layers.ops import (
    add_layer, remove_layer, merge_layers, duplicate_layer, lock_layer,
)


def _setup(td, n=3):
    """Create N-layer artwork in temp dir."""
    infos = []
    for i in range(n):
        name = f"layer_{i}"
        img = Image.new("RGBA", (50, 50), (i * 80, 0, 0, 255))
        img.save(str(Path(td) / f"{name}.png"))
        infos.append(LayerInfo(name=name, description=f"layer {i}", z_index=i))
    write_manifest(infos, output_dir=td, width=50, height=50)


# ===========================================================================
# CRITICAL #1: merge_layers should refuse locked layers
# ===========================================================================

class TestMergeLockedLayers:
    def test_merge_with_locked_layer_raises(self):
        """Merging a locked layer should raise ValueError, not silently delete it."""
        with tempfile.TemporaryDirectory() as td:
            _setup(td, 3)
            artwork = load_manifest(td)

            # Lock layer_1
            lock_layer(artwork, artwork_dir=td, layer_name="layer_1", locked=True)
            artwork = load_manifest(td)

            with pytest.raises(ValueError, match="locked"):
                merge_layers(artwork, artwork_dir=td,
                            layer_names=["layer_0", "layer_1"],
                            merged_name="merged")

    def test_merge_without_locked_succeeds(self):
        """Merging unlocked layers should work normally."""
        with tempfile.TemporaryDirectory() as td:
            _setup(td, 3)
            artwork = load_manifest(td)
            result = merge_layers(artwork, artwork_dir=td,
                                 layer_names=["layer_0", "layer_1"],
                                 merged_name="merged")
            assert result.info.name == "merged"


# ===========================================================================
# CRITICAL #2: duplicate with missing source file
# ===========================================================================

class TestDuplicateMissingFile:
    def test_duplicate_missing_source_raises_clear_error(self):
        """Duplicate when source PNG doesn't exist should raise FileNotFoundError."""
        with tempfile.TemporaryDirectory() as td:
            _setup(td, 2)
            artwork = load_manifest(td)

            # Delete the source file
            (Path(td) / "layer_0.png").unlink()

            with pytest.raises(FileNotFoundError):
                duplicate_layer(artwork, artwork_dir=td,
                               layer_name="layer_0", new_name="copy")


# ===========================================================================
# CRITICAL #3: _read_dimensions / _save_artwork without manifest
# ===========================================================================

class TestOpsWithoutManifest:
    def test_add_layer_to_empty_dir_raises(self):
        """add_layer on dir without manifest.json should raise FileNotFoundError."""
        from vulca.layers.types import LayeredArtwork
        with tempfile.TemporaryDirectory() as td:
            artwork = LayeredArtwork(
                composite_path="", layers=[], manifest_path="",
            )
            with pytest.raises(FileNotFoundError):
                add_layer(artwork, artwork_dir=td, name="test", description="test")
