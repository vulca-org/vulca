"""Run tiny_action_model feature ablation on an exported tiny dataset."""
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

from vulca.learning.tiny_dataset import DATASET_SPLITS  # noqa: E402
from vulca.learning.tiny_feature_ablation import (  # noqa: E402
    DEFAULT_OUTPUT_PATH,
    run_tiny_feature_ablation_report_for_dataset,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Measure how tiny_action_model_v1 changes when strong input "
            "feature groups are removed from a tiny dataset."
        )
    )
    parser.add_argument("--dataset", required=True, help="Tiny dataset JSONL path.")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Output JSON report path (default: {DEFAULT_OUTPUT_PATH}).",
    )
    parser.add_argument(
        "--split",
        default="test",
        choices=DATASET_SPLITS,
        help="Dataset split to evaluate.",
    )
    parser.add_argument(
        "--train-split",
        default="train",
        choices=DATASET_SPLITS,
        help="Dataset split used to fit train-derived baselines.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_tiny_feature_ablation_report_for_dataset(
            dataset_path=args.dataset,
            output_path=args.output,
            eval_split=args.split,
            train_split=args.train_split,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    print(f"Tiny feature ablation report: {args.output}")
    print(f"Policy: {report['policy_name']}")
    print(f"Examples: {report['example_count']}")
    for variant in report["variant_reports"]:
        policy_report = variant["policy_report"]
        print(
            f"{variant['variant_id']} action_accuracy: "
            f"{policy_report['action_accuracy']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
