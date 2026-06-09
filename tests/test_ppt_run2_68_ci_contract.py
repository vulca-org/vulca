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


def test_run2_68_static_debug_contract_is_ci_visible() -> None:
    generator = (ROOT / "scripts" / "generate_ppt_run2_68_targeted_debug_arms.mjs").read_text(
        encoding="utf-8"
    )
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    result = load_json(PACK / "results" / "run2_68_targeted_debug_rerun_result.json")

    assert result["run_id"] == "2.68"
    assert result["source_generated_run_id"] == "2.67"
    assert result["source_design_run_id"] == "2.66"
    assert result["debug_scope"]["targeted_roles"] == ["setup", "proof", "close"]
    assert result["quality_delta"]["target_layer"] == "run2_67_targeted_renderer_debug_repair"
    assert result["quality_delta"]["targeted_debug_roles_fixed"] == 3
    assert result["quality_delta"]["full_slides_with_text_overlap_risk_removed"] == 6
    assert result["quality_delta"]["full_slides_with_debug_renderer_modules"] == 3
    assert result["control_boundary"]["bad_run2_67_without_targeted_debug_repair"]

    assert_contains(
        generator,
        [
            "run2_67_reference_first_rerun_result.json",
            "run2_66_reference_first_design_grammar.json",
            "drawRun268LayeredOperatingStageDebug",
            "drawRun268InspectableWorkspaceDebug",
            "drawRun268ReleaseDecisionBoardDebug",
            "text_overlap_risk_removed",
            "bad_run2_67_without_targeted_debug_repair",
        ],
    )
    assert_contains(
        viewer,
        [
            'LATEST_RUN_PAYLOAD_HINT = \'"latestRunId": "2.70"\'',
            "Run 2.68",
            "ppt-run2-68-prompt-only",
            "ppt-run2-68-run1-5-skill",
            "ppt-run2-68-full-vulca",
            "ppt-run2-68-bad-without-targeted-debug",
            "run2_68_targeted_debug_rerun_result.json",
        ],
    )

