import json
from pathlib import Path

from vulca.learning.case_review import CASE_REVIEW_SPECS, load_cases


ROOT = Path(__file__).resolve().parent.parent
CASE_LOG = ROOT / "docs/benchmarks/learning/backlog_manual_cases_v1.reviewed.jsonl"
MANIFEST = ROOT / "docs/benchmarks/learning/backlog_manual_case_source_manifest_v1.json"
COMBINED_MANIFEST = ROOT / "docs/benchmarks/learning/combined_case_source_manifest_v1.json"
SOURCE_PACKET_DIR = ROOT / "docs/benchmarks/learning/manual_source_context_sources_v1"

EXPECTED_BUCKETS = {
    ("decompose_case", "occlusion", "fallback_to_agent"),
    ("decompose_case", "over_segmentation", "merge_layers"),
    ("decompose_case", "under_segmentation", "split_layer_further"),
    ("layer_generate_case", "prompt_ambiguity", "manual_review"),
    ("layer_generate_case", "layer_order", "manual_review"),
    ("layer_generate_case", "provider_failure", "fallback_to_agent"),
    ("layer_generate_case", "style_drift", "adjust_prompt"),
}


def test_backlog_manual_case_pack_v1_manifest_and_reviews():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cases = load_cases(CASE_LOG)

    assert manifest == {
        "schema_version": 1,
        "case_type": "learning_tiny_case_source_manifest",
        "sources": [
            {
                "source_id": "backlog_manual_cases_v1",
                "kind": "manual_case_log",
                "path": "backlog_manual_cases_v1.reviewed.jsonl",
                "privacy_scope": "project",
                "curation_status": "curated",
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
    assert sum(1 for item in cases if item["case_type"] == "decompose_case") == 3
    assert sum(1 for item in cases if item["case_type"] == "layer_generate_case") == 4

    for record in cases:
        review = record["review"]
        spec = CASE_REVIEW_SPECS[record["case_type"]]
        assert review["human_accept"] is False
        assert spec.validate_failure_type(review["failure_type"]) == review["failure_type"]
        assert spec.validate_preferred_action(review["preferred_action"]) == review[
            "preferred_action"
        ]
        assert review["reviewer"] == "backlog_manual_cases_v1"
        assert review["reviewed_at"] == "2026-05-06T00:00:00Z"

    serialized = MANIFEST.read_text(encoding="utf-8") + CASE_LOG.read_text(encoding="utf-8")
    assert "/Users/" not in serialized
    assert "private://local_path" not in serialized


def test_backlog_manual_case_pack_v1_exports_tiny_dataset(tmp_path):
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
    assert {item["source"]["kind"] for item in records} == {"manual_case_log"}
    assert {item["source"]["source_id"] for item in records} == {"backlog_manual_cases_v1"}


def test_combined_manifest_includes_backlog_manual_pack():
    manifest = json.loads(COMBINED_MANIFEST.read_text(encoding="utf-8"))

    assert {
        source["source_id"]
        for source in manifest["sources"]
    } == {
        "manual_curated_cases_v1",
        "real_user_cases_v1",
        "real_user_cases_v2",
        "taxonomy_holdout_cases_v1",
        "backlog_manual_cases_v1",
    }


def test_combined_dataset_includes_backlog_manual_pack(tmp_path):
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
        if item["source"].get("source_id") == "backlog_manual_cases_v1"
    ) == 7
    assert sum(1 for item in records if item["source"]["kind"] == "manual_case_log") == 15


def test_backlog_under_segmentation_case_has_reviewed_source_context_packet():
    cases = load_cases(CASE_LOG)
    record = next(
        item
        for item in cases
        if item["case_id"] == "backlog_manual_v1_decompose_under_segmentation"
    )

    source_refs = record["source_refs"]
    assert source_refs == {
        "source_brief_path": (
            "docs/benchmarks/learning/manual_source_context_sources_v1/"
            "backlog_manual_v1_decompose_under_segmentation.md"
        )
    }
    packet_path = ROOT / source_refs["source_brief_path"]
    assert packet_path.exists()
    assert packet_path.parent == SOURCE_PACKET_DIR
    packet_text = packet_path.read_text(encoding="utf-8")
    assert "backlog_manual_v1_decompose_under_segmentation" in packet_text
    assert "semantic_path" in packet_text
    assert "multi_instance" in packet_text
    assert "/Users/" not in packet_text
    assert "private://local_path" not in packet_text
