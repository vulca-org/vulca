from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
DEFAULT_OUT_DIR = PACK
DEFAULT_RESULT_JSON = PACK / "results" / "run2_21_visual_decision_memory_result.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_21_visual_decision_memory_result.md"


ROLE_PLANS: dict[str, dict[str, Any]] = {
    "cover": {
        "primary": "thick_2_18_figma_launch_identity_system",
        "secondary": ["thick_2_18_duarte_slide_design_method", "thick_2_18_whitespace_powerpoint_method"],
        "memory": ["memory_2_18_launch_identity_field", "memory_2_18_typographic_whitespace_system"],
        "gates": ["gate_2_18_identity_field_selection", "gate_2_18_density_and_anti_copy_selection"],
        "module": ["drawRun219LaunchIdentityField"],
        "typography": "One short launch promise owns first read; secondary evidence appears only as a compact proof caption.",
        "spacing": "Reserve a large promise field, protect wide outer margins, and keep source-boundary text outside the hero read.",
        "composition": "Use one identity motif plus one proof cue; reject equal feature cards and visible workflow machinery.",
        "proof": "Generated native platform motif, not source brand marks or copied event imagery.",
        "risk": "The cover can still become a brand-pastiche unless source-boundary notes stay out of the public surface.",
    },
    "setup": {
        "primary": "thick_2_18_google_cloud_ai_platform_climax",
        "secondary": ["thick_2_18_figma_launch_identity_system", "thick_2_18_figma_design_to_production_surface"],
        "memory": ["memory_2_18_launch_identity_field", "memory_2_18_demo_sequence_route"],
        "gates": ["gate_2_18_usecase_source_selection", "gate_2_18_identity_field_selection"],
        "module": ["drawRun219ProductSurfaceTheater", "drawRun219DemoSequenceRoute"],
        "typography": "Name the business pressure first, then use one capability phrase and one product consequence label.",
        "spacing": "Separate pressure, capability, and product consequence into three macro zones with no dense text blocks.",
        "composition": "Turn AI capability into a visible workflow map, not a model list or feature pile.",
        "proof": "Native workflow map with one routed product consequence.",
        "risk": "Setup can look generic if the capability label is not tied to a visible workflow state.",
    },
    "contrast": {
        "primary": "thick_2_18_stripe_keynote_business_demo",
        "secondary": ["thick_2_18_figma_design_to_production_surface", "thick_2_18_duarte_slide_design_method"],
        "memory": ["memory_2_18_demo_sequence_route", "memory_2_18_product_surface_theater"],
        "gates": ["gate_2_18_demo_sequence_selection", "gate_2_18_product_surface_theater_selection"],
        "module": ["drawRun219DemoSequenceRoute"],
        "typography": "Use action-led labels for before, route, and resolved state; explanations route to notes.",
        "spacing": "Keep before and after asymmetric: before is compressed, route is narrow, resolved state is dominant.",
        "composition": "Stage contrast as one transition path instead of a side-by-side diagnostic table.",
        "proof": "Native ordered state route with a dominant resolved endpoint.",
        "risk": "The contrast slide can collapse back to equal panels if primary/secondary state weights are not enforced.",
    },
    "proof": {
        "primary": "thick_2_18_figma_design_to_production_surface",
        "secondary": ["thick_2_18_apple_liquid_glass_motion_surface", "thick_2_18_stripe_keynote_business_demo"],
        "memory": ["memory_2_18_product_surface_theater", "memory_2_18_material_depth_motion"],
        "gates": ["gate_2_18_product_surface_theater_selection", "gate_2_18_density_and_anti_copy_selection"],
        "module": ["drawRun219ProductSurfaceTheater", "drawRun219DensityGate"],
        "typography": "Short product-state labels only; no paragraph text inside the surface.",
        "spacing": "Largest area belongs to the product surface, with an annotation rail and protected inspection gutter.",
        "composition": "Use a native editable product theater surface with one readable operational state.",
        "proof": "Editable native product surface and secondary rail; no screenshots or copied UI chrome.",
        "risk": "Depth treatment can become decoration if it is not attached to product evidence.",
    },
    "climax": {
        "primary": "thick_2_18_stripe_metric_climax",
        "secondary": ["thick_2_18_google_cloud_ai_platform_climax", "thick_2_18_apple_liquid_glass_motion_surface"],
        "memory": ["memory_2_18_metric_climax_object", "memory_2_18_material_depth_motion"],
        "gates": ["gate_2_18_metric_climax_selection", "gate_2_18_demo_sequence_selection"],
        "module": ["drawRun219MetricClimaxObject"],
        "typography": "One source-backed outcome phrase is the only first-read object; caveats route below or to trace.",
        "spacing": "Use a stage field with generous margin; no adjacent dense table or competing metric cluster.",
        "composition": "Make one outcome object own the slide and suppress all secondary proof into a quiet layer.",
        "proof": "Editable outcome object with caveat rail and no invented figures.",
        "risk": "Climax can overclaim if the outcome label is not source-bounded and human reviewed.",
    },
    "close": {
        "primary": "thick_2_18_duarte_slide_design_method",
        "secondary": ["thick_2_18_whitespace_powerpoint_method", "thick_2_18_figma_launch_identity_system"],
        "memory": ["memory_2_18_typographic_whitespace_system", "memory_2_18_launch_identity_field"],
        "gates": ["gate_2_18_density_and_anti_copy_selection", "gate_2_18_usecase_source_selection"],
        "module": ["drawRun219QuietReleaseHandoff"],
        "typography": "One quiet handoff sentence plus one release boundary label; no retrospective checklist.",
        "spacing": "Keep the close sparse with a single next-step field and a separate blocked-release rail.",
        "composition": "End with a deliberate handoff state, not a summary dashboard.",
        "proof": "Native handoff field with public-blocked marker and next-run instruction.",
        "risk": "Close can feel bureaucratic if the release gate becomes the main visual story.",
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def rejection_reason(role: str, evidence_id: str) -> str:
    if "metric" in evidence_id and role != "climax":
        return "Held for climax so metric evidence does not compete with this slide's primary read."
    if "whitespace" in evidence_id:
        return "Applied as a global spacing method only when selected; rejected here to keep the role-specific evidence narrow."
    if "duarte" in evidence_id:
        return "Held as editorial method background; rejected here because a concrete product or business source is stronger."
    if "apple" in evidence_id and role not in {"proof", "climax"}:
        return "Material-depth evidence is held back to avoid decorative premium effects without product proof."
    if "google" in evidence_id and role not in {"setup", "climax"}:
        return "AI platform climax evidence is held back to avoid generic capability claims on this slide."
    if "stripe" in evidence_id and role not in {"contrast", "climax", "proof"}:
        return "Business-demo evidence is held back until the slide needs sequence or outcome proof."
    if "figma_design_to_production" in evidence_id and role not in {"setup", "contrast", "proof"}:
        return "Product-surface evidence is held back until an inspectable workflow surface is the main proof object."
    return "Rejected for this role so primary and secondary evidence stay specific and inspectable."


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str]:
    evidence_doc = read_json(PACK / "run2_18_multimodal_evidence_expansion.json")
    memory_doc = read_json(PACK / "run2_18_design_memory_expansion.json")
    gate_doc = read_json(PACK / "run2_18_workflow_gate_expansion.json")
    audit = read_json(PACK / "results" / "run2_20_trace_effectiveness_audit.json")
    evidence_ids = [record["record_id"] for record in evidence_doc["records"]]
    memory_ids = {record["memory_id"] for record in memory_doc["memory_expansions"]}
    gate_ids = {record["gate_id"] for record in gate_doc["gates"]}

    decisions: list[dict[str, Any]] = []
    selector_gates: list[dict[str, Any]] = []
    rejection_records: list[dict[str, Any]] = []

    for index, (role, plan) in enumerate(ROLE_PLANS.items(), start=1):
        primary = plan["primary"]
        secondary = plan["secondary"]
        selected = {primary, *secondary}
        rejected = [{"evidence_id": evidence_id, "reason": rejection_reason(role, evidence_id)} for evidence_id in evidence_ids if evidence_id not in selected]
        decision_id = f"vdm_2_21_{role}"
        gate_id = f"gate_2_21_{role}_selector"
        missing_memory = [item for item in plan["memory"] if item not in memory_ids]
        missing_gates = [item for item in plan["gates"] if item not in gate_ids]
        if primary not in evidence_ids or any(item not in evidence_ids for item in secondary) or missing_memory or missing_gates:
            raise ValueError(f"Run 2.21 role plan has invalid ids for {role}")

        decisions.append(
            {
                "decision_id": decision_id,
                "role": role,
                "slide_index": index,
                "primary_evidence_id": primary,
                "secondary_evidence_ids": secondary,
                "rejected_evidence": rejected,
                "selected_memory_ids": plan["memory"],
                "selected_gate_ids": plan["gates"],
                "typography_decision": plan["typography"],
                "spacing_decision": plan["spacing"],
                "composition_decision": plan["composition"],
                "proof_object_decision": plan["proof"],
                "code_generation_obligation": f"Next generated rerun must call {', '.join(plan['module'])} only after binding {decision_id} and {gate_id}.",
                "required_code_module_ids": plan["module"],
                "visual_quality_risk": plan["risk"],
                "source_boundary": "Use derived observations only; no raw media, copied layouts, source screenshots, brand marks, or transcript text.",
                "release_boundary": "public_blocked_until_visual_human_review_native_render_review_and_source_boundary_review",
            }
        )
        selector_gates.append(
            {
                "gate_id": gate_id,
                "role": role,
                "required_visual_decision_memory_id": decision_id,
                "required_primary_evidence_count": 1,
                "max_secondary_evidence_count": 2,
                "required_rejection_policy": "Every non-selected Run 2.18 evidence id must have a role-specific rejection reason.",
                "required_code_module_ids": plan["module"],
                "required_trace_fields": [
                    "run2_21_visual_decision_memory_id",
                    "run2_21_primary_evidence_id",
                    "run2_21_secondary_evidence_ids",
                    "run2_21_rejected_evidence_reasons",
                    "run2_21_selector_gate_id",
                    "run2_21_visual_decision_delta",
                ],
                "public_surface_policy": "trace_suppressed_from_public_slide_surface",
                "pass_fail_checks": [
                    "Exactly one primary evidence id is selected before native PPT drawing.",
                    "At most two secondary evidence ids are selected before native PPT drawing.",
                    "All rejected evidence ids have reasons and are kept out of public slide labels.",
                    "The required code module ids are recorded in the trace manifest.",
                ],
                "release_boundary": "public_blocked_until_run2_21_selector_is_consumed_by_next_generated_rerun_and_human_review_passes",
            }
        )
        rejection_records.append(
            {
                "role": role,
                "visual_decision_memory_id": decision_id,
                "primary_evidence_id": primary,
                "secondary_evidence_ids": secondary,
                "rejected_evidence": rejected,
                "all_evidence_accounted_for": {primary, *secondary, *(item["evidence_id"] for item in rejected)} == set(evidence_ids),
            }
        )

    decision_doc = {
        "schema_version": "ppt_run2_visual_decision_memory.v1",
        "status": "run2_21_visual_decision_memory_ready_public_blocked",
        "run_id": "2.21",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "derived_from": [
            "run2_18_multimodal_evidence_expansion.json",
            "run2_18_design_memory_expansion.json",
            "run2_18_workflow_gate_expansion.json",
            "results/run2_20_trace_effectiveness_audit.json",
        ],
        "quality_target": "make visual decisions explicit before another generated rerun",
        "visual_decision_memory": decisions,
    }
    selector_doc = {
        "schema_version": "ppt_run2_per_role_selector_gates.v1",
        "status": "run2_21_per_role_selector_gates_ready_public_blocked",
        "run_id": "2.21",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "gates": selector_gates,
    }
    rejection_doc = {
        "schema_version": "ppt_run2_evidence_rejection_matrix.v1",
        "status": "run2_21_evidence_rejection_matrix_ready_public_blocked",
        "run_id": "2.21",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "evidence_inventory": evidence_ids,
        "role_records": rejection_records,
    }
    result_doc = {
        "schema_version": 1,
        "run_id": "2.21",
        "status": "run2_21_visual_decision_memory_ready_public_blocked",
        "source_audit_run": "2.20",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "delivery_artifacts": {
            "pptx_paths": [],
            "rendered_slide_paths": [],
            "contact_sheet_paths": [],
            "html_motion_renderer_paths": [],
        },
        "artifact_counts": {
            "visual_decision_memory": len(decisions),
            "per_role_selector_gates": len(selector_gates),
            "evidence_rejection_records": len(rejection_records),
        },
        "input_chain": {
            "trace_effectiveness_audit": "docs/product/ppt-run2-data-skill-quality/results/run2_20_trace_effectiveness_audit.json",
            "evidence": "docs/product/ppt-run2-data-skill-quality/run2_18_multimodal_evidence_expansion.json",
            "memory": "docs/product/ppt-run2-data-skill-quality/run2_18_design_memory_expansion.json",
            "workflow_gates": "docs/product/ppt-run2-data-skill-quality/run2_18_workflow_gate_expansion.json",
        },
        "what_changed": [
            "Run 2.21 turns broad Run 2.19 evidence coverage into role-specific visual-decision memory.",
            "Each slide role now has exactly one primary evidence id, at most two secondary ids, and explicit rejected-evidence reasons.",
            "Per-role selector gates define the trace fields that the next generated rerun must record before native PPT drawing.",
        ],
        "release_boundary": "public_blocked_until_next_generated_rerun_consumes_run2_21_selectors_and_human_visual_review_passes",
        "next_required_action": "consume_run2_21_visual_decision_memory_before_next_generated_rerun",
    }
    markdown = build_markdown(result_doc)
    return decision_doc, selector_doc, rejection_doc, result_doc, markdown


def build_markdown(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Run 2.21 Visual-Decision Memory Result",
            "",
            "Status: visual-decision memory ready, public blocked.",
            "",
            "Run 2.21 is data/workflow-only. It creates no new PPT deck and does not advance to Run 3.0.",
            "",
            "It responds to Run 2.20 by turning broad trace effectiveness into specific visual-decision memory, a per-role selector, and an evidence rejection matrix.",
            "",
            "## Artifacts",
            "",
            "- `run2_21_visual_decision_memory.json`: one role-specific visual-decision memory record per slide role.",
            "- `run2_21_per_role_selector_gates.json`: one selector gate per role, requiring a primary evidence id, limited secondary ids, and trace fields.",
            "- `run2_21_evidence_rejection_matrix.json`: every Run 2.18 evidence id is either primary, secondary, or rejected with a reason for each role.",
            "- PPT delivery artifacts: none. `pptx_paths`, rendered slides, contact sheets, and motion renderer paths remain empty in this data/workflow-only run.",
            "",
            "## Gate",
            "",
            "Public release remains public blocked. This pass makes the next generated rerun more specific, but it does not prove visual quality by itself.",
            "",
            "Next: consume Run 2.21 visual-decision memory before the next generated rerun. Do not advance to Run 3.0.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    args = parser.parse_args()

    decision_doc, selector_doc, rejection_doc, result_doc, markdown = build_artifacts()
    write_json(args.out_dir / "run2_21_visual_decision_memory.json", decision_doc)
    write_json(args.out_dir / "run2_21_per_role_selector_gates.json", selector_doc)
    write_json(args.out_dir / "run2_21_evidence_rejection_matrix.json", rejection_doc)
    write_json(args.result_json, result_doc)
    args.result_md.parent.mkdir(parents=True, exist_ok=True)
    args.result_md.write_text(markdown, encoding="utf-8")
    print(f"Run 2.21 visual-decision memory: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
