"""Provider-free tiny action classifier for exported tiny datasets."""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from vulca.learning.tiny_dataset import (
    DATASET_SPLITS,
    SUPPORTED_PREDICTION_ACTIONS,
    load_tiny_dataset_examples,
)


POLICY_TINY_ACTION_MODEL = "tiny_action_model_v1"
SOURCE_POLICY_TRAIN_SPARSE = "train_sparse_feature_classifier"
TRAINING_MODE_SPARSE_FEATURE_BASELINE = "sparse_feature_baseline"
FAILURE_HINT_ACTION_PRIORS: Mapping[str, str] = {
    "alpha_expansion": "adjust_mask",
    "background_bleed": "adjust_mask",
    "color_drift": "adjust_mask",
    "layer_order": "manual_review",
    "large_white_component": "adjust_mask",
    "mask_leak": "adjust_mask",
    "mask_too_broad": "adjust_mask",
    "missing_detail": "adjust_instruction",
    "occlusion": "fallback_to_agent",
    "over_segmentation": "merge_layers",
    "over_split": "fallback_to_original",
    "pasteback_mismatch": "manual_review",
    "prompt_ambiguity": "adjust_prompt",
    "route_error": "adjust_route",
    "style_drift": "adjust_prompt",
    "under_segmentation": "split_layer_further",
    "under_split": "fallback_to_agent",
    "wrong_subject": "adjust_instruction",
}
_AUX_TEXT_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9]{2,31}")
_AUX_TEXT_STOPWORDS: frozenset[str] = frozenset(
    {
        "and",
        "are",
        "for",
        "from",
        "into",
        "next",
        "of",
        "on",
        "the",
        "this",
        "with",
    }
)
_AUX_TEXT_MAX_TOKENS = 12


@dataclass(frozen=True)
class TinyActionModelPredictionResult:
    output_path: str
    policy_name: str
    split: str
    train_split: str
    prediction_count: int


@dataclass(frozen=True)
class TinyActionClassifier:
    """Explainable train-derived sparse feature baseline for tiny action prediction."""

    train_split: str
    train_example_count: int
    feature_action_counts: Mapping[str, Counter[str]]
    global_action_counts: Counter[str]

    @classmethod
    def fit(
        cls,
        examples: Iterable[Mapping[str, Any]],
        *,
        train_split: str = "train",
    ) -> "TinyActionClassifier":
        _validate_split(train_split)
        feature_action_counts: dict[str, Counter[str]] = {}
        global_action_counts: Counter[str] = Counter()
        train_example_count = 0

        for example in examples:
            if example.get("split") != train_split:
                continue
            action = _target_action(example)
            if not action:
                continue
            if action not in SUPPORTED_PREDICTION_ACTIONS:
                raise ValueError(f"unsupported tiny action model target action {action!r}")

            train_example_count += 1
            global_action_counts[action] += 1
            for feature in sorted(set(extract_tiny_action_features(example))):
                feature_action_counts.setdefault(feature, Counter())[action] += 1

        return cls(
            train_split=train_split,
            train_example_count=train_example_count,
            feature_action_counts=feature_action_counts,
            global_action_counts=global_action_counts,
        )

    def predict(self, example: Mapping[str, Any]) -> dict[str, Any]:
        source_case = _mapping(example.get("source_case"))
        case_record = _case_record(example)
        features = sorted(set(extract_tiny_action_features(example)))
        failure_hints = extract_failure_hints(example)
        action_hints = extract_action_hints(example)
        matched_features: list[str] = []
        feature_votes: list[dict[str, Any]] = []
        action_scores: dict[str, float] = {}

        for feature in features:
            counts = self.feature_action_counts.get(feature)
            if not counts:
                continue
            matched_features.append(feature)
            weight = _feature_weight(feature)
            top_action = _best_counted_action(counts, self.global_action_counts)
            feature_votes.append(
                {
                    "feature": feature,
                    "action": top_action,
                    "count": counts[top_action],
                    "weight": weight,
                }
            )
            for action, count in counts.items():
                action_scores[action] = action_scores.get(action, 0.0) + count * weight

        unseen_failure_hints = [
            hint
            for hint in failure_hints
            if f"failure_hint:{hint}" not in self.feature_action_counts
        ]
        fallback_reason = ""
        hint_action = _prior_action_for_failure_hints(failure_hints)
        direct_action_hint = _first_supported_action(action_hints)
        if direct_action_hint:
            action = direct_action_hint
            fallback_reason = "visible_action_hint"
        elif hint_action:
            action = hint_action
            fallback_reason = "failure_hint_prior"
        elif unseen_failure_hints:
            action = "manual_review"
            fallback_reason = "unseen_failure_hint"
        elif _looks_like_clean_accept(case_record, features=features):
            action = "accept"
            fallback_reason = "no_visible_failure_signal"
        elif action_scores:
            action = _best_scored_action(action_scores, self.global_action_counts)
        else:
            action = _best_counted_action(self.global_action_counts, Counter()) or "manual_review"
            fallback_reason = "global_majority"

        return {
            "policy_name": POLICY_TINY_ACTION_MODEL,
            "model_version": POLICY_TINY_ACTION_MODEL,
            "example_id": str(example.get("example_id") or ""),
            "case_id": str(source_case.get("case_id") or ""),
            "source_case_type": str(source_case.get("case_type") or ""),
            "recommended_action": action,
            "failure_hint": failure_hints[0] if failure_hints else "",
            "confidence": _confidence(action_scores, action, fallback_reason),
            "source_policy": SOURCE_POLICY_TRAIN_SPARSE,
            "explanation": {
                "training_mode": TRAINING_MODE_SPARSE_FEATURE_BASELINE,
                "train_split": self.train_split,
                "train_example_count": self.train_example_count,
                "matched_features": matched_features,
                "unseen_failure_hints": unseen_failure_hints,
                "action_hints": action_hints,
                "fallback_reason": fallback_reason,
                "action_scores": _rounded_scores(action_scores),
                "top_feature_votes": feature_votes[:5],
            },
        }


