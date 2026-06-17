from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
DEFAULT_OUT_DIR = PACK
DEFAULT_RESULT_JSON = PACK / "results" / "run2_24_single_usecase_thickening_result.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_24_single_usecase_thickening_result.md"

SELECTED_USECASE_ID = "usecase_design_to_production_platform_launch"
NARRATIVE_USECASE_ID = "usecase_ai_design_to_production_platform_launch"
ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]


ROLE_PACKS: dict[str, dict[str, Any]] = {
    "cover": {
        "headline": "Design memory becomes a launch system.",
        "support_line": "The deck opens on one product promise: editable PPT output controlled by selected design knowledge.",
        "business_proof_points": [
            "The user is evaluating Vulca as a design-to-production presentation workflow, not a prompt-only slide generator.",
            "The first read must show a product-system promise before any trace detail appears.",
            "The launch story must avoid source-brand imitation while still feeling like a real commercial product reveal.",
        ],
        "visual_evidence_slots": [
            {
                "slot_id": "slot_2_24_cover_launch_field",
                "asset_type": "native_launch_field",
                "content_payload": "Large editable headline field plus one generated product-system motif.",
                "native_ppt_strategy": "Draw a launch-scale text field, one original motif, and a small source-boundary chip from native PPT text and shapes.",
            },
            {
                "slot_id": "slot_2_24_cover_case_badge",
                "asset_type": "case_context_badge",
                "content_payload": "AI design-to-production platform launch deck / public-demo candidate.",
                "native_ppt_strategy": "Use a compact editable badge that names the usecase without copied brand colors or logos.",
            },
        ],
    },
    "setup": {
        "headline": "Prompt-only decks lose the product thread.",
        "support_line": "The setup slide names the business failure: each one-off prompt forgets the case, source boundaries, and design rules.",
        "business_proof_points": [
            "The buyer needs repeatable launch-deck quality for public demos, customer briefings, and investor narratives.",
            "One-shot prompting cannot show which source records, memory, and gates shaped the output.",
            "The visual surface should show a thin prompt-only path collapsing before the selected product route appears.",
        ],
        "visual_evidence_slots": [
            {
                "slot_id": "slot_2_24_setup_prompt_loss",
                "asset_type": "before_state_strip",
                "content_payload": "Prompt-only request -> generic deck -> unreviewable output.",
                "native_ppt_strategy": "Draw a compressed before-state strip with editable labels and low visual priority.",
            },
            {
                "slot_id": "slot_2_24_setup_selected_route",
                "asset_type": "selected_route_map",
                "content_payload": "Usecase + source records + memory + gates -> native PPT code.",
                "native_ppt_strategy": "Draw a routed workflow map with one highlighted path and two supporting annotations.",
            },
        ],
    },
    "contrast": {
        "headline": "The same brief changes when evidence is selected first.",
        "support_line": "The contrast slide makes the product claim visible: prompt-only output versus source-bound design generation.",
        "business_proof_points": [
            "The selected usecase creates a concrete commercial decision instead of a generic AI capability claim.",
            "The deck must show what changed from prompt-only: more case specificity, visible product surface, and explicit release boundary.",
            "The visual comparison should be asymmetric: weak prompt output stays small while selected workflow output owns the frame.",
        ],
        "visual_evidence_slots": [
            {
                "slot_id": "slot_2_24_contrast_prompt_thumbnail",
                "asset_type": "weak_before_thumbnail",
                "content_payload": "Generic title + feature boxes + no trace.",
                "native_ppt_strategy": "Draw a small low-contrast thumbnail with editable labels, not a copied screenshot.",
            },
            {
                "slot_id": "slot_2_24_contrast_selected_thumbnail",
                "asset_type": "strong_after_thumbnail",
                "content_payload": "Selected usecase + memory-backed layout + visible QA gate.",
                "native_ppt_strategy": "Draw a larger native thumbnail with content labels, proof object, and source-boundary marker.",
            },
        ],
    },
    "proof": {
        "headline": "Content memory gives every slide a job.",
        "support_line": "The proof slide turns the six-slide arc into concrete content obligations before code writes the deck.",
        "business_proof_points": [
            "Each slide role receives a headline, support line, business proof points, and visual evidence slots.",
            "The product surface must show content memory and visual evidence as inspectable inputs, not hidden prompt text.",
            "The largest area should be an original native product surface that can later be opened and edited in PPT.",
        ],
        "visual_evidence_slots": [
            {
                "slot_id": "slot_2_24_proof_content_memory_surface",
                "asset_type": "content_memory_surface",
                "content_payload": "Role cards for cover, setup, contrast, proof, climax, close with content obligations.",
                "native_ppt_strategy": "Draw an original editable product surface with role rows, selected ids, and content density markers.",
            },
            {
                "slot_id": "slot_2_24_proof_visual_asset_rail",
                "asset_type": "visual_asset_rail",
                "content_payload": "Two visual evidence slots per slide role, with raw-media forbidden.",
                "native_ppt_strategy": "Draw a secondary rail of native chips linked to the surface; keep trace ids off public first read.",
            },
        ],
    },
    "climax": {
        "headline": "One generated proof object owns the room.",
        "support_line": "The climax slide should show a concrete editable result object, not another abstract selector diagram.",
        "business_proof_points": [
            "The viewer needs one large visible result that demonstrates the platform can structure a real launch deck.",
            "The hero object must carry business content, product surface, and QA boundary in one composition.",
            "The slide stays public-blocked until native render, source-boundary, and human visual review pass.",
        ],
        "visual_evidence_slots": [
            {
                "slot_id": "slot_2_24_climax_hero_result",
                "asset_type": "hero_result_object",
                "content_payload": "Editable generated PPT result object with usecase, memory, and QA gate signals.",
                "native_ppt_strategy": "Draw a large native proof object with layered editable text, shape hierarchy, and one release marker.",
            },
            {
                "slot_id": "slot_2_24_climax_density_annotation",
                "asset_type": "density_annotation_layer",
                "content_payload": "3 business facts, 2 visual evidence slots, 1 public-blocked gate.",
                "native_ppt_strategy": "Draw small annotation labels around the hero object; do not crowd the first-read field.",
            },
        ],
    },
    "close": {
        "headline": "The gate closes on an inspectable launch path.",
        "support_line": "The close slide turns the case into a next-run contract: consume the pack, rerun, review, then decide release.",
        "business_proof_points": [
            "The product is credible only if the generated deck can explain what data, memory, and visual evidence it used.",
            "The next generated rerun must prove this single-usecase pack changes visible slide content, not only trace fields.",
            "The public gate remains blocked until the deck passes native render and human release review.",
        ],
        "visual_evidence_slots": [
            {
                "slot_id": "slot_2_24_close_release_gate",
                "asset_type": "release_gate_panel",
                "content_payload": "Internal demo ok / public blocked / next rerun consumes Run 2.24 pack.",
                "native_ppt_strategy": "Draw an editable decision panel with three release states and a highlighted blocked gate.",
            },
            {
                "slot_id": "slot_2_24_close_trace_handoff",
                "asset_type": "trace_handoff_path",
                "content_payload": "Usecase -> content memory -> visual evidence -> workflow gates -> Run 2.25 generated rerun.",
                "native_ppt_strategy": "Draw a compact handoff route with native labels and no copied source visuals.",
            },
        ],
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def select_usecase() -> dict[str, Any]:
    bank = read_json(PACK / "commercial_usecase_bank.json")
    for usecase in bank["usecases"]:
        if usecase["id"] == SELECTED_USECASE_ID:
            return usecase
    raise ValueError(f"missing selected usecase {SELECTED_USECASE_ID}")


def build_content_memory(selected_usecase: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for index, role in enumerate(ROLES, start=1):
        pack = ROLE_PACKS[role]
        slots = pack["visual_evidence_slots"]
        records.append(
            {
                "content_memory_id": f"content_2_24_{role}",
                "role": role,
                "slide_index": index,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "headline": pack["headline"],
                "support_line": pack["support_line"],
                "business_proof_points": pack["business_proof_points"],
                "visual_evidence_slot_ids": [slot["slot_id"] for slot in slots],
                "content_density_contract": {
                    "min_business_proof_points": 2,
                    "min_visual_evidence_slots": 2,
                    "max_first_read_words": 18,
                    "body_copy_policy": "supporting_copy_must_be_short_and_editable",
                },
                "trace_fields_required": [
                    "run2_24_selected_usecase_id",
                    "run2_24_content_memory_id",
                    "run2_24_visual_evidence_slot_ids",
                    "run2_24_content_density_gate_id",
                ],
                "forbidden_source_materials": [
                    "screenshots",
                    "video frames",
                    "audio",
                    "full transcripts",
                    "copied layouts",
                    "brand marks",
                    "source prose",
                ],
                "public_surface_policy": "show_business_content_and_original_native_visuals_hide_trace_ids_from_first_read",
                "release_boundary": "public_blocked_until_run2_24_pack_is_consumed_by_generated_rerun_and_human_review_passes",
            }
        )

    return {
        "schema_version": "ppt_run2_single_usecase_content_memory.v1",
        "status": "run2_24_single_usecase_content_memory_ready_public_blocked",
        "run_id": "2.24",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase": {
            "id": selected_usecase["id"],
            "audience": selected_usecase["audience"],
            "business_decision": selected_usecase["business_decision"],
            "deck_mission": selected_usecase["deck_mission"],
            "source_ids": selected_usecase["source_ids"],
            "qa_probe": selected_usecase["qa_probe"],
        },
        "story_policy": {
            "single_primary_usecase": True,
            "supporting_references_only": True,
            "forbid_cross_case_primary_story": True,
            "reason": "Run 2.22 proved selector trace but mixed reference families across slide roles; Run 2.24 locks one commercial story before the next rerun.",
        },
        "derived_from": [
            "commercial_usecase_bank.json",
            "run2_7_commercial_usecase.json",
            "run2_7_multimodal_source_records.json",
            "results/run2_23_selector_effectiveness_audit.json",
        ],
        "slide_content_memory": records,
    }


def build_visual_assets() -> dict[str, Any]:
    assets: list[dict[str, Any]] = []
    for role in ROLES:
        for slot in ROLE_PACKS[role]["visual_evidence_slots"]:
            assets.append(
                {
                    "asset_id": slot["slot_id"].replace("slot_", "asset_"),
                    "slot_id": slot["slot_id"],
                    "role": role,
                    "selected_usecase_id": SELECTED_USECASE_ID,
                    "asset_type": slot["asset_type"],
                    "content_payload": slot["content_payload"],
                    "native_ppt_strategy": slot["native_ppt_strategy"],
                    "visual_density_role": "make_business_content_visible_without_using_raw_source_media",
                    "source_boundary": "Derived observations only; no copied screenshots, video frames, source layouts, brand marks, audio, or transcript text.",
                    "public_surface_allowed": True,
                    "qa_probe": "At contact-sheet scale, this asset should read as concrete product evidence rather than an abstract workflow symbol.",
                }
            )

    return {
        "schema_version": "ppt_run2_visual_evidence_asset_memory.v1",
        "status": "run2_24_visual_evidence_asset_memory_ready_public_blocked",
        "run_id": "2.24",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "storage_policy": {
            "raw_media": "forbidden",
            "screenshots": "forbidden",
            "video_frames": "forbidden",
            "copied_layouts": "forbidden",
            "brand_marks": "forbidden",
            "allowed_storage": "derived_visual_asset_instructions_only",
        },
        "visual_evidence_assets": assets,
    }


def build_workflow_gates() -> dict[str, Any]:
    gates: list[dict[str, Any]] = []
    for role in ROLES:
        gates.append(
            {
                "gate_id": f"gate_2_24_{role}_content_visual_density",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "required_content_memory_id": f"content_2_24_{role}",
                "min_business_proof_points": 2,
                "min_visual_evidence_slots": 2,
                "forbid_cross_case_primary_story": True,
                "required_trace_fields": [
                    "run2_24_selected_usecase_id",
                    "run2_24_content_memory_id",
                    "run2_24_visual_evidence_slot_ids",
                    "run2_24_content_density_gate_id",
                ],
                "pass_fail_checks": [
                    "The slide's primary story uses the selected design-to-production platform launch usecase.",
                    "At least two business proof points are visible or represented by native editable slide objects.",
                    "At least two visual evidence slots are generated as native PPT objects or documented public-blocked fallbacks.",
                    "Raw source screenshots, copied layouts, brand marks, audio, video frames, and transcript text are absent.",
                ],
                "bad_control_probe": "A bad control may receive the selected usecase label but fails if it lacks content memory, visual evidence assets, or density gates.",
                "public_release_gate": "blocked",
            }
        )
    return {
        "schema_version": "ppt_run2_content_visual_workflow_gates.v1",
        "status": "run2_24_content_visual_workflow_gates_ready_public_blocked",
        "run_id": "2.24",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "gates": gates,
    }


def build_result() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": "2.24",
        "status": "run2_24_single_usecase_content_visual_evidence_ready_public_blocked",
        "source_audit_run": "2.23",
        "selected_usecase_id": SELECTED_USECASE_ID,
        "narrative_usecase_id": NARRATIVE_USECASE_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "input_chain": {
            "commercial_usecase_bank": "docs/product/ppt-run2-data-skill-quality/commercial_usecase_bank.json",
            "narrative_usecase": "docs/product/ppt-run2-data-skill-quality/run2_7_commercial_usecase.json",
            "multimodal_source_records": "docs/product/ppt-run2-data-skill-quality/run2_7_multimodal_source_records.json",
            "selector_effectiveness_audit": "docs/product/ppt-run2-data-skill-quality/results/run2_23_selector_effectiveness_audit.json",
        },
        "output_chain": {
            "content_memory": "docs/product/ppt-run2-data-skill-quality/run2_24_single_usecase_content_memory.json",
            "visual_evidence_asset_memory": "docs/product/ppt-run2-data-skill-quality/run2_24_visual_evidence_asset_memory.json",
            "content_visual_workflow_gates": "docs/product/ppt-run2-data-skill-quality/run2_24_content_visual_workflow_gates.json",
        },
        "artifact_counts": {
            "slide_content_memory": 6,
            "visual_evidence_assets": 12,
            "content_visual_workflow_gates": 6,
        },
        "delivery_artifacts": {
            "pptx_paths": [],
            "rendered_slide_paths": [],
            "contact_sheet_paths": [],
            "html_motion_renderer_paths": [],
        },
        "public_release_gate": "blocked",
        "release_boundary": "public_blocked_until_next_generated_rerun_consumes_run2_24_pack_native_render_review_and_human_approval",
        "next_required_action": "consume_run2_24_single_usecase_pack_before_next_generated_rerun",
    }


def write_report(result: dict[str, Any], result_md: Path) -> None:
    lines = [
        "# Run 2.24 Single Usecase Content + Visual Evidence Thickening",
        "",
        "Status: single usecase content and visual evidence pack completed, public blocked.",
        "",
        "Run 2.24 is data/workflow-only. It creates no new PPT deck and does not advance to Run 3.0.",
        "",
        f"Selected usecase: `{result['selected_usecase_id']}`.",
        "",
        "## What Changed",
        "",
        "- The next rerun must use one primary commercial story instead of mixing different case families across slide roles.",
        "- `run2_24_single_usecase_content_memory.json` adds headline, support line, business proof points, and content density contracts for all six slide roles.",
        "- `run2_24_visual_evidence_asset_memory.json` adds twelve native-PPT visual evidence slots so the deck has visible product/content material, not only selector symbols.",
        "- `run2_24_content_visual_workflow_gates.json` requires the selected usecase id, content memory id, visual evidence slot ids, and density gate id before native PPT generation.",
        "",
        "## Gate",
        "",
        "- Creates new PPT deck: false.",
        "- Public ready: false.",
        "- Public release gate: blocked.",
        "",
        "Public release remains public blocked. Run 2.24 prepares thicker content and visual evidence for the next generated rerun; it does not prove visual quality by itself.",
        "",
        "Next: consume the Run 2.24 single-usecase pack before the next generated rerun. Do not advance to Run 3.0.",
        "",
    ]
    result_md.parent.mkdir(parents=True, exist_ok=True)
    result_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    args = parser.parse_args()

    selected_usecase = select_usecase()
    content_memory = build_content_memory(selected_usecase)
    visual_assets = build_visual_assets()
    workflow_gates = build_workflow_gates()
    result = build_result()

    write_json(args.out_dir / "run2_24_single_usecase_content_memory.json", content_memory)
    write_json(args.out_dir / "run2_24_visual_evidence_asset_memory.json", visual_assets)
    write_json(args.out_dir / "run2_24_content_visual_workflow_gates.json", workflow_gates)
    write_json(args.result_json, result)
    write_report(result, args.result_md)
    print(f"Run 2.24 single-usecase content/evidence pack: {args.result_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
