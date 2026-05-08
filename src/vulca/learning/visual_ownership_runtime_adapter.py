"""Provider-free runtime requests for visual ownership execution gates."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = 1
REQUEST_CASE_TYPE = "learning_visual_ownership_runtime_request"
REPORT_CASE_TYPE = "learning_visual_ownership_runtime_adapter_report"
DEFAULT_REQUEST_NAME = "visual_ownership_runtime_requests.jsonl"
DEFAULT_REPORT_NAME = "visual_ownership_runtime_adapter_report.json"

ADAPTER_NAME = "visual_ownership_runtime_adapter_v1"
READY_GATE_STATUS = "ready_for_agent_execution"


def run_visual_ownership_runtime_adapter(
    *,
    gate_path: str | Path,
    request_path: str | Path | None = None,
    report_path: str | Path | None = None,
) -> dict[str, Any]:
    """Convert ready visual ownership gates into runtime request records."""
    gate_records = _load_jsonl(gate_path)
    ready_gates = [
        gate
        for gate in gate_records
        if str(gate.get("gate_status") or "") == READY_GATE_STATUS
    ]
    requests = sorted(
        (_request_for_gate(gate) for gate in ready_gates),
        key=lambda item: (item["runtime_target"], item["case_id"]),
    )

    resolved_request_path = (
        Path(request_path)
        if request_path
        else Path(gate_path).parent / DEFAULT_REQUEST_NAME
    )
    _write_jsonl(resolved_request_path, requests)

    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": (
            "runtime_requests_ready_for_adapter_review"
            if requests
            else "no_runtime_requests"
        ),
        "inputs": {
            "gate_path": Path(gate_path).name,
        },
        "artifacts": {
            "request_path": str(resolved_request_path),
            "report_path": str(report_path or ""),
        },
        "summary": _summary(gate_records, requests),
        "counts_by_runtime_target": _counter_by(requests, "runtime_target"),
        "counts_by_runtime_action": _counter_by(requests, "runtime_action"),
        "counts_by_recommended_workflow": _counter_by(
            requests,
            "recommended_workflow",
        ),
        "blocked_gate_records": [
            _blocked_gate_summary(gate)
            for gate in gate_records
            if str(gate.get("gate_status") or "") != READY_GATE_STATUS
        ],
        "runtime_requests": requests,
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


def _summary(
    gate_records: Sequence[Mapping[str, Any]],
    requests: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    return {
        "gate_record_count": len(gate_records),
        "adapter_request_count": len(requests),
        "blocked_gate_count": len(gate_records) - len(requests),
        "production_runtime_candidate_count": len(requests),
        "provider_call_count": 0,
    }


def _request_for_gate(gate: Mapping[str, Any]) -> dict[str, Any]:
    workflow = str(gate.get("recommended_workflow") or "")
    target, action, required_inputs = _runtime_contract(workflow)
    readiness = _mapping(gate.get("readiness"))
    routing = _mapping(gate.get("routing"))
    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": REQUEST_CASE_TYPE,
        "adapter_name": ADAPTER_NAME,
        "example_id": str(gate.get("example_id") or ""),
        "case_id": str(gate.get("case_id") or ""),
        "source_case_type": str(gate.get("source_case_type") or ""),
        "visual_ownership_kind": str(gate.get("visual_ownership_kind") or ""),
        "recommended_workflow": workflow,
        "runtime_target": target,
        "runtime_action": action,
        "required_runtime_inputs": required_inputs,
        "gate_status": str(gate.get("gate_status") or ""),
        "source_context_available": bool(readiness.get("source_context_available")),
        "handoff": {
            "from_owner": "visual_ownership_agent",
            "to_runtime_target": target,
            "requires_runtime_adapter": bool(routing.get("requires_runtime_adapter")),
        },
        "execution_policy": {
            "provider_calls_enabled": False,
            "requires_visual_agent_judgement": True,
            "requires_runtime_adapter_review": True,
        },
    }


def _runtime_contract(workflow: str) -> tuple[str, str, list[str]]:
    if workflow == "decompose_occlusion_replan":
        return (
            "layers_decompose",
            "replan_decompose_layers",
            [
                "source_image",
                "current_layer_manifest",
                "layer_order_or_occlusion_notes",
            ],
        )
    if workflow == "redraw_under_split_boundary_replan":
        return (
            "layers_redraw",
            "replan_redraw_boundary",
            [
                "source_image",
                "current_mask_or_layer_bounds",
                "target_region_description",
            ],
        )
    if workflow == "decompose_under_split_boundary_replan":
        return (
            "layers_decompose",
            "replan_decompose_boundaries",
            [
                "source_image",
                "current_mask_or_layer_bounds",
                "target_region_description",
            ],
        )
    return (
        "visual_ownership_manual_review",
        "manual_visual_ownership_review",
        [
            "source_image",
            "current_visual_artifact",
            "target_region_description",
        ],
    )


def _blocked_gate_summary(gate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "example_id": str(gate.get("example_id") or ""),
        "case_id": str(gate.get("case_id") or ""),
        "source_case_type": str(gate.get("source_case_type") or ""),
        "recommended_workflow": str(gate.get("recommended_workflow") or ""),
        "gate_status": str(gate.get("gate_status") or ""),
        "gate_reasons": _string_list(gate.get("gate_reasons")),
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
