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


def test_run2_66_static_contract_is_ci_visible() -> None:
    script = (ROOT / "scripts" / "build_ppt_run2_66_reference_first_redesign.py").read_text(
        encoding="utf-8"
    )
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    result = load_json(PACK / "results" / "run2_66_reference_first_redesign_result.json")
    grammar = load_json(PACK / "run2_66_reference_first_design_grammar.json")
    result_md = (PACK / "results" / "run2_66_reference_first_redesign_result.md").read_text(
        encoding="utf-8"
    )

    assert result["run_id"] == "2.66"
    assert result["source_generated_run"] == "2.65"
    assert result["creates_new_ppt_deck"] is False
    assert result["next_required_action"] == (
        "run2_67_generate_four_arm_ppt_consuming_run2_66_reference_first_design_grammar"
    )
    assert grammar["raw_media_policy"] == "forbidden_reference_analysis_only"
    assert len(grammar["role_design_grammar_records"]) == 6

    assert_contains(
        script,
        [
            "run2_66_visual_failure_audit.json",
            "run2_66_reference_first_design_grammar.json",
            "run2_66_slide_art_direction_contracts.json",
            "run2_66_reference_first_workflow_gates.json",
            "stripe_sessions_2025_product_keynote",
            "figma_config_2026_opening_keynote",
            "run2_67_generate_four_arm_ppt_consuming_run2_66_reference_first_design_grammar",
        ],
    )
    assert_contains(
        viewer,
        [
            "Run 2.66 reference-first redesign",
            "run2_66_reference_first_redesign_result.json",
            "run2_66_reference_first_design_grammar.json",
            '"latestRunId": "2.71"',
        ],
    )
    assert_contains(
        result_md,
        [
            "Run 2.66 Reference-First Redesign",
            "does not generate a new PPT",
            "Run 2.67",
            "Do not advance to Run 3.0",
        ],
    )
