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
GATE_SCRIPT = ROOT / "scripts" / "tiny_training_eval_gate.py"


def _run_gate(tmp_path, *extra_args):
    output_dir = tmp_path / "tiny_training_eval"
    report_path = tmp_path / "tiny_training_eval_report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(GATE_SCRIPT),
            "--repo-root",
            str(ROOT),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report_path),
            *extra_args,
        ],
        capture_output=True,
        text=True,
        timeout=30,
        env=CLI_ENV,
        cwd=ROOT,
    )
    return result, output_dir, report_path


def test_tiny_training_eval_gate_command_writes_dataset_predictions_and_report(tmp_path):
    result, output_dir, report_path = _run_gate(tmp_path)

    assert result.returncode == 0, result.stderr
    assert (output_dir / "tiny_dataset.jsonl").exists()
    assert (output_dir / "tiny_agent_v0.predictions.jsonl").exists()
    assert (output_dir / "tiny_action_model_v1.predictions.jsonl").exists()
    assert (output_dir / "tiny_dataset_comparison.json").exists()
    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["case_type"] == "learning_tiny_training_eval_gate_report"
    assert report["gate"]["passed"] is True
    assert report["artifacts"]["dataset_path"] == str(output_dir / "tiny_dataset.jsonl")
    assert report["artifacts"]["comparison_report_path"] == str(
        output_dir / "tiny_dataset_comparison.json"
    )
    assert report["dataset"]["example_count"] == 20
    assert report["dataset"]["counts_by_split"]["test"] == 5


def test_tiny_training_eval_gate_report_includes_required_policies(tmp_path):
    result, _, report_path = _run_gate(tmp_path)

    assert result.returncode == 0, result.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    policy_reports = report["comparison"]["policy_reports"]
    assert set(policy_reports) >= {
        "majority_action",
        "redraw_observable_signal",
        "tiny_agent_v0",
        "tiny_action_model_v1",
    }


def test_tiny_training_eval_gate_fails_below_action_accuracy_threshold(tmp_path):
    result, _, report_path = _run_gate(
        tmp_path,
        "--min-action-accuracy",
        "tiny_action_model_v1=1.01",
    )

    assert result.returncode == 1
    assert "Tiny training/eval gate failed" in result.stderr
    assert "tiny_action_model_v1 action_accuracy 1.0 < 1.01" in result.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["gate"]["passed"] is False
    assert report["gate"]["violations"] == [
        {
            "policy": "tiny_action_model_v1",
            "metric": "action_accuracy",
            "actual": 1.0,
            "expected": ">= 1.01",
        }
    ]


def test_tiny_training_eval_gate_passes_for_current_seeds_and_manual_curated_cases(tmp_path):
    result, _, report_path = _run_gate(tmp_path)

    assert result.returncode == 0, result.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    policy_reports = report["comparison"]["policy_reports"]
    assert policy_reports["tiny_action_model_v1"]["missing_count"] == 0
    assert policy_reports["tiny_action_model_v1"]["mismatch_count"] == 0
    assert policy_reports["tiny_action_model_v1"]["action_accuracy"] == 1.0
    assert (
        policy_reports["tiny_action_model_v1"]["action_accuracy"]
        >= policy_reports["tiny_agent_v0"]["action_accuracy"]
    )
