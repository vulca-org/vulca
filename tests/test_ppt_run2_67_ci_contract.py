from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_contains(body: str, terms: list[str]) -> None:
    for term in terms:
        assert term in body, f"missing term: {term!r}"


def test_run2_67_static_contract_is_ci_visible() -> None:
    generator = (ROOT / "scripts" / "generate_ppt_run2_67_reference_first_arms.mjs").read_text(
        encoding="utf-8"
    )
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    result = load_json(PACK / "results" / "run2_67_reference_first_rerun_result.json")

    assert result["run_id"] == "2.67"
    assert result["source_design_run_id"] == "2.66"
    assert result["source_generated_run_id"] == "2.65"
    assert result["quality_delta"]["target_layer"] == (
        "run2_66_reference_first_public_surface_art_direction_consumed"
    )
    assert result["quality_delta"]["full_slides_with_run2_66_reference_grammar"] == 6
    assert result["quality_delta"]["full_slides_with_public_surface_aesthetic_gate"] == 6
    assert result["quality_delta"]["bad_control_slides_without_run2_66_reference_grammar"] == 6
    assert result["rerun"]["best_internal_arm"] == "run2_67_full_reference_first_design_grammar"
    assert result["input_chain"]["run2_66_design_grammar"].endswith(
        "run2_66_reference_first_design_grammar.json"
    )
    assert result["control_boundary"]["bad_run2_65_without_run2_66_reference_first_grammar"]

    assert_contains(
        generator,
        [
            "run2_66_reference_first_design_grammar.json",
            "run2_66_slide_art_direction_contracts.json",
            "run2_66_reference_first_workflow_gates.json",
            "drawRun267ReferenceFirstPublicSurface",
            "run2_66_reference_first_design_grammar_consumed_before_native_ppt_drawing",
            "bad_run2_65_without_run2_66_reference_first_grammar",
        ],
    )
    assert_contains(
        viewer,
        [
            'LATEST_RUN_PAYLOAD_HINT = \'"latestRunId": "2.70"\'',
            "Run 2.67",
            "ppt-run2-67-prompt-only",
            "ppt-run2-67-run1-5-skill",
            "ppt-run2-67-full-vulca",
            "ppt-run2-67-bad-without-reference-first-grammar",
            "run2_67_reference_first_rerun_result.json",
        ],
    )
