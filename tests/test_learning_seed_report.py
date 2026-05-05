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
        "layer_generate_case": 5,
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
    assert observable["action_accuracy"] == 1.0
    assert report["redraw_router_mismatches"]["observable_signal"] == []


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
    ] == 1.0


def test_baseline_gate_returns_violations_for_threshold_regressions():
    from vulca.learning.seed_report import (
        build_local_seed_baseline_report,
        check_baseline_report,
    )

    report = build_local_seed_baseline_report(ROOT)
    assert check_baseline_report(
        report,
        min_action_accuracy={"observable_signal": 1.0},
        max_mismatches={"observable_signal": 0},
    ) == []

    regressed = json.loads(json.dumps(report))
    regressed["redraw_router_baselines"]["observable_signal"]["action_accuracy"] = 0.5
    regressed["redraw_router_mismatches"]["observable_signal"] = [
        {"case_id": "seed_regression"}
    ]

    violations = check_baseline_report(
        regressed,
        min_action_accuracy={"observable_signal": 1.0},
        max_mismatches={"observable_signal": 0},
    )

    assert violations == [
        {
            "policy": "observable_signal",
            "metric": "action_accuracy",
            "actual": 0.5,
            "expected": ">= 1.0",
        },
        {
            "policy": "observable_signal",
            "metric": "mismatch_count",
            "actual": 1,
            "expected": "<= 0",
        },
    ]


def test_parse_baseline_gate_thresholds_validates_policy_values():
    from vulca.learning.seed_report import parse_policy_thresholds

    assert parse_policy_thresholds(["observable_signal=1.0"]) == {
        "observable_signal": 1.0
    }

    try:
        parse_policy_thresholds(["unknown=1.0"])
    except ValueError as exc:
        assert "unsupported baseline policy" in str(exc)
    else:
        raise AssertionError("expected unsupported policy to be rejected")


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
    assert "observable_signal action_accuracy: 1.0" in result.stdout


def test_cases_baseline_report_cli_fails_when_gate_violates(tmp_path):
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
            "--min-action-accuracy",
            "observable_signal=1.01",
            "--max-mismatches",
            "observable_signal=0",
        ],
        capture_output=True,
        text=True,
        timeout=20,
        env=CLI_ENV,
        cwd=tmp_path,
    )

    assert result.returncode == 1
    assert output_path.exists()
    assert "Baseline gate failed:" in result.stderr
    assert "observable_signal action_accuracy 1.0 < 1.01" in result.stderr
