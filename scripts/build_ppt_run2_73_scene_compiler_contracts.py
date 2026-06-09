from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
OUTPUT = PACK / "run2_73_scene_compiler_contracts.json"

SCENE_REQUIRED_FIELDS = sorted(
    [
        "content_units",
        "proof_object",
        "visual_role",
        "layout_intent",
        "renderer_action_bindings",
        "off_canvas_routes",
    ]
)

ROLE_RULE_BINDINGS = {
    "cover": [
        "vh_01_primary_subject_first_read",
        "ws_01_create_outer_breathing_room",
        "kr_04_hold_visual_before_explanation",
        "mp_01_object_before_label",
    ],
    "setup": [
        "kr_01_one_idea_per_build",
        "ws_03_consolidate_labels",
        "vh_05_labels_follow_visuals",
        "mp_05_motion_follows_causal_or_reading_flow",
    ],
    "contrast": [
        "kr_03_before_after_contrast",
        "vh_02_remove_competing_frames",
        "ws_02_delete_redundant_boxes",
        "mp_03_stagger_dependencies",
    ],
    "proof": [
        "vh_01_primary_subject_first_read",
        "kr_01_one_idea_per_build",
        "ws_04_align_to_fewer_axes",
        "mp_01_object_before_label",
    ],
    "climax": [
        "vh_01_primary_subject_first_read",
        "ws_01_create_outer_breathing_room",
        "kr_04_hold_visual_before_explanation",
        "mp_04_pause_after_major_reveal",
    ],
    "close": [
        "kr_05_state_change_by_duplication",
        "ws_05_reduce_background_noise",
        "vh_03_z_order_guides_attention",
        "mp_05_motion_follows_causal_or_reading_flow",
    ],
}

ROLE_RHYTHM = {
    "cover": "Sparse first read: product path first, proof labels second.",
    "setup": "Step through source, memory, obligation, and proof without becoming a table.",
    "contrast": "Use a matched before-after contrast so the product delta is the scene.",
    "proof": "Build from claim to proof object to route marker with one idea per beat.",
    "climax": "Hold the strongest proof object before adding labels or secondary evidence.",
    "close": "Resolve to release-bound handoff without implying public readiness.",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_inputs() -> list[dict[str, Any]]:
    names = [
        "run2_73_tutorial_to_design_moves.json",
        "run2_74_product_claim_graph.json",
        "run2_74_slide_story.json",
        "run2_74_content_quality_audit.json",
    ]
    return [
        {
            "path": f"docs/product/ppt-run2-data-skill-quality/{name}",
            "available": (PACK / name).exists(),
            "use_in_this_artifact": (
                "Bind B2 executable design moves to C1/C2/C3 approved scene content."
            ),
        }
        for name in names
    ]


def information_containers(role: str, units: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "container_id": f"{role}_claim_container",
            "container_role": "claim_container",
            "contains": ["headline", "supporting_line", "main_claim"],
            "source": "approved_content_units.on_canvas_copy",
            "must_remain_on_canvas": True,
        },
        {
            "container_id": f"{role}_proof_container",
            "container_role": "proof_container",
            "contains": ["proof_object", "proof_labels"],
            "source": "approved_content_units.proof_object",
            "must_remain_on_canvas": True,
        },
        {
            "container_id": f"{role}_route_marker_container",
            "container_role": "route_marker_container",
            "contains": ["review_boundary", "note_viewer_marker"],
            "source": "approved_content_units.delete_or_note_route",
            "must_remain_on_canvas": "only_as_small_route_marker",
        },
    ]


def chrome(role: str) -> list[dict[str, Any]]:
    return [
        {
            "chrome_id": f"{role}_scene_frame",
            "chrome_role": "scene_frame",
            "purpose": "Orient the scene without competing with the proof object.",
            "must_not_carry_claim_text": True,
        },
        {
            "chrome_id": f"{role}_route_affordance",
            "chrome_role": "note_viewer_affordance",
            "purpose": "Signal off-canvas detail without exposing raw records on the slide.",
            "must_not_carry_claim_text": True,
        },
    ]


def renderer_binding(
    role: str,
    rules: list[dict[str, Any]],
) -> dict[str, Any]:
    action_ids = [
        action["action_id"] for rule in rules for action in rule["renderer_actions"]
    ]
    action_types = sorted(
        {action["action_type"] for rule in rules for action in rule["renderer_actions"]}
    )
    return {
        "binding_id": f"{role}_b2_scene_binding",
        "source_rule_ids": [rule["rule_id"] for rule in rules],
        "principles": sorted({rule["principle"] for rule in rules}),
        "design_moves": [rule["design_move"] for rule in rules],
        "renderer_action_types": action_types,
        "renderer_action_ids": action_ids,
        "applies_to_scene_questions": [
            "first_read",
            "main_visual",
            "information_containers",
            "chrome",
            "must_delete",
        ],
        "acceptance_checks": [
            {
                "rule_id": rule["rule_id"],
                "checks": rule["acceptance_checks"],
            }
            for rule in rules
        ],
    }


