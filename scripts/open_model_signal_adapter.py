"""Write safe open-model signal records for reviewed learning cases."""
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

from vulca.learning.open_model_signals import (  # noqa: E402
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    DEFAULT_MODEL_CATALOG,
    DEFAULT_MODEL_IDS,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REPORT_NAME,
    DEFAULT_SIGNAL_OUTPUT_NAME,
    run_open_model_signal_adapter,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export reviewable Florence/SAM-style open-model signal records "
            "without downloading weights or enabling runtime providers."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Repository root (default: this script's repository).",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR / DEFAULT_SIGNAL_OUTPUT_NAME),
        help="Output JSONL path for signal records.",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_OUTPUT_DIR / DEFAULT_REPORT_NAME),
        help="Output JSON report path.",
    )
    parser.add_argument(
        "--model-catalog",
        default=str(DEFAULT_MODEL_CATALOG),
        help="Open model catalog JSON path.",
    )
    parser.add_argument(
        "--case-source-manifest",
        default=str(DEFAULT_COMBINED_CASE_SOURCE_MANIFEST),
        help="Combined reviewed case source manifest.",
    )
    parser.add_argument(
        "--model",
        action="append",
        default=[],
        help="Open model id to include; repeat for multiple models.",
    )
    parser.add_argument(
        "--no-local-seeds",
        action="store_true",
        help="Only use records from the case source manifest.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the full JSON report to stdout.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_open_model_signal_adapter(
            repo_root=args.repo_root,
            output_path=args.output,
            report_path=args.report,
            model_catalog_path=args.model_catalog,
            case_source_manifest_path=args.case_source_manifest,
            model_ids=tuple(args.model) or DEFAULT_MODEL_IDS,
            include_local_seeds=not args.no_local_seeds,
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    print(f"Open model signal records: {report['artifacts']['output_path']}")
    print(f"Open model signal report: {report['artifacts']['report_path']}")
    print(f"Signal records: {report['record_count']}")
    print(f"Examples: {report['example_count']}")
    print(f"Models: {', '.join(report['inputs']['model_ids'])}")
    print(f"Status: {report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
