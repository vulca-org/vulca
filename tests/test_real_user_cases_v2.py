import json
from collections import Counter
from pathlib import Path

from vulca.learning.case_review import CASE_REVIEW_SPECS, load_cases


ROOT = Path(__file__).resolve().parent.parent
CASE_LOG = ROOT / "docs/benchmarks/learning/real_user_cases_v2.private.user_cases.jsonl"
MANIFEST = ROOT / "docs/benchmarks/learning/real_user_case_source_manifest_v2.json"
COMBINED_MANIFEST = ROOT / "docs/benchmarks/learning/combined_case_source_manifest_v1.json"

EXPECTED_BUCKETS = {
    ("decompose_case", "occlusion", "fallback_to_agent"),
    ("decompose_case", "over_segmentation", "merge_layers"),
    ("decompose_case", "under_segmentation", "split_layer_further"),
    ("layer_generate_case", "prompt_ambiguity", "manual_review"),
    ("layer_generate_case", "layer_order", "manual_review"),
    ("layer_generate_case", "provider_failure", "fallback_to_agent"),
    ("layer_generate_case", "style_drift", "adjust_prompt"),
}


def test_real_user_case_pack_v2_manifest_and_reviews():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cases = load_cases(CASE_LOG)

    assert manifest == {
        "schema_version": 1,
        "case_type": "learning_tiny_case_source_manifest",
        "sources": [
            {
                "source_id": "real_user_cases_v2",
                "kind": "user_case_log",
                "path": "real_user_cases_v2.private.user_cases.jsonl",
                "privacy_scope": "private",
                "curation_status": "reviewed",
            }
        ],
    }
    assert len(cases) == 7
    assert {
        (
            item["case_type"],
            item["review"]["failure_type"],
            item["review"]["preferred_action"],
        )
        for item in cases
    } == EXPECTED_BUCKETS
    assert Counter(item["case_type"] for item in cases) == {
        "decompose_case": 3,
        "layer_generate_case": 4,
    }

    for index, record in enumerate(cases):
        review = record["review"]
        spec = CASE_REVIEW_SPECS[record["case_type"]]
        assert review["human_accept"] is False
        assert spec.validate_failure_type(review["failure_type"]) == review["failure_type"]
        assert spec.validate_preferred_action(review["preferred_action"]) == review[
            "preferred_action"
        ]
        assert review["reviewer"] == "real_user_cases_v2"
        assert review["reviewed_at"] == "2026-05-06T00:00:00Z"
        assert record["user_case_intake"] == {
            "schema_version": 1,
            "source_id": "real_user_cases_v2",
            "privacy_scope": "private",
            "curation_status": "reviewed",
            "record_index": index,
        }

    serialized = MANIFEST.read_text(encoding="utf-8") + CASE_LOG.read_text(encoding="utf-8")
    assert "/Users/" not in serialized
    assert "@example.com" not in serialized
    assert "private://local_path/" in serialized


def test_real_user_case_pack_v2_exports_tiny_dataset(tmp_path):
    from vulca.learning.tiny_dataset import write_tiny_dataset

    output_path = tmp_path / "tiny_dataset.jsonl"
    result = write_tiny_dataset(
        repo_root=ROOT,
        output_path=output_path,
        include_local_seeds=False,
        case_source_manifest_path=MANIFEST,
    )

    assert result.example_count == 7
    assert result.counts_by_case_type == {
        "decompose_case": 3,
        "layer_generate_case": 4,
    }
    records = load_cases(output_path)
    assert {
        (
            item["source_case"]["case_type"],
            item["targets"]["failure_type"],
            item["targets"]["preferred_action"],
        )
        for item in records
    } == EXPECTED_BUCKETS
    assert {item["source"]["source_id"] for item in records} == {"real_user_cases_v2"}
    assert {item["source"]["kind"] for item in records} == {"user_case_log"}
    assert {item["source"]["privacy_scope"] for item in records} == {"private"}
    encoded_inputs = json.dumps([item["input"] for item in records], sort_keys=True)
    assert '"review"' not in encoded_inputs
    assert '"learning_targets"' not in encoded_inputs


def test_combined_manifest_includes_real_user_case_pack_v2():
    manifest = json.loads(COMBINED_MANIFEST.read_text(encoding="utf-8"))

    assert {
        source["source_id"]
        for source in manifest["sources"]
    } == {
        "manual_curated_cases_v1",
        "real_user_cases_v1",
        "taxonomy_holdout_cases_v1",
        "backlog_manual_cases_v1",
        "real_user_cases_v2",
    }


def test_combined_dataset_includes_real_user_case_pack_v2(tmp_path):
    from vulca.learning.tiny_dataset import write_tiny_dataset

    output_path = tmp_path / "tiny_dataset.jsonl"
    result = write_tiny_dataset(
        repo_root=ROOT,
        output_path=output_path,
        include_local_seeds=True,
        case_source_manifest_path=COMBINED_MANIFEST,
    )

    assert result.example_count == 50
    assert result.counts_by_case_type == {
        "decompose_case": 12,
        "layer_generate_case": 23,
        "redraw_case": 15,
    }
    records = load_cases(output_path)
    assert sum(
        1
        for item in records
        if item["source"].get("source_id") == "real_user_cases_v2"
    ) == 7
    assert sum(1 for item in records if item["source"]["kind"] == "user_case_log") == 12
