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
REPORT_SCRIPT = ROOT / "scripts" / "model_selection_report.py"


def _run_report(tmp_path, *extra_args):
    output_dir = tmp_path / "model_selection"
    report_path = tmp_path / "model_selection_report.json"
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


def test_model_selection_report_promotes_tiny_action_model_and_keeps_baselines(tmp_path):
    from vulca.learning.model_selection_report import run_model_selection_report

    report = run_model_selection_report(
        repo_root=ROOT,
        output_dir=tmp_path / "model_selection",
        report_path=tmp_path / "model_selection_report.json",
    )

    assert report["case_type"] == "learning_model_selection_report"
    assert report["status"] == "ready_for_selection"
    assert report["dataset"] == {
        "example_count": 36,
        "eval_example_count": 17,
        "data_gap_count": 0,
        "counts_by_source_kind": {
            "local_seed": 12,
            "manual_case_log": 8,
            "synthetic_case_log": 11,
            "user_case_log": 5,
        },
    }
    assert report["selection"]["recommended_primary_policy"] == "tiny_action_model_v1"
    assert report["selection"]["recommended_baseline_policy"] == "tiny_agent_v0"
    assert report["selection"]["accuracy_delta_vs_baseline"] > 0.4
    assert report["selection"]["requires_more_data_before_training"] is False

    candidates = {
        item["policy_name"]: item
        for item in report["candidate_policies"]
    }
    assert set(candidates) == {
        "majority_action",
        "redraw_observable_signal",
        "tiny_action_model_v1",
        "tiny_agent_v0",
    }
    assert candidates["tiny_action_model_v1"]["decision"] == "promote_primary"
    assert candidates["tiny_action_model_v1"]["action_accuracy"] == 1.0
    assert candidates["tiny_agent_v0"]["decision"] == "keep_agent_baseline"
    assert candidates["redraw_observable_signal"]["decision"] == "keep_redraw_guardrail"
    assert candidates["majority_action"]["decision"] == "reject_baseline"


def test_model_selection_report_recommends_specialized_work_tracks(tmp_path):
    from vulca.learning.model_selection_report import run_model_selection_report

    report = run_model_selection_report(
        repo_root=ROOT,
        output_dir=tmp_path / "model_selection",
        report_path=tmp_path / "model_selection_report.json",
    )

    tracks = {
        item["case_type"]: item
        for item in report["workload_recommendations"]
    }
    assert set(tracks) == {
        "decompose_case",
        "layer_generate_case",
        "redraw_case",
    }
    assert tracks["redraw_case"]["recommended_track"] == "redraw_router_specialist_v1"
    assert tracks["redraw_case"]["best_policy"] == "tiny_action_model_v1"
    assert tracks["redraw_case"]["secondary_policy"] == "redraw_observable_signal"
    assert tracks["redraw_case"]["decision"] == "promote_with_guardrail"
    assert tracks["layer_generate_case"]["recommended_track"] == (
        "layer_generate_action_specialist_v1"
    )
    assert tracks["layer_generate_case"]["secondary_policy"] == "tiny_agent_v0"
    assert tracks["layer_generate_case"]["decision"] == "collect_more_real_cases"
    assert tracks["decompose_case"]["recommended_track"] == "decompose_action_specialist_v1"
    assert tracks["decompose_case"]["secondary_policy"] == "tiny_agent_v0"
    assert tracks["decompose_case"]["decision"] == "collect_more_real_cases"


def test_model_selection_report_script_writes_report_and_prints_selection(tmp_path):
    result, _, report_path = _run_report(tmp_path)

    assert result.returncode == 0, result.stderr
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["case_type"] == "learning_model_selection_report"
    assert "Model selection report:" in result.stdout
    assert "Dataset examples: 36" in result.stdout
    assert "Eval examples: 17" in result.stdout
    assert "Recommended primary: tiny_action_model_v1" in result.stdout
    assert "Recommended baseline: tiny_agent_v0" in result.stdout
    assert "Data gaps: 0" in result.stdout
    assert "redraw_case: tiny_action_model_v1" in result.stdout
