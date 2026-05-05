# Layer Generate Case Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a versioned `layer_generate_case` record builder and JSONL append helper for Learning Loop evidence from intent-to-layered-artifact generation runs.

**Architecture:** Add a focused `vulca.layers.layer_generate_cases` module. It owns schema construction, stable case IDs, generation failure/action taxonomy validation, sibling-boundary validation, and JSONL append. It does not import providers, MCP, CLI, image libraries, redraw execution, or decomposition execution.

**Tech Stack:** Python 3.10+, `json`, `hashlib`, `datetime`, `pathlib`, pytest, existing package layout under `src/vulca/layers`.

---

## File Structure

- Create `src/vulca/layers/layer_generate_cases.py`
  - Owns `layer_generate_case` constants, taxonomy validation, schema construction, case ID generation, sibling-boundary validation, and JSONL append.
  - Does not import `redraw_cases.py`; both modules are siblings.

- Create `tests/test_layer_generate_cases.py`
  - Verifies schema construction, taxonomy validation, sibling-boundary rejection, stable case IDs, output layer validation, and JSONL append.

- Do not modify `src/vulca/mcp_server.py`, `src/vulca/cli.py`, `src/vulca/layers/redraw_cases.py`, or decomposition runtime files in this implementation.

## Sibling Boundary Rules

- `layer_generate_case` records plan-to-layered-artifact generation only.
- A subsequent generated-layer edit is recorded by a separate `redraw_case`.
- A subsequent generated-composite split is recorded by a separate `decompose_case`.
- The implementation rejects supplied record fragments containing exact keys `route`, `geometry`, `refinement`, `detector`, `segmentation_confidence`, `residual_extraction_status`, or `extraction_provenance`.
- The key `route_recommendation` remains valid because it is a tiny model target, not a redraw route record.

## Task 1: Layer Generate Case Schema Tests

**Files:**
- Create: `tests/test_layer_generate_cases.py`
- Implementation target: `src/vulca/layers/layer_generate_cases.py`

- [ ] **Step 1: Write failing schema and boundary tests**

Create `tests/test_layer_generate_cases.py` with this content:

