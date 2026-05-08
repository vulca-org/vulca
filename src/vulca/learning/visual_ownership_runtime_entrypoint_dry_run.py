"""Provider-free runtime entrypoint dry-run contracts for visual ownership."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = 1
REPLAY_CASE_TYPE = "learning_visual_ownership_runtime_replay"
ENTRYPOINT_CASE_TYPE = "learning_visual_ownership_runtime_entrypoint_dry_run"
REPORT_CASE_TYPE = "learning_visual_ownership_runtime_entrypoint_dry_run_report"
DEFAULT_INVOCATION_NAME = "visual_ownership_runtime_entrypoint_dry_run.jsonl"
DEFAULT_REPORT_NAME = "visual_ownership_runtime_entrypoint_dry_run_report.json"

DRY_RUN_NAME = "visual_ownership_runtime_entrypoint_dry_run_v1"
READY_REPLAY_STATUS = "dry_run_replayable"


def run_visual_ownership_runtime_entrypoint_dry_run(
    *,
    replay_path: str | Path,
    invocation_path: str | Path | None = None,
    report_path: str | Path | None = None,
) -> dict[str, Any]:
    """Convert runtime replay records into provider-free entrypoint contracts."""
    replay_records = _load_jsonl(replay_path)
    invocations = sorted(
        (_invocation_for_replay(record) for record in replay_records),
        key=lambda item: (item["runtime_tool"], item["case_id"]),
    )

    resolved_invocation_path = (
        Path(invocation_path)
        if invocation_path
        else Path(replay_path).parent / DEFAULT_INVOCATION_NAME
    )
    _write_jsonl(resolved_invocation_path, invocations)

    blocked_records = [
        record
        for record in invocations
        if str(record.get("dry_run_status") or "") != "dry_run_invocation_ready"
    ]
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": _report_status(replay_records, blocked_records),
        "inputs": {
            "replay_path": Path(replay_path).name,
        },
        "artifacts": {
            "invocation_path": str(resolved_invocation_path),
            "report_path": str(report_path or ""),
        },
        "summary": _summary(replay_records, invocations, blocked_records),
        "counts_by_runtime_tool": _counter_by(invocations, "runtime_tool"),
        "counts_by_dry_run_status": _counter_by(invocations, "dry_run_status"),
        "blocked_invocations": [
            _blocked_invocation_summary(record) for record in blocked_records
        ],
        "runtime_entrypoint_dry_runs": invocations,
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
    replay_records: Sequence[Mapping[str, Any]],
    blocked_records: Sequence[Mapping[str, Any]],
) -> str:
    if not replay_records:
        return "no_runtime_replays"
    if blocked_records:
        return "blocked_runtime_entrypoint_dry_run"
    return "runtime_entrypoint_dry_run_ready"


def _summary(
    replay_records: Sequence[Mapping[str, Any]],
    invocations: Sequence[Mapping[str, Any]],
    blocked_records: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    return {
        "replay_record_count": len(replay_records),
        "dry_run_invocation_count": len(invocations),
        "ready_count": len(invocations) - len(blocked_records),
        "blocked_count": len(blocked_records),
        "provider_call_count": 0,
    }


def _invocation_for_replay(replay: Mapping[str, Any]) -> dict[str, Any]:
    runtime_entrypoint = str(replay.get("runtime_entrypoint") or "")
    runtime_contract = _mapping(replay.get("runtime_contract"))
    runtime_tool, contract, mapping_reasons = _entrypoint_contract(runtime_entrypoint)

    dry_run_reasons: list[str] = []
    dry_run_reasons.extend(mapping_reasons)
    if str(replay.get("replay_status") or "") != READY_REPLAY_STATUS:
        dry_run_reasons.append("previous_replay_not_replayable")
    if bool(runtime_contract.get("provider_calls_enabled")):
        dry_run_reasons.append("provider_calls_enabled")

    dry_run_status = _dry_run_status(dry_run_reasons)
    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": ENTRYPOINT_CASE_TYPE,
        "dry_run_name": DRY_RUN_NAME,
        "replay_name": str(replay.get("replay_name") or ""),
        "adapter_name": str(replay.get("adapter_name") or ""),
        "example_id": str(replay.get("example_id") or ""),
        "case_id": str(replay.get("case_id") or ""),
        "source_case_type": str(replay.get("source_case_type") or ""),
        "visual_ownership_kind": str(replay.get("visual_ownership_kind") or ""),
        "recommended_workflow": str(replay.get("recommended_workflow") or ""),
        "runtime_target": str(replay.get("runtime_target") or ""),
        "runtime_action": str(replay.get("runtime_action") or ""),
        "runtime_entrypoint": runtime_entrypoint,
        "runtime_tool": runtime_tool,
        "runtime_interface": contract.get("runtime_interface", "unknown"),
        "dry_run_status": dry_run_status,
        "dry_run_reasons": dry_run_reasons,
        "entrypoint_contract": contract,
        "readiness": {
            "dry_run_invocation_ready": (
                dry_run_status == "dry_run_invocation_ready"
            ),
            "provider_call_count": 0,
        },
    }


def _entrypoint_contract(runtime_entrypoint: str) -> tuple[str, dict[str, Any], list[str]]:
    if runtime_entrypoint == "layers_split_dry_run":
        return (
            "layers_split",
            {
                "runtime_interface": "mcp",
                "runtime_tool": "layers_split",
                "argument_contract": {
                    "image_path": "{source_image}",
                    "output_dir": "{runtime_output_dir}",
                    "mode": "orchestrated",
                    "provider": "dry_run",
                    "tradition": "{tradition}",
                    "plan": "{visual_ownership_replan_json}",
                    "case_log_path": "{optional_case_log_path}",
                },
                "expected_outputs": [
                    "layers",
                    "manifest_path",
                    "split_mode",
                ],
            },
            [],
        )
    if runtime_entrypoint == "layers_redraw_dry_run":
        return (
            "layers_redraw",
            {
                "runtime_interface": "mcp",
                "runtime_tool": "layers_redraw",
                "argument_contract": {
                    "artwork_dir": "{current_layer_manifest_dir}",
                    "layer": "{target_layer_name}",
                    "instruction": "{visual_ownership_redraw_instruction}",
                    "provider": "dry_run",
                    "tradition": "{tradition}",
                    "route": "auto",
                    "case_log_path": "{optional_case_log_path}",
                },
                "expected_outputs": [
                    "name",
                    "file",
                    "source_pasteback_path",
                ],
            },
            [],
        )
    return (
        "unknown",
        {
            "runtime_interface": "unknown",
            "runtime_tool": "unknown",
            "argument_contract": {},
            "expected_outputs": [],
        },
        ["unsupported_runtime_entrypoint"],
    )


def _dry_run_status(dry_run_reasons: Sequence[str]) -> str:
    if not dry_run_reasons:
        return "dry_run_invocation_ready"
    if "unsupported_runtime_entrypoint" in dry_run_reasons:
        return "blocked_unknown_runtime_entrypoint"
    if "previous_replay_not_replayable" in dry_run_reasons:
        return "blocked_previous_replay_status"
    if "provider_calls_enabled" in dry_run_reasons:
        return "blocked_provider_call_policy"
    return "blocked_runtime_entrypoint_dry_run"


def _blocked_invocation_summary(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "example_id": str(record.get("example_id") or ""),
        "case_id": str(record.get("case_id") or ""),
        "runtime_entrypoint": str(record.get("runtime_entrypoint") or ""),
        "runtime_tool": str(record.get("runtime_tool") or ""),
        "dry_run_status": str(record.get("dry_run_status") or ""),
        "dry_run_reasons": _string_list(record.get("dry_run_reasons")),
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
