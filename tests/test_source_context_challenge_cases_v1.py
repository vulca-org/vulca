import json
from pathlib import Path

from vulca.learning.case_review import CASE_REVIEW_SPECS, load_cases


ROOT = Path(__file__).resolve().parent.parent
LEARNING_DIR = ROOT / "docs/benchmarks/learning"
SOURCE_MANIFEST = LEARNING_DIR / "source_context_challenge_case_source_manifest_v1.json"
TRAIN_CASE_LOG = LEARNING_DIR / "source_context_challenge_cases_v1.train_reviewed.jsonl"
TEST_CASE_LOG = LEARNING_DIR / "source_context_challenge_cases_v1.test_reviewed.jsonl"
SOURCE_DIR = LEARNING_DIR / "source_context_challenge_sources_v1"


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_source_context_challenge_v1_manifest_and_cases_are_safe():
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    train_cases = load_cases(TRAIN_CASE_LOG)
    test_cases = load_cases(TEST_CASE_LOG)
    all_cases = train_cases + test_cases

    assert manifest == {
        "schema_version": 1,
        "case_type": "learning_tiny_case_source_manifest",
        "sources": [
            {
                "source_id": "source_context_challenge_cases_v1_train",
                "kind": "synthetic_case_log",
                "path": "source_context_challenge_cases_v1.train_reviewed.jsonl",
                "privacy_scope": "project",
                "curation_status": "synthetic_reviewed",
                "preferred_split": "train",
            },
            {
                "source_id": "source_context_challenge_cases_v1_test",
                "kind": "synthetic_case_log",
                "path": "source_context_challenge_cases_v1.test_reviewed.jsonl",
                "privacy_scope": "project",
                "curation_status": "synthetic_reviewed",
                "preferred_split": "test",
            },
        ],
    }
    assert len(train_cases) == 4
    assert len(test_cases) == 4
    assert {item["review"]["preferred_action"] for item in train_cases} == {
        "adjust_prompt",
        "manual_review",
    }
    assert {item["review"]["preferred_action"] for item in test_cases} == {
        "adjust_prompt",
        "manual_review",
    }

    for record in all_cases:
        spec = CASE_REVIEW_SPECS[record["case_type"]]
        review = record["review"]
        assert review["failure_type"] == ""
        assert spec.validate_preferred_action(review["preferred_action"]) == review[
            "preferred_action"
        ]
        assert record["quality"] == {"gate_passed": False}
        assert record["decisions"]["fallback_decisions"] == []
        assert "failures" not in record["quality"]

        source_refs = record["source_refs"]
        assert set(source_refs) == {"source_brief_path"}
        source_path = ROOT / source_refs["source_brief_path"]
        assert source_path.is_file()
        assert source_path.parent == SOURCE_DIR

    serialized = SOURCE_MANIFEST.read_text(encoding="utf-8")
    serialized += TRAIN_CASE_LOG.read_text(encoding="utf-8")
    serialized += TEST_CASE_LOG.read_text(encoding="utf-8")
    for source_file in SOURCE_DIR.glob("*.md"):
        serialized += source_file.read_text(encoding="utf-8")
    assert "private://local_path" not in serialized
    assert "/Users/" not in serialized
    assert ".worktrees" not in serialized


def test_source_context_challenge_v1_requires_auxiliary_source_signals(tmp_path):
    from vulca.learning.source_context_signals import write_source_context_signal_pack
    from vulca.learning.tiny_dataset import (
        build_tiny_dataset_examples,
        evaluate_tiny_prediction_records,
    )
    from vulca.learning.tiny_feature_ablation import run_tiny_feature_ablation_report
    from vulca.learning.tiny_action_model import build_tiny_action_model_predictions

    signal_manifest = tmp_path / "source_context_signal_promotion_manifest.json"
    signal_report = write_source_context_signal_pack(
        repo_root=ROOT,
        case_source_manifest_path=SOURCE_MANIFEST,
        output_path=tmp_path / "source_context_signals.promoted.jsonl",
        manifest_path=signal_manifest,
        report_path=tmp_path / "source_context_signal_report.json",
        include_local_seeds=False,
    )
    assert signal_report["summary"] == {
        "example_count": 8,
        "promoted_signal_count": 8,
        "skipped_count": 0,
    }

    signal_records = _jsonl(tmp_path / "source_context_signals.promoted.jsonl")
    tags_by_case = {
        item["source_case"]["case_id"]: set(item["signals"]["source_context_tags"])
        for item in signal_records
    }
    assert {
        "source_tag:tang_mural",
        "source_tag:registry_ambiguity",
    } <= tags_by_case["source_context_challenge_v1_test_tang_registry"]
    assert {
        "source_tag:gongbi",
        "source_tag:spring_festival",
    } <= tags_by_case["source_context_challenge_v1_test_gongbi_spring"]

    examples = build_tiny_dataset_examples(
        repo_root=ROOT,
        case_source_manifest_path=SOURCE_MANIFEST,
        auxiliary_signal_manifest_path=signal_manifest,
        include_local_seeds=False,
    )
    assert {item["split"] for item in examples} == {"train", "test"}
    assert sum(1 for item in examples if item["split"] == "train") == 4
    assert sum(1 for item in examples if item["split"] == "test") == 4

    predictions = build_tiny_action_model_predictions(
        examples,
        split="test",
        train_split="train",
    )
    full_report = evaluate_tiny_prediction_records(
        examples,
        predictions,
        dataset_split="test",
        policy_name="tiny_action_model_v1",
    )
    assert full_report["action_accuracy"] == 1.0
    assert full_report["mismatch_count"] == 0
    assert all(
        any(
            str(feature).startswith("aux_signal.source_context_tag:")
            for feature in item["explanation"]["matched_features"]
        )
        for item in predictions
    )

    ablation = run_tiny_feature_ablation_report(
        examples=examples,
        output_path=tmp_path / "tiny_feature_ablation.json",
        eval_split="test",
        train_split="train",
    )
    reports_by_variant = {
        item["variant_id"]: item["policy_report"]
        for item in ablation["variant_reports"]
    }
    assert reports_by_variant["without_auxiliary_signals"]["action_accuracy"] <= 0.5
    assert (
        reports_by_variant["full"]["action_accuracy"]
        > reports_by_variant["without_auxiliary_signals"]["action_accuracy"]
    )
