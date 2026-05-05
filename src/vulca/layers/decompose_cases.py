"""Versioned case records for decompose learning loops."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

CASE_SCHEMA_VERSION = 1
CASE_TYPE = "decompose_case"

FAILURE_TYPES: frozenset[str] = frozenset(
    {
        "over_split",
        "under_split",
        "semantic_mismatch",
        "alpha_bad",
        "residual_leakage",
        "missed_concept",
        "wrong_instance",
        "empty_layer",
        "duplicate_layer",
        "debug_artifact_missing",
        "route_error",
        "uncertain",
    }
)

PREFERRED_ACTIONS: frozenset[str] = frozenset(
    {
        "",
        "rerun_split",
        "adjust_hints",
        "merge_layers",
        "split_layer_further",
        "fallback_to_manual",
        "fallback_to_agent",
        "accept",
    }
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_failure_type(value: str) -> str:
    if value == "":
        return ""
    if value not in FAILURE_TYPES:
        raise ValueError(
            f"unsupported decompose failure_type {value!r}; expected one of {sorted(FAILURE_TYPES)}"
        )
    return value


def validate_preferred_action(value: str) -> str:
    if value not in PREFERRED_ACTIONS:
        raise ValueError(
            f"unsupported decompose preferred_action {value!r}; expected one of {sorted(PREFERRED_ACTIONS)}"
        )
    return value


def resolve_case_log_path(case_log_path: str, output_dir: str) -> str:
    if case_log_path:
        return str(Path(case_log_path))
    env_value = os.environ.get("VULCA_DECOMPOSE_CASE_LOG", "").strip()
    if not env_value:
        return ""
    if env_value.lower() in {"1", "true", "yes", "on"}:
        return str(Path(output_dir) / "decompose_cases.jsonl")
    return str(Path(env_value))


def target_hints_from_plan(plan: Any) -> list[dict[str, Any]]:
    if hasattr(plan, "model_dump"):
        data = plan.model_dump(mode="json")
    elif isinstance(plan, Mapping):
        data = dict(plan)
    else:
        data = json.loads(str(plan))

    hints: list[dict[str, Any]] = []
    for entity in data.get("entities", []) or []:
        hints.append(
            {
                "name": str(entity.get("name", "")),
                "label": str(entity.get("label", "")),
                "semantic_path": str(entity.get("semantic_path", "") or ""),
                "detector": str(entity.get("detector", "") or ""),
                "bbox_hint_pct": entity.get("bbox_hint_pct"),
                "multi_instance": bool(entity.get("multi_instance", False)),
                "threshold": entity.get("threshold"),
                "order": entity.get("order"),
            }
        )
    return hints


def target_hints_from_layer_infos(layers: Sequence[Any]) -> list[dict[str, Any]]:
    hints: list[dict[str, Any]] = []
    for item in layers:
        info = getattr(item, "info", item)
        hints.append(
            {
                "name": str(getattr(info, "name", "")),
                "label": str(getattr(info, "description", "") or getattr(info, "name", "")),
                "semantic_path": str(getattr(info, "semantic_path", "") or ""),
                "detector": "",
                "bbox_hint_pct": None,
                "multi_instance": False,
                "threshold": None,
                "order": None,
            }
        )
    return hints


def debug_artifacts_from_output_dir(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    qa_contact_sheet = out / "qa_contact_sheet.jpg"
    qa_prompt = out / "qa_prompt.md"
    log_path = out / "decompose.log"
    mask_overlay_paths = sorted(str(p) for p in out.glob("*mask_overlay*.png"))
    return {
        "qa_contact_sheet_path": str(qa_contact_sheet) if qa_contact_sheet.exists() else "",
        "qa_prompt_path": str(qa_prompt) if qa_prompt.exists() else "",
        "mask_overlay_paths": mask_overlay_paths,
        "log_path": str(log_path) if log_path.exists() else "",
    }


def build_decompose_case(
    *,
    source_image: str,
    mode: str,
    provider: str,
    model: str,
    tradition: str,
    output_dir: str,
    manifest_path: str,
    target_layer_hints: Sequence[Mapping[str, Any]] = (),
    manifest_data: Mapping[str, Any] | None = None,
    debug_artifacts: Mapping[str, Any] | None = None,
    created_at: str | None = None,
    human_accept: bool | None = None,
    failure_type: str = "",
    preferred_action: str = "",
    reviewer: str = "",
    reviewed_at: str = "",
    notes: str = "",
) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path, manifest_data)
    created = created_at or utc_now_iso()
    checked_failure_type = validate_failure_type(failure_type)
    checked_action = validate_preferred_action(preferred_action)
    normalized_hints = [dict(hint) for hint in target_layer_hints]
    layers = [_layer_record(output_dir, item) for item in manifest.get("layers", []) or []]
    detection_report = dict(manifest.get("detection_report", {}) or {})
    residual_path, residual_pct = _residual_from_layers(layers)
    composite_path = _artifact_path(output_dir, str(manifest.get("composite", "") or ""))
    quality = _quality_record(layers, detection_report, residual_pct)

    case_id = _make_case_id(
        created_at=created,
        source_image=source_image,
        mode=mode,
        provider=provider,
        model=model,
        tradition=tradition,
        output_dir=output_dir,
        manifest_path=manifest_path,
        target_layer_hints=normalized_hints,
    )

    return {
        "schema_version": CASE_SCHEMA_VERSION,
        "case_type": CASE_TYPE,
        "case_id": case_id,
        "created_at": created,
        "input": {
            "source_image": str(source_image or ""),
            "requested": {
                "mode": str(mode or ""),
                "provider": str(provider or ""),
                "model": str(model or ""),
                "tradition": str(tradition or ""),
            },
            "target_layer_hints": normalized_hints,
        },
        "output": {
            "output_dir": str(output_dir or ""),
            "manifest_path": str(manifest_path or ""),
            "manifest_version": int(manifest.get("manifest_version", manifest.get("version", 0)) or 0),
            "split_mode": str(manifest.get("split_mode", mode or "")),
            "status": str(manifest.get("status", "")),
            "layers": layers,
            "residual_path": residual_path,
            "composite_path": composite_path,
            "detection_report": detection_report,
            "debug_artifacts": _debug_artifacts_record(debug_artifacts),
        },
        "quality": quality,
        "review": {
            "human_accept": human_accept,
            "failure_type": checked_failure_type,
            "preferred_action": checked_action,
            "reviewer": str(reviewer or ""),
            "reviewed_at": str(reviewed_at or ""),
            "notes": str(notes or ""),
        },
    }


def append_decompose_case(case_log_path: str, record: Mapping[str, Any]) -> str:
    if not case_log_path:
        raise ValueError("case_log_path is required when appending a decompose case")
    path = Path(case_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
        fh.write("\n")
    return str(path)


def _load_manifest(
    manifest_path: str,
    manifest_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if manifest_data is not None:
        return dict(manifest_data)
    if not manifest_path:
        return {}
    path = Path(manifest_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _layer_record(output_dir: str, item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": str(item.get("id", "")),
        "name": str(item.get("name", "")),
        "semantic_path": str(item.get("semantic_path", "") or ""),
        "file": _artifact_path(output_dir, str(item.get("file", "") or "")),
        "z_index": int(item.get("z_index", 0) or 0),
        "quality_status": str(item.get("quality_status", "") or ""),
        "area_pct": float(item.get("area_pct", 0.0) or 0.0),
        "bbox": item.get("bbox"),
        "parent_layer_id": item.get("parent_layer_id"),
    }


def _artifact_path(output_dir: str, value: str) -> str:
    if not value:
        return ""
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str(Path(output_dir) / path)


def _is_residual_layer(layer: Mapping[str, Any]) -> bool:
    return (
        layer.get("name") == "residual"
        or layer.get("semantic_path") == "residual"
        or layer.get("quality_status") == "residual"
    )


def _residual_from_layers(layers: Sequence[Mapping[str, Any]]) -> tuple[str, float]:
    for layer in layers:
        if _is_residual_layer(layer):
            return str(layer.get("file", "") or ""), float(layer.get("area_pct", 0.0) or 0.0)
    return "", 0.0


def _quality_record(
    layers: Sequence[Mapping[str, Any]],
    detection_report: Mapping[str, Any],
    residual_pct: float,
) -> dict[str, Any]:
    non_residual = [layer for layer in layers if not _is_residual_layer(layer)]
    if residual_pct:
        claimed_pct = round(_clamp_pct(100.0 - residual_pct), 4)
    else:
        claimed_pct = round(
            _clamp_pct(
                sum(float(layer.get("area_pct", 0.0) or 0.0) for layer in non_residual)
            ),
            4,
        )
    empty_layer_count = sum(
        1 for layer in non_residual if float(layer.get("area_pct", 0.0) or 0.0) <= 0.0
    )
    missed = _report_count(detection_report, "missed")
    suspect = _report_count(detection_report, "suspect")
    return {
        "quality_score": None,
        "layer_coverage": {
            "claimed_pct": claimed_pct,
            "residual_pct": float(residual_pct),
            "missed_hint_count": missed,
            "suspect_hint_count": suspect,
        },
        "alpha_quality": {
            "mean_edge_softness": None,
            "hard_edge_ratio": None,
            "empty_layer_count": empty_layer_count,
            "opaque_noise_ratio": None,
        },
        "over_split": {"score": None, "evidence": []},
        "under_split": {"score": None, "evidence": []},
        "semantic_mismatch": {"score": None, "evidence": []},
        "residual_leakage": {
            "score": None,
            "residual_pct": float(residual_pct),
            "evidence": [],
        },
    }


def _clamp_pct(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def _report_count(detection_report: Mapping[str, Any], key: str) -> int:
    value = detection_report.get(key)
    if isinstance(value, int):
        return value
    per_entity = detection_report.get("per_entity", []) or []
    return sum(1 for item in per_entity if isinstance(item, Mapping) and item.get("status") == key)


def _debug_artifacts_record(debug_artifacts: Mapping[str, Any] | None) -> dict[str, Any]:
    raw = dict(debug_artifacts or {})
    return {
        "qa_contact_sheet_path": str(raw.get("qa_contact_sheet_path", "") or ""),
        "qa_prompt_path": str(raw.get("qa_prompt_path", "") or ""),
        "mask_overlay_paths": [str(item) for item in raw.get("mask_overlay_paths", []) or []],
        "log_path": str(raw.get("log_path", "") or ""),
    }


def _make_case_id(
    *,
    created_at: str,
    source_image: str,
    mode: str,
    provider: str,
    model: str,
    tradition: str,
    output_dir: str,
    manifest_path: str,
    target_layer_hints: Sequence[Mapping[str, Any]],
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
            source_image,
            mode,
            provider,
            model,
            tradition,
            output_dir,
            manifest_path,
            json.dumps(list(target_layer_hints), sort_keys=True, separators=(",", ":")),
        ]
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"decompose_{stamp}_{digest}"
