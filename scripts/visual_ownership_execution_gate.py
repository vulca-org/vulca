"""Run the provider-free visual ownership execution gate."""

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

from vulca.learning.visual_ownership_execution_gate import (  # noqa: E402
    DEFAULT_GATE_NAME,
    DEFAULT_REPORT_NAME,
    run_visual_ownership_execution_gate,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate visual ownership plans before agent/runtime execution.",
    )
    parser.add_argument(
        "--plans",
        required=True,
        help="Visual ownership plan JSONL path.",
    )
    parser.add_argument(
        "--gates",
        default="",
        help=f"Gate JSONL path (default: alongside plans as {DEFAULT_GATE_NAME}).",
    )
    parser.add_argument(
        "--report",
        default="",
        help=f"Report JSON path (default: alongside plans as {DEFAULT_REPORT_NAME}).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print full JSON report after writing it.",
    )
    args = parser.parse_args(argv)

    plan_path = Path(args.plans)
    gate_path = Path(args.gates) if args.gates else plan_path.parent / DEFAULT_GATE_NAME
    report_path = (
        Path(args.report) if args.report else plan_path.parent / DEFAULT_REPORT_NAME
    )
    try:
        report = run_visual_ownership_execution_gate(
            plan_path=plan_path,
            gate_path=gate_path,
            report_path=report_path,
        )
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    print(f"Visual ownership execution gate report: {report_path}")
    print(f"Visual ownership execution gates: {gate_path}")
    print(f"Plans: {summary['plan_count']}")
    print(f"Agent execution ready: {summary['agent_execution_ready_count']}")
    print(f"Blocked: {summary['blocked_count']}")
    print(f"Production runtime ready: {summary['production_runtime_ready_count']}")
    print(f"Source-context gaps: {summary['source_context_gap_count']}")
    print(f"Incomplete plans: {summary['incomplete_plan_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
