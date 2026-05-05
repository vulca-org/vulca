# Vulca Learning Loop v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional `redraw_case` JSONL logging for `layers_redraw` so redraw experiments become training and evaluation data without changing default runtime behavior.

**Architecture:** Add a focused `vulca.layers.redraw_cases` module that builds versioned case records and appends JSONL. Integrate it only at CLI/MCP redraw exits, reading existing `LayerInfo`, `redraw_advisory`, output paths, and pasteback preview fields. Keep decomposition and layered generation out of this first implementation; they will get sibling case schemas in separate workstreams.

**Tech Stack:** Python 3.10+, dataclasses-free dictionary records, `json`, `hashlib`, `pathlib`, existing `LayerInfo` / `LayerResult`, pytest.

---

## File Structure

- Create `src/vulca/layers/redraw_cases.py`
  - Owns `redraw_case` schema construction, failure taxonomy validation, case id generation, environment/path resolution, and JSONL append.
  - Does not import providers, MCP, CLI, image libraries, or redraw execution code.

- Modify `src/vulca/mcp_server.py`
  - Adds optional `case_log_path` parameter to `layers_redraw`.
  - Builds and appends a case record after redraw, pasteback preview, and advisory fields are available.
  - Returns `case_id` and `case_log_path` only when logging succeeds; returns `case_log_error` when explicitly enabled logging fails.

- Modify `src/vulca/cli.py`
  - Adds `vulca layers redraw --case-log PATH`.
  - Appends a case record for single-layer redraw and prints the case id/path.
  - Leaves default CLI behavior unchanged when the flag/env var is absent.

- Create `tests/test_redraw_cases.py`
  - Tests schema construction, JSONL append, failure taxonomy validation, and environment path resolution.

- Modify `tests/test_mcp_layers_redraw_advisory.py`
  - Adds an MCP integration test for case logging.

- Modify `tests/test_cli_commands.py`
  - Adds a parser/help regression for `--case-log`.

- Create `docs/benchmarks/redraw/failure_taxonomy.json`
  - Machine-readable copy of the first redraw failure taxonomy.

- Create `docs/benchmarks/redraw/seed_manifest.json`
  - Small seed manifest of known redraw/decomposition/layered-generation-adjacent case families, explicitly marked as `redraw_case_seed` entries.

- Create `tests/test_redraw_benchmark_manifest.py`
  - Verifies taxonomy and seed manifest are valid JSON and reference existing local artifacts.

## Task 1: Redraw Case Unit Tests

**Files:**
- Create: `tests/test_redraw_cases.py`
- Implementation target: `src/vulca/layers/redraw_cases.py`

- [ ] **Step 1: Write the failing unit tests**

Create `tests/test_redraw_cases.py` with this content:

