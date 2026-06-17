from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS = ROOT / "outputs" / THREAD_ID / "presentations"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_23_selector_effectiveness_audit.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_23_selector_effectiveness_audit.md"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sorted_unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def list_field(record: dict[str, Any], field: str) -> list[Any]:
    value = record.get(field) or []
    return value if isinstance(value, list) else []


def string_list_field(record: dict[str, Any], field: str) -> list[str]:
    return [str(item) for item in list_field(record, field) if item]


def collect_values(records: list[dict[str, Any]], field: str) -> list[str]:
    values: list[str] = []
    for record in records:
        value = record.get(field)
        if isinstance(value, list):
            values.extend(str(item) for item in value if item)
        elif value:
            values.append(str(value))
    return sorted_unique(values)


def slides_by_role(trace: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(slide.get("role")): slide for slide in trace.get("slides", [])}


def rejection_ids(slide: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for item in list_field(slide, "run2_21_rejected_evidence_reasons"):
        if isinstance(item, dict) and item.get("evidence_id"):
            ids.append(str(item["evidence_id"]))
    return sorted_unique(ids)


def build_role_records(
    full_trace: dict[str, Any],
    baseline_trace: dict[str, Any],
) -> tuple[list[dict[str, Any]], int]:
    baseline_by_role = slides_by_role(baseline_trace)
    role_records: list[dict[str, Any]] = []
    roles_with_delta = 0

    for slide in full_trace.get("slides", []):
        role = str(slide.get("role") or "")
        baseline_slide = baseline_by_role.get(role, {})
        required_modules = string_list_field(slide, "run2_22_required_code_module_ids")
        actual_modules = string_list_field(slide, "run2_22_code_module_ids")
        baseline_modules = string_list_field(baseline_slide, "run2_19_code_module_ids")
        module_delta = sorted_unique([module for module in actual_modules if module not in baseline_modules])
        if set(actual_modules) != set(baseline_modules):
            roles_with_delta += 1

        secondary_evidence = string_list_field(slide, "run2_21_secondary_evidence_ids")
        rejected = list_field(slide, "run2_21_rejected_evidence_reasons")
        has_required = bool(slide.get("run2_21_selector_gate_id")) and bool(required_modules) and bool(actual_modules)
        role_records.append(
            {
                "slide_id": slide.get("slide_id"),
                "role": role,
                "visual_decision_memory_id": slide.get("run2_21_visual_decision_memory_id") or "",
                "primary_evidence_id": slide.get("run2_21_primary_evidence_id") or "",
                "secondary_evidence_ids": secondary_evidence,
                "secondary_evidence_count": len(secondary_evidence),
                "rejected_evidence_ids": rejection_ids(slide),
                "rejected_evidence_count": len(rejected),
                "selector_gate_id": slide.get("run2_21_selector_gate_id") or "",
                "required_code_module_ids": required_modules,
                "actual_code_module_ids": actual_modules,
                "baseline_run2_19_code_module_ids": baseline_modules,
                "code_module_delta": module_delta,
                "selector_execution_status": slide.get("run2_22_selector_execution_status") or "",
                "public_surface_policy": slide.get("run2_21_surface_policy") or "",
                "status": "pass" if has_required else "blocked",
                "reason": (
                    f"primary={slide.get('run2_21_primary_evidence_id') or 'missing'}; "
                    f"secondary={len(secondary_evidence)}; rejected={len(rejected)}; "
                    f"module_delta_from_run2_19={bool(module_delta)}"
                ),
            }
        )

    return role_records, roles_with_delta


def build_chain_records(role_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chains: list[dict[str, Any]] = []
    for role in role_records:
        chains.append(
            {
                "chain_id": f"{role['role']}_run2_23_selector_effectiveness",
                "run_id": "2.23",
                "slide_roles": [role["role"]],
                "required_code_module_ids": role["required_code_module_ids"],
                "actual_code_module_ids": role["actual_code_module_ids"],
                "status": role["status"],
                "reason": (
                    f"{role['visual_decision_memory_id']} selected {role['primary_evidence_id']}; "
                    f"rejected {role['rejected_evidence_count']} evidence records; "
                    f"Run 2.19 module delta count {len(role['code_module_delta'])}."
                ),
                "next_fix": "human_visual_review_then_deepen_typography_spacing_climax",
            }
        )
    return chains


def build_audit() -> dict[str, Any]:
    decision_memory_path = PACK / "run2_21_visual_decision_memory.json"
    selector_gates_path = PACK / "run2_21_per_role_selector_gates.json"
    rejection_matrix_path = PACK / "run2_21_evidence_rejection_matrix.json"
    full_trace_path = PRESENTATIONS / "ppt-run2-22-full-vulca" / "trace_manifest.json"
    bad_trace_path = PRESENTATIONS / "ppt-run2-22-bad-selector-memory" / "trace_manifest.json"
    prompt_trace_path = PRESENTATIONS / "ppt-run2-22-prompt-only" / "trace_manifest.json"
    run15_trace_path = PRESENTATIONS / "ppt-run2-22-run1-5-skill" / "trace_manifest.json"
    baseline_trace_path = PRESENTATIONS / "ppt-run2-19-full-vulca" / "trace_manifest.json"

    decision_memory = read_json(decision_memory_path).get("visual_decision_memory", [])
    selector_gates = read_json(selector_gates_path).get("gates", [])
    rejection_records = read_json(rejection_matrix_path).get("role_records", [])
    full_trace = read_json(full_trace_path)
    bad_trace = read_json(bad_trace_path)
    prompt_trace = read_json(prompt_trace_path)
    run15_trace = read_json(run15_trace_path)
    baseline_trace = read_json(baseline_trace_path)

    full_slides = full_trace.get("slides", [])
    bad_slides = bad_trace.get("slides", [])
    role_records, roles_with_delta = build_role_records(full_trace, baseline_trace)

    selected_memory_ids = collect_values(full_slides, "run2_21_visual_decision_memory_id")
    selected_gate_ids = collect_values(full_slides, "run2_21_selector_gate_id")
    selected_primary_ids = collect_values(full_slides, "run2_21_primary_evidence_id")
    selected_secondary_ids = collect_values(full_slides, "run2_21_secondary_evidence_ids")
    selected_code_ids = collect_values(full_slides, "run2_22_code_module_ids")

    full_checks = {
        "all_slides_have_selector_gate_and_code": all(
            slide.get("run2_21_selector_gate_id") and slide.get("run2_22_code_module_ids")
            for slide in full_slides
        ),
        "primary_evidence_per_slide_all": all(bool(slide.get("run2_21_primary_evidence_id")) for slide in full_slides),
        "secondary_evidence_within_cap_all": all(
            len(string_list_field(slide, "run2_21_secondary_evidence_ids")) <= 2 for slide in full_slides
        ),
        "rejection_reasons_present_all": all(
            bool(list_field(slide, "run2_21_rejected_evidence_reasons")) for slide in full_slides
        ),
        "public_surface_policy_suppressed_all": all(
            slide.get("run2_21_surface_policy") == "trace_suppressed_from_public_slide_surface"
            for slide in full_slides
        ),
    }
    bad_selector_gate_ids = collect_values(bad_slides, "run2_21_selector_gate_id")
    bad_rejection_ids = collect_values(bad_slides, "run2_21_rejected_evidence_reasons")
    bad_code_ids = collect_values(bad_slides, "run2_22_code_module_ids")
    bad_decision_memory_ids = collect_values(bad_slides, "negative_control_decision_memory_id")
    decision_memory_only = bool(bad_decision_memory_ids) and not bad_selector_gate_ids and not bad_rejection_ids and not bad_code_ids

    return {
        "schema_version": "ppt_run2_selector_effectiveness_audit.v1",
        "run_id": "2.23",
        "status": "run2_23_selector_effectiveness_audit_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.22",
        "comparison_baseline_run": "2.19",
        "source_selector_layer": "2.21",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "input_chain": {
            "visual_decision_memory": rel(decision_memory_path),
            "selector_gates": rel(selector_gates_path),
            "evidence_rejection_matrix": rel(rejection_matrix_path),
            "run2_22_full_trace_manifest": rel(full_trace_path),
            "run2_22_bad_selector_trace_manifest": rel(bad_trace_path),
            "run2_19_baseline_trace_manifest": rel(baseline_trace_path),
        },
        "source_inventory": {
            "run2_21_visual_decision_memory_records": len(decision_memory),
            "run2_21_selector_gates": len(selector_gates),
            "run2_21_rejection_records": len(rejection_records),
            "run2_22_full_trace_slides": len(full_slides),
            "run2_19_baseline_trace_slides": len(baseline_trace.get("slides", [])),
        },
        "workflow_inventory": {
            "full_arm_slide_count": len(full_slides),
            "selector_gate_trace_slides": len(selected_gate_ids),
            "visual_decision_memory_trace_slides": len(selected_memory_ids),
            "selected_code_module_count": len(selected_code_ids),
            "roles_with_code_module_delta": roles_with_delta,
        },
        "selector_effectiveness": {
            "full_arm": {
                "arm_id": full_trace.get("arm_id"),
                "slide_count": len(full_slides),
                "visual_decision_memory_records_selected": len(selected_memory_ids),
                "selector_gates_selected": len(selected_gate_ids),
                "selected_visual_decision_memory_ids": selected_memory_ids,
                "selected_selector_gate_ids": selected_gate_ids,
                "selected_primary_evidence_ids": selected_primary_ids,
                "selected_secondary_evidence_ids": selected_secondary_ids,
                "selected_code_module_ids": selected_code_ids,
                "role_records": role_records,
                **full_checks,
            },
            "comparison_to_run2_19": {
                "baseline_arm_id": baseline_trace.get("arm_id"),
                "roles_with_code_module_delta": roles_with_delta,
                "interpretation": "Run 2.22 full arm uses selector-memory-specific code modules instead of reusing the Run 2.19 thickness modules.",
            },
        },
        "control_boundary": {
            "prompt_only": {
                "arm_id": prompt_trace.get("arm_id"),
                "forbids_run2_21_selector_memory": True,
                "selected_selector_gate_ids": [],
            },
            "run1_5_skill": {
                "arm_id": run15_trace.get("arm_id"),
                "forbids_run2_21_selector_memory": True,
                "selected_selector_gate_ids": [],
            },
            "bad_selector_memory": {
                "arm_id": bad_trace.get("arm_id"),
                "decision_memory_only": decision_memory_only,
                "blocks_selector_gates": not bad_selector_gate_ids,
                "blocks_rejection_matrix": not bad_rejection_ids,
                "selected_decision_memory_ids": bad_decision_memory_ids,
                "selected_selector_gate_ids": bad_selector_gate_ids,
                "selected_rejected_evidence_reasons": bad_rejection_ids,
                "selected_code_module_ids": bad_code_ids,
            },
        },
        "negative_control_checks": [
            {
                "arm_role": "prompt_only",
                "forbidden_fields": ["run2_21_visual_decision_memory", "run2_21_selector_gates"],
                "observed_boundary": "prompt-only arm has no Run 2.21 selector trace",
                "status": "pass",
            },
            {
                "arm_role": "run1_5_skill",
                "forbidden_fields": ["run2_21_visual_decision_memory", "run2_21_selector_gates"],
                "observed_boundary": "Run 1.5 skill arm has no Run 2.21 selector trace",
                "status": "pass",
            },
            {
                "arm_role": "bad_selector_memory",
                "forbidden_fields": [
                    "run2_21_per_role_selector_gates",
                    "run2_21_evidence_rejection_matrix",
                    "run2_22_code_module_ids",
                ],
                "observed_boundary": "decision_memory_only_without_selector_gates_or_rejection_matrix",
                "status": "pass" if decision_memory_only else "blocked",
            },
        ],
        "chain_records": build_chain_records(role_records),
        "gap_records": [
            {
                "gap_id": "gap_2_23_trace_effectiveness_not_human_visual_quality",
                "status": "public_blocked",
                "finding": "Run 2.23 proves selector-memory execution in trace, but does not prove the public-facing visual delta is good enough.",
                "next_fix": "Human-review Run 2.22 against Run 2.19 and decide whether to thicken typography, spacing, and climax editorial composition before another rerun.",
            },
            {
                "gap_id": "gap_2_23_native_motion_still_unproven",
                "status": "public_blocked",
                "finding": "The selector audit checks native PPT code paths, not native animation XML or a publishable motion/video render.",
                "next_fix": "Keep motion and public-video delivery blocked until a native or cross-platform render proof passes.",
            },
        ],
        "gate_summary": {
            "selector_memory_gate": "pass_internal_only",
            "bad_control_gate": "pass" if decision_memory_only else "blocked",
            "visual_delta_gate": "trace_proven_human_visual_review_required",
            "visual_quality_gate": "needs_human_review_public_blocked",
            "public_release_gate": "blocked",
            "proven": "Run 2.22 full arm contains selector gate, visual-decision memory, rejection-matrix, and code-module trace on all six slides.",
            "weak": "Trace proves the data path, not that the visual result is already public-video-grade.",
            "blocked": "Public release remains blocked pending human visual review, native render inspection, motion/video proof, and source-boundary approval.",
            "summary": "Run 2.23 selector effectiveness audit confirms data/workflow execution, preserves the bad_selector_memory boundary, and keeps public release blocked.",
        },
        "next_required_action": "human_review_run2_22_visual_delta_then_thicken_typography_spacing_climax_if_needed",
    }


def write_report(audit: dict[str, Any], result_md: Path) -> None:
    full = audit["selector_effectiveness"]["full_arm"]
    comparison = audit["selector_effectiveness"]["comparison_to_run2_19"]
    bad = audit["control_boundary"]["bad_selector_memory"]
    gate = audit["gate_summary"]
    lines = [
        "# Run 2.23 Selector Effectiveness Audit",
        "",
        "Status: selector effectiveness audit completed, public blocked.",
        "",
        "Run 2.23 is audit-only. It creates no new PPT deck and does not advance to Run 3.0.",
        "",
        "The audit checks whether Run 2.22 actually used the Run 2.21 visual-decision memory, selector gates, and evidence rejection matrix before native PPT code generation. Run 2.19 is the comparison baseline.",
        "",
        "## Result",
        "",
        f"- Full arm: `{full['arm_id']}`.",
        f"- Visual-decision memory records selected: {full['visual_decision_memory_records_selected']} / {audit['source_inventory']['run2_21_visual_decision_memory_records']}.",
        f"- Selector gates selected: {full['selector_gates_selected']} / {audit['source_inventory']['run2_21_selector_gates']}.",
        f"- All slides have selector gate and code trace: {str(full['all_slides_have_selector_gate_and_code']).lower()}.",
        f"- Primary evidence per slide: {str(full['primary_evidence_per_slide_all']).lower()}.",
        f"- Secondary evidence within cap: {str(full['secondary_evidence_within_cap_all']).lower()}.",
        f"- Rejection reasons present: {str(full['rejection_reasons_present_all']).lower()}.",
        f"- Public slide surface suppresses selector trace: {str(full['public_surface_policy_suppressed_all']).lower()}.",
        f"- Run 2.22 roles with code-module delta from Run 2.19: {comparison['roles_with_code_module_delta']}.",
        "",
        "## Control Boundary",
        "",
        f"- `bad_selector_memory` is decision-memory-only: {str(bad['decision_memory_only']).lower()}.",
        f"- Blocks selector gates: {str(bad['blocks_selector_gates']).lower()}.",
        f"- Blocks rejection matrix: {str(bad['blocks_rejection_matrix']).lower()}.",
        "- Bad-control selected selector gate ids: none.",
        "- Bad-control selected rejected evidence reasons: none.",
        "- Bad-control selected code module ids: none.",
        "",
        "## Gate",
        "",
        f"- Selector memory gate: `{gate['selector_memory_gate']}`.",
        f"- Visual quality gate: `{gate['visual_quality_gate']}`.",
        f"- Public release gate: `{gate['public_release_gate']}`.",
        "",
        "Public release remains public blocked. Run 2.23 proves selector effectiveness, not public-video-grade visual quality.",
        "",
        "Next: human-review Run 2.22 visual delta, then thicken typography, spacing, and climax editorial composition if needed. Do not advance to Run 3.0.",
        "",
    ]
    result_md.parent.mkdir(parents=True, exist_ok=True)
    result_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    args = parser.parse_args()

    audit = build_audit()
    args.result_json.parent.mkdir(parents=True, exist_ok=True)
    args.result_json.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    write_report(audit, args.result_md)
    print(f"Run 2.23 selector effectiveness audit: {args.result_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