def scene_plan(
    slide: dict[str, Any],
    audit_record: dict[str, Any],
    rules_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    role = slide["role"]
    units = audit_record["approved_content_units"]
    rules = [rules_by_id[rule_id] for rule_id in ROLE_RULE_BINDINGS[role]]
    delete_route = units["delete_or_note_route"]

    return {
        "scene_id": f"scene_compiler_2_73_{role}",
        "slide_index": slide["slide_index"],
        "role": role,
        "source_slide_story_id": slide["slide_id"],
        "source_content_qa_id": audit_record["audit_id"],
        "content_units": units,
        "proof_object": {
            "primary": units["proof_object"],
            "evidence": slide["proof_object"]["evidence"],
            "business_logic": units["business_logic"],
            "why_this_proves_the_claim": slide["proof_object"][
                "why_this_proves_the_claim"
            ],
        },
        "visual_role": units["visual_role"],
        "layout_intent": {
            "first_read": units["on_canvas_copy"]["headline"],
            "main_visual": units["proof_object"],
            "information_containers": information_containers(role, units),
            "chrome": chrome(role),
            "must_delete": delete_route["must_delete_from_canvas"],
            "scene_question": slide["handoff_to_scene_compiler"][
                "required_scene_question"
            ],
            "rhythm_intent": ROLE_RHYTHM[role],
        },
        "renderer_action_bindings": [renderer_binding(role, rules)],
        "off_canvas_routes": delete_route,
        "renderer_execution_boundary": {
            "must_use_scene_plan": True,
            "must_not_read_content_from_c3_record_top_level": True,
            "must_not_draw_generic_boxes": True,
            "may_resolve_b2_action_parameters_later": True,
        },
    }


def build_contract() -> dict[str, Any]:
    design_moves = read_json(PACK / "run2_73_tutorial_to_design_moves.json")
    claim_graph = read_json(PACK / "run2_74_product_claim_graph.json")
    story = read_json(PACK / "run2_74_slide_story.json")
    audit = read_json(PACK / "run2_74_content_quality_audit.json")

    rules_by_id = {rule["rule_id"]: rule for rule in design_moves["tutorial_rule_mappings"]}
    audit_by_role = {record["role"]: record for record in audit["slide_quality_audits"]}
    scenes = [
        scene_plan(slide, audit_by_role[slide["role"]], rules_by_id)
        for slide in story["slides"]
    ]
    bound_rule_ids = sorted(
        {rule_id for role in ROLE_RULE_BINDINGS for rule_id in ROLE_RULE_BINDINGS[role]}
    )
    bound_action_types = sorted(
        {
            action_type
            for scene in scenes
            for binding in scene["renderer_action_bindings"]
            for action_type in binding["renderer_action_types"]
        }
    )

    return {
        "artifact_id": "run2_73_scene_compiler_contracts",
        "part": "Part D1",
        "schema_version": "1.0",
        "status": "run2_73_scene_compiler_contracts_public_blocked",
        "stage_policy": "part_d1_scene_compiler_contract_only",
        "selected_usecase_id": claim_graph["selected_usecase_id"],
        "source_design_moves": "run2_73_tutorial_to_design_moves.json",
        "source_product_claim_graph": "run2_74_product_claim_graph.json",
        "source_slide_story": "run2_74_slide_story.json",
        "source_content_quality_audit": "run2_74_content_quality_audit.json",
        "source_inputs": source_inputs(),
        "artifact_scope": {
            "starts": [
                "merge_b2_design_moves_with_c1_c2_c3_content_logic",
                "define_per_page_scene_plan_before_renderer",
            ],
            "does_not_start": [
                "renderer_rerun",
                "pptx_output",
                "html_viewer",
                "public_release",
            ],
        },
        "scene_structure_schema": {
            "required_scene_fields": SCENE_REQUIRED_FIELDS,
            "content_unit_source": "slide_quality_audits[*].approved_content_units",
            "layout_intent_must_answer": [
                "first_read",
                "main_visual",
                "information_containers",
                "chrome",
                "must_delete",
            ],
            "renderer_binding_source": "run2_73_tutorial_to_design_moves.json:tutorial_rule_mappings",
            "forbidden_direct_renderer_fields": [
                "layout_geometry",
                "pptx_output",
                "html_viewer",
                "slide_shapes",
                "shape_rectangles",
                "direct_shape_plan",
            ],
        },
        "renderer_execution_contract": {
            "must_execute_scene_plan_before_shape_generation": True,
            "must_not_directly_draw_placeholder_boxes": True,
            "must_resolve_content_from_approved_content_units": True,
            "must_route_delete_or_note_items_off_canvas": True,
        },
        "scene_plans": scenes,
        "traceability_summary": {
            "slide_count": len(story["slides"]),
            "scene_count": len(scenes),
            "approved_content_units_source": (
                "run2_74_content_quality_audit.json:"
                "slide_quality_audits[*].approved_content_units"
            ),
            "design_rule_ids_bound": bound_rule_ids,
            "renderer_action_type_count": len(bound_action_types),
            "renderer_action_types_bound": bound_action_types,
            "roles": [scene["role"] for scene in scenes],
        },
        "next_required_action": "part_d2_renderer_execute_scene_plan_not_direct_boxes",
    }


def main() -> None:
    write_json(OUTPUT, build_contract())


if __name__ == "__main__":
    main()