```python
import json

import pytest

from vulca.layers.types import LayerInfo


def test_build_redraw_case_minimal_schema(tmp_path):
    from vulca.layers.redraw_cases import build_redraw_case

    layer = LayerInfo(
        id="layer_fg_001",
        name="fg",
        description="foreground object",
        z_index=1,
        content_type="subject",
        semantic_path="subject.object",
        quality_status="detected",
        area_pct=1.25,
    )
    record = build_redraw_case(
        artwork_dir=str(tmp_path),
        source_image="source.png",
        layer_info=layer,
        instruction="make it cleaner",
        provider="openai",
        model="gpt-image-2",
        route_requested="auto",
        source_layer_path=str(tmp_path / "fg.png"),
        redrawn_layer_path=str(tmp_path / "fg_redrawn.png"),
        source_pasteback_path=str(tmp_path / "fg_redrawn_on_source.png"),
        redraw_advisory={
            "route_chosen": "inpaint",
            "redraw_route": "sparse_bbox_crop",
            "geometry_redraw_route": "sparse_bbox_crop",
            "area_pct": 0.64,
            "bbox_fill": 1.0,
            "component_count": 1,
            "sparse_detected": True,
            "quality_gate_passed": True,
            "quality_failures": [],
            "refinement_applied": False,
            "refinement_reason": "no_target_profile",
            "refinement_strategy": "none",
            "refined_child_count": 0,
            "mask_granularity_score": 0.0,
        },
        created_at="2026-05-05T12:00:00Z",
    )

    assert record["schema_version"] == 1
    assert record["case_type"] == "redraw_case"
    assert record["case_id"].startswith("redraw_20260505T120000Z_")
    assert record["artwork_dir"] == str(tmp_path)
    assert record["source_image"] == "source.png"
    assert record["layer"] == {
        "id": "layer_fg_001",
        "name": "fg",
        "description": "foreground object",
        "semantic_path": "subject.object",
        "quality_status": "detected",
        "area_pct_manifest": 1.25,
    }
    assert record["route"]["requested"] == "auto"
    assert record["route"]["chosen"] == "inpaint"
    assert record["geometry"]["component_count"] == 1
    assert record["quality"]["gate_passed"] is True
    assert record["review"] == {
        "human_accept": None,
        "failure_type": "",
        "preferred_action": "",
        "reviewer": "",
        "reviewed_at": "",
    }


def test_append_redraw_case_writes_one_json_line(tmp_path):
    from vulca.layers.redraw_cases import append_redraw_case

    path = tmp_path / "cases" / "redraw_cases.jsonl"
    record = {
        "schema_version": 1,
        "case_type": "redraw_case",
        "case_id": "redraw_example",
    }

    written = append_redraw_case(str(path), record)

    assert written == str(path)
    lines = path.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == record


def test_validate_failure_type_rejects_unknown_label():
    from vulca.layers.redraw_cases import validate_failure_type

    assert validate_failure_type("") == ""
    assert validate_failure_type("mask_too_broad") == "mask_too_broad"
    with pytest.raises(ValueError, match="unsupported redraw failure_type"):
        validate_failure_type("bad_label")


def test_resolve_case_log_path_supports_env_default(tmp_path, monkeypatch):
    from vulca.layers.redraw_cases import resolve_case_log_path

    assert resolve_case_log_path("", str(tmp_path)) == ""

    monkeypatch.setenv("VULCA_REDRAW_CASE_LOG", "1")
    assert resolve_case_log_path("", str(tmp_path)) == str(tmp_path / "redraw_cases.jsonl")

    explicit = tmp_path / "custom.jsonl"
    assert resolve_case_log_path(str(explicit), str(tmp_path)) == str(explicit)

    monkeypatch.setenv("VULCA_REDRAW_CASE_LOG", str(tmp_path / "env.jsonl"))
    assert resolve_case_log_path("", str(tmp_path)) == str(tmp_path / "env.jsonl")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_redraw_cases.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.layers.redraw_cases'`.

## Task 2: Redraw Case Module

**Files:**
- Create: `src/vulca/layers/redraw_cases.py`
- Test: `tests/test_redraw_cases.py`

- [ ] **Step 1: Implement the focused module**

Create `src/vulca/layers/redraw_cases.py` with this content:

