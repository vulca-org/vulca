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
SCRIPT = ROOT / "scripts" / "open_model_signal_review_table.py"


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def _signal_record(
    signal_id: str,
    *,
    model_id: str = "florence_2",
    case_type: str = "redraw_case",
    case_id: str = "redraw_case_1",
    status: str = "completed",
    signals: dict | None = None,
) -> dict:
    signal_block = {
        "status": status,
        "signal_source": "local_runner",
        "label_source": "assistant_labeled",
        "review_status": "needs_human_review",
        "caption_candidates": ["A red car parked by the road."],
        "ocr_text": ["JAMES CO.UK"],
        "source_image": {
            "available": status == "completed",
            "ref_kind": "repo_relative",
            "width": 4032,
            "height": 3024,
        },
    }
    if signals is not None:
        signal_block.update(signals)
    return {
        "schema_version": 1,
        "case_type": "learning_open_model_signal_record",
        "signal_id": signal_id,
        "example_id": f"tiny_{signal_id}",
        "source": {"kind": "local_seed", "split": "seed"},
        "source_case": {
            "case_type": case_type,
            "case_id": case_id,
            "schema_version": 1,
        },
        "model": {
            "id": model_id,
            "name": model_id,
            "model_role": "mask_proposal"
            if model_id == "segment_anything_sam_vit"
            else "vision_caption_grounding_ocr",
            "output_training_policy": "weak_signal_requires_review",
            "default_runtime_enabled": False,
        },
        "input_summary": {
            "case_type": case_type,
            "case_id": case_id,
            "source_image_ref_kind": "repo_relative",
        },
        "signals": signal_block,
        "training_use": {
            "default_training_input": False,
            "requires_manual_review_for_training_labels": True,
            "review_status": "needs_human_review",
        },
    }


def test_open_model_signal_review_table_exports_completed_rows_only(tmp_path):
    from vulca.learning.open_model_signal_review_table import (
        run_open_model_signal_review_table,
    )

    input_path = tmp_path / "signals.jsonl"
    _write_jsonl(
        input_path,
        [
            _signal_record("open_signal_completed_a"),
            _signal_record("open_signal_skipped", status="skipped"),
            _signal_record(
                "open_signal_dry",
                status="dry_run_pending_model_execution",
                signals={"signal_source": "dry_run"},
            ),
            _signal_record(
                "open_signal_completed_sam",
                model_id="segment_anything_sam_vit",
                case_type="decompose_case",
                case_id="decompose_case_1",
                signals={
                    "mask_count": 3,
                    "total_mask_area_pct": 0.42,
                    "boundary_complexity": "medium",
                    "mask_coverage_candidates": [
                        {"area_pct": 0.21, "bbox": [4, 8, 40, 64]},
                    ],
                },
            ),
        ],
    )

    report = run_open_model_signal_review_table(
        input_path=input_path,
        output_dir=tmp_path / "review_table",
        report_path=tmp_path / "review_table_report.json",
        reviewed_output_path=tmp_path / "signals.reviewed.jsonl",
    )

    assert report["case_type"] == "learning_open_model_signal_review_table"
    assert report["status"] == "ready_for_human_review"
    assert report["summary"]["input_record_count"] == 4
    assert report["summary"]["row_count"] == 2
    assert report["summary"]["status_counts"] == {
        "completed": 2,
        "dry_run_pending_model_execution": 1,
        "skipped": 1,
    }
    assert report["summary"]["excluded_status_counts"] == {
        "dry_run_pending_model_execution": 1,
        "skipped": 1,
    }

    rows = _read_jsonl(Path(report["artifacts"]["review_table_jsonl_path"]))
    assert [row["signal_id"] for row in rows] == [
        "open_signal_completed_sam",
        "open_signal_completed_a",
    ]
    assert all(row["signal_status"] == "completed" for row in rows)
    assert {row["suggested_review_decision"] for row in rows} == {"hold"}
    assert rows[0]["model_id"] == "segment_anything_sam_vit"
    assert rows[0]["mask_count"] == 3
    assert rows[0]["total_mask_area_pct"] == 0.42
    assert rows[0]["boundary_complexity"] == "medium"
    assert rows[1]["caption_preview"] == "A red car parked by the road."
    assert rows[1]["ocr_preview"] == "JAMES CO.UK"
    assert "open_model_signal_review.py review" in rows[0]["review_command_promote"]
    assert "--decision promote" in rows[0]["review_command_promote"]
    assert "--decision reject" in rows[0]["review_command_reject"]
    assert "--decision hold" in rows[0]["review_command_hold"]


def test_open_model_signal_review_table_writes_csv_and_markdown(tmp_path):
    from vulca.learning.open_model_signal_review_table import (
        run_open_model_signal_review_table,
    )

    input_path = tmp_path / "signals.jsonl"
    _write_jsonl(
        input_path,
        [
            _signal_record("open_signal_completed_a"),
            _signal_record("open_signal_skipped", status="skipped"),
        ],
    )

    report = run_open_model_signal_review_table(
        input_path=input_path,
        output_dir=tmp_path / "review_table",
    )

    csv_path = Path(report["artifacts"]["review_table_csv_path"])
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert rows[0]["signal_id"] == "open_signal_completed_a"
    assert rows[0]["caption_preview"] == "A red car parked by the road."
    assert rows[0]["review_command_promote"]

    markdown = Path(report["artifacts"]["review_table_markdown_path"]).read_text(
        encoding="utf-8"
    )
    assert "| signal_id | model_id | source_case_type |" in markdown
    assert "open_signal_completed_a" in markdown
    assert "open_signal_skipped" not in markdown


def test_open_model_signal_review_table_cli_writes_artifacts(tmp_path):
    input_path = tmp_path / "signals.jsonl"
    output_dir = tmp_path / "review_table"
    report_path = tmp_path / "review_table_report.json"
    _write_jsonl(input_path, [_signal_record("open_signal_completed_a")])

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input",
            str(input_path),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report_path),
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["row_count"] == 1
    assert Path(report["artifacts"]["review_table_jsonl_path"]).exists()
    assert Path(report["artifacts"]["review_table_csv_path"]).exists()
    assert Path(report["artifacts"]["review_table_markdown_path"]).exists()
    assert "Open-model signal review table:" in result.stdout
    assert "Reviewable rows: 1" in result.stdout
