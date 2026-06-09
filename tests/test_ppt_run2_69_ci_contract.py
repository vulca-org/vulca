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


def test_run2_69_static_public_content_fill_contract_is_ci_visible() -> None:
    generator = (ROOT / "scripts" / "generate_ppt_run2_69_public_content_fill_arms.mjs").read_text(
        encoding="utf-8"
    )
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    result = load_json(PACK / "results" / "run2_69_public_content_fill_rerun_result.json")

    assert result["run_id"] == "2.69"
    assert result["source_generated_run_id"] == "2.68"
    assert result["source_design_run_id"] == "2.66"
    assert result["public_cleanup_scope"]["content_roles"] == [
        "cover",
        "setup",
        "contrast",
        "proof",
        "climax",
        "close",
    ]
    assert result["quality_delta"]["target_layer"] == "run2_68_public_content_slot_fill"
    assert result["quality_delta"]["full_slides_with_public_content_slots"] == 6
    assert result["quality_delta"]["full_slides_without_visible_debug_terms"] == 6
    assert result["quality_delta"]["full_slides_with_visual_slot_labels"] == 6
    assert result["control_boundary"]["bad_run2_68_without_public_content_fill"]

    assert_contains(
        generator,
        [
            "run2_68_targeted_debug_rerun_result.json",
            "run2_66_reference_first_design_grammar.json",
            "drawRun269PublicContentFilledSurface",
            "fillRun269SetupOperatingStageSlots",
            "fillRun269InspectableWorkspaceSlots",
            "fillRun269ReleaseDecisionBoardSlots",
            "no_visible_debug_terms",
            "bad_run2_68_without_public_content_fill",
        ],
    )
    assert_contains(
        viewer,
        [
            'LATEST_RUN_PAYLOAD_HINT = \'"latestRunId": "2.72"\'',
            "Run 2.69",
            "ppt-run2-69-prompt-only",
            "ppt-run2-69-run1-5-skill",
            "ppt-run2-69-full-vulca",
            "ppt-run2-69-bad-without-public-content-fill",
            "run2_69_public_content_fill_rerun_result.json",
        ],
    )