```python
"""Versioned case records for redraw learning loops."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from vulca.layers.types import LayerInfo

CASE_SCHEMA_VERSION = 1
CASE_TYPE = "redraw_case"

FAILURE_TYPES: frozenset[str] = frozenset(
    {
        "color_drift",
        "shape_collapse",
        "wrong_subject",
        "missing_detail",
        "over_smoothing",
        "texture_leak",
        "alpha_expansion",
        "mask_too_broad",
        "background_bleed",
        "large_white_component",
        "pasteback_mismatch",
        "route_error",
        "over_split",
        "under_split",
        "uncertain",
    }
)

PREFERRED_ACTIONS: frozenset[str] = frozenset(
    {
        "",
        "accept",
        "rerun",
        "fallback_to_agent",
        "fallback_to_original",
        "manual_review",
        "adjust_route",
        "adjust_mask",
        "adjust_instruction",
    }
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_failure_type(value: str) -> str:
    if value == "":
        return ""
    if value not in FAILURE_TYPES:
        raise ValueError(
            f"unsupported redraw failure_type {value!r}; expected one of {sorted(FAILURE_TYPES)}"
        )
    return value


def validate_preferred_action(value: str) -> str:
    if value not in PREFERRED_ACTIONS:
        raise ValueError(
            f"unsupported redraw preferred_action {value!r}; expected one of {sorted(PREFERRED_ACTIONS)}"
        )
    return value


def resolve_case_log_path(case_log_path: str, artwork_dir: str) -> str:
    if case_log_path:
        return str(Path(case_log_path))
    env_value = os.environ.get("VULCA_REDRAW_CASE_LOG", "").strip()
    if not env_value:
        return ""
    if env_value.lower() in {"1", "true", "yes", "on"}:
        return str(Path(artwork_dir) / "redraw_cases.jsonl")
    return str(Path(env_value))


def build_redraw_case(
    *,
    artwork_dir: str,
    source_image: str,
    layer_info: LayerInfo,
    instruction: str,
    provider: str,
    model: str,
    route_requested: str,
    source_layer_path: str,
    redrawn_layer_path: str,
    source_pasteback_path: str = "",
    redraw_advisory: Mapping[str, Any] | None = None,
    debug_summary_path: str = "",
    created_at: str | None = None,
    human_accept: bool | None = None,
    failure_type: str = "",
    preferred_action: str = "",
    reviewer: str = "",
    reviewed_at: str = "",
) -> dict[str, Any]:
    advisory = dict(redraw_advisory or {})
    created = created_at or utc_now_iso()
    checked_failure_type = validate_failure_type(failure_type)
    checked_action = validate_preferred_action(preferred_action)
    case_id = _make_case_id(
        created_at=created,
        source_layer_path=source_layer_path,
        redrawn_layer_path=redrawn_layer_path,
        instruction=instruction,
        provider=provider,
        model=model,
    )

    return {
        "schema_version": CASE_SCHEMA_VERSION,
        "case_type": CASE_TYPE,
        "case_id": case_id,
        "created_at": created,
        "artwork_dir": str(artwork_dir),
        "source_image": str(source_image or ""),
        "layer": {
            "id": str(layer_info.id),
            "name": str(layer_info.name),
            "description": str(layer_info.description),
            "semantic_path": str(layer_info.semantic_path or ""),
            "quality_status": str(layer_info.quality_status or ""),
            "area_pct_manifest": float(layer_info.area_pct or 0.0),
        },
        "instruction": str(instruction),
        "provider": str(provider),
        "model": str(model or advisory.get("model", "")),
        "route": {
            "requested": str(route_requested or advisory.get("route_requested", "")),
            "chosen": str(advisory.get("route_chosen", "")),
            "redraw_route": str(advisory.get("redraw_route", "")),
            "geometry_redraw_route": str(advisory.get("geometry_redraw_route", "")),
        },
        "geometry": {
            "area_pct": float(advisory.get("area_pct", 0.0) or 0.0),
            "bbox_fill": float(advisory.get("bbox_fill", 0.0) or 0.0),
            "component_count": int(advisory.get("component_count", 0) or 0),
            "sparse_detected": bool(advisory.get("sparse_detected", False)),
        },
        "quality": {
            "gate_passed": _optional_bool(advisory.get("quality_gate_passed")),
            "failures": [str(item) for item in advisory.get("quality_failures", [])],
            "metrics": dict(advisory.get("quality_metrics", {}) or {}),
        },
        "refinement": {
            "applied": bool(advisory.get("refinement_applied", False)),
            "reason": str(advisory.get("refinement_reason", "")),
            "strategy": str(advisory.get("refinement_strategy", "")),
            "child_count": int(advisory.get("refined_child_count", 0) or 0),
            "mask_granularity_score": float(
                advisory.get("mask_granularity_score", 0.0) or 0.0
            ),
        },
        "artifacts": {
            "source_layer_path": str(source_layer_path or ""),
            "redrawn_layer_path": str(redrawn_layer_path or ""),
            "source_pasteback_path": str(source_pasteback_path or ""),
            "debug_summary_path": str(debug_summary_path or ""),
        },
        "review": {
            "human_accept": human_accept,
            "failure_type": checked_failure_type,
            "preferred_action": checked_action,
            "reviewer": str(reviewer or ""),
            "reviewed_at": str(reviewed_at or ""),
        },
    }


def append_redraw_case(case_log_path: str, record: Mapping[str, Any]) -> str:
    if not case_log_path:
        raise ValueError("case_log_path is required when appending a redraw case")
    path = Path(case_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
        fh.write("\n")
    return str(path)


def _optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _make_case_id(
    *,
    created_at: str,
    source_layer_path: str,
    redrawn_layer_path: str,
    instruction: str,
    provider: str,
    model: str,
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
            source_layer_path,
            redrawn_layer_path,
            instruction,
            provider,
            model,
        ]
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"redraw_{stamp}_{digest}"
```

