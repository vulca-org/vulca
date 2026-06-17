from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS = ROOT / "outputs" / THREAD_ID / "presentations"
FULL_262 = PRESENTATIONS / "ppt-run2-62-full-vulca"
BAD_262 = PRESENTATIONS / "ppt-run2-62-bad-without-narrative-proof"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_63_narrative_proof_consumption_effectiveness_audit.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_63_narrative_proof_consumption_effectiveness_audit.md"

RUN262_FULL_STATUS = "run2_61_narrative_proof_dataset_consumed_before_native_ppt_drawing"
RUN262_BAD_STATUS = "fail_missing_run2_61"
NEXT_ACTION = (
    "build_run2_64_renderer_composition_repair_for_dynamic_sockets_and_semantic_diagrams_before_rerun"
)
ROOT_CAUSE = (
    "run2_62_consumes_narrative_proof_but_renderer_composition_grammar_collapses_it_into_"
    "generic_static_blocks"
)
RENDERER_BLOCKERS = [
    "static_socket_plan_repeated_on_every_slide",
    "generic_native_shape_grammar_collapses_role_specific_visual_carriers",
    "text_fit_and_wrapping_not_trace_gated",
    "semantic_diagram_labels_not_bound_to_active_slide_proof",
]
ROLE_RENDERER_REPAIRS = {
    "cover": "replace repeated socket legend with a role-specific source-pack hero object and visible proof chain.",
    "setup": "draw the source-to-memory operating loop as one semantic system instead of six equal cards.",
    "contrast": "make before/after labels and connector copy text-fit gated so mechanism contrast cannot truncate.",
    "proof": "turn the inspection board into a readable proof workspace with active source, gate, and output panes.",
    "climax": "make the editable PPT preview the dominant object with code-generated surface details, not a generic circle.",
    "close": "make the release handoff dynamic: gates, evidence, output, and next repair step should occupy distinct zones.",
}


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.63 audit missing required {label}: {path}")


def read_json(path: Path) -> dict[str, Any]:
    require_file(path, "JSON input")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(data, indent=2)}\n", encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def list_field(record: dict[str, Any], field: str) -> list[Any]:
    value = record.get(field) or []
    return value if isinstance(value, list) else []


def string_list_field(record: dict[str, Any], field: str) -> list[str]:
    return [str(item) for item in list_field(record, field) if item]


def average(values: list[int]) -> float:
    return round(sum(values) / len(values), 1) if values else 0.0


def has_run261_contracts(slide: dict[str, Any]) -> bool:
    return (
        str(slide.get("run2_61_narrative_proof_id") or "").startswith("narrative_proof_2_61_")
        and str(slide.get("run2_61_visual_carrier_selector_id") or "").startswith(
            "visual_carrier_selector_2_61_"
        )
        and str(slide.get("run2_61_text_socket_fusion_contract_id") or "").startswith(
            "text_socket_fusion_2_61_"
        )
        and str(slide.get("run2_61_public_proof_replacement_id") or "").startswith(
            "public_proof_replacement_2_61_"
        )
        and str(slide.get("run2_61_narrative_workflow_gate_id") or "").startswith("gate_2_61_")
    )


def has_socket_binding(slide: dict[str, Any]) -> bool:
    return int(slide.get("run2_62_socket_binding_count") or 0) >= 5


def has_required_answer(slide: dict[str, Any]) -> bool:
    return slide.get("run2_62_required_answer_visible") == "pass_internal"


def is_bad_without_run261(slide: dict[str, Any]) -> bool:
    return (
        all((slide.get(field) or "") == "" for field in RUN2_61_FIELDS)
        and slide.get("run2_62_narrative_proof_consumption_status") == RUN262_BAD_STATUS
        and int(slide.get("run2_62_socket_binding_count") or 0) == 0
    )


RUN2_61_FIELDS = [
    "run2_61_narrative_proof_id",
    "run2_61_visual_carrier_selector_id",
    "run2_61_text_socket_fusion_contract_id",
    "run2_61_public_proof_replacement_id",
    "run2_61_narrative_workflow_gate_id",
]


