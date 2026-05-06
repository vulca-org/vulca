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
REPORT_SCRIPT = ROOT / "scripts" / "training_effectiveness_report.py"


def _run_report(tmp_path, *extra_args):
    output_dir = tmp_path / "training_effectiveness"
    report_path = tmp_path / "training_effectiveness_report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(REPORT_SCRIPT),
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


def test_training_effectiveness_report_uses_combined_real_manual_and_seed_data(tmp_path):
    from vulca.learning.training_effectiveness import run_training_effectiveness_report

    report = run_training_effectiveness_report(
        repo_root=ROOT,
        output_dir=tmp_path / "effectiveness",
        report_path=tmp_path / "training_effectiveness_report.json",
    )

    assert report["case_type"] == "learning_training_effectiveness_report"
    assert report["status"] == "passed"
    assert report["dataset"]["example_count"] == 50
    assert report["dataset"]["eval_example_count"] == 21
    assert report["dataset"]["counts_by_split"] == {
        "dev": 9,
        "test": 21,
        "train": 20,
    }
    assert report["dataset"]["counts_by_source_kind"] == {
        "local_seed": 12,
        "manual_case_log": 15,
        "synthetic_case_log": 11,
        "user_case_log": 12,
    }
    assert report["effectiveness"]["gate_passed"] is True
    assert report["effectiveness"]["evaluated_policy"] == "tiny_action_model_v1"
    assert report["effectiveness"]["baseline_policy"] == "tiny_agent_v0"
    assert report["effectiveness"]["action_accuracy"] == 1.0
    assert report["effectiveness"]["mismatch_count"] == 0
    assert report["effectiveness"]["accuracy_delta_vs_baseline"] > 0
    assert report["effectiveness"]["ablation_summary"]["full_action_accuracy"] == 1.0
    assert (
        report["effectiveness"]["ablation_summary"]["largest_accuracy_drop"][
            "variant_id"
        ]
        == "without_failure_and_action_hints"
    )
    assert (
        "tiny_feature_ablation_report_path"
        in report["artifacts"]
    )
    ranked = {
        item["policy_name"]: item for item in report["effectiveness"]["policy_ranking"]
    }
    assert ranked["tiny_action_model_v1"]["action_accuracy"] == 1.0
    assert Path(report["artifacts"]["aggregated_report_path"]).exists()


def test_training_effectiveness_report_has_no_default_eval_coverage_gaps(tmp_path):
    from vulca.learning.training_effectiveness import run_training_effectiveness_report

    report = run_training_effectiveness_report(
        repo_root=ROOT,
        output_dir=tmp_path / "effectiveness",
        report_path=tmp_path / "training_effectiveness_report.json",
    )

    assert report["data_gaps"] == []
    assert report["coverage"]["source_kind"]["synthetic_case_log"] == {
        "example_count": 11,
        "eval_example_count": 11,
    }
    assert report["coverage"]["source_kind"]["user_case_log"] == {
        "example_count": 12,
        "eval_example_count": 3,
    }


def test_training_effectiveness_report_script_writes_report_and_prints_summary(tmp_path):
    result, _, report_path = _run_report(tmp_path)

    assert result.returncode == 0, result.stderr
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["case_type"] == "learning_training_effectiveness_report"
    assert "Training effectiveness report:" in result.stdout
    assert "Dataset examples: 50" in result.stdout
    assert "Eval examples: 21" in result.stdout
    assert "tiny_action_model_v1 action_accuracy: 1.0" in result.stdout
    assert "Ablation hardest drop:" in result.stdout
    assert "tiny_agent_v0 action_accuracy:" in result.stdout
    assert "Data gaps: 0" in result.stdout
    assert "source.kind local_seed: eval 0/12" not in result.stdout


def test_training_effectiveness_report_script_can_fail_on_data_gaps(tmp_path):
    result, _, report_path = _run_report(
        tmp_path,
        "--fail-on-data-gaps",
        "--min-eval-examples-per-bucket",
        "2",
    )

    assert result.returncode == 1
    assert report_path.exists()
    assert "Training effectiveness data coverage gaps:" in result.stderr
    assert "source.kind local_seed eval 0 < 1" not in result.stderr
    assert "targets.failure_type" in result.stderr
