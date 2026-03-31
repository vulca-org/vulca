"""Edit individual layers — V2 delegates to manifest.py.

Kept for backward compatibility: code that imports load_artwork/save_manifest
from edit.py still works.
"""
from __future__ import annotations

from vulca.layers.manifest import load_manifest as load_artwork, write_manifest


def save_manifest(artwork, artwork_dir: str) -> None:
    """V1 compat: save artwork manifest to directory."""
    import json
    from pathlib import Path

    # Try to read real dimensions from existing manifest
    manifest_path = Path(artwork_dir) / "manifest.json"
    width, height = 1024, 1024
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text())
            width = data.get("width", 1024)
            height = data.get("height", 1024)
        except (json.JSONDecodeError, KeyError):
            pass

    write_manifest(
        [l.info for l in artwork.layers],
        output_dir=artwork_dir,
        width=width,
        height=height,
        source_image=getattr(artwork, "source_image", ""),
        split_mode=getattr(artwork, "split_mode", ""),
    )
