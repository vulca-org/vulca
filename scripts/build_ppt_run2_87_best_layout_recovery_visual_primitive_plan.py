from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"

DEFAULT_RESULT_JSON = PACK / "run2_87_best_layout_recovery_visual_primitive_plan.json"
DEFAULT_RESULT_MD = PACK / "run2_87_best_layout_recovery_visual_primitive_plan.md"

RUN286_Q = PACK / "results" / "run2_86_visual_quality_evaluation.json"
RUN284_P1 = PACK / "run2_84_design_motif_taxonomy_style_router_plan.json"
RUN29_PRIMITIVES = PACK / "run2_9_visual_primitive_repair.json"
RUN29_MODULES = PACK / "run2_9_executable_visual_modules.json"
RUN210_RESULT = PACK / "results" / "run2_10_visual_system_rerun_result.json"
RUN216_RESULT = PACK / "results" / "run2_16_selector_rerun_result.json"
RUN267_RESULT = PACK / "results" / "run2_67_reference_first_rerun_result.json"
RUN268_RESULT = PACK / "results" / "run2_68_targeted_debug_rerun_result.json"
RUN285_RESULT = PACK / "results" / "run2_85_design_motif_renderer_rerun_result.json"

ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]
MODULE_BY_ROLE = {
    "cover": "product_reveal",
    "setup": "hero_field",
    "contrast": "before_after_theater",
    "proof": "evidence_workspace",
    "climax": "product_reveal",
    "close": "decision_map",
}
MOTIF_BY_ROLE = {
    "cover": "product_theater",
    "setup": "editorial_text_field",
    "contrast": "before_after_theater",
    "proof": "modular_matrix",
    "climax": "overlay_sticker_stack",
    "close": "decision_map",
}
PRIMITIVE_BY_ROLE = {
    "cover": "primitive_2_87_product_theater_surface",
    "setup": "primitive_2_87_editorial_text_field",
    "contrast": "primitive_2_87_before_after_surface",
    "proof": "primitive_2_87_modular_matrix_workspace",
    "climax": "primitive_2_87_overlay_sticker_stack",
    "close": "primitive_2_87_decision_map_board",
}
FUNCTION_BY_PRIMITIVE = {
    "primitive_2_87_product_theater_surface": "drawRun287ProductTheaterSurface",
    "primitive_2_87_editorial_text_field": "drawRun287EditorialTextField",
    "primitive_2_87_before_after_surface": "drawRun287BeforeAfterSurface",
    "primitive_2_87_modular_matrix_workspace": "drawRun287ModularMatrixWorkspace",
    "primitive_2_87_overlay_sticker_stack": "drawRun287OverlayStickerStack",
    "primitive_2_87_decision_map_board": "drawRun287DecisionMapBoard",
}
HISTORICAL_SOURCES_BY_ROLE = {
    "cover": ["2.10", "2.16", "2.67"],
    "setup": ["2.10", "2.16", "2.67", "2.68"],
    "contrast": ["2.10", "2.16", "2.67"],
    "proof": ["2.9", "2.10", "2.16", "2.68"],
    "climax": ["2.9", "2.10", "2.16", "2.67"],
    "close": ["2.9", "2.16", "2.67", "2.68"],
}
RECOVERED_PATTERN_BY_ROLE = {
    "cover": "editorial product-theater hero from Run 2.10/2.67 with one dominant product surface",
    "setup": "text-heavy editorial field plus anchored operating-loop stage from Run 2.16/2.68",
    "contrast": "before/after theater from Run 2.16/2.67 with enlarged after-state product surface",
    "proof": "inspectable modular evidence workspace from Run 2.10/2.68 with unequal matrix hierarchy",
    "climax": "cinematic climax stage plus overlay sticker stack from Run 2.9/2.10/2.67",
    "close": "release decision board from Run 2.16/2.68 with fewer nodes and a larger verdict branch",
}
ROOT_CAUSE_BY_ROLE = {
    "cover": "renderer_visual_primitives",
    "setup": "text_composition",
    "contrast": "design_motif_binding",
    "proof": "renderer_visual_primitives",
    "climax": "composition_engine",
    "close": "composition_engine",
}
PRIMITIVE_DETAILS = {
    "primitive_2_87_product_theater_surface": {
        "motif_family": "product_theater",
        "primitive_family": "layered_product_surface",
        "native_ppt_elements": [
            "editable product shell group",
            "stacked foreground/midground/background planes",
            "native screen chrome and content slots",
            "connected proof rail",
            "anchored object caption",
        ],
        "composition_rules": [
            "hero surface takes at least half the canvas",
            "foreground product plane must overlap a quieter context plane",
            "caption attaches to the product edge, never floats",
        ],
    },
    "primitive_2_87_editorial_text_field": {
        "motif_family": "editorial_text_field",
        "primitive_family": "text_heavy_editorial_spread",
        "native_ppt_elements": [
            "editable headline block",
            "readable subhead paragraph",
            "side caption rail",
            "anchored product destination object",
            "quiet margin markers",
        ],
        "composition_rules": [
            "main reading block is composed before labels",
            "paragraphs use one reading axis and one secondary rail",
            "object caption shares an axis with its anchor object",
        ],
    },
    "primitive_2_87_before_after_surface": {
        "motif_family": "before_after_theater",
        "primitive_family": "contrast_stage_with_surface_delta",
        "native_ppt_elements": [
            "before-state muted object",
            "after-state dominant product surface",
            "native transition bridge",
            "delta caption",
            "state labels bound to objects",
        ],
        "composition_rules": [
            "after state must be visually larger and richer than before state",
            "transition bridge must connect objects rather than sit as a loose arrow",
            "text labels attach to states",
        ],
    },
    "primitive_2_87_modular_matrix_workspace": {
        "motif_family": "modular_matrix",
        "primitive_family": "unequal_evidence_matrix",
        "native_ppt_elements": [
            "dominant evidence cell",
            "secondary proof cells",
            "matrix header rail",
            "native grouping lines",
            "embedded cell captions",
        ],
        "composition_rules": [
            "matrix cells are unequal and grouped by business logic",
            "one cell must carry the proof object",
            "cell copy is embedded in modules, not scattered around them",
        ],
    },
    "primitive_2_87_overlay_sticker_stack": {
        "motif_family": "overlay_sticker_stack",
        "primitive_family": "layered_sticker_payoff",
        "native_ppt_elements": [
            "dominant generated-deck surface",
            "tilted sticker badges",
            "overlapping proof strips",
            "scale marker",
            "short payoff phrase",
        ],
        "composition_rules": [
            "stickers overlap the product surface with visible depth",
            "the payoff object stays dominant",
            "badge text is short and audience-facing",
        ],
    },
    "primitive_2_87_decision_map_board": {
        "motif_family": "decision_map",
        "primitive_family": "release_decision_board",
        "native_ppt_elements": [
            "large decision branch geometry",
            "blocked-public outcome object",
            "native route connectors",
            "verdict caption",
            "supporting evidence chips",
        ],
        "composition_rules": [
            "decision map is the object, not a collection of small nodes",
            "one blocked-public outcome is visually explicit",
            "route labels stay attached to branches",
        ],
    },
}
REQUIRED_RUN2_9_PRIMITIVE_IDS = [
    "primitive_2_9_editorial_spread_composition",
    "primitive_2_9_product_surface_depth",
    "primitive_2_9_motion_storyboard_sequence",
    "primitive_2_9_climax_stage_composition",
    "primitive_2_9_typographic_field_composition",
]