def role_records(full_trace: dict[str, Any], bad_trace: dict[str, Any]) -> list[dict[str, Any]]:
    bad_by_role = {slide.get("role"): slide for slide in bad_trace.get("slides", [])}
    records: list[dict[str, Any]] = []
    for slide in full_trace.get("slides", []):
        role = str(slide.get("role") or "")
        bad = bad_by_role.get(role, {})
        metrics = slide.get("layout_metrics") or {}
        product_surface = str(metrics.get("product_system_surface_kind") or "")
        records.append(
            {
                "slide_id": slide.get("slide_id"),
                "role": role,
                "title": slide.get("title"),
                "product_system_surface_kind": product_surface,
                "run2_61_contracts_bound": has_run261_contracts(slide),
                "run2_62_socket_binding_count": slide.get("run2_62_socket_binding_count"),
                "run2_62_public_proof_object_count": slide.get("run2_62_public_proof_object_count"),
                "run2_62_required_answer_visible": slide.get("run2_62_required_answer_visible"),
                "visible_words": metrics.get("visible_words"),
                "text_box_count": metrics.get("text_box_count"),
                "zones": metrics.get("zones"),
                "bad_control_missing_run2_61": is_bad_without_run261(bad),
                "renderer_blockers": RENDERER_BLOCKERS,
                "role_specific_repair_requirement": ROLE_RENDERER_REPAIRS.get(role, ""),
                "interpretation": (
                    "The slide carries Run 2.61 narrative proof, carrier, socket, replacement, and "
                    "gate ids, so the next repair should target how the renderer turns those ids into "
                    "role-specific visual objects and text sockets."
                ),
            }
        )
    return records


def validate_inputs(
    full_trace: dict[str, Any],
    bad_trace: dict[str, Any],
    run262_result: dict[str, Any],
    run261_narrative: dict[str, Any],
    run261_fusion: dict[str, Any],
    run261_gates: dict[str, Any],
) -> None:
    if full_trace.get("arm_id") != "run2_62_full_narrative_proof":
        raise ValueError("Run 2.63 audit expected Run 2.62 full trace")
    if full_trace.get("run2_62_narrative_proof_consumption_status") != RUN262_FULL_STATUS:
        raise ValueError("Run 2.63 audit expected Run 2.62 full consumption status")
    if bad_trace.get("arm_id") != "bad_run2_60_without_run2_61_narrative_proof_dataset":
        raise ValueError("Run 2.63 audit expected Run 2.62 bad missing narrative proof trace")
    if run262_result.get("status") != "run2_62_narrative_proof_rerun_public_blocked":
        raise ValueError("Run 2.63 audit expected Run 2.62 result")
    if run261_narrative.get("status") != "run2_61_narrative_proof_dataset_ready_public_blocked":
        raise ValueError("Run 2.63 audit expected Run 2.61 narrative proof dataset")
    if run261_fusion.get("status") != "run2_61_text_socket_fusion_contracts_ready_public_blocked":
        raise ValueError("Run 2.63 audit expected Run 2.61 text socket fusion contracts")
    if run261_gates.get("status") != "run2_61_narrative_workflow_gates_ready_public_blocked":
        raise ValueError("Run 2.63 audit expected Run 2.61 narrative workflow gates")

    full_roles = [slide.get("role") for slide in full_trace.get("slides", [])]
    bad_roles = [slide.get("role") for slide in bad_trace.get("slides", [])]
    if len(full_roles) != 6 or len(bad_roles) != 6 or set(full_roles) != set(bad_roles):
        raise ValueError("Run 2.63 audit expected six matching full/bad slide roles")


