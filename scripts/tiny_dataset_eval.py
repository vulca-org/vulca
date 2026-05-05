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
    DATASET_SPLITS,
    TINY_DATASET_EVAL_POLICIES,
    build_tiny_dataset_comparison_report,
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
        "--split",
        default="all",
        choices=("all", *DATASET_SPLITS),
        help="Dataset split to evaluate.",
    )
    parser.add_argument(
        "--train-split",
        default="train",
        choices=DATASET_SPLITS,
        help="Training split used by train-derived baselines.",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Write a comparison report for default tiny baselines.",
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

    dataset_split = None if args.split == "all" else args.split
    examples = load_tiny_dataset_examples(args.dataset)
    if args.compare:
        eval_split = dataset_split or "test"
        report = build_tiny_dataset_comparison_report(
            examples,
            train_split=args.train_split,
            eval_split=eval_split,
        )
    else:
        report = evaluate_tiny_dataset_examples(
            examples,
            policy_name=args.policy,
            dataset_split=dataset_split,
            train_split=args.train_split,
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

    if args.compare:
        for policy_name in sorted(report["policy_reports"]):
            policy_report = report["policy_reports"][policy_name]
            print(f"{policy_name} evaluated_count: {policy_report['evaluated_count']}")
            print(f"{policy_name} skipped_count: {policy_report['skipped_count']}")
            print(f"{policy_name} action_accuracy: {policy_report['action_accuracy']}")
    else:
        print(f"{args.policy} evaluated_count: {report['evaluated_count']}")
        print(f"{args.policy} skipped_count: {report['skipped_count']}")
        print(f"{args.policy} action_accuracy: {report['action_accuracy']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
