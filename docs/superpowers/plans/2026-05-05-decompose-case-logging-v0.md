# Decompose Case Logging v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional `decompose_case` JSONL logging for `layers_split` so existing-image semantic split runs become Learning Loop evidence without changing default split behavior.

**Architecture:** Add a focused `vulca.layers.decompose_cases` module that builds versioned whole-split case records and appends JSONL. Integrate it only at CLI/MCP `layers split` exits, reading existing manifest, layer assets, detection report, target hints, residual/composite paths, and debug artifacts. Keep this schema separate from `redraw_case` and future `layer_generate_case`.

**Tech Stack:** Python 3.10+, dictionary records, `json`, `hashlib`, `pathlib`, existing `LayerInfo` / manifest JSON, pytest.

---

## File Structure

- Create `src/vulca/layers/decompose_cases.py`
  - Owns `decompose_case` schema construction, decompose-specific failure/action taxonomy validation, case id generation, target-hint normalization, debug-artifact discovery, environment/path resolution, and JSONL append.
  - Does not import providers, MCP, CLI, image libraries, redraw code, or layered generation code.

- Modify `src/vulca/mcp_server.py`
  - Adds optional `case_log_path` parameter to `layers_split`.
  - For `mode="orchestrated"`, appends a whole-run case after the pipeline result and manifest are available.
  - For existing non-orchestrated modes, appends a whole-run case after `split_extract`, `split_vlm`, `sam3_split`, or `split_regenerate` writes the manifest.
  - Returns `case_id` and `case_log_path` only when logging succeeds; returns `case_log_error` when explicitly enabled logging fails.

- Modify `src/vulca/cli.py`
  - Adds `vulca layers split --case-log PATH`.
  - Appends a decompose case for CLI split modes and prints the case id/path.
  - Leaves default CLI behavior unchanged when the flag/env var is absent.

- Create `tests/test_decompose_cases.py`
  - Tests schema construction, JSONL append, decompose taxonomy validation, environment path resolution, and hint normalization.

- Create `tests/test_mcp_layers_decompose_case.py`
  - Tests MCP `layers_split(mode="orchestrated")` appends one `decompose_case` JSONL record using a stubbed pipeline result.

- Modify `tests/test_cli_commands.py`
  - Adds a parser/help regression for `layers split --case-log`.

## Task 1: Decompose Case Unit Tests

**Files:**
- Create: `tests/test_decompose_cases.py`
- Implementation target: `src/vulca/layers/decompose_cases.py`

- [ ] **Step 1: Write the failing unit tests**

Create `tests/test_decompose_cases.py` with this content:

