"""Run real source recovery and audit as one provider-free workflow."""
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

from vulca.learning.real_source_context_recovery_audit import (  # noqa: E402
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    DEFAULT_OUTPUT_DIR,
    run_real_source_context_recovery_audit,
)
from vulca.learning.tiny_dataset import DATASET_SPLITS  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Recover local private source image/artifact maps, then run the "
            "real source-context audit with those maps attached."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Repository root used to resolve case source refs.",
    )
    parser.add_argument(
        "--case-source-manifest",
        default=str(DEFAULT_COMBINED_CASE_SOURCE_MANIFEST),
        help="Case source manifest JSON path.",
    )
    parser.add_argument(
        "--artifact-search-root",
        action="append",
        default=[],
        help="Local directory to search for private source artifact directories/files.",
    )
    parser.add_argument(
        "--image-search-root",
        action="append",
        default=[],
        help="Local directory to search for private source images.",
    )
    parser.add_argument(
        "--artifact-filename-alias",
        action="append",
        default=[],
        metavar="PRIVATE_BASENAME=LOCAL_BASENAME",
        help="Private source artifact basename alias. Repeat as needed.",
    )
    parser.add_argument(
        "--image-filename-alias",
        action="append",
        default=[],
        metavar="PRIVATE_BASENAME=LOCAL_BASENAME",
        help="Private source image basename alias. Repeat as needed.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for recovery maps and audit report (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--report",
        default="",
        help=(
            "Summary report path "
            "(default: OUTPUT_DIR/real_source_context_recovery_audit_report.json)."
        ),
    )
    parser.add_argument(
        "--no-local-seeds",
        action="store_true",
        help="Do not include local seed cases in the audit training dataset.",
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
        help="Print the full safe JSON report to stdout after writing it.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_real_source_context_recovery_audit(
            repo_root=args.repo_root,
            case_source_manifest_path=args.case_source_manifest,
            artifact_search_roots=args.artifact_search_root,
            image_search_roots=args.image_search_root,
            artifact_filename_aliases=_parse_aliases(args.artifact_filename_alias),
            image_filename_aliases=_parse_aliases(args.image_filename_alias),
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
    print(f"Real source-context recovery audit: {report['artifacts']['report_path']}")
    print(
        "Recovered source artifacts: "
        f"{summary['private_source_artifact_recovered_count']}/"
        f"{summary['private_source_artifact_ref_count']}"
    )
    print(
        "Recovered source images: "
        f"{summary['private_source_image_recovered_count']}/"
        f"{summary['private_source_image_ref_count']}"
    )
    print(
        "Source context available: "
        f"{summary['source_context_available_count']}/"
        f"{summary['real_user_case_count']}"
    )
    print(f"Review candidates: {summary['review_candidate_count']}")
    print(f"Status: {report['status']}")
    return 0


def _parse_aliases(values: Sequence[str]) -> dict[str, str]:
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
