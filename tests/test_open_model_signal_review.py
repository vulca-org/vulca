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


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def _first_decompose_example() -> dict:
    from vulca.learning.tiny_dataset import build_tiny_dataset_examples

    return next(
        example
        for example in build_tiny_dataset_examples(repo_root=ROOT)
        if example["source_case"]["case_type"] == "decompose_case"
    )


def _completed_sam_signal_record(example: dict, *, signal_id: str = "open_signal_demo") -> dict:
    return {
        "schema_version": 1,
        "case_type": "learning_open_model_signal_record",
        "signal_id": signal_id,
        "example_id": example["example_id"],
        "source": {
            "kind": "local_seed",
            "split": "seed",
            "privacy_scope": "project",
        },
        "source_case": dict(example["source_case"]),
        "model": {
            "id": "segment_anything_sam_vit",
            "name": "Segment Anything SAM ViT",
            "license": "Apache-2.0",
            "license_risk": "low",
            "model_role": "mask_proposal",
            "output_training_policy": "weak_signal_requires_review",
            "default_runtime_enabled": False,
        },
        "input_summary": {
            "case_type": example["source_case"]["case_type"],
            "case_id": example["source_case"]["case_id"],
            "source_image_ref_kind": "repo_relative",
        },
        "signals": {
            "status": "completed",
            "signal_source": "local_runner",
            "label_source": "assistant_labeled",
            "review_status": "needs_human_review",
            "mask_count": 3,
            "total_mask_area_pct": 0.42,
            "boundary_complexity": "medium",
            "mask_coverage_candidates": [
                {
                    "area_pct": 0.21,
                    "bbox": [4, 8, 40, 64],
                    "predicted_iou": 0.91,
                    "stability_score": 0.88,
                }
            ],
        },
        "training_use": {
            "default_training_input": False,
            "requires_manual_review_for_training_labels": True,
            "review_status": "needs_human_review",
            "output_training_policy": "weak_signal_requires_review",
        },
    }


