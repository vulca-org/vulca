"""Provider-free dry-run replay for visual ownership runtime requests."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = 1
REQUEST_CASE_TYPE = "learning_visual_ownership_runtime_request"
REPLAY_CASE_TYPE = "learning_visual_ownership_runtime_replay"
REPORT_CASE_TYPE = "learning_visual_ownership_runtime_replay_report"
DEFAULT_REPLAY_NAME = "visual_ownership_runtime_replay.jsonl"
DEFAULT_REPORT_NAME = "visual_ownership_runtime_replay_report.json"

REPLAY_NAME = "visual_ownership_runtime_replay_v1"


def run_visual_ownership_runtime_replay(
    *,
    request_path: str | Path,
    replay_path: str | Path | None = None,
    report_path: str | Path | None = None,
) -> dict[str, Any]:
    """Dry-run runtime requests into replay records without provider calls."""
    requests = _load_jsonl(request_path)
    replay_records = sorted(
        (_replay_for_request(request) for request in requests),
        key=lambda item: (item["runtime_target"], item["case_id"]),
    )

    resolved_replay_path = (
        Path(replay_path)
        if replay_path
        else Path(request_path).parent / DEFAULT_REPLAY_NAME
    )
    _write_jsonl(resolved_replay_path, replay_records)

    blocked_records = [
        record
        for record in replay_records
        if str(record.get("replay_status") or "") != "dry_run_replayable"
    ]
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": _report_status(requests, blocked_records),
        "inputs": {
            "request_path": Path(request_path).name,
        },
        "artifacts": {
            "replay_path": str(resolved_replay_path),
            "report_path": str(report_path or ""),
        },
        "summary": _summary(requests, replay_records, blocked_records),
        "counts_by_runtime_target": _counter_by(replay_records, "runtime_target"),
        "counts_by_runtime_entrypoint": _counter_by(
            replay_records,
            "runtime_entrypoint",
        ),
        "counts_by_replay_status": _counter_by(replay_records, "replay_status"),
        "blocked_requests": [
            _blocked_request_summary(record) for record in blocked_records
        ],
        "runtime_replays": replay_records,
        "safe_handling": {
            "copies_local_paths": False,
            "copies_private_refs": False,
            "copies_raw_source_text": False,
            "calls_model_provider": False,
        },
    }
    if report_path:
        output = Path(report_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        report["artifacts"]["report_path"] = str(output)
        output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return report


def _report_status(
    requests: Sequence[Mapping[str, Any]],
    blocked_records: Sequence[Mapping[str, Any]],
) -> str:
    if not requests:
        return "no_runtime_requests"
    if blocked_records:
        return "blocked_runtime_replay"
    return "runtime_replay_ready"


def _summary(
    requests: Sequence[Mapping[str, Any]],
    replay_records: Sequence[Mapping[str, Any]],
    blocked_records: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    return {
        "request_count": len(requests),
        "replay_record_count": len(replay_records),
        "replayable_count": len(replay_records) - len(blocked_records),
        "blocked_count": len(blocked_records),
        "provider_call_count": 0,
    }


def _replay_for_request(request: Mapping[str, Any]) -> dict[str, Any]:
    runtime_target = str(request.get("runtime_target") or "")
    runtime_action = str(request.get("runtime_action") or "")
    runtime_entrypoint, mapping_reasons = _runtime_entrypoint(
        runtime_target,
        runtime_action,
    )
    runtime_inputs = _string_list(request.get("required_runtime_inputs"))
    execution_policy = _mapping(request.get("execution_policy"))

    replay_reasons: list[str] = []
    replay_reasons.extend(mapping_reasons)
    if bool(execution_policy.get("provider_calls_enabled")):
        replay_reasons.append("provider_calls_enabled")
    if not runtime_inputs:
        replay_reasons.append("required_runtime_inputs_missing")

    replay_status = _replay_status(replay_reasons)
    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPLAY_CASE_TYPE,
        "replay_name": REPLAY_NAME,
        "adapter_name": str(request.get("adapter_name") or ""),
        "example_id": str(request.get("example_id") or ""),
        "case_id": str(request.get("case_id") or ""),
        "source_case_type": str(request.get("source_case_type") or ""),
        "visual_ownership_kind": str(request.get("visual_ownership_kind") or ""),
        "recommended_workflow": str(request.get("recommended_workflow") or ""),
        "runtime_target": runtime_target,
        "runtime_action": runtime_action,
        "runtime_entrypoint": runtime_entrypoint or "unknown",
        "replay_status": replay_status,
        "replay_reasons": replay_reasons,
        "runtime_contract": {
            "runtime_target": runtime_target,
            "runtime_action": runtime_action,
            "required_runtime_inputs": runtime_inputs,
            "provider_calls_enabled": False,
        },
        "readiness": {
            "dry_run_replayable": replay_status == "dry_run_replayable",
            "required_runtime_input_count": len(runtime_inputs),
            "provider_call_count": 0,
        },
    }


def _runtime_entrypoint(runtime_target: str, runtime_action: str) -> tuple[str, list[str]]:
    if runtime_target == "layers_decompose":
        if runtime_action in {
            "replan_decompose_layers",
            "replan_decompose_boundaries",
        }:
            return "layers_split_dry_run", []
        return "unknown", ["unsupported_runtime_action"]
    if runtime_target == "layers_redraw":
        if runtime_action == "replan_redraw_boundary":
            return "layers_redraw_dry_run", []
        return "unknown", ["unsupported_runtime_action"]
    return "unknown", ["unsupported_runtime_target"]


def _replay_status(replay_reasons: Sequence[str]) -> str:
    if not replay_reasons:
        return "dry_run_replayable"
    if "unsupported_runtime_target" in replay_reasons:
        return "blocked_unknown_runtime_target"
    if "unsupported_runtime_action" in replay_reasons:
        return "blocked_unknown_runtime_action"
    if "provider_calls_enabled" in replay_reasons:
        return "blocked_provider_call_policy"
    if "required_runtime_inputs_missing" in replay_reasons:
        return "blocked_missing_runtime_inputs"
    return "blocked_runtime_replay"


def _blocked_request_summary(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "example_id": str(record.get("example_id") or ""),
        "case_id": str(record.get("case_id") or ""),
        "runtime_target": str(record.get("runtime_target") or ""),
        "runtime_action": str(record.get("runtime_action") or ""),
        "replay_status": str(record.get("replay_status") or ""),
        "replay_reasons": _string_list(record.get("replay_reasons")),
    }


def _counter_by(items: Sequence[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        counts[str(item.get(key) or "unknown")] += 1
    return dict(sorted(counts.items()))


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, Mapping):
            records.append(dict(value))
    return records


def _write_jsonl(path: str | Path, records: Sequence[Mapping[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
            fh.write("\n")


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value]


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
