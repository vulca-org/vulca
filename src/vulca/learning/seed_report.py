"""Build baseline reports from local seed case records."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from vulca.layers.redraw_router_baseline import (
    POLICIES as REDRAW_ROUTER_POLICIES,
    POLICY_LABEL_ORACLE,
    POLICY_OBSERVABLE_SIGNAL,
    evaluate_records,
    recommend_action,
)
from vulca.learning.seed_cases import DEFAULT_SEED_MANIFEST, build_local_seed_cases


CASE_TYPE = "learning_local_seed_baseline_report"
SCHEMA_VERSION = 1
DEFAULT_BASELINE_POLICIES: tuple[str, ...] = (
    POLICY_LABEL_ORACLE,
    POLICY_OBSERVABLE_SIGNAL,
)


def build_local_seed_baseline_report(
    repo_root: str | Path,
    manifest_path: str | Path = DEFAULT_SEED_MANIFEST,
    policies: Sequence[str] = DEFAULT_BASELINE_POLICIES,
) -> dict[str, Any]:
    """Build a reproducible baseline report from tracked local seed cases."""
    checked_policies = _validate_policies(policies)
    bundle = build_local_seed_cases(repo_root, manifest_path)
    redraw_records = bundle.get("redraw_case", [])
    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": CASE_TYPE,
        "source_manifest": str(manifest_path),
        "seed_counts": {
            case_type: len(records) for case_type, records in sorted(bundle.items())
        },
        "review_summary": {
            case_type: _review_summary(records)
            for case_type, records in sorted(bundle.items())
        },
        "redraw_router_baselines": {
            policy: evaluate_records(redraw_records, policy_name=policy)
            for policy in checked_policies
        },
        "redraw_router_mismatches": {
            policy: _redraw_router_mismatches(redraw_records, policy)
            for policy in checked_policies
        },
    }


def write_local_seed_baseline_report(
    *,
    repo_root: str | Path,
    output_path: str | Path,
    manifest_path: str | Path = DEFAULT_SEED_MANIFEST,
    policies: Sequence[str] = DEFAULT_BASELINE_POLICIES,
) -> str:
    report = build_local_seed_baseline_report(
        repo_root=repo_root,
        manifest_path=manifest_path,
        policies=policies,
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return str(path)


def parse_policy_thresholds(values: Sequence[str]) -> dict[str, float]:
    """Parse CLI ``policy=value`` threshold pairs."""
    thresholds: dict[str, float] = {}
    for raw in values:
        if "=" not in raw:
            raise ValueError(
                f"invalid baseline threshold {raw!r}; expected POLICY=VALUE"
            )
        policy, value = raw.split("=", 1)
        policy = policy.strip()
        if policy not in REDRAW_ROUTER_POLICIES:
            raise ValueError(
                f"unsupported baseline policy {policy!r}; "
                f"expected one of {sorted(REDRAW_ROUTER_POLICIES)}"
            )
        try:
            thresholds[policy] = float(value.strip())
        except ValueError as exc:
            raise ValueError(
                f"invalid threshold value {value!r} for policy {policy!r}"
            ) from exc
    return thresholds


def parse_policy_int_thresholds(values: Sequence[str]) -> dict[str, int]:
    """Parse CLI ``policy=count`` threshold pairs."""
    thresholds: dict[str, int] = {}
    for policy, value in parse_policy_thresholds(values).items():
        count = int(value)
        if count != value:
            raise ValueError(
                f"integer threshold required for policy {policy!r}: {value!r}"
            )
        thresholds[policy] = count
    return thresholds


def check_baseline_report(
    report: Mapping[str, Any],
    *,
    min_action_accuracy: Mapping[str, float] | None = None,
    max_mismatches: Mapping[str, int] | None = None,
) -> list[dict[str, Any]]:
    """Return threshold violations for a local seed baseline report."""
    violations: list[dict[str, Any]] = []
    baselines = _mapping(report.get("redraw_router_baselines"))
    mismatches = _mapping(report.get("redraw_router_mismatches"))

    for policy, threshold in sorted((min_action_accuracy or {}).items()):
        metrics = _mapping(baselines.get(policy))
        actual = metrics.get("action_accuracy")
        if actual is None or float(actual) < float(threshold):
            violations.append(
                {
                    "policy": str(policy),
                    "metric": "action_accuracy",
                    "actual": actual,
                    "expected": f">= {float(threshold)}",
                }
            )

    for policy, threshold in sorted((max_mismatches or {}).items()):
        actual = len(list(mismatches.get(policy) or []))
        if actual > int(threshold):
            violations.append(
                {
                    "policy": str(policy),
                    "metric": "mismatch_count",
                    "actual": actual,
                    "expected": f"<= {int(threshold)}",
                }
            )

    return violations


def _validate_policies(policies: Sequence[str]) -> tuple[str, ...]:
    checked = tuple(str(item) for item in policies)
    if not checked:
        raise ValueError("at least one baseline policy is required")
    unsupported = sorted(set(checked) - REDRAW_ROUTER_POLICIES)
    if unsupported:
        raise ValueError(
            f"unsupported baseline policy {unsupported}; "
            f"expected one of {sorted(REDRAW_ROUTER_POLICIES)}"
        )
    return checked


def _review_summary(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    items = list(records)
    accept_counts = {"true": 0, "false": 0, "unlabeled": 0}
    failure_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()

    for record in items:
        review = _mapping(record.get("review"))
        human_accept = review.get("human_accept")
        if human_accept is True:
            accept_counts["true"] += 1
        elif human_accept is False:
            accept_counts["false"] += 1
        else:
            accept_counts["unlabeled"] += 1

        failure_type = str(review.get("failure_type") or "")
        preferred_action = str(review.get("preferred_action") or "")
        if failure_type:
            failure_counts[failure_type] += 1
        if preferred_action:
            action_counts[preferred_action] += 1

    return {
        "case_count": len(items),
        "human_accept_counts": accept_counts,
        "failure_type_counts": dict(sorted(failure_counts.items())),
        "preferred_action_counts": dict(sorted(action_counts.items())),
    }


def _redraw_router_mismatches(
    records: Iterable[Mapping[str, Any]],
    policy_name: str,
) -> list[dict[str, Any]]:
    mismatches = []
    for record in records:
        review = _mapping(record.get("review"))
        target_action = str(review.get("preferred_action") or "")
        if not target_action:
            continue
        recommendation = recommend_action(record, policy_name=policy_name)
        if recommendation.recommended_action == target_action:
            continue
        mismatches.append(
            {
                "case_id": str(record.get("case_id", "")),
                "failure_type": str(review.get("failure_type") or ""),
                "target_action": target_action,
                "recommended_action": recommendation.recommended_action,
                "failure_hint": recommendation.failure_hint,
                "rule_reason": recommendation.rule_reason,
            }
        )
    return mismatches


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