def test_open_model_signal_review_promotes_completed_local_signal(tmp_path):
    from vulca.learning.open_model_signal_review import (
        review_open_model_signal_log,
        write_promoted_open_model_signal_pack,
    )

    signal_path = tmp_path / "signals.jsonl"
    reviewed_path = tmp_path / "signals.reviewed.jsonl"
    promoted_path = tmp_path / "signals.promoted.jsonl"
    manifest_path = tmp_path / "signals.promotion_manifest.json"
    record = _completed_sam_signal_record(_first_decompose_example())
    _write_jsonl(signal_path, [record])

    result = review_open_model_signal_log(
        signal_path,
        signal_id=record["signal_id"],
        decision="promote",
        output_path=reviewed_path,
        reviewer="human-reviewer",
        reviewed_at="2026-05-06T21:00:00Z",
        notes="SAM mask proposals match the decompose failure.",
    )
    assert result.updated is True
    assert result.review_status == "reviewed_promoted"

    reviewed = _read_jsonl(reviewed_path)
    assert reviewed[0]["signal_review"] == {
        "schema_version": 1,
        "decision": "promote",
        "reviewer": "human-reviewer",
        "reviewed_at": "2026-05-06T21:00:00Z",
        "notes": "SAM mask proposals match the decompose failure.",
    }
    assert reviewed[0]["training_use"]["default_training_input"] is False
    assert reviewed[0]["training_use"]["approved_for_auxiliary_training"] is True
    assert reviewed[0]["training_use"]["review_status"] == "reviewed_promoted"

    pack = write_promoted_open_model_signal_pack(
        input_path=reviewed_path,
        output_path=promoted_path,
        manifest_path=manifest_path,
        source_id="sam-reviewed-v1",
    )
    assert pack.promoted_count == 1
    assert _read_jsonl(promoted_path)[0]["signal_id"] == record["signal_id"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["case_type"] == "learning_open_model_signal_promotion_manifest"
    assert manifest["record_count"] == 1
    assert manifest["sources"][0]["source_id"] == "sam-reviewed-v1"
    assert manifest["sources"][0]["kind"] == "open_model_signal_log"
    assert manifest["training_use"]["default_training_input"] is False
    assert manifest["training_use"]["requires_explicit_dataset_flag"] is True


def test_open_model_signal_review_rejects_dry_run_promotion(tmp_path):
    from vulca.learning.open_model_signal_review import review_open_model_signal_log

    signal_path = tmp_path / "signals.jsonl"
    record = _completed_sam_signal_record(_first_decompose_example())
    record["signals"] = {
        "status": "dry_run_pending_model_execution",
        "signal_source": "dry_run",
    }
    _write_jsonl(signal_path, [record])

    with pytest.raises(ValueError, match="cannot promote dry-run signal"):
        review_open_model_signal_log(
            signal_path,
            signal_id=record["signal_id"],
            decision="promote",
            reviewer="human-reviewer",
        )


def test_open_model_signal_review_rejects_skipped_signal_promotion(tmp_path):
    from vulca.learning.open_model_signal_review import review_open_model_signal_log

    signal_path = tmp_path / "signals.jsonl"
    record = _completed_sam_signal_record(_first_decompose_example())
    record["signals"]["status"] = "skipped"
    _write_jsonl(signal_path, [record])

    with pytest.raises(ValueError, match="cannot promote signal with status 'skipped'"):
        review_open_model_signal_log(
            signal_path,
            signal_id=record["signal_id"],
            decision="promote",
            reviewer="human-reviewer",
        )


def test_tiny_dataset_attaches_only_explicitly_promoted_auxiliary_signals(tmp_path):
    from vulca.learning.open_model_signal_review import (
        review_open_model_signal_log,
        write_promoted_open_model_signal_pack,
    )
    from vulca.learning.tiny_action_model import extract_tiny_action_features
    from vulca.learning.tiny_dataset import build_tiny_dataset_examples

    example = _first_decompose_example()
    signal_path = tmp_path / "signals.jsonl"
    reviewed_path = tmp_path / "signals.reviewed.jsonl"
    promoted_path = tmp_path / "signals.promoted.jsonl"
    manifest_path = tmp_path / "signals.promotion_manifest.json"
    _write_jsonl(signal_path, [_completed_sam_signal_record(example)])
    review_open_model_signal_log(
        signal_path,
        signal_id="open_signal_demo",
        decision="promote",
        output_path=reviewed_path,
        reviewer="human-reviewer",
        reviewed_at="2026-05-06T21:00:00Z",
    )
    write_promoted_open_model_signal_pack(
        input_path=reviewed_path,
        output_path=promoted_path,
        manifest_path=manifest_path,
        source_id="sam-reviewed-v1",
    )

    default_examples = build_tiny_dataset_examples(repo_root=ROOT)
    default_target = next(
        item for item in default_examples if item["example_id"] == example["example_id"]
    )
    assert "auxiliary_signals" not in default_target["input"]

    examples = build_tiny_dataset_examples(
        repo_root=ROOT,
        auxiliary_signal_manifest_path=manifest_path,
    )
    target = next(item for item in examples if item["example_id"] == example["example_id"])
    auxiliary_signals = target["input"]["auxiliary_signals"]
    assert len(auxiliary_signals) == 1
    assert auxiliary_signals[0]["signal_id"] == "open_signal_demo"
    assert auxiliary_signals[0]["training_use"]["review_status"] == "reviewed_promoted"

    features = extract_tiny_action_features(target)
    assert "aux_signal.model:segment_anything_sam_vit" in features
    assert "aux_signal.status:completed" in features
    assert "aux_signal.review_status:reviewed_promoted" in features
    assert "aux_signal.sam_mask_count:2-4" in features
    assert "aux_signal.sam_total_area_pct:25-50" in features


def test_open_model_signal_review_cli_writes_review_and_promotion_manifest(tmp_path):
    signal_path = tmp_path / "signals.jsonl"
    reviewed_path = tmp_path / "signals.reviewed.jsonl"
    promoted_path = tmp_path / "signals.promoted.jsonl"
    manifest_path = tmp_path / "signals.promotion_manifest.json"
    record = _completed_sam_signal_record(_first_decompose_example())
    _write_jsonl(signal_path, [record])

    review_result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/open_model_signal_review.py"),
            "review",
            "--input",
            str(signal_path),
            "--output",
            str(reviewed_path),
            "--signal-id",
            record["signal_id"],
            "--decision",
            "promote",
            "--reviewer",
            "human-reviewer",
            "--reviewed-at",
            "2026-05-06T21:00:00Z",
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        check=False,
    )
    assert review_result.returncode == 0, review_result.stderr
    assert "Reviewed signal:" in review_result.stdout

    promote_result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/open_model_signal_review.py"),
            "promote",
            "--input",
            str(reviewed_path),
            "--output",
            str(promoted_path),
            "--manifest",
            str(manifest_path),
            "--source-id",
            "sam-reviewed-v1",
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        check=False,
    )
    assert promote_result.returncode == 0, promote_result.stderr
    assert "Promoted signals: 1" in promote_result.stdout
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["record_count"] == 1
