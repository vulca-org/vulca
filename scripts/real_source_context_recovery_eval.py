"""Evaluate dry-run impact from recovered real-user source context."""
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

from vulca.learning.real_source_context_recovery_eval import (  # noqa: E402
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    DEFAULT_OUTPUT_DIR,
    run_real_source_context_recovery_eval,
)
from vulca.learning.tiny_dataset import DATASET_SPLITS  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Recover local private source context, generate source-context "
            "signals, and compare dry-run routing before and after recovery."
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
        "--source-dependency-manifest",
        default="",
        help="Optional reviewed source-dependency label manifest.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for recovery eval artifacts (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--report",
        default="",
        help=(
            "Summary report path "
            "(default: OUTPUT_DIR/real_source_context_recovery_eval_report.json)."
        ),
    )
    parser.add_argument(
        "--no-local-seeds",
        action="store_true",
        help="Do not include local seed cases in the eval dataset.",
    )
    parser.add_argument(
        "--split",
        default="test",
        choices=DATASET_SPLITS,
        help="Dataset split to compare.",
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
    parser.add_argument(
        "--max-recovered-source-context-gaps",
        type=int,
        default=None,
        help=(
            "Fail if recovered no_source_context_for_required_source count is "
            "greater than this value."
        ),
    )
    parser.add_argument(
        "--min-fallback-agent-reduction",
        type=int,
        default=None,
        help="Fail if fallback_agent_count_reduction is below this value.",
    )
    parser.add_argument(
        "--min-recovered-eval-cases",
        type=int,
        default=None,
        help="Fail if fewer than this many eval cases recover dispatch.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_real_source_context_recovery_eval(
            repo_root=args.repo_root,
            case_source_manifest_path=args.case_source_manifest,
            artifact_search_roots=args.artifact_search_root,
            image_search_roots=args.image_search_root,
            artifact_filename_aliases=_parse_aliases(args.artifact_filename_alias),
            image_filename_aliases=_parse_aliases(args.image_filename_alias),
            source_dependency_manifest_path=args.source_dependency_manifest or None,
            output_dir=args.output_dir,
            report_path=args.report or None,
            include_local_seeds=not args.no_local_seeds,
            eval_split=args.split,
            train_split=args.train_split,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))

    baseline = report["baseline"]
    recovered = report["recovered"]
    delta = report["delta"]
    print(f"Real source-context recovery eval: {report['artifacts']['report_path']}")
    print(
        "Source context signals: "
        f"{baseline['source_context_signal_count']} -> "
        f"{recovered['source_context_signal_count']} "
        f"(delta {delta['source_context_signal_count']})"
    )
    print(
        "Dry-run fallback_agent_count: "
        f"{baseline['fallback_agent_count']} -> "
        f"{recovered['fallback_agent_count']} "
        f"(reduction {delta['fallback_agent_count_reduction']})"
    )
    baseline_gap = baseline["data_gap_counts"].get(
        "no_source_context_for_required_source",
        0,
    )
    recovered_gap = recovered["data_gap_counts"].get(
        "no_source_context_for_required_source",
        0,
    )
    print(
        "Dry-run no_source_context_for_required_source: "
        f"{baseline_gap} -> {recovered_gap} "
        f"(reduction {delta['no_source_context_for_required_source_reduction']})"
    )
    print(f"Recovered eval cases: {report['recovered_eval_case_count']}")
    print(f"Status: {report['status']}")

    threshold_failures = _threshold_failures(
        report,
        max_recovered_source_context_gaps=args.max_recovered_source_context_gaps,
        min_fallback_agent_reduction=args.min_fallback_agent_reduction,
        min_recovered_eval_cases=args.min_recovered_eval_cases,
    )
    if threshold_failures:
        print("Thresholds: failed", file=sys.stderr)
        for failure in threshold_failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    if _thresholds_requested(
        args.max_recovered_source_context_gaps,
        args.min_fallback_agent_reduction,
        args.min_recovered_eval_cases,
    ):
        print("Thresholds: passed")
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


def _threshold_failures(
    report: dict,
    *,
    max_recovered_source_context_gaps: int | None,
    min_fallback_agent_reduction: int | None,
    min_recovered_eval_cases: int | None,
) -> list[str]:
    failures: list[str] = []
    recovered_gaps = int(
        report["recovered"]["data_gap_counts"].get(
            "no_source_context_for_required_source",
            0,
        )
    )
    fallback_reduction = int(report["delta"]["fallback_agent_count_reduction"])
    recovered_eval_cases = int(report["recovered_eval_case_count"])

    if (
        max_recovered_source_context_gaps is not None
        and recovered_gaps > max_recovered_source_context_gaps
    ):
        failures.append(
            "recovered no_source_context_for_required_source "
            f"{recovered_gaps} > {max_recovered_source_context_gaps}"
        )
    if (
        min_fallback_agent_reduction is not None
        and fallback_reduction < min_fallback_agent_reduction
    ):
        failures.append(
            "fallback_agent_count_reduction "
            f"{fallback_reduction} < {min_fallback_agent_reduction}"
        )
    if (
        min_recovered_eval_cases is not None
        and recovered_eval_cases < min_recovered_eval_cases
    ):
        failures.append(
            f"recovered_eval_case_count {recovered_eval_cases} < "
            f"{min_recovered_eval_cases}"
        )
    return failures


def _thresholds_requested(*values: int | None) -> bool:
    return any(value is not None for value in values)


if __name__ == "__main__":
    raise SystemExit(main())
