# Redraw Showcase Webapp Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make redraw result review consume `source_pasteback_path` as the primary after-image while preserving `file` as the editable layer asset.

**Architecture:** Add a small pure-Python review contract helper that classifies redraw payloads into stable webapp states. Keep MCP payload generation unchanged except for missing error-path coverage. Add a standalone static HTML renderer for redraw showcase summaries so the repo can dogfood the same contract even without a JS webapp in this tree.

**Tech Stack:** Python 3.14, pytest, existing Vulca MCP payloads, standard-library HTML/JSON/path utilities, static HTML.

---

## File Structure

- Create `src/vulca/layers/redraw_review.py`
  - Owns the product-level review-state contract for redraw payloads.
  - Has no PIL/provider/MCP dependency.
  - Accepts `Mapping[str, Any]` so MCP payloads, summary JSON rows, and external webapps can use the same field names.
- Create `tests/test_redraw_review_contract.py`
  - Unit tests for every review state in the product contract.
- Modify `tests/test_mcp_layers_redraw_advisory.py`
  - Add coverage for non-fatal `source_pasteback_error`.
- Create `scripts/build_redraw_review.py`
  - Reads a redraw showcase `summary.json`.
  - Normalizes it into the same payload shape consumed by `redraw_review.py`.
  - Writes a standalone before/after review HTML.
- Create `tests/test_redraw_showcase_review.py`
  - Tests summary normalization and generated HTML.
- Modify `docs/superpowers/specs/2026-04-30-redraw-showcase-product-contract-design.md`
  - Add implementation references after helpers exist.

## Task 1: Add Redraw Review State Helper

**Files:**
- Create: `src/vulca/layers/redraw_review.py`
- Test: `tests/test_redraw_review_contract.py`

- [ ] **Step 1: Write failing tests for all contract states**

Create `tests/test_redraw_review_contract.py`:

```python
from vulca.layers.redraw_review import classify_redraw_review


def test_ready_for_review_uses_source_pasteback_as_primary_after():
    review = classify_redraw_review(
        {
            "file": "/tmp/layer.png",
            "source_pasteback_path": "/tmp/layer_on_source.png",
            "quality_gate_passed": True,
        }
    )

    assert review.state == "ready_for_review"
    assert review.primary_after_path == "/tmp/layer_on_source.png"
    assert review.layer_asset_path == "/tmp/layer.png"
    assert review.show_as_final is True
    assert review.quality_gate_passed is True
    assert review.warnings == ()


def test_technical_preview_keeps_pasteback_but_marks_quality_failure():
    review = classify_redraw_review(
        {
            "file": "/tmp/layer.png",
            "source_pasteback_path": "/tmp/layer_on_source.png",
            "quality_gate_passed": False,
            "quality_failures": ["background_bleed"],
        }
    )

    assert review.state == "technical_preview"
    assert review.primary_after_path == "/tmp/layer_on_source.png"
    assert review.show_as_final is True
    assert review.quality_gate_passed is False
    assert review.warnings == ("quality_gate_failed: background_bleed",)


def test_unknown_quality_preview_tolerates_missing_advisory():
    review = classify_redraw_review(
        {
            "file": "/tmp/layer.png",
            "source_pasteback_path": "/tmp/layer_on_source.png",
        }
    )

    assert review.state == "unknown_quality_preview"
    assert review.primary_after_path == "/tmp/layer_on_source.png"
    assert review.show_as_final is True
    assert review.quality_gate_passed is None
    assert review.warnings == ("quality_gate_missing",)


def test_layer_only_result_does_not_promote_sparse_asset_as_final():
    review = classify_redraw_review({"file": "/tmp/layer.png"})

    assert review.state == "layer_only_result"
    assert review.primary_after_path == "/tmp/layer.png"
    assert review.layer_asset_path == "/tmp/layer.png"
    assert review.show_as_final is False
    assert review.warnings == ("source_pasteback_path_missing",)


def test_pasteback_warning_preserves_layer_asset_for_inspector():
    review = classify_redraw_review(
        {
            "file": "/tmp/layer.png",
            "source_pasteback_error": "source size (10, 10) != layer size (20, 20)",
        }
    )

    assert review.state == "pasteback_warning"
    assert review.primary_after_path == "/tmp/layer.png"
    assert review.layer_asset_path == "/tmp/layer.png"
    assert review.show_as_final is False
    assert review.warnings == (
        "source_pasteback_error: source size (10, 10) != layer size (20, 20)",
    )


def test_to_dict_matches_external_webapp_payload_shape():
    review = classify_redraw_review(
        {
            "file": "/tmp/layer.png",
            "source_pasteback_path": "/tmp/layer_on_source.png",
            "quality_gate_passed": True,
            "refinement_applied": True,
            "refined_child_count": 4,
        }
    )

    assert review.to_dict() == {
        "state": "ready_for_review",
        "primary_after_path": "/tmp/layer_on_source.png",
        "layer_asset_path": "/tmp/layer.png",
        "source_pasteback_path": "/tmp/layer_on_source.png",
        "source_pasteback_error": "",
        "show_as_final": True,
        "quality_gate_passed": True,
        "warnings": [],
        "refinement_applied": True,
        "refined_child_count": 4,
    }
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest tests/test_redraw_review_contract.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.layers.redraw_review'`.

