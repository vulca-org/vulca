"""Write a source-context gap pack from training effectiveness v3."""
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

from vulca.learning.source_context_gap_pack import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    run_source_context_gap_pack,
)
from vulca.learning.source_dependency_eval import (  # noqa: E402
    DEFAULT_SOURCE_DEPENDENCY_MANIFEST,
)
from vulca.learning.tiny_dataset import DATASET_SPLITS  # noqa: E402
from vulca.learning.training_effectiveness import (  # noqa: E402
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run training effectiveness v3 and write an actionable source-context "
            "gap pack for remaining dry-run router fallbacks."
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
        help="Directory for generated gap-pack artifacts.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Stable JSON report path (default: OUTPUT_DIR/source_context_gap_pack_report.json).",
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
        "--no-local-seeds",
        action="store_true",
        help="Only export records from the case source manifest.",
    )
    parser.add_argument(
        "--split",
        default="test",
        choices=DATASET_SPLITS,
        help="Dataset split to inspect for remaining source-context gaps.",
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
        report = run_source_context_gap_pack(
            repo_root=args.repo_root,
            output_dir=args.output_dir,
            report_path=args.report or None,
            case_source_manifest_path=args.case_source_manifest,
            source_dependency_manifest_path=args.source_dependency_manifest,
            include_local_seeds=not args.no_local_seeds,
            eval_split=args.split,
            train_split=args.train_split,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    print(f"Source context gap pack report: {report['artifacts']['report_path']}")
    print(f"Training effectiveness report: {report['artifacts']['training_effectiveness_report_path']}")
    print(f"Remaining source-context gaps: {summary['remaining_gap_count']}")
    print(
        "Tiny-model dispatch recoverable after source context: "
        f"{summary['tiny_model_dispatch_recoverable_count']}"
    )
    print(
        "Still agent-required after source context: "
        f"{summary['still_agent_required_after_source_context_count']}"
    )
    for gap_task, count in report["counts_by_gap_task"].items():
        print(f"Gap task {gap_task}: {count}")
    print(f"Source context gap pack status: {report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
