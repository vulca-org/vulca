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
EXPORT_SCRIPT = ROOT / "scripts" / "model_selection_review_table.py"


def _read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _run_export(tmp_path, *extra_args):
    output_dir = tmp_path / "model_selection_review"
    report_path = tmp_path / "model_selection_review_report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(EXPORT_SCRIPT),
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


def test_model_selection_review_table_exports_eval_rows_for_manual_review(tmp_path):
    from vulca.learning.model_selection_review_table import (
        run_model_selection_review_table,
    )

    report = run_model_selection_review_table(
        repo_root=ROOT,
        output_dir=tmp_path / "review_table",
        report_path=tmp_path / "review_table_report.json",
    )

    assert report["case_type"] == "learning_model_selection_review_table"
    assert report["status"] == "ready_for_review"
    assert report["summary"]["row_count"] == 17
    assert report["summary"]["primary_mismatch_count"] == 0
    assert report["summary"]["baseline_mismatch_count"] == 8
    assert report["summary"]["policy_disagreement_count"] >= 8
    assert report["selection"]["primary_policy"] == "tiny_action_model_v1"
    assert report["selection"]["baseline_policy"] == "tiny_agent_v0"
    assert report["selection"]["guardrail_policy"] == "redraw_observable_signal"

    rows = _read_jsonl(Path(report["artifacts"]["review_table_jsonl_path"]))
    assert len(rows) == 17
    assert rows == sorted(
        rows,
        key=lambda item: (
            -item["priority_score"],
            item["case_type"],
            item["failure_type"],
            item["case_id"],
        ),
    )
    first = rows[0]
    assert first["split"] == "test"
    assert first["primary_policy"] == "tiny_action_model_v1"
    assert first["primary_correct"] is True
    assert first["baseline_policy"] == "tiny_agent_v0"
    assert first["target_action"]
    assert first["review_action"] in {
        "collect_more_real_case",
        "verify_policy_disagreement",
    }
    assert set(first["policies"]) >= {
        "majority_action",
        "tiny_action_model_v1",
        "tiny_agent_v0",
    }


def test_model_selection_review_table_marks_workload_data_collection(tmp_path):
    from vulca.learning.model_selection_review_table import (
        run_model_selection_review_table,
    )

    report = run_model_selection_review_table(
        repo_root=ROOT,
        output_dir=tmp_path / "review_table",
        report_path=tmp_path / "review_table_report.json",
    )

    assert report["summary"]["workload_decision_counts"] == {
        "collect_more_real_cases": 9,
        "promote_with_guardrail": 8,
    }
    rows = _read_jsonl(Path(report["artifacts"]["review_table_jsonl_path"]))
    decompose_rows = [row for row in rows if row["case_type"] == "decompose_case"]
    layer_rows = [row for row in rows if row["case_type"] == "layer_generate_case"]
    redraw_rows = [row for row in rows if row["case_type"] == "redraw_case"]

    assert len(decompose_rows) == 3
    assert len(layer_rows) == 6
    assert len(redraw_rows) == 8
    assert all(row["workload_decision"] == "collect_more_real_cases" for row in decompose_rows)
    assert all(row["workload_decision"] == "collect_more_real_cases" for row in layer_rows)
    assert all(row["workload_decision"] == "promote_with_guardrail" for row in redraw_rows)
    assert any(row["source_kind"] == "user_case_log" for row in rows)


def test_model_selection_review_table_writes_csv_with_stable_columns(tmp_path):
    from vulca.learning.model_selection_review_table import (
        run_model_selection_review_table,
    )

    report = run_model_selection_review_table(
        repo_root=ROOT,
        output_dir=tmp_path / "review_table",
        report_path=tmp_path / "review_table_report.json",
    )

    csv_path = Path(report["artifacts"]["review_table_csv_path"])
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 17
    assert rows[0].keys() >= {
        "review_action",
        "priority_score",
        "case_type",
        "case_id",
        "source_kind",
        "source_id",
        "failure_type",
        "target_action",
        "primary_action",
        "primary_correct",
        "baseline_action",
        "baseline_correct",
        "guardrail_action",
        "policy_disagreement",
        "review_reason",
    }
    assert rows[0]["priority_score"]


def test_model_selection_review_table_script_writes_artifacts_and_summary(tmp_path):
    result, _, report_path = _run_export(tmp_path)

    assert result.returncode == 0, result.stderr
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert Path(report["artifacts"]["review_table_jsonl_path"]).exists()
    assert Path(report["artifacts"]["review_table_csv_path"]).exists()
    assert "Model selection review table:" in result.stdout
    assert "Review rows: 17" in result.stdout
    assert "Primary mismatches: 0" in result.stdout
    assert "Baseline mismatches: 8" in result.stdout
    assert "CSV:" in result.stdout
