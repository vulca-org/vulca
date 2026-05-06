"""Review and promote open-model signal records for auxiliary training use."""
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

from vulca.learning.open_model_signal_review import (  # noqa: E402
    REVIEW_DECISIONS,
    review_open_model_signal_log,
    write_promoted_open_model_signal_pack,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Human-review open-model signal records and explicitly promote "
            "reviewed signals into an auxiliary-signal manifest."
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    review = sub.add_parser("review", help="Review one signal record by signal_id.")
    review.add_argument("--input", required=True, help="Input signal JSONL path.")
    review.add_argument("--output", default="", help="Reviewed JSONL output path.")
    review.add_argument("--signal-id", required=True, help="Signal id to review.")
    review.add_argument(
        "--decision",
        required=True,
        choices=sorted(REVIEW_DECISIONS),
        help="Human review decision.",
    )
    review.add_argument("--reviewer", default="", help="Reviewer identifier.")
    review.add_argument("--reviewed-at", default="", help="UTC review timestamp.")
    review.add_argument("--notes", default="", help="Review notes.")

    promote = sub.add_parser(
        "promote",
        help="Write a promoted-only signal JSONL plus promotion manifest.",
    )
    promote.add_argument("--input", required=True, help="Reviewed signal JSONL path.")
    promote.add_argument("--output", required=True, help="Promoted signal JSONL path.")
    promote.add_argument("--manifest", required=True, help="Promotion manifest path.")
    promote.add_argument("--source-id", required=True, help="Promotion source id.")
    promote.add_argument(
        "--pretty",
        action="store_true",
        help="Print the pack result as pretty JSON.",
    )

    args = parser.parse_args(argv)

    try:
        if args.command == "review":
            result = review_open_model_signal_log(
                args.input,
                signal_id=args.signal_id,
                decision=args.decision,
                output_path=args.output or None,
                reviewer=args.reviewer,
                reviewed_at=args.reviewed_at or None,
                notes=args.notes,
            )
            print(f"Reviewed signal: {result.signal_id}")
            print(f"Review status: {result.review_status}")
            print(f"Reviewed output: {result.output_path}")
            return 0

        result = write_promoted_open_model_signal_pack(
            input_path=args.input,
            output_path=args.output,
            manifest_path=args.manifest,
            source_id=args.source_id,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(
            json.dumps(
                {
                    "output_path": result.output_path,
                    "manifest_path": result.manifest_path,
                    "source_id": result.source_id,
                    "promoted_count": result.promoted_count,
                    "counts_by_model": result.counts_by_model,
                },
                indent=2,
                sort_keys=True,
            )
        )
    print(f"Promoted signal output: {result.output_path}")
    print(f"Promotion manifest: {result.manifest_path}")
    print(f"Promoted signals: {result.promoted_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
