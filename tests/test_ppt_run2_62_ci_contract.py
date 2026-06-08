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


def test_run2_62_static_contract_is_ci_visible() -> None:
    generator = (ROOT / "scripts" / "generate_ppt_run2_62_narrative_proof_arms.mjs").read_text(
        encoding="utf-8"
    )
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    result = load_json(PACK / "results" / "run2_62_narrative_proof_rerun_result.json")
    result_md = (PACK / "results" / "run2_62_narrative_proof_rerun_result.md").read_text(
        encoding="utf-8"
    )

    assert result["run_id"] == "2.62"
    assert result["source_repair_run_id"] == "2.61"
    assert result["source_generated_run_id"] == "2.60"
    assert result["quality_delta"]["target_layer"] == "run2_61_narrative_proof_dataset_consumed"
    assert result["quality_delta"]["full_slides_with_run2_61_contracts"] == 6
    assert result["quality_delta"]["full_slides_with_socket_bindings"] == 6
    assert result["quality_delta"]["bad_control_slides_without_run2_61_contracts"] == 6

    assert_contains(
        generator,
        [
            "run2_61_narrative_proof_dataset.json",
            "run2_61_story_to_visual_carrier_selector.json",
            "run2_61_text_socket_fusion_contracts.json",
            "run2_61_source_to_public_proof_policy.json",
            "run2_61_narrative_workflow_gates.json",
            "run2_60_content_aware_composition_rerun_result.json",
            "ppt-run2-60-full-vulca/trace_manifest.json",
            "validateRun262NarrativeInputs",
            "Run 2.62 must consume Run 2.61 narrative proof dataset",
            "Run 2.62 must compare against Run 2.60 full trace",
            "drawRun262NarrativeProofComposition",
            "run2_61_narrative_proof_dataset_consumed_before_native_ppt_drawing",
            "bad_run2_60_without_run2_61_narrative_proof_dataset",
        ],
    )
    assert_contains(
        viewer,
        [
            'LATEST_RUN_PAYLOAD_HINT = \'"latestRunId": "2.65"\'',
            "Run 2.62",
            "ppt-run2-62-prompt-only",
            "ppt-run2-62-run1-5-skill",
            "ppt-run2-62-full-vulca",
            "ppt-run2-62-bad-without-narrative-proof",
            "run2_62_narrative_proof_rerun_result.json",
            "Run 2.62 generated narrative proof consumption",
        ],
    )
    assert_contains(
        result_md,
        [
            "Run 2.62 Narrative Proof Rerun",
            "consumes Run 2.61",
            "narrative proof dataset",
            "text socket fusion",
            "public proof replacement",
            "Do not advance to Run 3.0",
        ],
    )
