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


def test_tiny_case_type_prior_writes_prediction_jsonl(tmp_path):
    from vulca.learning.tiny_baseline_model import write_tiny_baseline_predictions
    from vulca.learning.tiny_dataset import (
        build_tiny_dataset_comparison_report,
        write_tiny_dataset,
    )

    dataset_path = tmp_path / "tiny_dataset.jsonl"
    prediction_path = tmp_path / "case_type_prior.jsonl"
    write_tiny_dataset(repo_root=ROOT, output_path=dataset_path)

    result = write_tiny_baseline_predictions(
        dataset_path=dataset_path,
        output_path=prediction_path,
        policy_name="tiny_case_type_prior_v0",
        split="test",
    )

    assert result.output_path == str(prediction_path)
    assert result.prediction_count == 2
    predictions = _read_jsonl(prediction_path)
    assert {item["policy_name"] for item in predictions} == {
        "tiny_case_type_prior_v0"
    }
    assert all(item["example_id"] for item in predictions)
    assert all(item["recommended_action"] for item in predictions)

    report = build_tiny_dataset_comparison_report(
        _read_jsonl(dataset_path),
        eval_split="test",
        prediction_paths=[prediction_path],
    )
    assert report["policy_reports"]["tiny_case_type_prior_v0"][
        "action_accuracy"
    ] == 0.5


def test_tiny_agent_v0_combines_redraw_router_and_learned_prior(tmp_path):
    from vulca.learning.tiny_baseline_model import write_tiny_baseline_predictions
    from vulca.learning.tiny_dataset import (
        build_tiny_dataset_comparison_report,
        write_tiny_dataset,
    )

    dataset_path = tmp_path / "tiny_dataset.jsonl"
    prediction_path = tmp_path / "tiny_agent_v0.jsonl"
    write_tiny_dataset(repo_root=ROOT, output_path=dataset_path)

    result = write_tiny_baseline_predictions(
        dataset_path=dataset_path,
        output_path=prediction_path,
        policy_name="tiny_agent_v0",
        split="test",
    )

    assert result.policy_name == "tiny_agent_v0"
    assert result.prediction_count == 2
    predictions = _read_jsonl(prediction_path)
    assert {item["policy_name"] for item in predictions} == {"tiny_agent_v0"}
    assert {item["source_policy"] for item in predictions} == {
        "case_type_prior",
        "redraw_observable_signal",
    }

    report = build_tiny_dataset_comparison_report(
        _read_jsonl(dataset_path),
        eval_split="test",
        prediction_paths=[prediction_path],
    )
    assert report["policy_reports"]["tiny_agent_v0"]["matched_count"] == 2
    assert report["policy_reports"]["tiny_agent_v0"]["action_accuracy"] == 1.0
    assert report["ranked_policies"][0]["policy_name"] == "tiny_agent_v0"


def test_tiny_baseline_predict_script_outputs_comparable_predictions(tmp_path):
    from vulca.learning.tiny_dataset import write_tiny_dataset

    dataset_path = tmp_path / "tiny_dataset.jsonl"
    prediction_path = tmp_path / "tiny_agent_v0.jsonl"
    report_path = tmp_path / "comparison.json"
    write_tiny_dataset(repo_root=ROOT, output_path=dataset_path)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "tiny_baseline_predict.py"),
            str(dataset_path),
            "--policy",
            "tiny_agent_v0",
            "--split",
            "test",
            "--output",
            str(prediction_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
        env=CLI_ENV,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert prediction_path.exists()
    assert "tiny_agent_v0 predictions: 2" in result.stdout

    eval_result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "tiny_dataset_eval.py"),
            str(dataset_path),
            "--compare",
            "--split",
            "test",
            "--prediction",
            str(prediction_path),
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
    assert "tiny_agent_v0 action_accuracy: 1.0" in eval_result.stdout
