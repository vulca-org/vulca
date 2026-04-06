"""Layer editing operations for VULCA layered artwork.

Provides add/remove/reorder/toggle/lock/merge/duplicate operations
on LayeredArtwork in memory, with automatic manifest persistence.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image

from vulca.layers.blend import blend_layers
from vulca.layers.manifest import load_manifest, write_manifest
from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _find_layer(artwork: LayeredArtwork, name: str) -> LayerResult:
    """Find layer by name. Raise ValueError("not found") if missing."""
    for layer in artwork.layers:
        if layer.info.name == name:
            return layer
    raise ValueError("not found")


def _read_dimensions(artwork_dir: str) -> tuple[int, int]:
    """Read width/height from manifest.json."""
    manifest_path = Path(artwork_dir) / "manifest.json"
    data = json.loads(manifest_path.read_text())
    return data["width"], data["height"]


def _save_artwork(artwork: LayeredArtwork, artwork_dir: str) -> None:
    """Persist current artwork state to manifest.json via write_manifest."""
    # Load existing manifest to preserve width/height/source_image/split_mode
    manifest_path = Path(artwork_dir) / "manifest.json"
    data = json.loads(manifest_path.read_text())
    write_manifest(
        [lr.info for lr in artwork.layers],
        output_dir=artwork_dir,
        width=data["width"],
        height=data["height"],
        source_image=data.get("source_image", ""),
        split_mode=data.get("split_mode", ""),
    )


# ---------------------------------------------------------------------------
# Public operations
# ---------------------------------------------------------------------------

def add_layer(
    artwork: LayeredArtwork,
    *,
    artwork_dir: str,
    name: str,
    description: str = "",
    z_index: int = -1,
    content_type: str = "subject",
    blend_mode: str = "normal",
) -> LayerResult:
    """Add new transparent layer.

    Raise ValueError("already exists") if name exists.
    z_index=-1 means top (max existing z_index + 1).
    """
    # Check for duplicate
    for layer in artwork.layers:
        if layer.info.name == name:
            raise ValueError("already exists")

    width, height = _read_dimensions(artwork_dir)

    # Determine z_index
    if z_index == -1:
        if artwork.layers:
            z_index = max(lr.info.z_index for lr in artwork.layers) + 1
        else:
            z_index = 0

    # Create transparent RGBA PNG
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    png_path = Path(artwork_dir) / f"{name}.png"
    img.save(str(png_path))

    info = LayerInfo(
        name=name,
        description=description,
        z_index=z_index,
        content_type=content_type,
        blend_mode=blend_mode,
    )
    result = LayerResult(info=info, image_path=str(png_path))

    artwork.layers.append(result)
    _save_artwork(artwork, artwork_dir)
    return result


def remove_layer(
    artwork: LayeredArtwork,
    *,
    artwork_dir: str,
    layer_name: str,
) -> None:
    """Remove layer + delete PNG file.

    Raise ValueError("locked") if locked.
    Raise ValueError("not found") if missing.
    """
    layer = _find_layer(artwork, layer_name)

    if layer.info.locked:
        raise ValueError("locked")

    # Delete PNG file
    png_path = Path(layer.image_path)
    if png_path.exists():
        png_path.unlink()

    artwork.layers = [lr for lr in artwork.layers if lr.info.name != layer_name]
    _save_artwork(artwork, artwork_dir)


def reorder_layer(
    artwork: LayeredArtwork,
    *,
    artwork_dir: str,
    layer_name: str,
    new_z_index: int,
) -> None:
    """Move layer to new z_index. Re-number all layers sequentially."""
    layer = _find_layer(artwork, layer_name)

    # Sort layers by z_index, then reorder
    sorted_layers = sorted(artwork.layers, key=lambda lr: lr.info.z_index)

    # Remove the target layer from sorted list
    sorted_layers = [lr for lr in sorted_layers if lr.info.name != layer_name]

    # Clamp new_z_index to valid range
    clamped = max(0, min(new_z_index, len(sorted_layers)))

    # Insert at new position
    sorted_layers.insert(clamped, layer)

    # Re-number sequentially
    for i, lr in enumerate(sorted_layers):
        lr.info.z_index = i

    artwork.layers = sorted_layers
    _save_artwork(artwork, artwork_dir)


def toggle_visibility(
    artwork: LayeredArtwork,
    *,
    artwork_dir: str,
    layer_name: str,
    visible: bool,
) -> None:
    """Set layer visible flag."""
    layer = _find_layer(artwork, layer_name)
    layer.info.visible = visible
    _save_artwork(artwork, artwork_dir)


def lock_layer(
    artwork: LayeredArtwork,
    *,
    artwork_dir: str,
    layer_name: str,
    locked: bool,
) -> None:
    """Set layer locked flag."""
    layer = _find_layer(artwork, layer_name)
    layer.info.locked = locked
    _save_artwork(artwork, artwork_dir)


def merge_layers(
    artwork: LayeredArtwork,
    *,
    artwork_dir: str,
    layer_names: list[str],
    merged_name: str = "merged",
) -> LayerResult:
    """Composite selected layers via blend_layers → save as merged PNG.

    Remove source layers + files. Return merged LayerResult with z_index=min of selected.
    """
    if not layer_names:
        raise ValueError("layer_names must not be empty")

    # Collect target layers (validates they exist)
    target_layers = [_find_layer(artwork, name) for name in layer_names]

    # Refuse to merge locked layers (data loss protection)
    locked = [lr.info.name for lr in target_layers if lr.info.locked]
    if locked:
        raise ValueError(f"Cannot merge locked layer(s): {', '.join(locked)} — unlock first")

    width, height = _read_dimensions(artwork_dir)
    min_z = min(lr.info.z_index for lr in target_layers)

    # Composite via blend_layers
    merged_img = blend_layers(target_layers, width=width, height=height)

    # Save merged PNG
    merged_path = Path(artwork_dir) / f"{merged_name}.png"
    merged_img.save(str(merged_path))

    # Remove source layers and their files
    for lr in target_layers:
        src_png = Path(lr.image_path)
        if src_png.exists():
            src_png.unlink()

    artwork.layers = [lr for lr in artwork.layers if lr.info.name not in layer_names]

    # Create merged LayerResult
    merged_info = LayerInfo(
        name=merged_name,
        description="merged layer",
        z_index=min_z,
        content_type="subject",
        blend_mode="normal",
    )
    merged_result = LayerResult(info=merged_info, image_path=str(merged_path))
    artwork.layers.append(merged_result)

    # Sort layers by z_index
    artwork.layers = sorted(artwork.layers, key=lambda lr: lr.info.z_index)

    _save_artwork(artwork, artwork_dir)
    return merged_result


def transform_layer(
    artwork: LayeredArtwork,
    *,
    artwork_dir: str,
    layer_name: str,
    dx: float = 0.0,
    dy: float = 0.0,
    scale: float = 1.0,
    rotate: float = 0.0,
    set_x: float | None = None,
    set_y: float | None = None,
    set_width: float | None = None,
    set_height: float | None = None,
    set_opacity: float | None = None,
) -> None:
    """Transform a layer's spatial properties.

    dx/dy are relative offsets (added to current x/y).
    scale multiplies current width/height.
    rotate adds to current rotation.
    set_* values override absolutely.

    Raise ValueError("locked") if layer is locked.
    Raise ValueError("not found") if layer doesn't exist.
    """
    layer = _find_layer(artwork, layer_name)

    if layer.info.locked:
        raise ValueError("locked")

    # Relative adjustments
    layer.info.x += dx
    layer.info.y += dy
    layer.info.width *= scale
    layer.info.height *= scale
    layer.info.rotation += rotate

    # Absolute overrides
    if set_x is not None:
        layer.info.x = set_x
    if set_y is not None:
        layer.info.y = set_y
    if set_width is not None:
        layer.info.width = set_width
    if set_height is not None:
        layer.info.height = set_height
    if set_opacity is not None:
        layer.info.opacity = set_opacity

    # Clamp values
    layer.info.width = max(1.0, layer.info.width)
    layer.info.height = max(1.0, layer.info.height)
    layer.info.opacity = max(0.0, min(1.0, layer.info.opacity))

    _save_artwork(artwork, artwork_dir)


def duplicate_layer(
    artwork: LayeredArtwork,
    *,
    artwork_dir: str,
    layer_name: str,
    new_name: str = "",
) -> LayerResult:
    """Copy layer PNG to new_name.png.

    New z_index = source.z_index + 1. Default new_name = "{layer_name}_copy".
    """
    source = _find_layer(artwork, layer_name)

    if not new_name:
        new_name = f"{layer_name}_copy"

    # Copy PNG file
    src_path = Path(source.image_path)
    dst_path = Path(artwork_dir) / f"{new_name}.png"
    shutil.copy2(str(src_path), str(dst_path))

    # Create new LayerInfo with incremented z_index
    new_info = LayerInfo(
        name=new_name,
        description=source.info.description,
        z_index=source.info.z_index + 1,
        content_type=source.info.content_type,
        blend_mode=source.info.blend_mode,
        visible=source.info.visible,
        locked=source.info.locked,
        dominant_colors=list(source.info.dominant_colors),
        regeneration_prompt=source.info.regeneration_prompt,
    )
    new_result = LayerResult(info=new_info, image_path=str(dst_path))
    artwork.layers.append(new_result)

    _save_artwork(artwork, artwork_dir)
    return new_result
