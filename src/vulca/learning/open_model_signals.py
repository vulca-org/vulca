"""Safe open-model signal extraction records for learning cases.

This module does not download weights or call model providers. It builds a
reviewable signal-record layer around case examples, with optional injected
runners for tests or explicitly enabled local experiments.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from vulca.learning.tiny_dataset import build_tiny_dataset_examples
from vulca.learning.training_effectiveness import (
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
)


SCHEMA_VERSION = 1
SIGNAL_RECORD_CASE_TYPE = "learning_open_model_signal_record"
SIGNAL_REPORT_CASE_TYPE = "learning_open_model_signal_report"
MODEL_CATALOG_CASE_TYPE = "learning_open_source_model_catalog"
DEFAULT_MODEL_CATALOG = Path(
    "docs/benchmarks/learning/open_source_model_catalog_v1.json"
)
DEFAULT_OUTPUT_DIR = Path("build/open_model_signal_adapter")
DEFAULT_SIGNAL_OUTPUT_NAME = "open_model_signals.jsonl"
DEFAULT_REPORT_NAME = "open_model_signal_report.json"
DEFAULT_MODEL_IDS: tuple[str, ...] = (
    "florence_2",
    "segment_anything_sam_vit",
)
ELIGIBLE_INTAKE_STATUSES: frozenset[str] = frozenset({"recommended_pilot"})

SignalRunner = Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]]
LocalRunnerFactory = Callable[..., SignalRunner]


def run_open_model_signal_adapter(
    *,
    repo_root: str | Path,
    output_path: str | Path | None = None,
    report_path: str | Path | None = None,
    model_catalog_path: str | Path = DEFAULT_MODEL_CATALOG,
    case_source_manifest_path: str | Path = DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    model_ids: Sequence[str] = DEFAULT_MODEL_IDS,
    include_local_seeds: bool = True,
    runners: Mapping[str, SignalRunner] | None = None,
    enable_local_runners: Sequence[str] = (),
    local_runner_factories: Mapping[str, LocalRunnerFactory] | None = None,
    max_examples: int | None = None,
    allow_weight_download: bool = False,
    florence_model_id: str = "microsoft/Florence-2-base",
    florence_device: str = "auto",
    sam_checkpoint: str | Path | None = None,
    sam_model_type: str = "vit_b",
    sam_device: str = "auto",
    sam_points_per_side: int = 16,
    private_asset_map_paths: Sequence[str | Path] = (),
) -> dict[str, Any]:
    """Write dry-run or injected open-model signal records and a summary report."""
    if max_examples is not None and max_examples < 0:
        raise ValueError("max_examples must be >= 0")

    root = Path(repo_root)
    resolved_catalog_path = _resolve_repo_path(root, model_catalog_path)
    resolved_manifest_path = _resolve_repo_path(root, case_source_manifest_path)
    resolved_output_path = Path(output_path) if output_path else (
        root / DEFAULT_OUTPUT_DIR / DEFAULT_SIGNAL_OUTPUT_NAME
    )
    resolved_report_path = Path(report_path) if report_path else (
        root / DEFAULT_OUTPUT_DIR / DEFAULT_REPORT_NAME
    )

    examples = build_tiny_dataset_examples(
        repo_root=root,
        case_source_manifest_path=resolved_manifest_path,
        include_local_seeds=include_local_seeds,
    )
    if max_examples is not None:
        examples = examples[:max_examples]
    model_specs = select_open_model_specs(
        resolved_catalog_path,
        model_ids=model_ids,
    )
    runner_map = _build_runner_map(
        root,
        runners=runners,
        enable_local_runners=enable_local_runners,
        local_runner_factories=local_runner_factories,
        model_ids=[str(item.get("id") or "") for item in model_specs],
        allow_weight_download=allow_weight_download,
        florence_model_id=florence_model_id,
        florence_device=florence_device,
        sam_checkpoint=sam_checkpoint,
        sam_model_type=sam_model_type,
        sam_device=sam_device,
        sam_points_per_side=sam_points_per_side,
        private_asset_map_paths=private_asset_map_paths,
    )
    records = build_open_model_signal_records(
        examples,
        model_specs=model_specs,
        runners=runner_map,
    )

    _write_jsonl(resolved_output_path, records)
    report = build_open_model_signal_report(
        records,
        examples=examples,
        model_specs=model_specs,
        repo_root=root,
        model_catalog_path=resolved_catalog_path,
        case_source_manifest_path=resolved_manifest_path,
        output_path=resolved_output_path,
        report_path=resolved_report_path,
        include_local_seeds=include_local_seeds,
        enable_local_runners=enable_local_runners,
        max_examples=max_examples,
        weight_download_enabled=allow_weight_download,
        private_asset_map_count=len(private_asset_map_paths),
    )
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def select_open_model_specs(
    model_catalog_path: str | Path,
    *,
    model_ids: Sequence[str] = DEFAULT_MODEL_IDS,
) -> tuple[dict[str, Any], ...]:
    """Select recommended-pilot model specs from the open model catalog."""
    catalog = load_open_model_catalog(model_catalog_path)
    models = catalog.get("models")
    if not isinstance(models, list):
        raise ValueError("open model catalog models must be a list")

    model_by_id = {
        str(item.get("id") or ""): dict(item)
        for item in models
        if isinstance(item, Mapping)
    }
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw_model_id in model_ids:
        model_id = str(raw_model_id)
        if model_id in seen:
            continue
        seen.add(model_id)
        model = model_by_id.get(model_id)
        if model is None:
            raise ValueError(f"unknown open model id {model_id!r}")
        status = str(model.get("intake_status") or "")
        if status not in ELIGIBLE_INTAKE_STATUSES:
            raise ValueError(
                f"open model {model_id!r} is not eligible for signal pilot: "
                f"intake_status={status!r}"
            )
        if bool(model.get("default_runtime_enabled")):
            raise ValueError(
                f"open model {model_id!r} must not be enabled by default"
            )
        selected.append(model)
    return tuple(selected)


def load_open_model_catalog(path: str | Path) -> dict[str, Any]:
    """Load and validate the open model catalog wrapper."""
    catalog_path = Path(path)
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(catalog, Mapping):
        raise ValueError("open model catalog must be a JSON object")
    if catalog.get("case_type") != MODEL_CATALOG_CASE_TYPE:
        raise ValueError(
            f"open model catalog case_type must be {MODEL_CATALOG_CASE_TYPE!r}"
        )
    return dict(catalog)


def build_open_model_signal_records(
    examples: Sequence[Mapping[str, Any]],
    *,
    model_specs: Sequence[Mapping[str, Any]],
    runners: Mapping[str, SignalRunner] | None = None,
) -> list[dict[str, Any]]:
    """Build reviewable signal records for examples targeted by each model."""
    runner_by_model = dict(runners or {})
    records: list[dict[str, Any]] = []

    for example in examples:
        source_case = _mapping(example.get("source_case"))
        case_type = str(source_case.get("case_type") or "")
        for model_spec in model_specs:
            target_case_types = {
                str(item) for item in model_spec.get("target_case_types", []) or []
            }
            if case_type not in target_case_types:
                continue
            records.append(
                _build_signal_record(
                    example,
                    model_spec=model_spec,
                    runner=runner_by_model.get(str(model_spec.get("id") or "")),
                )
            )

    return records


def build_open_model_signal_report(
    records: Sequence[Mapping[str, Any]],
    *,
    examples: Sequence[Mapping[str, Any]],
    model_specs: Sequence[Mapping[str, Any]],
    repo_root: str | Path,
    model_catalog_path: str | Path,
    case_source_manifest_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    include_local_seeds: bool,
    enable_local_runners: Sequence[str] = (),
    max_examples: int | None = None,
    weight_download_enabled: bool = False,
    private_asset_map_count: int = 0,
) -> dict[str, Any]:
    """Summarize signal-record coverage and safety policy."""
    counts_by_model: Counter[str] = Counter()
    counts_by_case_type: Counter[str] = Counter()
    counts_by_source_kind: Counter[str] = Counter()
    for record in records:
        counts_by_model[str(_mapping(record.get("model")).get("id") or "unknown")] += 1
        counts_by_case_type[
            str(_mapping(record.get("source_case")).get("case_type") or "unknown")
        ] += 1
        counts_by_source_kind[
            str(_mapping(record.get("source")).get("kind") or "unknown")
        ] += 1

    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": SIGNAL_REPORT_CASE_TYPE,
        "status": "needs_human_review",
        "inputs": {
            "repo_root": _safe_repo_root(repo_root),
            "model_catalog_path": _safe_repo_path(model_catalog_path),
            "case_source_manifest_path": _safe_repo_path(case_source_manifest_path),
            "include_local_seeds": bool(include_local_seeds),
            "model_ids": [str(item.get("id") or "") for item in model_specs],
            "enable_local_runners": [str(item) for item in enable_local_runners],
            "max_examples": max_examples,
            "private_asset_map_count": int(private_asset_map_count),
        },
        "artifacts": {
            "output_path": _safe_artifact_path(repo_root, output_path),
            "report_path": _safe_artifact_path(repo_root, report_path),
        },
        "example_count": len(examples),
        "record_count": len(records),
        "counts_by_model": dict(sorted(counts_by_model.items())),
        "counts_by_case_type": dict(sorted(counts_by_case_type.items())),
        "counts_by_source_kind": dict(sorted(counts_by_source_kind.items())),
        "training_use": {
            "default_training_input": False,
            "requires_manual_review_for_training_labels": True,
            "review_status": "needs_human_review",
        },
        "runtime": {
            "downloads_weights": False,
            "weight_download_enabled": bool(weight_download_enabled),
            "calls_model_provider": False,
            "uses_injected_runner": _uses_injected_runner(records),
            "uses_local_runner": _uses_local_runner(records),
            "default_runtime_enabled": False,
        },
    }


def _build_signal_record(
    example: Mapping[str, Any],
    *,
    model_spec: Mapping[str, Any],
    runner: SignalRunner | None,
) -> dict[str, Any]:
    source_case = _mapping(example.get("source_case"))
    source = _safe_source_summary(_mapping(example.get("source")))
    input_case = _mapping(_mapping(example.get("input")).get("case_record"))
    model_id = str(model_spec.get("id") or "")
    runner_output = dict(runner(example, model_spec)) if runner is not None else {}
    if runner_output:
        signals = dict(runner_output)
        signals.setdefault("signal_source", "injected_runner")
    else:
        signals = _dry_run_signals(input_case, model_spec=model_spec)
    output_policy = str(model_spec.get("output_training_policy") or "")

    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": SIGNAL_RECORD_CASE_TYPE,
        "signal_id": _make_signal_id(example, model_id),
        "example_id": str(example.get("example_id") or ""),
        "source": source,
        "source_case": {
            "case_type": str(source_case.get("case_type") or ""),
            "case_id": str(source_case.get("case_id") or ""),
            "schema_version": int(source_case.get("schema_version") or 0),
        },
        "model": _safe_model_summary(model_spec),
        "input_summary": _input_summary(input_case),
        "signals": signals,
        "training_use": {
            "default_training_input": False,
            "requires_manual_review_for_training_labels": bool(
                model_spec.get("requires_manual_review_for_training_labels")
            ),
            "review_status": "needs_human_review",
            "output_training_policy": output_policy,
        },
    }


def _dry_run_signals(
    case_record: Mapping[str, Any],
    *,
    model_spec: Mapping[str, Any],
) -> dict[str, Any]:
    model_role = str(model_spec.get("model_role") or "")
    signal_families = {
        "vision_caption_grounding_ocr": [
            "caption_candidates",
            "ocr_text_presence",
            "dense_region_description",
        ],
        "mask_proposal": [
            "mask_count_estimate",
            "boundary_complexity",
            "mask_coverage_candidates",
        ],
        "text_grounded_detection": [
            "grounded_box_candidates",
            "object_coverage",
        ],
    }.get(model_role, ["quality_signal"])

    return {
        "status": "dry_run_pending_model_execution",
        "signal_source": "dry_run",
        "model_role": model_role,
        "planned_signal_families": signal_families,
        "case_features": {
            "has_source_image": bool(case_record.get("source_image")),
            "has_outputs": bool(case_record.get("outputs")),
            "has_quality_block": bool(case_record.get("quality")),
            "has_layer_plan": bool(
                _mapping(_mapping(case_record.get("inputs")).get("layer_plan"))
            ),
        },
    }


def _build_runner_map(
    repo_root: Path,
    *,
    runners: Mapping[str, SignalRunner] | None,
    enable_local_runners: Sequence[str],
    local_runner_factories: Mapping[str, LocalRunnerFactory] | None,
    model_ids: Sequence[str],
    allow_weight_download: bool,
    florence_model_id: str,
    florence_device: str,
    sam_checkpoint: str | Path | None,
    sam_model_type: str,
    sam_device: str,
    sam_points_per_side: int,
    private_asset_map_paths: Sequence[str | Path],
) -> dict[str, SignalRunner]:
    runner_map = dict(runners or {})
    model_id_set = {str(item) for item in model_ids}
    factories = dict(local_runner_factories or {})
    for raw_model_id in enable_local_runners:
        model_id = str(raw_model_id)
        if model_id not in model_id_set:
            raise ValueError(
                f"local runner {model_id!r} was enabled but the model is not selected"
            )
        if model_id in runner_map:
            raise ValueError(f"runner for model {model_id!r} is already provided")
        factory = factories.get(model_id)
        if factory is None:
            if model_id == "florence_2":
                from vulca.learning.florence_signal_runner import (
                    build_florence2_signal_runner,
                )

                factory = build_florence2_signal_runner
                factory_kwargs = {
                    "repo_root": repo_root,
                    "allow_weight_download": allow_weight_download,
                    "model_id": florence_model_id,
                    "device": florence_device,
                    "private_asset_map_paths": tuple(private_asset_map_paths),
                }
            elif model_id == "segment_anything_sam_vit":
                from vulca.learning.sam_signal_runner import (
                    build_sam_vit_signal_runner,
                )

                factory = build_sam_vit_signal_runner
                factory_kwargs = {
                    "repo_root": repo_root,
                    "checkpoint_path": sam_checkpoint,
                    "model_type": sam_model_type,
                    "device": sam_device,
                    "points_per_side": sam_points_per_side,
                    "private_asset_map_paths": tuple(private_asset_map_paths),
                }
            else:
                raise ValueError(f"no local runner is available for model {model_id!r}")
        else:
            factory_kwargs = _local_runner_factory_kwargs(
                model_id,
                repo_root=repo_root,
                allow_weight_download=allow_weight_download,
                florence_model_id=florence_model_id,
                florence_device=florence_device,
                sam_checkpoint=sam_checkpoint,
                sam_model_type=sam_model_type,
                sam_device=sam_device,
                sam_points_per_side=sam_points_per_side,
                private_asset_map_paths=private_asset_map_paths,
            )
        runner_map[model_id] = factory(**factory_kwargs)
    return runner_map


def _local_runner_factory_kwargs(
    model_id: str,
    *,
    repo_root: Path,
    allow_weight_download: bool,
    florence_model_id: str,
    florence_device: str,
    sam_checkpoint: str | Path | None,
    sam_model_type: str,
    sam_device: str,
    sam_points_per_side: int,
    private_asset_map_paths: Sequence[str | Path],
) -> dict[str, Any]:
    if model_id == "florence_2":
        return {
            "repo_root": repo_root,
            "allow_weight_download": allow_weight_download,
            "model_id": florence_model_id,
            "device": florence_device,
            "private_asset_map_paths": tuple(private_asset_map_paths),
        }
    if model_id == "segment_anything_sam_vit":
        return {
            "repo_root": repo_root,
            "checkpoint_path": sam_checkpoint,
            "model_type": sam_model_type,
            "device": sam_device,
            "points_per_side": sam_points_per_side,
            "private_asset_map_paths": tuple(private_asset_map_paths),
        }
    return {
        "repo_root": repo_root,
        "private_asset_map_paths": tuple(private_asset_map_paths),
    }


def _safe_model_summary(model_spec: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": str(model_spec.get("id") or ""),
        "name": str(model_spec.get("name") or ""),
        "license": str(model_spec.get("license") or ""),
        "license_risk": str(model_spec.get("license_risk") or ""),
        "model_role": str(model_spec.get("model_role") or ""),
        "output_training_policy": str(model_spec.get("output_training_policy") or ""),
        "default_runtime_enabled": bool(model_spec.get("default_runtime_enabled")),
    }


def _safe_source_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    summary = {
        "kind": str(source.get("kind") or ""),
        "source_id": str(source.get("source_id") or ""),
        "privacy_scope": str(source.get("privacy_scope") or ""),
        "curation_status": str(source.get("curation_status") or ""),
    }
    if source.get("preferred_split"):
        summary["preferred_split"] = str(source.get("preferred_split") or "")
    if source.get("split"):
        summary["split"] = str(source.get("split") or "")
    return {key: value for key, value in summary.items() if value}


def _input_summary(case_record: Mapping[str, Any]) -> dict[str, Any]:
    inputs = _mapping(case_record.get("inputs"))
    outputs = _mapping(case_record.get("outputs"))
    quality = _mapping(case_record.get("quality"))
    return {
        "case_type": str(case_record.get("case_type") or ""),
        "case_id": str(case_record.get("case_id") or ""),
        "has_source_image": bool(case_record.get("source_image")),
        "source_image_ref_kind": _ref_kind(str(case_record.get("source_image") or "")),
        "input_keys": sorted(str(key) for key in inputs),
        "output_keys": sorted(str(key) for key in outputs),
        "quality_keys": sorted(str(key) for key in quality),
    }


def _ref_kind(ref: str) -> str:
    if not ref:
        return "missing"
    if ref.startswith("private://"):
        return "private_uri"
    if ref.startswith("http://") or ref.startswith("https://"):
        return "remote_url"
    if Path(ref).is_absolute():
        return "absolute_path"
    return "repo_relative"


def _make_signal_id(example: Mapping[str, Any], model_id: str) -> str:
    seed = json.dumps(
        {
            "example_id": str(example.get("example_id") or ""),
            "model_id": model_id,
            "case_type": SIGNAL_RECORD_CASE_TYPE,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"open_signal_{digest}"


def _write_jsonl(path: str | Path, records: Sequence[Mapping[str, Any]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
            fh.write("\n")


def _resolve_repo_path(repo_root: str | Path, path: str | Path) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = Path(repo_root) / resolved
    return resolved


def _safe_repo_path(path: str | Path) -> str:
    parts = Path(path).parts
    if "docs" in parts:
        docs_index = parts.index("docs")
        return str(Path(*parts[docs_index:]))
    return Path(path).name


def _safe_repo_root(path: str | Path) -> str:
    return Path(path).name


def _safe_artifact_path(repo_root: str | Path, path: str | Path) -> str:
    artifact_path = Path(path)
    try:
        return str(artifact_path.relative_to(Path(repo_root)))
    except ValueError:
        return str(artifact_path)


def _uses_injected_runner(records: Sequence[Mapping[str, Any]]) -> bool:
    for record in records:
        if str(_mapping(record.get("signals")).get("signal_source") or "") == (
            "injected_runner"
        ):
            return True
    return False


def _uses_local_runner(records: Sequence[Mapping[str, Any]]) -> bool:
    for record in records:
        if str(_mapping(record.get("signals")).get("signal_source") or "") == (
            "local_runner"
        ):
            return True
    return False


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
