import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CLI_ENV = dict(
    os.environ,
    PYTHONPATH=str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
)


def _read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_tiny_action_model_predicts_complete_frozen_test_split(tmp_path):
    from vulca.learning.tiny_action_model import (
        POLICY_TINY_ACTION_MODEL,
        build_tiny_action_model_predictions,
    )
    from vulca.learning.tiny_dataset import write_tiny_dataset

    dataset_path = tmp_path / "tiny_dataset.jsonl"
    write_tiny_dataset(repo_root=ROOT, output_path=dataset_path)
    examples = _read_jsonl(dataset_path)
    test_examples = [item for item in examples if item["split"] == "test"]

    predictions = build_tiny_action_model_predictions(
        examples,
        split="test",
        train_split="train",
    )

    assert {item["example_id"] for item in predictions} == {
        item["example_id"] for item in test_examples
    }
    assert {item["policy_name"] for item in predictions} == {
        POLICY_TINY_ACTION_MODEL
    }
    by_case_id = {
        item["case_id"]: item
        for item in predictions
    }
    assert by_case_id["redraw_20260505T144500Z_0d13fd902885"][
        "recommended_action"
    ] == "manual_review"
    assert by_case_id["redraw_20260505T144500Z_0d13fd902885"][
        "failure_hint"
    ] == "pasteback_mismatch"
    assert by_case_id["redraw_20260505T144500Z_0d13fd902885"][
        "source_policy"
    ] == "train_sparse_feature_classifier"
    assert by_case_id["redraw_20260505T144500Z_0d13fd902885"][
        "explanation"
    ]["fallback_reason"] == "failure_hint_prior"
    assert by_case_id["layer_generate_20260505T144500Z_b4ac612ba871"][
        "recommended_action"
    ] == "accept"
    assert "case_type:layer_generate_case" in by_case_id[
        "layer_generate_20260505T144500Z_b4ac612ba871"
    ]["explanation"]["matched_features"]


def test_tiny_action_model_prediction_script_compares_required_baselines(tmp_path):
    from vulca.learning.tiny_dataset import write_tiny_dataset

    dataset_path = tmp_path / "tiny_dataset.jsonl"
    action_model_path = tmp_path / "tiny_action_model_v1.jsonl"
    case_type_prior_path = tmp_path / "tiny_case_type_prior_v0.jsonl"
    tiny_agent_path = tmp_path / "tiny_agent_v0.jsonl"
    report_path = tmp_path / "tiny_action_model_comparison.json"
    write_tiny_dataset(repo_root=ROOT, output_path=dataset_path)

    action_result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "tiny_action_model_predict.py"),
            str(dataset_path),
            "--split",
            "test",
            "--train-split",
            "train",
            "--output",
            str(action_model_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
        env=CLI_ENV,
        cwd=ROOT,
    )
    assert action_result.returncode == 0, action_result.stderr
    assert "tiny_action_model_v1 predictions: 2" in action_result.stdout

    for policy_name, output_path in (
        ("tiny_case_type_prior_v0", case_type_prior_path),
        ("tiny_agent_v0", tiny_agent_path),
    ):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "tiny_baseline_predict.py"),
                str(dataset_path),
                "--policy",
                policy_name,
                "--split",
                "test",
                "--train-split",
                "train",
                "--output",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            timeout=20,
            env=CLI_ENV,
            cwd=ROOT,
        )
        assert result.returncode == 0, result.stderr

    eval_result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "tiny_dataset_eval.py"),
            str(dataset_path),
            "--compare",
            "--split",
            "test",
            "--train-split",
            "train",
            "--prediction",
            str(action_model_path),
            "--prediction",
            str(case_type_prior_path),
            "--prediction",
            str(tiny_agent_path),
            "--output",
            str(report_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
        env=CLI_ENV,
        cwd=ROOT,
    )

    assert eval_result.returncode == 0, eval_result.stderr
    for policy_name in (
        "majority_action",
        "tiny_case_type_prior_v0",
        "tiny_agent_v0",
        "tiny_action_model_v1",
    ):
        assert f"{policy_name} action_accuracy:" in eval_result.stdout

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert set(report["policy_reports"]) >= {
        "majority_action",
        "redraw_observable_signal",
        "tiny_case_type_prior_v0",
        "tiny_agent_v0",
        "tiny_action_model_v1",
    }
    action_report = report["policy_reports"]["tiny_action_model_v1"]
    assert action_report["prediction_count"] == 2
    assert action_report["missing_count"] == 0
    assert action_report["extra_count"] == 0
    assert action_report["action_accuracy"] == 1.0


def test_tiny_action_model_uses_manual_curated_failure_signals(tmp_path):
    from vulca.learning.tiny_action_model import build_tiny_action_model_predictions
    from vulca.learning.tiny_dataset import (
        evaluate_tiny_prediction_records,
        write_tiny_dataset,
    )

    dataset_path = tmp_path / "tiny_dataset.jsonl"
    write_tiny_dataset(
        repo_root=ROOT,
        output_path=dataset_path,
        case_source_manifest_path=(
            ROOT
            / "docs/benchmarks/learning/manual_curated_case_source_manifest_v1.json"
        ),
    )
    examples = _read_jsonl(dataset_path)

    predictions = build_tiny_action_model_predictions(
        examples,
        split="test",
        train_split="train",
    )

    by_case_id = {item["case_id"]: item for item in predictions}
    assert by_case_id["manual_v1_redraw_mask_leak"][
        "recommended_action"
    ] == "adjust_mask"
    assert by_case_id["manual_v1_layer_generate_layer_order"][
        "recommended_action"
    ] == "manual_review"
    assert by_case_id["manual_v1_layer_generate_prompt_ambiguity"][
        "recommended_action"
    ] == "adjust_prompt"
    assert by_case_id["manual_v1_decompose_under_segmentation"][
        "recommended_action"
    ] == "split_layer_further"

    prediction_report = evaluate_tiny_prediction_records(
        examples,
        predictions,
        dataset_split="test",
        policy_name="tiny_action_model_v1",
    )
    assert prediction_report["example_count"] == 5
    assert prediction_report["action_accuracy"] == 1.0


def test_tiny_action_model_uses_redraw_instruction_failure_priors():
    from vulca.learning.tiny_action_model import TinyActionClassifier

    classifier = TinyActionClassifier.fit([])
    prediction = classifier.predict(
        {
            "example_id": "example-redraw-missing-detail",
            "input": {
                "case_record": {
                    "case_type": "redraw_case",
                    "quality": {
                        "failures": ["missing_detail"],
                        "gate_passed": False,
                    },
                }
            },
            "source_case": {
                "case_id": "real_redraw_missing_detail",
                "case_type": "redraw_case",
            },
        }
    )

    assert prediction["recommended_action"] == "adjust_instruction"
    assert prediction["failure_hint"] == "missing_detail"
    assert prediction["explanation"]["fallback_reason"] == "failure_hint_prior"