```python
import json

import pytest

from vulca.layers.types import LayerInfo


def test_build_decompose_case_minimal_schema(tmp_path):
    from vulca.layers.decompose_cases import build_decompose_case

    manifest_path = tmp_path / "manifest.json"
    manifest_data = {
        "version": 5,
        "split_mode": "claude_orchestrated",
        "status": "partial",
        "layers": [
            {
                "id": "layer_sky",
                "name": "sky",
                "semantic_path": "background.sky",
                "file": "sky.png",
                "z_index": 10,
                "quality_status": "detected",
                "area_pct": 70.0,
                "bbox": [0, 0, 100, 70],
                "parent_layer_id": None,
            },
            {
                "id": "layer_residual",
                "name": "residual",
                "semantic_path": "residual",
                "file": "residual.png",
                "z_index": 1,
                "quality_status": "residual",
                "area_pct": 30.0,
                "bbox": [0, 0, 100, 100],
                "parent_layer_id": None,
            },
        ],
        "detection_report": {
            "requested": 2,
            "detected": 1,
            "suspect": 0,
            "missed": 1,
            "success_rate": 0.5,
        },
    }
    manifest_path.write_text(json.dumps(manifest_data))

    record = build_decompose_case(
        source_image="source.jpg",
        mode="orchestrated",
        provider="",
        model="",
        tradition="post_impressionist_painting",
        output_dir=str(tmp_path),
        manifest_path=str(manifest_path),
        target_layer_hints=[
            {
                "name": "sky",
                "label": "swirling sky",
                "semantic_path": "background.sky",
                "detector": "sam_bbox",
                "bbox_hint_pct": [0.0, 0.0, 1.0, 0.7],
                "multi_instance": False,
                "threshold": None,
                "order": None,
            }
        ],
        debug_artifacts={"qa_contact_sheet_path": str(tmp_path / "qa.jpg")},
        created_at="2026-05-05T12:00:00Z",
    )

    assert record["schema_version"] == 1
    assert record["case_type"] == "decompose_case"
    assert record["case_id"].startswith("decompose_20260505T120000Z_")
    assert record["input"]["source_image"] == "source.jpg"
    assert record["input"]["requested"] == {
        "mode": "orchestrated",
        "provider": "",
        "model": "",
        "tradition": "post_impressionist_painting",
    }
    assert record["input"]["target_layer_hints"][0]["semantic_path"] == "background.sky"
    assert record["output"]["manifest_path"] == str(manifest_path)
    assert record["output"]["output_dir"] == str(tmp_path)
    assert record["output"]["manifest_version"] == 5
    assert record["output"]["split_mode"] == "claude_orchestrated"
    assert record["output"]["status"] == "partial"
    assert record["output"]["layers"][0] == {
        "id": "layer_sky",
        "name": "sky",
        "semantic_path": "background.sky",
        "file": str(tmp_path / "sky.png"),
        "z_index": 10,
        "quality_status": "detected",
        "area_pct": 70.0,
        "bbox": [0, 0, 100, 70],
        "parent_layer_id": None,
    }
    assert record["output"]["residual_path"] == str(tmp_path / "residual.png")
    assert record["output"]["composite_path"] == ""
    assert record["output"]["detection_report"]["missed"] == 1
    assert record["output"]["debug_artifacts"]["qa_contact_sheet_path"] == str(tmp_path / "qa.jpg")
    assert record["quality"]["quality_score"] is None
    assert record["quality"]["layer_coverage"] == {
        "claimed_pct": 70.0,
        "residual_pct": 30.0,
        "missed_hint_count": 1,
        "suspect_hint_count": 0,
    }
    assert record["quality"]["alpha_quality"]["empty_layer_count"] == 0
    assert record["quality"]["residual_leakage"]["residual_pct"] == 30.0
    assert record["review"] == {
        "human_accept": None,
        "failure_type": "",
        "preferred_action": "",
        "reviewer": "",
        "reviewed_at": "",
        "notes": "",
    }


def test_append_decompose_case_writes_one_json_line(tmp_path):
    from vulca.layers.decompose_cases import append_decompose_case

    path = tmp_path / "cases" / "decompose_cases.jsonl"
    record = {
        "schema_version": 1,
        "case_type": "decompose_case",
        "case_id": "decompose_example",
    }

    written = append_decompose_case(str(path), record)

    assert written == str(path)
    lines = path.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == record


def test_validate_decompose_labels_reject_unknown_values():
    from vulca.layers.decompose_cases import (
        validate_failure_type,
        validate_preferred_action,
    )

    assert validate_failure_type("") == ""
    assert validate_failure_type("under_split") == "under_split"
    assert validate_preferred_action("") == ""
    assert validate_preferred_action("adjust_hints") == "adjust_hints"

    with pytest.raises(ValueError, match="unsupported decompose failure_type"):
        validate_failure_type("color_drift")
    with pytest.raises(ValueError, match="unsupported decompose preferred_action"):
        validate_preferred_action("adjust_mask")


def test_resolve_case_log_path_supports_env_default(tmp_path, monkeypatch):
    from vulca.layers.decompose_cases import resolve_case_log_path

    assert resolve_case_log_path("", str(tmp_path)) == ""

    monkeypatch.setenv("VULCA_DECOMPOSE_CASE_LOG", "1")
    assert resolve_case_log_path("", str(tmp_path)) == str(tmp_path / "decompose_cases.jsonl")

    explicit = tmp_path / "custom.jsonl"
    assert resolve_case_log_path(str(explicit), str(tmp_path)) == str(explicit)

    monkeypatch.setenv("VULCA_DECOMPOSE_CASE_LOG", str(tmp_path / "env.jsonl"))
    assert resolve_case_log_path("", str(tmp_path)) == str(tmp_path / "env.jsonl")


def test_target_hints_from_plan_and_layer_infos():
    from vulca.layers.decompose_cases import (
        target_hints_from_layer_infos,
        target_hints_from_plan,
    )

    plan = {
        "entities": [
            {
                "name": "person",
                "label": "main person",
                "semantic_path": "subject.person[0]",
                "detector": "yolo",
                "bbox_hint_pct": None,
                "multi_instance": True,
                "threshold": 0.25,
                "order": 1,
            }
        ]
    }
    assert target_hints_from_plan(plan) == [
        {
            "name": "person",
            "label": "main person",
            "semantic_path": "subject.person[0]",
            "detector": "yolo",
            "bbox_hint_pct": None,
            "multi_instance": True,
            "threshold": 0.25,
            "order": 1,
        }
    ]

    infos = [
        LayerInfo(
            name="sky",
            description="blue sky",
            z_index=0,
            content_type="background",
            semantic_path="background.sky",
        )
    ]
    assert target_hints_from_layer_infos(infos) == [
        {
            "name": "sky",
            "label": "blue sky",
            "semantic_path": "background.sky",
            "detector": "",
            "bbox_hint_pct": None,
            "multi_instance": False,
            "threshold": None,
            "order": None,
        }
    ]
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_decompose_cases.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.layers.decompose_cases'`.

