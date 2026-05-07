"""Provider-free planning for visual ownership boundary decisions."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = 1
PLAN_CASE_TYPE = "learning_visual_ownership_plan"
REPORT_CASE_TYPE = "learning_visual_ownership_planner_report"
DEFAULT_PLAN_NAME = "visual_ownership_plans.jsonl"
DEFAULT_REPORT_NAME = "visual_ownership_planner_report.json"

PLANNER_NAME = "visual_ownership_planner_v1"
NEXT_OWNER = "visual_ownership_agent"


def run_visual_ownership_planner(
    *,
    decision_path: str | Path,
    plan_path: str | Path | None = None,
    report_path: str | Path | None = None,
) -> dict[str, Any]:
    """Create structured visual ownership plans from dry-run decisions."""
    decisions = _load_jsonl(decision_path)
    visual_decisions = [
        decision
        for decision in decisions
        if bool(_mapping(decision.get("dispatch")).get("visual_ownership_planner"))
    ]
    plans = sorted(
        (_plan_for_decision(decision) for decision in visual_decisions),
        key=lambda item: (item["source_case_type"], item["case_id"]),
    )

    resolved_plan_path = (
        Path(plan_path) if plan_path else Path(decision_path).parent / DEFAULT_PLAN_NAME
    )
    _write_jsonl(resolved_plan_path, plans)

    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": (
            "planned_visual_ownership_work"
            if plans
            else "no_visual_ownership_decisions"
        ),
        "inputs": {
            "decision_path": Path(decision_path).name,
        },
        "artifacts": {
            "plan_path": str(resolved_plan_path),
            "report_path": str(report_path or ""),
        },
        "summary": _summary(decisions, plans),
        "counts_by_case_type": _counter_by(plans, "source_case_type"),
        "counts_by_visual_ownership_kind": _counter_by(
            plans,
            "visual_ownership_kind",
        ),
        "counts_by_recommended_workflow": _counter_by(
            plans,
            "recommended_workflow",
        ),
        "plans": plans,
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
    decisions: Sequence[Mapping[str, Any]],
    plans: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    source_context_gap_count = sum(
        1 for plan in plans if not bool(plan.get("source_context_available"))
    )
    return {
        "decision_count": len(decisions),
        "visual_ownership_decision_count": len(plans),
        "plan_count": len(plans),
        "source_context_gap_count": source_context_gap_count,
    }


def _plan_for_decision(decision: Mapping[str, Any]) -> dict[str, Any]:
    action_router = _mapping(decision.get("action_router"))
    dispatch = _mapping(decision.get("dispatch"))
    source_dependency = _mapping(decision.get("source_dependency_router"))
    source_context = _mapping(decision.get("source_context"))
    case_type = str(decision.get("source_case_type") or "")
    failure_hint = str(action_router.get("failure_hint") or "")
    ownership_kind = str(dispatch.get("visual_ownership_kind") or failure_hint)
    workflow, required_inputs, planner_steps = _workflow_contract(
        case_type=case_type,
        visual_ownership_kind=ownership_kind,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": PLAN_CASE_TYPE,
        "planner_name": PLANNER_NAME,
        "example_id": str(decision.get("example_id") or ""),
        "case_id": str(decision.get("case_id") or ""),
        "source_case_type": case_type,
        "recommended_action": str(action_router.get("recommended_action") or ""),
        "failure_hint": failure_hint,
        "visual_ownership_kind": ownership_kind,
        "recommended_workflow": workflow,
        "required_inputs": required_inputs,
        "planner_steps": planner_steps,
        "source_context_available": bool(source_context.get("available")),
        "source_context_signal_count": int(source_context.get("signal_count") or 0),
        "source_dependency": str(
            source_dependency.get("recommended_source_dependency") or ""
        ),
        "decision_basis": str(
            source_dependency.get("recommended_decision_basis") or ""
        ),
        "routing": {
            "next_owner": NEXT_OWNER,
            "production_runtime_ready": False,
            "requires_visual_agent_judgement": True,
        },
    }


def _workflow_contract(
    *,
    case_type: str,
    visual_ownership_kind: str,
) -> tuple[str, list[str], list[str]]:
    if visual_ownership_kind == "occlusion":
        return (
            "decompose_occlusion_replan",
            [
                "source_image",
                "current_layer_manifest",
                "layer_order_or_occlusion_notes",
            ],
            [
                "inspect_source_occlusion_relationships",
                "separate_occluder_and_occluded_regions",
                "verify_layer_order_and_mask_edges",
            ],
        )
    if visual_ownership_kind == "under_split":
        workflow = (
            "redraw_under_split_boundary_replan"
            if case_type == "redraw_case"
            else "decompose_under_split_boundary_replan"
        )
        return (
            workflow,
            [
                "source_image",
                "current_mask_or_layer_bounds",
                "target_region_description",
            ],
            [
                "inspect_under_split_boundaries",
                "propose_additional_layer_or_mask_splits",
                "verify_target_region_isolation",
            ],
        )
    return (
        "visual_ownership_manual_replan",
        [
            "source_image",
            "current_visual_artifact",
            "target_region_description",
        ],
        [
            "inspect_visual_ownership_boundary",
            "choose_redraw_decompose_or_manual_review_route",
            "verify_target_region_ownership",
        ],
    )


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


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
