"""Train and run the provider-free tiny action model prediction JSONL."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vulca.learning.tiny_action_model import (  # noqa: E402
    POLICY_TINY_ACTION_MODEL,
    write_tiny_action_model_predictions,
)
from vulca.learning.tiny_dataset import DATASET_SPLITS  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fit the provider-free tiny action classifier on a tiny dataset "
            "train split and emit prediction JSONL for evaluation."
        )
    )
    parser.add_argument("dataset", help="Path to tiny dataset JSONL.")
    parser.add_argument(
        "--split",
        default="test",
        choices=DATASET_SPLITS,
        help="Dataset split to predict.",
    )
    parser.add_argument(
        "--train-split",
        default="train",
        choices=DATASET_SPLITS,
        help="Dataset split used to fit sparse feature weights.",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output prediction JSONL path.",
    )
    args = parser.parse_args(argv)

    result = write_tiny_action_model_predictions(
        dataset_path=args.dataset,
        output_path=args.output,
        split=args.split,
        train_split=args.train_split,
    )
    print(f"{POLICY_TINY_ACTION_MODEL} predictions: {result.prediction_count}")
    print(f"split: {result.split}")
    print(f"train_split: {result.train_split}")
    print(f"output: {result.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