## Task 2: Decompose Case Module

**Files:**
- Create: `src/vulca/layers/decompose_cases.py`
- Test: `tests/test_decompose_cases.py`

- [ ] **Step 1: Implement the focused module**

Create `src/vulca/layers/decompose_cases.py` with this content:

```python
"""Versioned case records for decompose learning loops."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

CASE_SCHEMA_VERSION = 1
CASE_TYPE = "decompose_case"

FAILURE_TYPES: frozenset[str] = frozenset(
    {
        "over_split",
        "under_split",
        "semantic_mismatch",
        "alpha_bad",
        "residual_leakage",
        "missed_concept",
        "wrong_instance",
        "empty_layer",
        "duplicate_layer",
        "debug_artifact_missing",
        "route_error",
        "uncertain",
    }
)

PREFERRED_ACTIONS: frozenset[str] = frozenset(
    {
        "",
        "rerun_split",
        "adjust_hints",
        "merge_layers",
        "split_layer_further",
        "fallback_to_manual",
        "fallback_to_agent",
        "accept",
    }
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_failure_type(value: str) -> str:
    if value == "":
        return ""
    if value not in FAILURE_TYPES:
        raise ValueError(
            f"unsupported decompose failure_type {value!r}; expected one of {sorted(FAILURE_TYPES)}"
        )
    return value


def validate_preferred_action(value: str) -> str:
    if value not in PREFERRED_ACTIONS:
        raise ValueError(
            f"unsupported decompose preferred_action {value!r}; expected one of {sorted(PREFERRED_ACTIONS)}"
        )
    return value


def resolve_case_log_path(case_log_path: str, output_dir: str) -> str:
    if case_log_path:
        return str(Path(case_log_path))
    env_value = os.environ.get("VULCA_DECOMPOSE_CASE_LOG", "").strip()
    if not env_value:
        return ""
    if env_value.lower() in {"1", "true", "yes", "on"}:
        return str(Path(output_dir) / "decompose_cases.jsonl")
    return str(Path(env_value))


def target_hints_from_plan(plan: Any) -> list[dict[str, Any]]:
    if hasattr(plan, "model_dump"):
        data = plan.model_dump(mode="json")
    elif isinstance(plan, Mapping):
        data = dict(plan)
    else:
        data = json.loads(str(plan))

    hints: list[dict[str, Any]] = []
    for entity in data.get("entities", []) or []:
        hints.append(
            {
                "name": str(entity.get("name", "")),
                "label": str(entity.get("label", "")),
                "semantic_path": str(entity.get("semantic_path", "") or ""),
                "detector": str(entity.get("detector", "") or ""),
                "bbox_hint_pct": entity.get("bbox_hint_pct"),
                "multi_instance": bool(entity.get("multi_instance", False)),
                "threshold": entity.get("threshold"),
                "order": entity.get("order"),
            }
        )
    return hints


def target_hints_from_layer_infos(layers: Sequence[Any]) -> list[dict[str, Any]]:
    hints: list[dict[str, Any]] = []
    for item in layers:
        info = getattr(item, "info", item)
        hints.append(
            {
                "name": str(getattr(info, "name", "")),
                "label": str(getattr(info, "description", "") or getattr(info, "name", "")),
                "semantic_path": str(getattr(info, "semantic_path", "") or ""),
                "detector": "",
                "bbox_hint_pct": None,
                "multi_instance": False,
                "threshold": None,
                "order": None,
            }
        )
    return hints


def debug_artifacts_from_output_dir(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    qa_contact_sheet = out / "qa_contact_sheet.jpg"
    qa_prompt = out / "qa_prompt.md"
    log_path = out / "decompose.log"
    mask_overlay_paths = sorted(str(p) for p in out.glob("*mask_overlay*.png"))
    return {
        "qa_contact_sheet_path": str(qa_contact_sheet) if qa_contact_sheet.exists() else "",
        "qa_prompt_path": str(qa_prompt) if qa_prompt.exists() else "",
        "mask_overlay_paths": mask_overlay_paths,
        "log_path": str(log_path) if log_path.exists() else "",
    }


def build_decompose_case(
    *,
    source_image: str,
    mode: str,
    provider: str,
    model: str,
    tradition: str,
    output_dir: str,
    manifest_path: str,
    target_layer_hints: Sequence[Mapping[str, Any]] = (),
    manifest_data: Mapping[str, Any] | None = None,
    debug_artifacts: Mapping[str, Any] | None = None,
    created_at: str | None = None,
    human_accept: bool | None = None,
    failure_type: str = "",
    preferred_action: str = "",
    reviewer: str = "",
    reviewed_at: str = "",
    notes: str = "",
) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path, manifest_data)
    created = created_at or utc_now_iso()
    checked_failure_type = validate_failure_type(failure_type)
    checked_action = validate_preferred_action(preferred_action)
    normalized_hints = [dict(hint) for hint in target_layer_hints]
    layers = [_layer_record(output_dir, item) for item in manifest.get("layers", []) or []]
    detection_report = dict(manifest.get("detection_report", {}) or {})
    residual_path, residual_pct = _residual_from_layers(layers)
    composite_path = _artifact_path(output_dir, str(manifest.get("composite", "") or ""))
    quality = _quality_record(layers, detection_report, residual_pct)

    case_id = _make_case_id(
        created_at=created,
        source_image=source_image,
        mode=mode,
        provider=provider,
        model=model,
        tradition=tradition,
        output_dir=output_dir,
        manifest_path=manifest_path,
        target_layer_hints=normalized_hints,
    )

    return {
        "schema_version": CASE_SCHEMA_VERSION,
        "case_type": CASE_TYPE,
        "case_id": case_id,
        "created_at": created,
        "input": {
            "source_image": str(source_image or ""),
            "requested": {
                "mode": str(mode or ""),
                "provider": str(provider or ""),
                "model": str(model or ""),
                "tradition": str(tradition or ""),
            },
            "target_layer_hints": normalized_hints,
        },
        "output": {
            "output_dir": str(output_dir or ""),
            "manifest_path": str(manifest_path or ""),
            "manifest_version": int(manifest.get("manifest_version", manifest.get("version", 0)) or 0),
            "split_mode": str(manifest.get("split_mode", mode or "")),
            "status": str(manifest.get("status", "")),
            "layers": layers,
            "residual_path": residual_path,
            "composite_path": composite_path,
            "detection_report": detection_report,
            "debug_artifacts": _debug_artifacts_record(debug_artifacts),
        },
        "quality": quality,
        "review": {
            "human_accept": human_accept,
            "failure_type": checked_failure_type,
            "preferred_action": checked_action,
            "reviewer": str(reviewer or ""),
            "reviewed_at": str(reviewed_at or ""),
            "notes": str(notes or ""),
        },
    }


def append_decompose_case(case_log_path: str, record: Mapping[str, Any]) -> str:
    if not case_log_path:
        raise ValueError("case_log_path is required when appending a decompose case")
    path = Path(case_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
        fh.write("\n")
    return str(path)


def _load_manifest(
    manifest_path: str,
    manifest_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if manifest_data is not None:
        return dict(manifest_data)
    if not manifest_path:
        return {}
    path = Path(manifest_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _layer_record(output_dir: str, item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": str(item.get("id", "")),
        "name": str(item.get("name", "")),
        "semantic_path": str(item.get("semantic_path", "") or ""),
        "file": _artifact_path(output_dir, str(item.get("file", "") or "")),
        "z_index": int(item.get("z_index", 0) or 0),
        "quality_status": str(item.get("quality_status", "") or ""),
        "area_pct": float(item.get("area_pct", 0.0) or 0.0),
        "bbox": item.get("bbox"),
        "parent_layer_id": item.get("parent_layer_id"),
    }


def _artifact_path(output_dir: str, value: str) -> str:
    if not value:
        return ""
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str(Path(output_dir) / path)


def _is_residual_layer(layer: Mapping[str, Any]) -> bool:
    return (
        layer.get("name") == "residual"
        or layer.get("semantic_path") == "residual"
        or layer.get("quality_status") == "residual"
    )


def _residual_from_layers(layers: Sequence[Mapping[str, Any]]) -> tuple[str, float]:
    for layer in layers:
        if _is_residual_layer(layer):
            return str(layer.get("file", "") or ""), float(layer.get("area_pct", 0.0) or 0.0)
    return "", 0.0


def _quality_record(
    layers: Sequence[Mapping[str, Any]],
    detection_report: Mapping[str, Any],
    residual_pct: float,
) -> dict[str, Any]:
    non_residual = [layer for layer in layers if not _is_residual_layer(layer)]
    claimed_pct = round(sum(float(layer.get("area_pct", 0.0) or 0.0) for layer in non_residual), 4)
    empty_layer_count = sum(
        1 for layer in non_residual if float(layer.get("area_pct", 0.0) or 0.0) <= 0.0
    )
    missed = _report_count(detection_report, "missed")
    suspect = _report_count(detection_report, "suspect")
    return {
        "quality_score": None,
        "layer_coverage": {
            "claimed_pct": claimed_pct,
            "residual_pct": float(residual_pct),
            "missed_hint_count": missed,
            "suspect_hint_count": suspect,
        },
        "alpha_quality": {
            "mean_edge_softness": None,
            "hard_edge_ratio": None,
            "empty_layer_count": empty_layer_count,
            "opaque_noise_ratio": None,
        },
        "over_split": {"score": None, "evidence": []},
        "under_split": {"score": None, "evidence": []},
        "semantic_mismatch": {"score": None, "evidence": []},
        "residual_leakage": {
            "score": None,
            "residual_pct": float(residual_pct),
            "evidence": [],
        },
    }


def _report_count(detection_report: Mapping[str, Any], key: str) -> int:
    value = detection_report.get(key)
    if isinstance(value, int):
        return value
    per_entity = detection_report.get("per_entity", []) or []
    return sum(1 for item in per_entity if isinstance(item, Mapping) and item.get("status") == key)


def _debug_artifacts_record(debug_artifacts: Mapping[str, Any] | None) -> dict[str, Any]:
    raw = dict(debug_artifacts or {})
    return {
        "qa_contact_sheet_path": str(raw.get("qa_contact_sheet_path", "") or ""),
        "qa_prompt_path": str(raw.get("qa_prompt_path", "") or ""),
        "mask_overlay_paths": [str(item) for item in raw.get("mask_overlay_paths", []) or []],
        "log_path": str(raw.get("log_path", "") or ""),
    }


def _make_case_id(
    *,
    created_at: str,
    source_image: str,
    mode: str,
    provider: str,
    model: str,
    tradition: str,
    output_dir: str,
    manifest_path: str,
    target_layer_hints: Sequence[Mapping[str, Any]],
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
            source_image,
            mode,
            provider,
            model,
            tradition,
            output_dir,
            manifest_path,
            json.dumps(list(target_layer_hints), sort_keys=True, separators=(",", ":")),
        ]
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"decompose_{stamp}_{digest}"
```

