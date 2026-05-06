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


def _coverage_record(case_id: str, asset_status: str, **extra) -> dict:
    return {
        "case_id": case_id,
        "case_type": extra.pop("case_type", "layer_generate_case"),
        "source": {
            "source_id": "real_user_fixture",
            "kind": "user_case_log",
            "privacy_scope": "private",
            "record_index": extra.pop("record_index", 0),
        },
        "asset_status": asset_status,
        "open_model_runnable": asset_status == "available",
        "source_image": {
            "has_ref": asset_status not in {"missing_source_reference", "source_hint_only"},
            "ref_kind": extra.pop("ref_kind", "missing"),
            "available": asset_status == "available",
        },
        "path_hints": {
            "source_path_hint_count": extra.pop("source_path_hint_count", 0),
            "private_ref_count": extra.pop("private_ref_count", 0),
            "remote_ref_count": 0,
        },
        "next_action": extra.pop("next_action", "manual_review"),
        **extra,
    }


def _write_coverage(path: Path) -> None:
    records = [
        _coverage_record("ready", "available", case_type="redraw_case"),
        _coverage_record(
            "brief_hint",
            "source_hint_only",
            source_path_hint_count=1,
            private_ref_count=1,
        ),
        _coverage_record("missing_ref", "missing_source_reference", record_index=2),
        _coverage_record(
            "needs_map",
            "needs_private_asset_map",
            ref_kind="private_uri",
            record_index=3,
        ),
    ]
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "case_type": "learning_real_user_asset_coverage_report",
                "summary": {"example_count": len(records)},
                "records": records,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_real_user_asset_reintake_pack_writes_safe_tasks(tmp_path):
    from vulca.learning.real_user_asset_reintake import (
        write_real_user_asset_reintake_pack,
    )

    coverage = tmp_path / "coverage.json"
    output_dir = tmp_path / "reintake"
    _write_coverage(coverage)

    report = write_real_user_asset_reintake_pack(
        coverage_report_path=coverage,
        output_dir=output_dir,
    )

    assert report["case_type"] == "learning_real_user_asset_reintake_report"
    assert report["status"] == "needs_user_assets"
    assert report["summary"] == {
        "coverage_record_count": 4,
        "task_count": 3,
        "ready_count": 1,
        "counts_by_action": {
            "add_source_image_ref": 1,
            "provide_private_asset_map": 1,
            "re_intake_with_source_image": 1,
        },
        "counts_by_asset_status": {
            "missing_source_reference": 1,
            "needs_private_asset_map": 1,
            "source_hint_only": 1,
        },
    }
    assert [task["case_id"] for task in report["tasks"]] == [
        "needs_map",
        "brief_hint",
        "missing_ref",
    ]
    assert report["tasks"][0]["required_user_asset"] == "private_asset_map_entry"
    assert report["tasks"][1]["required_user_asset"] == "source_image_or_source_artifact"
    assert report["tasks"][2]["required_user_asset"] == "source_image"
    assert (output_dir / report["artifacts"]["markdown_path"]).exists()

    encoded = json.dumps(report, sort_keys=True)
    markdown = (output_dir / report["artifacts"]["markdown_path"]).read_text(
        encoding="utf-8"
    )
    assert "private://local_path" not in encoded
    assert "private://local_path" not in markdown
    assert str(tmp_path) not in encoded
    assert "brief_hint" in markdown
    assert "missing_ref" in markdown


def test_real_user_asset_reintake_cli_writes_pack(tmp_path):
    coverage = tmp_path / "coverage.json"
    output_dir = tmp_path / "reintake"
    _write_coverage(coverage)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/real_user_asset_reintake.py"),
            "--coverage-report",
            str(coverage),
            "--output-dir",
            str(output_dir),
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads((output_dir / "real_user_asset_reintake_report.json").read_text())
    assert report["summary"]["task_count"] == 3
    assert "Re-intake tasks: 3" in result.stdout
