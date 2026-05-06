"""Run the canonical provider-free tiny training/eval gate."""
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
from vulca.learning.tiny_training_eval import (  # noqa: E402
    DEFAULT_MANUAL_CURATED_CASE_SOURCE_MANIFEST,
    DEFAULT_MAX_MISMATCHES,
    DEFAULT_MIN_ACTION_ACCURACY,
    DEFAULT_OUTPUT_DIR,
    format_gate_violation,
    parse_policy_float_thresholds,
    parse_policy_int_thresholds,
    run_tiny_training_eval_gate,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export the tiny dataset, run provider-free tiny_agent_v0 and "
            "tiny_action_model_v1 predictions, compare policies, and enforce "
            "the tiny training/eval quality gate."
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
        help="Directory for generated dataset, predictions, and comparison JSON.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Stable JSON gate report path (default: OUTPUT_DIR/tiny_training_eval_report.json).",
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
        default=str(DEFAULT_MANUAL_CURATED_CASE_SOURCE_MANIFEST),
        help=(
            "Reviewed case source manifest to include. Defaults to the manual "
            "curated v1 manifest."
        ),
    )
    parser.add_argument(
        "--auxiliary-signal-manifest",
        default="",
        help=(
            "Explicit reviewed open-model signal promotion manifest to attach "
            "as auxiliary training features."
        ),
    )
    parser.add_argument(
        "--no-case-source-manifest",
        action="store_true",
        help="Do not include the default manual curated case source manifest.",
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
        "--min-action-accuracy",
        action="append",
        default=[],
        metavar="POLICY=VALUE",
        help=(
            "Fail if a policy action_accuracy is below VALUE. "
            f"Default: {dict(DEFAULT_MIN_ACTION_ACCURACY)}."
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
        "--allow-missing-predictions",
        action="store_true",
        help="Do not fail when prediction JSONL files omit examples from the eval split.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        min_thresholds = parse_policy_float_thresholds(args.min_action_accuracy)
        max_thresholds = parse_policy_int_thresholds(args.max_mismatches)
        report = run_tiny_training_eval_gate(
            repo_root=args.repo_root,
            output_dir=args.output_dir,
            report_path=args.report or None,
            manifest_path=args.manifest or None,
            case_log_paths=args.case_log,
            case_source_manifest_path=(
                None if args.no_case_source_manifest else args.case_source_manifest
            ),
            auxiliary_signal_manifest_path=args.auxiliary_signal_manifest or None,
            include_local_seeds=not args.no_local_seeds,
            eval_split=args.split,
            train_split=args.train_split,
            min_action_accuracy=min_thresholds,
            max_mismatches=max_thresholds,
            require_no_missing_predictions=not args.allow_missing_predictions,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    print(f"Tiny training/eval report: {report['artifacts']['report_path']}")
    print(f"Tiny dataset: {report['artifacts']['dataset_path']}")
    print(
        "tiny_agent_v0 predictions: "
        f"{report['predictions']['tiny_agent_v0']['prediction_count']}"
    )
    print(
        "tiny_action_model_v1 predictions: "
        f"{report['predictions']['tiny_action_model_v1']['prediction_count']}"
    )
    for policy in sorted(report["comparison"]["policy_reports"]):
        policy_report = report["comparison"]["policy_reports"][policy]
        print(f"{policy} action_accuracy: {policy_report['action_accuracy']}")

    if not report["gate"]["passed"]:
        print("Tiny training/eval gate failed:", file=sys.stderr)
        for violation in report["gate"]["violations"]:
            print(f"  {format_gate_violation(violation)}", file=sys.stderr)
        return 1

    print("Tiny training/eval gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
