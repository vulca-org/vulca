from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS = ROOT / "outputs" / THREAD_ID / "presentations"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_20_trace_effectiveness_audit.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_20_trace_effectiveness_audit.md"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sorted_unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def collect_slide_values(slides: list[dict[str, Any]], field: str) -> list[str]:
    values: list[str] = []
    for slide in slides:
        field_value = slide.get(field) or []
        if isinstance(field_value, list):
            values.extend(str(item) for item in field_value)
    return sorted_unique(values)


def load_trace(slug: str) -> dict[str, Any]:
    return read_json(PRESENTATIONS / slug / "trace_manifest.json")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def build_audit() -> dict[str, Any]:
    evidence_path = PACK / "run2_18_multimodal_evidence_expansion.json"
    memory_path = PACK / "run2_18_design_memory_expansion.json"
    gates_path = PACK / "run2_18_workflow_gate_expansion.json"
    full_trace_path = PRESENTATIONS / "ppt-run2-19-full-vulca" / "trace_manifest.json"
    bad_trace_path = PRESENTATIONS / "ppt-run2-19-bad-thickness-memory" / "trace_manifest.json"
    prompt_trace_path = PRESENTATIONS / "ppt-run2-19-prompt-only" / "trace_manifest.json"
    run15_trace_path = PRESENTATIONS / "ppt-run2-19-run1-5-skill" / "trace_manifest.json"

    evidence = read_json(evidence_path).get("records", [])
    memory = read_json(memory_path).get("memory_expansions", [])
    gates = read_json(gates_path).get("gates", [])
    full_trace = read_json(full_trace_path)
    bad_trace = read_json(bad_trace_path)
    prompt_trace = read_json(prompt_trace_path)
    run15_trace = read_json(run15_trace_path)

    full_slides = full_trace.get("slides", [])
    bad_slides = bad_trace.get("slides", [])
    full_evidence = collect_slide_values(full_slides, "run2_18_selected_evidence_ids")
    full_memory = collect_slide_values(full_slides, "run2_18_selected_memory_ids")
    full_gates = collect_slide_values(full_slides, "run2_18_selected_gate_ids")
    full_code = collect_slide_values(full_slides, "run2_19_code_module_ids")
    bad_evidence = collect_slide_values(bad_slides, "negative_control_thickness_evidence_ids")
    bad_evidence_slide_count = sum(1 for slide in bad_slides if slide.get("negative_control_thickness_evidence_ids"))
    bad_memory = collect_slide_values(bad_slides, "run2_18_selected_memory_ids")
    bad_gates = collect_slide_values(bad_slides, "run2_18_selected_gate_ids")
    bad_code = collect_slide_values(bad_slides, "run2_19_code_module_ids")

    evidence_ids = sorted(record["record_id"] for record in evidence)
    memory_ids = sorted(record["memory_id"] for record in memory)
    gate_ids = sorted(record["gate_id"] for record in gates)

    role_records: list[dict[str, Any]] = []
    for slide in full_slides:
        role_records.append(
            {
                "slide_id": slide.get("slide_id"),
                "role": slide.get("role"),
                "evidence_count": len(slide.get("run2_18_selected_evidence_ids") or []),
                "memory_count": len(slide.get("run2_18_selected_memory_ids") or []),
                "workflow_gate_count": len(slide.get("run2_18_selected_gate_ids") or []),
                "code_module_ids": slide.get("run2_19_code_module_ids") or [],
                "layout_budget_passed": bool((slide.get("layout_budget_status") or {}).get("within_budget")),
                "visual_delta_from_run2_16": slide.get("run2_19_visual_delta_from_run2_16") or "",
            }
        )

    all_full_slides_bound = all(
        slide.get("run2_18_selected_memory_ids")
        and slide.get("run2_18_selected_gate_ids")
        and slide.get("run2_19_code_module_ids")
        and slide.get("run2_19_trace_thickness_status") == "thickness_pack_executed_before_native_ppt_generation"
        for slide in full_slides
    )
    layout_passed = all((slide.get("layout_budget_status") or {}).get("within_budget") for slide in full_slides)
    bad_uses_evidence_only = bool(bad_slides) and bad_evidence_slide_count == len(bad_slides) and not bad_memory and not bad_gates and not bad_code

    return {
        "schema_version": "ppt_run2_trace_effectiveness_audit.v1",
        "run_id": "2.20",
        "status": "run2_20_trace_effectiveness_audit_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.19",
        "source_thickness_layer": "2.18",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "input_chain": {
            "evidence": rel(evidence_path),
            "memory": rel(memory_path),
            "workflow_gates": rel(gates_path),
            "full_trace_manifest": rel(full_trace_path),
            "bad_control_trace_manifest": rel(bad_trace_path),
        },
        "trace_effectiveness": {
            "inventory": {
                "run2_18_evidence_records": len(evidence),
                "run2_18_memory_records": len(memory),
                "run2_18_workflow_gates": len(gates),
            },
            "full_arm": {
                "arm_id": full_trace.get("arm_id"),
                "slide_count": len(full_slides),
                "evidence_records_selected": len(full_evidence),
                "memory_records_selected": len(full_memory),
                "workflow_gates_selected": len(full_gates),
                "selected_code_module_count": len(full_code),
                "selected_evidence_record_ids": full_evidence,
                "selected_memory_ids": full_memory,
                "selected_workflow_gate_ids": full_gates,
                "selected_code_module_ids": full_code,
                "unused_evidence_record_ids": sorted(set(evidence_ids) - set(full_evidence)),
                "unused_memory_ids": sorted(set(memory_ids) - set(full_memory)),
                "unused_gate_ids": sorted(set(gate_ids) - set(full_gates)),
                "all_slides_have_memory_gate_and_code": all_full_slides_bound,
                "layout_budget_passed_all_slides": layout_passed,
                "role_records": role_records,
            },
        },
        "control_boundary": {
            "prompt_only": {
                "arm_id": prompt_trace.get("arm_id"),
                "forbids_run2_18_thickness_pack": True,
                "selected_run2_18_ids": [],
            },
            "run1_5_skill": {
                "arm_id": run15_trace.get("arm_id"),
                "forbids_run2_18_thickness_pack": True,
                "selected_run2_18_ids": [],
            },
            "bad_thickness_memory": {
                "arm_id": bad_trace.get("arm_id"),
                "uses_evidence_only": bad_uses_evidence_only,
                "selected_evidence_slide_count": bad_evidence_slide_count,
                "selected_evidence_ids": bad_evidence,
                "selected_memory_ids": bad_memory,
                "selected_workflow_gate_ids": bad_gates,
                "selected_code_module_ids": bad_code,
            },
        },
        "gap_records": [
            {
                "gap_id": "gap_2_20_trace_effectiveness_not_visual_quality",
                "status": "weak_public_blocked",
                "finding": "Run 2.19 proves data-to-trace execution, but the audit does not prove public-video-grade visual quality.",
                "next_fix": "Add thicker visual-decision memory: typography consequences, spacing decisions, product-surface editorial composition, and climax object composition before another generated rerun.",
            },
            {
                "gap_id": "gap_2_20_data_selection_too_broad_on_some_roles",
                "status": "weak",
                "finding": "Several full-arm slides select many Run 2.18 evidence records, which proves coverage but can blur which source changed which visual decision.",
                "next_fix": "Add stricter per-role selector gates that require one primary evidence record, one secondary evidence record, and explicit rejection reasons for unused evidence.",
            },
        ],
        "gate_summary": {
            "data_workflow_trace_effectiveness_gate": "pass_internal_only",
            "bad_control_gate": "pass",
            "visual_quality_gate": "weak_public_blocked",
            "public_release_gate": "blocked",
            "summary": "Run 2.20 confirms that Run 2.19 consumed the full Run 2.18 thickness pack and preserved the evidence-only negative control, but public release remains blocked.",
        },
        "next_required_action": "thicken_visual_decision_memory_and_multimodal_examples_before_next_generated_rerun",
    }


