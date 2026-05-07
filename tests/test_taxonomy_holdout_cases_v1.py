import json
from pathlib import Path

from vulca.learning.case_review import CASE_REVIEW_SPECS, load_cases


ROOT = Path(__file__).resolve().parent.parent
CASE_LOG = ROOT / "docs/benchmarks/learning/taxonomy_holdout_cases_v1.synthetic_reviewed.jsonl"
COMBINED_MANIFEST = ROOT / "docs/benchmarks/learning/combined_case_source_manifest_v1.json"
SOURCE_PACKET_DIR = ROOT / "docs/benchmarks/learning/synthetic_source_context_sources_v1"

TARGET_HOLDOUT_FAILURES = {
    "color_drift",
    "layer_order",
    "mask_leak",
    "mask_too_broad",
    "missing_detail",
    "occlusion",
    "over_segmentation",
    "pasteback_mismatch",
    "provider_failure",
    "style_drift",
    "under_split",
}

EXPECTED_SYNTHETIC_SOURCE_PACKET_CASES = {
    "taxonomy_v1_decompose_occlusion_holdout",
    "taxonomy_v1_decompose_over_segmentation_holdout",
    "taxonomy_v1_layer_generate_layer_order_holdout",
    "taxonomy_v1_layer_generate_style_drift_holdout",
    "taxonomy_v1_redraw_color_drift_holdout",
    "taxonomy_v1_redraw_mask_leak_holdout",
    "taxonomy_v1_redraw_mask_too_broad_holdout",
    "taxonomy_v1_redraw_missing_detail_holdout",
    "taxonomy_v1_redraw_pasteback_mismatch_holdout",
    "taxonomy_v1_redraw_under_split_holdout",
}


def test_taxonomy_holdout_case_pack_v1_is_manifested_and_valid():
    cases = load_cases(CASE_LOG)
    manifest = json.loads(COMBINED_MANIFEST.read_text(encoding="utf-8"))

    assert len(cases) == 11
    assert {item["review"]["failure_type"] for item in cases} == TARGET_HOLDOUT_FAILURES
    assert {
        item["source_id"]
        for item in manifest["sources"]
        if item["source_id"] == "taxonomy_holdout_cases_v1"
    } == {"taxonomy_holdout_cases_v1"}

    for record in cases:
        review = record["review"]
        spec = CASE_REVIEW_SPECS[record["case_type"]]
        assert review["human_accept"] is False
        assert spec.validate_failure_type(review["failure_type"]) == review["failure_type"]
        assert spec.validate_preferred_action(review["preferred_action"]) == review[
            "preferred_action"
        ]
        assert review["reviewer"] == "taxonomy_holdout_cases_v1"
        assert review["reviewed_at"] == "2026-05-06T00:00:00Z"

    serialized = CASE_LOG.read_text(encoding="utf-8")
    assert "private://local_path" not in serialized
    assert "/Users/" not in serialized


def test_combined_training_effectiveness_has_failure_type_holdout_coverage(tmp_path):
    from vulca.learning.training_effectiveness import run_training_effectiveness_report

    report = run_training_effectiveness_report(
        repo_root=ROOT,
        output_dir=tmp_path / "training_effectiveness",
        report_path=tmp_path / "training_effectiveness_report.json",
    )

    assert report["dataset"]["example_count"] == 50
    assert report["effectiveness"]["gate_passed"] is True
    assert report["effectiveness"]["evaluated_policy"] == "tiny_action_model_v1"
    assert report["effectiveness"]["action_accuracy"] == 1.0
    assert report["data_gaps"] == []
    assert report["status"] == "passed"

    failure_type_coverage = report["coverage"]["failure_type"]
    for failure_type in TARGET_HOLDOUT_FAILURES:
        assert failure_type_coverage[failure_type]["eval_example_count"] >= 1


def test_taxonomy_holdout_source_context_packets_cover_synthetic_router_gaps():
    cases = load_cases(CASE_LOG)
    records_by_id = {item["case_id"]: item for item in cases}

    assert EXPECTED_SYNTHETIC_SOURCE_PACKET_CASES <= set(records_by_id)
    for case_id in EXPECTED_SYNTHETIC_SOURCE_PACKET_CASES:
        source_refs = records_by_id[case_id]["source_refs"]
        assert source_refs == {
            "source_brief_path": (
                f"docs/benchmarks/learning/synthetic_source_context_sources_v1/"
                f"{case_id}.md"
            )
        }
        packet_path = ROOT / source_refs["source_brief_path"]
        assert packet_path.exists()
        assert packet_path.parent == SOURCE_PACKET_DIR
        packet_text = packet_path.read_text(encoding="utf-8")
        assert case_id in packet_text
        assert "semantic_path" in packet_text
        assert "/Users/" not in packet_text
        assert "private://local_path" not in packet_text