- [ ] **Step 2: Run unit tests**

Run:

```bash
pytest tests/test_decompose_cases.py -v
```

Expected: PASS, 5 tests.

- [ ] **Step 3: Commit the module and unit tests**

Run:

```bash
git add src/vulca/layers/decompose_cases.py tests/test_decompose_cases.py
git commit -m "feat(decompose): add learning case records"
```

## Task 3: MCP `layers_split` Case Logging

**Files:**
- Modify: `src/vulca/mcp_server.py`
- Create: `tests/test_mcp_layers_decompose_case.py`
- Test: `tests/test_mcp_layers_decompose_case.py`

- [ ] **Step 1: Write the failing MCP test**

Create `tests/test_mcp_layers_decompose_case.py` with this content:

```python
import asyncio
import json
import sys
import types
from pathlib import Path


def _run(coro):
    return asyncio.run(coro)


class _FastMCPStub:
    def __init__(self, *args, **kwargs):
        pass

    def tool(self, *args, **kwargs):
        def decorator(fn):
            return fn

        return decorator

    def run(self):
        pass


def _install_fastmcp_stub(monkeypatch):
    module = types.ModuleType("fastmcp")
    module.FastMCP = _FastMCPStub
    monkeypatch.setitem(sys.modules, "fastmcp", module)


class _FakePipelineResult:
    def __init__(self, output_dir: Path, manifest_path: Path):
        self.status = "partial"
        self.manifest_path = manifest_path
        self.output_dir = output_dir
        self.reason = None
        self.detection_report = {
            "requested": 1,
            "detected": 0,
            "suspect": 0,
            "missed": 1,
            "success_rate": 0.0,
        }
        self.stage_timings = [{"stage": "total", "seconds": 0.01}]
        self.layers = [
            {
                "id": "layer_residual",
                "name": "residual",
                "semantic_path": "residual",
                "file": "residual.png",
                "z_index": 1,
                "content_type": "residual",
                "blend_mode": "normal",
                "quality_status": "residual",
                "area_pct": 100.0,
                "bbox": [0, 0, 20, 20],
                "parent_layer_id": None,
            }
        ]


def test_layers_split_orchestrated_appends_decompose_case(tmp_path, monkeypatch):
    _install_fastmcp_stub(monkeypatch)

    import vulca.pipeline.segment as segment_mod
    from vulca.mcp_server import layers_split

    source = tmp_path / "source.png"
    source.write_bytes(b"not-read-by-stub")
    out_dir = tmp_path / "layers"
    case_log = tmp_path / "decompose_cases.jsonl"
    plan = {
        "slug": "case-test",
        "domain": "news_photograph",
        "entities": [
            {
                "name": "subject",
                "label": "main subject",
                "semantic_path": "subject.main",
                "detector": "sam_bbox",
                "bbox_hint_pct": [0.1, 0.1, 0.9, 0.9],
            }
        ],
    }

    def _fake_run(plan_obj, image_path, output_dir, force=True):  # noqa: ARG001
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "residual.png").write_bytes(b"fake")
        (output_dir / "qa_prompt.md").write_text("review prompt")
        manifest_path = output_dir / "manifest.json"
        manifest = {
            "version": 5,
            "split_mode": "claude_orchestrated",
            "status": "partial",
            "layers": [
                {
                    "id": "layer_residual",
                    "name": "residual",
                    "semantic_path": "residual",
                    "file": "residual.png",
                    "z_index": 1,
                    "quality_status": "residual",
                    "area_pct": 100.0,
                    "bbox": [0, 0, 20, 20],
                    "parent_layer_id": None,
                }
            ],
            "detection_report": {
                "requested": 1,
                "detected": 0,
                "suspect": 0,
                "missed": 1,
                "success_rate": 0.0,
            },
        }
        manifest_path.write_text(json.dumps(manifest))
        return _FakePipelineResult(output_dir, manifest_path)

    monkeypatch.setattr(segment_mod, "run", _fake_run)

    result = _run(
        layers_split(
            image_path=str(source),
            output_dir=str(out_dir),
            mode="orchestrated",
            plan=json.dumps(plan),
            case_log_path=str(case_log),
        )
    )

    assert result["case_log_path"] == str(case_log)
    assert result["case_id"].startswith("decompose_")
    assert result["split_mode"] == "orchestrated"
    lines = case_log.read_text().splitlines()
    assert len(lines) == 1

    record = json.loads(lines[0])
    assert record["case_id"] == result["case_id"]
    assert record["case_type"] == "decompose_case"
    assert record["input"]["source_image"] == str(source.resolve())
    assert record["input"]["requested"]["mode"] == "orchestrated"
    assert record["input"]["requested"]["tradition"] == "news_photograph"
    assert record["input"]["target_layer_hints"][0]["semantic_path"] == "subject.main"
    assert record["output"]["manifest_path"] == str(out_dir / "manifest.json")
    assert record["output"]["residual_path"] == str(out_dir / "residual.png")
    assert record["output"]["debug_artifacts"]["qa_prompt_path"] == str(out_dir / "qa_prompt.md")
    assert record["quality"]["layer_coverage"]["residual_pct"] == 100.0
    assert record["review"]["preferred_action"] == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_mcp_layers_decompose_case.py -v
```

