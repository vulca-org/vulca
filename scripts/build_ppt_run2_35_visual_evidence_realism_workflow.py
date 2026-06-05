from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
DEFAULT_OUT_DIR = PACK
DEFAULT_RESULT_JSON = PACK / "results" / "run2_35_visual_evidence_realism_workflow_result.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_35_visual_evidence_realism_workflow_result.md"

SELECTED_USECASE_ID = "usecase_design_to_production_platform_launch"
SOURCE_AUDIT_TARGET = "usecase_specific_visual_evidence_asset_realism_and_editorial_composition"
ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]


ROLE_REALISM: dict[str, dict[str, Any]] = {
    "cover": {
        "anchor": "launch-system product stage with one visible generated deck object",
        "hero_target": 0.42,
        "question": "Can a viewer understand the product promise before reading the trace?",
        "states": [
            "Generated launch deck canvas with selected memory chips attached to one visible output object.",
            "Public-demo readiness badge showing internal demo ok and public blocked in the same first-read field.",
        ],
        "captions": [
            "Design memory is not a note; it is the control layer before code draws the deck.",
            "The launch object stays original and source-boundary safe while still looking like a product reveal.",
        ],
        "strategy": "Draw a large editable product-stage object with one output deck slab, two memory chips, and one release badge; avoid a row of small abstract cards.",
    },
    "setup": {
        "anchor": "prompt-only failure path collapsing into a selected product route",
        "hero_target": 0.38,
        "question": "Can the buyer see why prompt-only output is commercially weaker?",
        "states": [
            "Three-step prompt-only path losing source boundary, product state, and review gate.",
            "Selected product route where usecase, memory, and QA gate converge before generation.",
        ],
        "captions": [
            "Prompt-only produces an unreviewable slide surface with no durable case memory.",
            "Selected evidence creates a route that can be inspected, repeated, and blocked before release.",
        ],
        "strategy": "Compress the prompt-only path to a weak left rail and make the selected route the dominant anchor with directional flow and concrete labels.",
    },
    "contrast": {
        "anchor": "before/after product-route comparison with asymmetric weight",
        "hero_target": 0.40,
        "question": "Can the same brief visibly become more specific after evidence selection?",
        "states": [
            "Before thumbnail: generic title, generic feature boxes, no audit trail.",
            "After thumbnail: selected usecase, memory-backed slide surface, and public-blocked gate.",
        ],
        "captions": [
            "The weak before state stays small because it has no decision path.",
            "The after state owns the frame because the workflow can explain what changed.",
        ],
        "strategy": "Use a small pale before thumbnail and a larger product-like after thumbnail with clear state labels and one visible gate.",
    },
    "proof": {
        "anchor": "product proof surface showing content memory as an inspectable object",
        "hero_target": 0.46,
        "question": "Can the proof slide look like a real product surface rather than a schema diagram?",
        "states": [
            "Six-role content memory surface with selected headline, proof point, and visual asset status per row.",
            "Visual asset rail that explains which public-safe object each slide must render next.",
        ],
        "captions": [
            "Every slide role gets a job before code generation starts.",
            "Visual evidence assets become inspectable product obligations, not hidden prompt fragments.",
        ],
        "strategy": "Draw an editable product-console surface with rows, status dots, and a single selected row emphasis instead of disconnected rectangles.",
    },
    "climax": {
        "anchor": "large generated result object with product state and release boundary in one stage",
        "hero_target": 0.68,
        "question": "Can one result object prove the product's value at thumbnail scale?",
        "states": [
            "Generated PPT result stage with output deck, selected memory, and QA boundary fused into one object.",
            "Human-review strip showing why the result is powerful internally but still public blocked.",
        ],
        "captions": [
            "The result object must be large enough to carry the room, not another selector diagram.",
            "The public gate stays visible so the demo does not overclaim release readiness.",
        ],
        "strategy": "Keep the hero result object dominant, add one concrete output-state label, and push all secondary evidence into a quiet rail.",
    },
    "close": {
        "anchor": "inspectable launch path handoff with next-run contract",
        "hero_target": 0.36,
        "question": "Can the close feel like a product handoff rather than a bureaucratic checklist?",
        "states": [
            "Launch path: usecase -> visual evidence realism -> editorial composition -> Run 2.36 rerun.",
            "Release gate with internal demo ok, native review pending, human release blocked.",
        ],
        "captions": [
            "The next action is not more prompting; it is consuming a stricter data/workflow contract.",
            "The release path is inspectable because every future visual claim must preserve provenance.",
        ],
        "strategy": "Make one launch-path object the main read, with three release states as supporting markers rather than the whole slide.",
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def selected_usecase() -> dict[str, Any]:
    bank = read_json(PACK / "commercial_usecase_bank.json")
    for usecase in bank["usecases"]:
        if usecase["id"] == SELECTED_USECASE_ID:
            return usecase
    raise ValueError(f"missing selected usecase {SELECTED_USECASE_ID}")


def source_ids_for_usecase(usecase: dict[str, Any]) -> list[str]:
    return list(usecase.get("source_ids") or [])


def build_realism_memory(usecase: dict[str, Any]) -> dict[str, Any]:
    audit = read_json(PACK / "results" / "run2_34_main_surface_visual_evidence_audit.json")
    visual_assets = read_json(PACK / "run2_24_visual_evidence_asset_memory.json")
    content_memory = read_json(PACK / "run2_24_single_usecase_content_memory.json")
    source_ids = source_ids_for_usecase(usecase)
    content_by_role = {record["role"]: record for record in content_memory["slide_content_memory"]}
    records: list[dict[str, Any]] = []
    role_asset_counts: dict[str, int] = {role: 0 for role in ROLES}
    for asset in visual_assets["visual_evidence_assets"]:
        role = asset["role"]
        role_asset_counts[role] += 1
        index = role_asset_counts[role] - 1
        plan = ROLE_REALISM[role]
        records.append(
            {
                "realism_memory_id": f"realism_2_35_{role}_{index + 1}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "parent_run2_24_asset_id": asset["asset_id"],
                "parent_run2_24_slot_id": asset["slot_id"],
                "source_ids": source_ids,
                "source_titles": source_ids,
                "usecase_specific_visual_evidence_object": f"{role} {asset['asset_type']} rendered as a product-specific state, not a generic evidence box",
                "observable_product_state": plan["states"][index],
                "business_context_caption": plan["captions"][index],
                "audience_question_answered": plan["question"],
                "native_ppt_realism_strategy": plan["strategy"],
                "anti_schematic_constraints": [
                    "Do not render this as a generic block diagram.",
                    "Do not use equal-weight placeholder rectangles as the primary proof object.",
                    "Do not label objects only as primary evidence or supporting evidence without a product state.",
                    "Do not use copied screenshots, brand marks, source layouts, raw video frames, audio, or transcript text.",
                ],
                "content_memory_binding": content_by_role[role]["content_memory_id"],
                "business_proof_points_to_surface": content_by_role[role]["business_proof_points"][:2],
                "required_trace_fields": [
                    "run2_35_visual_evidence_asset_realism_ids",
                    "run2_35_realism_source_ids",
                    "run2_35_observable_product_state",
                    "run2_35_visual_evidence_realism_execution_status",
                ],
                "source_boundary": "Derived observations only; no copied screenshots, video frames, source layouts, brand marks, audio, or transcript text.",
                "public_surface_allowed": True,
                "qa_probe": "At contact-sheet scale, the object should read as a usecase-specific product or business state rather than a schematic evidence token.",
            }
        )

    return {
        "schema_version": "ppt_run2_visual_evidence_asset_realism_memory.v1",
        "status": "run2_35_visual_evidence_asset_realism_memory_ready_public_blocked",
        "run_id": "2.35",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_audit_run": "2.34",
        "source_audit_target": audit["quality_summary"]["top_next_layer_to_thicken"],
        "derived_from": [
            "results/run2_34_main_surface_visual_evidence_audit.json",
            "run2_24_single_usecase_content_memory.json",
            "run2_24_visual_evidence_asset_memory.json",
            "sources.json",
            "commercial_usecase_bank.json",
        ],
        "storage_policy": {
            "raw_media": "forbidden",
            "copied_screenshots": "forbidden",
            "video_frames": "forbidden",
            "copied_layouts": "forbidden",
            "brand_marks": "forbidden",
            "allowed_storage": "derived_usecase_specific_visual_evidence_instructions_only",
        },
        "visual_evidence_asset_realism_records": records,
    }


def build_editorial_composition_memory() -> dict[str, Any]:
    audit = read_json(PACK / "results" / "run2_34_main_surface_visual_evidence_audit.json")
    weak_roles = set(audit["quality_summary"]["roles_with_weak_editorial_anchor"])
    records: list[dict[str, Any]] = []
    for role in ROLES:
        plan = ROLE_REALISM[role]
        records.append(
            {
                "composition_memory_id": f"composition_2_35_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "editorial_anchor_object": plan["anchor"],
                "hero_canvas_share_target": plan["hero_target"],
                "repairs_run2_34_weak_editorial_anchor": role in weak_roles,
                "composition_obligations": [
                    "One main object must own the first read before evidence-spine detail appears.",
                    "Secondary proof is allowed only as a rail, badge, or caption that supports the anchor.",
                    "The slide must show a product or business state, not a dashboard of equal tokens.",
                    plan["strategy"],
                ],
                "typography_obligations": [
                    "Use one short state label for the main object.",
                    "Keep trace language out of the public first-read surface.",
                    "Use captions as proof labels, not paragraphs.",
                ],
                "spacing_obligations": [
                    "Protect the main object with whitespace on at least two sides.",
                    "Avoid evenly distributed small cards across the main canvas.",
                    "Reserve the right evidence spine for reviewer context only.",
                ],
                "forbidden_patterns": [
                    "equal-weight schematic panels",
                    "generic block diagram",
                    "feature-card grid",
                    "tiny proof chips as the main visual",
                    "copied brand or source layout",
                ],
                "required_trace_fields": [
                    "run2_35_editorial_composition_memory_id",
                    "run2_35_editorial_anchor_object",
                    "run2_35_hero_canvas_share_target",
                    "run2_35_visual_evidence_realism_execution_status",
                ],
                "qa_probe": "At thumbnail scale, the role should have a stronger main anchor than Run 2.33 and should not read as a report panel.",
            }
        )
    return {
        "schema_version": "ppt_run2_editorial_composition_memory.v1",
        "status": "run2_35_editorial_composition_memory_ready_public_blocked",
        "run_id": "2.35",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_audit_run": "2.34",
        "derived_from": [
            "results/run2_34_main_surface_visual_evidence_audit.json",
            "run2_35_visual_evidence_asset_realism_memory.json",
        ],
        "editorial_composition_records": records,
    }


def build_workflow_gates(realism_memory: dict[str, Any], composition_memory: dict[str, Any]) -> dict[str, Any]:
    realism_by_role: dict[str, list[str]] = {role: [] for role in ROLES}
    for record in realism_memory["visual_evidence_asset_realism_records"]:
        realism_by_role[record["role"]].append(record["realism_memory_id"])
    composition_by_role = {
        record["role"]: record["composition_memory_id"]
        for record in composition_memory["editorial_composition_records"]
    }
    gates: list[dict[str, Any]] = []
    for role in ROLES:
        gates.append(
            {
                "gate_id": f"gate_2_35_{role}_visual_evidence_realism",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "required_realism_memory_ids": realism_by_role[role],
                "required_editorial_composition_memory_id": composition_by_role[role],
                "min_realistic_visual_evidence_objects": 2,
                "forbid_generic_block_diagrams": True,
                "forbid_copied_source_media": True,
                "next_rerun_contract": "must_be_consumed_before_run2_36_four_arm_rerun",
                "required_trace_fields": [
                    "run2_35_visual_evidence_asset_realism_ids",
                    "run2_35_editorial_composition_memory_id",
                    "run2_35_realism_gate_id",
                    "run2_35_observable_product_state",
                    "run2_35_hero_canvas_share_target",
                    "run2_35_visual_evidence_realism_execution_status",
                ],
                "pass_fail_checks": [
                    "The generated slide binds at least two Run 2.35 realism memory ids before native PPT drawing.",
                    "The main visual object has a usecase-specific observable product or business state.",
                    "The main object is not only a generic block diagram, token rail, or equal-weight card grid.",
                    "The role's editorial anchor object owns the first read at thumbnail scale.",
                    "No copied screenshots, brand marks, source layouts, raw media, or transcript text are used.",
                ],
                "bad_control_probe": "A negative control may receive the usecase label but fails if it lacks Run 2.35 realism memory ids, editorial composition memory, or gate id.",
                "public_release_gate": "blocked",
            }
        )
    return {
        "schema_version": "ppt_run2_visual_evidence_workflow_gates.v1",
        "status": "run2_35_visual_evidence_workflow_gates_ready_public_blocked",
        "run_id": "2.35",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "gates": gates,
    }


def build_result() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": "2.35",
        "status": "run2_35_visual_evidence_realism_workflow_ready_public_blocked",
        "source_audit_run": "2.34",
        "selected_usecase_id": SELECTED_USECASE_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "input_chain": {
            "main_surface_visual_evidence_audit": "docs/product/ppt-run2-data-skill-quality/results/run2_34_main_surface_visual_evidence_audit.json",
            "content_memory": "docs/product/ppt-run2-data-skill-quality/run2_24_single_usecase_content_memory.json",
            "visual_evidence_asset_memory": "docs/product/ppt-run2-data-skill-quality/run2_24_visual_evidence_asset_memory.json",
            "sources": "docs/product/ppt-run2-data-skill-quality/sources.json",
            "commercial_usecase_bank": "docs/product/ppt-run2-data-skill-quality/commercial_usecase_bank.json",
        },
        "output_chain": {
            "visual_evidence_asset_realism_memory": "docs/product/ppt-run2-data-skill-quality/run2_35_visual_evidence_asset_realism_memory.json",
            "editorial_composition_memory": "docs/product/ppt-run2-data-skill-quality/run2_35_editorial_composition_memory.json",
            "visual_evidence_workflow_gates": "docs/product/ppt-run2-data-skill-quality/run2_35_visual_evidence_workflow_gates.json",
        },
        "target_layer": SOURCE_AUDIT_TARGET,
        "artifact_counts": {
            "visual_evidence_asset_realism_records": 12,
            "editorial_composition_records": 6,
            "visual_evidence_workflow_gates": 6,
        },
        "delivery_artifacts": {
            "pptx_paths": [],
            "rendered_slide_paths": [],
            "contact_sheet_paths": [],
            "html_motion_renderer_paths": [],
        },
        "public_release_gate": "blocked",
        "release_boundary": "public_blocked_until_run2_36_consumes_run2_35_workflow_native_render_review_and_human_approval",
        "next_required_action": "consume_run2_35_visual_evidence_realism_workflow_before_run2_36_rerun",
    }


def update_skill_workflow() -> None:
    path = PACK / "skill_workflow.json"
    workflow = read_json(path)
    workflow["status"] = "run2_35_visual_evidence_realism_workflow_directed_public_blocked"
    existing = {stage["id"]: stage for stage in workflow["stages"]}
    new_stages = [
        {
            "id": "compile_run2_35_visual_evidence_asset_realism_memory",
            "order": 35,
            "layer": "evidence_aesthetic_asset_memory",
            "inputs": [
                "results/run2_34_main_surface_visual_evidence_audit.json",
                "run2_24_visual_evidence_asset_memory.json",
                "run2_24_single_usecase_content_memory.json",
                "sources.json",
            ],
            "outputs": ["run2_35_visual_evidence_asset_realism_memory.json"],
            "gates": [
                "each Run 2.24 visual evidence asset becomes a usecase-specific product or business state",
                "generic block diagrams and equal-weight placeholder rectangles are forbidden",
                "raw media, copied screenshots, source layouts, brand marks, audio, and transcript text remain forbidden",
            ],
        },
        {
            "id": "compile_run2_35_editorial_composition_memory",
            "order": 36,
            "layer": "design_memory",
            "inputs": [
                "results/run2_34_main_surface_visual_evidence_audit.json",
                "run2_35_visual_evidence_asset_realism_memory.json",
            ],
            "outputs": ["run2_35_editorial_composition_memory.json"],
            "gates": [
                "cover, setup, contrast, and close repair weak editorial anchors",
                "each role defines a first-read anchor object and hero canvas share target",
                "right-side evidence spine remains reviewer context, not the main public surface",
            ],
        },
        {
            "id": "apply_run2_35_visual_evidence_workflow_gates",
            "order": 37,
            "layer": "skill_workflow",
            "inputs": [
                "run2_35_visual_evidence_asset_realism_memory.json",
                "run2_35_editorial_composition_memory.json",
            ],
            "outputs": [
                "run2_35_visual_evidence_workflow_gates.json",
                "results/run2_35_visual_evidence_realism_workflow_result.json",
            ],
            "gates": [
                "Run 2.36 must consume Run 2.35 realism memory, editorial composition memory, and gates before native PPT generation",
                "negative control may receive the usecase label but not Run 2.35 memory or gate ids",
                "Run 2.35 is not a new PPT output and does not advance to Run 3.0",
            ],
        },
    ]
    for stage in new_stages:
        existing[stage["id"]] = stage
    workflow["stages"] = sorted(existing.values(), key=lambda item: item["order"])
    triggers = {trigger["id"]: trigger for trigger in workflow.get("repair_triggers", [])}
    triggers["run2_35_visual_evidence_realism_required_before_run2_36_rerun"] = {
        "id": "run2_35_visual_evidence_realism_required_before_run2_36_rerun",
        "trigger": "Run 2.34 found that Run 2.33 passes contract-only visual evidence counts but still uses schematic evidence and weak editorial anchors",
        "recommendation": "require run2_35_visual_evidence_asset_realism_memory.json, run2_35_editorial_composition_memory.json, and run2_35_visual_evidence_workflow_gates.json before Run 2.36 four-arm rerun",
        "human_gate": "required before Run 2.36 generated rerun",
    }
    workflow["repair_triggers"] = list(triggers.values())
    write_json(path, workflow)


def write_report(result: dict[str, Any], result_md: Path) -> None:
    lines = [
        "# Run 2.35 Visual Evidence Realism Workflow",
        "",
        "Status: Run 2.35 data/workflow pack completed, public blocked.",
        "",
        "Run 2.35 is data/workflow-only. It creates no new PPT deck and does not advance to Run 3.0.",
        "",
        f"Target layer: `{result['target_layer']}`.",
        "",
        "## What Changed",
        "",
        "- `run2_35_visual_evidence_asset_realism_memory.json` turns Run 2.24 abstract visual assets into usecase-specific product and business states.",
        "- `run2_35_editorial_composition_memory.json` defines the first-read anchor object, hero canvas share target, and forbidden composition patterns for every slide role.",
        "- `run2_35_visual_evidence_workflow_gates.json` requires the next generated rerun to bind realism memory, editorial composition memory, and a gate id before native PPT drawing.",
        "",
        "## Gate",
        "",
        "- Creates new PPT deck: false.",
        "- Public ready: false.",
        "- Public release gate: blocked.",
        "",
        "Next: consume the Run 2.35 visual evidence realism workflow before Run 2.36 four-arm rerun. Do not advance to Run 3.0.",
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

    usecase = selected_usecase()
    realism_memory = build_realism_memory(usecase)
    composition_memory = build_editorial_composition_memory()
    workflow_gates = build_workflow_gates(realism_memory, composition_memory)
    result = build_result()

    write_json(args.out_dir / "run2_35_visual_evidence_asset_realism_memory.json", realism_memory)
    write_json(args.out_dir / "run2_35_editorial_composition_memory.json", composition_memory)
    write_json(args.out_dir / "run2_35_visual_evidence_workflow_gates.json", workflow_gates)
    write_json(args.result_json, result)
    write_report(result, args.result_md)
    if args.out_dir.resolve() == DEFAULT_OUT_DIR.resolve():
        update_skill_workflow()
    print(f"Run 2.35 visual-evidence realism workflow pack: {args.result_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
