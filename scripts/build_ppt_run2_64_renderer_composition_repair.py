from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
RESULTS = PACK / "results"

NEXT_ACTION = "run2_65_generate_four_arm_ppt_consuming_run2_64_renderer_composition_repair"
RUN2_64_TRACE_FIELDS = [
    "run2_64_dynamic_socket_renderer_id",
    "run2_64_semantic_diagram_renderer_id",
    "run2_64_text_fit_gate_id",
    "run2_64_renderer_dry_run_binding_id",
    "run2_64_dynamic_socket_plan_status",
    "run2_64_semantic_diagram_binding_status",
    "run2_64_text_fit_preflight_status",
]
OUTPUT_FILES = {
    "dynamic_socket": "run2_64_dynamic_socket_renderer_memory.json",
    "semantic_diagram": "run2_64_semantic_diagram_renderer_memory.json",
    "text_fit": "run2_64_text_fit_renderer_gates.json",
    "dry_run": "run2_64_renderer_dry_run_binding_matrix.json",
    "result_json": "run2_64_renderer_composition_repair_result.json",
    "result_md": "run2_64_renderer_composition_repair_result.md",
}
ROLE_DIAGRAM_TYPES = {
    "cover": "source_pack_to_editable_ppt_object",
    "setup": "source_to_memory_operating_loop",
    "contrast": "before_after_mechanism_delta",
    "proof": "inspection_workspace_board",
    "climax": "editable_ppt_preview_hero_object",
    "close": "release_handoff_chain",
}
ROLE_COMPOSITION_RECIPES = {
    "cover": [
        "one dominant source-pack object with nested input, memory, code, and editable PPT states",
        "socket labels attach to the object surface instead of a repeated legend",
        "proof badges sit as inspected chips on the object edge",
    ],
    "setup": [
        "draw a single operating loop with directional source, memory, gate, and renderer stages",
        "group sockets by loop stage rather than equal card rows",
        "use one active proof lane for the selected commercial brief",
    ],
    "contrast": [
        "use asymmetric before/after surfaces with one mechanism connector",
        "bind the connector label to a text-fit checked socket",
        "show proof delta as generated PPT state rather than abstract comparison copy",
    ],
    "proof": [
        "render a workspace board with source, gate, trace, and output panes",
        "make each pane carry one proof object binding",
        "avoid equal summary cards when the role is inspection",
    ],
    "climax": [
        "make the editable PPT preview the largest visual object",
        "draw code-generated slide details inside the hero object",
        "place proof sockets as surface annotations instead of separate badges",
    ],
    "close": [
        "draw a release handoff route from evidence to output to next repair",
        "separate blocked gate, passed data gate, and next generated rerun",
        "keep internal run ids trace-visible but not dominant public copy",
    ],
}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.64 missing required input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(data, indent=2)}\n", encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def by_role(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(record.get("role") or ""): record for record in records}


def list_field(record: dict[str, Any], field: str) -> list[Any]:
    value = record.get(field) or []
    return value if isinstance(value, list) else []


def active_copy_unit_keys(fusion: dict[str, Any]) -> list[str]:
    copy_units = fusion.get("source_copy_units") or {}
    return [key for key in copy_units if key]


def socket_bindings(fusion: dict[str, Any]) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    for binding in list_field(fusion, "socket_bindings"):
        if not isinstance(binding, dict):
            continue
        bindings.append(
            {
                "copy_unit_key": binding.get("copy_unit_key"),
                "socket_id": binding.get("socket_id"),
                "owning_shape_role": binding.get("owning_shape_role"),
                "character_budget": binding.get("character_budget"),
                "max_lines": binding.get("max_lines"),
                "minimum_font_size": binding.get("minimum_font_size"),
                "dynamic_socket_behavior": (
                    "render only when this copy unit is active for the slide; do not reuse a global "
                    "static socket plan block"
                ),
                "failure_status": binding.get("failure_status"),
            }
        )
    return bindings


