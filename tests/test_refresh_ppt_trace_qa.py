from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.refresh_ppt_trace_qa import refresh_trace_manifest


def write_trace(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "arm_id": "run2_skill",
                "release_decision": "public_blocked",
                "slides": [
                    {
                        "slide_id": "slide_01",
                        "structural_qa": "pending validate_pptx_delivery.py after PPTX export",
                        "aesthetic_qa": "pending contact-sheet review and rubric scoring",
                        "release_gate_inputs": {
                            "render_inspection": "not-run",
                            "asset_provenance_complete": True,
                            "human_approval": "not-recorded",
                        },
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def write_delivery(path: Path) -> None:
    path.write_text(
        "# PPT Delivery QA Report\n\n"
        "- Delivery gate: `internal-demo-ok-public-blocked`\n"
        "- Slide count: `6`\n"
        "- Human review required: `True`\n\n"
        "### Gate Notes\n\n"
        "- Errors: `0`\n"
        "- Warnings: `1`\n",
        encoding="utf-8",
    )


def write_layout(path: Path) -> None:
    path.write_text("Checked 6 layout file(s): 0 error(s), 8 warning(s).\n", encoding="utf-8")


def test_refresh_trace_manifest_dry_run_does_not_write(tmp_path: Path) -> None:
    trace = tmp_path / "trace_manifest.json"
    delivery = tmp_path / "delivery_report.md"
    layout = tmp_path / "layout_quality.txt"
    write_trace(trace)
    write_delivery(delivery)
    write_layout(layout)
    before = trace.read_text(encoding="utf-8")

    summary = refresh_trace_manifest(
        trace,
        delivery,
        layout,
        dry_run=True,
        aesthetic_status="gemini_contact_sheet_reviewed_internal_only",
    )

    assert summary["would_update"] is True
    assert summary["backup_path"] is None
    assert trace.read_text(encoding="utf-8") == before


def test_refresh_trace_manifest_writes_backup_and_post_qa_outcomes(tmp_path: Path) -> None:
    trace = tmp_path / "trace_manifest.json"
    delivery = tmp_path / "delivery_report.md"
    layout = tmp_path / "layout_quality.txt"
    write_trace(trace)
    write_delivery(delivery)
    write_layout(layout)

    summary = refresh_trace_manifest(
        trace,
        delivery,
        layout,
        dry_run=False,
        aesthetic_status="gemini_contact_sheet_reviewed_internal_only",
    )

    data = json.loads(trace.read_text(encoding="utf-8"))
    backup = trace.with_suffix(".json.bak")
    assert summary["would_update"] is True
    assert summary["backup_path"] == str(backup)
    assert backup.exists()
    assert data["qa_outcome_refresh"]["delivery_gate"] == "internal-demo-ok-public-blocked"
    assert data["qa_outcome_refresh"]["layout_errors"] == 0
    assert (
        data["slides"][0]["structural_qa"]
        == "post_qa_refresh: delivery=internal-demo-ok-public-blocked; layout_errors=0; layout_warnings=8"
    )
    assert data["slides"][0]["aesthetic_qa"] == "gemini_contact_sheet_reviewed_internal_only"
    assert data["slides"][0]["release_gate_inputs"]["render_inspection"] == "not-run"
    assert data["slides"][0]["release_gate_inputs"]["human_approval"] == "not-recorded"


def test_refresh_trace_manifest_invalid_layout_does_not_overwrite(tmp_path: Path) -> None:
    trace = tmp_path / "trace_manifest.json"
    delivery = tmp_path / "delivery_report.md"
    layout = tmp_path / "layout_quality.txt"
    write_trace(trace)
    write_delivery(delivery)
    layout.write_text("layout checker crashed\n", encoding="utf-8")
    before = trace.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="layout report"):
        refresh_trace_manifest(trace, delivery, layout, dry_run=False)

    assert trace.read_text(encoding="utf-8") == before
    assert not trace.with_suffix(".json.bak").exists()
