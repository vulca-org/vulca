"""Audit real user cases where source-context signals may affect tiny learning."""
from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from vulca.learning.source_context_signals import (
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    write_source_context_signal_pack,
)
from vulca.learning.tiny_action_model import TinyActionClassifier
from vulca.learning.tiny_dataset import DATASET_SPLITS, build_tiny_dataset_examples


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_real_source_context_audit_report"
DEFAULT_OUTPUT_DIR = Path("build/real_source_context_audit")
DEFAULT_REPORT_NAME = "real_source_context_audit_report.json"
DEFAULT_SIGNAL_OUTPUT_NAME = "source_context_signals.promoted.jsonl"
DEFAULT_SIGNAL_MANIFEST_NAME = "source_context_signal_promotion_manifest.json"
DEFAULT_SIGNAL_REPORT_NAME = "source_context_signal_report.json"
REAL_USER_SOURCE_KIND = "user_case_log"


def run_real_source_context_audit_report(
    *,
    repo_root: str | Path,
    case_source_manifest_path: str | Path = DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    private_asset_map_paths: Sequence[str | Path] = (),
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    include_local_seeds: bool = True,
    train_split: str = "train",
) -> dict[str, Any]:
    """Write a safe audit report for real user source-context review candidates."""
    _validate_split(train_split, label="train_split")
    root = Path(repo_root)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = Path(report_path) if report_path else output / DEFAULT_REPORT_NAME
    signal_output_path = output / DEFAULT_SIGNAL_OUTPUT_NAME
    signal_manifest_path = output / DEFAULT_SIGNAL_MANIFEST_NAME
    signal_report_path = output / DEFAULT_SIGNAL_REPORT_NAME

    signal_report = write_source_context_signal_pack(
        repo_root=root,
        case_source_manifest_path=case_source_manifest_path,
        private_asset_map_paths=private_asset_map_paths,
        output_path=signal_output_path,
        manifest_path=signal_manifest_path,
        report_path=signal_report_path,
        include_local_seeds=include_local_seeds,
    )
    examples = build_tiny_dataset_examples(
        repo_root=root,
        case_source_manifest_path=_resolve_repo_path(root, case_source_manifest_path),
        auxiliary_signal_manifest_path=signal_manifest_path,
        include_local_seeds=include_local_seeds,
    )
    no_aux_examples = _without_auxiliary_signals(examples)
    full_classifier = TinyActionClassifier.fit(examples, train_split=train_split)
    no_aux_classifier = TinyActionClassifier.fit(no_aux_examples, train_split=train_split)
    no_aux_by_id = {
        str(example.get("example_id") or ""): example for example in no_aux_examples
    }

    records = []
    for example in examples:
        source = _mapping(example.get("source"))
        if str(source.get("kind") or "") != REAL_USER_SOURCE_KIND:
            continue
        no_aux_example = no_aux_by_id[str(example.get("example_id") or "")]
        full_prediction = full_classifier.predict(example)
        no_aux_prediction = no_aux_classifier.predict(no_aux_example)
        records.append(
            _audit_record(
                example,
                full_prediction=full_prediction,
                no_aux_prediction=no_aux_prediction,
            )
        )

    records.sort(key=_record_sort_key)
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": "needs_review" if _candidate_count(records) else "no_candidates",
        "train_split": train_split,
        "inputs": {
            "repo_root": root.name,
            "case_source_manifest_path": _safe_path(case_source_manifest_path),
            "include_local_seeds": bool(include_local_seeds),
            "private_asset_map_count": len(private_asset_map_paths),
        },
        "artifacts": {
            "report_path": _safe_artifact_path(root, resolved_report_path),
            "source_context_signal_output_path": _safe_artifact_path(
                root,
                signal_output_path,
            ),
            "source_context_signal_manifest_path": _safe_artifact_path(
                root,
                signal_manifest_path,
            ),
            "source_context_signal_report_path": _safe_artifact_path(
                root,
                signal_report_path,
            ),
        },
        "source_context_signal_summary": dict(signal_report["summary"]),
        "summary": _summary(examples, records),
        "counts_by_candidate_reason": _counts(records, "candidate_reason"),
        "counts_by_recommended_review_action": _counts(
            records,
            "recommended_review_action",
        ),
        "records": records,
        "safety": {
            "copies_raw_source_text": False,
            "copies_local_paths": False,
            "copies_private_refs": False,
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


def _audit_record(
    example: Mapping[str, Any],
    *,
    full_prediction: Mapping[str, Any],
    no_aux_prediction: Mapping[str, Any],
) -> dict[str, Any]:
    source = _mapping(example.get("source"))
    source_case = _mapping(example.get("source_case"))
    targets = _mapping(example.get("targets"))
    case_record = _mapping(_mapping(example.get("input")).get("case_record"))
    source_context = _source_context_summary(example)
    target_action = str(targets.get("preferred_action") or "")
    full_action = str(full_prediction.get("recommended_action") or "")
    no_aux_action = str(no_aux_prediction.get("recommended_action") or "")
    action_changed = full_action != no_aux_action
    source_feature_match_count = _source_feature_match_count(full_prediction)
    candidate_reason = _candidate_reason(
        source_context_available=bool(source_context["available"]),
        action_changed=action_changed,
        source_feature_match_count=source_feature_match_count,
    )
    return {
        "case_id": str(source_case.get("case_id") or ""),
        "case_type": str(source_case.get("case_type") or ""),
        "source": {
            "source_id": str(source.get("source_id") or ""),
            "kind": str(source.get("kind") or ""),
            "privacy_scope": str(source.get("privacy_scope") or ""),
            "curation_status": str(source.get("curation_status") or ""),
            "record_index": int(source.get("index") or 0),
            "split": str(example.get("split") or ""),
        },
        "targets": {
            "preferred_action": target_action,
            "failure_type": str(targets.get("failure_type") or ""),
        },
        "source_context": source_context,
        "predictions": {
            "full_action": full_action,
            "without_auxiliary_signals_action": no_aux_action,
            "action_changed_with_source_context": action_changed,
            "full_matches_target": full_action == target_action if target_action else None,
            "without_auxiliary_signals_matches_target": (
                no_aux_action == target_action if target_action else None
            ),
        },
        "model_explanation": {
            "source_context_feature_match_count": source_feature_match_count,
            "matched_source_context_features": _matched_source_context_features(
                full_prediction
            ),
            "fallback_reason": str(
                _mapping(full_prediction.get("explanation")).get("fallback_reason")
                or "scored_features"
            ),
        },
        "source_reference_summary": _source_reference_summary(case_record),
        "candidate_reason": candidate_reason,
        "recommended_review_action": _recommended_review_action(candidate_reason),
    }


def _source_context_summary(example: Mapping[str, Any]) -> dict[str, Any]:
    signals = _auxiliary_source_context_signals(example)
    tags: set[str] = set()
    source_image_available = False
    source_image_ref_kinds: set[str] = set()
    artifact_available_count = 0
    artifact_kind_counts: Counter[str] = Counter()
    text_file_count = 0
    for signal in signals:
        signal_block = _mapping(signal.get("signals"))
        for tag in signal_block.get("source_context_tags") or []:
            if isinstance(tag, str) and tag:
                tags.add(tag)
        source_image = _mapping(signal_block.get("source_image"))
        if bool(source_image.get("available")):
            source_image_available = True
        ref_kind = str(source_image.get("ref_kind") or "")
        if ref_kind:
            source_image_ref_kinds.add(ref_kind)
        source_artifacts = _mapping(signal_block.get("source_artifacts"))
        artifact_available_count += int(source_artifacts.get("available_count") or 0)
        text_file_count += int(source_artifacts.get("text_file_count") or 0)
        for kind, count in _mapping(
            source_artifacts.get("artifact_kind_counts")
        ).items():
            artifact_kind_counts[str(kind)] += int(count or 0)

    return {
        "available": bool(signals),
        "signal_count": len(signals),
        "tags": sorted(tags),
        "source_image_available": source_image_available,
        "source_image_ref_kinds": sorted(source_image_ref_kinds),
        "source_artifact_available_count": artifact_available_count,
        "source_artifact_kind_counts": dict(sorted(artifact_kind_counts.items())),
        "source_artifact_text_file_count": text_file_count,
    }


def _auxiliary_source_context_signals(
    example: Mapping[str, Any],
) -> tuple[Mapping[str, Any], ...]:
    input_block = _mapping(example.get("input"))
    auxiliary_signals = input_block.get("auxiliary_signals")
    if not isinstance(auxiliary_signals, Sequence) or isinstance(
        auxiliary_signals,
        (str, bytes),
    ):
        return ()
    records = []
    for signal in auxiliary_signals:
        if not isinstance(signal, Mapping):
            continue
        model_id = str(_mapping(signal.get("model")).get("id") or "")
        if model_id == "source_context_static_v1":
            records.append(signal)
    return tuple(records)


def _source_feature_match_count(prediction: Mapping[str, Any]) -> int:
    return len(_matched_source_context_features(prediction))


def _matched_source_context_features(prediction: Mapping[str, Any]) -> list[str]:
    explanation = _mapping(prediction.get("explanation"))
    matched = explanation.get("matched_features")
    if not isinstance(matched, Sequence) or isinstance(matched, (str, bytes)):
        return []
    return [
        str(feature)
        for feature in matched
        if str(feature).startswith(
            (
                "aux_signal.source_context_tag:",
                "aux_signal.source_artifact_kind:",
                "aux_signal.source_image",
            )
        )
    ]


def _source_reference_summary(case_record: Mapping[str, Any]) -> dict[str, Any]:
    refs = _source_ref_values(case_record)
    return {
        "has_source_refs": bool(_mapping(case_record.get("source_refs"))),
        "has_source_image_ref": bool(_source_image_ref(case_record)),
        "has_source_path_hint": bool(
            str(_mapping(case_record.get("source_summary")).get("source_path_hint") or "")
        ),
        "private_ref_count": sum(1 for ref in refs if ref.startswith("private://")),
        "remote_ref_count": sum(
            1 for ref in refs if ref.startswith(("http://", "https://"))
        ),
        "repo_or_relative_ref_count": sum(
            1
            for ref in refs
            if ref and not ref.startswith(("private://", "http://", "https://"))
        ),
    }


def _source_ref_values(case_record: Mapping[str, Any]) -> tuple[str, ...]:
    refs: list[str] = []
    source_refs = _mapping(case_record.get("source_refs"))
    refs.extend(str(value) for value in source_refs.values() if str(value or ""))
    source_image = _source_image_ref(case_record)
    if source_image:
        refs.append(source_image)
    source_path_hint = str(
        _mapping(case_record.get("source_summary")).get("source_path_hint") or ""
    )
    if source_path_hint:
        refs.append(source_path_hint)
    return tuple(refs)


def _source_image_ref(case_record: Mapping[str, Any]) -> str:
    for container in (case_record, _mapping(case_record.get("input"))):
        value = str(_mapping(container).get("source_image") or "")
        if value:
            return value
    return ""


def _candidate_reason(
    *,
    source_context_available: bool,
    action_changed: bool,
    source_feature_match_count: int,
) -> str:
    if not source_context_available:
        return "needs_source_context"
    if action_changed:
        return "prediction_changed_with_source_context"
    if source_feature_match_count > 0:
        return "source_context_used_no_action_change"
    return "metadata_sufficient"


def _recommended_review_action(candidate_reason: str) -> str:
    if candidate_reason == "needs_source_context":
        return "recover_source_context"
    if candidate_reason == "prediction_changed_with_source_context":
        return "human_review_source_dependency"
    if candidate_reason == "source_context_used_no_action_change":
        return "verify_source_dependency_label"
    return "defer"


def _summary(
    examples: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    return {
        "dataset_example_count": len(examples),
        "real_user_case_count": len(records),
        "source_context_available_count": sum(
            1 for item in records if bool(_mapping(item["source_context"])["available"])
        ),
        "source_context_unavailable_count": sum(
            1 for item in records if not bool(_mapping(item["source_context"])["available"])
        ),
        "prediction_changed_with_source_context_count": sum(
            1
            for item in records
            if bool(_mapping(item["predictions"])["action_changed_with_source_context"])
        ),
        "source_context_feature_matched_count": sum(
            1
            for item in records
            if int(_mapping(item["model_explanation"])["source_context_feature_match_count"])
            > 0
        ),
        "review_candidate_count": _candidate_count(records),
    }


def _candidate_count(records: Sequence[Mapping[str, Any]]) -> int:
    return sum(
        1
        for item in records
        if str(item.get("recommended_review_action") or "") != "defer"
    )


def _counts(records: Sequence[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: Counter[str] = Counter(str(item.get(key) or "") for item in records)
    return dict(sorted(counts.items()))


def _record_sort_key(record: Mapping[str, Any]) -> tuple[int, str, str]:
    priority = {
        "prediction_changed_with_source_context": 0,
        "needs_source_context": 1,
        "source_context_used_no_action_change": 2,
        "metadata_sufficient": 3,
    }.get(str(record.get("candidate_reason") or ""), 9)
    source = _mapping(record.get("source"))
    return (
        priority,
        str(source.get("source_id") or ""),
        str(record.get("case_id") or ""),
    )


def _without_auxiliary_signals(
    examples: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    stripped = [copy.deepcopy(dict(example)) for example in examples]
    for example in stripped:
        input_block = example.get("input")
        if isinstance(input_block, dict):
            input_block.pop("auxiliary_signals", None)
    return stripped


def _resolve_repo_path(repo_root: str | Path, path: str | Path) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = Path(repo_root) / resolved
    return resolved


def _safe_path(path: str | Path) -> str:
    value = Path(path)
    parts = value.parts
    if "docs" in parts:
        return str(Path(*parts[parts.index("docs") :]))
    return value.name


def _safe_artifact_path(repo_root: str | Path, path: str | Path) -> str:
    artifact_path = Path(path)
    try:
        return str(artifact_path.relative_to(Path(repo_root)))
    except ValueError:
        return artifact_path.name


def _validate_split(value: str, *, label: str) -> None:
    if value not in DATASET_SPLITS:
        raise ValueError(f"unsupported {label} {value!r}; expected one of {DATASET_SPLITS}")


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
