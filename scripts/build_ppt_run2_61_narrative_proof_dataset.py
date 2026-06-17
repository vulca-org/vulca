from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
RESULTS = PACK / "results"
PRESENTATIONS_DIR = ROOT / "outputs" / "019e7d9c-532a-70b3-8892-fa3ae42baef2" / "presentations"

RUN_ID = "2.61"
SOURCE_GENERATED_RUN_ID = "2.60"
SELECTED_USECASE_ID = "usecase_design_to_production_platform_launch"
NEXT_ACTION = "run2_62_generate_four_arm_ppt_consuming_run2_61_narrative_proof_dataset"
NEXT_OBLIGATION = "must_be_consumed_before_run2_62_four_arm_rerun"
NEXT_TRACE_FIELDS = [
    "run2_61_narrative_proof_id",
    "run2_61_visual_carrier_selector_id",
    "run2_61_text_socket_fusion_contract_id",
    "run2_61_public_proof_replacement_id",
    "run2_61_narrative_workflow_gate_id",
]

SOURCE_INPUTS = {
    "run2_8_tutorial_decomposition": "run2_8_tutorial_decomposition.json",
    "run2_12_thick_multimodal_evidence": "run2_12_thick_multimodal_evidence.json",
    "run2_18_multimodal_evidence_expansion": "run2_18_multimodal_evidence_expansion.json",
    "run2_15_layout_module_memory": "run2_15_layout_module_memory.json",
    "run2_51_shape_text_socket_memory": "run2_51_shape_text_socket_memory.json",
    "run2_57_slide_message_contracts": "run2_57_slide_message_contracts.json",
    "run2_59_content_composition_contracts": "run2_59_content_composition_contracts.json",
    "run2_59_content_to_layout_selector": "run2_59_content_to_layout_selector.json",
}

OUTPUT_FILES = {
    "narrative": "run2_61_narrative_proof_dataset.json",
    "selector": "run2_61_story_to_visual_carrier_selector.json",
    "fusion": "run2_61_text_socket_fusion_contracts.json",
    "source_policy": "run2_61_source_to_public_proof_policy.json",
    "workflow_gates": "run2_61_narrative_workflow_gates.json",
    "result_json": "run2_61_narrative_proof_dataset_result.json",
    "result_md": "run2_61_narrative_proof_dataset_result.md",
}

ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]

