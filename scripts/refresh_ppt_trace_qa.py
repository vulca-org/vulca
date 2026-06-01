from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DELIVERY_GATE_RE = re.compile(r"Delivery gate:\s*`([^`]+)`")
LAYOUT_SUMMARY_RE = re.compile(r"Checked\s+(\d+)\s+layout file\(s\):\s+(\d+)\s+error\(s\),\s+(\d+)\s+warning\(s\)\.")


def load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def parse_delivery_gate(path: Path) -> str:
    body = path.read_text(encoding="utf-8")
    match = DELIVERY_GATE_RE.search(body)
    if not match:
        raise ValueError(f"delivery report {path} does not contain a Delivery gate line")
    return match.group(1)


def parse_layout_summary(path: Path) -> dict[str, int]:
    body = path.read_text(encoding="utf-8")
    match = LAYOUT_SUMMARY_RE.search(body)
    if not match:
        raise ValueError(f"layout report {path} does not contain a recognized summary")
    return {
        "layout_files": int(match.group(1)),
        "layout_errors": int(match.group(2)),
        "layout_warnings": int(match.group(3)),
    }


def refreshed_manifest(
    trace: dict[str, Any],
    delivery_gate: str,
    layout_summary: dict[str, int],
    aesthetic_status: str,
) -> dict[str, Any]:
    updated = json.loads(json.dumps(trace))
    updated["qa_outcome_refresh"] = {
        "status": "refreshed",
        "delivery_gate": delivery_gate,
        **layout_summary,
        "aesthetic_status": aesthetic_status,
        "release_note": "public release remains blocked unless render inspection and human approval pass",
    }
    updated["release_decision"] = "public_blocked"

    structural = (
        f"post_qa_refresh: delivery={delivery_gate}; "
        f"layout_errors={layout_summary['layout_errors']}; "
        f"layout_warnings={layout_summary['layout_warnings']}"
    )
    for slide in updated.get("slides", []):
        if not isinstance(slide, dict):
            continue
        slide["structural_qa"] = structural
        slide["aesthetic_qa"] = aesthetic_status
        gate_inputs = slide.setdefault("release_gate_inputs", {})
        if isinstance(gate_inputs, dict):
            gate_inputs.setdefault("render_inspection", "not-run")
            gate_inputs.setdefault("human_approval", "not-recorded")
            if gate_inputs.get("render_inspection") in {"pass", "passed"}:
                gate_inputs["render_inspection"] = "not-run"
            if gate_inputs.get("human_approval") in {"approved", "pass", "passed"}:
                gate_inputs["human_approval"] = "not-recorded"
    return updated


def refresh_trace_manifest(
    trace_path: Path,
    delivery_report_path: Path,
    layout_report_path: Path,
    *,
    dry_run: bool = False,
    aesthetic_status: str = "contact_sheet_reviewed_internal_only",
) -> dict[str, Any]:
    trace = load_json_object(trace_path)
    delivery_gate = parse_delivery_gate(delivery_report_path)
    layout_summary = parse_layout_summary(layout_report_path)
    updated = refreshed_manifest(trace, delivery_gate, layout_summary, aesthetic_status)

    would_update = updated != trace
    backup_path = trace_path.with_suffix(f"{trace_path.suffix}.bak")
    summary = {
        "trace_path": str(trace_path),
        "would_update": would_update,
        "delivery_gate": delivery_gate,
        **layout_summary,
        "backup_path": None if dry_run or not would_update else str(backup_path),
    }
    if dry_run or not would_update:
        return summary

    backup_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    tmp_path = trace_path.with_suffix(f"{trace_path.suffix}.tmp")
    tmp_path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(trace_path)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Refresh PPT trace_manifest.json with post-QA outcomes.")
    parser.add_argument("--trace", required=True, type=Path)
    parser.add_argument("--delivery-report", required=True, type=Path)
    parser.add_argument("--layout-report", required=True, type=Path)
    parser.add_argument("--aesthetic-status", default="contact_sheet_reviewed_internal_only")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = refresh_trace_manifest(
        args.trace,
        args.delivery_report,
        args.layout_report,
        dry_run=args.dry_run,
        aesthetic_status=args.aesthetic_status,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