- [ ] **Step 3: Implement the minimal helper**

Create `src/vulca/layers/redraw_review.py`:

```python
"""Product-level review contract for redraw results."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping

ReviewState = Literal[
    "ready_for_review",
    "technical_preview",
    "unknown_quality_preview",
    "layer_only_result",
    "pasteback_warning",
]


@dataclass(frozen=True)
class RedrawReview:
    state: ReviewState
    primary_after_path: str
    layer_asset_path: str
    source_pasteback_path: str
    source_pasteback_error: str
    show_as_final: bool
    quality_gate_passed: bool | None
    warnings: tuple[str, ...]
    refinement_applied: bool | None = None
    refined_child_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "state": self.state,
            "primary_after_path": self.primary_after_path,
            "layer_asset_path": self.layer_asset_path,
            "source_pasteback_path": self.source_pasteback_path,
            "source_pasteback_error": self.source_pasteback_error,
            "show_as_final": self.show_as_final,
            "quality_gate_passed": self.quality_gate_passed,
            "warnings": list(self.warnings),
        }
        if self.refinement_applied is not None:
            payload["refinement_applied"] = self.refinement_applied
        if self.refined_child_count is not None:
            payload["refined_child_count"] = self.refined_child_count
        return payload


def _quality_failures(payload: Mapping[str, Any]) -> tuple[str, ...]:
    raw = payload.get("quality_failures") or ()
    if isinstance(raw, str):
        return (raw,)
    return tuple(str(item) for item in raw)


def _optional_bool(payload: Mapping[str, Any], key: str) -> bool | None:
    if key not in payload:
        return None
    value = payload.get(key)
    return value if isinstance(value, bool) else None


def _optional_int(payload: Mapping[str, Any], key: str) -> int | None:
    value = payload.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def classify_redraw_review(payload: Mapping[str, Any]) -> RedrawReview:
    layer_asset = str(payload.get("file") or "")
    source_pasteback = str(payload.get("source_pasteback_path") or "")
    source_error = str(payload.get("source_pasteback_error") or "")
    quality = _optional_bool(payload, "quality_gate_passed")
    refinement_applied = _optional_bool(payload, "refinement_applied")
    refined_child_count = _optional_int(payload, "refined_child_count")

    if source_error and not source_pasteback:
        return RedrawReview(
            state="pasteback_warning",
            primary_after_path=layer_asset,
            layer_asset_path=layer_asset,
            source_pasteback_path="",
            source_pasteback_error=source_error,
            show_as_final=False,
            quality_gate_passed=quality,
            warnings=(f"source_pasteback_error: {source_error}",),
            refinement_applied=refinement_applied,
            refined_child_count=refined_child_count,
        )

    if source_pasteback:
        if quality is True:
            state: ReviewState = "ready_for_review"
            warnings: tuple[str, ...] = ()
        elif quality is False:
            state = "technical_preview"
            failures = ", ".join(_quality_failures(payload)) or "unknown"
            warnings = (f"quality_gate_failed: {failures}",)
        else:
            state = "unknown_quality_preview"
            warnings = ("quality_gate_missing",)
        return RedrawReview(
            state=state,
            primary_after_path=source_pasteback,
            layer_asset_path=layer_asset,
            source_pasteback_path=source_pasteback,
            source_pasteback_error="",
            show_as_final=True,
            quality_gate_passed=quality,
            warnings=warnings,
            refinement_applied=refinement_applied,
            refined_child_count=refined_child_count,
        )

    return RedrawReview(
        state="layer_only_result",
        primary_after_path=layer_asset,
        layer_asset_path=layer_asset,
        source_pasteback_path="",
        source_pasteback_error="",
        show_as_final=False,
        quality_gate_passed=quality,
        warnings=("source_pasteback_path_missing",),
        refinement_applied=refinement_applied,
        refined_child_count=refined_child_count,
    )
```

