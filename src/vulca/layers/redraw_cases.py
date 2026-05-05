"""Versioned case records for redraw learning loops."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from vulca.layers.types import LayerInfo

CASE_SCHEMA_VERSION = 1
CASE_TYPE = "redraw_case"

FAILURE_TYPES: frozenset[str] = frozenset(
    {
        "color_drift",
        "shape_collapse",
        "wrong_subject",
        "missing_detail",
        "over_smoothing",
        "texture_leak",
        "alpha_expansion",
        "mask_too_broad",
        "background_bleed",
        "large_white_component",
        "pasteback_mismatch",
        "route_error",
        "over_split",
        "under_split",
        "uncertain",
    }
)

PREFERRED_ACTIONS: frozenset[str] = frozenset(
    {
        "",
        "accept",
        "rerun",
        "fallback_to_agent",
        "fallback_to_original",
        "manual_review",
        "adjust_route",
        "adjust_mask",
        "adjust_instruction",
    }
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_failure_type(value: str) -> str:
    if value == "":
        return ""
    if value not in FAILURE_TYPES:
        raise ValueError(
            f"unsupported redraw failure_type {value!r}; expected one of {sorted(FAILURE_TYPES)}"
        )
    return value


def validate_preferred_action(value: str) -> str:
    if value not in PREFERRED_ACTIONS:
        raise ValueError(
            f"unsupported redraw preferred_action {value!r}; expected one of {sorted(PREFERRED_ACTIONS)}"
        )
    return value


def resolve_case_log_path(case_log_path: str, artwork_dir: str) -> str:
    if case_log_path:
        return str(Path(case_log_path))
    env_value = os.environ.get("VULCA_REDRAW_CASE_LOG", "").strip()
    if not env_value:
        return ""
    if env_value.lower() in {"1", "true", "yes", "on"}:
        return str(Path(artwork_dir) / "redraw_cases.jsonl")
    return str(Path(env_value))


def build_redraw_case(
    *,
    artwork_dir: str,
    source_image: str,
    layer_info: LayerInfo,
    instruction: str,
    provider: str,
    model: str,
    route_requested: str,
    source_layer_path: str,
    redrawn_layer_path: str,
    source_pasteback_path: str = "",
    redraw_advisory: Mapping[str, Any] | None = None,
    debug_summary_path: str = "",
    created_at: str | None = None,
    human_accept: bool | None = None,
    failure_type: str = "",
    preferred_action: str = "",
    reviewer: str = "",
    reviewed_at: str = "",
) -> dict[str, Any]:
    advisory = dict(redraw_advisory or {})
    created = created_at or utc_now_iso()
    checked_failure_type = validate_failure_type(failure_type)
    checked_action = validate_preferred_action(preferred_action)
    case_id = _make_case_id(
        created_at=created,
        source_layer_path=source_layer_path,
        redrawn_layer_path=redrawn_layer_path,
        instruction=instruction,
        provider=provider,
        model=model,
    )

    return {
        "schema_version": CASE_SCHEMA_VERSION,
        "case_type": CASE_TYPE,
        "case_id": case_id,
        "created_at": created,
        "artwork_dir": str(artwork_dir),
        "source_image": str(source_image or ""),
        "layer": {
            "id": str(layer_info.id),
            "name": str(layer_info.name),
            "description": str(layer_info.description),
            "semantic_path": str(layer_info.semantic_path or ""),
            "quality_status": str(layer_info.quality_status or ""),
            "area_pct_manifest": float(layer_info.area_pct or 0.0),
        },
        "instruction": str(instruction),
        "provider": str(provider),
        "model": str(model or advisory.get("model", "")),
        "route": {
            "requested": str(route_requested or advisory.get("route_requested", "")),
            "chosen": str(advisory.get("route_chosen", "")),
            "redraw_route": str(advisory.get("redraw_route", "")),
            "geometry_redraw_route": str(advisory.get("geometry_redraw_route", "")),
        },
        "geometry": {
            "area_pct": float(advisory.get("area_pct", 0.0) or 0.0),
            "bbox_fill": float(advisory.get("bbox_fill", 0.0) or 0.0),
            "component_count": int(advisory.get("component_count", 0) or 0),
            "sparse_detected": bool(advisory.get("sparse_detected", False)),
        },
        "quality": {
            "gate_passed": _optional_bool(advisory.get("quality_gate_passed")),
            "failures": [str(item) for item in advisory.get("quality_failures", [])],
            "metrics": dict(advisory.get("quality_metrics", {}) or {}),
        },
        "refinement": {
            "applied": bool(advisory.get("refinement_applied", False)),
            "reason": str(advisory.get("refinement_reason", "")),
            "strategy": str(advisory.get("refinement_strategy", "")),
            "child_count": int(advisory.get("refined_child_count", 0) or 0),
            "mask_granularity_score": float(
                advisory.get("mask_granularity_score", 0.0) or 0.0
            ),
        },
        "artifacts": {
            "source_layer_path": str(source_layer_path or ""),
            "redrawn_layer_path": str(redrawn_layer_path or ""),
            "source_pasteback_path": str(source_pasteback_path or ""),
            "debug_summary_path": str(debug_summary_path or ""),
        },
        "review": {
            "human_accept": human_accept,
            "failure_type": checked_failure_type,
            "preferred_action": checked_action,
            "reviewer": str(reviewer or ""),
            "reviewed_at": str(reviewed_at or ""),
        },
    }


def append_redraw_case(case_log_path: str, record: Mapping[str, Any]) -> str:
    if not case_log_path:
        raise ValueError("case_log_path is required when appending a redraw case")
    path = Path(case_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
        fh.write("\n")
    return str(path)


def _optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _make_case_id(
    *,
    created_at: str,
    source_layer_path: str,
    redrawn_layer_path: str,
    instruction: str,
    provider: str,
    model: str,
) -> str:
    stamp = (
        created_at.replace("-", "")
        .replace(":", "")
        .replace(".", "")
        .replace("+", "")
    )
    seed = "\n".join(
        [
            created_at,
            source_layer_path,
            redrawn_layer_path,
            instruction,
            provider,
            model,
        ]
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"redraw_{stamp}_{digest}"
