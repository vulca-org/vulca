from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
SOURCE = PACK / "run2_73_scene_plan_expansion.json"
OUTPUT = PACK / "run2_73_renderer_input_validation.json"

REQUIRED_COMPONENTS = {
    "hero_object",
    "proof_panel",
    "supporting_copy",
    "evidence_marks",
    "viewer_note_route",
}
ALLOWED_ELEMENT_TYPES = {"shape", "text", "connector", "image", "svg"}
FORBIDDEN_RENDERER_FIELD_KEYS = {
    "layout_geometry",
    "pptx_output",
    "html_viewer",
    "slide_shapes",
    "shape_rectangles",
    "direct_shape_plan",
    "x",
    "y",
    "w",
    "h",
    "width",
    "height",
    "left",
    "top",
    "x_pct",
    "y_pct",
    "width_pct",
    "height_pct",
}
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
REQUIRED_CHECK_IDS = [
    "required_components_present",
    "allowed_element_types_only",
    "components_bound_to_content_or_semantic_role",
    "visual_containers_bound_to_components",
    "visual_containers_not_empty",
    "expanded_bindings_target_components",
    "expanded_bindings_have_actions",
    "forbidden_renderer_fields_absent",
    "off_canvas_terms_not_on_canvas",
    "renderer_scope_not_started",
]
ON_CANVAS_COMPONENTS = {
    "hero_object",
    "proof_panel",
    "supporting_copy",
    "evidence_marks",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_inputs() -> list[dict[str, Any]]:
    return [
        {
            "path": "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
            "available": SOURCE.exists(),
            "use_in_this_artifact": "Validate D2 renderer-ready JSON before any renderer rerun.",
        }
    ]


def has_bound_value(binding: dict[str, Any]) -> bool:
    return bool(binding.get("value"))


def add_issue(
    issues: list[dict[str, Any]],
    *,
    issue_id: str,
    role: str,
    location: str,
    message: str,
) -> None:
    issues.append(
        {
            "issue_id": issue_id,
            "severity": "blocking",
            "role": role,
            "location": location,
            "message": message,
        }
    )


def nested_forbidden_key_hits(value: Any, path: str = "$") -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_RENDERER_FIELD_KEYS:
                hits.append((key, child_path))
            hits.extend(nested_forbidden_key_hits(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(nested_forbidden_key_hits(child, f"{path}[{index}]"))
    return hits


def lower_text_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.lower()]
    if isinstance(value, dict):
        values: list[str] = []
        for child in value.values():
            values.extend(lower_text_values(child))
        return values
    if isinstance(value, list):
        values = []
        for child in value:
            values.extend(lower_text_values(child))
        return values
    return []


def off_canvas_terms(structure: dict[str, Any]) -> list[str]:
    contract = structure.get("off_canvas_contract", {})
    terms = []
    for key in ("viewer_only", "must_delete_from_canvas"):
        values = contract.get(key, [])
        if isinstance(values, list):
            terms.extend(str(value).lower() for value in values)
    return [term for term in terms if term]


def check_result(
    check_id: str,
    issues_before: int,
    issues_after: int,
    evidence: str,
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "status": "pass" if issues_before == issues_after else "fail",
        "evidence": evidence,
    }


def validate_scene(structure: dict[str, Any]) -> dict[str, Any]:
    role = structure["role"]
    issues: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    components = structure.get("semantic_components", {})
    component_ids = {
        component.get("component_id")
        for component in components.values()
        if isinstance(component, dict)
    }

    before = len(issues)
    missing_components = REQUIRED_COMPONENTS - set(components)
    for component_key in sorted(missing_components):
        add_issue(
            issues,
            issue_id="missing_required_component",
            role=role,
            location=f"semantic_components.{component_key}",
            message="Required renderer input component is missing.",
        )
    checks.append(
        check_result(
            "required_components_present",
            before,
            len(issues),
            f"checked {len(components)} semantic components",
        )
    )

    before = len(issues)
    for component_key, component in components.items():
        element_type = component.get("element_type")
        if element_type not in ALLOWED_ELEMENT_TYPES:
            add_issue(
                issues,
                issue_id="invalid_element_type",
                role=role,
                location=f"semantic_components.{component_key}.element_type",
                message=f"Element type {element_type!r} is not allowed.",
            )
        target_type = component.get("renderer_target", {}).get("target_element_type")
        if target_type != element_type:
            add_issue(
                issues,
                issue_id="renderer_target_type_mismatch",
                role=role,
                location=f"semantic_components.{component_key}.renderer_target.target_element_type",
                message="Renderer target element type must match component element type.",
            )
    checks.append(
        check_result(
            "allowed_element_types_only",
            before,
            len(issues),
            f"allowed types: {sorted(ALLOWED_ELEMENT_TYPES)}",
        )
    )

    before = len(issues)
    for component_key, component in components.items():
        if not (
            has_bound_value(component.get("content_binding", {}))
            or has_bound_value(component.get("semantic_role_binding", {}))
        ):
            add_issue(
                issues,
                issue_id="unbound_semantic_component",
                role=role,
                location=f"semantic_components.{component_key}",
                message="Component must bind content or semantic role before renderer handoff.",
            )
    checks.append(
        check_result(
            "components_bound_to_content_or_semantic_role",
            before,
            len(issues),
            "checked component content_binding and semantic_role_binding",
        )
    )

    before = len(issues)
    for index, container in enumerate(structure.get("visual_containers", [])):
        bound_component_id = container.get("bound_component_id")
        if bound_component_id not in component_ids:
            add_issue(
                issues,
                issue_id="visual_container_unknown_component",
                role=role,
                location=f"visual_containers[{index}].bound_component_id",
                message="Visual container must bind a known semantic component.",
            )
    checks.append(
        check_result(
            "visual_containers_bound_to_components",
            before,
            len(issues),
            f"checked {len(structure.get('visual_containers', []))} visual containers",
        )
    )

    before = len(issues)
    for index, container in enumerate(structure.get("visual_containers", [])):
        if container.get("empty_box_policy") != "forbidden":
            add_issue(
                issues,
                issue_id="empty_box_policy_not_forbidden",
                role=role,
                location=f"visual_containers[{index}].empty_box_policy",
                message="Visual containers must forbid empty boxes.",
            )
        if not (
            has_bound_value(container.get("content_binding", {}))
            or has_bound_value(container.get("semantic_role_binding", {}))
        ):
            add_issue(
                issues,
                issue_id="unbound_visual_container",
                role=role,
                location=f"visual_containers[{index}]",
                message="Visual container must bind content or semantic role.",
            )
    checks.append(
        check_result(
            "visual_containers_not_empty",
            before,
            len(issues),
            "checked empty_box_policy plus content/semantic bindings",
        )
    )

    before = len(issues)
    for index, binding in enumerate(structure.get("expanded_renderer_action_bindings", [])):
        target_id = binding.get("target_component_id")
        target_key = binding.get("target_component_key")
        if target_id not in component_ids or target_key not in components:
            add_issue(
                issues,
                issue_id="expanded_binding_unknown_component",
                role=role,
                location=f"expanded_renderer_action_bindings[{index}]",
                message="Expanded binding must target an existing component key and id.",
            )
    checks.append(
        check_result(
            "expanded_bindings_target_components",
            before,
            len(issues),
            f"checked {len(structure.get('expanded_renderer_action_bindings', []))} bindings",
        )
    )

    before = len(issues)
    for index, binding in enumerate(structure.get("expanded_renderer_action_bindings", [])):
        if not binding.get("source_b2_action_ids"):
            add_issue(
                issues,
                issue_id="expanded_binding_missing_actions",
                role=role,
                location=f"expanded_renderer_action_bindings[{index}].source_b2_action_ids",
                message="Expanded binding must carry at least one B2 renderer action id.",
            )
    checks.append(
        check_result(
            "expanded_bindings_have_actions",
            before,
            len(issues),
            "checked source_b2_action_ids",
        )
    )

    before = len(issues)
    for key, location in nested_forbidden_key_hits(structure):
        add_issue(
            issues,
            issue_id="forbidden_renderer_field",
            role=role,
            location=location,
            message=f"Renderer-only field {key!r} is forbidden in D3 input.",
        )
    checks.append(
        check_result(
            "forbidden_renderer_fields_absent",
            before,
            len(issues),
            f"forbidden keys: {sorted(FORBIDDEN_RENDERER_FIELD_KEYS)}",
        )
    )

    before = len(issues)
    terms = off_canvas_terms(structure)
    for component_key in ON_CANVAS_COMPONENTS & set(components):
        text = "\n".join(
            lower_text_values(components[component_key].get("content_binding", {}).get("value"))
        )
        for term in terms:
            if term in text:
                add_issue(
                    issues,
                    issue_id="off_canvas_term_on_canvas",
                    role=role,
                    location=f"semantic_components.{component_key}.content_binding.value",
                    message=f"Off-canvas term {term!r} appears in an on-canvas component.",
                )
    checks.append(
        check_result(
            "off_canvas_terms_not_on_canvas",
            before,
            len(issues),
            "checked viewer_only and must_delete terms against on-canvas components",
        )
    )

    before = len(issues)
    if structure.get("renderer_ready_boundary", {}).get("must_not_render_ppt") is not True:
        add_issue(
            issues,
            issue_id="renderer_scope_started",
            role=role,
            location="renderer_ready_boundary.must_not_render_ppt",
            message="D3 input must preserve the no-render boundary.",
        )
    checks.append(
        check_result(
            "renderer_scope_not_started",
            before,
            len(issues),
            "checked renderer_ready_boundary.must_not_render_ppt",
        )
    )

    return {
        "validation_id": f"renderer_input_validation_2_73_{role}",
        "role": role,
        "source_expansion_id": structure["expansion_id"],
        "status": "pass" if not issues else "fail",
        "blocking_issues": issues,
        "checked_components": len(components),
        "checked_visual_containers": len(structure.get("visual_containers", [])),
        "checked_bindings": len(structure.get("expanded_renderer_action_bindings", [])),
        "validation_checks": checks,
        "renderer_handoff": {
            "can_handoff_to_renderer": not issues,
            "must_not_render_in_d3": True,
            "component_manifest_count": len(components),
            "visual_container_count": len(structure.get("visual_containers", [])),
            "action_binding_count": len(structure.get("expanded_renderer_action_bindings", [])),
            "handoff_payload_source": "run2_73_scene_plan_expansion.json",
        },
    }


def validate_renderer_input(expansion: dict[str, Any]) -> dict[str, Any]:
    scene_results = [
        validate_scene(structure)
        for structure in expansion["scene_structures"]
    ]
    blocking_issues = [
        issue
        for record in scene_results
        for issue in record["blocking_issues"]
    ]
    component_count = sum(record["checked_components"] for record in scene_results)
    visual_container_count = sum(record["checked_visual_containers"] for record in scene_results)
    binding_count = sum(record["checked_bindings"] for record in scene_results)
    return {
        "status": "pass" if not blocking_issues else "fail",
        "scene_validation_results": scene_results,
        "blocking_issues": blocking_issues,
        "traceability_summary": {
            "scene_count": len(scene_results),
            "component_count": component_count,
            "visual_container_count": visual_container_count,
            "expanded_renderer_binding_count": binding_count,
            "blocking_issue_count": len(blocking_issues),
        },
    }


def build_validation_artifact() -> dict[str, Any]:
    expansion = read_json(SOURCE)
    validation = validate_renderer_input(expansion)
    summary = validation["traceability_summary"]
    return {
        "artifact_id": "run2_73_renderer_input_validation",
        "part": "Part D3",
        "schema_version": "1.0",
        "status": (
            "run2_73_renderer_input_validation_passed_public_blocked"
            if validation["status"] == "pass"
            else "run2_73_renderer_input_validation_failed_public_blocked"
        ),
        "stage_policy": "part_d3_renderer_input_validation_only",
        "source_scene_plan_expansion": "run2_73_scene_plan_expansion.json",
        "source_inputs": source_inputs(),
        "artifact_scope": {
            "starts": [
                "validate_d2_renderer_ready_json",
                "block_bad_scene_inputs_before_renderer",
            ],
            "does_not_start": [
                "renderer_rerun",
                "pptx_output",
                "html_viewer",
                "public_release",
            ],
        },
        "execution_guard": {
            "mode": "validation_only",
            "rendering_subprocesses_allowed": False,
            "allowed_side_effects": [
                "read_run2_73_scene_plan_expansion_json",
                "write_run2_73_renderer_input_validation_json",
            ],
            "forbidden_invocations": [
                "renderer_rerun",
                "pptx_output",
                "html_viewer",
                "public_release",
            ],
            "forbidden_runtime_imports": sorted(FORBIDDEN_RUNTIME_IMPORTS),
            "forbidden_dynamic_import_calls": sorted(FORBIDDEN_DYNAMIC_IMPORT_CALLS),
        },
        "validation_policy": {
            "required_check_ids": REQUIRED_CHECK_IDS,
            "allowed_element_types": sorted(ALLOWED_ELEMENT_TYPES),
            "forbidden_renderer_field_keys": sorted(FORBIDDEN_RENDERER_FIELD_KEYS),
            "off_canvas_term_sources": [
                "scene_structures[*].off_canvas_contract.viewer_only",
                "scene_structures[*].off_canvas_contract.must_delete_from_canvas",
            ],
            "failure_behavior": "block_renderer_handoff",
        },
        "scene_validation_results": validation["scene_validation_results"],
        "blocking_issues": validation["blocking_issues"],
        "renderer_handoff_contract": {
            "input_status": (
                "validated_renderer_ready_json"
                if validation["status"] == "pass"
                else "blocked_renderer_input"
            ),
            "input_contract_scope": "strictly_d2_renderer_ready_json_not_ppt_or_html_schema",
            "can_handoff_to_renderer": validation["status"] == "pass",
            "must_not_render_in_d3": True,
            "must_consume_source_artifact": "run2_73_scene_plan_expansion.json",
            "renderer_must_validate_again_before_ppt": True,
        },
        "traceability_summary": {
            **summary,
            "source_scene_plan_expansion": "run2_73_scene_plan_expansion.json",
            "renderer_handoff_approved": (
                "validated_renderer_ready_json_only"
                if validation["status"] == "pass"
                else "blocked_due_to_validation_issues"
            ),
        },
        "next_required_action": "part_e_renderer_rerun_from_validated_scene_plan",
    }


def main() -> None:
    write_json(OUTPUT, build_validation_artifact())


if __name__ == "__main__":
    main()
