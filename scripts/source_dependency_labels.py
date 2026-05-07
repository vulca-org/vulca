"""Export reviewed source-dependency labels for tiny training datasets."""
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

from vulca.learning.source_dependency_labels import (  # noqa: E402
    write_source_dependency_label_pack,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Write a sanitized source-dependency label JSONL and manifest from "
            "completed real_source_dependency_review JSONL items."
        )
    )
    parser.add_argument("--input", required=True, help="Reviewed review-item JSONL path")
    parser.add_argument("--output", required=True, help="Output label JSONL path")
    parser.add_argument("--manifest", required=True, help="Output label manifest path")
    parser.add_argument("--source-id", required=True, help="Stable label source id")
    parser.add_argument("--reviewer", default="", help="Reviewer id/name")
    parser.add_argument(
        "--reviewed-at",
        default="",
        help="Review timestamp, ISO-8601 UTC recommended",
    )
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow unknown labels; default requires completed human_review fields",
    )
    args = parser.parse_args(argv)

    try:
        result = write_source_dependency_label_pack(
            input_path=args.input,
            output_path=args.output,
            manifest_path=args.manifest,
            source_id=args.source_id,
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at or None,
            require_complete=not args.allow_incomplete,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(f"Source dependency labels: {result.record_count}")
    print(f"Label JSONL: {result.output_path}")
    print(f"Label manifest: {result.manifest_path}")
    print(f"Source dependency counts: {result.counts_by_source_dependency}")
    print(f"Decision basis counts: {result.counts_by_decision_basis}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