def proof_object_bindings(role: str, bindings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    proof_like = [
        binding
        for binding in bindings
        if binding.get("copy_unit_key") in {"proof_badges", "annotations", "state_labels"}
    ]
    if len(proof_like) < 3:
        proof_like = bindings[:3]
    records: list[dict[str, Any]] = []
    for index, binding in enumerate(proof_like, start=1):
        records.append(
            {
                "proof_object_binding_id": f"proof_object_binding_2_64_{role}_{index}",
                "copy_unit_key": binding.get("copy_unit_key"),
                "source_socket_id": binding.get("socket_id"),
                "visual_object_role": binding.get("owning_shape_role"),
                "semantic_binding_rule": (
                    "the proof object must be visually attached to the role-specific diagram object, "
                    "not rendered as a detached generic badge"
                ),
            }
        )
    return records


def validate_inputs(
    run263_audit: dict[str, Any],
    run261_fusion: dict[str, Any],
    run261_selector: dict[str, Any],
    run261_gates: dict[str, Any],
) -> None:
    if run263_audit.get("run_id") != "2.63":
        raise ValueError("Run 2.64 expected Run 2.63 audit input")
    if run263_audit.get("root_cause_assessment", {}).get("primary_layer") != "renderer_composition_grammar":
        raise ValueError("Run 2.64 expected renderer_composition_grammar root cause")
    if run261_fusion.get("status") != "run2_61_text_socket_fusion_contracts_ready_public_blocked":
        raise ValueError("Run 2.64 expected Run 2.61 socket fusion input")
    if run261_selector.get("status") != "run2_61_story_to_visual_carrier_selector_ready_public_blocked":
        raise ValueError("Run 2.64 expected Run 2.61 visual carrier selector input")
    if run261_gates.get("status") != "run2_61_narrative_workflow_gates_ready_public_blocked":
        raise ValueError("Run 2.64 expected Run 2.61 narrative workflow gates input")


def build_artifacts() -> dict[str, dict[str, Any]]:
    run263_audit_path = RESULTS / "run2_63_narrative_proof_consumption_effectiveness_audit.json"
    run261_fusion_path = PACK / "run2_61_text_socket_fusion_contracts.json"
    run261_selector_path = PACK / "run2_61_story_to_visual_carrier_selector.json"
    run261_gates_path = PACK / "run2_61_narrative_workflow_gates.json"

    run263_audit = read_json(run263_audit_path)
    run261_fusion = read_json(run261_fusion_path)
    run261_selector = read_json(run261_selector_path)
    run261_gates = read_json(run261_gates_path)
    validate_inputs(run263_audit, run261_fusion, run261_selector, run261_gates)

    role_audit = by_role(run263_audit["data_consumption_assessment"]["role_records"])
    fusion_by_role = by_role(run261_fusion["text_socket_fusion_contracts"])
    selector_by_role = by_role(run261_selector["story_to_visual_carrier_records"])
    gate_by_role = by_role(run261_gates["narrative_workflow_gates"])
    roles = [
        str(record.get("role"))
        for record in run263_audit["data_consumption_assessment"]["role_records"]
        if record.get("role")
    ]
    blockers = sorted(run263_audit["root_cause_assessment"]["renderer_blockers"])

    dynamic_records: list[dict[str, Any]] = []
    diagram_records: list[dict[str, Any]] = []
    text_gate_records: list[dict[str, Any]] = []
    dry_run_records: list[dict[str, Any]] = []

    for role in roles:
        audit_record = role_audit[role]
        fusion = fusion_by_role[role]
        selector = selector_by_role[role]
        gate = gate_by_role[role]
        copy_keys = active_copy_unit_keys(fusion)
        bindings = socket_bindings(fusion)
        binding_keys = {str(binding.get("copy_unit_key")) for binding in bindings}
        unbound_keys = sorted(set(copy_keys) - binding_keys)
        orphan_bindings = [
            binding for binding in bindings if str(binding.get("copy_unit_key")) not in set(copy_keys)
        ]
        dynamic_id = f"dynamic_socket_renderer_2_64_{role}"
        diagram_id = f"semantic_diagram_renderer_2_64_{role}"
        text_gate_id = f"text_fit_gate_2_64_{role}"
        dry_run_id = f"renderer_dry_run_binding_2_64_{role}"
        proof_bindings = proof_object_bindings(role, bindings)

        dynamic_records.append(
            {
                "dynamic_socket_renderer_id": dynamic_id,
                "role": role,
                "source_run2_63_role_title": audit_record.get("title"),
                "source_run2_63_blockers": blockers,
                "source_text_socket_fusion_contract_id": fusion.get("fusion_contract_id"),
                "source_visual_carrier_selector_id": selector.get("selector_id"),
                "static_socket_plan_replaced": True,
                "active_copy_unit_keys": copy_keys,
                "active_socket_bindings": bindings,
                "dynamic_socket_plan_policy": (
                    "show only sockets active for this role; suppress repeated global socket legend; "
                    "send overflow diagnostics to trace/viewer"
                ),
                "public_surface_rule": (
                    "socket labels must attach to semantic visual objects, not float as detached cards"
                ),
                "bad_control_probe": f"fail_if_{role}_keeps_static_socket_plan_or_unbound_copy_units",
                "required_trace_fields_for_run2_65": RUN2_64_TRACE_FIELDS,
            }
        )
        diagram_records.append(
            {
                "semantic_diagram_renderer_id": diagram_id,
                "role": role,
                "source_run2_63_blockers": blockers,
                "source_visual_carrier_selector_id": selector.get("selector_id"),
                "source_visual_carrier_type": selector.get("visual_carrier_type"),
                "source_layout_module_id": selector.get("selected_layout_module_id"),
                "semantic_diagram_type": ROLE_DIAGRAM_TYPES[role],
                "native_ppt_composition_recipe": ROLE_COMPOSITION_RECIPES[role],
                "proof_object_bindings": proof_bindings,
                "forbid_generic_repeated_shape_system": True,
                "forbid_equal_card_cluster_as_primary_surface": True,
                "required_visual_difference_from_run2_62": (
                    "the role-specific diagram type must be visible before reading text"
                ),
                "bad_control_probe": f"fail_if_{role}_uses_generic_boxes_without_semantic_diagram_binding",
                "required_trace_fields_for_run2_65": RUN2_64_TRACE_FIELDS,
            }
        )
        text_gate_records.append(
            {
                "text_fit_gate_id": text_gate_id,
                "role": role,
                "source_text_socket_fusion_contract_id": fusion.get("fusion_contract_id"),
                "source_narrative_workflow_gate_id": gate.get("gate_id"),
                "runtime_claim_boundary": "must_be_verified_by_run2_65_render_trace",
                "preflight_gate_status": "metadata_gate_only_not_runtime_proof",
                "forbid_ellipsis_or_clipped_public_copy": True,
                "wrap_and_scale_policy": {
                    "prefer_wrap_over_truncate": True,
                    "minimum_font_size_by_socket": {
                        binding.get("socket_id"): binding.get("minimum_font_size")
                        for binding in bindings
                    },
                    "max_lines_by_socket": {
                        binding.get("socket_id"): binding.get("max_lines") for binding in bindings
                    },
                    "fallback_when_over_capacity": (
                        "move nonessential annotation detail to viewer while preserving headline, "
                        "state label, and proof object"
                    ),
                },
                "max_public_text_boxes_before_trace_overflow": max(8, int(audit_record.get("text_box_count") or 0) - 4),
                "bad_control_probe": f"fail_if_{role}_records_zero_truncation_without_runtime_trace",
                "required_trace_fields_for_run2_65": RUN2_64_TRACE_FIELDS,
            }
        )
        dry_run_records.append(
            {
                "renderer_dry_run_binding_id": dry_run_id,
                "role": role,
                "dynamic_socket_renderer_id": dynamic_id,
                "semantic_diagram_renderer_id": diagram_id,
                "text_fit_gate_id": text_gate_id,
                "required_copy_unit_keys": copy_keys,
                "active_socket_count": len(bindings),
                "proof_object_binding_count": len(proof_bindings),
                "all_required_copy_units_bound": not unbound_keys,
                "orphan_socket_count": len(orphan_bindings),
                "unbound_copy_unit_count": len(unbound_keys),
                "unbound_copy_unit_keys": unbound_keys,
                "orphan_socket_ids": [binding.get("socket_id") for binding in orphan_bindings],
                "ready_for_run2_65_consumption": not unbound_keys and not orphan_bindings,
                "required_trace_fields_for_run2_65": RUN2_64_TRACE_FIELDS,
            }
        )

    dynamic_socket = {
        "schema_version": "ppt_run2_dynamic_socket_renderer_memory.v1",
        "run_id": "2.64",
        "status": "run2_64_dynamic_socket_renderer_memory_ready_public_blocked",
        "source_audit_run": "2.63",
        "source_data_run": "2.61",
        "dynamic_socket_renderer_records": dynamic_records,
        "next_required_action": NEXT_ACTION,
    }
    semantic_diagram = {
        "schema_version": "ppt_run2_semantic_diagram_renderer_memory.v1",
        "run_id": "2.64",
        "status": "run2_64_semantic_diagram_renderer_memory_ready_public_blocked",
        "source_audit_run": "2.63",
        "source_data_run": "2.61",
        "semantic_diagram_renderer_records": diagram_records,
        "next_required_action": NEXT_ACTION,
    }
    text_fit = {
        "schema_version": "ppt_run2_text_fit_renderer_gates.v1",
        "run_id": "2.64",
        "status": "run2_64_text_fit_renderer_gates_ready_public_blocked",
        "source_audit_run": "2.63",
        "source_data_run": "2.61",
        "text_fit_renderer_gates": text_gate_records,
        "runtime_claim_boundary": "must_be_verified_by_run2_65_render_trace",
        "next_required_action": NEXT_ACTION,
    }
    dry_run = {
        "schema_version": "ppt_run2_renderer_dry_run_binding_matrix.v1",
        "run_id": "2.64",
        "status": "run2_64_renderer_dry_run_binding_matrix_ready_public_blocked",
        "source_audit_run": "2.63",
        "source_data_run": "2.61",
        "dry_run_binding_records": dry_run_records,
        "all_roles_ready_for_run2_65": all(
            record["ready_for_run2_65_consumption"] for record in dry_run_records
        ),
        "next_required_action": NEXT_ACTION,
    }
    result = {
        "schema_version": "ppt_run2_renderer_composition_repair_result.v1",
        "run_id": "2.64",
        "status": "run2_64_renderer_composition_repair_ready_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "source_audit_run": "2.63",
        "source_generated_run": "2.62",
        "source_data_run": "2.61",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "input_chain": {
            "run2_63_audit": rel(run263_audit_path),
            "run2_61_text_socket_fusion_contracts": rel(run261_fusion_path),
            "run2_61_story_to_visual_carrier_selector": rel(run261_selector_path),
            "run2_61_narrative_workflow_gates": rel(run261_gates_path),
        },
        "output_chain": {
            "dynamic_socket_renderer_memory": OUTPUT_FILES["dynamic_socket"],
            "semantic_diagram_renderer_memory": OUTPUT_FILES["semantic_diagram"],
            "text_fit_renderer_gates": OUTPUT_FILES["text_fit"],
            "renderer_dry_run_binding_matrix": OUTPUT_FILES["dry_run"],
        },
        "quality_delta": {
            "target_layer": "renderer_composition_grammar_repair_contract",
            "repairs_blockers": blockers,
            "dynamic_socket_records": len(dynamic_records),
            "semantic_diagram_records": len(diagram_records),
            "text_fit_gates": len(text_gate_records),
            "dry_run_roles_ready": sum(
                1 for record in dry_run_records if record["ready_for_run2_65_consumption"]
            ),
            "runtime_claim_boundary": "text_fit_and_collision_must_be_verified_by_run2_65_render_trace",
        },
        "next_generated_run_contract": {
            "run_id": "2.65",
            "required_trace_fields": RUN2_64_TRACE_FIELDS,
            "bad_control_arm": "bad_run2_64_without_renderer_composition_repair",
            "full_arm_pass_status": "run2_64_renderer_composition_repair_consumed_before_native_ppt_drawing",
        },
        "next_required_action": NEXT_ACTION,
        "release_boundary": (
            "public_blocked_until_run2_65_consumes_run2_64_and_proves_runtime_text_fit_and_visual_delta"
        ),
    }
    return {
        "dynamic_socket": dynamic_socket,
        "semantic_diagram": semantic_diagram,
        "text_fit": text_fit,
        "dry_run": dry_run,
        "result": result,
    }


def write_report(result: dict[str, Any], result_md: Path) -> None:
    quality = result["quality_delta"]
    contract = result["next_generated_run_contract"]
    lines = [
        "# Run 2.64 Renderer Composition Repair",
        "",
        "Status: data/workflow-only, public blocked.",
        "",
        "Run 2.64 creates no new PPT deck and does not advance to Run 3.0.",
        "",
        "It converts the Run 2.63 root cause into renderer contracts that Run 2.65 must consume before native PPT drawing.",
        "",
        "## Repair Contracts",
        "",
        "- dynamic socket renderer memory: replaces the repeated static socket plan with active per-role sockets.",
        "- semantic diagram renderer memory: maps each visual carrier into a role-specific semantic diagram instead of generic boxes.",
        "- text-fit renderer gates: define metadata preflight rules, while runtime fit must still be verified by Run 2.65 render trace.",
        "- dry-run binding matrix: checks required copy units, sockets, diagram bindings, and orphan sockets before rerun.",
        "",
        "## Result",
        "",
        f"- Target layer: `{quality['target_layer']}`.",
        f"- Dynamic socket records: {quality['dynamic_socket_records']} / 6.",
        f"- Semantic diagram records: {quality['semantic_diagram_records']} / 6.",
        f"- Text-fit gates: {quality['text_fit_gates']} / 6.",
        f"- Dry-run roles ready: {quality['dry_run_roles_ready']} / 6.",
        f"- Runtime boundary: `{quality['runtime_claim_boundary']}`.",
        "",
        "## Next Generated Run",
        "",
        f"- Run: {contract['run_id']}.",
        f"- Bad control: `{contract['bad_control_arm']}`.",
        f"- Full pass status: `{contract['full_arm_pass_status']}`.",
        "",
        f"Next: `{result['next_required_action']}`.",
        "",
        "Do not advance to Run 3.0.",
        "",
    ]
    result_md.parent.mkdir(parents=True, exist_ok=True)
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Run 2.64 renderer composition repair.")
    parser.add_argument("--out-dir", type=Path, default=PACK)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir
    artifacts = build_artifacts()
    write_json(out_dir / OUTPUT_FILES["dynamic_socket"], artifacts["dynamic_socket"])
    write_json(out_dir / OUTPUT_FILES["semantic_diagram"], artifacts["semantic_diagram"])
    write_json(out_dir / OUTPUT_FILES["text_fit"], artifacts["text_fit"])
    write_json(out_dir / OUTPUT_FILES["dry_run"], artifacts["dry_run"])
    write_json(out_dir / "results" / OUTPUT_FILES["result_json"], artifacts["result"])
    write_report(artifacts["result"], out_dir / "results" / OUTPUT_FILES["result_md"])
    print(
        json.dumps(
            {
                "status": artifacts["result"]["status"],
                "result_json": str(out_dir / "results" / OUTPUT_FILES["result_json"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