Expected: FAIL with `TypeError` mentioning unexpected keyword argument `case_log_path`.

- [ ] **Step 3: Add the MCP parameter**

In `src/vulca/mcp_server.py`, change the `layers_split` signature from:

```python
async def layers_split(
    image_path: str,
    output_dir: str = "",
    mode: str = "regenerate",
    provider: str = "gemini",
    tradition: str = "default",
    plan_path: str = "",
    plan: str = "",
) -> dict:
```

to:

```python
async def layers_split(
    image_path: str,
    output_dir: str = "",
    mode: str = "regenerate",
    provider: str = "gemini",
    tradition: str = "default",
    plan_path: str = "",
    plan: str = "",
    case_log_path: str = "",
) -> dict:
```

In the docstring Args block, add:

```python
        case_log_path: Optional JSONL path for Learning Loop decompose_case logging.
                       If omitted, VULCA_DECOMPOSE_CASE_LOG can enable logging.
```

- [ ] **Step 4: Replace the orchestrated return literal with a payload plus logging**

In `src/vulca/mcp_server.py`, replace the `return { ... }` block inside the `mode == "orchestrated"` branch with:

```python
        payload = {
            "split_mode": "orchestrated",
            "status": result.status,
            "manifest_path": str(result.manifest_path),
            "output_dir": str(result.output_dir),
            "reason": result.reason,
            "detection_report": result.detection_report,
            "stage_timings": result.stage_timings,
            "layers": [
                {"name": l["name"], "file": str(result.output_dir / l["file"]),
                 "z_index": l["z_index"],
                 "content_type": l.get("content_type", l["name"]),
                 "semantic_path": l.get("semantic_path", ""),
                 "blend_mode": l.get("blend_mode", "normal")}
                for l in result.layers
            ],
        }

        from vulca.layers.decompose_cases import (
            append_decompose_case,
            build_decompose_case,
            debug_artifacts_from_output_dir,
            resolve_case_log_path,
            target_hints_from_plan,
        )

        resolved_case_log_path = resolve_case_log_path(
            case_log_path,
            str(result.output_dir),
        )
        if resolved_case_log_path:
            try:
                record = build_decompose_case(
                    source_image=str(img_p),
                    mode="orchestrated",
                    provider=provider,
                    model="",
                    tradition=getattr(plan_obj, "domain", "") or tradition,
                    output_dir=str(result.output_dir),
                    manifest_path=str(result.manifest_path),
                    target_layer_hints=target_hints_from_plan(plan_obj),
                    debug_artifacts=debug_artifacts_from_output_dir(result.output_dir),
                )
                payload["case_log_path"] = append_decompose_case(
                    resolved_case_log_path,
                    record,
                )
                payload["case_id"] = record["case_id"]
            except Exception as exc:
                payload["case_log_error"] = str(exc)

        return payload
```

