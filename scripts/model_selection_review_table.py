"""Write the tiny model/agent per-case review table."""
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

from vulca.learning.model_selection_report import (  # noqa: E402
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
)
from vulca.learning.model_selection_review_table import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    run_model_selection_review_table,
)
from vulca.learning.tiny_dataset import DATASET_SPLITS  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run model selection and export a per-case JSONL/CSV review table "
            "with policy predictions, mismatches, and manual-review priorities."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Repository root (default: this script's repository).",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for generated review table artifacts.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Stable JSON report path (default: OUTPUT_DIR/model_selection_review_table_report.json).",
    )
    parser.add_argument(
        "--case-source-manifest",
        default=str(DEFAULT_COMBINED_CASE_SOURCE_MANIFEST),
        help="Combined reviewed case source manifest.",
    )
    parser.add_argument(
        "--no-local-seeds",
        action="store_true",
        help="Only export records from the case source manifest.",
    )
    parser.add_argument(
        "--split",
        default="test",
        choices=DATASET_SPLITS,
        help="Dataset split to include in the review table.",
    )
    parser.add_argument(
        "--train-split",
        default="train",
        choices=DATASET_SPLITS,
        help="Dataset split used to fit train-derived policies.",
    )
    parser.add_argument(
        "--min-eval-examples-per-bucket",
        type=int,
        default=1,
        help="Minimum eval examples required before a bucket is no longer a data gap.",
    )
    parser.add_argument(
        "--min-workload-eval-examples",
        type=int,
        default=8,
        help="Minimum eval examples before a workload is considered ready to specialize.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_model_selection_review_table(
            repo_root=args.repo_root,
            output_dir=args.output_dir,
            report_path=args.report or None,
            case_source_manifest_path=args.case_source_manifest,
            include_local_seeds=not args.no_local_seeds,
            eval_split=args.split,
            train_split=args.train_split,
            min_eval_examples_per_bucket=args.min_eval_examples_per_bucket,
            min_workload_eval_examples=args.min_workload_eval_examples,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    artifacts = report["artifacts"]
    print(f"Model selection review table: {artifacts['report_path']}")
    print(f"JSONL: {artifacts['review_table_jsonl_path']}")
    print(f"CSV: {artifacts['review_table_csv_path']}")
    print(f"Review rows: {summary['row_count']}")
    print(f"Primary mismatches: {summary['primary_mismatch_count']}")
    print(f"Baseline mismatches: {summary['baseline_mismatch_count']}")
    print(f"Policy disagreements: {summary['policy_disagreement_count']}")
    print("Workload decisions:")
    for decision, count in summary["workload_decision_counts"].items():
        print(f"  {decision}: {count}")
    print(f"Review table status: {report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
