"""Write a review table for completed open-model signal records."""
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

from vulca.learning.open_model_signal_review_table import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REVIEWABLE_STATUSES,
    run_open_model_signal_review_table,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export JSONL/CSV/Markdown rows for human review of completed "
            "open-model signal records."
        )
    )
    parser.add_argument("--input", required=True, help="Open-model signal JSONL path.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for review table artifacts.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Stable JSON report path (default: OUTPUT_DIR/open_model_signal_review_table_report.json).",
    )
    parser.add_argument(
        "--reviewed-output",
        default="",
        help="Reviewed signal JSONL path used in generated review commands.",
    )
    parser.add_argument(
        "--include-status",
        action="append",
        default=[],
        help=(
            "Signal status to include; repeat for multiple statuses. "
            f"Default: {DEFAULT_REVIEWABLE_STATUSES}."
        ),
    )
    parser.add_argument(
        "--max-preview-chars",
        type=int,
        default=120,
        help="Maximum caption/OCR preview length per row.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_open_model_signal_review_table(
            input_path=args.input,
            output_dir=args.output_dir,
            report_path=args.report or None,
            reviewed_output_path=args.reviewed_output or None,
            reviewable_statuses=tuple(args.include_status)
            or DEFAULT_REVIEWABLE_STATUSES,
            max_preview_chars=args.max_preview_chars,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    artifacts = report["artifacts"]
    summary = report["summary"]
    print(f"Open-model signal review table: {artifacts['report_path']}")
    print(f"JSONL: {artifacts['review_table_jsonl_path']}")
    print(f"CSV: {artifacts['review_table_csv_path']}")
    print(f"Markdown: {artifacts['review_table_markdown_path']}")
    print(f"Input records: {summary['input_record_count']}")
    print(f"Reviewable rows: {summary['row_count']}")
    print(f"Status counts: {summary['status_counts']}")
    print(f"Review table status: {report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