def require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Run 2.87 plan missing required {label}: {path}")


def read_json(path: Path) -> dict[str, Any]:
    require_file(path, "JSON input")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(data, indent=2)}\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def validate_inputs(
    q_eval: dict[str, Any],
    p1_plan: dict[str, Any],
    run29_primitives: dict[str, Any],
    run29_modules: dict[str, Any],
    run285: dict[str, Any],
) -> None:
    if q_eval.get("status") != "run2_86_visual_quality_evaluation_public_blocked":
        raise ValueError("Run 2.87 expected Run 2.86 visual evaluation status")
    if q_eval.get("next_required_action") != "part_r_best_layout_recovery_and_visual_primitive_plan_from_q_evaluation":
        raise ValueError("Run 2.87 expected Q to hand off to Part R")
    root_cause = q_eval.get("root_cause_summary", {}).get("primary_layer")
    if root_cause != "renderer_visual_primitive_and_composition_engine":
        raise ValueError("Run 2.87 expected Q primary layer to be renderer visual primitive and composition engine")
    if p1_plan.get("status") != "run2_84_design_motif_taxonomy_style_router_plan_ready_public_blocked":
        raise ValueError("Run 2.87 expected Run 2.84 design motif plan")
    if run29_primitives.get("status") != "run2_9_visual_primitive_repair_public_blocked":
        raise ValueError("Run 2.87 expected Run 2.9 visual primitive repair data")
    if run29_modules.get("status") != "run2_9_executable_visual_modules_public_blocked":
        raise ValueError("Run 2.87 expected Run 2.9 executable visual modules")
    primitive_ids = {record.get("id") for record in run29_primitives.get("primitive_repairs", [])}
    missing = set(REQUIRED_RUN2_9_PRIMITIVE_IDS) - primitive_ids
    if missing:
        raise ValueError(f"Run 2.87 missing source Run 2.9 primitive ids: {sorted(missing)}")
    if run285.get("status") != "run2_85_design_motif_renderer_rerun_generated_public_blocked":
        raise ValueError("Run 2.87 expected Run 2.85 renderer result for latest failed generated state")


