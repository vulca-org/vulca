#!/usr/bin/env python3
"""Build a static before/after review page for redraw showcase summaries."""
from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
from typing import Any

from vulca.layers.redraw_review import RedrawReview, classify_redraw_review


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def rel(path: str, output_path: Path) -> str:
    if not path:
        return ""
    return os.path.relpath(path, output_path.parent)


def _last_succeeded_child_after(summary: dict[str, Any]) -> str:
    selected = ""
    for child in summary.get("children", []):
        if not isinstance(child, dict):
            continue
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
    if isinstance(refinement, dict):
        if isinstance(refinement.get("applied"), bool):
            payload["refinement_applied"] = refinement["applied"]
        prepared = refinement.get("child_count_prepared")
        if isinstance(prepared, int) and not isinstance(prepared, bool):
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
        if not isinstance(child, dict):
            continue
        index = child.get("index", "?")
        status = child.get("status", "unknown")
        cost = child.get("cost_usd")
        cost_text = f"${cost:.3f}" if isinstance(cost, (int, float)) else ""
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


def _main_after_slot(review: RedrawReview, output_path: Path) -> str:
    if review.show_as_final and review.source_pasteback_path:
        return (
            f'<figure><img src="{esc(rel(review.source_pasteback_path, output_path))}" '
            f'alt="source pasteback result"><figcaption>After: source pasteback</figcaption></figure>'
        )

    messages = "".join(f"<li>{esc(item)}</li>" for item in review.warnings)
    if not messages and review.source_pasteback_error:
        messages += f"<li>{esc(review.source_pasteback_error)}</li>"
    if not messages:
        messages = "<li>source_pasteback_path_missing</li>"
    return f"""
    <div class="panel compare-fallback" role="status">
      <h2>{esc(_state_label(review.state))}</h2>
      <p>The final source pasteback is unavailable for the main after-image slot.</p>
      <ul>{messages}</ul>
    </div>
    """


def build_html(summary: dict[str, Any], output_path: Path) -> str:
    review = classify_redraw_review(payload_from_summary(summary))
    source_path = str(summary.get("source_path") or "")
    layer_path = review.layer_asset_path
    prompt = str(summary.get("prompt") or "")
    warnings = "".join(f"<li>{esc(item)}</li>" for item in review.warnings)
    main_after_slot = _main_after_slot(review, output_path)
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
  .panel.compare-fallback {{ min-height:240px; display:flex; flex-direction:column; justify-content:center; background:#fff8e5; border-color:#d8b45d; }}
  .compare-fallback h2 {{ color:var(--warn); }}
  .panel h2 {{ margin:0 0 8px; font-size:16px; }}
  code {{ background:#f0f0ed; padding:2px 5px; border-radius:4px; }}
  .children {{ max-width:1180px; margin:18px auto; display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:14px; }}
  .child-card {{ border:1px solid var(--line); padding:10px; }}
  .child-card h3 {{ margin:0 0 8px; font-size:15px; display:flex; justify-content:space-between; gap:8px; }}
  .child-card h3 span {{ color:var(--muted); font-weight:500; }}
  .mini-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:6px; }}
  .mini-grid figure img {{ aspect-ratio:1; object-fit:cover; }}
  .meta {{ color:var(--muted); font-size:12px; }}
  @media (max-width: 760px) {{
    body {{ padding:16px; }}
    .compare, .inspector {{ grid-template-columns:1fr; }}
  }}
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
    {main_after_slot}
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