- [ ] **Step 4: Run the tests and verify GREEN**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest tests/test_redraw_review_contract.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/redraw_review.py tests/test_redraw_review_contract.py
git commit -m "feat: add redraw review contract helper"
```

## Task 2: Cover MCP Pasteback Warning Path

**Files:**
- Modify: `tests/test_mcp_layers_redraw_advisory.py`

- [ ] **Step 1: Write failing test for pasteback error fallback**

Append to `tests/test_mcp_layers_redraw_advisory.py`:

```python
def _stage_mismatched_source_artwork(tmp_path):
    size = (1000, 1000)
    alpha = Image.new("L", size, 0)
    alpha.paste(Image.new("L", (80, 80), 255), (440, 440))
    rgb = Image.new("RGB", size, (120, 80, 60))
    Image.merge("RGBA", (*rgb.split(), alpha)).save(tmp_path / "fg.png")
    Image.new("RGB", (900, 900), (100, 100, 100)).save(tmp_path / "source.png")
    write_manifest(
        [
            LayerInfo(
                name="fg",
                description="foreground object",
                z_index=1,
                content_type="subject",
            )
        ],
        output_dir=str(tmp_path),
        width=size[0],
        height=size[1],
        source_image="source.png",
    )


def test_layers_redraw_returns_nonfatal_source_pasteback_error(tmp_path, monkeypatch):
    _install_fastmcp_stub(monkeypatch)

    from vulca.mcp_server import layers_redraw
    import vulca.providers as providers_mod

    provider = RecordingEditProvider()
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    _stage_mismatched_source_artwork(tmp_path)

    result = _run(
        layers_redraw(
            artwork_dir=str(tmp_path),
            layer="fg",
            instruction="make it cleaner",
            provider="openai",
            route="auto",
            preserve_alpha=True,
        )
    )

    assert result["file"].endswith("fg_redrawn.png")
    assert "source_pasteback_path" not in result
    assert "source size (900, 900) != layer size (1000, 1000)" in result[
        "source_pasteback_error"
    ]
```

- [ ] **Step 2: Run the test and verify RED or GREEN**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest tests/test_mcp_layers_redraw_advisory.py::test_layers_redraw_returns_nonfatal_source_pasteback_error -q
```

Expected: PASS with the current implementation. If it fails, fix only `_source_pasteback_preview` error propagation in `src/vulca/mcp_server.py`.

- [ ] **Step 3: Run full MCP redraw advisory tests**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest tests/test_mcp_layers_redraw_advisory.py -q
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add tests/test_mcp_layers_redraw_advisory.py src/vulca/mcp_server.py
git commit -m "test: cover redraw source pasteback warnings"
```

## Task 3: Add Static Redraw Review Renderer

**Files:**
- Create: `scripts/build_redraw_review.py`
- Test: `tests/test_redraw_showcase_review.py`

- [ ] **Step 1: Write failing tests for summary normalization and HTML output**

Create `tests/test_redraw_showcase_review.py`:

```python
import json
from pathlib import Path

from scripts.build_redraw_review import build_html, payload_from_summary, write_review_html


def _path(tmp_path: Path, name: str) -> str:
    p = tmp_path / name
    p.write_text("fake image bytes")
    return str(p)


def test_payload_from_summary_prefers_final_source_pasteback(tmp_path):
    summary = {
        "layer_path": _path(tmp_path, "layer.png"),
        "final_source_pasteback_path": _path(tmp_path, "final_on_source.png"),
        "quality_gate_passed": True,
        "refinement": {"applied": True, "child_count_prepared": 4},
    }

    payload = payload_from_summary(summary)

    assert payload["file"].endswith("layer.png")
    assert payload["source_pasteback_path"].endswith("final_on_source.png")
    assert payload["quality_gate_passed"] is True
    assert payload["refinement_applied"] is True
    assert payload["refined_child_count"] == 4


