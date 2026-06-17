from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
SOURCE_EXPANSION = PACK / "run2_73_scene_plan_expansion.json"
SOURCE_ADAPTER = PACK / "run2_73_renderer_adapter_contracts.json"
SOURCE_VISUAL_GRAMMAR = PACK / "run2_73_visual_grammar_modules.json"
SOURCE_SLIDE_STORY = PACK / "run2_74_slide_story.json"
SOURCE_CONTENT_AUDIT = PACK / "run2_74_content_quality_audit.json"
OUTPUT = PACK / "run2_73_text_binding_strategy.json"

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
FORBIDDEN_TEXT_PATTERNS = [
    "empty text box",
    "generic rectangle label",
    "duplicated headline/supporting copy",
    "text floating without bound visual object",
    "all slides using the same text layout",
]

ROLE_SOCKET_TARGETS = {
    "cover": {
        "layout_signature": "cover_product_edge_headline_with_orbital_proof_labels",
        "headline": "negative space pocket",
        "proof_a": "product edge",
        "proof_b": "evidence rail",
        "supporting": "field route",
        "callout_a": "product edge",
        "callout_b": "connector endpoint",
        "viewer": "connector endpoint",
    },
    "setup": {
        "layout_signature": "setup_source_field_route_with_condenser_labels",
        "headline": "field route",
        "proof_a": "evidence rail",
        "proof_b": "connector endpoint",
        "supporting": "field route",
        "callout_a": "connector endpoint",
        "callout_b": "negative space pocket",
        "viewer": "connector endpoint",
    },
    "contrast": {
        "layout_signature": "contrast_comparison_seam_with_opposed_label_rails",
        "headline": "comparison seam",
        "proof_a": "comparison seam",
        "proof_b": "evidence rail",
        "supporting": "negative space pocket",
        "callout_a": "comparison seam",
        "callout_b": "connector endpoint",
        "viewer": "connector endpoint",
    },
    "proof": {
        "layout_signature": "proof_evidence_rail_with_inspection_callouts",
        "headline": "evidence rail",
        "proof_a": "evidence rail",
        "proof_b": "connector endpoint",
        "supporting": "field route",
        "callout_a": "evidence rail",
        "callout_b": "connector endpoint",
        "viewer": "connector endpoint",
    },
    "climax": {
        "layout_signature": "climax_product_edge_headline_with_result_perimeter_labels",
        "headline": "product edge",
        "proof_a": "product edge",
        "proof_b": "evidence rail",
        "supporting": "negative space pocket",
        "callout_a": "product edge",
        "callout_b": "connector endpoint",
        "viewer": "connector endpoint",
    },
    "close": {
        "layout_signature": "close_decision_node_with_quiet_route_labels",
        "headline": "decision node",
        "proof_a": "decision node",
        "proof_b": "evidence rail",
        "supporting": "field route",
        "callout_a": "decision node",
        "callout_b": "connector endpoint",
        "viewer": "connector endpoint",
    },
}


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
            "use_in_this_artifact": "Provide D2 semantic components, visual containers, and expanded renderer binding IDs for text sockets.",
        },
        {
            "path": "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
            "available": SOURCE_ADAPTER.exists(),
            "use_in_this_artifact": "Provide E2 adapter scene IDs, visual grammar binding, and renderer adapter manifest IDs.",
        },
        {
            "path": "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
            "available": SOURCE_VISUAL_GRAMMAR.exists(),
            "use_in_this_artifact": "Provide Part E visual structure terms and non-card grammar modules.",
        },
        {
            "path": "docs/product/ppt-run2-data-skill-quality/run2_74_slide_story.json",
            "available": SOURCE_SLIDE_STORY.exists(),
            "use_in_this_artifact": "Provide on-canvas copy roles, text budgets, and speaker/viewer routing intent.",
        },
        {
            "path": "docs/product/ppt-run2-data-skill-quality/run2_74_content_quality_audit.json",
            "available": SOURCE_CONTENT_AUDIT.exists(),
            "use_in_this_artifact": "Provide content quality watch items and approved content unit boundaries.",
        },
    ]


