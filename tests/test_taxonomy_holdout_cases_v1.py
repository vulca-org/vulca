import json
from pathlib import Path

from vulca.learning.case_review import CASE_REVIEW_SPECS, load_cases


ROOT = Path(__file__).resolve().parent.parent
CASE_LOG = ROOT / "docs/benchmarks/learning/taxonomy_holdout_cases_v1.synthetic_reviewed.jsonl"
COMBINED_MANIFEST = ROOT / "docs/benchmarks/learning/combined_case_source_manifest_v1.json"

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

    assert report["dataset"]["example_count"] == 43
    assert report["effectiveness"]["gate_passed"] is True
    assert report["effectiveness"]["evaluated_policy"] == "tiny_action_model_v1"
    assert report["effectiveness"]["action_accuracy"] == 1.0
    assert report["data_gaps"] == []
    assert report["status"] == "passed"

    failure_type_coverage = report["coverage"]["failure_type"]
    for failure_type in TARGET_HOLDOUT_FAILURES:
        assert failure_type_coverage[failure_type]["eval_example_count"] >= 1