```python
import json

import pytest


def _style_constraints():
    return {
        "positive": ["clean readable layers", "consistent daylight"],
        "negative": ["flat single-image output"],
        "palette": ["blue sky", "green hedge", "white flowers"],
        "composition": ["roadside guardrail above flower bank"],
        "required_motifs": ["sky", "guardrail", "flower bank"],
        "prohibited_motifs": [],
    }


def _layer_plan():
    return {
        "source": "visual_plan",
        "desired_layer_count": 2,
        "layers": [
            {
                "semantic_path": "background.sky",
                "display_name": "Sky",
                "role": "background",
                "z_index": 0,
                "generation_prompt_ref": "prompts/layers/background.sky.txt",
                "alpha_strategy": "opaque_full_canvas",
                "required": True,
            },
            {
                "semantic_path": "foreground.flowers",
                "display_name": "White flowers",
                "role": "foreground",
                "z_index": 10,
                "generation_prompt_ref": "prompts/layers/foreground.flowers.txt",
                "alpha_strategy": "transparent_subject",
                "required": True,
            },
        ],
    }


def _prompt_stack():
    return {
        "system_prompt_path": "prompts/system.txt",
        "plan_prompt_path": "prompts/plan.txt",
        "layer_prompt_refs": [
            {
                "semantic_path": "background.sky",
                "prompt_path": "prompts/layers/background.sky.txt",
                "prompt_text_hash": "sha256:sky",
            },
            {
                "semantic_path": "foreground.flowers",
                "prompt_path": "prompts/layers/foreground.flowers.txt",
                "prompt_text_hash": "sha256:flowers",
            },
        ],
        "negative_prompt_path": "prompts/negative.txt",
        "provider_request": {
            "size": "1024x1024",
            "quality": "high",
            "output_format": "png",
        },
    }


def _layers():
    return [
        {
            "semantic_path": "background.sky",
            "asset_path": "runs/layered/case/background.sky.png",
            "mask_path": "",
            "alpha_path": "",
            "visible": True,
            "locked": False,
            "status": "generated",
        },
        {
            "semantic_path": "foreground.flowers",
            "asset_path": "runs/layered/case/foreground.flowers.png",
            "mask_path": "runs/layered/case/foreground.flowers.mask.png",
            "alpha_path": "runs/layered/case/foreground.flowers.alpha.png",
            "visible": True,
            "locked": False,
            "status": "generated",
        },
    ]


def test_build_layer_generate_case_minimal_schema():
    from vulca.layers.layer_generate_cases import build_layer_generate_case

    record = build_layer_generate_case(
        user_intent="Create a layered roadside botanical scene.",
        tradition="ipad_cartoon_showcase",
        style_constraints=_style_constraints(),
        layer_plan=_layer_plan(),
        prompt_stack=_prompt_stack(),
        provider="openai",
        model="gpt-image-2",
        artifact_dir="runs/layered/case",
        layer_manifest_path="runs/layered/case/manifest.json",
        layers=_layers(),
        composite_path="runs/layered/case/composite.png",
        preview_path="runs/layered/case/preview.png",
        created_at="2026-05-05T12:00:00Z",
    )

    assert record["schema_version"] == 1
    assert record["case_type"] == "layer_generate_case"
    assert record["case_id"].startswith("layer_generate_20260505T120000Z_")
    assert record["created_at"] == "2026-05-05T12:00:00Z"
    assert record["inputs"]["user_intent"] == (
        "Create a layered roadside botanical scene."
    )
    assert record["inputs"]["tradition"] == "ipad_cartoon_showcase"
    assert record["inputs"]["provider"] == "openai"
    assert record["inputs"]["model"] == "gpt-image-2"
    assert record["inputs"]["style_constraints"]["positive"] == [
        "clean readable layers",
        "consistent daylight",
    ]
    assert record["inputs"]["layer_plan"]["desired_layer_count"] == 2
    assert record["inputs"]["prompt_stack"]["provider_request"]["quality"] == "high"
    assert record["decisions"]["layer_count"] == {
        "planned": 2,
        "generated": 2,
        "accepted": 0,
    }
    assert record["decisions"]["semantic_roles"] == [
        {
            "semantic_path": "background.sky",
            "role": "background",
            "required": True,
        },
        {
            "semantic_path": "foreground.flowers",
            "role": "foreground",
            "required": True,
        },
    ]
    assert record["decisions"]["z_index"][0] == {
        "semantic_path": "background.sky",
        "z_index": 0,
        "reason": "layer_plan",
    }
    assert record["decisions"]["mask_alpha_strategy"]["canvas_mode"] == (
        "full_canvas_rgba_layers"
    )
    assert record["decisions"]["fallback_decisions"] == []
    assert record["outputs"]["artifact_dir"] == "runs/layered/case"
    assert record["outputs"]["layer_manifest_path"] == (
        "runs/layered/case/manifest.json"
    )
    assert record["outputs"]["layers"][1]["asset_path"].endswith(
        "foreground.flowers.png"
    )
    assert record["outputs"]["composite_path"] == "runs/layered/case/composite.png"
    assert record["outputs"]["preview_path"] == "runs/layered/case/preview.png"
    assert record["learning_targets"] == {
        "tiny_model": {
            "failure_classification": "",
            "quality_score": None,
            "route_recommendation": "",
        },
        "tiny_agent": {
            "next_action_policy": "",
        },
    }
    assert record["review"] == {
        "human_accept": None,
        "failure_type": "",
        "preferred_action": "",
        "reviewer": "",
        "reviewed_at": "",
    }


def test_layer_generate_case_rejects_redraw_route_geometry_refinement_fields():
    from vulca.layers.layer_generate_cases import build_layer_generate_case

    with pytest.raises(ValueError, match="forbidden sibling case field"):
        build_layer_generate_case(
            user_intent="Generate layers.",
            tradition="test",
            style_constraints=_style_constraints(),
            layer_plan=_layer_plan(),
            prompt_stack=_prompt_stack(),
            provider="openai",
            model="gpt-image-2",
            layer_manifest_path="runs/layered/case/manifest.json",
            layers=_layers(),
            decisions={"route": {"chosen": "inpaint"}},
            created_at="2026-05-05T12:00:00Z",
        )

    with pytest.raises(ValueError, match="forbidden sibling case field"):
        build_layer_generate_case(
            user_intent="Generate layers.",
            tradition="test",
            style_constraints=_style_constraints(),
            layer_plan={"desired_layer_count": 1, "detector": "sam", "layers": []},
            prompt_stack=_prompt_stack(),
            provider="openai",
            model="gpt-image-2",
            layer_manifest_path="runs/layered/case/manifest.json",
            layers=_layers(),
            created_at="2026-05-05T12:00:00Z",
        )


def test_layer_generate_case_requires_per_layer_asset_paths():
    from vulca.layers.layer_generate_cases import build_layer_generate_case

    bad_layers = [{"semantic_path": "background.sky"}]

    with pytest.raises(ValueError, match="asset_path"):
        build_layer_generate_case(
            user_intent="Generate layers.",
            tradition="test",
            style_constraints=_style_constraints(),
            layer_plan=_layer_plan(),
            prompt_stack=_prompt_stack(),
            provider="openai",
            model="gpt-image-2",
            layer_manifest_path="runs/layered/case/manifest.json",
            layers=bad_layers,
            created_at="2026-05-05T12:00:00Z",
        )
```