def build_audit() -> dict[str, Any]:
    full_trace_path = FULL_262 / "trace_manifest.json"
    bad_trace_path = BAD_262 / "trace_manifest.json"
    run262_result_path = PACK / "results" / "run2_62_narrative_proof_rerun_result.json"
    run261_narrative_path = PACK / "run2_61_narrative_proof_dataset.json"
    run261_selector_path = PACK / "run2_61_story_to_visual_carrier_selector.json"
    run261_fusion_path = PACK / "run2_61_text_socket_fusion_contracts.json"
    run261_policy_path = PACK / "run2_61_source_to_public_proof_policy.json"
    run261_gates_path = PACK / "run2_61_narrative_workflow_gates.json"
    four_arm_path = PRESENTATIONS / "run2-62-four-arm-contact-sheet.png"
    full_contact_path = FULL_262 / "preview" / "contact-sheet.png"
    full_series_path = PRESENTATIONS / "run2-full-skill-series-horizontal.png"

    full_trace = read_json(full_trace_path)
    bad_trace = read_json(bad_trace_path)
    run262_result = read_json(run262_result_path)
    run261_narrative = read_json(run261_narrative_path)
    run261_selector = read_json(run261_selector_path)
    run261_fusion = read_json(run261_fusion_path)
    run261_policy = read_json(run261_policy_path)
    run261_gates = read_json(run261_gates_path)
    require_file(four_arm_path, "Run 2.62 four-arm contact sheet")
    require_file(full_contact_path, "Run 2.62 full-arm contact sheet")
    require_file(full_series_path, "Run 2 full-skill series sheet")
    validate_inputs(full_trace, bad_trace, run262_result, run261_narrative, run261_fusion, run261_gates)

    full_slides = full_trace.get("slides", [])
    bad_slides = bad_trace.get("slides", [])
    records = role_records(full_trace, bad_trace)
    full_contract_count = sum(1 for slide in full_slides if has_run261_contracts(slide))
    full_socket_count = sum(1 for slide in full_slides if has_socket_binding(slide))
    full_proof_count = sum(
        1 for slide in full_slides if int(slide.get("run2_62_public_proof_object_count") or 0) >= 2
    )
    full_required_answer_count = sum(1 for slide in full_slides if has_required_answer(slide))
    bad_missing_count = sum(1 for slide in bad_slides if is_bad_without_run261(slide))
    visible_words = [
        int((slide.get("layout_metrics") or {}).get("visible_words") or 0)
        for slide in full_slides
    ]
    text_boxes = [
        int((slide.get("layout_metrics") or {}).get("text_box_count") or 0)
        for slide in full_slides
    ]
    surface_kinds = {
        str((slide.get("layout_metrics") or {}).get("product_system_surface_kind") or "")
        for slide in full_slides
    }
    data_consumed = len(full_slides) == 6 and full_contract_count == 6 and full_socket_count == 6
    bad_boundary = len(bad_slides) == 6 and bad_missing_count == 6

    return {
        "schema_version": "ppt_run2_narrative_proof_consumption_effectiveness_audit.v1",
        "run_id": "2.63",
        "status": "run2_63_narrative_proof_consumption_effectiveness_audit_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_generated_run": "2.62",
        "source_data_run": "2.61",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "input_chain": {
            "run2_62_full_trace_manifest": rel(full_trace_path),
            "run2_62_bad_trace_manifest": rel(bad_trace_path),
            "run2_62_rerun_result": rel(run262_result_path),
            "run2_61_narrative_proof_dataset": rel(run261_narrative_path),
            "run2_61_story_to_visual_carrier_selector": rel(run261_selector_path),
            "run2_61_text_socket_fusion_contracts": rel(run261_fusion_path),
            "run2_61_source_to_public_proof_policy": rel(run261_policy_path),
            "run2_61_narrative_workflow_gates": rel(run261_gates_path),
            "run2_62_four_arm_contact_sheet": rel(four_arm_path),
            "run2_62_full_contact_sheet": rel(full_contact_path),
            "run2_full_skill_series_sheet": rel(full_series_path),
        },
        "source_inventory": {
            "run2_61_narrative_records": len(run261_narrative["narrative_proof_records"]),
            "run2_61_visual_carrier_records": len(run261_selector["story_to_visual_carrier_records"]),
            "run2_61_text_socket_contracts": len(run261_fusion["text_socket_fusion_contracts"]),
            "run2_61_source_policy_rules": len(run261_policy.get("policy_rules", [])),
            "run2_61_narrative_workflow_gates": len(run261_gates["narrative_workflow_gates"]),
            "run2_62_full_trace_slides": len(full_slides),
            "run2_62_bad_trace_slides": len(bad_slides),
        },
        "data_consumption_assessment": {
            "run2_61_data_consumed": data_consumed,
            "bad_control_boundary_passed": bad_boundary,
            "full_arm_id": full_trace.get("arm_id"),
            "bad_control_arm_id": bad_trace.get("arm_id"),
            "full_slides_with_run2_61_contracts": full_contract_count,
            "full_slides_with_socket_bindings": full_socket_count,
            "full_slides_with_public_proof_objects": full_proof_count,
            "full_slides_with_required_answer_visible": full_required_answer_count,
            "bad_control_without_run2_61_contracts": bad_missing_count,
            "distinct_product_surface_kinds_in_trace": sorted(surface_kinds),
            "role_records": records,
        },
        "renderer_effectiveness_assessment": {
            "trace_has_role_specific_surface_kinds": len(surface_kinds) == 6,
            "public_surface_still_not_video_grade": True,
            "average_visible_words_per_slide": average(visible_words),
            "average_text_boxes_per_slide": average(text_boxes),
            "artifact_review_status": "advisory_not_human_confirmed",
            "artifact_review_findings": [
                "static socket plan appears repeated across all six slides",
                "slide 03 shows visible text truncation in a dark diagram block",
                "node and proof diagrams are clean but still rely on generic boxes and circles",
                "composition rhythm is more consistent than the bad arm but not yet a high-aesthetic public presentation",
            ],
            "why_more_raw_data_is_not_the_next_move": (
                "The trace already shows six role-specific narrative records, carriers, socket contracts, "
                "public proof replacements, and gates. The failure happens after consumption, when those "
                "contracts are translated into repeated native PPT components."
            ),
        },
        "root_cause_assessment": {
            "primary_layer": "renderer_composition_grammar",
            "not_primary_layer": "raw_data_or_workflow_consumption",
            "root_cause_primary": ROOT_CAUSE,
            "renderer_blockers": RENDERER_BLOCKERS,
            "required_repair_primitives": [
                "dynamic_socket_plan_component",
                "role_specific_semantic_diagram_renderer",
                "text_fit_and_wrap_gate_before_export",
                "proof_object_to_visual_object_binding",
                "contact_sheet_sameness_score_before_acceptance",
            ],
        },
        "gate_summary": {
            "data_consumption_gate": "pass_internal" if data_consumed else "blocked",
            "bad_control_gate": "pass" if bad_boundary else "blocked",
            "renderer_effectiveness_gate": "blocked",
            "public_release_gate": "blocked",
            "summary": (
                "Run 2.63 confirms Run 2.62 consumes Run 2.61 correctly. The next repair should "
                "change renderer/composition behavior, especially dynamic sockets, semantic diagrams, "
                "and text-fit gates, before another four-arm rerun."
            ),
        },
        "next_required_action": NEXT_ACTION,
        "release_boundary": (
            "public_blocked_until_run2_64_repairs_renderer_composition_grammar_and_reruns_four_arms"
        ),
    }


