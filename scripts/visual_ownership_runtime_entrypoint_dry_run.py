"""Build provider-free visual ownership runtime entrypoint dry-runs."""

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

from vulca.learning.visual_ownership_runtime_entrypoint_dry_run import (  # noqa: E402
    DEFAULT_INVOCATION_NAME,
    DEFAULT_REPORT_NAME,
    run_visual_ownership_runtime_entrypoint_dry_run,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Convert visual ownership runtime replay records into provider-free "
            "entrypoint invocation contracts."
        )
    )
    parser.add_argument(
        "--replay",
        required=True,
        help="Visual ownership runtime replay JSONL path.",
    )
    parser.add_argument(
        "--invocations",
        default="",
        help=(
            "Dry-run invocation JSONL path "
            f"(default: alongside replay as {DEFAULT_INVOCATION_NAME})."
        ),
    )
    parser.add_argument(
        "--report",
        default="",
        help=f"Report JSON path (default: alongside replay as {DEFAULT_REPORT_NAME}).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print full JSON report after writing it.",
    )
    args = parser.parse_args(argv)

    replay_path = Path(args.replay)
    invocation_path = (
        Path(args.invocations)
        if args.invocations
        else replay_path.parent / DEFAULT_INVOCATION_NAME
    )
    report_path = (
        Path(args.report) if args.report else replay_path.parent / DEFAULT_REPORT_NAME
    )
    try:
        report = run_visual_ownership_runtime_entrypoint_dry_run(
            replay_path=replay_path,
            invocation_path=invocation_path,
            report_path=report_path,
        )
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    print(f"Visual ownership runtime entrypoint dry-run report: {report_path}")
    print(f"Visual ownership runtime entrypoint dry-runs: {invocation_path}")
    print(f"Replay records: {summary['replay_record_count']}")
    print(f"Ready: {summary['ready_count']}")
    print(f"Blocked: {summary['blocked_count']}")
    print(f"Provider calls: {summary['provider_call_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
