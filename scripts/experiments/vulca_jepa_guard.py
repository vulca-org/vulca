#!/usr/bin/env python3
"""Prototype non-blocking Vulca JEPA audit guards."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SIGLIP_PROBABILITY_MAX = 0.001


def _load_json(path: Path | str) -> Any:
    return json.loads(Path(path).read_text())


def sample_family(sample_id: str) -> str:
    for family in ("gongbi", "xieyi", "japanese"):
        if family in sample_id:
            return family
    return sample_id.split("_", 1)[0]


def _dinov2_by_id(dinov2: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["sample_id"]: row for row in dinov2.get("anomaly_ranking", [])}


def _siglip_by_id(siglip: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["sample_id"]: row for row in siglip.get("samples", [])}


def _gallery_promptfix_samples(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        sample
        for sample in inventory.get("samples", [])
        if sample.get("group") == "gallery_promptfix"
        and sample.get("audit_set") == "core"
        and sample.get("usable_for_embedding") is True
    ]


def _subject_drift_warning(
    sample: dict[str, Any],
    dino: dict[str, Any],
    siglip: dict[str, Any],
) -> dict[str, Any] | None:
    sample_id = sample["sample_id"]
    nearest_id = dino.get("nearest_sample_id")
    probability = siglip.get("probability")
    text_source = siglip.get("text_source")
    if nearest_id is None or probability is None:
        return None

    same_family = sample_family(sample_id) == sample_family(str(nearest_id))
    low_text_alignment = text_source == "prompt" and float(probability) < SIGLIP_PROBABILITY_MAX
    if same_family or not low_text_alignment:
        return None

    return {
        "sample_id": sample_id,
        "warning_type": "subject_drift_warning",
        "severity": "warning",
        "action": "warn_only",
        "message": "DINOv2 nearest neighbor points to a different prompt family while SigLIP prompt-image score is very low.",
        "signals": {
            "sample_family": sample_family(sample_id),
            "nearest_sample_id": nearest_id,
            "nearest_family": sample_family(str(nearest_id)),
            "nearest_distance": dino.get("nearest_distance"),
            "siglip_probability": probability,
            "siglip_logit": siglip.get("logit"),
            "siglip_text_source": text_source,
        },
    }


def build_guard_result(
    *,
    inventory_path: Path | str,
    dinov2_audit_path: Path | str,
    siglip_audit_path: Path | str,
) -> dict[str, Any]:
    inventory = _load_json(inventory_path)
    dinov2 = _load_json(dinov2_audit_path)
    siglip = _load_json(siglip_audit_path)
    dino_by_id = _dinov2_by_id(dinov2)
    siglip_by_id = _siglip_by_id(siglip)

    samples = _gallery_promptfix_samples(inventory)
    warnings: list[dict[str, Any]] = []
    evaluated: list[dict[str, Any]] = []
    for sample in samples:
        sample_id = sample["sample_id"]
        dino = dino_by_id.get(sample_id, {})
        siglip_row = siglip_by_id.get(sample_id, {})
        evaluated.append(
            {
                "sample_id": sample_id,
                "sample_family": sample_family(sample_id),
                "nearest_sample_id": dino.get("nearest_sample_id"),
                "nearest_family": sample_family(str(dino.get("nearest_sample_id"))) if dino.get("nearest_sample_id") else None,
                "siglip_probability": siglip_row.get("probability"),
                "siglip_text_source": siglip_row.get("text_source"),
            }
        )
        warning = _subject_drift_warning(sample, dino, siglip_row)
        if warning:
            warnings.append(warning)

    return {
        "schema_version": "vulca_jepa_guard.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "ok",
        "non_blocking": True,
        "guard_scope": "gallery_promptfix",
        "rules": {
            "subject_drift_warning": {
                "action": "warn_only",
                "siglip_probability_max": SIGLIP_PROBABILITY_MAX,
                "requires_prompt_text": True,
                "requires_nearest_family_mismatch": True,
            }
        },
        "inputs": {
            "inventory": str(inventory_path),
            "dinov2_audit": str(dinov2_audit_path),
            "siglip_audit": str(siglip_audit_path),
        },
        "samples_evaluated": len(samples),
        "warnings_total": len(warnings),
        "warnings": warnings,
        "evaluated_samples": evaluated,
    }


def build_eval_metadata(guard_result: dict[str, Any]) -> dict[str, Any]:
    warnings = guard_result.get("warnings", [])
    compact_warnings = [
        {
            "sample_id": warning.get("sample_id"),
            "type": warning.get("warning_type"),
            "severity": warning.get("severity"),
            "action": warning.get("action"),
            "message": warning.get("message"),
            "signals": warning.get("signals", {}),
        }
        for warning in warnings
    ]

    return {
        "schema_version": "vulca_eval_metadata.v1",
        "generated_at": guard_result.get("generated_at"),
        "source_schema_version": guard_result.get("schema_version"),
        "guards": {
            "vulca_jepa_subject_drift": {
                "status": "warning" if compact_warnings else "ok",
                "non_blocking": guard_result.get("non_blocking", True),
                "scope": guard_result.get("guard_scope"),
                "rules": guard_result.get("rules", {}),
                "samples_evaluated": guard_result.get("samples_evaluated", 0),
                "warnings_total": guard_result.get("warnings_total", len(compact_warnings)),
                "warnings": compact_warnings,
            }
        },
    }


def write_guard(
    *,
    inventory_path: Path | str,
    dinov2_audit_path: Path | str,
    siglip_audit_path: Path | str,
    out: Path | str,
    metadata_out: Path | str | None = None,
) -> dict[str, Any]:
    result = build_guard_result(
        inventory_path=inventory_path,
        dinov2_audit_path=dinov2_audit_path,
        siglip_audit_path=siglip_audit_path,
    )
    output_path = Path(out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    if metadata_out:
        metadata_path = Path(metadata_out)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(
            json.dumps(build_eval_metadata(result), ensure_ascii=False, indent=2) + "\n"
        )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--dinov2-audit", required=True, type=Path)
    parser.add_argument("--siglip-audit", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--metadata-out", type=Path)
    args = parser.parse_args(argv)

    result = write_guard(
        inventory_path=args.inventory,
        dinov2_audit_path=args.dinov2_audit,
        siglip_audit_path=args.siglip_audit,
        out=args.out,
        metadata_out=args.metadata_out,
    )
    print(f"wrote {args.out}")
    if args.metadata_out:
        print(f"wrote_metadata {args.metadata_out}")
    print(f"guard_scope: {result['guard_scope']}")
    print(f"samples_evaluated: {result['samples_evaluated']}")
    print(f"warnings: {result['warnings_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
