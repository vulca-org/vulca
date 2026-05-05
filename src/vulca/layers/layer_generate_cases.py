"""Versioned case records for layer generation learning loops."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

CASE_SCHEMA_VERSION = 1
CASE_TYPE = "layer_generate_case"

FAILURE_TYPES: frozenset[str] = frozenset(
    {
        "layer_mismatch",
        "missing_layer",
        "wrong_semantic_role",
        "z_order_error",
        "style_drift",
        "prompt_conflict",
        "alpha_failure",
        "composite_mismatch",
        "provider_failure",
        "uncertain",
    }
)

PREFERRED_ACTIONS: frozenset[str] = frozenset(
    {
        "",
        "accept",
        "rerun_layer",
        "adjust_prompt",
        "merge_layers",
        "split_layer",
        "adjust_alpha_strategy",
        "fallback_to_agent",
        "manual_review",
    }
)

ROUTE_RECOMMENDATIONS: frozenset[str] = frozenset(
    {
        "",
        "direct_generation",
        "rerun_layer",
        "adjust_prompt",
        "merge_layers",
        "split_layer",
        "adjust_alpha_strategy",
        "fallback_to_agent",
        "manual_review",
    }
)

FORBIDDEN_SIBLING_FIELDS: frozenset[str] = frozenset(
    {
        "route",
        "geometry",
        "refinement",
        "detector",
        "segmentation_confidence",
        "residual_extraction_status",
        "extraction_provenance",
    }
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_failure_type(value: str) -> str:
    if value == "":
        return ""
    if value not in FAILURE_TYPES:
        raise ValueError(
            "unsupported layer_generate failure_type "
            f"{value!r}; expected one of {sorted(FAILURE_TYPES)}"
        )
    return value


def validate_preferred_action(value: str) -> str:
    if value not in PREFERRED_ACTIONS:
        raise ValueError(
            "unsupported layer_generate preferred_action "
            f"{value!r}; expected one of {sorted(PREFERRED_ACTIONS)}"
        )
    return value


def validate_route_recommendation(value: str) -> str:
    if value not in ROUTE_RECOMMENDATIONS:
        raise ValueError(
            "unsupported layer_generate route_recommendation "
            f"{value!r}; expected one of {sorted(ROUTE_RECOMMENDATIONS)}"
        )
    return value


def build_layer_generate_case(
    *,
    user_intent: str,
    tradition: str,
    style_constraints: Mapping[str, Any] | None = None,
    layer_plan: Mapping[str, Any] | None = None,
    prompt_stack: Mapping[str, Any] | None = None,
    provider: str,
    model: str,
    artifact_dir: str = "",
    layer_manifest_path: str,
    layers: list[Mapping[str, Any]],
    composite_path: str = "",
    preview_path: str = "",
    decisions: Mapping[str, Any] | None = None,
    learning_targets: Mapping[str, Any] | None = None,
    created_at: str | None = None,
    human_accept: bool | None = None,
    failure_type: str = "",
    preferred_action: str = "",
    reviewer: str = "",
    reviewed_at: str = "",
) -> dict[str, Any]:
    style = dict(style_constraints or {})
    plan = dict(layer_plan or {})
    prompts = dict(prompt_stack or {})
    normalized_layers = _normalize_layers(layers)
    _reject_forbidden_sibling_fields(style)
    _reject_forbidden_sibling_fields(plan)
    _reject_forbidden_sibling_fields(prompts)
    if decisions is not None:
        _reject_forbidden_sibling_fields(decisions)
    created = created_at or utc_now_iso()
    checked_failure = validate_failure_type(failure_type)
    checked_action = validate_preferred_action(preferred_action)
    normalized_learning_targets = _normalize_learning_targets(learning_targets)
    case_id = _make_case_id(
        created_at=created,
        user_intent=user_intent,
        tradition=tradition,
        layer_plan=plan,
        prompt_stack=prompts,
        provider=provider,
        model=model,
        layer_manifest_path=layer_manifest_path,
    )
    generated_decisions = dict(decisions or _derive_decisions(plan, normalized_layers))
    record = {
        "schema_version": CASE_SCHEMA_VERSION,
        "case_type": CASE_TYPE,
        "case_id": case_id,
        "created_at": created,
        "inputs": {
            "user_intent": str(user_intent),
            "tradition": str(tradition),
            "style_constraints": style,
            "layer_plan": plan,
            "prompt_stack": prompts,
            "provider": str(provider),
            "model": str(model),
        },
        "decisions": generated_decisions,
        "outputs": {
            "artifact_dir": str(artifact_dir or ""),
            "layer_manifest_path": str(layer_manifest_path),
            "layers": normalized_layers,
            "composite_path": str(composite_path or ""),
            "preview_path": str(preview_path or ""),
        },
        "learning_targets": normalized_learning_targets,
        "review": {
            "human_accept": human_accept,
            "failure_type": checked_failure,
            "preferred_action": checked_action,
            "reviewer": str(reviewer or ""),
            "reviewed_at": str(reviewed_at or ""),
        },
    }
    _reject_forbidden_sibling_fields(record)
    return record


def _normalize_layers(layers: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not layers:
        raise ValueError("layer_generate_case requires at least one output layer")
    normalized = []
    for item in layers:
        semantic_path = str(item.get("semantic_path", ""))
        asset_path = str(item.get("asset_path", ""))
        if not semantic_path:
            raise ValueError("layer_generate_case output layer requires semantic_path")
        if not asset_path:
            raise ValueError("layer_generate_case output layer requires asset_path")
        normalized.append(
            {
                "semantic_path": semantic_path,
                "asset_path": asset_path,
                "mask_path": str(item.get("mask_path", "")),
                "alpha_path": str(item.get("alpha_path", "")),
                "visible": bool(item.get("visible", True)),
                "locked": bool(item.get("locked", False)),
                "status": str(item.get("status", "generated")),
            }
        )
    return normalized


def _derive_decisions(
    layer_plan: Mapping[str, Any],
    layers: list[Mapping[str, Any]],
) -> dict[str, Any]:
    planned_layers = list(layer_plan.get("layers", []))
    planned_count = int(layer_plan.get("desired_layer_count") or len(planned_layers))
    semantic_roles = [
        {
            "semantic_path": str(item.get("semantic_path", "")),
            "role": str(item.get("role", "")),
            "required": bool(item.get("required", False)),
        }
        for item in planned_layers
    ]
    z_index = [
        {
            "semantic_path": str(item.get("semantic_path", "")),
            "z_index": int(item.get("z_index", index)),
            "reason": "layer_plan",
        }
        for index, item in enumerate(planned_layers)
    ]
    per_layer = [
        {
            "semantic_path": str(item.get("semantic_path", "")),
            "alpha_strategy": str(item.get("alpha_strategy", "")),
            "mask_source": str(item.get("mask_source", "none")),
        }
        for item in planned_layers
    ]
    accepted_count = sum(1 for item in layers if item.get("status") == "accepted")
    return {
        "layer_count": {
            "planned": planned_count,
            "generated": len(layers),
            "accepted": accepted_count,
        },
        "semantic_roles": semantic_roles,
        "z_index": z_index,
        "mask_alpha_strategy": {
            "canvas_mode": "full_canvas_rgba_layers",
            "composite_blend_order": "ascending_z_index",
            "per_layer": per_layer,
        },
        "fallback_decisions": [],
    }


def _normalize_learning_targets(
    value: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if value is None:
        return {
            "tiny_model": {
                "failure_classification": "",
                "quality_score": None,
                "route_recommendation": "",
            },
            "tiny_agent": {
                "next_action_policy": "",
            },
        }
    tiny_model = dict(value.get("tiny_model", {}) or {})
    tiny_agent = dict(value.get("tiny_agent", {}) or {})
    failure_classification = validate_failure_type(
        str(tiny_model.get("failure_classification", ""))
    )
    route_recommendation = validate_route_recommendation(
        str(tiny_model.get("route_recommendation", ""))
    )
    next_action_policy = validate_preferred_action(
        str(tiny_agent.get("next_action_policy", ""))
    )
    return {
        "tiny_model": {
            "failure_classification": failure_classification,
            "quality_score": tiny_model.get("quality_score"),
            "route_recommendation": route_recommendation,
        },
        "tiny_agent": {
            "next_action_policy": next_action_policy,
        },
    }


def _reject_forbidden_sibling_fields(value: Any, path: str = "record") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in FORBIDDEN_SIBLING_FIELDS:
                raise ValueError(
                    f"forbidden sibling case field {path}.{key}: "
                    "layer_generate_case cannot contain redraw or decompose "
                    "case provenance"
                )
            _reject_forbidden_sibling_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_sibling_fields(child, f"{path}[{index}]")


def _make_case_id(
    *,
    created_at: str,
    user_intent: str,
    tradition: str,
    layer_plan: Mapping[str, Any],
    prompt_stack: Mapping[str, Any],
    provider: str,
    model: str,
    layer_manifest_path: str,
) -> str:
    stamp = (
        created_at.replace("-", "")
        .replace(":", "")
        .replace(".", "")
        .replace("+", "")
    )
    seed = "\n".join(
        [
            created_at,
            user_intent,
            tradition,
            json.dumps(dict(layer_plan), sort_keys=True),
            json.dumps(dict(prompt_stack), sort_keys=True),
            provider,
            model,
            layer_manifest_path,
        ]
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"layer_generate_{stamp}_{digest}"


def append_layer_generate_case(
    case_log_path: str,
    record: Mapping[str, Any],
) -> str:
    if not case_log_path:
        raise ValueError("case_log_path is required when appending a layer case")
    path = Path(case_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
        fh.write("\n")
    return str(path)
