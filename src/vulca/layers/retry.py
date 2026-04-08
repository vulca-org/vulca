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
    """Pick retry targets from a manifest.

    Raises `UnknownLayerError` when `layer_names` contains a name that
    doesn't exist in the manifest, so operators see an explicit error
    instead of a silent "0 ok, 0 failed" no-op.
    """
    entries = manifest.get("layers", [])
    if layer_names:
        wanted = list(layer_names)
        available = {e.get("name") for e in entries}
        unknown = [n for n in wanted if n not in available]
        if unknown:
            raise UnknownLayerError(unknown, sorted(available))
        wanted_set = set(wanted)
        return [e for e in entries if e.get("name") in wanted_set]
    if all_failed:
        return [e for e in entries if _is_failed(e, artifact_dir)]
    return []


class UnknownLayerError(ValueError):
    """Raised by pick_targets when a requested layer name doesn't exist."""

    def __init__(self, unknown: list[str], available: list[str]):
        self.unknown = unknown
        self.available = available
        super().__init__(
            f"Unknown layer name(s): {', '.join(unknown)}. "
            f"Available: {', '.join(available)}"
        )


async def retry_layers(
    artifact_dir: str,
    *,
    tradition_name: str | None = None,
    layer_names: Iterable[str] | None = None,
    all_failed: bool = False,
    provider,
    parallelism: int = 4,
) -> LayeredResult:
    """Re-run `layered_generate` on a subset of the artifact's layers.

    The tradition anchor / canvas / keying strategy are re-derived via
    `vulca.cultural.loader.get_tradition`, matching the original
    LayerGenerateNode native path.

    P0.1: `tradition_name` is optional. The canonical value lives in
    `manifest.json["tradition"]` (persisted by CompositeNode on the
    initial run). If the caller passes `None` we read it from the
    manifest. If the caller passes an explicit value AND the manifest
    disagrees, we raise `ValueError` rather than silently overriding —
    mis-applying one tradition's prompt/keying to another tradition's
    artifact was the P0.1 foot-gun Codex flagged.
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

    manifest_tradition = (manifest.get("tradition") or "").strip()
    caller_tradition = (tradition_name or "").strip() or None

    if caller_tradition and manifest_tradition and caller_tradition != manifest_tradition:
        raise ValueError(
            f"tradition mismatch: manifest records {manifest_tradition!r} but "
            f"caller passed {caller_tradition!r}. Refusing to re-run with the "
            f"wrong prompt/keying stack. Pass --tradition {manifest_tradition} "
            f"or omit it to use the manifest value."
        )

    resolved_tradition = caller_tradition or manifest_tradition
    if not resolved_tradition:
        raise ValueError(
            "tradition not recorded in manifest and no tradition_name supplied. "
            "Pass --tradition explicitly to avoid silently regenerating layers "
            "with the wrong prompt/keying stack."
        )

    from vulca.cultural.loader import get_tradition
    trad = get_tradition(resolved_tradition)
    canvas_hex = getattr(trad, "canvas_color", "#ffffff") or "#ffffff"
    anchor = TraditionAnchor(
        canvas_color_hex=canvas_hex,
        canvas_description=getattr(trad, "canvas_description", "") or "white canvas",
        style_keywords=getattr(trad, "style_keywords", "") or "",
    )
    canvas = CanvasSpec.from_hex(canvas_hex)
    key_strategy_name = getattr(trad, "key_strategy", "luminance") or "luminance"

    # P0.2: thread position/coverage back from LayerInfo (now first-class
    # fields that round-trip through manifest.json). Without this, retry
    # falls back to layered_prompt's weaker default spatial block and
    # computes a different cache key than the original run.
    positions = {info.name: info.position for info in plan if info.position}
    coverages = {info.name: info.coverage for info in plan if info.coverage}

    # P0.3: read canvas dimensions from manifest so non-default-size
    # artifacts don't retry at 0×0 (which breaks cache keying AND
    # produces wrong output dimensions).
    manifest_width = int(manifest.get("width", 1024) or 1024)
    manifest_height = int(manifest.get("height", 1024) or 1024)

    result = await layered_generate(
        plan=plan,
        tradition_anchor=anchor,
        canvas=canvas,
        key_strategy_name=key_strategy_name,
        provider=provider,
        output_dir=str(adir),
        positions=positions,
        coverages=coverages,
        parallelism=parallelism,
        cache_enabled=True,
        width=manifest_width,
        height=manifest_height,
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
    # v0.13.2 P2 review nit: don't carry extras for retried targets. Their
    # prior status/validation gets replaced by the retried outcome below;
    # carrying the old `validation` dict would re-inject stale warnings via
    # the merged_warnings rebuild even when the layer comes back clean.
    targeted_ids = {info.id for info in plan}
    merged_extras: dict[str, dict] = {}
    for e in manifest.get("layers", []):
        if e.get("id", "") in targeted_ids:
            continue
        carried = {k: v for k, v in e.items() if k in _PASSTHROUGH_KEYS}
        if carried:
            merged_extras[e.get("id", "")] = carried

    # Overlay retried outcomes — successes become status=ok, failures status=failed.
    # Keep canvas_color / key_strategy attached to retried entries too, matching
    # the A-path extras contract from composite_node.
    _canvas_color = canvas_hex
    _key_strategy = key_strategy_name
    for o in result.layers:
        extra: dict = {
            "source": "a", "status": "ok",
            "cache_hit": bool(o.cache_hit), "attempts": o.attempts,
            "canvas_color": _canvas_color, "key_strategy": _key_strategy,
        }
        if o.validation is not None:
            extra["validation"] = _validation_to_dict(o.validation)
        merged_extras[o.info.id] = extra
    for f in result.failed:
        extra = {
            "source": "a", "status": "failed",
            "reason": f.reason, "attempts": f.attempts,
            "canvas_color": _canvas_color, "key_strategy": _key_strategy,
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
    # v0.13.2 P2 T12: preserve non-validation warnings from the prior manifest
    # (e.g. tradition-layerability discouraged). Validation warnings get
    # re-derived from merged_extras below.
    #
    # v0.13.2 P2 review nit: also DROP prior validation-warning strings from
    # the seed, so a retried-clean layer's stale validation warning doesn't
    # linger in the top-level list. We collect the set of prior validation
    # messages from the prior manifest's per-layer `validation.warnings`
    # entries and filter them out of the seed.
    prior_validation_msgs: set[str] = set()
    for layer_dict in manifest.get("layers", []) or []:
        vd = layer_dict.get("validation") or {}
        for w in vd.get("warnings", []) or []:
            msg = w.get("message") if isinstance(w, dict) else None
            if msg:
                prior_validation_msgs.add(msg)
    merged_warnings: list[str] = [
        w for w in (manifest.get("warnings", []) or [])
        if w not in prior_validation_msgs
    ]
    for extra in merged_extras.values():
        vd = extra.get("validation") or {}
        for w in vd.get("warnings", []) or []:
            msg = w.get("message") if isinstance(w, dict) else None
            if msg and msg not in merged_warnings:
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
        tradition=resolved_tradition,
    )
    return result
