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


def test_build_local_seed_baseline_report_summarizes_cases_and_router_metrics():
    from vulca.learning.seed_report import build_local_seed_baseline_report

    report = build_local_seed_baseline_report(ROOT)

    assert report["case_type"] == "learning_local_seed_baseline_report"
    assert report["seed_counts"] == {
        "redraw_case": 6,
        "decompose_case": 1,
        "layer_generate_case": 1,
    }
    assert report["review_summary"]["redraw_case"]["preferred_action_counts"][
        "adjust_mask"
    ] == 2
    assert report["review_summary"]["decompose_case"]["human_accept_counts"][
        "true"
    ] == 1

    label_oracle = report["redraw_router_baselines"]["label_oracle"]
    assert label_oracle["case_count"] == 6
    assert label_oracle["action_accuracy"] == 1.0
    assert report["redraw_router_mismatches"]["label_oracle"] == []

    observable = report["redraw_router_baselines"]["observable_signal"]
    assert observable["case_count"] == 6
    assert observable["action_accuracy"] == 0.5
    assert len(report["redraw_router_mismatches"]["observable_signal"]) == 3


def test_write_local_seed_baseline_report_creates_json(tmp_path):
    from vulca.learning.seed_report import write_local_seed_baseline_report

    output_path = tmp_path / "local_seed_baseline_report.json"

    result_path = write_local_seed_baseline_report(
        repo_root=ROOT,
        output_path=output_path,
    )

    assert result_path == str(output_path)
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["redraw_router_baselines"]["observable_signal"][
        "failure_macro_f1"
    ] == 0.42857142857142855


def test_cases_baseline_report_cli_writes_report(tmp_path):
    output_path = tmp_path / "baseline.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "vulca.cli",
            "cases",
            "baseline-report",
            "--repo-root",
            str(ROOT),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
        env=CLI_ENV,
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert output_path.exists()
    assert "Baseline report:" in result.stdout
    assert "observable_signal action_accuracy: 0.5" in result.stdout
