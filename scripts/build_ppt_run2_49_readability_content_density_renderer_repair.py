from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS_DIR = ROOT / "outputs" / "019e7d9c-532a-70b3-8892-fa3ae42baef2" / "presentations"
DEFAULT_OUT_DIR = PACK
DEFAULT_RESULT_JSON = PACK / "results" / "run2_49_readability_content_density_renderer_repair_result.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_49_readability_content_density_renderer_repair_result.md"

SELECTED_USECASE_ID = "usecase_design_to_production_platform_launch"
TARGET_LAYER = "readability_content_density_and_editorial_renderer_repair"
NEXT_ACTION = "consume_run2_49_before_run2_50_four_arm_rerun"
NEXT_RERUN_CONTRACT = "must_be_consumed_before_run2_50_four_arm_rerun"
SOURCE_AUDIT_ROOT_CAUSE = "run2_47_composition_grammar_consumed_but_visual_editorial_quality_still_not_public_grade"
ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]

ROLE_REPAIR_CONTRACTS: dict[str, dict[str, Any]] = {
    "cover": {
        "readability_goal": "launch promise must read at contact-sheet scale before system proof labels",
        "headline_max_words": 7,
        "title_px": 28,
        "support_max_words": 18,
        "evidence_objects": [
            "generated launch deck hero object",
            "memory control field",
            "commercial launch decision badge",
        ],
        "proof_objects": [
            "inspectable deck thumbnail cluster",
            "memory-to-output route marker",
        ],
        "surface_contract": "one poster-scale non-square hero surface with secondary proof rail",
    },
    "setup": {
        "readability_goal": "failure and selected route must be readable without workflow terminology",
        "headline_max_words": 8,
        "title_px": 24,
        "support_max_words": 20,
        "evidence_objects": [
            "prompt-only failure thumbnail",
            "selected commercial route board",
            "risk-to-route connector",
        ],
        "proof_objects": [
            "small failed deck state",
            "route decision surface",
        ],
        "surface_contract": "asymmetric storyboard with failure small and route large",
    },
    "contrast": {
        "readability_goal": "before/after delta must show business consequence, not equal cards",
        "headline_max_words": 8,
        "title_px": 24,
        "support_max_words": 18,
        "evidence_objects": [
            "before prompt-only slide strip",
            "after product-state surface",
            "delta consequence label",
        ],
        "proof_objects": [
            "before thumbnail",
            "after inspectable product canvas",
        ],
        "surface_contract": "wide after-state canvas with compressed before inset",
    },
    "proof": {
        "readability_goal": "active product surface must expose proof objects without becoming a table",
        "headline_max_words": 9,
        "title_px": 22,
        "support_max_words": 22,
        "evidence_objects": [
            "active decision lane",
            "deck preview proof object",
            "review state proof object",
        ],
        "proof_objects": [
            "inspectable decision lane",
            "editable deck preview state",
        ],
        "surface_contract": "product workspace scene with one dominant active lane",
    },
    "climax": {
        "readability_goal": "result object must own the frame and still carry concrete proof",
        "headline_max_words": 6,
        "title_px": 30,
        "support_max_words": 16,
        "evidence_objects": [
            "single generated deck result object",
            "before-to-memory transformation rail",
            "release boundary marker",
        ],
        "proof_objects": [
            "large final deck preview",
            "small memory/proof rail",
        ],
        "surface_contract": "cinematic result object, not a centered block grid",
    },
    "close": {
        "readability_goal": "handoff decision must be clear while release remains blocked",
        "headline_max_words": 8,
        "title_px": 23,
        "support_max_words": 20,
        "evidence_objects": [
            "decision handoff surface",
            "release readiness wall",
            "next-run action route",
        ],
        "proof_objects": [
            "handoff board with visible state",
            "next action path",
        ],
        "surface_contract": "decision room handoff with directional next-action strip",
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def selected_usecase() -> dict[str, Any]:
    bank = read_json(PACK / "commercial_usecase_bank.json")
    for usecase in bank["usecases"]:
        if usecase["id"] == SELECTED_USECASE_ID:
            return usecase
    raise ValueError(f"missing selected usecase {SELECTED_USECASE_ID}")


def assert_no_run249_deck_artifacts() -> None:
    if not PRESENTATIONS_DIR.exists():
        return
    deck_paths = sorted(
        path
        for pattern in ("*2-49*.ppt", "*2-49*.pptx")
        for path in PRESENTATIONS_DIR.glob(pattern)
    )
    if deck_paths:
        names = ", ".join(path.name for path in deck_paths)
        raise ValueError(f"Run 2.49 is data/workflow-only and must not create PPT artifacts: {names}")


def role_record(records: list[dict[str, Any]], role: str, key: str) -> dict[str, Any]:
    for record in records:
        if record.get("role") == role:
            return record
    raise ValueError(f"missing {key} for role {role}")


def validate_inputs(
    run248: dict[str, Any],
    grammar_memory: dict[str, Any],
    composition_gates: dict[str, Any],
    content_memory: dict[str, Any],
) -> None:
    visual = run248.get("visual_effectiveness_assessment") or {}
    if run248.get("status") != "run2_48_composition_grammar_effectiveness_audit_public_blocked":
        raise ValueError("Run 2.49 requires Run 2.48 composition grammar effectiveness audit")
    if run248.get("source_generated_run") != "2.47":
        raise ValueError("Run 2.49 source generated run must be Run 2.47")
    if run248.get("source_composition_memory_run") != "2.46":
        raise ValueError("Run 2.49 source composition memory must be Run 2.46")
    if run248.get("creates_new_ppt_deck") is not False:
        raise ValueError("Run 2.48 must be audit-only")
    if visual.get("visual_quality_gate") != "blocked":
        raise ValueError("Run 2.49 only applies while visual quality is blocked")
    if visual.get("root_cause_primary") != SOURCE_AUDIT_ROOT_CAUSE:
        raise ValueError("Run 2.49 source audit root cause mismatch")
    if visual.get("top_next_layer_to_thicken") != TARGET_LAYER:
        raise ValueError("Run 2.48 did not target Run 2.49 readability/content density repair")
    if grammar_memory.get("status") != "run2_46_visual_object_grammar_memory_ready_public_blocked":
        raise ValueError("Run 2.49 requires Run 2.46 visual object grammar memory")
    if composition_gates.get("status") != "run2_46_composition_workflow_gates_ready_public_blocked":
        raise ValueError("Run 2.49 requires Run 2.46 composition workflow gates")
    if content_memory.get("status") != "run2_24_single_usecase_content_memory_ready_public_blocked":
        raise ValueError("Run 2.49 requires Run 2.24 single-usecase content memory")
    if len(grammar_memory.get("visual_object_grammar_records") or []) != 6:
        raise ValueError("Run 2.49 expected six Run 2.46 grammar records")
    if len(composition_gates.get("composition_workflow_gates") or []) != 6:
        raise ValueError("Run 2.49 expected six Run 2.46 composition gates")
    if len(content_memory.get("slide_content_memory") or []) != 6:
        raise ValueError("Run 2.49 expected six Run 2.24 content records")


def build_readability_memory(
    run248: dict[str, Any],
    grammar_memory: dict[str, Any],
    content_memory: dict[str, Any],
) -> dict[str, Any]:
    grammar_records = grammar_memory["visual_object_grammar_records"]
    content_records = content_memory["slide_content_memory"]
    content_density = (
        (run248.get("visual_effectiveness_assessment") or {}).get("content_density_diagnosis") or {}
    )
    records: list[dict[str, Any]] = []
    for role in ROLES:
        contract = ROLE_REPAIR_CONTRACTS[role]
        grammar = role_record(grammar_records, role, "Run 2.46 grammar")
        content = role_record(content_records, role, "Run 2.24 content memory")
        records.append(
            {
                "readability_memory_id": f"readability_memory_2_49_{role}",
                "readability_gate_id": f"gate_2_49_{role}_contact_sheet_scale_readability",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "source_audit_run": "2.48",
                "source_generated_run": "2.47",
                "source_composition_memory_run": "2.46",
                "source_run2_46_visual_object_grammar_id": grammar["visual_object_grammar_id"],
                "source_run2_24_content_memory_id": content["content_memory_id"],
                "source_content_density_diagnosis": content_density,
                "readability_goal": contract["readability_goal"],
                "min_contact_sheet_title_px": contract["title_px"],
                "min_body_font_px": 16,
                "max_headline_words": contract["headline_max_words"],
                "max_support_words": contract["support_max_words"],
                "min_text_contrast_ratio": 4.5,
                "forbid_title_clipping": True,
                "forbid_micro_labels_as_primary_evidence": True,
                "forbid_trace_terms_on_public_surface": True,
                "required_readability_checks": [
                    "title remains legible at 25 percent contact-sheet scale",
                    "headline fits the intended title box without clipping",
                    "support copy does not overlap the primary visual object",
                    "public slide text hides run ids, memory ids, gate ids, and database terms",
                ],
                "next_rerun_obligation": NEXT_RERUN_CONTRACT,
            }
        )

    return {
        "schema_version": "ppt_run2_readability_memory.v1",
        "status": "run2_49_readability_memory_ready_public_blocked",
        "run_id": "2.49",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_audit_run": "2.48",
        "source_generated_run": "2.47",
        "source_composition_memory_run": "2.46",
        "target_layer": TARGET_LAYER,
        "readability_records": records,
    }


def build_content_evidence_density_memory(
    readability_memory: dict[str, Any],
    grammar_memory: dict[str, Any],
    content_memory: dict[str, Any],
) -> dict[str, Any]:
    grammar_records = grammar_memory["visual_object_grammar_records"]
    content_records = content_memory["slide_content_memory"]
    readability_records = readability_memory["readability_records"]
    records: list[dict[str, Any]] = []
    for role in ROLES:
        contract = ROLE_REPAIR_CONTRACTS[role]
        grammar = role_record(grammar_records, role, "Run 2.46 grammar")
        content = role_record(content_records, role, "Run 2.24 content memory")
        readability = role_record(readability_records, role, "Run 2.49 readability")
        records.append(
            {
                "content_evidence_density_memory_id": f"content_evidence_density_2_49_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "source_audit_run": "2.48",
                "source_generated_run": "2.47",
                "source_composition_memory_run": "2.46",
                "required_readability_memory_id": readability["readability_memory_id"],
                "source_run2_46_visual_object_grammar_id": grammar["visual_object_grammar_id"],
                "source_run2_24_content_memory_id": content["content_memory_id"],
                "min_specific_business_evidence_objects": 3,
                "min_inspectable_visual_proof_objects": 2,
                "min_role_specific_claims": 3,
                "business_proof_points": content.get("business_proof_points", []),
                "evidence_object_contract": contract["evidence_objects"],
                "inspectable_visual_proof_object_contract": contract["proof_objects"],
                "forbidden_evidence_substitutes": [
                    "generic abstract proof",
                    "empty square grid",
                    "trace-only badge as business evidence",
                    "decorative icon standing in for a product state",
                    "brand-like copied source screenshot",
                ],
                "content_density_checks": [
                    "at least three role-specific evidence objects are visible",
                    "at least two proof objects can be inspected without reading notes",
                    "business proof points are paraphrased into native editable text",
                    "evidence objects support the commercial decision rather than internal process reporting",
                ],
                "next_rerun_obligation": NEXT_RERUN_CONTRACT,
            }
        )

    return {
        "schema_version": "ppt_run2_content_evidence_density_memory.v1",
        "status": "run2_49_content_evidence_density_memory_ready_public_blocked",
        "run_id": "2.49",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_audit_run": "2.48",
        "source_generated_run": "2.47",
        "source_composition_memory_run": "2.46",
        "target_layer": TARGET_LAYER,
        "content_evidence_density_records": records,
    }


def build_editorial_renderer_workflow_gates(
    readability_memory: dict[str, Any],
    density_memory: dict[str, Any],
    composition_gates: dict[str, Any],
) -> dict[str, Any]:
    readability_records = readability_memory["readability_records"]
    density_records = density_memory["content_evidence_density_records"]
    prior_gates = composition_gates["composition_workflow_gates"]
    gates: list[dict[str, Any]] = []
    for role in ROLES:
        contract = ROLE_REPAIR_CONTRACTS[role]
        readability = role_record(readability_records, role, "Run 2.49 readability")
        density = role_record(density_records, role, "Run 2.49 density")
        prior_gate = role_record(prior_gates, role, "Run 2.46 composition gate")
        gates.append(
            {
                "gate_id": f"gate_2_49_{role}_editorial_renderer",
                "renderer_contract_id": f"renderer_contract_2_49_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "source_audit_run": "2.48",
                "source_generated_run": "2.47",
                "source_composition_memory_run": "2.46",
                "required_readability_memory_id": readability["readability_memory_id"],
                "required_content_evidence_density_memory_id": density[
                    "content_evidence_density_memory_id"
                ],
                "required_run2_46_composition_gate_id": prior_gate["gate_id"],
                "surface_contract": contract["surface_contract"],
                "forbid_square_block_grid_as_primary_surface": True,
                "forbid_equal_card_distribution_as_primary_surface": True,
                "forbid_palette_swap_as_visual_delta": True,
                "min_non_square_surface_ratio_variants": 2,
                "require_contact_sheet_readability": True,
                "require_inspectable_business_evidence": True,
                "require_editorial_hierarchy_before_shape_count": True,
                "require_native_editable_ppt_output": True,
                "next_rerun_contract": NEXT_RERUN_CONTRACT,
                "required_trace_fields": [
                    "run2_49_readability_memory_id",
                    "run2_49_content_evidence_density_memory_id",
                    "run2_49_editorial_renderer_gate_id",
                    "run2_49_renderer_contract_id",
                    "run2_49_non_square_surface_ratio_variants",
                    "run2_49_contact_sheet_readability_status",
                    "run2_49_business_evidence_density_status",
                ],
                "pass_fail_checks": [
                    "Run 2.50 binds one Run 2.49 readability memory id before native PPT drawing.",
                    "Run 2.50 binds one Run 2.49 content evidence density memory id before drawing proof objects.",
                    "Slide title passes contact-sheet readability and is not clipped.",
                    "Primary surface uses at least two non-square ratio variants and is not a square block grid.",
                    "At least three specific business evidence objects and two inspectable proof objects are visible.",
                    "Renderer trace records the Run 2.49 editorial renderer gate id and renderer contract id.",
                ],
                "bad_control_probe": (
                    "A negative control may receive Run 2.46 composition grammar, but fails if it lacks "
                    "Run 2.49 readability, content evidence density, and editorial renderer ids."
                ),
                "public_release_gate": "blocked",
            }
        )

    return {
        "schema_version": "ppt_run2_editorial_renderer_workflow_gates.v1",
        "status": "run2_49_editorial_renderer_workflow_gates_ready_public_blocked",
        "run_id": "2.49",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_audit_run": "2.48",
        "source_generated_run": "2.47",
        "source_composition_memory_run": "2.46",
        "target_layer": TARGET_LAYER,
        "next_rerun_contract": NEXT_RERUN_CONTRACT,
        "editorial_renderer_workflow_gates": gates,
    }


def build_result(
    out_dir: Path,
    readability_memory: dict[str, Any],
    density_memory: dict[str, Any],
    renderer_gates: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_readability_content_density_renderer_repair_result.v1",
        "run_id": "2.49",
        "status": "run2_49_readability_content_density_renderer_repair_ready_public_blocked",
        "source_audit_run": "2.48",
        "source_generated_run": "2.47",
        "source_composition_memory_run": "2.46",
        "selected_usecase_id": SELECTED_USECASE_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "target_layer": TARGET_LAYER,
        "input_chain": {
            "composition_grammar_effectiveness_audit": rel(
                PACK / "results" / "run2_48_composition_grammar_effectiveness_audit.json"
            ),
            "visual_object_grammar_memory": rel(PACK / "run2_46_visual_object_grammar_memory.json"),
            "composition_workflow_gates": rel(PACK / "run2_46_composition_workflow_gates.json"),
            "single_usecase_content_memory": rel(PACK / "run2_24_single_usecase_content_memory.json"),
        },
        "output_chain": {
            "readability_memory": rel(out_dir / "run2_49_readability_memory.json"),
            "content_evidence_density_memory": rel(
                out_dir / "run2_49_content_evidence_density_memory.json"
            ),
            "editorial_renderer_workflow_gates": rel(
                out_dir / "run2_49_editorial_renderer_workflow_gates.json"
            ),
        },
        "artifact_counts": {
            "readability_records": len(readability_memory["readability_records"]),
            "content_evidence_density_records": len(
                density_memory["content_evidence_density_records"]
            ),
            "editorial_renderer_workflow_gates": len(
                renderer_gates["editorial_renderer_workflow_gates"]
            ),
        },
        "delivery_artifacts": {
            "pptx_paths": [],
            "rendered_slide_paths": [],
            "contact_sheet_paths": [],
        },
        "repair_contract": {
            "readability": "contact-sheet title and support copy must remain legible",
            "content evidence density": "specific business evidence objects replace generic abstract proof",
            "editorial renderer": "native renderer must avoid square-block-grid primary surfaces",
            "data/workflow-only": True,
        },
        "public_release_gate": "blocked",
        "release_boundary": (
            "public_blocked_until_run2_50_consumes_run2_49_memories_and_gates_then_four_arm_visual_review_passes"
        ),
        "next_required_action": NEXT_ACTION,
    }


def write_markdown(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Run 2.49 Readability, Content Evidence Density, Editorial Renderer Repair",
                "",
                "Status: data/workflow-only repair pack, public blocked.",
                "",
                "Run 2.49 creates no PPT deck and does not claim a final visual output.",
                "",
                "It responds to Run 2.48 by turning the remaining visual problem into enforceable readability, content evidence density, and editorial renderer gates.",
                "",
                "## Outputs",
                "",
                "- `run2_49_readability_memory.json`: per-role contact-sheet readability and clipping gates.",
                "- `run2_49_content_evidence_density_memory.json`: per-role specific business evidence and inspectable proof-object requirements.",
                "- `run2_49_editorial_renderer_workflow_gates.json`: renderer gates that forbid square block grids as the primary surface.",
                "",
                "## Gate",
                "",
                "Run 2.50 must consume this pack before any generated slide claims improved visual quality.",
                "",
                f"Next: `{result['next_required_action']}`.",
                "",
                "Do not advance to Run 3.0.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Run 2.49 readability/content-density/editorial-renderer repair pack."
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--result-json", type=Path, default=DEFAULT_RESULT_JSON)
    parser.add_argument("--result-md", type=Path, default=DEFAULT_RESULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run248 = read_json(PACK / "results" / "run2_48_composition_grammar_effectiveness_audit.json")
    grammar_memory = read_json(PACK / "run2_46_visual_object_grammar_memory.json")
    composition_gates = read_json(PACK / "run2_46_composition_workflow_gates.json")
    content_memory = read_json(PACK / "run2_24_single_usecase_content_memory.json")
    validate_inputs(run248, grammar_memory, composition_gates, content_memory)
    assert_no_run249_deck_artifacts()

    usecase = selected_usecase()
    if usecase.get("id") != SELECTED_USECASE_ID:
        raise ValueError("Run 2.49 selected usecase mismatch")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    readability_memory = build_readability_memory(run248, grammar_memory, content_memory)
    density_memory = build_content_evidence_density_memory(
        readability_memory, grammar_memory, content_memory
    )
    renderer_gates = build_editorial_renderer_workflow_gates(
        readability_memory, density_memory, composition_gates
    )

    write_json(args.out_dir / "run2_49_readability_memory.json", readability_memory)
    write_json(args.out_dir / "run2_49_content_evidence_density_memory.json", density_memory)
    write_json(args.out_dir / "run2_49_editorial_renderer_workflow_gates.json", renderer_gates)

    result = build_result(args.out_dir, readability_memory, density_memory, renderer_gates)
    write_json(args.result_json, result)
    write_markdown(args.result_md, result)
    assert_no_run249_deck_artifacts()
    print(json.dumps({"status": result["status"], "result_json": str(args.result_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
