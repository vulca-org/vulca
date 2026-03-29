"""Edit individual layers via inpainting or transformation."""
from __future__ import annotations

import json
from pathlib import Path

from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork


def load_artwork(artwork_dir: str) -> LayeredArtwork:
    """Load a LayeredArtwork from a directory with manifest.json."""
    d = Path(artwork_dir)
    manifest_path = d / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest.json in {artwork_dir}")

    manifest = json.loads(manifest_path.read_text())
    layers = []
    for item in manifest.get("layers", []):
        info = LayerInfo(
            name=item["name"],
            description=item.get("description", ""),
            bbox=item.get("bbox", {"x": 0, "y": 0, "w": 100, "h": 100}),
            z_index=item.get("z_index", 0),
            blend_mode=item.get("blend_mode", "normal"),
        )
        image_path = str(d / item["file"])
        scores = item.get("scores", {})
        layers.append(LayerResult(info=info, image_path=image_path, scores=scores))

    composite = str(d / manifest.get("composite", "composite.jpg"))
    return LayeredArtwork(
        composite_path=composite,
        layers=sorted(layers, key=lambda l: l.info.z_index),
        manifest_path=str(manifest_path),
    )


def save_manifest(artwork: LayeredArtwork, artwork_dir: str) -> None:
    """Save artwork manifest to directory."""
    d = Path(artwork_dir)
    manifest = {
        "composite": Path(artwork.composite_path).name,
        "width": 1024,
        "height": 1024,
        "layers": [
            {
                "name": l.info.name,
                "description": l.info.description,
                "file": Path(l.image_path).name,
                "bbox": l.info.bbox,
                "z_index": l.info.z_index,
                "blend_mode": l.info.blend_mode,
                "scores": l.scores,
            }
            for l in artwork.layers
        ],
    }
    (d / "manifest.json").write_text(json.dumps(manifest, indent=2))