def test_payload_from_summary_uses_last_succeeded_child_when_no_final(tmp_path):
    summary = {
        "layer_path": _path(tmp_path, "layer.png"),
        "children": [
            {
                "index": 1,
                "status": "succeeded",
                "source_pasteback_path": _path(tmp_path, "child_01_on_source.png"),
            },
            {
                "index": 2,
                "status": "succeeded",
                "source_pasteback_path": _path(tmp_path, "child_02_on_source.png"),
            },
            {
                "index": 3,
                "status": "prepared_waiting_for_api_key",
                "source_pasteback_path": _path(tmp_path, "child_03_on_source.png"),
            },
        ],
    }

    payload = payload_from_summary(summary)

    assert payload["source_pasteback_path"].endswith("child_02_on_source.png")
    assert "quality_gate_passed" not in payload


def test_build_html_shows_source_pasteback_as_after_image(tmp_path):
    summary = {
        "status": "completed",
        "prompt": "Make the flower cluster a storybook botanical accent.",
        "source_path": _path(tmp_path, "source.png"),
        "layer_path": _path(tmp_path, "layer.png"),
        "final_source_pasteback_path": _path(tmp_path, "final_on_source.png"),
        "quality_gate_passed": True,
        "children": [
            {
                "index": 1,
                "status": "succeeded",
                "input_path": _path(tmp_path, "child_01_input.png"),
                "mask_path": _path(tmp_path, "child_01_mask.png"),
                "source_pasteback_path": _path(tmp_path, "child_01_on_source.png"),
                "cost_usd": 0.061,
            }
        ],
    }
    output_path = tmp_path / "review.html"

    html = build_html(summary, output_path)

    assert "Ready for review" in html
    assert "final_on_source.png" in html
    assert "layer.png" in html
    assert "Make the flower cluster" in html
    assert "child_01_on_source.png" in html


def test_write_review_html_creates_file(tmp_path):
    summary_path = tmp_path / "summary.json"
    output_path = tmp_path / "review.html"
    summary_path.write_text(
        json.dumps(
            {
                "source_path": _path(tmp_path, "source.png"),
                "layer_path": _path(tmp_path, "layer.png"),
                "source_pasteback_path": _path(tmp_path, "after.png"),
                "quality_gate_passed": True,
                "children": [],
            }
        )
    )

    result = write_review_html(summary_path, output_path)

    assert result == output_path
    assert output_path.exists()
    assert "after.png" in output_path.read_text()
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest tests/test_redraw_showcase_review.py -q
```

Expected: FAIL with `ModuleNotFoundError` or missing `scripts.build_redraw_review`.

- [ ] **Step 3: Implement renderer**

Create `scripts/build_redraw_review.py`:

```python
#!/usr/bin/env python3
"""Build a static before/after review page for redraw showcase summaries."""
from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
from typing import Any

from vulca.layers.redraw_review import classify_redraw_review


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def rel(path: str, output_path: Path) -> str:
    if not path:
        return ""
    return os.path.relpath(path, output_path.parent)


def _last_succeeded_child_after(summary: dict[str, Any]) -> str:
    selected = ""
    for child in summary.get("children", []):
        if child.get("status") == "succeeded" and child.get("source_pasteback_path"):
            selected = str(child["source_pasteback_path"])
    return selected


def payload_from_summary(summary: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "file": str(summary.get("layer_path") or summary.get("file") or ""),
    }
    source_after = (
        summary.get("final_source_pasteback_path")
        or summary.get("source_pasteback_path")
        or _last_succeeded_child_after(summary)
    )
    if source_after:
        payload["source_pasteback_path"] = str(source_after)
    if "source_pasteback_error" in summary:
        payload["source_pasteback_error"] = str(summary["source_pasteback_error"])
    if isinstance(summary.get("quality_gate_passed"), bool):
        payload["quality_gate_passed"] = summary["quality_gate_passed"]
    if isinstance(summary.get("quality_failures"), list):
        payload["quality_failures"] = summary["quality_failures"]

    refinement = summary.get("refinement") or {}
    if isinstance(refinement.get("applied"), bool):
        payload["refinement_applied"] = refinement["applied"]
    prepared = refinement.get("child_count_prepared")
    if isinstance(prepared, int):
        payload["refined_child_count"] = prepared
    return payload


def _state_label(state: str) -> str:
    return {
        "ready_for_review": "Ready for review",
        "technical_preview": "Technical preview",
        "unknown_quality_preview": "Unknown quality preview",
        "layer_only_result": "Layer-only result",
        "pasteback_warning": "Pasteback warning",
    }.get(state, state)


