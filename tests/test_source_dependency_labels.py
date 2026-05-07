from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
CLI_ENV = dict(
    os.environ,
    PYTHONPATH=str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
)


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _review_item(
    case_id: str,
    *,
    source_dependency: str = "required",
    decision_basis: str = "artifact_source",
    record_index: int = 0,
    confirmed: bool | None = True,
    corrected_action: str = "",
    notes: str = "client-only sentence /Users/private/source.png",
) -> dict:
    return {
        "schema_version": 1,
        "case_type": "learning_real_source_dependency_review_item",
        "case_id": case_id,
        "source_case_type": "layer_generate_case",
        "source": {
            "source_id": "real_user_cases_v2",
            "kind": "user_case_log",
            "privacy_scope": "private",
            "curation_status": "reviewed",
            "record_index": record_index,
            "split": "test",
        },
        "current_labels": {
            "preferred_action": "manual_review",
            "failure_type": "prompt_ambiguity",
        },
        "source_context": {
            "available": True,
            "tags": ["source_tag:tang_mural"],
            "source_image_available": True,
            "source_artifact_available_count": 1,
            "source_artifact_text_file_count": 2,
        },
        "predictions": {
            "full_action": "manual_review",
            "without_auxiliary_signals_action": "manual_review",
            "action_changed_with_source_context": False,
            "full_matches_target": True,
            "without_auxiliary_signals_matches_target": True,
        },
        "audit": {
            "candidate_reason": "source_context_used_no_action_change",
            "recommended_review_action": "verify_source_dependency_label",
            "source_context_feature_match_count": 2,
        },
        "suggested_review": {
            "source_dependency": "helpful",
            "decision_basis": "artifact_source",
            "review_priority": "medium",
        },
        "human_review": {
            "source_dependency": source_dependency,
            "decision_basis": decision_basis,
            "preferred_action_confirmed": confirmed,
            "corrected_preferred_action": corrected_action,
            "review_notes": notes,
        },
    }


def _minimal_case(case_id: str) -> dict:
    return {
        "schema_version": 1,
        "case_type": "layer_generate_case",
        "case_id": case_id,
        "created_at": "2026-05-07T12:00:00Z",
        "inputs": {
            "user_intent": "test intent",
            "tradition": "test",
        },
        "outputs": {
            "layers": [],
        },
        "review": {
            "human_accept": False,
            "failure_type": "prompt_ambiguity",
            "preferred_action": "manual_review",
        },
    }


def _write_case_source_manifest(tmp_path: Path, case_log: Path) -> Path:
    manifest = {
        "schema_version": 1,
        "case_type": "learning_tiny_case_source_manifest",
        "sources": [
            {
                "source_id": "real_user_cases_v2",
                "kind": "user_case_log",
                "path": os.path.relpath(case_log, tmp_path),
                "privacy_scope": "private",
                "curation_status": "reviewed",
                "preferred_split": "test",
            }
        ],
    }
    path = tmp_path / "case_source_manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def test_source_dependency_label_pack_rejects_incomplete_human_review(tmp_path):
    from vulca.learning.source_dependency_labels import write_source_dependency_label_pack

    review_path = tmp_path / "review.template.jsonl"
    _write_jsonl(
        review_path,
        [
            _review_item(
                "case_a",
                source_dependency="unknown",
                decision_basis="unknown",
                confirmed=None,
            )
        ],
    )

    with pytest.raises(ValueError, match="incomplete source dependency review"):
        write_source_dependency_label_pack(
            input_path=review_path,
            output_path=tmp_path / "labels.jsonl",
            manifest_path=tmp_path / "labels.manifest.json",
            source_id="real-source-dependency-review-v1",
        )


def test_source_dependency_label_pack_writes_sanitized_labels_and_manifest(tmp_path):
    from vulca.learning.source_dependency_labels import write_source_dependency_label_pack

    review_path = tmp_path / "review.reviewed.jsonl"
    label_path = tmp_path / "source_dependency_labels.reviewed.jsonl"
    manifest_path = tmp_path / "source_dependency_label_manifest.json"
    _write_jsonl(
        review_path,
        [
            _review_item("case_a", source_dependency="required"),
            _review_item(
                "case_b",
                source_dependency="not_needed",
                decision_basis="metadata_only",
                record_index=1,
                confirmed=False,
                corrected_action="adjust_prompt",
            ),
        ],
    )

    result = write_source_dependency_label_pack(
        input_path=review_path,
        output_path=label_path,
        manifest_path=manifest_path,
        source_id="real-source-dependency-review-v1",
        reviewer="human-reviewer",
        reviewed_at="2026-05-07T12:30:00Z",
    )

    assert result.record_count == 2
    assert result.counts_by_source_dependency == {"not_needed": 1, "required": 1}
    records = _read_jsonl(label_path)
    assert records[0]["case_type"] == "learning_source_dependency_label_record"
    assert records[0]["labels"] == {
        "corrected_preferred_action": "",
        "decision_basis": "artifact_source",
        "preferred_action_confirmed": True,
        "source_dependency": "required",
    }
    assert records[1]["labels"]["corrected_preferred_action"] == "adjust_prompt"
    assert records[0]["training_use"] == {
        "approved_label_use": "source_dependency_training_label",
        "approved_for_source_dependency_training": True,
        "default_training_input": False,
        "review_status": "reviewed_source_dependency_label",
    }

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["case_type"] == "learning_source_dependency_label_manifest"
    assert manifest["record_count"] == 2
    assert manifest["sources"][0]["path"] == "source_dependency_labels.reviewed.jsonl"
    assert manifest["training_use"]["requires_explicit_dataset_flag"] is True

    encoded = json.dumps(manifest, sort_keys=True)
    encoded += "\n".join(json.dumps(item, sort_keys=True) for item in records)
    assert "client-only sentence" not in encoded
    assert "/Users/private" not in encoded