- [ ] **Step 2: Run tests to verify red**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_layer_generate_cases.py::test_build_layer_generate_case_minimal_schema tests/test_layer_generate_cases.py::test_layer_generate_case_rejects_redraw_route_geometry_refinement_fields tests/test_layer_generate_cases.py::test_layer_generate_case_requires_per_layer_asset_paths -q
```

Expected: FAIL during import with `ModuleNotFoundError: No module named 'vulca.layers.layer_generate_cases'`.

- [ ] **Step 3: Commit red tests**

Run:

```bash
git add tests/test_layer_generate_cases.py
git commit -m "test(learning): cover layer generate case schema"
```

## Task 2: Case Builder And Boundary Validation

**Files:**
- Create: `src/vulca/layers/layer_generate_cases.py`
- Test: `tests/test_layer_generate_cases.py`

- [ ] **Step 1: Implement the schema builder**

Create `src/vulca/layers/layer_generate_cases.py` with this content:

```python
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
```

- [ ] **Step 2: Run schema tests to verify green**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_layer_generate_cases.py::test_build_layer_generate_case_minimal_schema tests/test_layer_generate_cases.py::test_layer_generate_case_rejects_redraw_route_geometry_refinement_fields tests/test_layer_generate_cases.py::test_layer_generate_case_requires_per_layer_asset_paths -q
```

Expected: PASS, `3 passed`.

- [ ] **Step 3: Commit builder implementation**

Run:

```bash
git add src/vulca/layers/layer_generate_cases.py tests/test_layer_generate_cases.py
git commit -m "feat(learning): add layer generate case records"
```

## Task 3: Taxonomy, Learning Targets, And JSONL Tests

**Files:**
- Modify: `tests/test_layer_generate_cases.py`
- Modify: `src/vulca/layers/layer_generate_cases.py`

- [ ] **Step 1: Append failing taxonomy and append tests**

Append this content to `tests/test_layer_generate_cases.py`:

```python
def test_layer_generate_case_taxonomy_rejects_unknown_labels():
    from vulca.layers.layer_generate_cases import (
        validate_failure_type,
        validate_preferred_action,
        validate_route_recommendation,
    )

    assert validate_failure_type("") == ""
    assert validate_failure_type("style_drift") == "style_drift"
    with pytest.raises(ValueError, match="unsupported layer_generate failure_type"):
        validate_failure_type("pasteback_mismatch")

    assert validate_preferred_action("") == ""
    assert validate_preferred_action("split_layer") == "split_layer"
    with pytest.raises(ValueError, match="unsupported layer_generate preferred_action"):
        validate_preferred_action("adjust_mask")

    assert validate_route_recommendation("") == ""
    assert validate_route_recommendation("direct_generation") == "direct_generation"
    with pytest.raises(
        ValueError,
        match="unsupported layer_generate route_recommendation",
    ):
        validate_route_recommendation("sparse_bbox_crop")


def test_layer_generate_case_learning_targets_round_trip():
    from vulca.layers.layer_generate_cases import build_layer_generate_case

    record = build_layer_generate_case(
        user_intent="Create layers.",
        tradition="test",
        style_constraints=_style_constraints(),
        layer_plan=_layer_plan(),
        prompt_stack=_prompt_stack(),
        provider="openai",
        model="gpt-image-2",
        layer_manifest_path="runs/layered/case/manifest.json",
        layers=_layers(),
        learning_targets={
            "tiny_model": {
                "failure_classification": "style_drift",
                "quality_score": 0.42,
                "route_recommendation": "adjust_prompt",
            },
            "tiny_agent": {
                "next_action_policy": "adjust_prompt",
            },
        },
        failure_type="style_drift",
        preferred_action="adjust_prompt",
        reviewer="human:reviewer-a",
        reviewed_at="2026-05-05T13:00:00Z",
        created_at="2026-05-05T12:00:00Z",
    )

    assert record["learning_targets"] == {
        "tiny_model": {
            "failure_classification": "style_drift",
            "quality_score": 0.42,
            "route_recommendation": "adjust_prompt",
        },
        "tiny_agent": {
            "next_action_policy": "adjust_prompt",
        },
    }
    assert record["review"] == {
        "human_accept": None,
        "failure_type": "style_drift",
        "preferred_action": "adjust_prompt",
        "reviewer": "human:reviewer-a",
        "reviewed_at": "2026-05-05T13:00:00Z",
    }


def test_layer_generate_case_id_is_stable_for_same_inputs():
    from vulca.layers.layer_generate_cases import build_layer_generate_case

    kwargs = {
        "user_intent": "Create layers.",
        "tradition": "test",
        "style_constraints": _style_constraints(),
        "layer_plan": _layer_plan(),
        "prompt_stack": _prompt_stack(),
        "provider": "openai",
        "model": "gpt-image-2",
        "layer_manifest_path": "runs/layered/case/manifest.json",
        "layers": _layers(),
        "created_at": "2026-05-05T12:00:00Z",
    }
    first = build_layer_generate_case(**kwargs)
    second = build_layer_generate_case(**kwargs)
    changed = build_layer_generate_case(**{**kwargs, "model": "other-model"})

    assert first["case_id"] == second["case_id"]
    assert first["case_id"] != changed["case_id"]


def test_append_layer_generate_case_writes_one_json_line(tmp_path):
    from vulca.layers.layer_generate_cases import append_layer_generate_case

    path = tmp_path / "cases" / "layer_generate_cases.jsonl"
    record = {
        "schema_version": 1,
        "case_type": "layer_generate_case",
        "case_id": "layer_generate_example",
    }

    written = append_layer_generate_case(str(path), record)

    assert written == str(path)
    lines = path.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == record
```