- [ ] **Step 5: Add logging to the non-orchestrated MCP branch**

At the end of the non-orchestrated branch, replace the final `return { ... }` with:

```python
    payload = {
        "split_mode": mode,
        "manifest_path": str(Path(out) / "manifest.json"),
        "layers": [
            {
                "name": r.info.name,
                "file": r.image_path,
                "z_index": r.info.z_index,
                "content_type": r.info.content_type,
                "blend_mode": r.info.blend_mode,
            }
            for r in results
        ],
    }

    from vulca.layers.decompose_cases import (
        append_decompose_case,
        build_decompose_case,
        debug_artifacts_from_output_dir,
        resolve_case_log_path,
        target_hints_from_layer_infos,
    )

    resolved_case_log_path = resolve_case_log_path(case_log_path, out)
    if resolved_case_log_path:
        try:
            record = build_decompose_case(
                source_image=image_path,
                mode=mode,
                provider=provider,
                model="",
                tradition=tradition,
                output_dir=out,
                manifest_path=payload["manifest_path"],
                target_layer_hints=target_hints_from_layer_infos([r.info for r in results]),
                debug_artifacts=debug_artifacts_from_output_dir(out),
            )
            payload["case_log_path"] = append_decompose_case(
                resolved_case_log_path,
                record,
            )
            payload["case_id"] = record["case_id"]
        except Exception as exc:
            payload["case_log_error"] = str(exc)

    return payload
```

