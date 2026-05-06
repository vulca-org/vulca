"""Write the tiny model/agent selection report."""
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
    DEFAULT_OUTPUT_DIR,
    run_model_selection_report,
)
from vulca.learning.tiny_dataset import DATASET_SPLITS  # noqa: E402
from vulca.learning.training_effectiveness import (  # noqa: E402
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the combined tiny eval and write a model/agent selection "
            "report for primary policy, baselines, and workload specialists."
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
        help="Directory for generated model selection artifacts.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Stable JSON report path (default: OUTPUT_DIR/model_selection_report.json).",
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
        help="Dataset split to predict and compare.",
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
        report = run_model_selection_report(
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

    dataset = report["dataset"]
    selection = report["selection"]
    print(f"Model selection report: {report['artifacts']['report_path']}")
    print(f"Training effectiveness report: {report['artifacts']['training_effectiveness_report_path']}")
    print(f"Dataset examples: {dataset['example_count']}")
    print(f"Eval examples: {dataset['eval_example_count']}")
    print(f"Data gaps: {dataset['data_gap_count']}")
    print(f"Recommended primary: {selection['recommended_primary_policy']}")
    print(f"Recommended baseline: {selection['recommended_baseline_policy']}")
    print(
        "Accuracy delta vs baseline: "
        f"{selection['accuracy_delta_vs_baseline']}"
    )
    print("Candidate policies:")
    for candidate in report["candidate_policies"]:
        print(
            f"  {candidate['policy_name']}: {candidate['decision']} "
            f"accuracy={candidate['action_accuracy']}"
        )
    print("Workload recommendations:")
    for workload in report["workload_recommendations"]:
        print(
            f"  {workload['case_type']}: {workload['best_policy']} "
            f"track={workload['recommended_track']} decision={workload['decision']}"
        )
    print(f"Model selection status: {report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
