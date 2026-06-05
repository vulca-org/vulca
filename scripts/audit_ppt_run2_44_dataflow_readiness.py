from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
DEFAULT_RESULT_JSON = PACK / "results" / "run2_44_dataflow_readiness_audit.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_44_dataflow_readiness_audit.md"

RUN241_GENERATOR = ROOT / "scripts" / "generate_ppt_run2_41_content_visual_asset_arms.mjs"
RUN243_BUILDER = ROOT / "scripts" / "build_ppt_run2_43_visual_asset_semantics_workflow.py"
RUN241_FULL_TRACE = (
    ROOT
    / "outputs"
    / "019e7d9c-532a-70b3-8892-fa3ae42baef2"
    / "presentations"
    / "ppt-run2-41-full-vulca"
    / "trace_manifest.json"
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def build_audit() -> dict[str, Any]:
    generator_text = RUN241_GENERATOR.read_text(encoding="utf-8")
    builder_text = RUN243_BUILDER.read_text(encoding="utf-8")
    trace = read_json(RUN241_FULL_TRACE)
    trace_text = json.dumps(trace)
    run241_result = read_json(PACK / "results" / "run2_41_content_visual_asset_compiler_rerun_result.json")
    run243_result = read_json(PACK / "results" / "run2_43_visual_asset_semantics_workflow_result.json")
    run243_semantic = read_json(PACK / "run2_43_semantic_visual_asset_memory.json")
    run243_editorial = read_json(PACK / "run2_43_editorial_composition_typography_memory.json")
    run243_gates = read_json(PACK / "run2_43_visual_asset_semantics_workflow_gates.json")

    run2_41_reads_run2_38_data = all(
        token in generator_text
        for token in [
            "run2_38_public_video_slide_direction_memory.json",
            "run2_38_per_slide_visual_recipe_memory.json",
            "run2_38_public_video_workflow_gates.json",
        ]
    )
    run2_41_reads_run2_43_data = any(
        token in generator_text
        for token in [
            "run2_43_semantic_visual_asset_memory.json",
            "run2_43_editorial_composition_typography_memory.json",
            "run2_43_visual_asset_semantics_workflow_gates.json",
            "run2_43_semantic_visual_asset_ids",
        ]
    )
    data_drives_text_and_trace = all(
        token in generator_text
        for token in [
            "selection.publicHeadline",
            "selection.publicOutcome",
            "selection.publicObject",
            "selection.businessDetails",
            "run2_38_visual_direction_memory_id",
            "run2_38_per_slide_visual_recipe_id",
        ]
    )
    visual_geometry_is_hardcoded = all(
        token in generator_text
        for token in [
            "function drawRun241MarketScenePoster",
            "function drawRun241CinematicLaunchMoment",
            "rect(slide, poster.x + 46",
            "rect(slide, object.x + 42",
            "const visualAssetSurfaceTypes = {",
        ]
    )
    run2_43_semantics_hardcoded = all(
        token in builder_text for token in ["ROLE_SEMANTIC_OBJECTS", "ROLE_COMPOSITION_RULES"]
    )
    run2_43_reads_multimodal = any(
        token in builder_text
        for token in [
            "run2_7_multimodal_source_records.json",
            "production_reference_decompositions.json",
            "run2_18_multimodal_evidence_expansion.json",
            "sources.json",
        ]
    )

    findings = {
        "run2_43_consumed_by_latest_visible_ppt": False,
        "run2_41_generator_reads_run2_38_data": run2_41_reads_run2_38_data,
        "run2_41_generator_reads_run2_43_data": run2_41_reads_run2_43_data,
        "run2_41_trace_has_run2_38_direction_and_recipe_ids": (
            "run2_38_visual_direction_memory_id" in trace_text
            and "run2_38_per_slide_visual_recipe_id" in trace_text
            and "direction_2_38_" in trace_text
            and "recipe_2_38_" in trace_text
        ),
        "run2_41_trace_has_run2_38_gate_ids": "gate_2_38_" in trace_text,
        "run2_41_trace_has_run2_43_ids": "run2_43_" in trace_text,
        "run2_41_data_drives_text_and_trace": data_drives_text_and_trace,
        "run2_41_visual_geometry_is_hardcoded": visual_geometry_is_hardcoded,
        "run2_43_semantic_memory_is_hardcoded_from_prior_trace": run2_43_semantics_hardcoded,
        "run2_43_builder_reads_multimodal_source_records": run2_43_reads_multimodal,
    }

    return {
        "schema_version": "ppt_run2_dataflow_readiness_audit.v1",
        "run_id": "2.44-preflight",
        "status": "run2_44_dataflow_readiness_blocked",
        "bug_confirmed": True,
        "not_a_run2_44_output": True,
        "risk_priority": "high",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "creates_new_ppt_deck": False,
        "public_ready": False,
        "latest_visible_ppt_run": "2.41",
        "latest_visible_ppt_result_status": run241_result["status"],
        "latest_workflow_run": "2.43",
        "latest_workflow_status": run243_result["status"],
        "input_chain": {
            "run2_41_generator": rel(RUN241_GENERATOR),
            "run2_41_full_trace_manifest": rel(RUN241_FULL_TRACE),
            "run2_41_rerun_result": rel(PACK / "results" / "run2_41_content_visual_asset_compiler_rerun_result.json"),
            "run2_43_workflow_result": rel(PACK / "results" / "run2_43_visual_asset_semantics_workflow_result.json"),
            "run2_43_semantic_visual_asset_memory": rel(PACK / "run2_43_semantic_visual_asset_memory.json"),
            "run2_43_editorial_composition_typography_memory": rel(
                PACK / "run2_43_editorial_composition_typography_memory.json"
            ),
            "run2_43_visual_asset_semantics_workflow_gates": rel(
                PACK / "run2_43_visual_asset_semantics_workflow_gates.json"
            ),
        },
        "dataflow_findings": findings,
        "artifact_counts": {
            "run2_43_semantic_visual_asset_records": len(run243_semantic["semantic_visual_asset_records"]),
            "run2_43_editorial_composition_typography_records": len(
                run243_editorial["editorial_composition_typography_records"]
            ),
            "run2_43_visual_asset_semantics_workflow_gates": len(
                run243_gates["visual_asset_semantics_workflow_gates"]
            ),
        },
        "root_cause_primary": "latest_visible_ppt_does_not_consume_latest_run2_43_workflow",
        "root_cause_secondary": [
            "Run 2.41 consumes Run 2.38 data for copy, trace, and module selection, but visual geometry remains mostly hardcoded in drawRun241 functions.",
            "Run 2.43 is a post-2.41 workflow pack, so it cannot change the currently visible Run 2.41 slides until a new generator consumes it.",
            "Run 2.43 semantic memory is derived from Run 2.41 trace plus hardcoded role mappings; it does not yet re-read the multimodal tutorial/source records as the semantic source of truth.",
        ],
        "classification": "workflow_data_consumption_bug_and_stage_boundary",
        "next_rerun_gate": {
            "required_before_run2_44_generator": [
                "run2_43_semantic_visual_asset_memory.json",
                "run2_43_editorial_composition_typography_memory.json",
                "run2_43_visual_asset_semantics_workflow_gates.json",
            ],
            "generator_must_fail_if_run2_43_not_consumed": True,
            "visual_geometry_must_be_data_bound": True,
            "required_trace_fields": [
                "run2_43_semantic_visual_asset_ids",
                "run2_43_editorial_typography_memory_id",
                "run2_43_visual_asset_semantics_gate_id",
                "run2_43_visual_asset_semantics_execution_status",
                "run2_43_source_boundary_status",
            ],
            "negative_control_boundary": (
                "bad control may reuse the usecase and surface names, but must fail if it lacks Run 2.43 memory ids, "
                "gate ids, and data-bound geometry evidence"
            ),
        },
        "delivery_artifacts": {
            "pptx_paths": [],
            "rendered_slide_paths": [],
            "contact_sheet_paths": [],
        },
        "public_release_gate": "blocked",
        "next_required_action": "build_run2_44_generator_that_consumes_run2_43_memory_for_visual_geometry_before_render",
    }


def write_report(audit: dict[str, Any], result_md: Path) -> None:
    lines = [
        "# Run 2.44 Dataflow Readiness Audit",
        "",
        "Status: bug confirmed, dataflow readiness blocked.",
        "",
        "This is not a generated Run 2.44 output. It creates no new PPT deck.",
        "",
        "This audit checks whether the current visible PPT output actually consumes the latest workflow layer.",
        "",
        "Risk priority: high-priority technical debt.",
        "",
        "## Finding",
        "",
        "- The latest visible PPT is Run 2.41.",
        "- The latest workflow layer is Run 2.43.",
        "- The latest visible PPT does not consume Run 2.43.",
        "- Run 2.41 does consume Run 2.38 data, but data drives text and trace more than visual geometry.",
        "- Run 2.41 visual geometry is still largely hardcoded in drawRun241 modules.",
        "- Run 2.43 semantic memory is derived from prior trace plus role mappings; it does not yet re-read multimodal source records as the semantic source of truth.",
        "",
        "## Required Next Gate",
        "",
        "- Run 2.44 generator must fail if Run 2.43 memory is not consumed.",
        "- Run 2.44 must bind semantic visual asset ids, editorial typography memory id, workflow gate id, and source-boundary status into trace.",
        "- Run 2.44 must use Run 2.43 records to drive visual geometry, not only labels, captions, or trace metadata.",
        "",
        f"Next: `{audit['next_required_action']}`.",
        "",
    ]
    result_md.parent.mkdir(parents=True, exist_ok=True)
    result_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Run 2.44 dataflow readiness before generating another PPT.")
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_audit()
    write_json(args.result_json, audit)
    write_report(audit, args.result_md)
    print(json.dumps({"status": audit["status"], "result_json": str(args.result_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