def _child_cards(summary: dict[str, Any], output_path: Path) -> str:
    cards = []
    for child in summary.get("children", []):
        index = child.get("index", "?")
        status = child.get("status", "unknown")
        cost = child.get("cost_usd")
        cost_text = f"${cost:.3f}" if isinstance(cost, int | float) else ""
        cards.append(
            f"""
            <article class="child-card" data-status="{esc(status)}">
              <h3>Child {esc(index)} <span>{esc(status)}</span></h3>
              <div class="mini-grid">
                <figure><img src="{esc(rel(str(child.get('input_path') or ''), output_path))}" alt="child input"><figcaption>input</figcaption></figure>
                <figure><img src="{esc(rel(str(child.get('mask_path') or ''), output_path))}" alt="child mask"><figcaption>mask</figcaption></figure>
                <figure><img src="{esc(rel(str(child.get('source_pasteback_path') or ''), output_path))}" alt="child source pasteback"><figcaption>on source</figcaption></figure>
              </div>
              <p class="meta">{esc(cost_text)}</p>
            </article>
            """
        )
    return "\n".join(cards)


def build_html(summary: dict[str, Any], output_path: Path) -> str:
    review = classify_redraw_review(payload_from_summary(summary))
    source_path = str(summary.get("source_path") or "")
    after_path = review.primary_after_path
    layer_path = review.layer_asset_path
    prompt = str(summary.get("prompt") or "")
    warnings = "".join(f"<li>{esc(item)}</li>" for item in review.warnings)
    child_cards = _child_cards(summary, output_path)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vulca redraw review</title>
