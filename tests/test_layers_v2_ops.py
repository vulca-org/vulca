"""Tests for layer editing operations (ops.py)."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from vulca.layers.manifest import load_manifest, write_manifest
from vulca.layers.ops import (
    add_layer,
    duplicate_layer,
    lock_layer,
    merge_layers,
    remove_layer,
    reorder_layer,
    toggle_visibility,
)
from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork


# ---------------------------------------------------------------------------
# Test helper
# ---------------------------------------------------------------------------

def _setup_artwork(td: str, layer_count: int = 3) -> str:
    """Create test artwork: background(blue,z=0), midground(green,z=1), foreground(red,z=2)."""
    names = ["background", "midground", "foreground"][:layer_count]
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)][:layer_count]
    infos = []
    for i, (name, (r, g, b)) in enumerate(zip(names, colors)):
        img = Image.new("RGBA", (100, 100), (r, g, b, 255))
        img.save(str(Path(td) / f"{name}.png"))
        infos.append(
            LayerInfo(
                name=name,
                description=f"{name} layer",
                z_index=i,
                content_type="background" if i == 0 else "subject",
            )
        )
    write_manifest(infos, output_dir=td, width=100, height=100, source_image="orig.png")
    return td


# ---------------------------------------------------------------------------
# TestAddLayer
# ---------------------------------------------------------------------------

class TestAddLayer:
    def test_add_creates_transparent_rgba_png_at_correct_size(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        result = add_layer(artwork, artwork_dir=td, name="overlay")

        png_path = Path(result.image_path)
        assert png_path.exists(), "PNG file should be created"
        img = Image.open(str(png_path))
        assert img.mode == "RGBA", "Layer must be RGBA"
        assert img.size == (100, 100), "Layer size must match manifest dimensions"
        # All pixels should be fully transparent
        pixels = list(img.getdata())
        assert all(p[3] == 0 for p in pixels), "New layer must be fully transparent"

    def test_add_updates_manifest(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        add_layer(artwork, artwork_dir=td, name="overlay")

        # Reload from disk and verify
        reloaded = load_manifest(td)
        names = [lr.info.name for lr in reloaded.layers]
        assert "overlay" in names, "Manifest should include new layer after reload"

    def test_add_duplicate_name_raises(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        with pytest.raises(ValueError, match="already exists"):
            add_layer(artwork, artwork_dir=td, name="background")

    def test_add_default_z_index_is_top(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        result = add_layer(artwork, artwork_dir=td, name="topmost")
        assert result.info.z_index == 3, "Default z_index=-1 should place layer at top (z=3)"

    def test_add_explicit_z_index(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        result = add_layer(artwork, artwork_dir=td, name="inserted", z_index=1)
        assert result.info.z_index == 1


# ---------------------------------------------------------------------------
# TestRemoveLayer
# ---------------------------------------------------------------------------

class TestRemoveLayer:
    def test_remove_deletes_file_and_removes_from_manifest(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        bg_path = Path(td) / "background.png"
        assert bg_path.exists()

        remove_layer(artwork, artwork_dir=td, layer_name="background")

        assert not bg_path.exists(), "PNG file should be deleted"
        reloaded = load_manifest(td)
        names = [lr.info.name for lr in reloaded.layers]
        assert "background" not in names, "Layer should be removed from manifest"

    def test_remove_locked_layer_raises(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        # First lock the layer
        lock_layer(artwork, artwork_dir=td, layer_name="midground", locked=True)

        with pytest.raises(ValueError, match="locked"):
            remove_layer(artwork, artwork_dir=td, layer_name="midground")

    def test_remove_nonexistent_raises(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        with pytest.raises(ValueError, match="not found"):
            remove_layer(artwork, artwork_dir=td, layer_name="nonexistent")


# ---------------------------------------------------------------------------
# TestReorderLayer
# ---------------------------------------------------------------------------

class TestReorderLayer:
    def test_reorder_changes_target_z_index(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        reorder_layer(artwork, artwork_dir=td, layer_name="foreground", new_z_index=0)

        reloaded = load_manifest(td)
        fg = next(lr for lr in reloaded.layers if lr.info.name == "foreground")
        assert fg.info.z_index == 0

    def test_reorder_shifts_other_layers(self, tmp_path):
        """Move foreground (z=2) to z=0 → others shift to 1, 2."""
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        reorder_layer(artwork, artwork_dir=td, layer_name="foreground", new_z_index=0)

        reloaded = load_manifest(td)
        z_map = {lr.info.name: lr.info.z_index for lr in reloaded.layers}
        assert z_map["foreground"] == 0
        # Remaining layers should have z_indices 1 and 2 (sequential)
        other_z = sorted(z_map[n] for n in ["background", "midground"])
        assert other_z == [1, 2], f"Others should be sequential: {z_map}"

    def test_reorder_all_z_indices_are_sequential(self, tmp_path):
        """After reorder, z_indices should be 0, 1, 2 (no gaps)."""
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        reorder_layer(artwork, artwork_dir=td, layer_name="midground", new_z_index=2)

        reloaded = load_manifest(td)
        z_values = sorted(lr.info.z_index for lr in reloaded.layers)
        assert z_values == [0, 1, 2], f"Z indices should be sequential: {z_values}"


# ---------------------------------------------------------------------------
# TestToggleVisibility
# ---------------------------------------------------------------------------

class TestToggleVisibility:
    def test_toggle_off_persists(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        toggle_visibility(artwork, artwork_dir=td, layer_name="midground", visible=False)

        reloaded = load_manifest(td)
        mid = next(lr for lr in reloaded.layers if lr.info.name == "midground")
        assert mid.info.visible is False

    def test_toggle_on_persists(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        # First toggle off, then back on
        toggle_visibility(artwork, artwork_dir=td, layer_name="background", visible=False)
        toggle_visibility(artwork, artwork_dir=td, layer_name="background", visible=True)

        reloaded = load_manifest(td)
        bg = next(lr for lr in reloaded.layers if lr.info.name == "background")
        assert bg.info.visible is True


# ---------------------------------------------------------------------------
# TestLockLayer
# ---------------------------------------------------------------------------

class TestLockLayer:
    def test_lock_persists(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        lock_layer(artwork, artwork_dir=td, layer_name="foreground", locked=True)

        reloaded = load_manifest(td)
        fg = next(lr for lr in reloaded.layers if lr.info.name == "foreground")
        assert fg.info.locked is True

    def test_unlock_persists(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        lock_layer(artwork, artwork_dir=td, layer_name="foreground", locked=True)
        lock_layer(artwork, artwork_dir=td, layer_name="foreground", locked=False)

        reloaded = load_manifest(td)
        fg = next(lr for lr in reloaded.layers if lr.info.name == "foreground")
        assert fg.info.locked is False


# ---------------------------------------------------------------------------
# TestMergeLayers
# ---------------------------------------------------------------------------

class TestMergeLayers:
    def test_merge_creates_combined_png(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        result = merge_layers(
            artwork,
            artwork_dir=td,
            layer_names=["background", "midground"],
            merged_name="bg_mid_merged",
        )

        merged_path = Path(result.image_path)
        assert merged_path.exists(), "Merged PNG must be created"
        img = Image.open(str(merged_path))
        assert img.mode == "RGBA", "Merged layer must be RGBA"
        assert img.size == (100, 100), "Merged layer must match artwork dimensions"

    def test_merge_removes_source_layers_from_manifest(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        merge_layers(
            artwork,
            artwork_dir=td,
            layer_names=["background", "midground"],
            merged_name="combined",
        )

        reloaded = load_manifest(td)
        names = [lr.info.name for lr in reloaded.layers]
        assert "background" not in names, "Source layer background should be removed"
        assert "midground" not in names, "Source layer midground should be removed"
        assert "combined" in names, "Merged layer should appear in manifest"

    def test_merge_z_index_equals_min_of_selected(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        # background z=0, midground z=1, foreground z=2
        result = merge_layers(
            artwork,
            artwork_dir=td,
            layer_names=["midground", "foreground"],
            merged_name="mid_fg_merged",
        )

        assert result.info.z_index == 1, "Merged z_index should be min(1, 2) = 1"

    def test_merge_removes_source_png_files(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        merge_layers(
            artwork,
            artwork_dir=td,
            layer_names=["background", "midground"],
            merged_name="merged",
        )

        assert not (Path(td) / "background.png").exists(), "Source PNG must be deleted"
        assert not (Path(td) / "midground.png").exists(), "Source PNG must be deleted"


# ---------------------------------------------------------------------------
# TestDuplicateLayer
# ---------------------------------------------------------------------------

class TestDuplicateLayer:
    def test_duplicate_creates_copy_with_same_content(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        result = duplicate_layer(artwork, artwork_dir=td, layer_name="background")

        copy_path = Path(result.image_path)
        assert copy_path.exists(), "Copy PNG must be created"

        # Compare pixel content
        orig_img = Image.open(str(Path(td) / "background.png"))
        copy_img = Image.open(str(copy_path))
        assert orig_img.size == copy_img.size
        assert list(orig_img.getdata()) == list(copy_img.getdata()), "Copy must have same pixels"

    def test_duplicate_z_index_is_source_plus_one(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        # background is z=0
        result = duplicate_layer(artwork, artwork_dir=td, layer_name="background")
        assert result.info.z_index == 1, "Duplicate z_index should be source + 1"

    def test_duplicate_updates_manifest(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        result = duplicate_layer(
            artwork, artwork_dir=td, layer_name="foreground", new_name="foreground_v2"
        )

        reloaded = load_manifest(td)
        names = [lr.info.name for lr in reloaded.layers]
        assert "foreground_v2" in names, "Duplicated layer must appear in manifest"

    def test_duplicate_default_name_is_copy_suffix(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        result = duplicate_layer(artwork, artwork_dir=td, layer_name="midground")
        assert result.info.name == "midground_copy"

    def test_duplicate_custom_name(self, tmp_path):
        td = str(tmp_path)
        _setup_artwork(td)
        artwork = load_manifest(td)

        result = duplicate_layer(
            artwork, artwork_dir=td, layer_name="background", new_name="bg_alt"
        )
        assert result.info.name == "bg_alt"
        assert (Path(td) / "bg_alt.png").exists()
