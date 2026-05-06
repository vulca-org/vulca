import csv
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
BACKLOG_SCRIPT = ROOT / "scripts" / "data_expansion_backlog.py"


def _run_backlog(tmp_path, *extra_args):
    output_dir = tmp_path / "data_expansion_backlog"
    report_path = tmp_path / "data_expansion_backlog_report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(BACKLOG_SCRIPT),
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


def test_data_expansion_backlog_targets_decompose_and_layer_generate_gaps(tmp_path):
    from vulca.learning.data_expansion_backlog import run_data_expansion_backlog

    report = run_data_expansion_backlog(
        repo_root=ROOT,
        output_dir=tmp_path / "backlog",
        report_path=tmp_path / "backlog_report.json",
    )

    assert report["case_type"] == "learning_data_expansion_backlog"
    assert report["status"] == "ready_for_case_collection"
    assert report["summary"] == {
        "source_review_row_count": 19,
        "backlog_item_count": 7,
        "requested_real_case_count": 14,
        "requested_manual_case_count": 7,
        "case_type_counts": {
            "decompose_case": 3,
            "layer_generate_case": 4,
        },
    }
    assert Path(report["artifacts"]["backlog_json_path"]).exists()
    assert Path(report["artifacts"]["backlog_csv_path"]).exists()

    items = report["backlog_items"]
    assert [item["backlog_id"] for item in items] == [
        "layer_generate_case__provider_failure",
        "layer_generate_case__style_drift",
        "decompose_case__under_segmentation",
        "layer_generate_case__prompt_ambiguity",
        "decompose_case__over_segmentation",
        "layer_generate_case__layer_order",
        "decompose_case__occlusion",
    ]
    assert all(item["workload_decision"] == "collect_more_real_cases" for item in items)
    assert all(item["requested_real_cases"] == 2 for item in items)
    assert all(item["requested_manual_cases"] == 1 for item in items)
    assert all(item["collection_prompt"] for item in items)
    assert not any(item["case_type"] == "redraw_case" for item in items)


def test_data_expansion_backlog_prioritizes_real_user_signal_and_actions(tmp_path):
    from vulca.learning.data_expansion_backlog import run_data_expansion_backlog

    report = run_data_expansion_backlog(
        repo_root=ROOT,
        output_dir=tmp_path / "backlog",
        report_path=tmp_path / "backlog_report.json",
    )

    by_id = {item["backlog_id"]: item for item in report["backlog_items"]}
    prompt = by_id["layer_generate_case__prompt_ambiguity"]
    assert prompt["priority_tier"] == "P0"
    assert prompt["priority_score"] == 100
    assert prompt["current_real_eval_count"] == 1
    assert prompt["target_actions"] == {"manual_review": 1}
    assert prompt["source_kind_counts"]["user_case_log"] == 1
    assert "real user case" in prompt["priority_reason"]

    occlusion = by_id["decompose_case__occlusion"]
    assert occlusion["priority_tier"] == "P2"
    assert occlusion["current_real_eval_count"] == 0
    assert occlusion["target_actions"] == {"fallback_to_agent": 1}
    assert occlusion["source_kind_counts"]["synthetic_case_log"] == 1


def test_data_expansion_backlog_writes_csv_for_parallel_case_sessions(tmp_path):
    from vulca.learning.data_expansion_backlog import run_data_expansion_backlog

    report = run_data_expansion_backlog(
        repo_root=ROOT,
        output_dir=tmp_path / "backlog",
        report_path=tmp_path / "backlog_report.json",
    )

    with Path(report["artifacts"]["backlog_csv_path"]).open(
        newline="",
        encoding="utf-8",
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 7
    assert rows[0].keys() >= {
        "priority_tier",
        "priority_score",
        "backlog_id",
        "case_type",
        "failure_type",
        "requested_real_cases",
        "requested_manual_cases",
        "target_actions",
        "collection_prompt",
    }
    assert rows[0]["backlog_id"] == "layer_generate_case__provider_failure"
    assert rows[0]["requested_real_cases"] == "2"


def test_data_expansion_backlog_script_writes_artifacts_and_summary(tmp_path):
    result, _, report_path = _run_backlog(tmp_path)

    assert result.returncode == 0, result.stderr
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert Path(report["artifacts"]["backlog_json_path"]).exists()
    assert Path(report["artifacts"]["backlog_csv_path"]).exists()
    assert "Data expansion backlog:" in result.stdout
    assert "Backlog items: 7" in result.stdout
    assert "Requested real cases: 14" in result.stdout
    assert "Requested manual cases: 7" in result.stdout
    assert "layer_generate_case__provider_failure" in result.stdout
