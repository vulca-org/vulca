"""Write a safe source-asset coverage report for reviewed real user cases."""
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

from vulca.learning.real_user_asset_coverage import (  # noqa: E402
    DEFAULT_OUTPUT_PATH,
    run_real_user_asset_coverage_report,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Measure which reviewed real user cases have local source images "
            "available for provider-free open-model signal extraction."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Repository root (default: this script's repository).",
    )
    parser.add_argument(
        "--case-source-manifest",
        required=True,
        help="Reviewed case source manifest JSON path.",
    )
    parser.add_argument(
        "--private-asset-map",
        action="append",
        default=[],
        help=(
            "Private local asset map JSON path. Repeat to include multiple maps. "
            "Mapped local paths are never copied into the report."
        ),
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Coverage report JSON path (default: {DEFAULT_OUTPUT_PATH}).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_real_user_asset_coverage_report(
            repo_root=args.repo_root,
            case_source_manifest_path=args.case_source_manifest,
            private_asset_map_paths=args.private_asset_map,
            output_path=args.output,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    example_count = summary["example_count"]
    print(f"Real-user asset coverage report: {args.output}")
    print(f"Cases: {example_count}")
    print(
        "Open-model runnable: "
        f"{summary['open_model_runnable_count']}/{example_count}"
    )
    print(f"Needs private asset map: {summary['needs_private_asset_map_count']}")
    print(f"Source hint only: {summary['source_hint_only_count']}")
    print(f"Missing source refs: {summary['missing_source_reference_count']}")
    print(f"Invalid source images: {summary['invalid_image_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