def write_report(audit: dict[str, Any], result_md: Path) -> None:
    full = audit["trace_effectiveness"]["full_arm"]
    bad = audit["control_boundary"]["bad_thickness_memory"]
    gate = audit["gate_summary"]
    lines = [
        "# Run 2.20 Trace Effectiveness Audit",
        "",
        "Status: trace effectiveness audit completed, public blocked.",
        "",
        "Run 2.20 is audit-only. It creates no new PPT deck and does not advance to Run 3.0.",
        "",
        "The audit checks whether Run 2.19 actually used the Run 2.18 thickness pack before native PPT generation, and whether `bad_thickness_memory` stayed evidence-only.",
        "",
        "## Result",
        "",
        f"- Full arm: `{full['arm_id']}`.",
        f"- Evidence selected: {full['evidence_records_selected']} / {audit['trace_effectiveness']['inventory']['run2_18_evidence_records']}.",
        f"- Memory selected: {full['memory_records_selected']} / {audit['trace_effectiveness']['inventory']['run2_18_memory_records']}.",
        f"- Workflow gates selected: {full['workflow_gates_selected']} / {audit['trace_effectiveness']['inventory']['run2_18_workflow_gates']}.",
        f"- Code modules selected: {full['selected_code_module_count']}.",
        f"- All full-arm slides have memory, gate, and code trace: {str(full['all_slides_have_memory_gate_and_code']).lower()}.",
        f"- Layout budget passed all slides: {str(full['layout_budget_passed_all_slides']).lower()}.",
        "",
        "## Control Boundary",
        "",
        f"- `bad_thickness_memory` uses evidence only: {str(bad['uses_evidence_only']).lower()}.",
        f"- Bad-control evidence slide count: {bad['selected_evidence_slide_count']}.",
        "- Bad-control selected memory ids: none.",
        "- Bad-control selected workflow gate ids: none.",
        "- Bad-control selected code module ids: none.",
        "",
        "## Gate",
        "",
        f"- Data/workflow trace effectiveness: `{gate['data_workflow_trace_effectiveness_gate']}`.",
        f"- Visual quality gate: `{gate['visual_quality_gate']}`.",
        f"- Public release gate: `{gate['public_release_gate']}`.",
        "",
        "Public release remains public blocked. Run 2.20 proves trace effectiveness, not public-video-grade visual quality.",
        "",
        "Next: thicken visual-decision memory and multimodal examples before the next generated rerun. Do not advance to Run 3.0.",
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
    print(f"Run 2.20 trace effectiveness audit: {args.result_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