def build_page_layout_recovery_records(q_eval: dict[str, Any]) -> list[dict[str, Any]]:
    q_by_role = {record.get("role"): record for record in q_eval.get("role_assessments", [])}
    records: list[dict[str, Any]] = []
    for index, role in enumerate(ROLES, start=1):
        q_record = q_by_role.get(role, {})
        records.append(
            {
                "role": role,
                "slide_index": index,
                "visual_grammar_module": MODULE_BY_ROLE[role],
                "motif_family": MOTIF_BY_ROLE[role],
                "source_q_root_cause_layer": q_record.get("root_cause_layer", ROOT_CAUSE_BY_ROLE[role]),
                "source_q_repair_instruction": q_record.get(
                    "next_repair_instruction",
                    "recover best historical layout and add richer native visual primitive",
                ),
                "historical_layout_sources": HISTORICAL_SOURCES_BY_ROLE[role],
                "recovered_layout_pattern": RECOVERED_PATTERN_BY_ROLE[role],
                "renderer_primitive_id": PRIMITIVE_BY_ROLE[role],
                "composition_engine_obligation": {
                    "recover_best_historical_layout": True,
                    "preserve_text_heavy_readability": True,
                    "avoid_generic_box_layout": True,
                },
                "forbidden_patterns": [
                    "floating labels",
                    "traceability labels on slide canvas",
                    "generic rectangles only",
                    "equal card grid",
                ],
            }
        )
    return records


def build_visual_primitive_contracts() -> list[dict[str, Any]]:
    contracts = []
    for primitive_id, function_name in FUNCTION_BY_PRIMITIVE.items():
        detail = PRIMITIVE_DETAILS[primitive_id]
        contracts.append(
            {
                "primitive_id": primitive_id,
                "motif_family": detail["motif_family"],
                "primitive_family": detail["primitive_family"],
                "renderer_function_name": function_name,
                "native_ppt_elements": detail["native_ppt_elements"],
                "composition_rules": detail["composition_rules"],
                "anti_regression_gates": [
                    "not_rectangle_only",
                    "text_integrated_with_shape",
                    "collision_avoidance",
                    "motif_fidelity_visible",
                ],
                "forbidden_shortcuts": [
                    "generic rectangles only",
                    "floating trace labels",
                    "equal card grid",
                ],
            }
        )
    return contracts


