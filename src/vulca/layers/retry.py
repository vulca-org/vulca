"""Retry helper for failed layers in a layered artifact.

Reads manifest.json from a v0.13 layered artifact directory, identifies
failed layers (file missing on disk or validation.ok == False in layer
extras), and re-invokes `layered_generate` on just those targets so the
sidecar cache keeps the healthy layers free.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Iterable

from vulca.layers.keying import CanvasSpec
from vulca.layers.layered_generate import LayeredResult, layered_generate
from vulca.layers.layered_prompt import TraditionAnchor
from vulca.layers.manifest import load_manifest, write_manifest
from vulca.layers.types import LayerInfo


def _is_failed(layer_entry: dict, artifact_dir: Path) -> bool:
    # Explicit status wins (v0.13 post-P0#2).
    if layer_entry.get("status") == "failed":
        return True
    file_path = artifact_dir / layer_entry.get("file", f"{layer_entry.get('name', '')}.png")
    if not file_path.exists():
        return True
    validation = layer_entry.get("validation") or {}
    if validation and not validation.get("ok", True):
        return True
    return False


def pick_targets(
    manifest: dict,
    artifact_dir: Path,
    *,
    layer_names: Iterable[str] | None = None,
    all_failed: bool = False,
) -> list[dict]:
    entries = manifest.get("layers", [])
    if layer_names:
        wanted = set(layer_names)
        return [e for e in entries if e.get("name") in wanted]
    if all_failed:
        return [e for e in entries if _is_failed(e, artifact_dir)]
    return []


async def retry_layers(
    artifact_dir: str,
    *,
    tradition_name: str,
    layer_names: Iterable[str] | None = None,
    all_failed: bool = False,
    provider,
    parallelism: int = 4,
) -> LayeredResult:
    """Re-run `layered_generate` on a subset of the artifact's layers.

    The tradition anchor / canvas / keying strategy are re-derived from
    `tradition_name` via `vulca.cultural.loader.get_tradition`, matching the
    original LayerGenerateNode native path.
    """
    adir = Path(artifact_dir)
    manifest_path = adir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())

    targets = pick_targets(manifest, adir, layer_names=layer_names, all_failed=all_failed)
    if not targets:
        return LayeredResult(layers=[], failed=[])

    # Reload through load_manifest so we get LayerInfo objects with ids.
    artwork = load_manifest(str(adir))
    info_by_name: dict[str, LayerInfo] = {r.info.name: r.info for r in artwork.layers}
    plan = [info_by_name[e["name"]] for e in targets if e.get("name") in info_by_name]

    from vulca.cultural.loader import get_tradition
    trad = get_tradition(tradition_name)
    canvas_hex = getattr(trad, "canvas_color", "#ffffff") or "#ffffff"
    anchor = TraditionAnchor(
        canvas_color_hex=canvas_hex,
        canvas_description=getattr(trad, "canvas_description", "") or "white canvas",
        style_keywords=getattr(trad, "style_keywords", "") or "",
    )
    canvas = CanvasSpec.from_hex(canvas_hex)
    key_strategy_name = getattr(trad, "key_strategy", "luminance") or "luminance"

    result = await layered_generate(
        plan=plan,
        tradition_anchor=anchor,
        canvas=canvas,
        key_strategy_name=key_strategy_name,
        provider=provider,
        output_dir=str(adir),
        parallelism=parallelism,
        cache_enabled=True,
    )

    # P0 #3: recompute manifest health from the FULL merged artifact state,
    # not just the retried subset, so retrying one layer can't falsely mark
    # the whole artifact healthy.

    def _validation_to_dict(v) -> dict:
        return {
            "ok": v.ok,
            "warnings": [
                {"kind": w.kind, "message": w.message, "detail": w.detail}
                for w in v.warnings
            ],
            "coverage_actual": v.coverage_actual,
            "position_iou": v.position_iou,
        }

    # Start from existing extras so untouched layers keep their source/status.
    _PASSTHROUGH_KEYS = (
        "source", "status", "reason", "cache_hit", "attempts", "validation",
        "canvas_color", "key_strategy",
    )
    merged_extras: dict[str, dict] = {}
    for e in manifest.get("layers", []):
        carried = {k: v for k, v in e.items() if k in _PASSTHROUGH_KEYS}
        if carried:
            merged_extras[e.get("id", "")] = carried

    # Overlay retried outcomes — successes become status=ok, failures status=failed.
    for o in result.layers:
        extra: dict = {
            "source": "a", "status": "ok",
            "cache_hit": bool(o.cache_hit), "attempts": o.attempts,
        }
        if o.validation is not None:
            extra["validation"] = _validation_to_dict(o.validation)
        merged_extras[o.info.id] = extra
    for f in result.failed:
        extra = {
            "source": "a", "status": "failed",
            "reason": f.reason, "attempts": f.attempts,
        }
        if f.validation is not None:
            extra["validation"] = _validation_to_dict(f.validation)
        merged_extras[f.layer_id] = extra

    # Health derived from the merged state.
    any_failed = any(
        merged_extras.get(info.id, {}).get("status") == "failed"
        or not (adir / f"{info.name}.png").exists()
        for info in (r.info for r in artwork.layers)
    )
    merged_warnings: list[str] = []
    for extra in merged_extras.values():
        vd = extra.get("validation") or {}
        for w in vd.get("warnings", []) or []:
            msg = w.get("message") if isinstance(w, dict) else None
            if msg:
                merged_warnings.append(msg)

    write_manifest(
        [r.info for r in artwork.layers],
        output_dir=str(adir),
        width=manifest.get("width", 1024),
        height=manifest.get("height", 1024),
        source_image=manifest.get("source_image", ""),
        split_mode=manifest.get("split_mode", ""),
        generation_path=manifest.get("generation_path", "a"),
        layerability=manifest.get("layerability", ""),
        partial=any_failed,
        warnings=merged_warnings,
        layer_extras=merged_extras,
    )
    return result
