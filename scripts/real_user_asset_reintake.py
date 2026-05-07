"""Write a safe re-intake task pack from a real user asset coverage report."""
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

from vulca.learning.real_user_asset_reintake import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    write_real_user_asset_reintake_pack,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Turn a safe real-user asset coverage report into JSON/Markdown "
            "tasks for re-intaking missing source images."
        )
    )
    parser.add_argument(
        "--coverage-report",
        required=True,
        help="Coverage JSON from scripts/real_user_asset_coverage.py.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for report and Markdown tasks (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Stable JSON report path (default: OUTPUT_DIR/real_user_asset_reintake_report.json).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = write_real_user_asset_reintake_pack(
            coverage_report_path=args.coverage_report,
            output_dir=args.output_dir,
            report_path=args.report or None,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    artifacts = report["artifacts"]
    summary = report["summary"]
    print(f"Re-intake report: {artifacts['report_path']}")
    print(f"Re-intake Markdown: {artifacts['markdown_path']}")
    print(f"Coverage records: {summary['coverage_record_count']}")
    print(f"Ready records: {summary['ready_count']}")
    print(f"Re-intake tasks: {summary['task_count']}")
    print(f"Status: {report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