- [ ] **Step 2: Run the unit tests**

Run:

```bash
pytest tests/test_redraw_cases.py -v
```

Expected: PASS, 4 tests passed.

- [ ] **Step 3: Commit the module and unit tests**

Run:

```bash
git add src/vulca/layers/redraw_cases.py tests/test_redraw_cases.py
git commit -m "feat(redraw): add redraw case records"
```

## Task 3: MCP Redraw Case Logging

**Files:**
- Modify: `tests/test_mcp_layers_redraw_advisory.py`
- Modify: `src/vulca/mcp_server.py`

- [ ] **Step 1: Add the failing MCP integration test**

Append this test to `tests/test_mcp_layers_redraw_advisory.py`:

```python
def test_layers_redraw_appends_case_log_when_enabled(tmp_path, monkeypatch):
    _install_fastmcp_stub(monkeypatch)

    from vulca.mcp_server import layers_redraw
    import vulca.providers as providers_mod

    provider = RecordingEditProvider()
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    _stage_artwork(tmp_path)
    case_log = tmp_path / "redraw_cases.jsonl"

    result = _run(
        layers_redraw(
            artwork_dir=str(tmp_path),
            layer="fg",
            instruction="make it cleaner",
            provider="openai",
            route="auto",
            preserve_alpha=True,
            case_log_path=str(case_log),
        )
    )

    assert result["case_log_path"] == str(case_log)
    assert result["case_id"].startswith("redraw_")
    lines = case_log.read_text().splitlines()
    assert len(lines) == 1

    import json

    record = json.loads(lines[0])
    assert record["case_id"] == result["case_id"]
    assert record["layer"]["name"] == "fg"
    assert record["instruction"] == "make it cleaner"
    assert record["provider"] == "openai"
    assert record["model"] == ""
    assert record["route"]["chosen"] == "inpaint"
    assert record["artifacts"]["source_pasteback_path"].endswith("_on_source.png")
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
pytest tests/test_mcp_layers_redraw_advisory.py::test_layers_redraw_appends_case_log_when_enabled -v
```

Expected: FAIL with `TypeError` because `layers_redraw()` does not accept `case_log_path`.

- [ ] **Step 3: Modify the MCP tool signature and docstring**

In `src/vulca/mcp_server.py`, update the `layers_redraw` signature around the current `output_format` parameter:

```python
    output_format: str = "",
    case_log_path: str = "",
) -> dict:
```

In the same docstring, add this argument description after the `route` description:

```python
        case_log_path: Optional JSONL path for Learning Loop v0 redraw case
            logging. Empty means disabled unless VULCA_REDRAW_CASE_LOG is set.
            Logging is best-effort and never invalidates the redraw result.
```

- [ ] **Step 4: Add MCP logging after payload/advisory construction**

In `src/vulca/mcp_server.py`, replace the final lines:

```python
    payload.update(getattr(result, "redraw_advisory", {}) or {})
    return payload
```

with:

