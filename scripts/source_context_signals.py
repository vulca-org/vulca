"""Write promoted provider-free source-context auxiliary signals."""
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

from vulca.learning.source_context_signals import (  # noqa: E402
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    DEFAULT_OUTPUT_DIR,
    write_source_context_signal_pack,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Extract provider-free source-context summaries into explicitly "
            "promoted auxiliary signal records."
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
        help="Reviewed case source manifest JSON path.",
    )
    parser.add_argument(
        "--private-asset-map",
        action="append",
        default=[],
        help=(
            "Private local image/artifact map JSON path. Repeat to include "
            "multiple maps. Local paths are never copied into signal records."
        ),
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR / "source_context_signals.promoted.jsonl"),
        help="Promoted source context signal JSONL output path.",
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_OUTPUT_DIR / "source_context_signal_promotion_manifest.json"),
        help="Auxiliary signal promotion manifest output path.",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_OUTPUT_DIR / "source_context_signal_report.json"),
        help="Safe source context signal report output path.",
    )
    parser.add_argument(
        "--source-id",
        default="source_context_static_v1",
        help="source_id to write into the auxiliary signal manifest.",
    )
    parser.add_argument(
        "--no-local-seeds",
        action="store_true",
        help="Only export records from --case-source-manifest.",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=None,
        help="Optional maximum number of examples to inspect.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = write_source_context_signal_pack(
            repo_root=args.repo_root,
            case_source_manifest_path=args.case_source_manifest,
            private_asset_map_paths=args.private_asset_map,
            output_path=args.output,
            manifest_path=args.manifest,
            report_path=args.report,
            include_local_seeds=not args.no_local_seeds,
            max_examples=args.max_examples,
            source_id=args.source_id,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    print(f"Source context signal report: {report['artifacts']['report_path']}")
    print(f"Promoted signal output: {report['artifacts']['output_path']}")
    print(f"Promotion manifest: {report['artifacts']['manifest_path']}")
    print(
        "Source context signals: "
        f"{summary['promoted_signal_count']}/{summary['example_count']}"
    )
    print(f"Skipped examples: {summary['skipped_count']}")
    print(f"Status: {report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