def test_source_dependency_label_manifest_attaches_labels_to_dataset_examples(tmp_path):
    from vulca.learning.source_dependency_labels import (
        attach_source_dependency_labels,
        write_source_dependency_label_pack,
    )

    review_path = tmp_path / "review.reviewed.jsonl"
    label_path = tmp_path / "labels.reviewed.jsonl"
    manifest_path = tmp_path / "labels.manifest.json"
    _write_jsonl(review_path, [_review_item("case_a", source_dependency="helpful")])
    write_source_dependency_label_pack(
        input_path=review_path,
        output_path=label_path,
        manifest_path=manifest_path,
        source_id="real-source-dependency-review-v1",
    )

    examples = [
        {
            "example_id": "example_a",
            "source": {"source_id": "real_user_cases_v2", "index": 0},
            "source_case": {
                "case_type": "layer_generate_case",
                "case_id": "case_a",
            },
            "targets": {},
            "tasks": {},
        },
        {
            "example_id": "example_b",
            "source": {"source_id": "real_user_cases_v2", "index": 1},
            "source_case": {
                "case_type": "layer_generate_case",
                "case_id": "case_b",
            },
            "targets": {},
            "tasks": {},
        },
    ]

    attached = attach_source_dependency_labels(examples, manifest_path=manifest_path)

    assert attached == 1
    assert examples[0]["targets"]["source_dependency"] == "helpful"
    assert examples[0]["targets"]["source_decision_basis"] == "artifact_source"
    assert examples[0]["tasks"]["source_context"]["dependency_classification"] == "helpful"
    assert "source_dependency_review" not in examples[1]


def test_tiny_dataset_export_accepts_source_dependency_manifest(tmp_path):
    from vulca.learning.source_dependency_labels import write_source_dependency_label_pack
    from vulca.learning.tiny_dataset import write_tiny_dataset

    case_log = tmp_path / "real_cases.jsonl"
    review_path = tmp_path / "review.reviewed.jsonl"
    label_path = tmp_path / "labels.reviewed.jsonl"
    source_dependency_manifest = tmp_path / "labels.manifest.json"
    dataset_path = tmp_path / "tiny_dataset.jsonl"
    _write_jsonl(case_log, [_minimal_case("case_a")])
    case_source_manifest = _write_case_source_manifest(tmp_path, case_log)
    _write_jsonl(review_path, [_review_item("case_a", source_dependency="required")])
    write_source_dependency_label_pack(
        input_path=review_path,
        output_path=label_path,
        manifest_path=source_dependency_manifest,
        source_id="real-source-dependency-review-v1",
    )

    result = write_tiny_dataset(
        repo_root=ROOT,
        output_path=dataset_path,
        case_source_manifest_path=case_source_manifest,
        source_dependency_manifest_path=source_dependency_manifest,
        include_local_seeds=False,
    )

    assert result.example_count == 1
    example = _read_jsonl(dataset_path)[0]
    assert example["targets"]["source_dependency"] == "required"
    assert example["targets"]["source_decision_basis"] == "artifact_source"
    assert example["tasks"]["source_context"] == {
        "decision_basis_classification": "artifact_source",
        "dependency_classification": "required",
    }
    index = json.loads(dataset_path.with_suffix(".index.json").read_text(encoding="utf-8"))
    assert index["source_dependency_manifest_path"] == str(source_dependency_manifest)


def test_source_dependency_labels_cli_and_cases_export_dataset_cli(tmp_path):
    case_log = tmp_path / "real_cases.jsonl"
    review_path = tmp_path / "review.reviewed.jsonl"
    label_path = tmp_path / "labels.reviewed.jsonl"
    source_dependency_manifest = tmp_path / "labels.manifest.json"
    dataset_path = tmp_path / "tiny_dataset.jsonl"
    _write_jsonl(case_log, [_minimal_case("case_a")])
    case_source_manifest = _write_case_source_manifest(tmp_path, case_log)
    _write_jsonl(review_path, [_review_item("case_a", source_dependency="helpful")])

    label_result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/source_dependency_labels.py"),
            "--input",
            str(review_path),
            "--output",
            str(label_path),
            "--manifest",
            str(source_dependency_manifest),
            "--source-id",
            "real-source-dependency-review-v1",
            "--reviewer",
            "human-reviewer",
            "--reviewed-at",
            "2026-05-07T12:30:00Z",
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        check=False,
    )
    assert label_result.returncode == 0, label_result.stderr
    assert "Source dependency labels: 1" in label_result.stdout

    dataset_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "vulca.cli",
            "cases",
            "export-dataset",
            "--output",
            str(dataset_path),
            "--case-source-manifest",
            str(case_source_manifest),
            "--source-dependency-manifest",
            str(source_dependency_manifest),
            "--no-local-seeds",
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        check=False,
    )

    assert dataset_result.returncode == 0, dataset_result.stderr
    assert _read_jsonl(dataset_path)[0]["targets"]["source_dependency"] == "helpful"
