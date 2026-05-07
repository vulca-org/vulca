"""Audit residual fallback-agent decisions after source-context recovery."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_fallback_residual_audit_report"
DEFAULT_REPORT_NAME = "fallback_residual_audit_report.json"

RESIDUAL_TINY_CONFIDENCE = "tiny_router_confidence_gap"
RESIDUAL_PROVIDER_RUNTIME = "provider_runtime_fallback"
RESIDUAL_COMPLEX_OWNERSHIP = "agent_boundary_complex_visual_ownership"
RESIDUAL_AGENT_ACTION = "agent_boundary_action_fallback"
RESIDUAL_SOURCE_CONTEXT_GAP = "source_context_gap"

NEXT_CONFIDENCE = "add_confidence_calibration_or_label"
NEXT_PROVIDER = "route_provider_failure_to_runtime_handler"
NEXT_AGENT_BOUNDARY = "keep_agent_boundary"
NEXT_SOURCE_CONTEXT = "recover_source_context"


def run_fallback_residual_audit(
    *,
    decision_path: str | Path,
    report_path: str | Path | None = None,
) -> dict[str, Any]:
    """Classify dry-run fallback-agent residuals into actionable buckets."""
    decisions = _load_jsonl(decision_path)
    fallback_decisions = [
        decision for decision in decisions if bool(_mapping(decision.get("dispatch")).get("fallback_agent"))
    ]
    residual_cases = [_residual_case(decision) for decision in fallback_decisions]
    residual_cases = sorted(
        residual_cases,
        key=lambda item: (item["residual_kind"], item["case_type"], item["case_id"]),
    )
    summary = _summary(decisions, residual_cases)
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": ("needs_agent_or_router_boundary_work" if residual_cases else "no_fallback_residuals"),
        "inputs": {
            "decision_path": Path(decision_path).name,
        },
        "summary": summary,
        "counts_by_case_type": _counter_by(residual_cases, "case_type"),
        "counts_by_residual_kind": _counter_by(residual_cases, "residual_kind"),
        "counts_by_recommended_next_step": _counter_by(
            residual_cases,
            "recommended_next_step",
        ),
        "counts_by_fallback_reason": _fallback_reason_counts(residual_cases),
        "residual_cases": residual_cases,
        "safe_handling": {
            "copies_local_paths": False,
            "copies_private_refs": False,
            "copies_raw_source_text": False,
            "calls_model_provider": False,
        },
    }
    if report_path:
        output = Path(report_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return report


def _summary(
    decisions: Sequence[Mapping[str, Any]],
    residual_cases: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    tiny_router_candidate_count = sum(1 for item in residual_cases if bool(item.get("tiny_router_candidate")))
    source_context_gap_count = sum(
        1 for item in residual_cases if item.get("residual_kind") == RESIDUAL_SOURCE_CONTEXT_GAP
    )
    return {
        "decision_count": len(decisions),
        "fallback_agent_count": len(residual_cases),
        "agent_required_count": len(residual_cases) - tiny_router_candidate_count,
        "tiny_router_candidate_count": tiny_router_candidate_count,
        "source_context_gap_count": source_context_gap_count,
    }


def _residual_case(decision: Mapping[str, Any]) -> dict[str, Any]:
    action_router = _mapping(decision.get("action_router"))
    dispatch = _mapping(decision.get("dispatch"))
    source_dependency = _mapping(decision.get("source_dependency_router"))
    source_context = _mapping(decision.get("source_context"))
    fallback_reasons = _string_list(dispatch.get("fallback_reasons"))
    data_gap_tags = _string_list(dispatch.get("data_gap_tags"))
    failure_hint = str(action_router.get("failure_hint") or "")
    residual_kind, next_step, tiny_candidate = _classify_residual(
        fallback_reasons=fallback_reasons,
        data_gap_tags=data_gap_tags,
        failure_hint=failure_hint,
    )
    return {
        "example_id": str(decision.get("example_id") or ""),
        "case_id": str(decision.get("case_id") or ""),
        "case_type": str(decision.get("source_case_type") or ""),
        "recommended_action": str(action_router.get("recommended_action") or ""),
        "action_confidence": _float_or_none(action_router.get("confidence")),
        "failure_hint": failure_hint,
        "fallback_reasons": fallback_reasons,
        "data_gap_tags": data_gap_tags,
        "source_context_available": bool(source_context.get("available")),
        "source_context_signal_count": int(source_context.get("signal_count") or 0),
        "source_dependency": str(source_dependency.get("recommended_source_dependency") or ""),
        "decision_basis": str(source_dependency.get("recommended_decision_basis") or ""),
        "residual_kind": residual_kind,
        "tiny_router_candidate": tiny_candidate,
        "recommended_next_step": next_step,
    }


def _classify_residual(
    *,
    fallback_reasons: Sequence[str],
    data_gap_tags: Sequence[str],
    failure_hint: str,
) -> tuple[str, str, bool]:
    if "no_source_context_for_required_source" in data_gap_tags:
        return RESIDUAL_SOURCE_CONTEXT_GAP, NEXT_SOURCE_CONTEXT, True
    if "low_action_confidence" in fallback_reasons:
        return RESIDUAL_TINY_CONFIDENCE, NEXT_CONFIDENCE, True
    if failure_hint == "provider_failure":
        return RESIDUAL_PROVIDER_RUNTIME, NEXT_PROVIDER, False
    if failure_hint in {"occlusion", "under_split"}:
        return RESIDUAL_COMPLEX_OWNERSHIP, NEXT_AGENT_BOUNDARY, False
    return RESIDUAL_AGENT_ACTION, NEXT_AGENT_BOUNDARY, False


def _fallback_reason_counts(
    residual_cases: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in residual_cases:
        for reason in _string_list(item.get("fallback_reasons")):
            counts[reason] += 1
    return dict(sorted(counts.items()))


def _counter_by(items: Sequence[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        value = str(item.get(key) or "unknown")
        counts[value] += 1
    return dict(sorted(counts.items()))


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, Mapping):
            records.append(dict(value))
    return records


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value]


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
