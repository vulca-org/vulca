"""Write a safe source-context audit for real user learning cases."""
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

from vulca.learning.real_source_context_audit import (  # noqa: E402
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    DEFAULT_OUTPUT_DIR,
    run_real_source_context_audit_report,
)
from vulca.learning.tiny_dataset import DATASET_SPLITS  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit real user cases where source-context auxiliary signals may "
            "change or support tiny_action_model_v1 decisions."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Repository root (default: this script's repository).",
    )
    parser.add_argument(
        "--case-source-manifest",
        default=str(DEFAULT_COMBINED_CASE_SOURCE_MANIFEST),
        help="Case source manifest JSON path.",
    )
    parser.add_argument(
        "--private-asset-map",
        action="append",
        default=[],
        help="Private local image/artifact map JSON path. Repeat to include multiple maps.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for audit report and generated source-context signal pack.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Audit report JSON path (default: OUTPUT_DIR/real_source_context_audit_report.json).",
    )
    parser.add_argument(
        "--no-local-seeds",
        action="store_true",
        help="Do not include local seed cases in the training dataset.",
    )
    parser.add_argument(
        "--train-split",
        default="train",
        choices=DATASET_SPLITS,
        help="Dataset split used to fit train-derived tiny policies.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_real_source_context_audit_report(
            repo_root=args.repo_root,
            case_source_manifest_path=args.case_source_manifest,
            private_asset_map_paths=args.private_asset_map,
            output_dir=args.output_dir,
            report_path=args.report or None,
            include_local_seeds=not args.no_local_seeds,
            train_split=args.train_split,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    print(f"Real source-context audit: {report['artifacts']['report_path']}")
    print(
        "Review candidates: "
        f"{summary['review_candidate_count']}/{summary['real_user_case_count']}"
    )
    print(
        "Source context available: "
        f"{summary['source_context_available_count']}/"
        f"{summary['real_user_case_count']}"
    )
    print(
        "Prediction changed with source context: "
        f"{summary['prediction_changed_with_source_context_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