- [ ] **Step 2: Run tests to verify red**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_layer_generate_cases.py::test_layer_generate_case_taxonomy_rejects_unknown_labels tests/test_layer_generate_cases.py::test_layer_generate_case_learning_targets_round_trip tests/test_layer_generate_cases.py::test_layer_generate_case_id_is_stable_for_same_inputs tests/test_layer_generate_cases.py::test_append_layer_generate_case_writes_one_json_line -q
```

Expected: PASS, `4 passed`.

- [ ] **Step 3: Run full layer generate case tests**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_layer_generate_cases.py -q
```

Expected: PASS, `7 passed`.

- [ ] **Step 4: Commit taxonomy and append coverage**

Run:

```bash
git add src/vulca/layers/layer_generate_cases.py tests/test_layer_generate_cases.py
git commit -m "test(learning): cover layer generate case labels"
```

## Task 4: Public Boundary Documentation In Tests

**Files:**
- Modify: `tests/test_layer_generate_cases.py`

- [ ] **Step 1: Add explicit sibling boundary regression**

Append this content to `tests/test_layer_generate_cases.py`:

```python
def test_layer_generate_case_uses_sibling_schema_not_redraw_or_decompose():
    from vulca.layers.layer_generate_cases import build_layer_generate_case

    record = build_layer_generate_case(
        user_intent="Create layers.",
        tradition="test",
        style_constraints=_style_constraints(),
        layer_plan=_layer_plan(),
        prompt_stack=_prompt_stack(),
        provider="openai",
        model="gpt-image-2",
        layer_manifest_path="runs/layered/case/manifest.json",
        layers=_layers(),
        created_at="2026-05-05T12:00:00Z",
    )

    assert record["case_type"] == "layer_generate_case"
    assert "route" not in record
    assert "geometry" not in record
    assert "refinement" not in record
    assert "artifacts" not in record
    assert "inputs" in record
    assert "decisions" in record
    assert "outputs" in record
    assert record["outputs"]["layer_manifest_path"].endswith("manifest.json")
```

- [ ] **Step 2: Run boundary regression**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_layer_generate_cases.py::test_layer_generate_case_uses_sibling_schema_not_redraw_or_decompose -q
```

Expected: PASS.

- [ ] **Step 3: Commit boundary regression**

Run:

```bash
git add tests/test_layer_generate_cases.py
git commit -m "test(learning): lock layer generate case boundary"
```

## Task 5: Focused Verification

**Files:**
- Verify only.

- [ ] **Step 1: Run layer generate case tests**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_layer_generate_cases.py -q
```

Expected: PASS, `8 passed`.

- [ ] **Step 2: Run redraw case regression tests**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest tests/test_redraw_cases.py -q
```

Expected: PASS. These tests confirm the sibling `redraw_case` builder remains unchanged.

- [ ] **Step 3: Run diff checks**

Run:

```bash
git diff --check
grep -R "case_type.*redraw_case" -n src/vulca/layers/layer_generate_cases.py tests/test_layer_generate_cases.py
```

Expected: `git diff --check` exits 0. The grep command exits 1 because `layer_generate_cases.py` and its tests do not declare `redraw_case` records.

- [ ] **Step 4: Inspect staged scope before final commit**

Run:

```bash
git status --short
git diff --stat
```

Expected: changed files are limited to `src/vulca/layers/layer_generate_cases.py` and `tests/test_layer_generate_cases.py`, plus no runtime integration files.

- [ ] **Step 5: Final commit**

Run:

```bash
git add src/vulca/layers/layer_generate_cases.py tests/test_layer_generate_cases.py
git commit -m "feat(learning): implement layer generate case schema"
```

## Future Integration Notes

- CLI, MCP, and runtime generation integration stay out of this implementation.
- A separate integration plan can add opt-in JSONL logging from a layered generation exit point after the builder is stable.
- A separate `decompose_case` spec and plan can define extraction case records. Do not add decompose fields to `layer_generate_case`.