ROLE_SPECS: list[dict[str, Any]] = [
    {
        "role": "cover",
        "reader_question": "What does Vulca produce, and why is this not an image-generation demo?",
        "required_answer": (
            "Vulca turns a real commercial brief plus selected source data into a code-generated "
            "editable PPT deck with traceable proof."
        ),
        "business_action": "Position the product as an evidence-to-editable-PPT workflow.",
        "public_takeaway": "A real brief becomes editable PPT proof.",
        "primary_evidence_object": "input-to-output product surface",
        "secondary_evidence_objects": [
            "commercial brief card",
            "source pack object",
            "generated PPT preview",
        ],
        "product_mechanism": (
            "brief, source pack, memory, code, and PPT output are shown as one native product path"
        ),
        "business_consequence": (
            "buyers can judge a repeatable workflow instead of a one-off pretty slide"
        ),
        "before_state": "prompt-only deck with weak provenance",
        "after_state": "editable PPT generated from selected case data",
        "visual_carrier_type": "product_surface",
        "selected_layout_module_id": "module_2_15_editorial_cover_field",
        "selected_socket_memory_id": "shape_text_socket_2_51_cover",
        "public_proof_replacement_type": "source_pack_object",
        "tutorial_decomposition_id": "decomp_2_8_design_first_code_second_pipeline",
        "thick_evidence_id": "thick_2_12_figma_platform_launch_arc",
        "expanded_evidence_id": "thick_2_18_figma_launch_identity_system",
    },
    {
        "role": "setup",
        "reader_question": "How does raw tutorial and business material become design memory before drawing?",
        "required_answer": (
            "The system selects allowed source records, extracts design rules, creates capability "
            "memory, and resolves slide contracts before native drawing."
        ),
        "business_action": "Stage the data-to-memory compiler as the product's first operating step.",
        "public_takeaway": "Sources become design decisions before drawing.",
        "primary_evidence_object": "source-to-memory compiler stage",
        "secondary_evidence_objects": [
            "allowed source pack",
            "design rule extraction",
            "message contract",
        ],
        "product_mechanism": (
            "tutorial, case, and multimodal records are reduced into explicit memory and gate objects"
        ),
        "business_consequence": "the deck can explain why a visual decision was chosen",
        "before_state": "raw tutorials sit outside the product",
        "after_state": "source rules are compiled into selectable memory",
        "visual_carrier_type": "operating_loop",
        "selected_layout_module_id": "module_2_15_product_theater_stage",
        "selected_socket_memory_id": "shape_text_socket_2_51_setup",
        "public_proof_replacement_type": "native_editable_proxy",
        "tutorial_decomposition_id": "decomp_2_8_type_hierarchy_readability_stack",
        "thick_evidence_id": "thick_2_12_figma_design_to_code_surface",
        "expanded_evidence_id": "thick_2_18_figma_design_to_production_surface",
    },
    {
        "role": "contrast",
        "reader_question": "What mechanism separates Vulca from prompt-only or template-style decks?",
        "required_answer": (
            "Vulca binds usecase data, design memory, layout capacity, text sockets, and QA gates "
            "before generating editable PPT objects."
        ),
        "business_action": "Show the competitor path breaking at the missing compiler turn.",
        "public_takeaway": "The difference is mechanism, not taste.",
        "primary_evidence_object": "before-after route break",
        "secondary_evidence_objects": [
            "prompt-only output",
            "missing compiler turn",
            "Vulca editable PPT route",
        ],
        "product_mechanism": (
            "the prompt-only path lacks source memory, carrier selection, and socket-bound copy"
        ),
        "business_consequence": (
            "the buyer sees a system boundary rather than a subjective style comparison"
        ),
        "before_state": "generic deck from a prompt",
        "after_state": "source-bound generated PPT with visible decision route",
        "visual_carrier_type": "before_after_delta",
        "selected_layout_module_id": "module_2_15_before_after_route",
        "selected_socket_memory_id": "shape_text_socket_2_51_contrast",
        "public_proof_replacement_type": "before_after_route_break",
        "tutorial_decomposition_id": "decomp_2_8_makeover_split_text_into_visual_steps",
        "thick_evidence_id": "thick_2_12_present_partners_whitespace_hierarchy",
        "expanded_evidence_id": "thick_2_18_duarte_slide_design_method",
    },
    {
        "role": "proof",
        "reader_question": "How do we know the source data and workflow were actually used?",
        "required_answer": (
            "The output carries narrative proof ids, visual carrier ids, socket fusion ids, proof "
            "replacements, and workflow gate ids in trace."
        ),
        "business_action": "Expose a reviewable proof surface without dumping raw trace onto the public slide.",
        "public_takeaway": "Trace becomes inspectable product proof.",
        "primary_evidence_object": "inspection board with compact proof objects",
        "secondary_evidence_objects": [
            "narrative proof id",
            "socket fusion id",
            "public proof replacement",
        ],
        "product_mechanism": (
            "public proof objects point to trace-only records that remain inspectable in the viewer"
        ),
        "business_consequence": (
            "reviewers can audit the pipeline without turning the slide into a compliance report"
        ),
        "before_state": "raw trace text competes with the main message",
        "after_state": "public proof object links to detailed trace",
        "visual_carrier_type": "workspace_inspection",
        "selected_layout_module_id": "module_2_15_dense_evidence_compression",
        "selected_socket_memory_id": "shape_text_socket_2_51_proof",
        "public_proof_replacement_type": "inspection_board",
        "tutorial_decomposition_id": "decomp_2_8_source_brand_sanitized_case_evidence",
        "thick_evidence_id": "thick_2_12_figma_design_to_code_surface",
        "expanded_evidence_id": "thick_2_18_figma_design_to_production_surface",
    },
    {
        "role": "climax",
        "reader_question": "What is the strongest product moment the viewer should remember?",
        "required_answer": (
            "A source-bound product loop creates an editable PPT preview, with code generation, "
            "design memory, and QA evidence orbiting one result object."
        ),
        "business_action": "Make the generated PPT result object own the frame.",
        "public_takeaway": "One generated result owns the product moment.",
        "primary_evidence_object": "editable PPT preview hero object",
        "secondary_evidence_objects": [
            "design memory route",
            "code renderer tag",
            "QA gate tag",
        ],
        "product_mechanism": (
            "the source memory and code path converge into one editable native PPT preview"
        ),
        "business_consequence": "the product feels like an operating system for presentation generation",
        "before_state": "separate proof tags and disconnected diagrams",
        "after_state": "one generated result object with attached proof",
        "visual_carrier_type": "climax_result_object",
        "selected_layout_module_id": "module_2_15_metric_reveal_stage",
        "selected_socket_memory_id": "shape_text_socket_2_51_climax",
        "public_proof_replacement_type": "operating_loop_proxy",
        "tutorial_decomposition_id": "decomp_2_8_climax_object_scale_and_pause",
        "thick_evidence_id": "thick_2_12_stripe_product_keynote_metric_reframe",
        "expanded_evidence_id": "thick_2_18_google_cloud_ai_platform_climax",
    },
    {
        "role": "close",
        "reader_question": "What must happen before the product can claim public release quality?",
        "required_answer": (
            "Run 2.61 prepares the next proof layer; Run 2.62 must consume it, generate a new "
            "four-arm comparison, and pass visual, trace, source-boundary, and human review."
        ),
        "business_action": "Close with a release gate and the next concrete rerun.",
        "public_takeaway": "The next proof is generated, not claimed.",
        "primary_evidence_object": "release handoff gate",
        "secondary_evidence_objects": [
            "Run 2.61 data layer",
            "Run 2.62 rerun",
            "human review gate",
        ],
        "product_mechanism": (
            "the narrative proof dataset becomes a required consumer contract for the next PPT generator"
        ),
        "business_consequence": (
            "the demo stays credible by showing the remaining gate instead of overclaiming"
        ),
        "before_state": "public release claimed from a thin proof",
        "after_state": "next proof waits for generated comparison and review",
        "visual_carrier_type": "release_handoff",
        "selected_layout_module_id": "module_2_15_quiet_release_handoff",
        "selected_socket_memory_id": "shape_text_socket_2_51_close",
        "public_proof_replacement_type": "release_gate_proxy",
        "tutorial_decomposition_id": "decomp_2_8_source_brand_sanitized_case_evidence",
        "thick_evidence_id": "thick_2_12_slidecow_powerpoint_whitespace",
        "expanded_evidence_id": "thick_2_18_whitespace_powerpoint_method",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def role_spec(role: str) -> dict[str, Any]:
    for spec in ROLE_SPECS:
        if spec["role"] == role:
            return spec
    raise ValueError(f"missing role spec: {role}")


def role_record(records: list[dict[str, Any]], role: str, key: str) -> dict[str, Any]:
    for record in records:
        if record.get("role") == role:
            return record
    raise ValueError(f"missing {key} record for role {role}")


def key_record(records: list[dict[str, Any]], field: str, value: str, key: str) -> dict[str, Any]:
    for record in records:
        if record.get(field) == value:
            return record
    raise ValueError(f"missing {key} record with {field}={value}")


def unique_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def assert_no_run261_deck_artifacts() -> None:
    if not PRESENTATIONS_DIR.exists():
        return
    deck_paths = sorted(
        path
        for pattern in ("*2-61*.ppt", "*2-61*.pptx", "ppt-run2-61-*")
        for path in PRESENTATIONS_DIR.glob(pattern)
    )
    if deck_paths:
        names = ", ".join(path.name for path in deck_paths)
        raise ValueError(f"Run 2.61 is data/workflow-only and must not create PPT artifacts: {names}")


def load_sources() -> dict[str, dict[str, Any]]:
    sources: dict[str, dict[str, Any]] = {}
    for key, rel_path in SOURCE_INPUTS.items():
        source_path = PACK / rel_path
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        sources[key] = read_json(source_path)
    return sources


def validate_inputs(sources: dict[str, dict[str, Any]]) -> None:
    if sources["run2_8_tutorial_decomposition"].get("status") != (
        "run2_8_tutorial_decomposition_public_blocked"
    ):
        raise ValueError("Run 2.61 requires Run 2.8 tutorial decomposition")
    if sources["run2_12_thick_multimodal_evidence"].get("status") != (
        "run2_12_thick_multimodal_evidence_public_blocked"
    ):
        raise ValueError("Run 2.61 requires Run 2.12 thick multimodal evidence")
    if sources["run2_18_multimodal_evidence_expansion"].get("status") != (
        "run2_18_multimodal_evidence_expansion_ready"
    ):
        raise ValueError("Run 2.61 requires Run 2.18 multimodal evidence expansion")
    if sources["run2_15_layout_module_memory"].get("status") != "run2_15_layout_module_memory_ready":
        raise ValueError("Run 2.61 requires Run 2.15 layout module memory")
    if sources["run2_51_shape_text_socket_memory"].get("status") != (
        "run2_51_shape_text_socket_memory_ready_public_blocked"
    ):
        raise ValueError("Run 2.61 requires Run 2.51 shape text socket memory")
    if sources["run2_57_slide_message_contracts"].get("status") != (
        "run2_57_slide_message_contracts_ready_public_blocked"
    ):
        raise ValueError("Run 2.61 requires Run 2.57 slide message contracts")
    if sources["run2_59_content_composition_contracts"].get("status") != (
        "run2_59_content_composition_contracts_ready_public_blocked"
    ):
        raise ValueError("Run 2.61 requires Run 2.59 content composition contracts")
    if sources["run2_59_content_to_layout_selector"].get("status") != (
        "run2_59_content_to_layout_selector_ready_public_blocked"
    ):
        raise ValueError("Run 2.61 requires Run 2.59 content-to-layout selector")

    for source_key in (
        "run2_51_shape_text_socket_memory",
        "run2_57_slide_message_contracts",
    ):
        if sources[source_key].get("selected_usecase_id") != SELECTED_USECASE_ID:
            raise ValueError(f"Run 2.61 selected usecase mismatch in {source_key}")

    tutorial_ids = {unit["id"] for unit in sources["run2_8_tutorial_decomposition"]["units"]}
    thick_ids = {record["id"] for record in sources["run2_12_thick_multimodal_evidence"]["records"]}
    expanded_ids = {
        record["record_id"] for record in sources["run2_18_multimodal_evidence_expansion"]["records"]
    }
    module_ids = {module["module_id"] for module in sources["run2_15_layout_module_memory"]["modules"]}
    socket_ids = {
        record["socket_memory_id"]
        for record in sources["run2_51_shape_text_socket_memory"]["shape_text_socket_records"]
    }
    message_roles = {
        record["role"] for record in sources["run2_57_slide_message_contracts"]["slide_message_contracts"]
    }
    composition_roles = {
        record["role"]
        for record in sources["run2_59_content_composition_contracts"]["content_composition_contracts"]
    }
    selector_roles = {
        record["role"]
        for record in sources["run2_59_content_to_layout_selector"]["content_to_layout_selection_records"]
    }
    if message_roles != set(ROLES) or composition_roles != set(ROLES) or selector_roles != set(ROLES):
        raise ValueError("Run 2.61 requires complete Run 2.57/2.59 role coverage")

    for spec in ROLE_SPECS:
        role = spec["role"]
        if spec["tutorial_decomposition_id"] not in tutorial_ids:
            raise ValueError(f"{role} missing Run 2.8 tutorial decomposition source")
        if spec["thick_evidence_id"] not in thick_ids:
            raise ValueError(f"{role} missing Run 2.12 thick evidence source")
        if spec["expanded_evidence_id"] not in expanded_ids:
            raise ValueError(f"{role} missing Run 2.18 expanded evidence source")
        if spec["selected_layout_module_id"] not in module_ids:
            raise ValueError(f"{role} missing Run 2.15 layout module source")
        if spec["selected_socket_memory_id"] not in socket_ids:
            raise ValueError(f"{role} missing Run 2.51 socket memory source")


def source_refs(role: str, sources: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    spec = role_spec(role)
    layout_modules = sources["run2_15_layout_module_memory"]["modules"]
    socket_records = sources["run2_51_shape_text_socket_memory"]["shape_text_socket_records"]
    message_records = sources["run2_57_slide_message_contracts"]["slide_message_contracts"]
    composition_records = sources["run2_59_content_composition_contracts"][
        "content_composition_contracts"
    ]
    selector_records = sources["run2_59_content_to_layout_selector"][
        "content_to_layout_selection_records"
    ]
    module = key_record(layout_modules, "module_id", spec["selected_layout_module_id"], "Run 2.15 module")
    socket = key_record(
        socket_records,
        "socket_memory_id",
        spec["selected_socket_memory_id"],
        "Run 2.51 socket",
    )
    message = role_record(message_records, role, "Run 2.57 message contract")
    composition = role_record(composition_records, role, "Run 2.59 content composition contract")
    selector = role_record(selector_records, role, "Run 2.59 content-to-layout selector")
    return [
        {
            "source_type": "prior_run",
            "source_id": "run2_8_tutorial_decomposition",
            "source_record_id": spec["tutorial_decomposition_id"],
            "path": SOURCE_INPUTS["run2_8_tutorial_decomposition"],
            "role": role,
        },
        {
            "source_type": "prior_run",
            "source_id": "run2_12_thick_multimodal_evidence",
            "source_record_id": spec["thick_evidence_id"],
            "path": SOURCE_INPUTS["run2_12_thick_multimodal_evidence"],
            "role": role,
        },
        {
            "source_type": "prior_run",
            "source_id": "run2_18_multimodal_evidence_expansion",
            "source_record_id": spec["expanded_evidence_id"],
            "path": SOURCE_INPUTS["run2_18_multimodal_evidence_expansion"],
            "role": role,
        },
        {
            "source_type": "prior_run",
            "source_id": "run2_15_layout_module_memory",
            "source_record_id": module["module_id"],
            "path": SOURCE_INPUTS["run2_15_layout_module_memory"],
            "role": role,
        },
        {
            "source_type": "prior_run",
            "source_id": "run2_51_shape_text_socket_memory",
            "source_record_id": socket["socket_memory_id"],
            "path": SOURCE_INPUTS["run2_51_shape_text_socket_memory"],
            "role": role,
        },
        {
            "source_type": "prior_run",
            "source_id": "run2_57_slide_message_contracts",
            "source_record_id": message["contract_id"],
            "path": SOURCE_INPUTS["run2_57_slide_message_contracts"],
            "role": role,
        },
        {
            "source_type": "prior_run",
            "source_id": "run2_59_content_composition_contracts",
            "source_record_id": composition["content_contract_id"],
            "path": SOURCE_INPUTS["run2_59_content_composition_contracts"],
            "role": role,
        },
        {
            "source_type": "prior_run",
            "source_id": "run2_59_content_to_layout_selector",
            "source_record_id": selector["content_contract_id"],
            "path": SOURCE_INPUTS["run2_59_content_to_layout_selector"],
            "role": role,
        },
    ]


def copy_units(spec: dict[str, Any], message: dict[str, Any], composition: dict[str, Any]) -> dict[str, Any]:
    return {
        "headline": spec["public_takeaway"],
        "subhead": message["required_answer"],
        "proof_badges": unique_strings(
            composition["evidence_chips"] + [spec["secondary_evidence_objects"][0]]
        ),
        "annotations": [
            spec["product_mechanism"],
            spec["business_consequence"],
        ],
        "state_labels": [
            "before: " + spec["before_state"],
            "after: " + spec["after_state"],
        ],
        "speaker_note": composition["speaker_note"],
    }


def narrative_record(spec: dict[str, Any], sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    role = spec["role"]
    message = role_record(
        sources["run2_57_slide_message_contracts"]["slide_message_contracts"],
        role,
        "Run 2.57 message contract",
    )
    composition = role_record(
        sources["run2_59_content_composition_contracts"]["content_composition_contracts"],
        role,
        "Run 2.59 content composition contract",
    )
    return {
        "narrative_proof_id": f"narrative_proof_2_61_{role}",
        "role": role,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_generated_run_id": SOURCE_GENERATED_RUN_ID,
        "source_run_ids": ["2.8", "2.12", "2.18", "2.15", "2.51", "2.57", "2.59"],
        "reader_question": message["reader_question"],
        "required_answer": spec["required_answer"],
        "business_action": spec["business_action"],
        "public_takeaway": spec["public_takeaway"],
        "proof_payload": {
            "primary_evidence_object": spec["primary_evidence_object"],
            "secondary_evidence_objects": spec["secondary_evidence_objects"],
            "product_mechanism": spec["product_mechanism"],
            "business_consequence": spec["business_consequence"],
            "before_state": spec["before_state"],
            "after_state": spec["after_state"],
            "what_the_viewer_should_notice": (
                "the main visual object demonstrates the business action before small labels are read"
            ),
        },
        "copy_units": copy_units(spec, message, composition),
        "source_refs": source_refs(role, sources),
        "trace_only_payload": [
            "full source record inventory",
            "raw tutorial decomposition fields",
            "complete workflow gate details",
            "all prior-run trace ids",
        ],
        "public_proof_replacement": {
            "replacement_id": f"public_proof_replacement_2_61_{role}",
            "replacement_type": spec["public_proof_replacement_type"],
            "replacement_rule": (
                "render a native editable proxy that shows the product action without copying source "
                "visuals or leaking raw trace"
            ),
        },
        "density_budget": {
            "maximum_public_visible_words": 86,
            "minimum_public_proof_objects": 2,
            "maximum_trace_placeholders": 1,
            "minimum_visual_carrier_area_pct": 30,
            "maximum_free_floating_labels": 2,
            "minimum_socket_bound_copy_units": 4,
        },
        "forbidden_surface_terms": [
            "run2",
            "trace manifest",
            "workflow gate",
            "schema id",
            "raw source inventory",
        ],
        "bad_control_probe": f"fail_if_{role}_renders_claim_without_narrative_proof_and_socket_fusion",
        "next_rerun_obligation": NEXT_OBLIGATION,
    }


def build_narrative_dataset(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_narrative_proof_dataset.v1",
        "run_id": RUN_ID,
        "status": "run2_61_narrative_proof_dataset_ready_public_blocked",
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_generated_run_id": SOURCE_GENERATED_RUN_ID,
        "creates_new_ppt_deck": False,
        "latest_generated_run_id": SOURCE_GENERATED_RUN_ID,
        "source_inputs": SOURCE_INPUTS,
        "trace_fields_for_next_rerun": NEXT_TRACE_FIELDS,
        "narrative_proof_records": records,
        "next_required_action": NEXT_ACTION,
    }


def build_selector(records: list[dict[str, Any]]) -> dict[str, Any]:
    selector_records = []
    for record in records:
        spec = role_spec(record["role"])
        selector_records.append(
            {
                "selector_id": f"visual_carrier_selector_2_61_{record['role']}",
                "role": record["role"],
                "source_narrative_proof_id": record["narrative_proof_id"],
                "selected_layout_module_id": spec["selected_layout_module_id"],
                "selected_socket_memory_id": spec["selected_socket_memory_id"],
                "visual_carrier_type": spec["visual_carrier_type"],
                "carrier_reason": (
                    "selected by business action, proof payload, existing Run 2.15 layout capacity, "
                    "and Run 2.51 socket availability"
                ),
                "visual_weight_requirement": {
                    "minimum_primary_carrier_area_pct": 30,
                    "maximum_equal_card_clusters": 1,
                    "must_show_business_action": True,
                },
                "text_socket_requirement": (
                    "all public copy units must bind to Run 2.61 socket fusion contract"
                ),
                "fallback_if_over_capacity": (
                    "split proof payload to viewer and preserve the dominant visual carrier"
                ),
                "bad_control_probe": (
                    f"fail_if_{record['role']}_uses_generic_workflow_diagram_without_visual_carrier_selector"
                ),
            }
        )
    return {
        "schema_version": "ppt_run2_story_to_visual_carrier_selector.v1",
        "run_id": RUN_ID,
        "status": "run2_61_story_to_visual_carrier_selector_ready_public_blocked",
        "story_to_visual_carrier_records": selector_records,
        "next_required_action": NEXT_ACTION,
    }


def socket_binding(role: str, copy_unit_key: str, shape_role: str, budget: int) -> dict[str, Any]:
    max_lines_by_key = {
        "headline": 2,
        "subhead": 3,
        "proof_badges": 3,
        "annotations": 4,
        "state_labels": 2,
        "speaker_note": 4,
    }
    min_font_by_key = {
        "headline": 24,
        "subhead": 13,
        "proof_badges": 10,
        "annotations": 9,
        "state_labels": 9,
        "speaker_note": 8,
    }
    return {
        "copy_unit_key": copy_unit_key,
        "socket_id": f"socket_2_61_{role}_{copy_unit_key}",
        "owning_shape_role": shape_role,
        "character_budget": budget,
        "max_lines": max_lines_by_key[copy_unit_key],
        "minimum_font_size": min_font_by_key[copy_unit_key],
        "placement_rule": f"bind {copy_unit_key} to the {shape_role} and reject detached labels",
        "failure_status": f"fail_missing_{copy_unit_key}_socket",
    }


def build_fusion(records: list[dict[str, Any]], selectors: list[dict[str, Any]]) -> dict[str, Any]:
    selector_by_role = {selector["role"]: selector for selector in selectors}
    fusion_records = []
    for record in records:
        role = record["role"]
        fusion_records.append(
            {
                "fusion_contract_id": f"text_socket_fusion_2_61_{role}",
                "role": role,
                "source_narrative_proof_id": record["narrative_proof_id"],
                "source_visual_carrier_selector_id": selector_by_role[role]["selector_id"],
                "source_socket_memory_id": selector_by_role[role]["selected_socket_memory_id"],
                "source_copy_units": record["copy_units"],
                "socket_bindings": [
                    socket_binding(role, "headline", "primary_carrier", 64),
                    socket_binding(role, "subhead", "support_surface", 160),
                    socket_binding(role, "proof_badges", "proof_object", 120),
                    socket_binding(role, "annotations", "annotation_callout", 180),
                    socket_binding(role, "state_labels", "state_marker", 96),
                    socket_binding(role, "speaker_note", "speaker_note_channel", 220),
                ],
                "fit_rules": {
                    "reject_if_any_required_copy_unit_is_unbound": True,
                    "reject_if_public_words_exceed_budget": True,
                    "reject_if_more_than_two_free_floating_labels": True,
                },
                "overflow_behavior": "move raw detail to viewer and preserve public proof replacement",
                "surface_terms_policy": (
                    "public copy must avoid run ids, raw trace names, schema ids, and source brand names"
                ),
                "trace_fields_for_next_rerun": NEXT_TRACE_FIELDS,
            }
        )
    return {
        "schema_version": "ppt_run2_text_socket_fusion_contracts.v1",
        "run_id": RUN_ID,
        "status": "run2_61_text_socket_fusion_contracts_ready_public_blocked",
        "trace_fields_for_next_rerun": NEXT_TRACE_FIELDS,
        "text_socket_fusion_contracts": fusion_records,
        "next_required_action": NEXT_ACTION,
    }


def build_source_policy() -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_source_to_public_proof_policy.v1",
        "run_id": RUN_ID,
        "status": "run2_61_source_to_public_proof_policy_ready_public_blocked",
        "policy_id": "run2_61_source_to_public_proof_policy",
        "allowed_source_abstraction_types": [
            "native_editable_proxy",
            "native_editable_proxy_object",
            "source_pack_object",
            "inspection_board",
            "before_after_route_break",
            "operating_loop_proxy",
            "release_gate_proxy",
        ],
        "forbidden_source_copying_behaviors": [
            "copy_source_slide_or_video_frame",
            "copy_source_brand_visual_system",
            "copy_source_transcript_prose",
            "store_copyrighted_frame_as_reusable_asset",
        ],
        "public_replacement_rules": [
            "replace raw source inventory with a compact source pack object",
            "replace full workflow gate list with one pass/fail inspection board",
            "replace raw competitor prose with one before-after route break",
            "replace real screenshots with native editable proxy objects",
        ],
        "trace_only_retention_rules": [
            "keep raw source ids in trace manifests and viewer diagnostics",
            "keep workflow gate details outside public slide text",
            "keep source URLs in attribution fields",
        ],
        "next_required_action": NEXT_ACTION,
    }


def build_gates(
    records: list[dict[str, Any]],
    selectors: list[dict[str, Any]],
    fusions: list[dict[str, Any]],
) -> dict[str, Any]:
    selector_by_role = {selector["role"]: selector for selector in selectors}
    fusion_by_role = {fusion["role"]: fusion for fusion in fusions}
    gate_records = []
    for record in records:
        role = record["role"]
        gate_records.append(
            {
                "gate_id": f"gate_2_61_{role}_narrative_proof_fusion",
                "role": role,
                "source_narrative_proof_id": record["narrative_proof_id"],
                "source_visual_carrier_selector_id": selector_by_role[role]["selector_id"],
                "source_text_socket_fusion_contract_id": fusion_by_role[role]["fusion_contract_id"],
                "source_public_proof_replacement_id": record["public_proof_replacement"][
                    "replacement_id"
                ],
                "required_checks": [
                    "reader_question_answered",
                    "business_action_present",
                    "proof_payload_specific",
                    "visual_carrier_selected",
                    "required_copy_units_socket_bound",
                    "public_proof_replacement_present",
                    "bad_control_probe_defined",
                ],
                "next_run_required_trace_fields": NEXT_TRACE_FIELDS,
                "next_generated_run_contract": {
                    "run_id": "2.62",
                    "required_trace_fields": NEXT_TRACE_FIELDS,
                    "bad_control_arm": "bad_run2_60_without_run2_61_narrative_proof_dataset",
                    "full_arm_pass_status": (
                        "run2_61_narrative_proof_dataset_consumed_before_native_ppt_drawing"
                    ),
                },
                "bad_control_probe": record["bad_control_probe"],
            }
        )
    return {
        "schema_version": "ppt_run2_narrative_workflow_gates.v1",
        "run_id": RUN_ID,
        "status": "run2_61_narrative_workflow_gates_ready_public_blocked",
        "narrative_workflow_gates": gate_records,
        "next_generated_run_contract": {
            "run_id": "2.62",
            "required_trace_fields": NEXT_TRACE_FIELDS,
            "bad_control_arm": "bad_run2_60_without_run2_61_narrative_proof_dataset",
            "full_arm_pass_status": (
                "run2_61_narrative_proof_dataset_consumed_before_native_ppt_drawing"
            ),
        },
        "next_required_action": NEXT_ACTION,
    }


def build_result(
    out_dir: Path,
    records: list[dict[str, Any]],
    selector: dict[str, Any],
    fusion: dict[str, Any],
    source_policy: dict[str, Any],
    gates: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_narrative_proof_dataset_result.v1",
        "run_id": RUN_ID,
        "status": "run2_61_narrative_proof_dataset_ready_public_blocked",
        "source_generated_run_id": SOURCE_GENERATED_RUN_ID,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "input_chain": SOURCE_INPUTS,
        "output_chain": {
            "narrative_proof_dataset": rel(out_dir / OUTPUT_FILES["narrative"]),
            "story_to_visual_carrier_selector": rel(out_dir / OUTPUT_FILES["selector"]),
            "text_socket_fusion_contracts": rel(out_dir / OUTPUT_FILES["fusion"]),
            "source_to_public_proof_policy": rel(out_dir / OUTPUT_FILES["source_policy"]),
            "narrative_workflow_gates": rel(out_dir / OUTPUT_FILES["workflow_gates"]),
        },
        "generation_boundary": {
            "creates_new_ppt_deck": False,
            "latest_generated_run_id": SOURCE_GENERATED_RUN_ID,
            "public_ready": False,
        },
        "quality_delta": {
            "target_layer": "narrative_proof_dataset_and_socket_fusion",
            "fixes_failure_mode": (
                "run2_60_compressed_summary_layer_loses_source_text_visual_thickness"
            ),
            "roles_with_narrative_proof_records": len(records),
            "roles_with_visual_carrier_selection": len(
                selector["story_to_visual_carrier_records"]
            ),
            "roles_with_socket_fusion_contracts": len(fusion["text_socket_fusion_contracts"]),
            "roles_with_public_proof_replacement": len(records),
            "source_policy_count": 1 if source_policy["policy_id"] else 0,
            "roles_with_workflow_gates": len(gates["narrative_workflow_gates"]),
        },
        "next_required_action": NEXT_ACTION,
    }


def build_result_markdown(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Run 2.61 Narrative Proof Dataset",
            "",
            "Run 2.61 is a data/workflow repair layer. It does not generate a new PPT deck.",
            "",
            (
                "It fixes the Run 2.60 failure where the renderer consumed compressed claims but "
                "lost source, tutorial, text socket, and visual carrier thickness."
            ),
            "",
            "## Outputs",
            "",
            "- `run2_61_narrative_proof_dataset.json`: per-role reader question, answer, business action, proof payload, copy units, and public proof replacement.",
            "- `run2_61_story_to_visual_carrier_selector.json`: per-role visual carrier choices bound to Run 2.15 layout modules and Run 2.51 socket memory.",
            "- `run2_61_text_socket_fusion_contracts.json`: text socket fusion contracts for headline, subhead, proof badges, annotations, state labels, and speaker notes.",
            "- `run2_61_source_to_public_proof_policy.json`: source-to-public-proof abstraction rules and forbidden copying behaviors.",
            "- `run2_61_narrative_workflow_gates.json`: workflow gates that require Run 2.62 trace fields before native drawing.",
            "",
            "## Required Next Action",
            "",
            f"`{result['next_required_action']}`",
            "",
            "Do not advance to Run 3.0.",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Run 2.61 narrative proof dataset artifacts.")
    parser.add_argument("--out-dir", type=Path, default=PACK)
    parser.add_argument("--result-json", type=Path, default=RESULTS / OUTPUT_FILES["result_json"])
    parser.add_argument("--result-md", type=Path, default=RESULTS / OUTPUT_FILES["result_md"])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sources = load_sources()
    validate_inputs(sources)
    assert_no_run261_deck_artifacts()

    records = [narrative_record(spec, sources) for spec in ROLE_SPECS]
    narrative = build_narrative_dataset(records)
    selector = build_selector(records)
    fusion = build_fusion(records, selector["story_to_visual_carrier_records"])
    source_policy = build_source_policy()
    gates = build_gates(
        records,
        selector["story_to_visual_carrier_records"],
        fusion["text_socket_fusion_contracts"],
    )
    result = build_result(args.out_dir, records, selector, fusion, source_policy, gates)
    result_md = build_result_markdown(result)

    write_json(args.out_dir / OUTPUT_FILES["narrative"], narrative)
    write_json(args.out_dir / OUTPUT_FILES["selector"], selector)
    write_json(args.out_dir / OUTPUT_FILES["fusion"], fusion)
    write_json(args.out_dir / OUTPUT_FILES["source_policy"], source_policy)
    write_json(args.out_dir / OUTPUT_FILES["workflow_gates"], gates)
    write_json(args.result_json, result)
    write_text(args.result_md, result_md)
    assert_no_run261_deck_artifacts()
    print(json.dumps({"status": result["status"], "result_json": str(args.result_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
