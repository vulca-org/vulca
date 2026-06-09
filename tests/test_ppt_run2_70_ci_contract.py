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


def test_run2_70_static_high_fidelity_mock_content_contract_is_ci_visible() -> None:
    generator = (
        ROOT / "scripts" / "generate_ppt_run2_70_high_fidelity_mock_content_arms.mjs"
    ).read_text(encoding="utf-8")
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    result = load_json(PACK / "results" / "run2_70_high_fidelity_mock_content_rerun_result.json")

    assert result["run_id"] == "2.70"
    assert result["source_generated_run_id"] == "2.69"
    assert result["source_design_run_id"] == "2.66"
    assert result["mock_content_scope"]["target_roles"] == ["contrast", "proof", "climax"]
    assert result["mock_content_scope"]["required_mock_surfaces"] == [
        "product_scene_mock",
        "inspectable_generated_slide_mock",
        "editable_presentation_surface_mock",
    ]
    assert result["quality_delta"]["target_layer"] == "run2_69_high_fidelity_product_mock_content"
    assert result["quality_delta"]["full_targeted_slides_with_high_fidelity_mock_content"] == 3
    assert result["quality_delta"]["full_targeted_slides_without_empty_wireframes"] == 3
    assert result["quality_delta"]["full_targeted_slides_with_realistic_mock_objects"] == 3
    assert result["quality_delta"]["bad_control_targeted_slides_without_high_fidelity_mock_content"] == 3
    assert result["control_boundary"]["bad_run2_69_without_high_fidelity_mock_content"]

    assert_contains(
        generator,
        [
            "run2_69_public_content_fill_rerun_result.json",
            "drawRun270HighFidelityProductMockSurface",
            "drawRun270ProductSceneMock",
            "fillRun270InspectableGeneratedSlideMock",
            "fillRun270EditablePresentationSurfaceMock",
            "high_fidelity_mock_content",
            "bad_run2_69_without_high_fidelity_mock_content",
        ],
    )
    assert_contains(
        viewer,
        [
            'LATEST_RUN_PAYLOAD_HINT = \'"latestRunId": "2.72"\'',
            "Run 2.70",
            "ppt-run2-70-prompt-only",
            "ppt-run2-70-run1-5-skill",
            "ppt-run2-70-full-vulca",
            "ppt-run2-70-bad-without-high-fidelity-mock-content",
            "run2_70_high_fidelity_mock_content_rerun_result.json",
        ],
    )