def write_report(audit: dict[str, Any], result_md: Path) -> None:
    data = audit["data_consumption_assessment"]
    renderer = audit["renderer_effectiveness_assessment"]
    root = audit["root_cause_assessment"]
    gate = audit["gate_summary"]
    lines = [
        "# Run 2.63 Narrative Proof Consumption Effectiveness Audit",
        "",
        "Status: audit-only, public blocked.",
        "",
        "Run 2.63 creates no new PPT deck and does not advance to Run 3.0.",
        "",
        "The audit asks a narrow question: 2.62 consumes 2.61, but does that consumption create a stronger public-facing presentation surface?",
        "",
        "## Result",
        "",
        f"- 2.62 consumes 2.61: {str(data['run2_61_data_consumed']).lower()}.",
        f"- Full-arm slides with Run 2.61 contracts: {data['full_slides_with_run2_61_contracts']} / 6.",
        f"- Full-arm slides with socket bindings: {data['full_slides_with_socket_bindings']} / 6.",
        f"- Bad control without Run 2.61 contracts: {data['bad_control_without_run2_61_contracts']} / 6.",
        "",
        "## Root Cause",
        "",
        f"- Primary layer: `{root['primary_layer']}`.",
        f"- Not primary layer: `{root['not_primary_layer']}`.",
        f"- Root cause: `{root['root_cause_primary']}`.",
        "",
        "The problem is not that the data/workflow layer is absent. The problem is renderer/composition grammar: the proof data is entering native drawing, then getting flattened into repeated shape systems.",
        "",
        "## Renderer Blockers",
        "",
        "- static socket plan repeated on every slide.",
        "- generic native shape grammar collapses role-specific visual carriers.",
        "- text fit and wrapping are not trace-gated; slide 03 can truncate text.",
        "- semantic diagram labels are not bound tightly enough to active slide proof.",
        "",
        "## Why Not Just Add More Data",
        "",
        renderer["why_more_raw_data_is_not_the_next_move"],
        "",
        "## Gate",
        "",
        f"- Data consumption gate: `{gate['data_consumption_gate']}`.",
        f"- Bad control gate: `{gate['bad_control_gate']}`.",
        f"- Renderer effectiveness gate: `{gate['renderer_effectiveness_gate']}`.",
        f"- Public release gate: `{gate['public_release_gate']}`.",
        "",
        f"Next: Run 2.64 should `{audit['next_required_action']}`.",
        "",
        "Do not advance to Run 3.0.",
        "",
    ]
    result_md.parent.mkdir(parents=True, exist_ok=True)
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Run 2.62 narrative proof consumption effectiveness."
    )
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_audit()
    write_json(args.result_json, audit)
    write_report(audit, args.result_md)
    print(json.dumps({"status": audit["status"], "result_json": str(args.result_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
