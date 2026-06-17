from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
OUTPUT = PACK / "run2_73_scene_plan_expansion.json"

REQUIRED_COMPONENTS = [
    "hero_object",
    "proof_panel",
    "supporting_copy",
    "evidence_marks",
    "viewer_note_route",
]
ALLOWED_ELEMENT_TYPES = ["shape", "text", "connector", "image", "svg"]
HERO_ELEMENT_TYPE_BY_ROLE = {
    "cover": "svg",
    "setup": "connector",
    "contrast": "shape",
    "proof": "svg",
    "climax": "svg",
    "close": "shape",
}
COMPONENT_ACTION_TYPES = {
    "hero_object": {
        "select_element",
        "set_geometry",
        "set_style",
        "reorder_element",
        "crop_media",
        "add_animation",
    },
    "proof_panel": {
        "set_geometry",
        "align_elements",
        "distribute_spacing",
        "group_elements",
        "create_comparison_layout",
        "set_style",
    },
    "supporting_copy": {
        "hide_element",
        "add_reveal_step",
        "set_timing",
        "set_style",
        "add_animation",
    },
    "evidence_marks": {
        "add_reveal_step",
        "set_timing",
        "align_elements",
        "distribute_spacing",
        "group_elements",
        "add_animation",
        "create_comparison_layout",
    },
    "viewer_note_route": {
        "remove_element",
        "hide_element",
        "set_style",
        "set_transition",
        "duplicate_slide",
        "reorder_element",
        "set_timing",
    },
}
COMPONENT_LAYOUT_INTENT = {
    "hero_object": "main_visual",
    "proof_panel": "information_containers",
    "supporting_copy": "first_read",
    "evidence_marks": "information_containers",
    "viewer_note_route": "off_canvas_routes",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_inputs() -> list[dict[str, Any]]:
    names = [
        "run2_73_scene_compiler_contracts.json",
        "run2_73_tutorial_to_design_moves.json",
    ]
    return [
        {
            "path": f"docs/product/ppt-run2-data-skill-quality/{name}",
            "available": (PACK / name).exists(),
            "use_in_this_artifact": (
                "Expand D1 scene plans into renderer-ready semantic components."
            ),
        }
        for name in names
    ]


def action_index(design_moves: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        action["action_id"]: action
        for rule in design_moves["tutorial_rule_mappings"]
        for action in rule["renderer_actions"]
    }


def content_binding(source: str, value: Any) -> dict[str, Any]:
    return {
        "source": source,
        "value": value,
    }


def semantic_binding(source: str, value: Any) -> dict[str, Any]:
    return {
        "source": source,
        "value": value,
    }


def renderer_target(component_id: str, element_type: str, semantic_role: str) -> dict[str, Any]:
    return {
        "target_component_id": component_id,
        "target_element_type": element_type,
        "target_semantic_role": semantic_role,
    }


def semantic_components(scene: dict[str, Any]) -> dict[str, dict[str, Any]]:
    role = scene["role"]
    units = scene["content_units"]
    copy = units["on_canvas_copy"]
    routes = scene["off_canvas_routes"]

    specs = {
        "hero_object": {
            "element_type": HERO_ELEMENT_TYPE_BY_ROLE[role],
            "value": scene["proof_object"]["primary"],
            "source": "scene_plan.proof_object.primary",
            "semantic_value": scene["visual_role"],
            "semantic_source": "scene_plan.visual_role",
            "source_fields": ["proof_object.primary", "visual_role", "layout_intent.main_visual"],
        },
        "proof_panel": {
            "element_type": "shape",
            "value": scene["proof_object"],
            "source": "scene_plan.proof_object",
            "semantic_value": "proof_panel",
            "semantic_source": "scene_plan.layout_intent.information_containers",
            "source_fields": ["proof_object", "layout_intent.information_containers"],
        },
        "supporting_copy": {
            "element_type": "text",
            "value": copy,
            "source": "scene_plan.content_units.on_canvas_copy",
            "semantic_value": "supporting_copy",
            "semantic_source": "scene_plan.content_units.on_canvas_copy",
            "source_fields": ["content_units.on_canvas_copy", "layout_intent.first_read"],
        },
        "evidence_marks": {
            "element_type": "connector",
            "value": copy["proof_labels"],
            "source": "scene_plan.content_units.on_canvas_copy.proof_labels",
            "semantic_value": "evidence_marks",
            "semantic_source": "scene_plan.proof_object.evidence",
            "source_fields": ["content_units.on_canvas_copy.proof_labels", "proof_object.evidence"],
        },
        "viewer_note_route": {
            "element_type": "text",
            "value": routes,
            "source": "scene_plan.off_canvas_routes",
            "semantic_value": "viewer_note_route",
            "semantic_source": "scene_plan.off_canvas_routes",
            "source_fields": ["off_canvas_routes", "layout_intent.must_delete"],
        },
    }

    return {
        key: {
            "component_id": f"{role}_{key}",
            "component_role": key,
            "element_type": spec["element_type"],
            "content_binding": content_binding(spec["source"], spec["value"]),
            "semantic_role_binding": semantic_binding(
                spec["semantic_source"],
                spec["semantic_value"],
            ),
            "renderer_target": renderer_target(
                f"{role}_{key}",
                spec["element_type"],
                str(spec["semantic_value"]),
            ),
            "empty_box_policy": "forbidden",
            "source_scene_plan_fields": spec["source_fields"],
        }
        for key, spec in specs.items()
    }


def visual_containers(
    scene: dict[str, Any],
    components: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    role = scene["role"]
    containers: list[dict[str, Any]] = []
    for key, component in components.items():
        containers.append(
            {
                "container_id": f"{role}_{key}_container",
                "container_type": "component_container",
                "bound_component_id": component["component_id"],
                "content_binding": component["content_binding"],
                "semantic_role_binding": component["semantic_role_binding"],
                "empty_box_policy": "forbidden",
            }
        )

    info_component_by_role = {
        "claim_container": "supporting_copy",
        "proof_container": "proof_panel",
        "route_marker_container": "viewer_note_route",
    }
    for source_container in scene["layout_intent"]["information_containers"]:
        component_key = info_component_by_role[source_container["container_role"]]
        component = components[component_key]
        containers.append(
            {
                "container_id": f"{role}_{source_container['container_role']}_expanded",
                "container_type": "information_container",
                "bound_component_id": component["component_id"],
                "source_d1_container_id": source_container["container_id"],
                "content_binding": component["content_binding"],
                "semantic_role_binding": component["semantic_role_binding"],
                "empty_box_policy": "forbidden",
            }
        )

    for source_chrome in scene["layout_intent"]["chrome"]:
        component_key = (
            "viewer_note_route"
            if source_chrome["chrome_role"] == "note_viewer_affordance"
            else "hero_object"
        )
        component = components[component_key]
        containers.append(
            {
                "container_id": f"{role}_{source_chrome['chrome_role']}_expanded",
                "container_type": "chrome",
                "bound_component_id": component["component_id"],
                "source_d1_chrome_id": source_chrome["chrome_id"],
                "content_binding": component["content_binding"],
                "semantic_role_binding": semantic_binding(
                    "scene_plan.layout_intent.chrome",
                    source_chrome["chrome_role"],
                ),
                "empty_box_policy": "forbidden",
            }
        )

    return containers


def selected_actions(
    component_key: str,
    available_actions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    preferred_types = COMPONENT_ACTION_TYPES[component_key]
    actions = [
        action
        for action in available_actions
        if action["action_type"] in preferred_types
    ]
    return actions or available_actions[:1]


def expanded_bindings(
    scene: dict[str, Any],
    components: dict[str, dict[str, Any]],
    actions_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    source_binding = scene["renderer_action_bindings"][0]
    available_actions = [
        actions_by_id[action_id]
        for action_id in source_binding["renderer_action_ids"]
    ]
    bindings: list[dict[str, Any]] = []
    for component_key in REQUIRED_COMPONENTS:
        component = components[component_key]
        actions = selected_actions(component_key, available_actions)
        bindings.append(
            {
                "binding_id": f"{scene['role']}_{component_key}_expanded_binding",
                "target_component_key": component_key,
                "target_component_id": component["component_id"],
                "component_element_type": component["element_type"],
                "source_d1_binding_id": source_binding["binding_id"],
                "source_b2_rule_ids": source_binding["source_rule_ids"],
                "source_b2_action_ids": [action["action_id"] for action in actions],
                "source_b2_action_types": sorted(
                    {action["action_type"] for action in actions}
                ),
                "design_moves": source_binding["design_moves"],
                "layout_intent_binding": COMPONENT_LAYOUT_INTENT[component_key],
                "renderer_resolution_policy": {
                    "geometry_resolution": "defer_to_renderer",
                    "must_not_create_empty_box": True,
                    "must_bind_to_component_before_action": True,
                },
            }
        )

    covered_ids = {
        action_id
        for binding in bindings
        for action_id in binding["source_b2_action_ids"]
    }
    uncovered = [
        action
        for action in available_actions
        if action["action_id"] not in covered_ids
    ]
    if uncovered:
        hero_binding = bindings[0]
        hero_binding["source_b2_action_ids"].extend(
            action["action_id"] for action in uncovered
        )
        hero_binding["source_b2_action_types"] = sorted(
            {
                actions_by_id[action_id]["action_type"]
                for action_id in hero_binding["source_b2_action_ids"]
            }
        )

    return bindings


def scene_structure(
    scene: dict[str, Any],
    actions_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    components = semantic_components(scene)
    return {
        "expansion_id": f"scene_expansion_2_73_{scene['role']}",
        "source_scene_id": scene["scene_id"],
        "slide_index": scene["slide_index"],
        "role": scene["role"],
        "semantic_components": components,
        "visual_containers": visual_containers(scene, components),
        "expanded_renderer_action_bindings": expanded_bindings(
            scene,
            components,
            actions_by_id,
        ),
        "off_canvas_contract": scene["off_canvas_routes"],
        "renderer_ready_boundary": {
            "is_renderer_ready_json": True,
            "must_not_render_ppt": True,
            "must_validate_before_d3": True,
            "geometry_resolution_deferred": True,
        },
    }


def has_bound_value(binding: dict[str, Any]) -> bool:
    return bool(binding.get("value"))


def validate_expansion(payload: dict[str, Any]) -> None:
    for structure in payload["scene_structures"]:
        components = structure["semantic_components"]
        if set(components) != set(REQUIRED_COMPONENTS):
            raise ValueError(f"{structure['role']} missing required components")

        component_ids = {
            component["component_id"]
            for component in components.values()
        }
        for component in components.values():
            if component["element_type"] not in ALLOWED_ELEMENT_TYPES:
                raise ValueError(f"{component['component_id']} has invalid element type")
            if component["empty_box_policy"] != "forbidden":
                raise ValueError(f"{component['component_id']} allows empty boxes")
            if not (
                has_bound_value(component["content_binding"])
                or has_bound_value(component["semantic_role_binding"])
            ):
                raise ValueError(f"{component['component_id']} is unbound")

        for container in structure["visual_containers"]:
            if container["bound_component_id"] not in component_ids:
                raise ValueError(f"{container['container_id']} binds unknown component")
            if container["empty_box_policy"] != "forbidden":
                raise ValueError(f"{container['container_id']} allows empty boxes")
            if not (
                has_bound_value(container["content_binding"])
                or has_bound_value(container["semantic_role_binding"])
            ):
                raise ValueError(f"{container['container_id']} is unbound")

        action_ids = {
            action_id
            for binding in structure["expanded_renderer_action_bindings"]
            for action_id in binding["source_b2_action_ids"]
        }
        if not action_ids:
            raise ValueError(f"{structure['role']} has no expanded renderer actions")


def build_expansion() -> dict[str, Any]:
    scene_contract = read_json(PACK / "run2_73_scene_compiler_contracts.json")
    design_moves = read_json(PACK / "run2_73_tutorial_to_design_moves.json")
    actions_by_id = action_index(design_moves)
    structures = [
        scene_structure(scene, actions_by_id)
        for scene in scene_contract["scene_plans"]
    ]
    component_count = sum(
        len(structure["semantic_components"])
        for structure in structures
    )
    element_types_used = sorted(
        {
            component["element_type"]
            for structure in structures
            for component in structure["semantic_components"].values()
        }
    )
    expanded_binding_count = sum(
        len(structure["expanded_renderer_action_bindings"])
        for structure in structures
    )

    payload = {
        "artifact_id": "run2_73_scene_plan_expansion",
        "part": "Part D2",
        "schema_version": "1.0",
        "status": "run2_73_scene_plan_expansion_public_blocked",
        "stage_policy": "part_d2_scene_plan_expansion_only",
        "source_scene_compiler_contracts": "run2_73_scene_compiler_contracts.json",
        "source_design_moves": "run2_73_tutorial_to_design_moves.json",
        "source_inputs": source_inputs(),
        "artifact_scope": {
            "starts": [
                "expand_d1_contract_into_renderer_ready_scene_structure",
                "bind_visual_containers_to_content_or_semantic_roles",
            ],
            "does_not_start": [
                "part_d3_renderer_input_validation",
                "renderer_rerun",
                "pptx_output",
                "html_viewer",
                "public_release",
            ],
        },
        "component_schema": {
            "required_components": sorted(REQUIRED_COMPONENTS),
            "allowed_element_types": ALLOWED_ELEMENT_TYPES,
            "component_keys_are_semantic_not_geometry": True,
            "image_policy": "allowed_only_for_non_source_renderer_assets_after_d3_validation",
        },
        "renderer_ready_contract": {
            "no_empty_boxes": True,
            "every_visual_container_bound": True,
            "geometry_resolution_deferred": True,
            "must_preserve_d1_off_canvas_routes": True,
        },
        "scene_structures": structures,
        "traceability_summary": {
            "scene_count": len(structures),
            "component_count": component_count,
            "expanded_renderer_binding_count": expanded_binding_count,
            "source_scene_compiler_contracts": "run2_73_scene_compiler_contracts.json",
            "element_types_used": element_types_used,
            "empty_visual_container_count": 0,
        },
        "next_required_action": "part_d3_renderer_input_validation",
    }
    validate_expansion(payload)
    return payload


def main() -> None:
    write_json(OUTPUT, build_expansion())


if __name__ == "__main__":
    main()
