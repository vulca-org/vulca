#!/usr/bin/env python3
"""Scan customer-facing solution-pack artifacts for internal-only material."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vulca.solution_pack_preflight import reports_to_json, scan_paths  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Preflight customer-facing VULCA solution-pack artifacts for local "
            "paths, raw internal labels, debug overlays, internal reference "
            "material, and unsupported relationship/certification claims."
        )
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("paths", nargs="+", help="Markdown, text, HTML, JSON, or PDF artifacts to scan.")
    args = parser.parse_args(argv)

    reports = scan_paths([Path(path) for path in args.paths])
    ok = all(report.ok for report in reports)

    if args.json:
        print(reports_to_json(reports))
    else:
        for report in reports:
            if report.ok:
                print(f"PASS {report.source}")
                continue
            print(f"FAIL {report.source}")
            for issue in report.issues:
                print(f"  line {issue.line}: {issue.rule_id}: {issue.match} - {issue.message}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