def index_by_key(records: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        value = record.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{label} record missing string key {key}")
        if value in indexed:
            raise ValueError(f"{label} duplicate key: {value}")
        indexed[value] = record
    return indexed


def assert_role_alignment(*indexes: dict[str, dict[str, Any]]) -> list[str]:
    roles = list(indexes[0])
    expected = set(roles)
    for index in indexes[1:]:
        if set(index) != expected:
            raise ValueError("Part F source roles must align across D2, E2, story, audit, and Part E")
    if len(roles) != 6:
        raise ValueError("Part F requires exactly six page roles")
    return roles


def capacity(
    max_words: int,
    max_lines: int,
    hierarchy_level: str,
    min_scale: float,
    max_scale: float,
    overflow_behavior: str,
) -> dict[str, Any]:
    return {
        "max_words": max_words,
        "max_lines": max_lines,
        "hierarchy_level": hierarchy_level,
        "allowed_font_scale": {"min": min_scale, "max": max_scale},
        "overflow_behavior": overflow_behavior,
    }


def text_socket(
    *,
    socket_id: str,
    binding_role: str,
    bound_visual_object_type: str,
    bound_source_artifact: str,
    bound_source_id: str,
    bound_source_path: str,
    text_source: dict[str, Any],
    capacity_spec: dict[str, Any],
) -> dict[str, Any]:
    return {
        "socket_id": socket_id,
        "binding_role": binding_role,
        "bound_visual_object_type": bound_visual_object_type,
        "bound_source_artifact": bound_source_artifact,
        "bound_source_id": bound_source_id,
        "bound_source_path": bound_source_path,
        "text_source": text_source,
        "binding_rationale": (
            "Socket position inherits from a named visual object and source ID; "
            "it is not a free-floating text box."
        ),
        "capacity": capacity_spec,
    }


def semantic_component_id(scene: dict[str, Any], component_key: str) -> str:
    return scene["semantic_components"][component_key]["component_id"]


def visual_container_id(scene: dict[str, Any], container_id: str) -> str:
    ids = {
        container["container_id"]
        for container in scene["visual_containers"]
        if isinstance(container, dict) and isinstance(container.get("container_id"), str)
    }
    if container_id not in ids:
        raise ValueError(f"D2 visual container missing: {container_id}")
    return container_id


def build_page_record(
    role: str,
    scene: dict[str, Any],
    adapter: dict[str, Any],
    story: dict[str, Any],
    audit: dict[str, Any],
) -> dict[str, Any]:
    targets = ROLE_SOCKET_TARGETS[role]
    copy = story["on_canvas_copy"]
    text_budget = story["text_budget"]
    proof_labels = copy.get("proof_labels", [])
    adapter_scene_id = adapter["adapter_scene_id"]
    claim_container_id = visual_container_id(scene, f"{role}_claim_container_expanded")
    route_container_id = visual_container_id(scene, f"{role}_route_marker_container_expanded")

    headline_socket = text_socket(
        socket_id=f"{role}_headline_socket",
        binding_role="headline",
        bound_visual_object_type=targets["headline"],
        bound_source_artifact="run2_73_renderer_adapter_contracts",
        bound_source_id=adapter_scene_id,
        bound_source_path=f"adapter_scene_records.{role}.visual_grammar_binding.main_structure",
        text_source={
            "source_artifact": "run2_74_slide_story",
            "source_field": "on_canvas_copy.headline",
            "copy_preview": copy["headline"],
        },
        capacity_spec=capacity(9, 2, "h1", 0.82, 1.0, "truncate_with_route_to_viewer"),
    )
    supporting_copy_socket = text_socket(
        socket_id=f"{role}_supporting_copy_socket",
        binding_role="supporting_copy",
        bound_visual_object_type=targets["supporting"],
        bound_source_artifact="run2_73_scene_plan_expansion",
        bound_source_id=semantic_component_id(scene, "supporting_copy"),
        bound_source_path=f"scene_structures.{role}.semantic_components.supporting_copy",
        text_source={
            "source_artifact": "run2_74_slide_story",
            "source_field": "on_canvas_copy.supporting_line",
            "copy_preview": copy["supporting_line"],
        },
        capacity_spec=capacity(18, 3, "supporting_copy", 0.72, 0.9, "truncate_with_route_to_viewer"),
    )
    viewer_note_socket = text_socket(
        socket_id=f"{role}_viewer_note_socket",
        binding_role="viewer_note",
        bound_visual_object_type=targets["viewer"],
        bound_source_artifact="run2_73_scene_plan_expansion",
        bound_source_id=semantic_component_id(scene, "viewer_note_route"),
        bound_source_path=f"scene_structures.{role}.semantic_components.viewer_note_route",
        text_source={
            "source_artifact": "run2_74_slide_story",
            "source_field": "speaker_note_or_viewer_route.speaker_note",
            "copy_preview": story["speaker_note_or_viewer_route"]["speaker_note"],
        },
        capacity_spec=capacity(18, 3, "viewer_note", 0.62, 0.8, "route_to_speaker_note"),
    )
    proof_label_sockets = [
        text_socket(
            socket_id=f"{role}_proof_label_{index + 1}_socket",
            binding_role="proof_label",
            bound_visual_object_type=targets["proof_a" if index == 0 else "proof_b"],
            bound_source_artifact="run2_73_scene_plan_expansion",
            bound_source_id=semantic_component_id(scene, "proof_panel" if index == 0 else "evidence_marks"),
            bound_source_path=(
                f"scene_structures.{role}.semantic_components."
                f"{'proof_panel' if index == 0 else 'evidence_marks'}"
            ),
            text_source={
                "source_artifact": "run2_74_slide_story",
                "source_field": f"on_canvas_copy.proof_labels[{index}]",
                "copy_preview": label,
            },
            capacity_spec=capacity(5, 1, "proof_label", 0.62, 0.78, "route_to_html_viewer_metadata"),
        )
        for index, label in enumerate(proof_labels[:2])
    ]
    callout_sockets = [
        text_socket(
            socket_id=f"{role}_callout_claim_socket",
            binding_role="callout",
            bound_visual_object_type=targets["callout_a"],
            bound_source_artifact="run2_73_scene_plan_expansion",
            bound_source_id=claim_container_id,
            bound_source_path=f"scene_structures.{role}.visual_containers.claim_container_expanded",
            text_source={
                "source_artifact": "run2_74_content_quality_audit",
                "source_field": "scene_compiler_constraints[0]",
                "copy_preview": "claim anchor",
            },
            capacity_spec=capacity(7, 2, "callout", 0.58, 0.72, "route_to_html_viewer_metadata"),
        ),
        text_socket(
            socket_id=f"{role}_callout_route_socket",
            binding_role="callout",
            bound_visual_object_type=targets["callout_b"],
            bound_source_artifact="run2_73_scene_plan_expansion",
            bound_source_id=route_container_id,
            bound_source_path=f"scene_structures.{role}.visual_containers.route_marker_container_expanded",
            text_source={
                "source_artifact": "run2_74_slide_story",
                "source_field": "speaker_note_or_viewer_route.viewer_only",
                "copy_preview": "viewer route",
            },
            capacity_spec=capacity(7, 2, "callout", 0.58, 0.72, "route_to_html_viewer_metadata"),
        ),
    ]

    return {
        "text_binding_id": f"text_binding_2_73_{role}",
        "role": role,
        "slide_index": scene["slide_index"],
        "layout_signature": targets["layout_signature"],
        "source_expansion_id": scene["expansion_id"],
        "source_adapter_scene_id": adapter_scene_id,
        "source_visual_grammar_module": adapter["visual_grammar_binding"]["module_id"],
        "source_slide_story_id": story["slide_id"],
        "source_content_audit_id": audit["audit_id"],
        "text_socket_strategy": {
            "headline_socket": headline_socket,
            "proof_label_sockets": proof_label_sockets,
            "supporting_copy_socket": supporting_copy_socket,
            "callout_sockets": callout_sockets,
            "viewer_note_socket": viewer_note_socket,
        },
        "overflow_policy": {
            "max_canvas_words": min(text_budget["max_public_words"], 42),
            "max_proof_labels_on_canvas": min(text_budget["max_proof_labels"], 3),
            "route_excess_to": ["speaker_note", "html_viewer_metadata"],
            "never_create_empty_text_box": True,
            "if_socket_overflows": "shorten on-canvas copy first, then route full text to speaker note and HTML metadata.",
        },
        "text_routing": {
            "canvas_text": [
                "headline_socket",
                "supporting_copy_socket",
                "proof_label_sockets",
                "callout_sockets",
            ],
            "speaker_note_text": [
                "viewer_note_socket",
                "overflowed_supporting_copy",
                "full_speaker_note",
            ],
            "html_viewer_metadata": [
                "overflow_payload",
                "source_trace",
                "socket_capacity_report",
            ],
        },
        "forbidden_text_patterns": FORBIDDEN_TEXT_PATTERNS,
    }


def build_text_binding_strategy(
    expansion: dict[str, Any] | None = None,
    adapter: dict[str, Any] | None = None,
    grammar: dict[str, Any] | None = None,
    story: dict[str, Any] | None = None,
    audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    expansion = expansion or read_json(SOURCE_EXPANSION)
    adapter = adapter or read_json(SOURCE_ADAPTER)
    grammar = grammar or read_json(SOURCE_VISUAL_GRAMMAR)
    story = story or read_json(SOURCE_SLIDE_STORY)
    audit = audit or read_json(SOURCE_CONTENT_AUDIT)

    scene_by_role = index_by_key(expansion["scene_structures"], "role", "D2 scene")
    adapter_by_role = index_by_key(adapter["adapter_scene_records"], "role", "E2 adapter")
    story_by_role = index_by_key(story["slides"], "role", "Run 2.74 story")
    audit_by_role = index_by_key(audit["slide_quality_audits"], "role", "Run 2.74 audit")
    grammar_by_role = index_by_key(grammar["page_type_to_visual_grammar"], "page_type", "Part E page")
    roles = assert_role_alignment(scene_by_role, adapter_by_role, story_by_role, audit_by_role, grammar_by_role)

    records = [
        build_page_record(
            role,
            scene_by_role[role],
            adapter_by_role[role],
            story_by_role[role],
            audit_by_role[role],
        )
        for role in roles
    ]
    socket_count = sum(
        1
        + len(record["text_socket_strategy"]["proof_label_sockets"])
        + 1
        + len(record["text_socket_strategy"]["callout_sockets"])
        + 1
        for record in records
    )
    return {
        "artifact_id": "run2_73_text_binding_strategy",
        "part": "Part F",
        "schema_version": "ppt_run2_73_text_binding_strategy.v1",
        "status": "run2_73_text_binding_strategy_ready_public_blocked",
        "stage_policy": "part_f_text_binding_strategy_only_no_renderer_rerun_no_public_release",
        "source_scene_plan_expansion": "run2_73_scene_plan_expansion.json",
        "source_renderer_adapter_contracts": "run2_73_renderer_adapter_contracts.json",
        "source_visual_grammar_modules": "run2_73_visual_grammar_modules.json",
        "source_slide_story": "run2_74_slide_story.json",
        "source_content_quality_audit": "run2_74_content_quality_audit.json",
        "source_inputs": source_inputs(),
        "artifact_scope": {
            "starts": [
                "bind_copy_roles_to_visual_sockets",
                "define_capacity_and_overflow_routes_before_rendering",
            ],
            "does_not_start": FORBIDDEN_INVOCATIONS,
        },
        "execution_guard": {
            "mode": "text_binding_strategy_only",
            "rendering_subprocesses_allowed": False,
            "allowed_side_effects": [
                "read_run2_73_scene_plan_expansion_json",
                "read_run2_73_renderer_adapter_contracts_json",
                "read_run2_73_visual_grammar_modules_json",
                "read_run2_74_slide_story_json",
                "read_run2_74_content_quality_audit_json",
                "write_run2_73_text_binding_strategy_json",
            ],
            "forbidden_invocations": FORBIDDEN_INVOCATIONS,
            "forbidden_runtime_imports": sorted(FORBIDDEN_RUNTIME_IMPORTS),
            "forbidden_dynamic_import_calls": sorted(FORBIDDEN_DYNAMIC_IMPORT_CALLS),
        },
        "global_text_binding_contract": {
            "must_bind_text_to_visual_object": True,
            "must_define_socket_capacity_before_render": True,
            "must_route_overflow_off_canvas": True,
            "must_preserve_distinct_layout_signature_per_role": True,
        },
        "global_forbidden_text_patterns": FORBIDDEN_TEXT_PATTERNS,
        "page_text_binding_records": records,
        "traceability_summary": {
            "page_text_binding_count": len(records),
            "socket_count": socket_count,
            "layout_signature_count": len({record["layout_signature"] for record in records}),
            "sources_consumed": [
                "run2_73_scene_plan_expansion.json",
                "run2_73_renderer_adapter_contracts.json",
                "run2_73_visual_grammar_modules.json",
                "run2_74_slide_story.json",
                "run2_74_content_quality_audit.json",
            ],
        },
        "next_required_action": "part_g_renderer_rerun_from_validated_text_binding_strategy",
    }


def main() -> None:
    write_json(OUTPUT, build_text_binding_strategy())


if __name__ == "__main__":
    main()
