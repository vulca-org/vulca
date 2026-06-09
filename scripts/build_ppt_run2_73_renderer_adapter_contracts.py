from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
SOURCE_EXPANSION = PACK / "run2_73_scene_plan_expansion.json"
SOURCE_VALIDATION = PACK / "run2_73_renderer_input_validation.json"
SOURCE_VISUAL_GRAMMAR = PACK / "run2_73_visual_grammar_modules.json"
OUTPUT = PACK / "run2_73_renderer_adapter_contracts.json"

FORBIDDEN_RUNTIME_IMPORTS = {
    "importlib",
    "subprocess",
    "pptx",
    "playwright",
    "runpy",
    "selenium",
    "webbrowser",
}
FORBIDDEN_DYNAMIC_IMPORT_CALLS = {"__import__", "eval", "exec"}
FORBIDDEN_INVOCATIONS = [
    "renderer_rerun",
    "pptx_output",
    "html_viewer",
    "public_release",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_inputs() -> list[dict[str, Any]]:
    return [
        {
            "path": "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
            "available": SOURCE_EXPANSION.exists(),
            "use_in_this_artifact": "Provide D2 renderer-ready semantic components, visual containers, and expanded renderer action bindings.",
        },
        {
            "path": "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_input_validation.json",
            "available": SOURCE_VALIDATION.exists(),
            "use_in_this_artifact": "Provide D3 pass/fail validation and renderer handoff status before adapter binding.",
        },
        {
            "path": "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
            "available": SOURCE_VISUAL_GRAMMAR.exists(),
            "use_in_this_artifact": "Provide Part E visual grammar module, main structure, draw order, and geometry blueprint.",
        },
    ]


def index_by_key(records: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for record in records:
        record_key = record.get(key)
        if not isinstance(record_key, str) or not record_key:
            raise ValueError(f"{label} record missing string key {key}")
        if record_key in index:
            raise ValueError(f"{label} duplicate key: {record_key}")
        index[record_key] = record
    return index


def role_sequence(expansion: dict[str, Any]) -> list[str]:
    roles = []
    for structure in expansion.get("scene_structures", []):
        role = structure.get("role")
        if not isinstance(role, str) or not role:
            raise ValueError("D2 scene structure missing role")
        roles.append(role)
    if not roles:
        raise ValueError("D2 scene structures are empty")
    if len(set(roles)) != len(roles):
        raise ValueError("D2 scene structures contain duplicate roles")
    return roles


def assert_role_alignment(
    roles: list[str],
    validation_by_role: dict[str, dict[str, Any]],
    grammar_by_role: dict[str, dict[str, Any]],
) -> None:
    expected = set(roles)
    if set(validation_by_role) != expected:
        raise ValueError("D3 validation roles must match D2 scene roles")
    if set(grammar_by_role) != expected:
        raise ValueError("Part E visual grammar page roles must match D2 scene roles")


def adapter_scene_record(
    role: str,
    expansion: dict[str, Any],
    validation: dict[str, Any],
    grammar_page: dict[str, Any],
    blueprint: dict[str, Any],
) -> dict[str, Any]:
    module_id = grammar_page["primary_visual_grammar_module"]
    semantic_components = expansion["semantic_components"]
    visual_containers = expansion["visual_containers"]
    action_bindings = expansion["expanded_renderer_action_bindings"]
    blocking_issues = list(validation.get("blocking_issues", []))
    if validation.get("status") != "pass":
        blocking_issues.append(
            {
                "issue_id": "source_d3_validation_not_passed",
                "severity": "blocking",
                "role": role,
                "location": "source_renderer_input_validation",
                "message": "Renderer adapter requires a passing D3 scene validation record.",
            }
        )
    if validation.get("renderer_handoff", {}).get("can_handoff_to_renderer") is not True:
        blocking_issues.append(
            {
                "issue_id": "source_d3_handoff_not_approved",
                "severity": "blocking",
                "role": role,
                "location": "source_renderer_input_validation.renderer_handoff",
                "message": "Renderer adapter requires D3 handoff approval.",
            }
        )

    return {
        "adapter_scene_id": f"renderer_adapter_2_73_{role}",
        "role": role,
        "slide_index": expansion["slide_index"],
        "source_expansion_id": expansion["expansion_id"],
        "source_validation_id": validation["validation_id"],
        "source_visual_grammar_page_type": grammar_page["page_type"],
        "validation_status": validation["status"],
        "adapter_blocking_issues": blocking_issues,
        "visual_grammar_binding": {
            "module_id": module_id,
            "module_variant": grammar_page["module_variant"],
            "main_structure": grammar_page["main_structure"],
            "draw_order": grammar_page["draw_order"],
            "forbidden_fallbacks": grammar_page["forbidden_fallbacks"],
            "success_probe": grammar_page["success_probe"],
        },
        "geometry_blueprint_binding": {
            "module_id": blueprint["module_id"],
            "coordinate_system": blueprint["coordinate_system"],
            "primary_structure_is_not": blueprint["primary_structure_is_not"],
            "primary_structure_is": blueprint["primary_structure_is"],
            "native_ppt_shape_plan": blueprint["native_ppt_shape_plan"],
            "content_attachment_points": blueprint["content_attachment_points"],
        },
        "renderer_adapter_manifest": {
            "semantic_component_ids": [
                component["component_id"]
                for component in semantic_components.values()
            ],
            "visual_container_ids": [
                container["container_id"]
                for container in visual_containers
            ],
            "expanded_renderer_binding_ids": [
                binding["binding_id"]
                for binding in action_bindings
            ],
            "d3_renderer_handoff": validation["renderer_handoff"],
            "d2_off_canvas_contract": expansion["off_canvas_contract"],
        },
        "adapter_renderer_instructions": {
            "draw_primary_structure_before_components": True,
            "apply_geometry_blueprint_before_component_layout": True,
            "bind_semantic_components_before_geometry": True,
            "preserve_off_canvas_contract": True,
            "renderer_execution_allowed_in_this_artifact": False,
            "public_release_allowed_in_this_artifact": False,
        },
    }


def build_adapter_contracts(
    expansion: dict[str, Any] | None = None,
    validation: dict[str, Any] | None = None,
    grammar: dict[str, Any] | None = None,
) -> dict[str, Any]:
    expansion = expansion or read_json(SOURCE_EXPANSION)
    validation = validation or read_json(SOURCE_VALIDATION)
    grammar = grammar or read_json(SOURCE_VISUAL_GRAMMAR)

    roles = role_sequence(expansion)
    expansion_by_role = index_by_key(expansion["scene_structures"], "role", "D2 scene")
    validation_by_role = index_by_key(validation["scene_validation_results"], "role", "D3 validation")
    grammar_by_role = index_by_key(grammar["page_type_to_visual_grammar"], "page_type", "Part E page")
    blueprint_by_module = index_by_key(grammar["module_geometry_blueprints"], "module_id", "Part E blueprint")
    assert_role_alignment(roles, validation_by_role, grammar_by_role)

    records = []
    for role in roles:
        grammar_page = grammar_by_role[role]
        module_id = grammar_page["primary_visual_grammar_module"]
        if module_id not in blueprint_by_module:
            raise ValueError(f"Part E blueprint missing module: {module_id}")
        records.append(
            adapter_scene_record(
                role,
                expansion_by_role[role],
                validation_by_role[role],
                grammar_page,
                blueprint_by_module[module_id],
            )
        )

    blocking_issue_count = sum(
        len(record["adapter_blocking_issues"])
        for record in records
    )
    status = (
        "run2_73_renderer_adapter_contracts_ready_public_blocked"
        if blocking_issue_count == 0
        else "run2_73_renderer_adapter_contracts_failed_public_blocked"
    )
    return {
        "artifact_id": "run2_73_renderer_adapter_contracts",
        "part": "Part E2",
        "schema_version": "ppt_run2_73_renderer_adapter_contracts.v1",
        "status": status,
        "stage_policy": "part_e2_renderer_adapter_contracts_only_no_renderer_rerun_no_public_release",
        "source_scene_plan_expansion": "run2_73_scene_plan_expansion.json",
        "source_renderer_input_validation": "run2_73_renderer_input_validation.json",
        "source_visual_grammar_modules": "run2_73_visual_grammar_modules.json",
        "source_inputs": source_inputs(),
        "artifact_scope": {
            "starts": [
                "bind_validated_d2_scene_structures_to_part_e_visual_grammar",
                "prepare_renderer_adapter_manifest_from_d2_d3_e_inputs",
            ],
            "does_not_start": FORBIDDEN_INVOCATIONS,
        },
        "execution_guard": {
            "mode": "adapter_contract_only",
            "rendering_subprocesses_allowed": False,
            "allowed_side_effects": [
                "read_run2_73_scene_plan_expansion_json",
                "read_run2_73_renderer_input_validation_json",
                "read_run2_73_visual_grammar_modules_json",
                "write_run2_73_renderer_adapter_contracts_json",
            ],
            "forbidden_invocations": FORBIDDEN_INVOCATIONS,
            "forbidden_runtime_imports": sorted(FORBIDDEN_RUNTIME_IMPORTS),
            "forbidden_dynamic_import_calls": sorted(FORBIDDEN_DYNAMIC_IMPORT_CALLS),
        },
        "adapter_policy": {
            "must_consume_d2_scene_plan_expansion": True,
            "must_consume_d3_renderer_input_validation": True,
            "must_consume_part_e_visual_grammar_modules": True,
            "must_bind_visual_grammar_before_renderer_execution": True,
            "geometry_source_priority": [
                "part_e.module_geometry_blueprint",
                "d2.semantic_components",
                "d2.expanded_renderer_action_bindings",
            ],
            "no_empty_boxes": True,
            "public_release_blocked": True,
        },
        "adapter_scene_records": records,
        "traceability_summary": {
            "scene_count": len(records),
            "validated_scene_count": sum(
                1 for record in records if record["validation_status"] == "pass"
            ),
            "visual_grammar_module_count": len(grammar["visual_grammar_modules"]),
            "geometry_blueprint_count": len(grammar["module_geometry_blueprints"]),
            "adapter_blocking_issue_count": blocking_issue_count,
            "modules_used": sorted(
                {
                    record["visual_grammar_binding"]["module_id"]
                    for record in records
                }
            ),
            "sources_consumed": [
                "run2_73_scene_plan_expansion.json",
                "run2_73_renderer_input_validation.json",
                "run2_73_visual_grammar_modules.json",
            ],
        },
        "next_required_action": "renderer_execute_from_d2_d3_e_adapter_manifest",
    }


def main() -> None:
    write_json(OUTPUT, build_adapter_contracts())


if __name__ == "__main__":
    main()
