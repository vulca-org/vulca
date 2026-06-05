from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
DEFAULT_OUT_DIR = PACK
DEFAULT_RESULT_JSON = PACK / "results" / "run2_38_public_video_visual_direction_workflow_result.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_38_public_video_visual_direction_workflow_result.md"

SELECTED_USECASE_ID = "usecase_design_to_production_platform_launch"
TARGET_LAYER = "public_video_grade_slide_direction_and_per_slide_visual_recipe"
NEXT_ACTION = "consume_run2_38_public_video_visual_direction_workflow_before_run2_39_rerun"
RUN2_36_DOMINANT_SIGNATURE = "editorial_anchor_object+two_product_state_cards+gate_ribbon"
SOURCE_AUDIT_FINDING = "visual_module_language_too_repetitive_and_card_like"
ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]


ROLE_DIRECTIONS: dict[str, dict[str, Any]] = {
    "cover": {
        "visual_rhythm_id": "poster_reveal",
        "public_video_scene_type": "launch_poster",
        "first_read_object": "one oversized generated launch deck emerging from a memory-control field",
        "specific_business_object": "public-demo launch deck object with selected design-memory controls attached",
        "viewer_takeaway": "Vulca turns design memory into a launch surface before code draws slides.",
        "business_outcome": "repeatable launch-quality presentation generation, still public blocked until review",
        "code_module": "drawRun239LaunchPosterStage",
        "layout_signature_target": "poster_scale_launch_object_with_memory_halo",
        "primary_weight": 0.64,
        "typography": [
            "Use one short poster headline, one product-state label, and one small release boundary line.",
            "Keep trace terms off the first-read surface; put provenance in hidden trace fields.",
        ],
        "spacing": [
            "Reserve the center-right 60 percent for the launch object.",
            "Give the hero object open space on the top and right edges.",
        ],
        "visual_evidence": [
            "Show a single deck canvas with three attached memory-control markers.",
            "Avoid multiple equal cards; one product object must own the frame.",
        ],
        "motion": "slow poster reveal: memory markers settle after the launch object is already readable",
    },
    "setup": {
        "visual_rhythm_id": "failure_path_scene",
        "public_video_scene_type": "failure_scene",
        "first_read_object": "prompt-only failure path collapsing into a smaller unreviewable slide surface",
        "specific_business_object": "broken prompt-only route losing source boundary, product state, and release gate",
        "viewer_takeaway": "The problem is not making a slide; it is making a slide that can be inspected and blocked.",
        "business_outcome": "lower review risk by moving from prompt-only output to selected workflow control",
        "code_module": "drawRun239FailurePathScene",
        "layout_signature_target": "diagonal_failure_path_to_selected_route",
        "primary_weight": 0.56,
        "typography": [
            "Use a problem headline with one concrete failure label per broken step.",
            "Make the selected route label larger than the failed prompt fragments.",
        ],
        "spacing": [
            "Compress failure fragments into a left-down diagonal.",
            "Protect the selected route with a clean arrival zone, not a grid.",
        ],
        "visual_evidence": [
            "Draw the weak prompt output as a small unstable surface.",
            "Draw the selected route as a stable product path, not another card row.",
        ],
        "motion": "failure fragments fade downward; selected route locks into place",
    },
    "contrast": {
        "visual_rhythm_id": "asymmetric_before_after",
        "public_video_scene_type": "before_after_product_state",
        "first_read_object": "large after-state product surface dwarfing a small prompt-only before thumbnail",
        "specific_business_object": "same commercial brief before and after evidence selection",
        "viewer_takeaway": "The same brief becomes more specific when evidence and workflow are selected before generation.",
        "business_outcome": "clearer buyer confidence because output changes are attributable, not aesthetic luck",
        "code_module": "drawRun239AsymmetricBeforeAfterState",
        "layout_signature_target": "small_before_large_after_product_state",
        "primary_weight": 0.62,
        "typography": [
            "Use Before and After as state labels, not equal section headers.",
            "Give the after state one larger outcome caption tied to the usecase.",
        ],
        "spacing": [
            "Before thumbnail occupies less than one quarter of the canvas.",
            "After state occupies the dominant reading path with a clear edge gap.",
        ],
        "visual_evidence": [
            "Before state must look generic and intentionally underpowered.",
            "After state must show selected usecase, visual memory, and output surface in one product object.",
        ],
        "motion": "before state recedes; after state scales in as the selected evidence route appears",
    },
    "proof": {
        "visual_rhythm_id": "product_workflow_surface",
        "public_video_scene_type": "product_workflow_surface",
        "first_read_object": "working product console that maps slide roles to visual decisions and proof objects",
        "specific_business_object": "six-role visual decision surface with selected visual recipe per slide",
        "viewer_takeaway": "The product does not just remember references; it turns them into executable slide decisions.",
        "business_outcome": "faster review loops because every generated slide has a visible decision source",
        "code_module": "drawRun239ProductWorkflowSurface",
        "layout_signature_target": "product_console_with_selected_recipe_lane",
        "primary_weight": 0.58,
        "typography": [
            "Use a product-console label and three compact column labels.",
            "Use one highlighted selected lane, not six identical cards.",
        ],
        "spacing": [
            "Use a broad horizontal console with one selected lane expanded.",
            "Keep reviewer metadata as quiet badges around the console.",
        ],
        "visual_evidence": [
            "Show slide role, visual rhythm, and recipe binding in a product-like surface.",
            "Make one selected row visibly active so it reads as an app state.",
        ],
        "motion": "selected recipe lane expands while inactive lanes stay compressed",
    },
    "climax": {
        "visual_rhythm_id": "cinematic_climax_object",
        "public_video_scene_type": "cinematic_climax_object",
        "first_read_object": "one cinematic generated deck object with visible before, memory, and release state fused together",
        "specific_business_object": "final generated output object carrying the source-bound design memory proof",
        "viewer_takeaway": "The value is one powerful generated result, not another audit of the system.",
        "business_outcome": "internal-demo proof strong enough to justify another quality loop, not public release",
        "code_module": "drawRun239CinematicClimaxObject",
        "layout_signature_target": "single_cinematic_result_object_with_quiet_release_boundary",
        "primary_weight": 0.76,
        "typography": [
            "Use one cinematic claim and one small release boundary label.",
            "Do not show workflow field names on the public first-read surface.",
        ],
        "spacing": [
            "Let the result object occupy most of the canvas with a stage-like margin.",
            "Push all secondary proof into a low-contrast rail.",
        ],
        "visual_evidence": [
            "The result object must be a single visual climax, not a cluster of proof cards.",
            "Fuse generated deck, selected memory, and review state into one object.",
        ],
        "motion": "single result object enters last and holds; supporting evidence stays quiet",
    },
    "close": {
        "visual_rhythm_id": "decision_handoff_path",
        "public_video_scene_type": "decision_handoff_path",
        "first_read_object": "inspectable next-run handoff path with one clear decision gate and one public-blocked state",
        "specific_business_object": "Run 2.39 contract path from visual direction memory to generated deck",
        "viewer_takeaway": "The next action is not more prompting; it is consuming a stricter visual-direction workflow.",
        "business_outcome": "controlled product iteration before public launch or video release",
        "code_module": "drawRun239DecisionHandoffPath",
        "layout_signature_target": "quiet_handoff_path_with_single_decision_gate",
        "primary_weight": 0.55,
        "typography": [
            "Use a decision headline and three path labels.",
            "Keep the blocked release state explicit but visually quiet.",
        ],
        "spacing": [
            "Use one clean path from memory to rerun to review.",
            "Avoid a checklist surface; the path is the proof object.",
        ],
        "visual_evidence": [
            "Show one future rerun contract as an inspectable launch path.",
            "Keep gate markers small and semantic rather than ribbon-like.",
        ],
        "motion": "path draws left to right; release boundary appears as the final stop",
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


def validate_source_audit(audit: dict[str, Any]) -> None:
    assessment = audit.get("visual_quality_assessment") or {}
    if audit.get("status") != "run2_37_visual_quality_audit_public_blocked":
        raise ValueError("Run 2.38 requires the Run 2.37 visual-quality audit")
    if audit.get("source_generated_run") != "2.36" or audit.get("source_data_workflow_run") != "2.35":
        raise ValueError("Run 2.37 audit source chain mismatch")
    if assessment.get("design_quality_gate") != "blocked":
        raise ValueError("Run 2.38 should only run while design quality remains blocked")
    if assessment.get("root_cause_primary") != SOURCE_AUDIT_FINDING:
        raise ValueError("Run 2.38 source audit finding mismatch")
    if assessment.get("top_next_layer_to_thicken") != TARGET_LAYER:
        raise ValueError("Run 2.37 did not target the Run 2.38 public-video visual direction layer")


def build_public_video_slide_direction_memory(usecase: dict[str, Any]) -> dict[str, Any]:
    audit = read_json(PACK / "results" / "run2_37_visual_quality_audit.json")
    run236 = read_json(PACK / "results" / "run2_36_visual_evidence_realism_rerun_result.json")
    validate_source_audit(audit)
    source_ids = source_ids_for_usecase(usecase)
    records: list[dict[str, Any]] = []
    for role in ROLES:
        spec = ROLE_DIRECTIONS[role]
        records.append(
            {
                "direction_memory_id": f"direction_2_38_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "source_ids": source_ids,
                "source_audit_run": "2.37",
                "source_generated_run": "2.36",
                "source_audit_finding": audit["visual_quality_assessment"]["root_cause_primary"],
                "source_rejected_layout_signature": RUN2_36_DOMINANT_SIGNATURE,
                "visual_rhythm_id": spec["visual_rhythm_id"],
                "public_video_scene_type": spec["public_video_scene_type"],
                "first_read_object": spec["first_read_object"],
                "commercial_story_payload": {
                    "specific_business_object": spec["specific_business_object"],
                    "viewer_takeaway": spec["viewer_takeaway"],
                    "business_outcome": spec["business_outcome"],
                    "product_platform_gate": "show the product system, not a list of features",
                },
                "required_code_modules": [spec["code_module"]],
                "forbidden_visible_patterns": [
                    "same_visual_module_signature_across_all_roles",
                    "feature-card grid",
                    "audit ribbon as public composition",
                    "generic architecture boxes",
                    "equal-weight product state cards",
                    RUN2_36_DOMINANT_SIGNATURE,
                ],
                "required_trace_fields": [
                    "run2_38_visual_direction_memory_id",
                    "run2_38_visual_rhythm_id",
                    "run2_38_public_video_scene_type",
                    "run2_38_first_read_object",
                    "run2_38_public_video_execution_status",
                ],
                "public_video_grade_acceptance_checks": [
                    "At contact-sheet size the slide rhythm differs from the other five roles.",
                    "The first read is a concrete product or business object, not an audit panel.",
                    "The public surface does not show workflow gates as a ribbon.",
                    "The slide can be explained as a commercial launch moment without reading trace metadata.",
                    "The code module is role-specific and not the repeated Run 2.36 module stack.",
                ],
                "source_boundary": "Derived visual direction only; no copied screenshots, source layouts, brand marks, raw media, audio, transcript text, or tutorial frames.",
                "public_surface_allowed": True,
            }
        )

    return {
        "schema_version": "ppt_run2_public_video_slide_direction_memory.v1",
        "status": "run2_38_public_video_slide_direction_memory_ready_public_blocked",
        "run_id": "2.38",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_audit_run": "2.37",
        "source_generated_run": "2.36",
        "source_data_workflow_run": "2.35",
        "source_user_feedback": audit.get("user_feedback", ""),
        "source_audit_root_cause": audit["visual_quality_assessment"]["root_cause_primary"],
        "source_rerun_verdict": run236["rerun"]["best_internal_arm_verdict"],
        "target_layer": TARGET_LAYER,
        "derived_from": [
            "results/run2_37_visual_quality_audit.json",
            "results/run2_36_visual_evidence_realism_rerun_result.json",
            "results/run2_35_visual_evidence_realism_workflow_result.json",
            "commercial_usecase_bank.json",
            "sources.json",
        ],
        "public_video_slide_direction_records": records,
    }


def build_per_slide_visual_recipe_memory(direction_memory: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    direction_by_role = {
        record["role"]: record for record in direction_memory["public_video_slide_direction_records"]
    }
    for role in ROLES:
        spec = ROLE_DIRECTIONS[role]
        direction = direction_by_role[role]
        records.append(
            {
                "recipe_memory_id": f"recipe_2_38_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "source_direction_memory_id": direction["direction_memory_id"],
                "visual_rhythm_id": spec["visual_rhythm_id"],
                "layout_signature_target": spec["layout_signature_target"],
                "forbid_run2_36_dominant_layout_signature": RUN2_36_DOMINANT_SIGNATURE,
                "show_workflow_gate_as_public_ribbon": False,
                "primary_visual_weight_target": spec["primary_weight"],
                "typography_recipe": spec["typography"],
                "spacing_recipe": spec["spacing"],
                "visual_evidence_recipe": spec["visual_evidence"],
                "motion_beat_recipe": spec["motion"],
                "native_ppt_code_obligations": [
                    f"Call {spec['code_module']} before any generic product card surface is drawn.",
                    "Store workflow gate evidence in trace fields, not as a public ribbon.",
                    "Render one dominant first-read object before any supporting rails.",
                    "Keep the output editable native PPT shapes and text.",
                ],
                "required_trace_fields": [
                    "run2_38_per_slide_visual_recipe_id",
                    "run2_38_layout_signature_target",
                    "run2_38_primary_visual_weight_target",
                    "run2_38_public_video_execution_status",
                ],
                "qa_probe": "The slide should fail if it could be mistaken for the Run 2.36 dark-card plus gate-ribbon layout.",
            }
        )
    return {
        "schema_version": "ppt_run2_per_slide_visual_recipe_memory.v1",
        "status": "run2_38_per_slide_visual_recipe_memory_ready_public_blocked",
        "run_id": "2.38",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_audit_run": "2.37",
        "source_direction_memory": "run2_38_public_video_slide_direction_memory.json",
        "per_slide_visual_recipe_records": records,
    }


def build_workflow_gates(direction_memory: dict[str, Any], recipe_memory: dict[str, Any]) -> dict[str, Any]:
    direction_by_role = {
        record["role"]: record for record in direction_memory["public_video_slide_direction_records"]
    }
    recipe_by_role = {
        record["role"]: record for record in recipe_memory["per_slide_visual_recipe_records"]
    }
    gates: list[dict[str, Any]] = []
    for role in ROLES:
        direction = direction_by_role[role]
        recipe = recipe_by_role[role]
        gates.append(
            {
                "gate_id": f"gate_2_38_{role}_public_video_visual_direction",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "required_public_video_slide_direction_memory_id": direction["direction_memory_id"],
                "required_per_slide_visual_recipe_memory_id": recipe["recipe_memory_id"],
                "required_visual_rhythm_id": direction["visual_rhythm_id"],
                "required_layout_signature_target": recipe["layout_signature_target"],
                "required_code_modules": direction["required_code_modules"],
                "forbid_run2_36_dominant_layout_signature": True,
                "forbid_workflow_gate_as_public_ribbon": True,
                "next_rerun_contract": "must_be_consumed_before_run2_39_four_arm_rerun",
                "required_trace_fields": [
                    "run2_38_visual_direction_memory_id",
                    "run2_38_per_slide_visual_recipe_id",
                    "run2_38_visual_rhythm_id",
                    "run2_38_layout_signature_target",
                    "run2_38_public_video_execution_status",
                ],
                "pass_fail_checks": [
                    "The generated slide must use the Run 2.38 per-slide recipe before native PPT drawing.",
                    "The public surface must not expose workflow gates as audit ribbons.",
                    "The slide layout signature must differ from the Run 2.36 dominant card layout.",
                    "Across the full arm, all six roles must use six unique visual rhythms.",
                    "The slide must keep source media boundaries: derived instructions only, no copied source visuals.",
                ],
                "bad_control_probe": "A negative control may receive the usecase label but fails if it lacks Run 2.38 direction memory, visual recipe memory, visual rhythm id, or layout signature target.",
                "public_release_gate": "blocked",
            }
        )
    return {
        "schema_version": "ppt_run2_public_video_workflow_gates.v1",
        "status": "run2_38_public_video_workflow_gates_ready_public_blocked",
        "run_id": "2.38",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "visual_rhythm_diversity_contract": {
            "min_unique_visual_rhythms": 6,
            "max_repeated_layout_signature_allowed": 1,
            "forbidden_dominant_layout_signature": RUN2_36_DOMINANT_SIGNATURE,
        },
        "gates": gates,
    }


def build_result() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": "2.38",
        "status": "run2_38_public_video_visual_direction_workflow_ready_public_blocked",
        "source_audit_run": "2.37",
        "source_generated_run": "2.36",
        "source_data_workflow_run": "2.35",
        "selected_usecase_id": SELECTED_USECASE_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "input_chain": {
            "visual_quality_audit": "docs/product/ppt-run2-data-skill-quality/results/run2_37_visual_quality_audit.json",
            "visual_evidence_realism_rerun_result": "docs/product/ppt-run2-data-skill-quality/results/run2_36_visual_evidence_realism_rerun_result.json",
            "visual_evidence_realism_workflow_result": "docs/product/ppt-run2-data-skill-quality/results/run2_35_visual_evidence_realism_workflow_result.json",
            "commercial_usecase_bank": "docs/product/ppt-run2-data-skill-quality/commercial_usecase_bank.json",
            "sources": "docs/product/ppt-run2-data-skill-quality/sources.json",
        },
        "output_chain": {
            "public_video_slide_direction_memory": "docs/product/ppt-run2-data-skill-quality/run2_38_public_video_slide_direction_memory.json",
            "per_slide_visual_recipe_memory": "docs/product/ppt-run2-data-skill-quality/run2_38_per_slide_visual_recipe_memory.json",
            "public_video_workflow_gates": "docs/product/ppt-run2-data-skill-quality/run2_38_public_video_workflow_gates.json",
        },
        "target_layer": TARGET_LAYER,
        "artifact_counts": {
            "public_video_slide_direction_records": 6,
            "per_slide_visual_recipe_records": 6,
            "public_video_workflow_gates": 6,
        },
        "delivery_artifacts": {
            "pptx_paths": [],
            "rendered_slide_paths": [],
            "contact_sheet_paths": [],
            "html_motion_renderer_paths": [],
        },
        "public_release_gate": "blocked",
        "release_boundary": "public_blocked_until_run2_39_consumes_run2_38_workflow_native_render_review_motion_review_and_human_approval",
        "next_required_action": NEXT_ACTION,
    }


def update_skill_workflow() -> None:
    path = PACK / "skill_workflow.json"
    workflow = read_json(path)
    workflow["status"] = "run2_38_public_video_visual_direction_workflow_directed_public_blocked"
    existing = {stage["id"]: stage for stage in workflow["stages"]}
    new_stages = [
        {
            "id": "compile_run2_38_public_video_slide_direction_memory",
            "order": 38,
            "layer": "public_video_visual_direction_memory",
            "inputs": [
                "results/run2_37_visual_quality_audit.json",
                "results/run2_36_visual_evidence_realism_rerun_result.json",
                "commercial_usecase_bank.json",
                "sources.json",
            ],
            "outputs": ["run2_38_public_video_slide_direction_memory.json"],
            "gates": [
                "each slide role receives a unique public-video visual rhythm",
                "Run 2.36 dominant card layout is explicitly rejected",
                "product-platform proof objects replace generic cards and audit ribbons",
            ],
        },
        {
            "id": "compile_run2_38_per_slide_visual_recipe_memory",
            "order": 39,
            "layer": "per_slide_visual_recipe_memory",
            "inputs": ["run2_38_public_video_slide_direction_memory.json"],
            "outputs": ["run2_38_per_slide_visual_recipe_memory.json"],
            "gates": [
                "each role defines layout signature, typography, spacing, visual evidence, and motion beat obligations",
                "workflow gates are stored in trace, not shown as public ribbon composition",
                "all six layout signatures must be unique before the next rerun",
            ],
        },
        {
            "id": "apply_run2_38_public_video_workflow_gates",
            "order": 40,
            "layer": "skill_workflow",
            "inputs": [
                "run2_38_public_video_slide_direction_memory.json",
                "run2_38_per_slide_visual_recipe_memory.json",
            ],
            "outputs": [
                "run2_38_public_video_workflow_gates.json",
                "results/run2_38_public_video_visual_direction_workflow_result.json",
            ],
            "gates": [
                "Run 2.39 must consume Run 2.38 visual direction memory, visual recipe memory, and gates before native PPT generation",
                "negative control may receive the usecase label but not Run 2.38 direction or recipe ids",
                "Run 2.38 is not a new PPT output and does not advance to Run 3.0",
            ],
        },
    ]
    for stage in new_stages:
        existing[stage["id"]] = stage
    workflow["stages"] = sorted(existing.values(), key=lambda item: item["order"])
    triggers = {trigger["id"]: trigger for trigger in workflow.get("repair_triggers", [])}
    triggers["run2_38_public_video_direction_required_before_run2_39_rerun"] = {
        "id": "run2_38_public_video_direction_required_before_run2_39_rerun",
        "trigger": "Run 2.37 found that Run 2.36 proves data consumption but stays visually average because all six slides share one card-like layout signature",
        "recommendation": "require run2_38_public_video_slide_direction_memory.json, run2_38_per_slide_visual_recipe_memory.json, and run2_38_public_video_workflow_gates.json before Run 2.39 four-arm rerun",
        "human_gate": "required before Run 2.39 generated rerun",
    }
    workflow["repair_triggers"] = list(triggers.values())
    write_json(path, workflow)


def write_report(result: dict[str, Any], result_md: Path) -> None:
    lines = [
        "# Run 2.38 Public Video Visual Direction Workflow",
        "",
        "Status: Run 2.38 data/workflow pack completed, public blocked.",
        "",
        "Run 2.38 is data/workflow-only. It creates no new PPT deck and does not advance to Run 3.0.",
        "",
        "It converts the Run 2.37 finding `visual_module_language_too_repetitive_and_card_like` into per-slide visual direction and workflow gates.",
        "",
        f"Target layer: `{result['target_layer']}`.",
        "",
        "## What Changed",
        "",
        "- `run2_38_public_video_slide_direction_memory.json` gives every slide role a unique visual rhythm and public-video scene type.",
        "- `run2_38_per_slide_visual_recipe_memory.json` defines layout signature, typography, spacing, visual evidence, and motion beat obligations per slide.",
        "- `run2_38_public_video_workflow_gates.json` requires the next generated rerun to consume those direction and recipe ids before native PPT drawing.",
        "",
        "## Gate",
        "",
        "- Creates new PPT deck: false.",
        "- Public ready: false.",
        "- Public release gate: blocked.",
        "- Run 2.39 four-arm rerun must consume this workflow before any generated slide claims public-video quality.",
        "",
        "Next: consume the Run 2.38 public-video visual direction workflow before Run 2.39 four-arm rerun. Do not advance to Run 3.0.",
        "",
    ]
    result_md.parent.mkdir(parents=True, exist_ok=True)
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Run 2.38 public-video visual-direction data/workflow pack.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    usecase = selected_usecase()
    direction_memory = build_public_video_slide_direction_memory(usecase)
    recipe_memory = build_per_slide_visual_recipe_memory(direction_memory)
    workflow_gates = build_workflow_gates(direction_memory, recipe_memory)
    result = build_result()

    out_dir = args.out_dir
    write_json(out_dir / "run2_38_public_video_slide_direction_memory.json", direction_memory)
    write_json(out_dir / "run2_38_per_slide_visual_recipe_memory.json", recipe_memory)
    write_json(out_dir / "run2_38_public_video_workflow_gates.json", workflow_gates)
    write_json(args.result_json, result)
    write_report(result, args.result_md)
    if out_dir.resolve() == PACK.resolve():
        update_skill_workflow()
    print(json.dumps({"status": result["status"], "result_json": str(args.result_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
