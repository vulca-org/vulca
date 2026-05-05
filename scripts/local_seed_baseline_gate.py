"""CI entrypoint for the local seed baseline regression gate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vulca.learning.seed_cases import DEFAULT_SEED_MANIFEST  # noqa: E402
from vulca.learning.seed_report import (  # noqa: E402
    DEFAULT_BASELINE_POLICIES,
    check_baseline_report,
    parse_policy_int_thresholds,
    parse_policy_thresholds,
    write_local_seed_baseline_report,
)


DEFAULT_MIN_ACTION_ACCURACY = ("observable_signal=1.0",)
DEFAULT_MAX_MISMATCHES = ("observable_signal=0",)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the local seed baseline regression gate."
    )
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Repository root (default: script parent directory)",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "build" / "local_seed_baseline_report.json"),
        help="Output JSON report path",
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_SEED_MANIFEST),
        help="Seed manifest path",
    )
    parser.add_argument(
        "--policy",
        action="append",
        default=[],
        choices=DEFAULT_BASELINE_POLICIES,
        help="Redraw router policy to evaluate; repeat to include multiple policies",
    )
    parser.add_argument(
        "--min-action-accuracy",
        action="append",
        default=list(DEFAULT_MIN_ACTION_ACCURACY),
        metavar="POLICY=VALUE",
        help="Fail if a policy action_accuracy is below VALUE",
    )
    parser.add_argument(
        "--max-mismatches",
        action="append",
        default=list(DEFAULT_MAX_MISMATCHES),
        metavar="POLICY=COUNT",
        help="Fail if a policy has more than COUNT mismatched cases",
    )
    args = parser.parse_args(argv)

    policies = tuple(args.policy) if args.policy else DEFAULT_BASELINE_POLICIES
    output_path = write_local_seed_baseline_report(
        repo_root=args.repo_root,
        output_path=args.output,
        manifest_path=args.manifest,
        policies=policies,
    )
    report = json.loads(Path(output_path).read_text(encoding="utf-8"))
    violations = check_baseline_report(
        report,
        min_action_accuracy=parse_policy_thresholds(args.min_action_accuracy),
        max_mismatches=parse_policy_int_thresholds(args.max_mismatches),
    )

    if violations:
        print(f"Local seed baseline gate failed: {output_path}", file=sys.stderr)
        _print_violations(violations)
        return 1

    print(f"Local seed baseline gate passed: {output_path}")
    _print_summary(report, policies)
    return 0


def _print_summary(report: Mapping[str, Any], policies: Sequence[str]) -> None:
    for case_type in sorted(report["seed_counts"]):
        print(f"  {case_type}: {report['seed_counts'][case_type]}")
    for policy in policies:
        metrics = report["redraw_router_baselines"][policy]
        print(f"  {policy} action_accuracy: {metrics['action_accuracy']}")


def _print_violations(violations: Sequence[Mapping[str, Any]]) -> None:
    for item in violations:
        if item["metric"] == "action_accuracy":
            expected = str(item["expected"]).replace(">= ", "")
            print(
                f"  {item['policy']} action_accuracy {item['actual']} < {expected}",
                file=sys.stderr,
            )
        elif item["metric"] == "mismatch_count":
            expected = str(item["expected"]).replace("<= ", "")
            print(
                f"  {item['policy']} mismatch_count {item['actual']} > {expected}",
                file=sys.stderr,
            )


if __name__ == "__main__":
    raise SystemExit(main())
