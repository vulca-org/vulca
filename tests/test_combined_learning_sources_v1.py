import json
from pathlib import Path

from vulca.learning.case_review import load_cases


ROOT = Path(__file__).resolve().parent.parent
COMBINED_MANIFEST = ROOT / "docs/benchmarks/learning/combined_case_source_manifest_v1.json"


def test_combined_case_source_manifest_v1_keeps_sources_explicit():
    manifest = json.loads(COMBINED_MANIFEST.read_text(encoding="utf-8"))

    assert manifest == {
        "schema_version": 1,
        "case_type": "learning_tiny_case_source_manifest",
        "sources": [
            {
                "source_id": "manual_curated_cases_v1",
                "kind": "manual_case_log",
                "path": "manual_curated_cases_v1.reviewed.jsonl",
                "privacy_scope": "project",
                "curation_status": "curated",
            },
            {
                "source_id": "real_user_cases_v1",
                "kind": "user_case_log",
                "path": "real_user_cases_v1.private.user_cases.jsonl",
                "privacy_scope": "private",
                "curation_status": "reviewed",
            },
            {
                "source_id": "taxonomy_holdout_cases_v1",
                "kind": "synthetic_case_log",
                "path": "taxonomy_holdout_cases_v1.synthetic_reviewed.jsonl",
                "privacy_scope": "project",
                "curation_status": "synthetic_reviewed",
                "preferred_split": "test",
            },
            {
                "source_id": "backlog_manual_cases_v1",
                "kind": "manual_case_log",
                "path": "backlog_manual_cases_v1.reviewed.jsonl",
                "privacy_scope": "project",
                "curation_status": "curated",
            },
            {
                "source_id": "real_user_cases_v2",
                "kind": "user_case_log",
                "path": "real_user_cases_v2.private.user_cases.jsonl",
                "privacy_scope": "private",
                "curation_status": "reviewed",
            },
        ],
    }
    serialized = COMBINED_MANIFEST.read_text(encoding="utf-8")
    assert "external_dataset_catalog_v1" not in serialized
    assert "/Users/" not in serialized


def test_combined_case_source_manifest_v1_exports_50_example_training_eval_set(tmp_path):
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
    assert result.counts_by_split == {
        "dev": 9,
        "test": 21,
        "train": 20,
    }

    records = load_cases(output_path)
    assert sum(1 for item in records if item["source"]["kind"] == "local_seed") == 12
    assert sum(1 for item in records if item["source"]["kind"] == "manual_case_log") == 15
    assert sum(1 for item in records if item["source"]["kind"] == "user_case_log") == 12
    assert sum(1 for item in records if item["source"]["kind"] == "synthetic_case_log") == 11
    assert any(
        item["split"] == "test" and item["source"]["kind"] == "user_case_log"
        for item in records
    )
    assert {
        item["split"]
        for item in records
        if item["source"].get("source_id") == "taxonomy_holdout_cases_v1"
    } == {"test"}
    assert {
        item["source"].get("source_id")
        for item in records
        if item["source"]["kind"] != "local_seed"
    } == {
        "backlog_manual_cases_v1",
        "manual_curated_cases_v1",
        "real_user_cases_v1",
        "real_user_cases_v2",
        "taxonomy_holdout_cases_v1",
    }

    index = json.loads(Path(result.index_path).read_text(encoding="utf-8"))
    assert index["counts_by_source"] == {
        "local_seed": 12,
        "manual_case_log": 15,
        "synthetic_case_log": 11,
        "user_case_log": 12,
    }


def test_combined_case_source_manifest_v1_runs_aggregated_eval_gate(tmp_path):
    from vulca.learning.aggregated_case_source_eval import run_aggregated_case_source_eval

    report = run_aggregated_case_source_eval(
        repo_root=ROOT,
        output_dir=tmp_path / "aggregated",
        case_source_manifest_paths=[COMBINED_MANIFEST],
        include_default_case_source_manifest=False,
        include_local_seeds=True,
        eval_split="test",
        train_split="train",
    )

    assert report["dataset_summary"]["example_count"] == 50
    assert report["dataset_summary"]["counts_by_split"] == {
        "dev": 9,
        "test": 21,
        "train": 20,
    }
    bucket_metrics = report["bucket_metrics"]
    assert bucket_metrics["source.kind"]["local_seed"]["example_count"] == 12
    assert bucket_metrics["source.kind"]["manual_case_log"]["example_count"] == 15
    assert bucket_metrics["source.kind"]["user_case_log"]["example_count"] == 12
    assert bucket_metrics["source.kind"]["synthetic_case_log"]["example_count"] == 11
    assert bucket_metrics["source.kind"]["local_seed"]["eval_example_count"] == 3
    assert bucket_metrics["source.kind"]["manual_case_log"]["eval_example_count"] == 4
    assert bucket_metrics["source.kind"]["user_case_log"]["eval_example_count"] == 3
    assert bucket_metrics["source.kind"]["synthetic_case_log"]["eval_example_count"] == 11
    assert bucket_metrics["source_id"]["manual_curated_cases_v1"]["example_count"] == 8
    assert bucket_metrics["source_id"]["real_user_cases_v1"]["example_count"] == 5
    assert bucket_metrics["source_id"]["real_user_cases_v2"]["example_count"] == 7
    assert bucket_metrics["source_id"]["taxonomy_holdout_cases_v1"]["example_count"] == 11
    assert bucket_metrics["source_id"]["backlog_manual_cases_v1"]["example_count"] == 7

    policy_reports = report["policy_comparison"]["policy_reports"]
    assert policy_reports["tiny_action_model_v1"]["action_accuracy"] == 1.0
    assert (
        policy_reports["tiny_action_model_v1"]["action_accuracy"]
        >= policy_reports["tiny_agent_v0"]["action_accuracy"]
    )
    assert report["tiny_training_eval"]["gate"]["passed"] is True