def build_tiny_action_model_predictions(
    examples: Iterable[Mapping[str, Any]],
    *,
    split: str = "test",
    train_split: str = "train",
) -> list[dict[str, Any]]:
    """Fit on train split examples and predict the requested frozen split."""
    _validate_split(split)
    _validate_split(train_split)
    items = list(examples)
    classifier = TinyActionClassifier.fit(items, train_split=train_split)
    return [
        classifier.predict(example)
        for example in items
        if example.get("split") == split
    ]


def write_tiny_action_model_predictions(
    *,
    dataset_path: str | Path,
    output_path: str | Path,
    split: str = "test",
    train_split: str = "train",
) -> TinyActionModelPredictionResult:
    predictions = build_tiny_action_model_predictions(
        load_tiny_dataset_examples(dataset_path),
        split=split,
        train_split=train_split,
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in predictions:
            fh.write(json.dumps(record, sort_keys=True, separators=(",", ":")))
            fh.write("\n")
    return TinyActionModelPredictionResult(
        output_path=str(path),
        policy_name=POLICY_TINY_ACTION_MODEL,
        split=split,
        train_split=train_split,
        prediction_count=len(predictions),
    )


def extract_tiny_action_features(example: Mapping[str, Any]) -> tuple[str, ...]:
    """Extract leak-resistant sparse features from tiny dataset model input."""
    source_case = _mapping(example.get("source_case"))
    case_record = _case_record(example)
    case_type = str(source_case.get("case_type") or case_record.get("case_type") or "")
    features: list[str] = []
    if case_type:
        features.append(f"case_type:{case_type}")

    features.extend(_quality_features(case_record))
    features.extend(_route_features(case_record))
    features.extend(_geometry_features(case_record))
    features.extend(_refinement_features(case_record))
    features.extend(_layer_generate_features(case_record))
    features.extend(_auxiliary_signal_features(example))
    return tuple(features)


def extract_failure_hints(example: Mapping[str, Any]) -> tuple[str, ...]:
    case_record = _case_record(example)
    quality = _mapping(case_record.get("quality"))
    hints: list[str] = []

    failures = quality.get("failures")
    if isinstance(failures, Sequence) and not isinstance(failures, (str, bytes)):
        hints.extend(str(item) for item in failures if str(item or ""))

    for key in (
        "over_split",
        "under_split",
        "over_segmentation",
        "under_segmentation",
        "semantic_mismatch",
        "occlusion",
        "residual_leakage",
        "alpha_quality",
    ):
        value = _mapping(quality.get(key))
        if value.get("evidence") or _positive_number(value.get("score")):
            hints.append(key)
        if key == "alpha_quality" and int(value.get("empty_layer_count") or 0) > 0:
            hints.append("empty_layer")

    return tuple(dict.fromkeys(hints))


def extract_action_hints(example: Mapping[str, Any]) -> tuple[str, ...]:
    """Extract visible next-action hints produced before human review."""
    case_record = _case_record(example)
    decisions = _mapping(case_record.get("decisions"))
    hints: list[str] = []

    fallback_decisions = decisions.get("fallback_decisions")
    if isinstance(fallback_decisions, Sequence) and not isinstance(
        fallback_decisions, (str, bytes)
    ):
        for item in fallback_decisions:
            if not isinstance(item, Mapping):
                continue
            action = str(item.get("suggested_action") or "")
            if action:
                hints.append(action)

    return tuple(dict.fromkeys(hints))


def _looks_like_clean_accept(
    case_record: Mapping[str, Any],
    *,
    features: Sequence[str],
) -> bool:
    quality = _mapping(case_record.get("quality"))
    if quality.get("gate_passed") is False:
        return False
    failures = quality.get("failures")
    if isinstance(failures, Sequence) and not isinstance(failures, (str, bytes)):
        if any(str(item or "") for item in failures):
            return False
    if any(feature.startswith("route.signal:") for feature in features):
        return False

    outputs = _mapping(case_record.get("outputs"))
    layers = outputs.get("layers")
    if isinstance(layers, Sequence) and not isinstance(layers, (str, bytes)):
        for layer in layers:
            if not isinstance(layer, Mapping):
                continue
            status = str(layer.get("status") or "")
            if status and status not in {"generated", "accepted"}:
                return False
    return True


def _quality_features(case_record: Mapping[str, Any]) -> tuple[str, ...]:
    quality = _mapping(case_record.get("quality"))
    if not quality:
        return ()

    features: list[str] = []
    gate_passed = quality.get("gate_passed")
    if isinstance(gate_passed, bool):
        features.append(f"quality.gate_passed:{str(gate_passed).lower()}")

    for hint in extract_failure_hints({"input": {"case_record": case_record}}):
        features.append(f"failure_hint:{hint}")

    layer_coverage = _mapping(quality.get("layer_coverage"))
    residual_pct = _number(layer_coverage.get("residual_pct"))
    if residual_pct is not None:
        features.append(f"quality.layer_coverage.residual_pct:{_pct_bucket(residual_pct)}")
    claimed_pct = _number(layer_coverage.get("claimed_pct"))
    if claimed_pct is not None:
        features.append(f"quality.layer_coverage.claimed_pct:{_pct_bucket(claimed_pct)}")

    return tuple(features)


def _route_features(case_record: Mapping[str, Any]) -> tuple[str, ...]:
    route = _mapping(case_record.get("route"))
    if not route:
        return ()

    features: list[str] = []
    values: dict[str, str] = {}
    for key in ("requested", "chosen", "redraw_route", "geometry_redraw_route"):
        value = str(route.get(key) or "")
        values[key] = value
        if value:
            features.append(f"route.{key}:{value}")

    chosen = values.get("chosen") or values.get("redraw_route")
    geometry_route = values.get("geometry_redraw_route")
    requested = values.get("requested")
    if chosen and geometry_route and chosen != geometry_route:
        features.append("route.signal:mismatch_chosen_geometry")
    if requested and chosen and requested != "seed" and requested != chosen:
        features.append("route.signal:mismatch_requested_chosen")
    return tuple(features)


def _geometry_features(case_record: Mapping[str, Any]) -> tuple[str, ...]:
    geometry = _mapping(case_record.get("geometry"))
    if not geometry:
        return ()

    features: list[str] = []
    area_pct = _number(geometry.get("area_pct"))
    if area_pct is not None:
        features.append(f"geometry.area_pct:{_pct_bucket(area_pct)}")
    bbox_fill = _number(geometry.get("bbox_fill"))
    if bbox_fill is not None:
        features.append(f"geometry.bbox_fill:{_ratio_bucket(bbox_fill)}")
    component_count = _number(geometry.get("component_count"))
    if component_count is not None:
        features.append(f"geometry.component_count:{_count_bucket(component_count)}")
    sparse_detected = geometry.get("sparse_detected")
    if isinstance(sparse_detected, bool):
        features.append(f"geometry.sparse_detected:{str(sparse_detected).lower()}")
    return tuple(features)


def _refinement_features(case_record: Mapping[str, Any]) -> tuple[str, ...]:
    refinement = _mapping(case_record.get("refinement"))
    if not refinement:
        return ()

    features: list[str] = []
    applied = refinement.get("applied")
    if isinstance(applied, bool):
        features.append(f"refinement.applied:{str(applied).lower()}")
    strategy = str(refinement.get("strategy") or "")
    if strategy:
        features.append(f"refinement.strategy:{strategy}")
    reason = str(refinement.get("reason") or "")
    if reason:
        features.append(f"refinement.reason:{reason}")
    child_count = _number(refinement.get("child_count"))
    if child_count is not None:
        features.append(f"refinement.child_count:{_count_bucket(child_count)}")
    granularity = _number(refinement.get("mask_granularity_score"))
    if granularity is not None:
        features.append(f"refinement.mask_granularity_score:{_ratio_bucket(granularity)}")
    return tuple(features)


def _layer_generate_features(case_record: Mapping[str, Any]) -> tuple[str, ...]:
    decisions = _mapping(case_record.get("decisions"))
    outputs = _mapping(case_record.get("outputs"))
    features: list[str] = []

    layer_count = _mapping(decisions.get("layer_count"))
    planned = _number(layer_count.get("planned"))
    generated = _number(layer_count.get("generated"))
    if planned is not None:
        features.append(f"layer_count.planned:{_count_bucket(planned)}")
    if generated is not None:
        features.append(f"layer_count.generated:{_count_bucket(generated)}")
    if planned is not None and generated is not None:
        features.append(f"layer_count.complete:{str(generated >= planned).lower()}")

    layers = outputs.get("layers")
    if isinstance(layers, Sequence) and not isinstance(layers, (str, bytes)):
        statuses = Counter(
            str(layer.get("status") or "")
            for layer in layers
            if isinstance(layer, Mapping)
        )
        for status, count in sorted(statuses.items()):
            if status:
                features.append(f"output.layer_status:{status}:{_count_bucket(count)}")
    fallback_decisions = decisions.get("fallback_decisions")
    if isinstance(fallback_decisions, Sequence) and not isinstance(
        fallback_decisions, (str, bytes)
    ):
        for item in fallback_decisions:
            if not isinstance(item, Mapping):
                continue
            action = str(item.get("suggested_action") or "")
            if action:
                features.append(f"decision.suggested_action:{action}")
    return tuple(features)


def _auxiliary_signal_features(example: Mapping[str, Any]) -> tuple[str, ...]:
    input_block = _mapping(example.get("input"))
    auxiliary_signals = input_block.get("auxiliary_signals")
    if not isinstance(auxiliary_signals, Sequence) or isinstance(
        auxiliary_signals, (str, bytes)
    ):
        return ()

    features: list[str] = []
    for signal_record in auxiliary_signals:
        if not isinstance(signal_record, Mapping):
            continue
        training_use = _mapping(signal_record.get("training_use"))
        if not bool(training_use.get("approved_for_auxiliary_training")):
            continue
        review_status = str(training_use.get("review_status") or "")
        if review_status != "reviewed_promoted":
            continue

        model_id = str(_mapping(signal_record.get("model")).get("id") or "")
        signals = _mapping(signal_record.get("signals"))
        if model_id:
            features.append(f"aux_signal.model:{model_id}")
        status = str(signals.get("status") or "")
        if status:
            features.append(f"aux_signal.status:{status}")
        features.append(f"aux_signal.review_status:{review_status}")

        signal_source = str(signals.get("signal_source") or "")
        if signal_source:
            features.append(f"aux_signal.source:{signal_source}")
        features.extend(
            _aux_text_features(
                signals.get("caption_candidates"),
                prefix="caption_token",
            )
        )
        features.extend(
            _aux_text_features(
                signals.get("dense_region_descriptions"),
                prefix="dense_token",
            )
        )
        features.extend(
            _aux_text_features(
                signals.get("ocr_text"),
                prefix="ocr_token",
                max_tokens=8,
            )
        )
        mask_count = _number(signals.get("mask_count"))
        if mask_count is not None:
            features.append(f"aux_signal.sam_mask_count:{_mask_count_bucket(mask_count)}")
        total_area = _number(signals.get("total_mask_area_pct"))
        if total_area is not None:
            features.append(
                f"aux_signal.sam_total_area_pct:{_aux_percent_bucket(total_area)}"
            )
        boundary_complexity = str(signals.get("boundary_complexity") or "")
        if boundary_complexity:
            features.append(f"aux_signal.boundary_complexity:{boundary_complexity}")
    return tuple(features)


def _aux_text_features(
    value: Any,
    *,
    prefix: str,
    max_tokens: int = _AUX_TEXT_MAX_TOKENS,
) -> tuple[str, ...]:
    tokens: list[str] = []
    for text in _flatten_aux_text(value):
        for match in _AUX_TEXT_TOKEN_RE.finditer(text.lower()):
            token = match.group(0)
            if token in _AUX_TEXT_STOPWORDS:
                continue
            tokens.append(token)
            if len(tokens) >= max_tokens:
                return _aux_token_features(prefix, tokens)
    return _aux_token_features(prefix, tokens)


def _aux_token_features(prefix: str, tokens: Sequence[str]) -> tuple[str, ...]:
    return tuple(f"aux_signal.{prefix}:{item}" for item in dict.fromkeys(tokens))


def _flatten_aux_text(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Mapping):
        texts: list[str] = []
        for child in value.values():
            texts.extend(_flatten_aux_text(child))
        return tuple(texts)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        texts = []
        for item in value:
            texts.extend(_flatten_aux_text(item))
        return tuple(texts)
    return (str(value),)


def _target_action(example: Mapping[str, Any]) -> str:
    return str(_mapping(example.get("targets")).get("preferred_action") or "")


def _prior_action_for_failure_hints(hints: Sequence[str]) -> str:
    for hint in hints:
        action = FAILURE_HINT_ACTION_PRIORS.get(hint)
        if action in SUPPORTED_PREDICTION_ACTIONS:
            return action
    return ""


def _first_supported_action(actions: Sequence[str]) -> str:
    for action in actions:
        if action in SUPPORTED_PREDICTION_ACTIONS:
            return action
    return ""


def _case_record(example: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(_mapping(example.get("input")).get("case_record"))


def _feature_weight(feature: str) -> float:
    if feature.startswith("decision.suggested_action:"):
        return 5.0
    if feature.startswith("failure_hint:"):
        return 4.0
    if feature.startswith("route.signal:"):
        return 3.0
    if feature.startswith(("quality.", "geometry.", "refinement.", "layer_count.", "output.")):
        return 2.0
    if feature.startswith("aux_signal."):
        return 1.5
    if feature.startswith("case_type:"):
        return 1.0
    return 1.0


def _confidence(
    action_scores: Mapping[str, float],
    action: str,
    fallback_reason: str,
) -> float:
    if fallback_reason == "visible_action_hint":
        return 0.88
    if fallback_reason == "failure_hint_prior":
        return 0.82
    if fallback_reason == "unseen_failure_hint":
        return 0.45
    if fallback_reason:
        return 0.4
    total = sum(action_scores.values())
    if total <= 0:
        return 0.4
    share = action_scores.get(action, 0.0) / total
    return round(min(0.95, 0.5 + share * 0.45), 3)


def _rounded_scores(scores: Mapping[str, float]) -> dict[str, float]:
    return {
        action: round(score, 4)
        for action, score in sorted(scores.items())
    }


def _best_scored_action(
    scores: Mapping[str, float],
    global_counts: Counter[str],
) -> str:
    if not scores:
        return ""
    return sorted(
        scores,
        key=lambda action: (
            -scores[action],
            -global_counts.get(action, 0),
            action,
        ),
    )[0]


def _best_counted_action(
    counts: Mapping[str, int],
    global_counts: Counter[str],
) -> str:
    if not counts:
        return ""
    return sorted(
        counts,
        key=lambda action: (
            -counts[action],
            -global_counts.get(action, 0),
            action,
        ),
    )[0]


def _pct_bucket(value: float) -> str:
    if value <= 0:
        return "zero"
    if value < 5:
        return "tiny"
    if value < 20:
        return "small"
    if value < 50:
        return "medium"
    if value < 80:
        return "large"
    return "very_large"


def _ratio_bucket(value: float) -> str:
    if value <= 0:
        return "zero"
    if value < 0.1:
        return "tiny"
    if value < 0.35:
        return "low"
    if value < 0.7:
        return "medium"
    return "high"


def _count_bucket(value: float) -> str:
    if value <= 0:
        return "zero"
    if value == 1:
        return "one"
    if value <= 3:
        return "few"
    if value <= 8:
        return "several"
    return "many"


def _mask_count_bucket(value: float) -> str:
    if value <= 0:
        return "zero"
    if value == 1:
        return "one"
    if value <= 4:
        return "2-4"
    if value <= 8:
        return "5-8"
    return "9+"


def _aux_percent_bucket(value: float) -> str:
    percent = value * 100 if 0 < value <= 1 else value
    if percent <= 0:
        return "0"
    if percent < 5:
        return "0-5"
    if percent < 25:
        return "5-25"
    if percent < 50:
        return "25-50"
    if percent < 75:
        return "50-75"
    return "75-100"


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _positive_number(value: Any) -> bool:
    number = _number(value)
    return number is not None and number > 0


def _validate_split(value: str) -> None:
    if value not in DATASET_SPLITS:
        raise ValueError(
            f"unsupported tiny action model split {value!r}; expected one of {DATASET_SPLITS}"
        )


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
