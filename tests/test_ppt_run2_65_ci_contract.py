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


def test_run2_65_static_contract_is_ci_visible() -> None:
    generator = (
        ROOT / "scripts" / "generate_ppt_run2_65_renderer_composition_arms.mjs"
    ).read_text(encoding="utf-8")
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    result = load_json(PACK / "results" / "run2_65_renderer_composition_rerun_result.json")
    result_md = (PACK / "results" / "run2_65_renderer_composition_rerun_result.md").read_text(
        encoding="utf-8"
    )

    assert result["run_id"] == "2.65"
    assert result["source_repair_run_id"] == "2.64"
    assert result["source_generated_run_id"] == "2.62"
    assert result["quality_delta"]["target_layer"] == "run2_64_renderer_composition_repair_consumed"
    assert result["quality_delta"]["full_slides_with_run2_64_contracts"] == 6
    assert result["quality_delta"]["full_slides_with_dynamic_sockets"] == 6
    assert result["quality_delta"]["full_slides_with_semantic_diagrams"] == 6
    assert result["quality_delta"]["bad_control_slides_without_run2_64_contracts"] == 6

    assert_contains(
        generator,
        [
            "run2_64_dynamic_socket_renderer_memory.json",
            "run2_64_semantic_diagram_renderer_memory.json",
            "run2_64_text_fit_renderer_gates.json",
            "run2_64_renderer_dry_run_binding_matrix.json",
            "validateRun265RendererInputs",
            "drawRun265RendererCompositionRepair",
            "run2_64_renderer_composition_repair_consumed_before_native_ppt_drawing",
            "bad_run2_64_without_renderer_composition_repair",
        ],
    )
    assert_contains(
        viewer,
        [
            'LATEST_RUN_PAYLOAD_HINT = \'"latestRunId": "2.72"\'',
            "Run 2.65",
            "ppt-run2-65-prompt-only",
            "ppt-run2-65-run1-5-skill",
            "ppt-run2-65-full-vulca",
            "ppt-run2-65-bad-without-renderer-composition-repair",
            "run2_65_renderer_composition_rerun_result.json",
        ],
    )
    assert_contains(
        result_md,
        [
            "Run 2.65 Renderer Composition Rerun",
            "consumes Run 2.64",
            "dynamic socket",
            "semantic diagram",
            "text-fit",
            "Do not advance to Run 3.0",
        ],
    )
