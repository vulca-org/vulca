"""Manifest V2 read/write for VULCA layered artwork.

Single source of truth for manifest I/O, replacing the scattered
write_manifest in split.py and load_artwork in edit.py.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork

MANIFEST_VERSION = 3


def write_manifest(
    layers: list[LayerInfo],
    *,
    output_dir: str,
    width: int,
    height: int,
    source_image: str = "",
    split_mode: str = "",
    generation_path: str = "",
    layerability: str = "",
    partial: bool = False,
    warnings: list | None = None,
    layer_extras: dict[str, dict] | None = None,
) -> str:
    """Write manifest V3 JSON to output_dir/manifest.json. Returns path."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    extras = layer_extras or {}

    manifest = {
        "version": MANIFEST_VERSION,
        "width": width,
        "height": height,
        "source_image": source_image,
        "split_mode": split_mode,
        "generation_path": generation_path,
        "layerability": layerability,
        "partial": partial,
        "warnings": warnings or [],
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "layers": [
            {
                **(extras.get(info.id, {})),
                "id": info.id,
                "name": info.name,
                "description": info.description,
                "z_index": info.z_index,
                "blend_mode": info.blend_mode,
                "content_type": info.content_type,
                "visible": info.visible,
                "locked": info.locked,
                "file": f"{info.name}.png",
                "dominant_colors": info.dominant_colors,
                "regeneration_prompt": info.regeneration_prompt,
                "opacity": info.opacity,
                "x": info.x,
                "y": info.y,
                "width": info.width,
                "height": info.height,
                "rotation": info.rotation,
                "content_bbox": info.content_bbox,
            }
            for info in sorted(layers, key=lambda l: l.z_index)
        ],
    }

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return str(manifest_path)


def load_manifest(artwork_dir: str) -> LayeredArtwork:
    """Load LayeredArtwork from manifest.json. Auto-migrates V1 manifests."""
    d = Path(artwork_dir)
    manifest_path = d / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest.json in {artwork_dir}")

    manifest = json.loads(manifest_path.read_text())
    version = manifest.get("version", 1)

    layers = []
    for index, item in enumerate(manifest.get("layers", [])):
        if version >= 2:
            # V2: use id and content_type directly
            info = LayerInfo(
                name=item["name"],
                description=item.get("description", ""),
                z_index=item.get("z_index", index),
                id=item.get("id", f"layer_{item['name']}_{index:03d}"),
                content_type=item.get("content_type", "background"),
                dominant_colors=item.get("dominant_colors", []),
                regeneration_prompt=item.get("regeneration_prompt", ""),
                visible=item.get("visible", True),
                blend_mode=item.get("blend_mode", "normal"),
                locked=item.get("locked", False),
                opacity=item.get("opacity", 1.0),
                x=item.get("x", 0.0),
                y=item.get("y", 0.0),
                width=item.get("width", 100.0),
                height=item.get("height", 100.0),
                rotation=item.get("rotation", 0.0),
                content_bbox=item.get("content_bbox"),
            )
        else:
            # V1: migrate — generate id, default content_type, preserve bbox
            name = item.get("name", f"layer_{index:03d}")
            generated_id = f"layer_{name}_{index:03d}"
            info = LayerInfo(
                name=name,
                description=item.get("description", ""),
                z_index=item.get("z_index", index),
                id=generated_id,
                content_type="background",
                dominant_colors=[],
                regeneration_prompt="",
                visible=True,
                blend_mode=item.get("blend_mode", "normal"),
                locked=False,
                bbox=item.get("bbox"),
            )

        image_path = str(d / item.get("file", f"{info.name}.png"))
        scores = item.get("scores", {})
        layers.append(LayerResult(info=info, image_path=image_path, scores=scores))

    composite = str(d / manifest.get("composite", "composite.png"))

    return LayeredArtwork(
        composite_path=composite,
        layers=sorted(layers, key=lambda lr: lr.info.z_index),
        manifest_path=str(manifest_path),
        source_image=manifest.get("source_image", ""),
        split_mode=manifest.get("split_mode", ""),
    )
