"""Audit residual fallback-agent dry-run decisions."""

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

from vulca.learning.fallback_residual_audit import (  # noqa: E402
    DEFAULT_REPORT_NAME,
    run_fallback_residual_audit,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Classify residual fallback-agent dry-run decisions.",
    )
    parser.add_argument(
        "--decision-path",
        required=True,
        help="Dry-run decision JSONL path.",
    )
    parser.add_argument(
        "--report",
        default="",
        help=f"Report JSON path (default: alongside decision path as {DEFAULT_REPORT_NAME}).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print full JSON report after writing it.",
    )
    args = parser.parse_args(argv)

    decision_path = Path(args.decision_path)
    report_path = Path(args.report) if args.report else decision_path.parent / DEFAULT_REPORT_NAME
    try:
        report = run_fallback_residual_audit(
            decision_path=decision_path,
            report_path=report_path,
        )
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    print(f"Fallback residual audit: {report_path}")
    print(f"Decisions: {summary['decision_count']}")
    print(f"Fallback agent decisions: {summary['fallback_agent_count']}")
    print(f"Tiny router candidates: {summary['tiny_router_candidate_count']}")
    print(f"Agent-required residuals: {summary['agent_required_count']}")
    print(f"Source-context gaps: {summary['source_context_gap_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
