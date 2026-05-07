"""Write the combined tiny training effectiveness report."""
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
from vulca.learning.training_effectiveness import (  # noqa: E402
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SOURCE_DEPENDENCY_MANIFEST,
    format_data_gap,
    run_training_effectiveness_report,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the combined tiny learning eval and write a training "
            "effectiveness report with policy deltas and data coverage gaps."
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
        help="Directory for generated aggregate artifacts.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Stable JSON report path (default: OUTPUT_DIR/training_effectiveness_report.json).",
    )
    parser.add_argument(
        "--case-source-manifest",
        default=str(DEFAULT_COMBINED_CASE_SOURCE_MANIFEST),
        help="Combined reviewed case source manifest.",
    )
    parser.add_argument(
        "--source-dependency-manifest",
        default=str(DEFAULT_SOURCE_DEPENDENCY_MANIFEST),
        help="Reviewed source-dependency label manifest.",
    )
    parser.add_argument(
        "--source-dependency-split",
        default="all",
        choices=("all", *DATASET_SPLITS),
        help="Dataset split for source-dependency eval; default evaluates all labeled examples.",
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
        help="Minimum eval examples required before a bucket is no longer reported as a data gap.",
    )
    parser.add_argument(
        "--fail-on-data-gaps",
        action="store_true",
        help="Return non-zero when coverage gaps remain.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_training_effectiveness_report(
            repo_root=args.repo_root,
            output_dir=args.output_dir,
            report_path=args.report or None,
            case_source_manifest_path=args.case_source_manifest,
            include_local_seeds=not args.no_local_seeds,
            eval_split=args.split,
            train_split=args.train_split,
            min_eval_examples_per_bucket=args.min_eval_examples_per_bucket,
            source_dependency_manifest_path=args.source_dependency_manifest,
            source_dependency_eval_split=(
                None
                if args.source_dependency_split == "all"
                else args.source_dependency_split
            ),
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    dataset = report["dataset"]
    effectiveness = report["effectiveness"]
    print(f"Training effectiveness report: {report['artifacts']['report_path']}")
    print(f"Aggregated eval report: {report['artifacts']['aggregated_report_path']}")
    print(f"Dataset examples: {dataset['example_count']}")
    print(f"Eval examples: {dataset['eval_example_count']}")
    print(
        f"{effectiveness['evaluated_policy']} action_accuracy: "
        f"{effectiveness['action_accuracy']}"
    )
    print(
        f"{effectiveness['baseline_policy']} action_accuracy: "
        f"{effectiveness['baseline_action_accuracy']}"
    )
    print(
        "Accuracy delta vs baseline: "
        f"{effectiveness['accuracy_delta_vs_baseline']}"
    )
    source_dependency = report["source_dependency"]
    source_best = source_dependency["best_policy"]
    print(f"Source dependency labeled examples: {source_dependency['labeled_count']}")
    print(
        f"{source_best['policy_name']} dependency_accuracy: "
        f"{source_best['dependency_accuracy']}"
    )
    print(
        f"{source_best['policy_name']} decision_basis_accuracy: "
        f"{source_best['decision_basis_accuracy']}"
    )
    for row in report["leaderboard"]:
        if row["task"] != "source_dependency":
            continue
        print(
            "Leaderboard source_dependency: "
            f"{row['best_policy']} "
            f"{row['primary_metric']}={row['primary_accuracy']} "
            f"{row['secondary_metric']}={row['secondary_accuracy']}"
        )
    hardest_drop = effectiveness.get("ablation_summary", {}).get(
        "largest_accuracy_drop",
        {},
    )
    if hardest_drop:
        print(
            "Ablation hardest drop: "
            f"{hardest_drop.get('variant_id')} "
            f"{hardest_drop.get('accuracy_delta_vs_full')}"
        )
    print(f"Tiny gate passed: {effectiveness['gate_passed']}")
    print(f"Data gaps: {len(report['data_gaps'])}")
    for gap in report["data_gaps"][:10]:
        print(
            f"  {gap['bucket']} {gap['value']}: "
            f"eval {gap['eval_example_count']}/{gap['example_count']}"
        )

    if not effectiveness["gate_passed"]:
        print("Training effectiveness gate failed:", file=sys.stderr)
        for violation in effectiveness["gate"].get("violations", []) or []:
            print(f"  {violation}", file=sys.stderr)
        return 1
    if not source_dependency["gate_passed"]:
        print("Source dependency effectiveness gate failed:", file=sys.stderr)
        for violation in source_dependency["gate"].get("violations", []) or []:
            print(f"  {violation}", file=sys.stderr)
        return 1

    if args.fail_on_data_gaps and report["data_gaps"]:
        print("Training effectiveness data coverage gaps:", file=sys.stderr)
        for gap in report["data_gaps"]:
            print(f"  {format_data_gap(gap)}", file=sys.stderr)
        return 1

    print(f"Training effectiveness status: {report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
