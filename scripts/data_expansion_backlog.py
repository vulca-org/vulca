"""Write the tiny learning data expansion backlog."""
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

from vulca.learning.data_expansion_backlog import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    run_data_expansion_backlog,
)
from vulca.learning.model_selection_report import (  # noqa: E402
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
)
from vulca.learning.tiny_dataset import DATASET_SPLITS  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a case-collection backlog from the model-selection review table, "
            "prioritizing decompose/layer_generate buckets that need more real cases."
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
        help="Directory for generated backlog artifacts.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Stable JSON report path (default: OUTPUT_DIR/data_expansion_backlog_report.json).",
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
        help="Dataset split to inspect for expansion backlog.",
    )
    parser.add_argument(
        "--train-split",
        default="train",
        choices=DATASET_SPLITS,
        help="Dataset split used to fit train-derived policies.",
    )
    parser.add_argument(
        "--real-cases-per-item",
        type=int,
        default=2,
        help="Requested new real user cases per backlog item.",
    )
    parser.add_argument(
        "--manual-cases-per-item",
        type=int,
        default=1,
        help="Requested new manually curated cases per backlog item.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_data_expansion_backlog(
            repo_root=args.repo_root,
            output_dir=args.output_dir,
            report_path=args.report or None,
            case_source_manifest_path=args.case_source_manifest,
            include_local_seeds=not args.no_local_seeds,
            eval_split=args.split,
            train_split=args.train_split,
            requested_real_cases_per_item=args.real_cases_per_item,
            requested_manual_cases_per_item=args.manual_cases_per_item,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    artifacts = report["artifacts"]
    print(f"Data expansion backlog: {artifacts['report_path']}")
    print(f"JSON: {artifacts['backlog_json_path']}")
    print(f"CSV: {artifacts['backlog_csv_path']}")
    print(f"Backlog items: {summary['backlog_item_count']}")
    print(f"Requested real cases: {summary['requested_real_case_count']}")
    print(f"Requested manual cases: {summary['requested_manual_case_count']}")
    print("Top backlog items:")
    for item in report["backlog_items"][:5]:
        print(
            f"  {item['priority_tier']} {item['backlog_id']}: "
            f"real={item['requested_real_cases']} manual={item['requested_manual_cases']}"
        )
    print(f"Data expansion backlog status: {report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
