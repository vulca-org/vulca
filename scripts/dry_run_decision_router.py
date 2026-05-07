"""Run the provider-free dry-run decision router."""
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

from vulca.learning.dry_run_decision_router import (  # noqa: E402
    DEFAULT_MIN_ACTION_CONFIDENCE,
    DEFAULT_OUTPUT_DIR,
    run_dry_run_decision_router,
)
from vulca.learning.source_dependency_eval import (  # noqa: E402
    DEFAULT_CASE_SOURCE_MANIFEST,
    DEFAULT_SOURCE_DEPENDENCY_MANIFEST,
)
from vulca.learning.tiny_dataset import DATASET_SPLITS  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run provider-free dry-run routing decisions over a tiny dataset "
            "split, combining action routing with source-dependency routing."
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
        help="Directory for generated dataset, decisions, and report.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Report JSON path (default: OUTPUT_DIR/dry_run_decision_router_report.json).",
    )
    parser.add_argument(
        "--case-source-manifest",
        default=str(DEFAULT_CASE_SOURCE_MANIFEST),
        help="Combined reviewed case source manifest.",
    )
    parser.add_argument(
        "--source-dependency-manifest",
        default=str(DEFAULT_SOURCE_DEPENDENCY_MANIFEST),
        help="Reviewed source-dependency label manifest.",
    )
    parser.add_argument(
        "--auxiliary-signal-manifest",
        default="",
        help="Reviewed promoted auxiliary signal manifest to attach to the dataset.",
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
        help="Dataset split to route.",
    )
    parser.add_argument(
        "--train-split",
        default="train",
        choices=DATASET_SPLITS,
        help="Dataset split used to fit tiny action classifier.",
    )
    parser.add_argument(
        "--min-action-confidence",
        type=float,
        default=DEFAULT_MIN_ACTION_CONFIDENCE,
        help="Below this action confidence, route execution to fallback_agent.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print full JSON report after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_dry_run_decision_router(
            repo_root=args.repo_root,
            output_dir=args.output_dir,
            report_path=args.report or None,
            case_source_manifest_path=args.case_source_manifest,
            source_dependency_manifest_path=args.source_dependency_manifest,
            auxiliary_signal_manifest_path=args.auxiliary_signal_manifest or None,
            include_local_seeds=not args.no_local_seeds,
            eval_split=args.split,
            train_split=args.train_split,
            min_action_confidence=args.min_action_confidence,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    evaluation = report["evaluation"]
    print(f"Dry-run decision router report: {report['artifacts']['report_path']}")
    print(f"Dry-run decisions: {report['artifacts']['decision_path']}")
    print(f"Dataset: {report['artifacts']['dataset_path']}")
    print(f"Decisions: {summary['decision_count']}")
    print(f"Fallback agent decisions: {summary['fallback_agent_count']}")
    print(f"Runtime recovery decisions: {summary['runtime_recovery_count']}")
    print(
        "Visual ownership planner decisions: "
        f"{summary['visual_ownership_planner_count']}"
    )
    print(
        "tiny_action_model_v1 action_accuracy: "
        f"{evaluation['action_accuracy']}"
    )
    print(
        "source_dependency_rule_v1 source_dependency_accuracy: "
        f"{evaluation['source_dependency_accuracy']}"
    )
    print(
        "source_dependency_rule_v1 decision_basis_accuracy: "
        f"{evaluation['decision_basis_accuracy']}"
    )
    if summary["data_gap_counts"]:
        print(f"Data gap tags: {summary['data_gap_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
