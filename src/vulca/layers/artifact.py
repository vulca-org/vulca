"""Artifact V3 — structured creation document for LAYERED pipeline."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork

ARTIFACT_VERSION = "3.0"


def write_artifact_v3(
    layers: list[LayerInfo],
    *,
    output_dir: str,
    width: int,
    height: int,
    intent: str = "",
    tradition: str = "default",
    composite_file: str = "composite.png",
    composite_scores: dict[str, float] | None = None,
    cultural_context: dict | None = None,
    rounds: list[dict] | None = None,
    session_id: str = "",
    layer_scores: dict[str, dict[str, float]] | None = None,
) -> str:
    """Write Artifact V3 JSON to output_dir/artifact.json."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    _layer_scores = layer_scores or {}
    layer_dicts = []
    for info in sorted(layers, key=lambda l: l.z_index):
        layer_dicts.append({
            "id": info.id,
            "name": info.name,
            "description": info.description,
            "tradition_role": info.tradition_role,
            "content_type": info.content_type,
            "z_index": info.z_index,
            "blend_mode": info.blend_mode,
            "opacity": info.opacity,
            "visible": info.visible,
            "locked": info.locked,
            "file": f"{info.name}.png",
            "generation_prompt": info.regeneration_prompt,
            "dominant_colors": info.dominant_colors,
            "scores": _layer_scores.get(info.name, {}),
            "status": info.status,
            "weakness": info.weakness,
            "generation_round": info.generation_round,
            # v0.16 multi-layer — dot-notation hierarchical path.
            "semantic_path": info.semantic_path,
        })

    artifact = {
        "artifact_version": ARTIFACT_VERSION,
        "type": "layered_artwork",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "intent": intent,
        "tradition": tradition,
        "generation_mode": "layered",
        "cultural_context": cultural_context or {},
        "canvas": {"width": width, "height": height},
        "layers": layer_dicts,
        "composite": {
            "file": composite_file,
            "scores": composite_scores or {},
            "risk_flags": [],
        },
        "rounds": rounds or [],
        "export_hints": {
            "parallax_ready": True,
            "suggested_format": "rgba_png",
            "psd_compatible": True,
        },
    }

    path = out_dir / "artifact.json"
    path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False))
    return str(path)


def load_artifact_v3(artwork_dir: str) -> LayeredArtwork:
    """Load Artifact V3 or Manifest V2, returning LayeredArtwork.

    V2 files are auto-upgraded with V3 default values.
    """
    art_dir = Path(artwork_dir)

    artifact_path = art_dir / "artifact.json"
    manifest_path = art_dir / "manifest.json"

    if artifact_path.exists():
        data = json.loads(artifact_path.read_text())
    elif manifest_path.exists():
        data = json.loads(manifest_path.read_text())
    else:
        raise FileNotFoundError(f"No artifact.json or manifest.json in {artwork_dir}")

    layers: list[LayerResult] = []
    for ld in data.get("layers", []):
        info = LayerInfo(
            name=ld.get("name", ""),
            description=ld.get("description", ""),
            z_index=ld.get("z_index", 0),
            id=ld.get("id", ""),
            content_type=ld.get("content_type", "background"),
            dominant_colors=ld.get("dominant_colors", []),
            regeneration_prompt=ld.get("regeneration_prompt", ld.get("generation_prompt", "")),
            visible=ld.get("visible", True),
            blend_mode=ld.get("blend_mode", "normal"),
            locked=ld.get("locked", False),
            tradition_role=ld.get("tradition_role", ""),
            opacity=ld.get("opacity", 1.0),
            status=ld.get("status", ""),
            weakness=ld.get("weakness", ""),
            generation_round=ld.get("generation_round", 0),
            semantic_path=ld.get("semantic_path", ""),
        )
        image_path = str(art_dir / ld.get("file", f"{info.name}.png"))
        scores = ld.get("scores", {})
        layers.append(LayerResult(info=info, image_path=image_path, scores=scores))

    composite = data.get("composite", {})

    return LayeredArtwork(
        composite_path=str(art_dir / composite.get("file", "composite.png")),
        layers=layers,
        manifest_path=str(artifact_path if artifact_path.exists() else manifest_path),
        source_image=data.get("source_image", ""),
        split_mode=data.get("generation_mode", data.get("split_mode", "")),
    )
