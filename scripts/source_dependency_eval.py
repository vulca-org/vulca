"""Run provider-free source-dependency label evaluation."""
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

from vulca.learning.source_dependency_eval import (  # noqa: E402
    DEFAULT_CASE_SOURCE_MANIFEST,
    DEFAULT_MAX_MISMATCHES,
    DEFAULT_MIN_DEPENDENCY_ACCURACY,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_POLICY_NAMES,
    DEFAULT_SOURCE_DEPENDENCY_MANIFEST,
    SOURCE_DEPENDENCY_POLICIES,
    format_source_dependency_gate_violation,
    parse_policy_float_thresholds,
    parse_policy_int_thresholds,
    run_source_dependency_eval,
)
from vulca.learning.tiny_dataset import DATASET_SPLITS  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export a tiny dataset with reviewed source-dependency labels, "
            "evaluate provider-free source-dependency policies, and enforce "
            "basic accuracy gates."
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
        help="Directory for generated dataset and comparison JSON.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Stable JSON report path (default: OUTPUT_DIR/source_dependency_eval_report.json).",
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
        default=str(DEFAULT_CASE_SOURCE_MANIFEST),
        help=(
            "Reviewed case source manifest to include "
            f"(default: {DEFAULT_CASE_SOURCE_MANIFEST})."
        ),
    )
    parser.add_argument(
        "--source-dependency-manifest",
        default=str(DEFAULT_SOURCE_DEPENDENCY_MANIFEST),
        help=(
            "Reviewed source-dependency label manifest "
            f"(default: {DEFAULT_SOURCE_DEPENDENCY_MANIFEST})."
        ),
    )
    parser.add_argument(
        "--no-case-source-manifest",
        action="store_true",
        help="Do not include the default case source manifest.",
    )
    parser.add_argument(
        "--no-local-seeds",
        action="store_true",
        help="Only export records from --case-log/--case-source-manifest inputs.",
    )
    parser.add_argument(
        "--split",
        default="all",
        choices=("all", *DATASET_SPLITS),
        help="Dataset split to evaluate (default: all labeled examples).",
    )
    parser.add_argument(
        "--train-split",
        default="train",
        choices=DATASET_SPLITS,
        help="Dataset split used by train-derived baselines.",
    )
    parser.add_argument(
        "--policy",
        action="append",
        default=[],
        choices=sorted(SOURCE_DEPENDENCY_POLICIES),
        help=(
            "Source-dependency policy to evaluate; repeat to include multiple "
            f"policies (default: {DEFAULT_POLICY_NAMES})."
        ),
    )
    parser.add_argument(
        "--min-dependency-accuracy",
        action="append",
        default=[],
        metavar="POLICY=VALUE",
        help=(
            "Fail if a policy dependency_accuracy is below VALUE. "
            f"Default: {dict(DEFAULT_MIN_DEPENDENCY_ACCURACY)}."
        ),
    )
    parser.add_argument(
        "--max-mismatches",
        action="append",
        default=[],
        metavar="POLICY=COUNT",
        help=(
            "Fail if a policy has more than COUNT mismatches. "
            f"Default: {dict(DEFAULT_MAX_MISMATCHES)}."
        ),
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_source_dependency_eval(
            repo_root=args.repo_root,
            output_dir=args.output_dir,
            report_path=args.report or None,
            manifest_path=args.manifest or None,
            case_log_paths=args.case_log,
            case_source_manifest_path=(
                None if args.no_case_source_manifest else args.case_source_manifest
            ),
            source_dependency_manifest_path=args.source_dependency_manifest,
            include_local_seeds=not args.no_local_seeds,
            eval_split=None if args.split == "all" else args.split,
            train_split=args.train_split,
            policy_names=tuple(args.policy) if args.policy else DEFAULT_POLICY_NAMES,
            min_dependency_accuracy=parse_policy_float_thresholds(
                args.min_dependency_accuracy
            ),
            max_mismatches=parse_policy_int_thresholds(args.max_mismatches),
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    print(f"Source dependency eval report: {report['artifacts']['report_path']}")
    print(f"Tiny dataset: {report['artifacts']['dataset_path']}")
    print(
        "Source dependency labeled examples: "
        f"{report['dataset']['source_dependency_labeled_count']}"
    )
    for policy in sorted(report["comparison"]["policy_reports"]):
        policy_report = report["comparison"]["policy_reports"][policy]
        print(f"{policy} dependency_accuracy: {policy_report['dependency_accuracy']}")
        print(
            f"{policy} decision_basis_accuracy: "
            f"{policy_report['decision_basis_accuracy']}"
        )

    if not report["gate"]["passed"]:
        print("Source dependency eval gate failed:", file=sys.stderr)
        for violation in report["gate"]["violations"]:
            print(
                f"  {format_source_dependency_gate_violation(violation)}",
                file=sys.stderr,
            )
        return 1

    print("Source dependency eval gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
