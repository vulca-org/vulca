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


def test_run2_60_static_contract_is_ci_visible() -> None:
    generator = (ROOT / "scripts" / "generate_ppt_run2_60_content_aware_composition_arms.mjs").read_text(
        encoding="utf-8"
    )
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    result = load_json(PACK / "results" / "run2_60_content_aware_composition_rerun_result.json")
    result_md = (PACK / "results" / "run2_60_content_aware_composition_rerun_result.md").read_text(
        encoding="utf-8"
    )

    assert result["run_id"] == "2.60"
    assert result["source_repair_run_id"] == "2.59"
    assert result["source_generated_run_id"] == "2.58"
    assert result["quality_delta"]["target_layer"] == "content_aware_composition_compiler_consumed"
    assert result["quality_delta"]["source_data_status"] == (
        "run2_59_composition_compiler_consumed_before_native_ppt_drawing"
    )
    assert result["quality_delta"]["full_slides_with_run2_59_content_contracts"] == 6
    assert result["quality_delta"]["bad_control_slides_without_run2_59_compiler"] == 6

    assert_contains(
        generator,
        [
            "run2_59_content_composition_contracts.json",
            "run2_59_layout_capacity_model.json",
            "run2_59_content_to_layout_selector.json",
            "run2_59_public_surface_trace_policy.json",
            "run2_59_composition_workflow_gates.json",
            "run2_58_product_content_contract_rerun_result.json",
            "ppt-run2-58-full-vulca/trace_manifest.json",
            "drawRun260ContentAwareComposition",
            "drawRun260EditorialCoverField",
            "drawRun260ProductTheaterStage",
            "drawRun260BeforeAfterRoute",
            "drawRun260DenseEvidenceCompression",
            "drawRun260MetricRevealStage",
            "drawRun260QuietReleaseHandoff",
            "bad_run2_58_without_run2_59_composition_compiler",
            "public_visible_word_budget_exceeds_selected_layout_capacity",
            "Run 2.60 must consume Run 2.59 content composition contracts",
            "Run 2.60 must compare against Run 2.58 full trace",
        ],
    )
    assert_contains(
        viewer,
        [
            'LATEST_RUN_PAYLOAD_HINT = \'"latestRunId": "2.62"\'',
            "Run 2.60",
            "ppt-run2-60-prompt-only",
            "ppt-run2-60-run1-5-skill",
            "ppt-run2-60-full-vulca",
            "ppt-run2-60-bad-without-composition-compiler",
            "run2_60_content_aware_composition_rerun_result.json",
            "Run 2.60 generated result",
            "content-aware composition compiler consumed",
        ],
    )
    assert_contains(
        result_md,
        [
            "Run 2.60 Content-Aware Composition Rerun",
            "consumes Run 2.59",
            "layout capacity model",
            "content-to-layout selector",
            "public slide / trace viewer split",
            "Do not advance to Run 3.0",
        ],
    )
