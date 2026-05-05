"""Offline evaluation entrypoint for exported tiny datasets."""
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

from vulca.learning.tiny_dataset import (  # noqa: E402
    POLICY_REDRAW_OBSERVABLE_SIGNAL,
    TINY_DATASET_EVAL_POLICIES,
    evaluate_tiny_dataset_examples,
    load_tiny_dataset_examples,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score provider-free baselines on exported tiny dataset JSONL."
    )
    parser.add_argument("dataset", help="Path to tiny dataset JSONL.")
    parser.add_argument(
        "--policy",
        default=POLICY_REDRAW_OBSERVABLE_SIGNAL,
        choices=sorted(TINY_DATASET_EVAL_POLICIES),
        help="Offline policy to evaluate.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="",
        help="Optional JSON report output path.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON to stdout when --output is omitted.",
    )
    args = parser.parse_args(argv)

    report = evaluate_tiny_dataset_examples(
        load_tiny_dataset_examples(args.dataset),
        policy_name=args.policy,
    )
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"Tiny dataset eval report: {output_path}")
    else:
        indent = 2 if args.pretty else None
        print(json.dumps(report, indent=indent, sort_keys=True))

    print(f"{args.policy} evaluated_count: {report['evaluated_count']}")
    print(f"{args.policy} skipped_count: {report['skipped_count']}")
    print(f"{args.policy} action_accuracy: {report['action_accuracy']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