def build_plan() -> dict[str, Any]:
    q_eval = read_json(RUN286_Q)
    p1_plan = read_json(RUN284_P1)
    run29_primitives = read_json(RUN29_PRIMITIVES)
    run29_modules = read_json(RUN29_MODULES)
    run210 = read_json(RUN210_RESULT)
    run216 = read_json(RUN216_RESULT)
    run267 = read_json(RUN267_RESULT)
    run268 = read_json(RUN268_RESULT)
    run285 = read_json(RUN285_RESULT)
    validate_inputs(q_eval, p1_plan, run29_primitives, run29_modules, run285)

    consumed_sources = [
        rel(RUN286_Q),
        rel(RUN284_P1),
        rel(RUN29_PRIMITIVES),
        rel(RUN29_MODULES),
        rel(RUN210_RESULT),
        rel(RUN216_RESULT),
        rel(RUN267_RESULT),
        rel(RUN268_RESULT),
        rel(RUN285_RESULT),
    ]
    return {
        "artifact_id": "run2_87_best_layout_recovery_visual_primitive_plan",
        "part": "Part R",
        "schema_version": "ppt_run2_87_best_layout_recovery_visual_primitive_plan.v1",
        "run_id": "2.87",
        "status": "run2_87_best_layout_recovery_visual_primitive_plan_ready_public_blocked",
        "stage_policy": "part_r_plan_only_best_layout_recovery_visual_primitive_contract_no_renderer_rerun",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "part_r_plan_only_no_renderer_rerun_no_public_release",
        "consumed_sources": consumed_sources,
        "source_q_evaluation": {
            "status": q_eval["status"],
            "next_required_action": q_eval["next_required_action"],
            "top_blocker": q_eval["visual_quality_assessment"]["top_blocker"],
            "primary_layer": q_eval["root_cause_summary"]["primary_layer"],
        },
        "historical_recovery_scope": {
            "candidate_runs": ["2.9", "2.10", "2.16", "2.67", "2.68"],
            "source_primitive_ids": REQUIRED_RUN2_9_PRIMITIVE_IDS,
            "source_module_ids": [module["id"] for module in run29_modules["modules"]],
            "recovery_principle": "recover best historical layout before drawing new motif primitive",
            "historical_evidence": {
                "run2_10": run210.get("visual_learning", {}).get("useful_delta", ""),
                "run2_16": run216.get("qa_summary", {}).get("gemini_artifact_review", ""),
                "run2_67": "reference-first archetypes, scene business objects, and depth layers",
                "run2_68": "targeted debug repairs for setup, proof, and close collision/layout issues",
            },
        },
        "page_layout_recovery_records": build_page_layout_recovery_records(q_eval),
        "visual_primitive_contracts": build_visual_primitive_contracts(),
        "composition_engine_repair_plan": {
            "layout_selection_order": [
                "historical_best_layout_recovery",
                "run2_67_reference_first_archetype",
                "run2_10_visual_system_module",
                "run2_84_design_motif_router",
            ],
            "collision_policy": {
                "reject_visible_text_overlap": True,
                "minimum_object_label_clearance_px": 12,
                "fallback_route": "move low-priority labels to speaker_note_or_viewer_metadata",
            },
            "traceability_policy": {
                "slide_canvas_traceability_allowed": False,
                "traceability_routes": ["viewer_metadata", "speaker_note", "trace_manifest"],
            },
            "text_density_policy": {
                "text_heavy_layout_allowed": True,
                "main_reading_block_required": True,
                "labels_must_attach_to_objects": True,
            },
        },
        "next_renderer_contract": {
            "next_run_id": "2.88",
            "next_renderer_script": "scripts/generate_ppt_run2_88_best_layout_visual_primitive_arms.mjs",
            "must_consume_part_r": True,
            "public_quality_verdict_deferred": True,
            "required_inputs": consumed_sources + [rel(DEFAULT_RESULT_JSON)],
            "arms": [
                "prompt_only",
                "run1_5_skill",
                "run2_88_full_best_layout_visual_primitives",
                "bad_without_best_layout_visual_primitives",
            ],
        },
        "no_new_renderer_proof": {
            "new_pptx_created": False,
            "new_html_created": False,
            "starts_renderer_rerun": False,
            "status": "pass",
        },
        "next_required_action": "part_s_renderer_rerun_from_run2_87_best_layout_visual_primitive_plan",
    }


def write_markdown(path: Path, plan: dict[str, Any]) -> None:
    lines = [
        "# Run 2.87 Best Layout Recovery",
        "",
        "Part R is a plan-only bridge from Q to the next renderer rerun. It does not generate PPT, HTML, or public release output.",
        "",
        "## Verdict",
        "",
        f"- Status: `{plan['status']}`",
        "- Strategy: historical best layout recovery before new visual primitive drawing.",
        "- Boundary: public blocked; visual quality verdict deferred to the rerun evaluation.",
        "",
        "## Page Recovery",
        "",
    ]
    for record in plan["page_layout_recovery_records"]:
        lines.append(
            f"- Slide {record['slide_index']} `{record['role']}`: "
            f"{record['recovered_layout_pattern']} -> `{record['renderer_primitive_id']}`"
        )
    lines.extend(
        [
            "",
            "## Visual Primitive Contracts",
            "",
        ]
    )
    for contract in plan["visual_primitive_contracts"]:
        lines.append(f"- `{contract['primitive_id']}` uses `{contract['renderer_function_name']}`.")
    lines.extend(
        [
            "",
            "## Next",
            "",
            "Run 2.88 must consume Part R and produce four arms, including a bad arm without best-layout visual primitives.",
            "",
            f"Next required action: `{plan['next_required_action']}`.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Run 2.87 best-layout recovery and visual primitive plan.")
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = build_plan()
    write_json(args.result_json, plan)
    write_markdown(args.result_md, plan)
    print(
        json.dumps(
            {
                "status": plan["status"],
                "result_json": rel(args.result_json.resolve()) if args.result_json.resolve().is_relative_to(ROOT) else str(args.result_json),
                "result_md": rel(args.result_md.resolve()) if args.result_md.resolve().is_relative_to(ROOT) else str(args.result_md),
                "public_ready": plan["public_ready"],
                "next_required_action": plan["next_required_action"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