```python
    payload.update(getattr(result, "redraw_advisory", {}) or {})

    from vulca.layers.redraw_cases import (
        append_redraw_case,
        build_redraw_case,
        resolve_case_log_path,
    )

    resolved_case_log_path = resolve_case_log_path(case_log_path, artwork_dir)
    if resolved_case_log_path:
        if merge or not layer:
            payload["case_log_error"] = (
                "redraw case logging supports only single-layer redraw in v0"
            )
        else:
            try:
                source_layer = next(
                    (lr for lr in artwork.layers if lr.info.name == layer),
                    None,
                )
                if source_layer is None:
                    raise ValueError(f"layer {layer!r} not found in artwork")
                record = build_redraw_case(
                    artwork_dir=artwork_dir,
                    source_image=artwork.source_image,
                    layer_info=source_layer.info,
                    instruction=instruction,
                    provider=provider,
                    model=model,
                    route_requested=route,
                    source_layer_path=source_layer.image_path,
                    redrawn_layer_path=result.image_path,
                    source_pasteback_path=payload.get("source_pasteback_path", ""),
                    redraw_advisory=payload,
                )
                payload["case_log_path"] = append_redraw_case(
                    resolved_case_log_path,
                    record,
                )
                payload["case_id"] = record["case_id"]
            except Exception as exc:
                payload["case_log_error"] = str(exc)
    return payload
```

- [ ] **Step 5: Run MCP advisory tests**

Run:

```bash
pytest tests/test_mcp_layers_redraw_advisory.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit MCP integration**

Run:

```bash
git add src/vulca/mcp_server.py tests/test_mcp_layers_redraw_advisory.py
git commit -m "feat(mcp): log redraw cases"
```

## Task 4: CLI Case Logging Flag

**Files:**
- Modify: `tests/test_cli_commands.py`
- Modify: `src/vulca/cli.py`

- [ ] **Step 1: Add the failing CLI help test**

Append this method inside `TestCLICommands` in `tests/test_cli_commands.py`:

```python
    def test_layers_redraw_help_mentions_case_log(self):
        result = subprocess.run(
            VULCA + ["layers", "redraw", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "--case-log" in result.stdout
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
pytest tests/test_cli_commands.py::TestCLICommands::test_layers_redraw_help_mentions_case_log -v
```

Expected: FAIL because `--case-log` is not present in help output.

- [ ] **Step 3: Add the CLI parser flag**

In `src/vulca/cli.py`, after the existing `layers_redraw.add_argument("--re-split", ...)` block, add:

```python
    layers_redraw.add_argument(
        "--case-log",
        default="",
        help=(
            "Append a Learning Loop v0 redraw case JSONL record to this path. "
            "If omitted, VULCA_REDRAW_CASE_LOG can enable logging."
        ),
    )
```

- [ ] **Step 4: Add CLI logging for single-layer redraw**

In `src/vulca/cli.py`, replace the single-layer redraw branch:

```python
            result = loop.run_until_complete(
                redraw_layer(artwork, layer_name=args.layer,
                             instruction=args.instruction, provider=args.provider,
                             tradition=args.tradition, artwork_dir=args.artwork_dir)
            )
            print(f"  Redrawn: {result.info.name} -> {result.image_path}")
```

with:

```python
            source_layer = next(
                (lr for lr in artwork.layers if lr.info.name == args.layer),
                None,
            )
            result = loop.run_until_complete(
                redraw_layer(artwork, layer_name=args.layer,
                             instruction=args.instruction, provider=args.provider,
                             tradition=args.tradition, artwork_dir=args.artwork_dir)
            )
            print(f"  Redrawn: {result.info.name} -> {result.image_path}")
            from vulca.layers.redraw_cases import (
                append_redraw_case,
                build_redraw_case,
                resolve_case_log_path,
            )
            resolved_case_log_path = resolve_case_log_path(
                getattr(args, "case_log", ""),
                args.artwork_dir,
            )
            if resolved_case_log_path:
                try:
                    if source_layer is None:
                        raise ValueError(f"layer {args.layer!r} not found in artwork")
                    advisory = getattr(result, "redraw_advisory", {}) or {}
                    record = build_redraw_case(
                        artwork_dir=args.artwork_dir,
                        source_image=artwork.source_image,
                        layer_info=source_layer.info,
                        instruction=args.instruction,
                        provider=args.provider,
                        model="",
                        route_requested=str(advisory.get("route_requested", "")),
                        source_layer_path=source_layer.image_path,
                        redrawn_layer_path=result.image_path,
                        redraw_advisory=advisory,
                    )
                    written_case_log_path = append_redraw_case(
                        resolved_case_log_path,
                        record,
                    )
                    print(f"  Case log: {record['case_id']} -> {written_case_log_path}")
                except Exception as exc:
                    print(f"  Case log error: {exc}", file=sys.stderr)
```

- [ ] **Step 5: Run CLI tests**

Run:

```bash
pytest tests/test_cli_commands.py::TestCLICommands::test_layers_redraw_help_mentions_case_log -v
```

Expected: PASS.

- [ ] **Step 6: Commit CLI integration**

Run:

```bash
git add src/vulca/cli.py tests/test_cli_commands.py
git commit -m "feat(cli): expose redraw case logging"
```

## Task 5: Benchmark Taxonomy And Seed Manifest

**Files:**
- Create: `docs/benchmarks/redraw/failure_taxonomy.json`
- Create: `docs/benchmarks/redraw/seed_manifest.json`
- Create: `tests/test_redraw_benchmark_manifest.py`

- [ ] **Step 1: Write failing benchmark manifest tests**

Create `tests/test_redraw_benchmark_manifest.py` with this content:

```python
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_redraw_failure_taxonomy_matches_seed_manifest():
    taxonomy_path = ROOT / "docs" / "benchmarks" / "redraw" / "failure_taxonomy.json"
    manifest_path = ROOT / "docs" / "benchmarks" / "redraw" / "seed_manifest.json"

    taxonomy = json.loads(taxonomy_path.read_text())
    manifest = json.loads(manifest_path.read_text())

    allowed = set(taxonomy["failure_types"])
    assert "mask_too_broad" in allowed
    assert manifest["case_type"] == "redraw_case_seed"
    assert manifest["schema_version"] == 1
    assert manifest["items"]
    for item in manifest["items"]:
        assert item["failure_type"] in allowed
        artifact = ROOT / item["source_artifact"]
        assert artifact.exists(), item["source_artifact"]
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
pytest tests/test_redraw_benchmark_manifest.py -v
```

Expected: FAIL because the JSON files do not exist.

- [ ] **Step 3: Add the failure taxonomy JSON**

Create `docs/benchmarks/redraw/failure_taxonomy.json` with this content:

```json
{
  "schema_version": 1,
  "case_type": "redraw_failure_taxonomy",
  "failure_types": [
    "color_drift",
    "shape_collapse",
    "wrong_subject",
    "missing_detail",
    "over_smoothing",
    "texture_leak",
    "alpha_expansion",
    "mask_too_broad",
    "background_bleed",
    "large_white_component",
    "pasteback_mismatch",
    "route_error",
    "over_split",
    "under_split",
    "uncertain"
  ],
  "preferred_actions": [
    "accept",
    "rerun",
    "fallback_to_agent",
    "fallback_to_original",
    "manual_review",
    "adjust_route",
    "adjust_mask",
    "adjust_instruction"
  ]
}
```

- [ ] **Step 4: Add the seed manifest JSON**

Create `docs/benchmarks/redraw/seed_manifest.json` with this content:

```json
{
  "schema_version": 1,
  "case_type": "redraw_case_seed",
  "items": [
    {
      "id": "ipad_flower_color_drift",
      "source_artifact": "docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/source/IMG_6847.jpg",
      "failure_type": "color_drift",
      "preferred_action": "adjust_mask",
      "notes": "Small bright flowers can drift in hue or subject identity without target-aware mask evidence."
    },
    {
      "id": "ipad_full_edit_mask_route",
      "source_artifact": "docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/source/full_edit_mask_1536x1024.png",
      "failure_type": "route_error",
      "preferred_action": "adjust_route",
      "notes": "Full-canvas edit masks are route evidence, not final product quality evidence."
    },
    {
      "id": "scottish_lantern_multi_instance",
      "source_artifact": "docs/visual-specs/2026-04-23-scottish-chinese-fusion/source.jpg",
      "failure_type": "mask_too_broad",
      "preferred_action": "adjust_mask",
      "notes": "Multi-instance lantern rows should remain separate enough for targeted redraw."
    },
    {
      "id": "mona_lisa_under_split",
      "source_artifact": "assets/demo/v2/masters/mona_lisa.jpg",
      "failure_type": "under_split",
      "preferred_action": "fallback_to_agent",
      "notes": "Missed chair/parapet style evidence should route to agent review instead of blind redraw."
    },
    {
      "id": "starry_night_over_split",
      "source_artifact": "assets/demo/v2/masters/starry_night.jpg",
      "failure_type": "over_split",
      "preferred_action": "fallback_to_original",
      "notes": "Low residual baselines should not be over-split or over-edited."
    },
    {
      "id": "scenario1_pasteback_contract",
      "source_artifact": "assets/demo/v2/scenario1-redo/original.png",
      "failure_type": "pasteback_mismatch",
      "preferred_action": "manual_review",
      "notes": "Pasteback preview is product evidence separate from isolated layer quality."
    }
  ]
}
```

- [ ] **Step 5: Run benchmark tests**

Run:

```bash
pytest tests/test_redraw_benchmark_manifest.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit benchmark docs**

Run:

```bash
git add docs/benchmarks/redraw/failure_taxonomy.json docs/benchmarks/redraw/seed_manifest.json tests/test_redraw_benchmark_manifest.py
git commit -m "docs(redraw): seed learning benchmark"
```

## Task 6: Focused Regression Sweep

**Files:**
- Uses files modified in Tasks 1-5.

- [ ] **Step 1: Run the new focused test suite**

Run:

```bash
pytest tests/test_redraw_cases.py tests/test_mcp_layers_redraw_advisory.py tests/test_cli_commands.py::TestCLICommands::test_layers_redraw_help_mentions_case_log tests/test_redraw_benchmark_manifest.py -v
```

Expected: PASS.

- [ ] **Step 2: Run existing redraw regression tests touched by the integration**

Run:

```bash
pytest tests/test_layers_redraw_strategy.py tests/test_layers_redraw_quality_gates.py tests/test_redraw_review_contract.py tests/test_mcp_layers_redraw_advisory.py -v
```

Expected: PASS.

- [ ] **Step 3: Check repository status**

Run:

```bash
git status --short
```

Expected: only unrelated pre-existing untracked dogfood/demo files remain. No modified tracked files should remain after the task commits.

- [ ] **Step 4: Final implementation note**

Record in the final handoff that Learning Loop v0 implemented only `redraw_case`. Decomposition case records and layered-generation case records remain distinct sibling schemas and should not be shoehorned into `redraw_case`.

## Self-Review

Spec coverage:
- Versioned `redraw_case` schema: Task 1 and Task 2.
- Optional case logging from `layers_redraw`: Task 3 and Task 4.
- CLI/MCP visibility: Task 3 and Task 4.
- Failure taxonomy and benchmark seed manifest: Task 5.
- No model training or heavy dependencies: all tasks use only standard library plus existing Vulca types.
- Decomposition vs layered generation distinction: File Structure and Task 6 final note keep sibling schemas separate.

Placeholder scan:
- The plan contains no forbidden planning markers, no unspecified test commands, and no unspecified files.

Type consistency:
- `case_log_path`, `case_id`, `case_log_error`, `redraw_advisory`, and `source_pasteback_path` names match the implementation snippets and tests.
