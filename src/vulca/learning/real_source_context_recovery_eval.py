"""Evaluate dry-run impact from recovered real-user source context."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from vulca.learning.dry_run_decision_router import run_dry_run_decision_router
from vulca.learning.real_source_context_recovery_audit import (
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    run_real_source_context_recovery_audit,
)
from vulca.learning.source_context_signals import write_source_context_signal_pack
from vulca.learning.tiny_dataset import DATASET_SPLITS


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_real_source_context_recovery_eval_report"
DEFAULT_OUTPUT_DIR = Path("build/real_source_context_recovery_eval")
DEFAULT_REPORT_NAME = "real_source_context_recovery_eval_report.json"
BASELINE_DIR_NAME = "baseline"
RECOVERED_DIR_NAME = "recovered"
RECOVERY_DIR_NAME = "recovery"
SOURCE_CONTEXT_GAP_TAG = "no_source_context_for_required_source"


def run_real_source_context_recovery_eval(
    *,
    repo_root: str | Path,
    case_source_manifest_path: str | Path = DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    artifact_search_roots: Sequence[str | Path],
    image_search_roots: Sequence[str | Path],
    artifact_filename_aliases: Mapping[str, str] | None = None,
    image_filename_aliases: Mapping[str, str] | None = None,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    source_dependency_manifest_path: str | Path | None = None,
    include_local_seeds: bool = True,
    eval_split: str = "test",
    train_split: str = "train",
) -> dict[str, Any]:
    """Recover private source context and compare dry-run routing before/after."""
    _validate_split(eval_split, label="eval_split")
    _validate_split(train_split, label="train_split")

    root = Path(repo_root).resolve()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = Path(report_path) if report_path else output / DEFAULT_REPORT_NAME

    baseline = _run_signal_router_pair(
        repo_root=root,
        output_dir=output / BASELINE_DIR_NAME,
        case_source_manifest_path=case_source_manifest_path,
        private_asset_map_paths=(),
        source_dependency_manifest_path=source_dependency_manifest_path,
        include_local_seeds=include_local_seeds,
        eval_split=eval_split,
        train_split=train_split,
    )
    recovery_output = output / RECOVERY_DIR_NAME
    recovery_report = run_real_source_context_recovery_audit(
        repo_root=root,
        case_source_manifest_path=case_source_manifest_path,
        artifact_search_roots=artifact_search_roots,
        image_search_roots=image_search_roots,
        artifact_filename_aliases=artifact_filename_aliases,
        image_filename_aliases=image_filename_aliases,
        output_dir=recovery_output,
        include_local_seeds=include_local_seeds,
        train_split=train_split,
    )
    recovery_artifacts = _mapping(recovery_report.get("artifacts"))
    private_asset_maps = (
        recovery_output / str(recovery_artifacts["source_artifact_private_asset_map_path"]),
        recovery_output / str(recovery_artifacts["source_image_private_asset_map_path"]),
    )
    recovered = _run_signal_router_pair(
        repo_root=root,
        output_dir=output / RECOVERED_DIR_NAME,
        case_source_manifest_path=case_source_manifest_path,
        private_asset_map_paths=private_asset_maps,
        source_dependency_manifest_path=source_dependency_manifest_path,
        include_local_seeds=include_local_seeds,
        eval_split=eval_split,
        train_split=train_split,
    )

    recovered_eval_cases = _recovered_eval_cases(
        baseline["decision_records"],
        recovered["decision_records"],
    )
    delta = _delta(baseline, recovered)
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": _status(delta, recovered_eval_cases),
        "inputs": {
            "repo_root": root.name,
            "case_source_manifest_path": _safe_path(root, case_source_manifest_path),
            "artifact_search_root_count": len(artifact_search_roots),
            "image_search_root_count": len(image_search_roots),
            "artifact_filename_alias_count": len(artifact_filename_aliases or {}),
            "image_filename_alias_count": len(image_filename_aliases or {}),
            "source_dependency_manifest_path": _safe_path(
                root,
                source_dependency_manifest_path,
            )
            if source_dependency_manifest_path
            else "",
            "include_local_seeds": bool(include_local_seeds),
            "eval_split": eval_split,
            "train_split": train_split,
        },
        "artifacts": {
            "report_path": _artifact_name(resolved_report_path, output),
            "recovery_report_path": str(
                Path(RECOVERY_DIR_NAME)
                / str(recovery_artifacts.get("report_path") or "")
            ),
            "baseline_source_context_signal_report_path": str(
                Path(BASELINE_DIR_NAME)
                / "source_context"
                / "source_context_signal_report.json"
            ),
            "baseline_dry_run_report_path": str(
                Path(BASELINE_DIR_NAME) / "dry_run" / "report.json"
            ),
            "recovered_source_context_signal_report_path": str(
                Path(RECOVERED_DIR_NAME)
                / "source_context"
                / "source_context_signal_report.json"
            ),
            "recovered_dry_run_report_path": str(
                Path(RECOVERED_DIR_NAME) / "dry_run" / "report.json"
            ),
        },
        "recovery": _compact_recovery(recovery_report),
        "baseline": _compact_run(baseline),
        "recovered": _compact_run(recovered),
        "delta": delta,
        "recovered_eval_case_count": len(recovered_eval_cases),
        "recovered_eval_cases": recovered_eval_cases,
        "safe_handling": {
            "private_asset_maps_contain_local_paths": True,
            "do_not_commit_private_asset_maps": True,
            "report_omits_local_paths": True,
            "report_omits_private_refs": True,
            "copies_raw_source_text": False,
            "calls_model_provider": False,
            "downloads_weights": False,
        },
    }
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _run_signal_router_pair(
    *,
    repo_root: Path,
    output_dir: Path,
    case_source_manifest_path: str | Path,
    private_asset_map_paths: Sequence[str | Path],
    source_dependency_manifest_path: str | Path | None,
    include_local_seeds: bool,
    eval_split: str,
    train_split: str,
) -> dict[str, Any]:
    source_context_output = output_dir / "source_context"
    signal_report = write_source_context_signal_pack(
        repo_root=repo_root,
        case_source_manifest_path=case_source_manifest_path,
        private_asset_map_paths=private_asset_map_paths,
        output_path=source_context_output / "source_context_signals.promoted.jsonl",
        manifest_path=source_context_output
        / "source_context_signal_promotion_manifest.json",
        report_path=source_context_output / "source_context_signal_report.json",
        include_local_seeds=include_local_seeds,
    )
    dry_run_output = output_dir / "dry_run"
    dry_run_report = run_dry_run_decision_router(
        repo_root=repo_root,
        output_dir=dry_run_output,
        report_path=dry_run_output / "report.json",
        case_source_manifest_path=case_source_manifest_path,
        source_dependency_manifest_path=source_dependency_manifest_path,
        auxiliary_signal_manifest_path=source_context_output
        / "source_context_signal_promotion_manifest.json",
        include_local_seeds=include_local_seeds,
        eval_split=eval_split,
        train_split=train_split,
    )
    decision_records = _load_jsonl(
        _mapping(dry_run_report.get("artifacts")).get("decision_path", "")
    )
    return {
        "source_context_signal_report": signal_report,
        "dry_run_report": dry_run_report,
        "decision_records": decision_records,
    }


def _compact_recovery(recovery_report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": str(recovery_report.get("status") or ""),
        "summary": dict(_mapping(recovery_report.get("summary"))),
        "source_artifact_recovery": dict(
            _mapping(recovery_report.get("source_artifact_recovery"))
        ),
        "source_image_recovery": dict(
            _mapping(recovery_report.get("source_image_recovery"))
        ),
    }


def _compact_run(run: Mapping[str, Any]) -> dict[str, Any]:
    signal_summary = _mapping(
        _mapping(run.get("source_context_signal_report")).get("summary")
    )
    dry_summary = _mapping(_mapping(run.get("dry_run_report")).get("summary"))
    return {
        "source_context_signal_count": int(
            signal_summary.get("promoted_signal_count") or 0
        ),
        "source_context_signal_example_count": int(
            signal_summary.get("example_count") or 0
        ),
        "fallback_agent_count": int(dry_summary.get("fallback_agent_count") or 0),
        "data_gap_counts": dict(_mapping(dry_summary.get("data_gap_counts"))),
    }


def _delta(
    baseline: Mapping[str, Any],
    recovered: Mapping[str, Any],
) -> dict[str, int]:
    baseline_compact = _compact_run(baseline)
    recovered_compact = _compact_run(recovered)
    baseline_gap_count = _data_gap_count(baseline_compact)
    recovered_gap_count = _data_gap_count(recovered_compact)
    baseline_fallback = int(baseline_compact.get("fallback_agent_count") or 0)
    recovered_fallback = int(recovered_compact.get("fallback_agent_count") or 0)
    baseline_signal_count = int(
        baseline_compact.get("source_context_signal_count") or 0
    )
    recovered_signal_count = int(
        recovered_compact.get("source_context_signal_count") or 0
    )
    return {
        "source_context_signal_count": recovered_signal_count - baseline_signal_count,
        "fallback_agent_count": recovered_fallback - baseline_fallback,
        "fallback_agent_count_reduction": baseline_fallback - recovered_fallback,
        "no_source_context_for_required_source": recovered_gap_count
        - baseline_gap_count,
        "no_source_context_for_required_source_reduction": baseline_gap_count
        - recovered_gap_count,
    }


def _recovered_eval_cases(
    baseline_decisions: Sequence[Mapping[str, Any]],
    recovered_decisions: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    recovered_by_example_id = {
        str(item.get("example_id") or ""): item for item in recovered_decisions
    }
    rows: list[dict[str, Any]] = []
    for baseline in baseline_decisions:
        example_id = str(baseline.get("example_id") or "")
        recovered = recovered_by_example_id.get(example_id)
        if recovered is None:
            continue
        baseline_dispatch = _mapping(baseline.get("dispatch"))
        recovered_dispatch = _mapping(recovered.get("dispatch"))
        if not bool(baseline_dispatch.get("fallback_agent")):
            continue
        if bool(recovered_dispatch.get("fallback_agent")):
            continue
        rows.append(
            {
                "case_id": str(baseline.get("case_id") or ""),
                "case_type": str(baseline.get("source_case_type") or ""),
                "example_id": example_id,
                "removed_data_gap_tags": _list_difference(
                    baseline_dispatch.get("data_gap_tags"),
                    recovered_dispatch.get("data_gap_tags"),
                ),
                "source_context": dict(_mapping(recovered.get("source_context"))),
            }
        )
    return sorted(rows, key=lambda item: (item["case_type"], item["case_id"]))


def _status(delta: Mapping[str, Any], recovered_eval_cases: Sequence[Mapping[str, Any]]) -> str:
    if recovered_eval_cases and int(delta.get("fallback_agent_count_reduction") or 0) > 0:
        return "recovered_source_context_improves_dry_run"
    if int(delta.get("source_context_signal_count") or 0) > 0:
        return "recovered_source_context_signals_no_dispatch_change"
    return "needs_more_source_recovery"


def _data_gap_count(compact_run: Mapping[str, Any]) -> int:
    return int(
        _mapping(compact_run.get("data_gap_counts")).get(
            SOURCE_CONTEXT_GAP_TAG,
        )
        or 0
    )


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    if not path:
        return []
    records: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if isinstance(item, Mapping):
            records.append(dict(item))
    return records


def _list_difference(old_value: Any, new_value: Any) -> list[str]:
    new_items = set(_string_list(new_value))
    return [item for item in _string_list(old_value) if item not in new_items]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value]


def _safe_path(repo_root: Path, path: str | Path | None) -> str:
    if not path:
        return ""
    value = Path(path)
    if not value.is_absolute():
        value = repo_root / value
    try:
        return str(value.relative_to(repo_root))
    except ValueError:
        return value.name


def _artifact_name(path: str | Path, output_dir: str | Path) -> str:
    value = Path(path)
    try:
        return str(value.relative_to(Path(output_dir)))
    except ValueError:
        return value.name


def _validate_split(value: str, *, label: str) -> None:
    if value not in DATASET_SPLITS:
        raise ValueError(f"unsupported {label} {value!r}; expected one of {DATASET_SPLITS}")


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
