"""Tiny provider-free predictors that emit prediction JSONL."""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from vulca.layers.redraw_cases import CASE_TYPE as REDRAW_CASE_TYPE
from vulca.layers.redraw_router_baseline import (
    POLICY_OBSERVABLE_SIGNAL,
    recommend_action,
)
from vulca.learning.tiny_dataset import (
    DATASET_SPLITS,
    load_tiny_dataset_examples,
)


POLICY_TINY_CASE_TYPE_PRIOR = "tiny_case_type_prior_v0"
POLICY_TINY_AGENT = "tiny_agent_v0"
TINY_BASELINE_POLICIES: frozenset[str] = frozenset(
    {POLICY_TINY_AGENT, POLICY_TINY_CASE_TYPE_PRIOR}
)


@dataclass(frozen=True)
class TinyBaselinePredictionResult:
    output_path: str
    policy_name: str
    split: str
    train_split: str
    prediction_count: int


def build_tiny_baseline_predictions(
    examples: Iterable[Mapping[str, Any]],
    *,
    policy_name: str = POLICY_TINY_AGENT,
    split: str = "test",
    train_split: str = "train",
) -> list[dict[str, Any]]:
    """Build prediction records from a tiny train-derived baseline."""
    if policy_name not in TINY_BASELINE_POLICIES:
        raise ValueError(
            f"unsupported tiny baseline policy {policy_name!r}; "
            f"expected one of {sorted(TINY_BASELINE_POLICIES)}"
        )
    _validate_split(split)
    _validate_split(train_split)

    items = list(examples)
    prior = _ActionPrior.from_examples(
        item for item in items if item.get("split") == train_split
    )
    eval_items = [item for item in items if item.get("split") == split]
    return [
        _predict_one(item, prior=prior, policy_name=policy_name)
        for item in eval_items
    ]


def write_tiny_baseline_predictions(
    *,
    dataset_path: str | Path,
    output_path: str | Path,
    policy_name: str = POLICY_TINY_AGENT,
    split: str = "test",
    train_split: str = "train",
) -> TinyBaselinePredictionResult:
    predictions = build_tiny_baseline_predictions(
        load_tiny_dataset_examples(dataset_path),
        policy_name=policy_name,
        split=split,
        train_split=train_split,
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in predictions:
            fh.write(json.dumps(record, sort_keys=True, separators=(",", ":")))
            fh.write("\n")
    return TinyBaselinePredictionResult(
        output_path=str(path),
        policy_name=policy_name,
        split=split,
        train_split=train_split,
        prediction_count=len(predictions),
    )


@dataclass(frozen=True)
class _ActionPrior:
    by_case_type: dict[str, str]
    global_action: str

    @classmethod
    def from_examples(cls, examples: Iterable[Mapping[str, Any]]) -> "_ActionPrior":
        by_case_type_counts: dict[str, Counter[str]] = {}
        global_counts: Counter[str] = Counter()
        for example in examples:
            action = str(_mapping(example.get("targets")).get("preferred_action") or "")
            if not action:
                continue
            case_type = str(_mapping(example.get("source_case")).get("case_type") or "")
            by_case_type_counts.setdefault(case_type, Counter())[action] += 1
            global_counts[action] += 1

        return cls(
            by_case_type={
                case_type: _majority_action(counts)
                for case_type, counts in by_case_type_counts.items()
            },
            global_action=_majority_action(global_counts) or "manual_review",
        )

    def action_for(self, case_type: str) -> str:
        return self.by_case_type.get(case_type, self.global_action)


def _predict_one(
    example: Mapping[str, Any],
    *,
    prior: _ActionPrior,
    policy_name: str,
) -> dict[str, Any]:
    source_case = _mapping(example.get("source_case"))
    case_type = str(source_case.get("case_type") or "")

    if policy_name == POLICY_TINY_AGENT and case_type == REDRAW_CASE_TYPE:
        case_record = _mapping(_mapping(example.get("input")).get("case_record"))
        recommendation = recommend_action(
            case_record,
            policy_name=POLICY_OBSERVABLE_SIGNAL,
        )
        action = recommendation.recommended_action
        failure_hint = recommendation.failure_hint
        source_policy = "redraw_observable_signal"
        confidence = 0.8 if action == "manual_review" else 0.85
    else:
        action = prior.action_for(case_type)
        failure_hint = ""
        source_policy = "case_type_prior"
        confidence = 0.55

    return {
        "policy_name": policy_name,
        "example_id": str(example.get("example_id") or ""),
        "recommended_action": action,
        "failure_hint": failure_hint,
        "confidence": confidence,
        "source_policy": source_policy,
    }


def _majority_action(counts: Counter[str]) -> str:
    if not counts:
        return ""
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _validate_split(value: str) -> None:
    if value not in DATASET_SPLITS:
        raise ValueError(
            f"unsupported tiny baseline split {value!r}; expected one of {DATASET_SPLITS}"
        )


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
