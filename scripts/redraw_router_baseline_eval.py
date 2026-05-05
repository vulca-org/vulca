"""Offline benchmark entrypoint for redraw tiny-router baselines."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from vulca.layers.redraw_router_baseline import (
    POLICIES,
    evaluate_records,
    load_jsonl_many,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score provider-free redraw router baseline policies on JSONL case records."
    )
    parser.add_argument("case_logs", nargs="+", help="Path(s) to redraw_case JSONL logs.")
    parser.add_argument(
        "--policy",
        default="observable_signal",
        choices=sorted(POLICIES),
        help="Baseline policy to evaluate.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    args = parser.parse_args(argv)

    records = load_jsonl_many(args.case_logs)
    report = evaluate_records(records, policy_name=args.policy)
    indent = 2 if args.pretty else None
    sys.stdout.write(json.dumps(report, sort_keys=True, indent=indent))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
