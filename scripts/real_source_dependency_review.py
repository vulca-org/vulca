"""Write a human review pack for real source-dependency labels."""
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

from vulca.learning.real_source_dependency_review import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    write_real_source_dependency_review_pack,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a safe JSONL and Markdown review pack for judging whether "
            "real user cases require source context."
        )
    )
    parser.add_argument(
        "--audit-report",
        required=True,
        help=(
            "real_source_context_audit_report.json or "
            "real_source_context_recovery_audit_report.json."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for review pack (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--report",
        default="",
        help=(
            "Review report path "
            "(default: OUTPUT_DIR/real_source_dependency_review_report.json)."
        ),
    )
    parser.add_argument(
        "--review-template",
        default="",
        help=(
            "Review JSONL template path "
            "(default: OUTPUT_DIR/real_source_dependency_review.template.jsonl)."
        ),
    )
    parser.add_argument(
        "--markdown",
        default="",
        help=(
            "Markdown checklist path "
            "(default: OUTPUT_DIR/real_source_dependency_review.md)."
        ),
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = write_real_source_dependency_review_pack(
            audit_report_path=args.audit_report,
            output_dir=args.output_dir,
            report_path=args.report or None,
            review_template_path=args.review_template or None,
            markdown_path=args.markdown or None,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    print(f"Real source dependency review: {report['artifacts']['report_path']}")
    print(f"Review items: {summary['review_item_count']}")
    print(
        "Suggested source_dependency: "
        f"{summary['counts_by_suggested_source_dependency']}"
    )
    print(f"Markdown checklist: {report['artifacts']['markdown_checklist_path']}")
    print(f"Review template: {report['artifacts']['review_template_jsonl_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
