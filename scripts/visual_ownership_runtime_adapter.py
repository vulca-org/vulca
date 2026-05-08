"""Build provider-free visual ownership runtime adapter requests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vulca.learning.visual_ownership_runtime_adapter import (  # noqa: E402
    DEFAULT_REPORT_NAME,
    DEFAULT_REQUEST_NAME,
    run_visual_ownership_runtime_adapter,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Convert ready visual ownership execution gates into provider-free "
            "runtime adapter requests."
        )
    )
    parser.add_argument(
        "--gates",
        required=True,
        help="Visual ownership execution gate JSONL path.",
    )
    parser.add_argument(
        "--requests",
        default="",
        help=f"Request JSONL path (default: alongside gates as {DEFAULT_REQUEST_NAME}).",
    )
    parser.add_argument(
        "--report",
        default="",
        help=f"Report JSON path (default: alongside gates as {DEFAULT_REPORT_NAME}).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print full JSON report after writing it.",
    )
    args = parser.parse_args(argv)

    gate_path = Path(args.gates)
    request_path = (
        Path(args.requests) if args.requests else gate_path.parent / DEFAULT_REQUEST_NAME
    )
    report_path = (
        Path(args.report) if args.report else gate_path.parent / DEFAULT_REPORT_NAME
    )
    try:
        report = run_visual_ownership_runtime_adapter(
            gate_path=gate_path,
            request_path=request_path,
            report_path=report_path,
        )
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    print(f"Visual ownership runtime adapter report: {report_path}")
    print(f"Visual ownership runtime requests: {request_path}")
    print(f"Gate records: {summary['gate_record_count']}")
    print(f"Adapter requests: {summary['adapter_request_count']}")
    print(f"Blocked gates: {summary['blocked_gate_count']}")
    print(
        "Production runtime candidates: "
        f"{summary['production_runtime_candidate_count']}"
    )
    print(f"Provider calls: {summary['provider_call_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