<style>
  :root {{ color-scheme: light; --ink:#181818; --muted:#686868; --line:#d9d9d9; --panel:#f7f7f4; --accent:#326441; --warn:#8b5d00; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:28px; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:var(--ink); background:#fff; }}
  header {{ max-width:1180px; margin:0 auto 24px; }}
  h1 {{ margin:0 0 8px; font-size:28px; }}
  .state {{ display:inline-flex; padding:4px 9px; border:1px solid var(--line); border-radius:999px; color:var(--accent); font-weight:600; }}
  .prompt {{ margin-top:14px; max-width:920px; color:var(--muted); line-height:1.55; }}
  .compare {{ max-width:1180px; margin:0 auto; display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  figure {{ margin:0; border:1px solid var(--line); background:var(--panel); }}
  figure img {{ width:100%; display:block; object-fit:contain; background:#eee; }}
  figcaption {{ padding:8px 10px; color:var(--muted); font-size:13px; }}
  .inspector {{ max-width:1180px; margin:18px auto; display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  .panel {{ border:1px solid var(--line); padding:14px; background:#fff; }}
  .panel h2 {{ margin:0 0 8px; font-size:16px; }}
  code {{ background:#f0f0ed; padding:2px 5px; border-radius:4px; }}
  .children {{ max-width:1180px; margin:18px auto; display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:14px; }}
  .child-card {{ border:1px solid var(--line); padding:10px; }}
  .child-card h3 {{ margin:0 0 8px; font-size:15px; display:flex; justify-content:space-between; gap:8px; }}
  .child-card h3 span {{ color:var(--muted); font-weight:500; }}
  .mini-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:6px; }}
  .mini-grid figure img {{ aspect-ratio:1; object-fit:cover; }}
  .meta {{ color:var(--muted); font-size:12px; }}
</style>
</head>
<body>
<header>
  <h1>Vulca redraw review</h1>
  <div class="state">{esc(_state_label(review.state))}</div>
  <p class="prompt">{esc(prompt)}</p>
</header>
<main>
  <section class="compare">
    <figure><img src="{esc(rel(source_path, output_path))}" alt="source image"><figcaption>Before: source image</figcaption></figure>
    <figure><img src="{esc(rel(after_path, output_path))}" alt="source pasteback result"><figcaption>After: source pasteback</figcaption></figure>
  </section>
  <section class="inspector">
    <div class="panel">
      <h2>Layer asset</h2>
      <p><code>{esc(rel(layer_path, output_path))}</code></p>
      <p>This is editable layer data, not the main after-image.</p>
    </div>
    <div class="panel">
      <h2>Review metadata</h2>
      <p><code>{esc(review.state)}</code></p>
      <ul>{warnings}</ul>
    </div>
  </section>
  <section class="children">
    {child_cards}
  </section>
</main>
</body>
</html>
"""


def write_review_html(summary_path: Path, output_path: Path) -> Path:
    summary = json.loads(summary_path.read_text())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(summary, output_path))
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = write_review_html(args.summary, args.output)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests and verify GREEN**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest tests/test_redraw_showcase_review.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Generate current Phase 2 review HTML**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 scripts/build_redraw_review.py \
  --summary docs/visual-specs/2026-04-27-ipad-cartoon-roadside/v0_22_gpt_image_2/phase2_art_direction_run1/summary.json \
  --output docs/visual-specs/2026-04-27-ipad-cartoon-roadside/v0_22_gpt_image_2/phase2_art_direction_run1/review.html
```

Expected: prints `docs/visual-specs/2026-04-27-ipad-cartoon-roadside/v0_22_gpt_image_2/phase2_art_direction_run1/review.html` and creates the file.

- [ ] **Step 6: Commit**

```bash
git add scripts/build_redraw_review.py tests/test_redraw_showcase_review.py docs/visual-specs/2026-04-27-ipad-cartoon-roadside/v0_22_gpt_image_2/phase2_art_direction_run1/review.html
git commit -m "feat: render redraw source-pasteback reviews"
```

## Task 4: Update Contract Docs With Implementation Hooks

**Files:**
- Modify: `docs/superpowers/specs/2026-04-30-redraw-showcase-product-contract-design.md`

- [ ] **Step 1: Update implementation section**

Add this section after `## Data Flow`:

```markdown
## Implementation Hooks

- `vulca.layers.redraw_review.classify_redraw_review(payload)` is the canonical in-repo state classifier for redraw payloads.
- External webapps should mirror the classifier's state names: `ready_for_review`, `technical_preview`, `unknown_quality_preview`, `layer_only_result`, `pasteback_warning`.
- `scripts/build_redraw_review.py` is the static showcase dogfood path. It reads a `summary.json`, chooses the best available source-context after-image, and renders a before/after HTML page.
- `source_pasteback_path` remains the highest-priority after-image input. A transparent `file` should be rendered as an inspector asset unless no pasteback exists.
```

- [ ] **Step 2: Run red-flag scan**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -c 'from pathlib import Path; terms=["TB"+"D","TO"+"DO","FIX"+"ME","place"+"holder","?""??"]; paths=[Path("docs/superpowers/specs/2026-04-30-redraw-showcase-product-contract-design.md"), Path("docs/superpowers/plans/2026-04-30-redraw-showcase-webapp-contract.md")]; hits=[(p,t) for p in paths for t in terms if t in p.read_text()]; print(hits); raise SystemExit(1 if hits else 0)'
```

Expected: prints `[]` and exits with code `0`.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/specs/2026-04-30-redraw-showcase-product-contract-design.md docs/superpowers/plans/2026-04-30-redraw-showcase-webapp-contract.md
git commit -m "docs: define redraw webapp review contract plan"
```

## Task 5: Regression Sweep

**Files:**
- No production changes unless tests expose a real regression.

- [ ] **Step 1: Run focused contract tests**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest \
  tests/test_redraw_review_contract.py \
  tests/test_redraw_showcase_review.py \
  tests/test_mcp_layers_redraw_advisory.py \
  -q
```

Expected: all tests pass.

- [ ] **Step 2: Run redraw regression tests**

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest \
  tests/test_mask_refine.py \
  tests/test_layers_redraw_refinement.py \
  tests/test_layers_redraw_crop_pipeline.py \
  tests/test_layers_redraw_quality_gates.py \
  tests/test_layers_redraw.py \
  -q
```

Expected: all tests pass.

- [ ] **Step 3: Run whitespace check**

Run:

```bash
git diff --check
```

Expected: no output and exit code `0`.

- [ ] **Step 4: Review changed files**

Run:

```bash
git status --short
```

Expected: changes are limited to:

```text
src/vulca/layers/redraw_review.py
scripts/build_redraw_review.py
tests/test_redraw_review_contract.py
tests/test_redraw_showcase_review.py
tests/test_mcp_layers_redraw_advisory.py
docs/superpowers/specs/2026-04-30-redraw-showcase-product-contract-design.md
docs/superpowers/plans/2026-04-30-redraw-showcase-webapp-contract.md
docs/visual-specs/2026-04-27-ipad-cartoon-roadside/v0_22_gpt_image_2/phase2_art_direction_run1/review.html
```
