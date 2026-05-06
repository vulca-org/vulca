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
    assert by_case_id["redraw_20260505T144500Z_f2741106fbf5"][
        "recommended_action"
    ] == "adjust_route"
    assert by_case_id["redraw_20260505T144500Z_f2741106fbf5"][
        "failure_hint"
    ] == "route_error"
    assert by_case_id["redraw_20260505T144500Z_f2741106fbf5"][
        "source_policy"
    ] == "train_sparse_feature_classifier"
    assert by_case_id["redraw_20260505T144500Z_f2741106fbf5"][
        "explanation"
    ]["fallback_reason"] == "failure_hint_prior"
    assert by_case_id["layer_generate_20260505T144500Z_e3c92ef7660d"][
        "recommended_action"
    ] == "accept"
    assert "case_type:layer_generate_case" in by_case_id[
        "layer_generate_20260505T144500Z_e3c92ef7660d"
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


def test_tiny_action_model_uses_curated_failure_priors_without_split_coupling():
    from vulca.learning.tiny_action_model import TinyActionClassifier

    classifier = TinyActionClassifier.fit([])

    for failure_hint, expected_action in {
        "mask_leak": "adjust_mask",
        "layer_order": "manual_review",
        "prompt_ambiguity": "adjust_prompt",
        "style_drift": "adjust_prompt",
    }.items():
        prediction = classifier.predict(
            {
                "example_id": f"example-{failure_hint}",
                "input": {
                    "case_record": {
                        "case_type": "layer_generate_case",
                        "quality": {
                            "failures": [failure_hint],
                            "gate_passed": False,
                        },
                    }
                },
                "source_case": {
                    "case_id": f"manual_{failure_hint}",
                    "case_type": "layer_generate_case",
                },
            }
        )

        assert prediction["recommended_action"] == expected_action
        assert prediction["failure_hint"] == failure_hint
        assert prediction["explanation"]["fallback_reason"] == "failure_hint_prior"


def test_tiny_action_model_learns_promoted_florence_caption_tokens():
    from vulca.learning.tiny_action_model import (
        TinyActionClassifier,
        extract_tiny_action_features,
    )

    def example(example_id, split, target_action, caption, ocr):
        return {
            "example_id": example_id,
            "split": split,
            "source_case": {
                "case_id": example_id,
                "case_type": "layer_generate_case",
            },
            "input": {
                "case_record": {
                    "case_type": "layer_generate_case",
                    "quality": {
                        "gate_passed": False,
                    },
                },
                "auxiliary_signals": [
                    {
                        "signal_id": f"signal_{example_id}",
                        "model": {
                            "id": "florence_2",
                        },
                        "signals": {
                            "status": "completed",
                            "signal_source": "local_runner",
                            "caption_candidates": [caption],
                            "ocr_text": [ocr],
                        },
                        "training_use": {
                            "approved_for_auxiliary_training": True,
                            "review_status": "reviewed_promoted",
                        },
                    }
                ],
            },
            "targets": {
                "preferred_action": target_action,
            },
        }

    train = example(
        "train_provider_failure_car",
        "train",
        "fallback_to_agent",
        "A red car is parked on the side of the road.",
        "JAMES CO.UK",
    )
    distractor = example(
        "train_prompt_case_bar",
        "train",
        "adjust_prompt",
        "A group of people sitting at a bar.",
        "PHILLIES",
    )
    test = example(
        "test_provider_failure_car",
        "test",
        "fallback_to_agent",
        "A red car is parked on the side of the road.",
        "JAMES CO.UK",
    )

    features = extract_tiny_action_features(test)
    assert "aux_signal.caption_token:red" in features
    assert "aux_signal.caption_token:car" in features
    assert "aux_signal.ocr_token:james" in features
    prediction = TinyActionClassifier.fit([train, distractor]).predict(test)

    assert prediction["recommended_action"] == "fallback_to_agent"
    assert "aux_signal.caption_token:car" in prediction["explanation"][
        "matched_features"
    ]
    assert prediction["explanation"]["fallback_reason"] == ""
