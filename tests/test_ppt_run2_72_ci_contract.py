from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_contains(text: str, terms: list[str]) -> None:
    missing = [term for term in terms if term not in text]
    assert not missing, f"missing terms: {missing}"


def test_run2_72_static_shape_bound_text_contract_is_ci_visible() -> None:
    script = (ROOT / "scripts" / "generate_ppt_run2_72_shape_bound_text_arms.mjs").read_text(
        encoding="utf-8"
    )
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    result = load_json(PACK / "results" / "run2_72_shape_bound_text_rerun_result.json")
    assert result["run_id"] == "2.72"
    assert result["source_generated_run_id"] == "2.71"
    assert result["source_design_run_id"] == "2.66"
    assert result["shape_bound_text_scope"]["target_roles"] == ["contrast", "proof", "climax"]
    assert result["quality_delta"]["target_layer"] == "run2_72_shape_bound_text_geometry"
    assert result["quality_delta"]["full_targeted_slides_with_shape_bound_text"] == 3
    assert result["quality_delta"]["full_targeted_slides_with_binding_geometry_records"] == 3
    assert result["quality_delta"]["full_targeted_slides_with_text_inside_component_bounds"] == 3
    assert result["quality_delta"]["full_targeted_slides_with_zero_unbound_component_labels"] == 3
    assert result["quality_delta"]["bad_control_targeted_slides_without_shape_bound_text"] == 3
    assert result["control_boundary"]["bad_run2_72_without_shape_bound_text"]

    assert_contains(
        script,
        [
            "run2_71_component_semantics_rerun_result.json",
            "drawRun272ShapeBoundTextSurface",
            "drawRun272BoundComponentLabel",
            "registerRun272ShapeBoundText",
            "assertRun272TextInsideComponentBounds",
            "shape_bound_text_geometry",
            "bad_run2_72_without_shape_bound_text",
        ],
    )

    assert_contains(
        viewer,
        [
            'LATEST_RUN_PAYLOAD_HINT = \'"latestRunId": "2.72"\'',
            "Run 2.72",
            "ppt-run2-72-full-vulca",
            "ppt-run2-72-bad-without-shape-bound-text",
            "run2-72-four-arm-contact-sheet.png",
            "run2_72_shape_bound_text_rerun_result.json",
            '"latestRunId": "2.72"',
        ],
    )
