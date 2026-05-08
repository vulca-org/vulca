"""Dry-run visual ownership runtime adapter requests."""

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

from vulca.learning.visual_ownership_runtime_replay import (  # noqa: E402
    DEFAULT_REPLAY_NAME,
    DEFAULT_REPORT_NAME,
    run_visual_ownership_runtime_replay,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Dry-run visual ownership runtime adapter requests into replay "
            "records without provider calls."
        )
    )
    parser.add_argument(
        "--requests",
        required=True,
        help="Visual ownership runtime request JSONL path.",
    )
    parser.add_argument(
        "--replay",
        default="",
        help=f"Replay JSONL path (default: alongside requests as {DEFAULT_REPLAY_NAME}).",
    )
    parser.add_argument(
        "--report",
        default="",
        help=f"Report JSON path (default: alongside requests as {DEFAULT_REPORT_NAME}).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print full JSON report after writing it.",
    )
    args = parser.parse_args(argv)

    request_path = Path(args.requests)
    replay_path = (
        Path(args.replay) if args.replay else request_path.parent / DEFAULT_REPLAY_NAME
    )
    report_path = (
        Path(args.report) if args.report else request_path.parent / DEFAULT_REPORT_NAME
    )
    try:
        report = run_visual_ownership_runtime_replay(
            request_path=request_path,
            replay_path=replay_path,
            report_path=report_path,
        )
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    summary = report["summary"]
    print(f"Visual ownership runtime replay report: {report_path}")
    print(f"Visual ownership runtime replay: {replay_path}")
    print(f"Requests: {summary['request_count']}")
    print(f"Replayable: {summary['replayable_count']}")
    print(f"Blocked: {summary['blocked_count']}")
    print(f"Provider calls: {summary['provider_call_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