- [ ] **Step 6: Run MCP tests**

Run:

```bash
pytest tests/test_mcp_layers_decompose_case.py tests/test_decompose_cases.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit MCP integration**

Run:

```bash
git add src/vulca/mcp_server.py tests/test_mcp_layers_decompose_case.py
git commit -m "feat(mcp): log decompose cases from layers split"
```

## Task 4: CLI `layers split --case-log`

**Files:**
- Modify: `src/vulca/cli.py`
- Modify: `tests/test_cli_commands.py`
- Test: `tests/test_cli_commands.py::TestCLICommands::test_layers_split_help_mentions_case_log`

- [ ] **Step 1: Write the failing CLI help test**

Append this method to `class TestCLICommands` in `tests/test_cli_commands.py`:

```python
    def test_layers_split_help_mentions_case_log(self):
        result = run_vulca(["layers", "split", "--help"])
        assert result.returncode == 0
        assert "--case-log" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_cli_commands.py::TestCLICommands::test_layers_split_help_mentions_case_log -v
```

Expected: FAIL because `--case-log` is absent from help output.

- [ ] **Step 3: Add the CLI argument**

In `src/vulca/cli.py`, after the existing `layers_split.add_argument("--tradition", "-t", ...)` line, insert:

```python
    layers_split.add_argument(
        "--case-log",
        default="",
        help=(
            "Append a Learning Loop decompose_case JSONL record to this path. "
            "If omitted, VULCA_DECOMPOSE_CASE_LOG can enable logging."
        ),
    )
