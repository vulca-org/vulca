"""Provider-free execution gate for visual ownership plans."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = 1
GATE_CASE_TYPE = "learning_visual_ownership_execution_gate"
REPORT_CASE_TYPE = "learning_visual_ownership_execution_gate_report"
DEFAULT_GATE_NAME = "visual_ownership_execution_gate.jsonl"
DEFAULT_REPORT_NAME = "visual_ownership_execution_gate_report.json"

STATUS_READY = "ready_for_agent_execution"
STATUS_MISSING_SOURCE = "blocked_missing_source_context"
STATUS_INCOMPLETE = "blocked_incomplete_plan"


def run_visual_ownership_execution_gate(
    *,
    plan_path: str | Path,
    gate_path: str | Path | None = None,
    report_path: str | Path | None = None,
) -> dict[str, Any]:
    """Validate visual ownership plans before agent/runtime execution."""
    plans = _load_jsonl(plan_path)
    gate_records = [_gate_record(plan) for plan in plans]
    resolved_gate_path = (
        Path(gate_path) if gate_path else Path(plan_path).parent / DEFAULT_GATE_NAME
    )
    _write_jsonl(resolved_gate_path, gate_records)

    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": (
            "ready_for_visual_ownership_agent_execution"
            if gate_records
            and all(record["gate_status"] == STATUS_READY for record in gate_records)
            else "blocked_visual_ownership_execution"
            if gate_records
            else "no_visual_ownership_plans"
        ),
        "inputs": {
            "plan_path": Path(plan_path).name,
        },
        "artifacts": {
            "gate_path": str(resolved_gate_path),
            "report_path": str(report_path or ""),
        },
        "summary": _summary(gate_records),
        "counts_by_gate_status": _counter_by(gate_records, "gate_status"),
        "counts_by_recommended_workflow": _counter_by(
            gate_records,
            "recommended_workflow",
        ),
        "gate_records": gate_records,
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


def _summary(gate_records: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "plan_count": len(gate_records),
        "agent_execution_ready_count": sum(
            1
            for record in gate_records
            if bool(_mapping(record.get("readiness")).get("agent_execution_ready"))
        ),
        "blocked_count": sum(
            1 for record in gate_records if record.get("gate_status") != STATUS_READY
        ),
        "production_runtime_ready_count": sum(
            1
            for record in gate_records
            if bool(_mapping(record.get("readiness")).get("production_runtime_ready"))
        ),
        "source_context_gap_count": sum(
            1 for record in gate_records if "source_context_unavailable" in record.get("gate_reasons", [])
        ),
        "incomplete_plan_count": sum(
            1
            for record in gate_records
            if record.get("gate_status") == STATUS_INCOMPLETE
        ),
    }


def _gate_record(plan: Mapping[str, Any]) -> dict[str, Any]:
    required_inputs = _string_list(plan.get("required_inputs"))
    planner_steps = _string_list(plan.get("planner_steps"))
    routing = _mapping(plan.get("routing"))
    source_context_available = bool(plan.get("source_context_available"))
    production_runtime_ready = bool(routing.get("production_runtime_ready"))
    gate_status, gate_reasons, next_owner = _gate_decision(
        source_context_available=source_context_available,
        required_inputs=required_inputs,
        planner_steps=planner_steps,
        routing=routing,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": GATE_CASE_TYPE,
        "example_id": str(plan.get("example_id") or ""),
        "case_id": str(plan.get("case_id") or ""),
        "source_case_type": str(plan.get("source_case_type") or ""),
        "visual_ownership_kind": str(plan.get("visual_ownership_kind") or ""),
        "recommended_workflow": str(plan.get("recommended_workflow") or ""),
        "gate_status": gate_status,
        "gate_reasons": gate_reasons,
        "readiness": {
            "agent_execution_ready": gate_status == STATUS_READY,
            "production_runtime_ready": production_runtime_ready,
            "required_input_count": len(required_inputs),
            "planner_step_count": len(planner_steps),
            "source_context_available": source_context_available,
        },
        "routing": {
            "next_owner": next_owner,
            "requires_runtime_adapter": not production_runtime_ready,
        },
    }


def _gate_decision(
    *,
    source_context_available: bool,
    required_inputs: Sequence[str],
    planner_steps: Sequence[str],
    routing: Mapping[str, Any],
) -> tuple[str, list[str], str]:
    if not source_context_available:
        return STATUS_MISSING_SOURCE, ["source_context_unavailable"], "source_context_recovery"

    reasons: list[str] = []
    if not required_inputs:
        reasons.append("required_inputs_missing")
    if not planner_steps:
        reasons.append("planner_steps_missing")
    if str(routing.get("next_owner") or "") != "visual_ownership_agent":
        reasons.append("visual_ownership_agent_route_missing")
    if reasons:
        return STATUS_INCOMPLETE, reasons, "visual_ownership_planner"

    return STATUS_READY, [], "visual_ownership_agent"


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
