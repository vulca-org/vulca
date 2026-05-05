"""Rule-based tiny router baselines for redraw case records."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from vulca.layers.redraw_cases import FAILURE_TYPES, PREFERRED_ACTIONS

POLICY_LABEL_ORACLE = "label_oracle"
POLICY_OBSERVABLE_SIGNAL = "observable_signal"
POLICIES: frozenset[str] = frozenset({POLICY_LABEL_ORACLE, POLICY_OBSERVABLE_SIGNAL})

ESCALATION_ACTIONS: frozenset[str] = frozenset(
    {"manual_review", "fallback_to_agent", "fallback_to_original"}
)

LABEL_ORACLE_FAILURE_ACTIONS: dict[str, str] = {
    "mask_too_broad": "adjust_mask",
    "route_error": "adjust_route",
    "pasteback_mismatch": "manual_review",
    "over_split": "fallback_to_original",
    "under_split": "fallback_to_agent",
    "alpha_expansion": "adjust_mask",
    "background_bleed": "adjust_mask",
    "large_white_component": "adjust_mask",
    "wrong_subject": "adjust_instruction",
    "missing_detail": "adjust_instruction",
    "color_drift": "rerun",
    "shape_collapse": "rerun",
    "over_smoothing": "rerun",
    "texture_leak": "rerun",
    "uncertain": "manual_review",
}

QUALITY_FAILURE_ALIASES: dict[str, tuple[str, str]] = {
    "mask_too_broad": ("mask_too_broad", "adjust_mask"),
    "mask_too_broad_for_target": ("mask_too_broad", "adjust_mask"),
    "alpha_expansion": ("alpha_expansion", "adjust_mask"),
    "alpha_bbox_expanded": ("alpha_expansion", "adjust_mask"),
    "background_bleed": ("background_bleed", "adjust_mask"),
    "large_white_component": ("large_white_component", "adjust_mask"),
    "route_error": ("route_error", "adjust_route"),
    "pasteback_mismatch": ("pasteback_mismatch", "manual_review"),
}


@dataclass(frozen=True)
class RouterRecommendation:
    policy_name: str
    recommended_action: str
    failure_hint: str = ""
    accept_prediction: bool | None = None
    rule_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_name": self.policy_name,
            "recommended_action": self.recommended_action,
            "failure_hint": self.failure_hint,
            "accept_prediction": self.accept_prediction,
            "rule_reason": self.rule_reason,
        }


def recommend_action(
    record: Mapping[str, Any],
    *,
    policy_name: str = POLICY_OBSERVABLE_SIGNAL,
) -> RouterRecommendation:
    if policy_name == POLICY_LABEL_ORACLE:
        return _recommend_label_oracle(record)
    if policy_name == POLICY_OBSERVABLE_SIGNAL:
        return _recommend_observable_signal(record)
    raise ValueError(
        f"unsupported router baseline policy {policy_name!r}; expected one of {sorted(POLICIES)}"
    )


def evaluate_records(
    records: Iterable[Mapping[str, Any]],
    *,
    policy_name: str = POLICY_OBSERVABLE_SIGNAL,
) -> dict[str, Any]:
    items = list(records)
    recommendations = [recommend_action(item, policy_name=policy_name) for item in items]

    action_total = 0
    action_correct = 0
    accept_total = 0
    accept_correct = 0
    failure_total = 0
    failure_correct = 0
    y_true_failure: list[str] = []
    y_pred_failure: list[str] = []
    confusion_by_failure: dict[str, dict[str, int]] = {}
    confusion_by_action: dict[str, dict[str, int]] = {}

    for record, recommendation in zip(items, recommendations, strict=True):
        review = _mapping(record.get("review"))
        target_action = str(review.get("preferred_action") or "")
        if target_action:
            action_total += 1
            action_correct += int(recommendation.recommended_action == target_action)

        human_accept = review.get("human_accept")
        if isinstance(human_accept, bool) and recommendation.accept_prediction is not None:
            accept_total += 1
            accept_correct += int(recommendation.accept_prediction is human_accept)

        target_failure = str(review.get("failure_type") or "")
        if target_failure:
            failure_total += 1
            predicted_failure = recommendation.failure_hint or "none"
            y_true_failure.append(target_failure)
            y_pred_failure.append(predicted_failure)
            failure_correct += int(predicted_failure == target_failure)
            _increment_nested(
                confusion_by_failure,
                target_failure,
                recommendation.recommended_action,
            )
            _increment_nested(
                confusion_by_action,
                recommendation.recommended_action,
                target_failure,
            )

    case_count = len(items)
    covered_count = sum(1 for item in recommendations if item.recommended_action)
    manual_review_count = sum(
        1 for item in recommendations if item.recommended_action == "manual_review"
    )
    escalation_count = sum(
        1 for item in recommendations if item.recommended_action in ESCALATION_ACTIONS
    )

    return {
        "policy_name": policy_name,
        "case_count": case_count,
        "covered_count": covered_count,
        "coverage": _ratio(covered_count, case_count),
        "action_labeled_count": action_total,
        "action_accuracy": _ratio(action_correct, action_total),
        "accept_labeled_count": accept_total,
        "accept_reject_accuracy": _ratio(accept_correct, accept_total),
        "failure_labeled_count": failure_total,
        "failure_classification_accuracy": _ratio(failure_correct, failure_total),
        "failure_macro_f1": _macro_f1(y_true_failure, y_pred_failure),
        "manual_review_rate": _ratio(manual_review_count, case_count),
        "escalation_rate": _ratio(escalation_count, case_count),
        "confusion_by_failure": confusion_by_failure,
        "confusion_by_action": confusion_by_action,
        "recommendations": [item.to_dict() for item in recommendations],
    }


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            value = json.loads(stripped)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not a JSON object")
            records.append(value)
    return records


def load_jsonl_many(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        records.extend(load_jsonl(path))
    return records


def _recommend_label_oracle(record: Mapping[str, Any]) -> RouterRecommendation:
    review = _mapping(record.get("review"))

    if review.get("human_accept") is True:
        return _recommend(
            POLICY_LABEL_ORACLE,
            "accept",
            "",
            "human_accept_true",
        )

    preferred_action = str(review.get("preferred_action") or "")
    if preferred_action:
        _validate_action(preferred_action)
        failure_type = str(review.get("failure_type") or "")
        return _recommend(
            POLICY_LABEL_ORACLE,
            preferred_action,
            _valid_failure_hint(failure_type),
            "preferred_action_label",
        )

    failure_type = str(review.get("failure_type") or "")
    if failure_type:
        _validate_failure(failure_type)
        action = LABEL_ORACLE_FAILURE_ACTIONS.get(failure_type, "manual_review")
        return _recommend(
            POLICY_LABEL_ORACLE,
            action,
            failure_type,
            f"failure_type:{failure_type}",
        )

    return _recommend(
        POLICY_LABEL_ORACLE,
        "manual_review",
        "uncertain",
        "missing_review_label",
    )


def _recommend_observable_signal(record: Mapping[str, Any]) -> RouterRecommendation:
    route = _mapping(record.get("route"))
    quality = _mapping(record.get("quality"))
    metrics = _mapping(quality.get("metrics"))
    refinement = _mapping(record.get("refinement"))
    artifacts = _mapping(record.get("artifacts"))

    if _has_pasteback_problem(record, artifacts):
        return _recommend(
            POLICY_OBSERVABLE_SIGNAL,
            "manual_review",
            "pasteback_mismatch",
            "pasteback_missing_or_failed",
        )

    route_failure = _route_failure_hint(route)
    if route_failure:
        return _recommend(
            POLICY_OBSERVABLE_SIGNAL,
            "adjust_route",
            route_failure,
            "route_fields_mismatch",
        )

    failure_hint, action = _quality_failure_action(_quality_failures(quality), metrics)
    if action:
        return _recommend(
            POLICY_OBSERVABLE_SIGNAL,
            action,
            failure_hint,
            f"quality_signal:{failure_hint}",
        )

    if _refinement_indicates_broad_mask(refinement, record):
        return _recommend(
            POLICY_OBSERVABLE_SIGNAL,
            "adjust_mask",
            "mask_too_broad",
            "refinement_expected_but_not_applied",
        )

    if quality.get("gate_passed") is True and artifacts.get("source_pasteback_path"):
        return _recommend(
            POLICY_OBSERVABLE_SIGNAL,
            "accept",
            "",
            "quality_passed_with_pasteback",
        )

    if quality.get("gate_passed") is False:
        return _recommend(
            POLICY_OBSERVABLE_SIGNAL,
            "rerun",
            "uncertain",
            "quality_failed_without_specific_cause",
        )

    return _recommend(
        POLICY_OBSERVABLE_SIGNAL,
        "manual_review",
        "uncertain",
        "inconclusive_observable_signals",
    )


def _recommend(
    policy_name: str,
    action: str,
    failure_hint: str,
    reason: str,
) -> RouterRecommendation:
    _validate_action(action)
    if failure_hint:
        _validate_failure(failure_hint)
    return RouterRecommendation(
        policy_name=policy_name,
        recommended_action=action,
        failure_hint=failure_hint,
        accept_prediction=action == "accept",
        rule_reason=reason,
    )


def _has_pasteback_problem(
    record: Mapping[str, Any],
    artifacts: Mapping[str, Any],
) -> bool:
    if record.get("source_pasteback_error") or artifacts.get("source_pasteback_error"):
        return True
    if artifacts.get("source_pasteback_path"):
        return False
    quality = _mapping(record.get("quality"))
    return quality.get("gate_passed") is True


def _route_failure_hint(route: Mapping[str, Any]) -> str:
    requested = str(route.get("requested") or "")
    chosen = str(route.get("chosen") or "")
    redraw_route = str(route.get("redraw_route") or "")
    geometry_route = str(route.get("geometry_redraw_route") or "")
    if redraw_route and geometry_route and redraw_route != geometry_route:
        return "route_error"
    if requested and requested != "auto" and chosen and requested != chosen:
        return "route_error"
    return ""


def _quality_failure_action(
    failures: Sequence[str],
    metrics: Mapping[str, Any],
) -> tuple[str, str]:
    for failure in failures:
        if failure in QUALITY_FAILURE_ALIASES:
            return QUALITY_FAILURE_ALIASES[failure]

    metric_aliases = {
        "alpha_bbox_expanded": "alpha_expansion",
        "background_bleed": "background_bleed",
        "large_white_component": "large_white_component",
    }
    for key, failure_hint in metric_aliases.items():
        if _metric_positive(metrics.get(key)):
            return failure_hint, "adjust_mask"
    if _float(metrics.get("bbox_ratio")) > 2.5:
        return "alpha_expansion", "adjust_mask"
    if _float(metrics.get("white_like_pct")) > 85.0:
        return "large_white_component", "adjust_mask"
    return "", ""


def _refinement_indicates_broad_mask(
    refinement: Mapping[str, Any],
    record: Mapping[str, Any],
) -> bool:
    if refinement.get("applied") is True:
        return False
    reason = str(refinement.get("reason") or "")
    child_count = _int(refinement.get("child_count"))
    if reason in {"target_profile_detected", "broad_mask", "candidate_children_missing"}:
        return child_count <= 0
    geometry = _mapping(record.get("geometry"))
    return (
        _float(geometry.get("area_pct")) > 5.0
        and _float(refinement.get("mask_granularity_score")) <= 0.0
        and reason not in {"", "no_target_profile"}
    )


def _quality_failures(quality: Mapping[str, Any]) -> tuple[str, ...]:
    raw = quality.get("failures") or ()
    if isinstance(raw, str):
        return (raw,)
    if isinstance(raw, Iterable):
        return tuple(str(item) for item in raw)
    return ()


def _valid_failure_hint(value: str) -> str:
    if not value:
        return ""
    _validate_failure(value)
    return value


def _validate_action(value: str) -> None:
    if value not in PREFERRED_ACTIONS or not value:
        raise ValueError(
            f"unsupported router recommended_action {value!r}; expected one of {sorted(PREFERRED_ACTIONS - {''})}"
        )


def _validate_failure(value: str) -> None:
    if value not in FAILURE_TYPES:
        raise ValueError(
            f"unsupported router failure_hint {value!r}; expected one of {sorted(FAILURE_TYPES)}"
        )


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _metric_positive(value: Any) -> bool:
    return _float(value) > 0.0


def _float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def _increment_nested(table: dict[str, dict[str, int]], key: str, nested_key: str) -> None:
    nested = table.setdefault(key, {})
    nested[nested_key] = nested.get(nested_key, 0) + 1


def _macro_f1(y_true: Sequence[str], y_pred: Sequence[str]) -> float | None:
    if not y_true:
        return None
    labels = sorted(set(y_true) | set(y_pred))
    scores: list[float] = []
    for label in labels:
        tp = sum(1 for true, pred in zip(y_true, y_pred, strict=True) if true == label and pred == label)
        fp = sum(1 for true, pred in zip(y_true, y_pred, strict=True) if true != label and pred == label)
        fn = sum(1 for true, pred in zip(y_true, y_pred, strict=True) if true == label and pred != label)
        denominator = (2 * tp) + fp + fn
        scores.append((2 * tp) / denominator if denominator else 0.0)
    return sum(scores) / len(scores)
