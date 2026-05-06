import json
from collections import Counter
from pathlib import Path

from vulca.learning.case_review import CASE_REVIEW_SPECS, load_cases


ROOT = Path(__file__).resolve().parent.parent
CASE_LOG = ROOT / "docs/benchmarks/learning/real_user_cases_v1.private.user_cases.jsonl"
MANIFEST = ROOT / "docs/benchmarks/learning/real_user_case_source_manifest_v1.json"

EXPECTED_CASE_IDS = {
    "real_v1_seattle_polish_film_festival_brief",
    "real_v1_scottish_chinese_additive_gongbi_reject",
    "real_v1_ipad_cartoon_provider_failure",
    "real_v1_spring_festival_gongbi_brief_accept",
    "real_v1_winter_solstice_tang_mural_registry_gap",
}


def test_real_user_case_pack_v1_manifest_and_reviews():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cases = load_cases(CASE_LOG)

    assert manifest == {
        "schema_version": 1,
        "case_type": "learning_tiny_case_source_manifest",
        "sources": [
            {
                "source_id": "real_user_cases_v1",
                "kind": "user_case_log",
                "path": "real_user_cases_v1.private.user_cases.jsonl",
                "privacy_scope": "private",
                "curation_status": "reviewed",
            }
        ],
    }

    assert len(cases) == 5
    assert {item["case_id"] for item in cases} == EXPECTED_CASE_IDS
    assert Counter(item["case_type"] for item in cases) == {
        "layer_generate_case": 4,
        "redraw_case": 1,
    }

    for index, record in enumerate(cases):
        review = record["review"]
        spec = CASE_REVIEW_SPECS[record["case_type"]]
        assert spec.validate_failure_type(review["failure_type"]) == review["failure_type"]
        assert spec.validate_preferred_action(review["preferred_action"]) == review[
            "preferred_action"
        ]
        assert review["reviewer"] == "real_user_cases_v1"
        assert review["reviewed_at"] == "2026-05-06T00:00:00Z"
        assert record["user_case_intake"] == {
            "schema_version": 1,
            "source_id": "real_user_cases_v1",
            "privacy_scope": "private",
            "curation_status": "reviewed",
            "record_index": index,
        }

    serialized = MANIFEST.read_text(encoding="utf-8") + CASE_LOG.read_text(encoding="utf-8")
    assert "/Users/" not in serialized
    assert "@example.com" not in serialized
    assert "source/IMG_6847.jpg" not in serialized
    assert "private://local_path/" in serialized


def test_real_user_case_pack_v1_exports_tiny_dataset(tmp_path):
    from vulca.learning.tiny_dataset import write_tiny_dataset

    output_path = tmp_path / "tiny_dataset.jsonl"
    result = write_tiny_dataset(
        repo_root=ROOT,
        output_path=output_path,
        include_local_seeds=False,
        case_source_manifest_path=MANIFEST,
    )

    assert result.example_count == 5
    assert result.counts_by_case_type == {
        "layer_generate_case": 4,
        "redraw_case": 1,
    }
    records = load_cases(output_path)
    assert {item["source"]["source_id"] for item in records} == {"real_user_cases_v1"}
    assert {item["source"]["kind"] for item in records} == {"user_case_log"}
    assert {item["source"]["privacy_scope"] for item in records} == {"private"}
    assert {item["source"]["curation_status"] for item in records} == {"reviewed"}
    encoded_inputs = json.dumps([item["input"] for item in records], sort_keys=True)
    assert '"review"' not in encoded_inputs
    assert '"learning_targets"' not in encoded_inputs


def test_real_user_case_pack_v1_participates_in_aggregated_eval(tmp_path):
    from vulca.learning.aggregated_case_source_eval import run_aggregated_case_source_eval

    report = run_aggregated_case_source_eval(
        repo_root=ROOT,
        output_dir=tmp_path / "aggregated",
        case_source_manifest_paths=[MANIFEST],
        include_default_case_source_manifest=False,
        include_local_seeds=False,
        eval_split="test",
        train_split="train",
    )

    assert report["dataset_summary"]["example_count"] == 5
    assert report["bucket_metrics"]["source_id"]["real_user_cases_v1"]["example_count"] == 5
    assert report["bucket_metrics"]["source.kind"]["user_case_log"]["example_count"] == 5
    assert report["bucket_metrics"]["privacy_scope"]["private"]["example_count"] == 5