```

- [ ] **Step 4: Add CLI logging after split output**

In the `elif args.layers_command == "split":` branch, after:

```python
        print(f"    manifest.json -> {Path(out_dir) / 'manifest.json'}")
```

insert:

```python
        from vulca.layers.decompose_cases import (
            append_decompose_case,
            build_decompose_case,
            debug_artifacts_from_output_dir,
            resolve_case_log_path,
            target_hints_from_layer_infos,
        )

        resolved_case_log_path = resolve_case_log_path(
            getattr(args, "case_log", ""),
            out_dir,
        )
        if resolved_case_log_path:
            try:
                manifest_path = str(Path(out_dir) / "manifest.json")
                record = build_decompose_case(
                    source_image=args.image,
                    mode=args.mode,
                    provider=args.provider,
                    model="",
                    tradition=args.tradition,
                    output_dir=out_dir,
                    manifest_path=manifest_path,
                    target_layer_hints=target_hints_from_layer_infos(layers),
                    debug_artifacts=debug_artifacts_from_output_dir(out_dir),
                )
                written_case_log_path = append_decompose_case(
                    resolved_case_log_path,
                    record,
                )
                print(f"    Case log: {record['case_id']} -> {written_case_log_path}")
            except Exception as exc:
                print(f"    Case log error: {exc}")
```

- [ ] **Step 5: Run CLI help test**

Run:

```bash
pytest tests/test_cli_commands.py::TestCLICommands::test_layers_split_help_mentions_case_log -v
```

Expected: PASS.

- [ ] **Step 6: Commit CLI integration**

Run:

```bash
git add src/vulca/cli.py tests/test_cli_commands.py
git commit -m "feat(cli): expose decompose case logging"
```

## Task 5: Final Verification

**Files:**
- Verify all files changed by Tasks 1-4.

- [ ] **Step 1: Run the focused verification suite**

Run:

```bash
pytest tests/test_decompose_cases.py tests/test_mcp_layers_decompose_case.py tests/test_cli_commands.py::TestCLICommands::test_layers_split_help_mentions_case_log -v
```

Expected: PASS.

- [ ] **Step 2: Inspect the final diff against the pre-implementation base**

Run:

```bash
git show --stat --oneline HEAD~3..HEAD
```

Expected: three implementation commits touching only:

```text
src/vulca/layers/decompose_cases.py
src/vulca/mcp_server.py
src/vulca/cli.py
tests/test_decompose_cases.py
tests/test_mcp_layers_decompose_case.py
tests/test_cli_commands.py
```

- [ ] **Step 3: Record implementation boundary in final handoff**

In the final response, state:

```text
Implemented only decompose_case case construction and optional logging. Runtime split/decompose behavior remains unchanged by default. redraw_case and layer_generate_case remain separate schemas.
```

## Self-Review Checklist

- Spec coverage:
  - `case_type: decompose_case`: Task 2.
  - Input `source_image`, requested mode/provider/model/tradition, target hints: Task 2.
  - Output manifest, layer assets, residual/composite, detection report, debug artifacts: Task 2.
  - Quality metrics layer coverage, alpha quality, over/under split, semantic mismatch, residual leakage: Task 2.
  - Review labels human_accept, failure_type, preferred_action: Task 2.
  - Tiny model/agent learning labels: represented by `quality_score`, `failure_type`, and `preferred_action` in Task 2.
  - Boundary from redraw/layered generation: enforced by separate module and tests in Tasks 2-3.

- Placeholder scan:
  - No implementation step uses open-ended labels.
  - Each test and code step includes concrete code.
  - Each verification step names a command and expected result.

- Type consistency:
  - Module exports use `append_decompose_case`, `build_decompose_case`, `resolve_case_log_path`, `target_hints_from_plan`, and `target_hints_from_layer_infos`.
  - MCP and CLI snippets import the same exported names.
  - Case logging return fields are consistently `case_id`, `case_log_path`, and `case_log_error`.
