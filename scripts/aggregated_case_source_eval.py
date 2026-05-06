"""Run the provider-free aggregated case-source eval report."""
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

from vulca.learning.aggregated_case_source_eval import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    format_aggregated_eval_gate_failure,
    run_aggregated_case_source_eval,
)
from vulca.learning.tiny_dataset import DATASET_SPLITS  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run provider-free tiny_agent_v0 and tiny_action_model_v1 eval, then "
            "write an aggregated case-source report with source and taxonomy buckets."
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
        help="Directory for generated dataset, predictions, comparison JSON, and aggregate artifacts.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Stable JSON aggregate report path (default: OUTPUT_DIR/aggregated_case_source_eval_report.json).",
    )
    parser.add_argument(
        "--manifest",
        default="",
        help="Seed manifest path (default: docs/benchmarks/learning/local_seed_manifest.json).",
    )
    parser.add_argument(
        "--case-log",
        action="append",
        default=[],
        help="Additional reviewed case JSONL path; repeat to include multiple logs.",
    )
    parser.add_argument(
        "--case-source-manifest",
        action="append",
        default=[],
        help=(
            "Reviewed case source manifest to include; repeat to include multiple "
            "manifests. The manual curated v1 manifest is included by default."
        ),
    )
    parser.add_argument(
        "--no-default-case-source-manifest",
        action="store_true",
        help="Do not include the default manual curated v1 case source manifest.",
    )
    parser.add_argument(
        "--no-local-seeds",
        action="store_true",
        help="Only export records from --case-log/--case-source-manifest inputs.",
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
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_aggregated_case_source_eval(
            repo_root=args.repo_root,
            output_dir=args.output_dir,
            report_path=args.report or None,
            manifest_path=args.manifest or None,
            case_log_paths=args.case_log,
            case_source_manifest_paths=args.case_source_manifest,
            include_default_case_source_manifest=not args.no_default_case_source_manifest,
            include_local_seeds=not args.no_local_seeds,
            eval_split=args.split,
            train_split=args.train_split,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    print(f"Aggregated case source eval report: {report['artifacts']['report_path']}")
    print(f"Tiny training/eval report: {report['artifacts']['tiny_training_eval_report_path']}")
    print(f"Dataset examples: {report['dataset_summary']['example_count']}")
    print("Source summary:")
    for source_id, metrics in report["bucket_metrics"]["source_id"].items():
        print(f"  {source_id}: {metrics['example_count']}")
    for kind, metrics in report["bucket_metrics"]["source.kind"].items():
        print(f"  source.kind {kind}: {metrics['example_count']}")
    print("Taxonomy summary:")
    for failure_type, metrics in report["bucket_metrics"]["targets.failure_type"].items():
        print(f"  {failure_type}: {metrics['example_count']}")
    for policy in sorted(report["policy_comparison"]["policy_reports"]):
        policy_report = report["policy_comparison"]["policy_reports"][policy]
        print(f"{policy} action_accuracy: {policy_report['action_accuracy']}")

    gate = report["tiny_training_eval"]["gate"]
    if not gate["passed"]:
        print("Aggregated case source eval tiny gate failed:", file=sys.stderr)
        for line in format_aggregated_eval_gate_failure(report):
            print(f"  {line}", file=sys.stderr)
        return 1

    print("Aggregated case source eval passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
