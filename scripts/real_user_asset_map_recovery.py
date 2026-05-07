"""Recover a local-only private asset map for real user source images."""
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

from vulca.learning.real_user_asset_map_recovery import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    recover_real_user_private_asset_map,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Search local asset directories for private real-user source image "
            "basenames and write a local-only private asset map."
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
        help="Reviewed real-user case source manifest JSON path.",
    )
    parser.add_argument(
        "--search-root",
        action="append",
        default=[],
        help="Local directory to search for source assets. Repeat as needed.",
    )
    parser.add_argument(
        "--filename-alias",
        action="append",
        default=[],
        metavar="PRIVATE_BASENAME=LOCAL_BASENAME",
        help=(
            "Explicit filename alias for recovered assets, for example "
            "nighthawks_reference.png=nighthawks.jpg. Repeat as needed."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for report and private map (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--report",
        default="",
        help=(
            "Safe JSON report path "
            "(default: OUTPUT_DIR/real_user_private_asset_recovery_report.json)."
        ),
    )
    parser.add_argument(
        "--asset-map",
        default="",
        help=(
            "Local private asset map path "
            "(default: OUTPUT_DIR/real_user_recovered.private.asset_map.json)."
        ),
    )
    parser.add_argument(
        "--source-id",
        default="real_user_cases_local_recovered",
        help="source_id to write into the private asset map.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full safe JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = recover_real_user_private_asset_map(
            repo_root=args.repo_root,
            case_source_manifest_path=args.case_source_manifest,
            search_roots=args.search_root,
            filename_aliases=_parse_filename_aliases(args.filename_alias),
            output_dir=args.output_dir,
            report_path=args.report or None,
            asset_map_path=args.asset_map or None,
            source_id=args.source_id,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    artifacts = report["artifacts"]
    print(f"Recovery report: {artifacts['report_path']}")
    print(f"Private asset map: {artifacts['private_asset_map_path']}")
    print(
        "Recovered private source refs: "
        f"{summary['recovered_count']}/{summary['private_source_ref_count']}"
    )
    print(f"Ambiguous private source refs: {summary['ambiguous_count']}")
    print(f"Unresolved private source refs: {summary['unresolved_count']}")
    print(f"Status: {report['status']}")
    return 0


def _parse_filename_aliases(values: Sequence[str]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(
                f"filename alias must use PRIVATE_BASENAME=LOCAL_BASENAME: {value!r}"
            )
        source_name, local_name = value.split("=", 1)
        source_name = source_name.strip()
        local_name = local_name.strip()
        if not source_name or not local_name:
            raise ValueError(
                f"filename alias must use PRIVATE_BASENAME=LOCAL_BASENAME: {value!r}"
            )
        aliases[source_name] = local_name
    return aliases


if __name__ == "__main__":
    raise SystemExit(main())
