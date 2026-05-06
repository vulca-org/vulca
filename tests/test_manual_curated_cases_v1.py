import json
from pathlib import Path

from vulca.learning.case_review import CASE_REVIEW_SPECS, load_cases


ROOT = Path(__file__).resolve().parent.parent
CASE_LOG = ROOT / "docs/benchmarks/learning/manual_curated_cases_v1.reviewed.jsonl"
MANIFEST = ROOT / "docs/benchmarks/learning/manual_curated_case_source_manifest_v1.json"

EXPECTED_FAILURE_TAXONOMY = {
    "pasteback_mismatch",
    "mask_leak",
    "style_drift",
    "layer_order",
    "occlusion",
    "over_segmentation",
    "under_segmentation",
    "prompt_ambiguity",
}


def test_manual_curated_case_pack_v1_manifest_and_reviews():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cases = load_cases(CASE_LOG)

    assert manifest["schema_version"] == 1
    assert manifest["case_type"] == "learning_tiny_case_source_manifest"
    assert manifest["sources"] == [
        {
            "source_id": "manual_curated_cases_v1",
            "kind": "manual_case_log",
            "path": "manual_curated_cases_v1.reviewed.jsonl",
            "privacy_scope": "project",
            "curation_status": "curated",
        }
    ]

    assert len(cases) == 8
    assert {item["review"]["failure_type"] for item in cases} == EXPECTED_FAILURE_TAXONOMY
    assert {item["case_type"] for item in cases} == {
        "redraw_case",
        "layer_generate_case",
        "decompose_case",
    }
    assert sum(1 for item in cases if item["case_type"] == "redraw_case") == 2
    assert sum(1 for item in cases if item["case_type"] == "layer_generate_case") == 3
    assert sum(1 for item in cases if item["case_type"] == "decompose_case") == 3

    for record in cases:
        review = record["review"]
        spec = CASE_REVIEW_SPECS[record["case_type"]]
        assert review["human_accept"] is False
        assert spec.validate_failure_type(review["failure_type"]) == review["failure_type"]
        assert spec.validate_preferred_action(review["preferred_action"]) == review[
            "preferred_action"
        ]
        assert review["reviewer"] == "manual_curated_cases_v1"
        assert review["reviewed_at"] == "2026-05-06T00:00:00Z"

    serialized = MANIFEST.read_text(encoding="utf-8") + CASE_LOG.read_text(encoding="utf-8")
    assert "real_brief" not in serialized
    assert "seattle" not in serialized.lower()


def test_manual_curated_case_pack_v1_exports_tiny_dataset(tmp_path):
    from vulca.learning.tiny_dataset import write_tiny_dataset

    output_path = tmp_path / "tiny_dataset.jsonl"
    result = write_tiny_dataset(
        repo_root=ROOT,
        output_path=output_path,
        include_local_seeds=False,
        case_source_manifest_path=MANIFEST,
    )

    assert result.example_count == 8
    assert result.counts_by_case_type == {
        "decompose_case": 3,
        "layer_generate_case": 3,
        "redraw_case": 2,
    }
    records = load_cases(output_path)
    assert {item["targets"]["failure_type"] for item in records} == EXPECTED_FAILURE_TAXONOMY
    assert {item["source"]["kind"] for item in records} == {"manual_case_log"}
    assert {item["source"]["privacy_scope"] for item in records} == {"project"}
    assert {item["source"]["curation_status"] for item in records} == {"curated"}
