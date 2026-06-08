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


def test_run2_61_static_contract_is_ci_visible() -> None:
    script = (ROOT / "scripts" / "build_ppt_run2_61_narrative_proof_dataset.py").read_text(
        encoding="utf-8"
    )
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    result = load_json(PACK / "results" / "run2_61_narrative_proof_dataset_result.json")
    result_md = (PACK / "results" / "run2_61_narrative_proof_dataset_result.md").read_text(
        encoding="utf-8"
    )

    assert result["run_id"] == "2.61"
    assert result["source_generated_run_id"] == "2.60"
    assert result["generation_boundary"]["creates_new_ppt_deck"] is False
    assert result["next_required_action"] == "run2_62_generate_four_arm_ppt_consuming_run2_61_narrative_proof_dataset"
    assert result["quality_delta"]["target_layer"] == "narrative_proof_dataset_and_socket_fusion"
    assert result["quality_delta"]["roles_with_narrative_proof_records"] == 6
    assert result["quality_delta"]["roles_with_visual_carrier_selection"] == 6
    assert result["quality_delta"]["roles_with_socket_fusion_contracts"] == 6

    assert_contains(
        script,
        [
            "run2_8_tutorial_decomposition.json",
            "run2_12_thick_multimodal_evidence.json",
            "run2_18_multimodal_evidence_expansion.json",
            "run2_15_layout_module_memory.json",
            "run2_51_shape_text_socket_memory.json",
            "run2_57_slide_message_contracts.json",
            "run2_59_content_composition_contracts.json",
            "run2_59_content_to_layout_selector.json",
            "run2_61_narrative_proof_dataset.json",
            "run2_61_story_to_visual_carrier_selector.json",
            "run2_61_text_socket_fusion_contracts.json",
            "run2_61_source_to_public_proof_policy.json",
            "run2_61_narrative_workflow_gates.json",
            "run2_62_generate_four_arm_ppt_consuming_run2_61_narrative_proof_dataset",
        ],
    )
    assert_contains(
        viewer,
        [
            'LATEST_RUN_PAYLOAD_HINT = \'"latestRunId": "2.68"\'',
            "Run 2.61 narrative proof dataset",
            "run2_61_narrative_proof_dataset.json",
            "run2_61_story_to_visual_carrier_selector.json",
            "run2_61_text_socket_fusion_contracts.json",
            "run2_61_source_to_public_proof_policy.json",
            "run2_61_narrative_workflow_gates.json",
            "run2_62_generate_four_arm_ppt_consuming_run2_61_narrative_proof_dataset",
        ],
    )
    assert_contains(
        result_md,
        [
            "Run 2.61 Narrative Proof Dataset",
            "does not generate a new PPT deck",
            "reader question",
            "visual carrier",
            "text socket fusion",
            "public proof replacement",
            "Do not advance to Run 3.0",
        ],
    )
