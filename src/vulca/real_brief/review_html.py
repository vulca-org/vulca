"""Offline HTML review renderer for real-brief benchmark dry runs."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any


_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]+"),
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _safe_json_script(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, sort_keys=True)
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[redacted]", text)
    return text.replace("</", "<\\/")


def _condition_cards(manifest: dict[str, Any]) -> str:
    cards = []
    for condition in manifest.get("conditions", []):
        condition_id = _escape(condition.get("id", ""))
        label = _escape(condition.get("label", "Untitled condition"))
        purpose = _escape(condition.get("purpose", ""))
        condition_path = _escape(condition.get("condition_path", ""))
        prompt_path = _escape(condition.get("prompt_path", ""))
        cards.append(
            "\n".join(
                [
                    '<article class="card condition-card">',
                    f"<h2>Condition {condition_id}</h2>",
                    f"<p>{label}</p>",
                    f'<p class="muted">{purpose}</p>',
                    '<div class="links">',
                    f'<a href="{condition_path}">{condition_path}</a>',
                    f'<a href="{prompt_path}">{prompt_path}</a>',
                    "</div>",
                    "</article>",
                ]
            )
        )
    return "\n".join(cards)


def _package_links() -> str:
    return "\n".join(
        [
            '<section class="card package-links">',
            "<h2>Review Packages</h2>",
            '<div class="links horizontal-links">',
            '<a href="decision_package.md">Decision Package</a>',
            '<a href="production_package.md">Production Package</a>',
            '<a href="workflow_handoff.json">Workflow Handoff</a>',
            '<a href="review_schema.json">Review Schema</a>',
            "</div>",
            "</section>",
        ]
    )


def _dimension_rows(
    manifest: dict[str, Any],
    review_schema: dict[str, Any],
) -> str:
    scale = review_schema.get("scale", {})
    min_score = int(scale.get("min", 0))
    max_score = int(scale.get("max", 2))
    options = "\n".join(
        f'<option value="{score}">{score}</option>'
        for score in range(min_score, max_score + 1)
    )
    rows = []
    for condition in manifest.get("conditions", []):
        condition_id = _escape(condition.get("id", ""))
        condition_label = _escape(condition.get("label", "Untitled condition"))
        for dimension in review_schema.get("dimensions", []):
            dimension_id = _escape(dimension.get("id", ""))
            label = _escape(dimension.get("label", dimension.get("id", "")))
            rows.append(
                "\n".join(
                    [
                        "<tr>",
                        f"<th scope=\"row\"><code>{condition_id}</code><span>{condition_label}</span></th>",
                        f"<td><code>{dimension_id}</code><span>{label}</span></td>",
                        (
                            f'<td><select data-score-condition="{condition_id}" '
                            f'data-score-dimension="{dimension_id}">'
                            f'<option value="">-</option>{options}</select></td>'
                        ),
                        (
                            f'<td><textarea data-note-condition="{condition_id}" '
                            f'data-note-dimension="{dimension_id}" rows="2"></textarea></td>'
                        ),
                        "</tr>",
                    ]
                )
            )
    return "\n".join(rows)


def _brief_summary(structured_brief: dict[str, Any]) -> str:
    title = _escape(structured_brief.get("title", "Untitled brief"))
    client = _escape(structured_brief.get("client", "Unknown client"))
    slug = _escape(structured_brief.get("slug", "unknown-slug"))
    return "\n".join(
        [
            '<section class="summary">',
            f"<h2>{title}</h2>",
            f"<p><strong>Client:</strong> {client}</p>",
            f"<p><strong>Slug:</strong> <code>{slug}</code></p>",
            "</section>",
        ]
    )


def _html_document(
    manifest: dict[str, Any],
    review_schema: dict[str, Any],
    structured_brief: dict[str, Any],
) -> str:
    review_payload = {
        "manifest": manifest,
        "review_schema": review_schema,
        "structured_brief": {
            "slug": structured_brief.get("slug"),
            "title": structured_brief.get("title"),
            "client": structured_brief.get("client"),
        },
    }
    storage_key = _escape(
        "real-brief-review:"
        + str(manifest.get("fixture_slug") or structured_brief.get("slug") or "run")
    )
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>Real Brief Benchmark Review</title>",
            "<style>",
            ":root{color-scheme:light;font-family:Arial,sans-serif;background:#f6f4ef;color:#1d2329}",
            "body{margin:0;padding:32px}",
            "main{max-width:1120px;margin:0 auto}",
            "header{display:flex;justify-content:space-between;gap:24px;align-items:flex-start}",
            "h1{font-size:32px;line-height:1.1;margin:0 0 12px}",
            "h2{font-size:18px;margin:0 0 10px}",
            ".summary,.card,table{background:#fff;border:1px solid #d8d2c6;border-radius:8px}",
            ".summary{padding:16px;margin:20px 0}",
            ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}",
            ".card{padding:14px}",
            ".links{display:flex;flex-direction:column;gap:6px}",
            ".horizontal-links{flex-direction:row;flex-wrap:wrap}",
            "a{color:#154f7f}",
            "table{width:100%;border-collapse:collapse;margin-top:12px;overflow:hidden}",
            "th,td{padding:12px;border-top:1px solid #e6e0d5;text-align:left;vertical-align:top}",
            "th span,td span{display:block;font-weight:400;color:#5c6670;margin-top:4px}",
            "select,textarea{width:100%;box-sizing:border-box;border:1px solid #b8c0c8;border-radius:6px;padding:8px;font:inherit}",
            "textarea{resize:vertical}",
            "button{border:1px solid #1d2329;background:#1d2329;color:#fff;border-radius:6px;padding:9px 12px;font:inherit;cursor:pointer}",
            ".actions{display:flex;gap:8px;align-items:center;margin:18px 0}",
            ".muted{color:#66717c}",
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<header>",
            "<div>",
            "<h1>Real Brief Benchmark Review</h1>",
            '<p class="muted">Offline scoring form for dry-run benchmark artifacts.</p>',
            "</div>",
            '<button id="export-json" type="button">Export JSON</button>',
            "</header>",
            _brief_summary(structured_brief),
            _package_links(),
            "<section>",
            "<h2>Conditions</h2>",
            f'<div class="grid">{_condition_cards(manifest)}</div>',
            "</section>",
            "<section>",
            "<h2>Review Dimensions</h2>",
            "<table>",
            "<thead><tr><th>Condition</th><th>Dimension</th><th>Score</th><th>Notes</th></tr></thead>",
            f"<tbody>{_dimension_rows(manifest, review_schema)}</tbody>",
            "</table>",
            '<div class="actions"><button id="save-review" type="button">Save</button><span id="status" class="muted"></span></div>',
            "</section>",
            f'<script id="review-data" type="application/json">{_safe_json_script(review_payload)}</script>',
            "<script>",
            "(function(){",
            f"const storageKey = {json.dumps(storage_key)};",
            "const data = JSON.parse(document.getElementById('review-data').textContent);",
            "const status = document.getElementById('status');",
            "function ensureNested(root,conditionId){if(!root[conditionId])root[conditionId]={};return root[conditionId];}",
            "function collect(){const scores={};document.querySelectorAll('[data-score-condition]').forEach(function(el){const conditionId=el.dataset.scoreCondition;const dimensionId=el.dataset.scoreDimension;ensureNested(scores,conditionId);scores[conditionId][dimensionId]=el.value;});const notes={};document.querySelectorAll('[data-note-condition]').forEach(function(el){const conditionId=el.dataset.noteCondition;const dimensionId=el.dataset.noteDimension;ensureNested(notes,conditionId);notes[conditionId][dimensionId]=el.value;});return {schema_version:'0.1',fixture_slug:data.manifest.fixture_slug,condition_ids:data.manifest.condition_ids,reviewed_at:new Date().toISOString(),scores:scores,notes:notes};}",
            "function restore(){const saved=localStorage.getItem(storageKey);if(!saved)return;const parsed=JSON.parse(saved);(data.manifest.condition_ids||[]).forEach(function(conditionId){const scoreBucket=(parsed.scores&&parsed.scores[conditionId])||{};Object.entries(scoreBucket).forEach(function(entry){const el=document.querySelector('[data-score-condition=\"'+conditionId+'\"][data-score-dimension=\"'+entry[0]+'\"]');if(el)el.value=entry[1];});const noteBucket=(parsed.notes&&parsed.notes[conditionId])||{};Object.entries(noteBucket).forEach(function(entry){const el=document.querySelector('[data-note-condition=\"'+conditionId+'\"][data-note-dimension=\"'+entry[0]+'\"]');if(el)el.value=entry[1];});});status.textContent='Loaded saved review';}",
            "function save(){localStorage.setItem(storageKey,JSON.stringify(collect(),null,2));status.textContent='Saved locally';}",
            "document.getElementById('save-review').addEventListener('click',save);",
            "document.getElementById('export-json').addEventListener('click',function(){const blob=new Blob([JSON.stringify(collect(),null,2)+'\\n'],{type:'application/json'});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download='human_review.json';link.click();URL.revokeObjectURL(link.href);});",
            "document.querySelectorAll('select,textarea').forEach(function(el){el.addEventListener('change',save);});",
            "restore();",
            "}());",
            "</script>",
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def write_review_html(out_dir: str | Path) -> Path:
    """Write the offline human review HTML file for a dry-run output directory."""
    out_dir_path = Path(out_dir)
    manifest = _read_json(out_dir_path / "manifest.json")
    review_schema = _read_json(out_dir_path / "review_schema.json")
    structured_brief = _read_json(out_dir_path / "structured_brief.json")
    html_path = out_dir_path / "human_review.html"
    html_path.write_text(
        _html_document(manifest, review_schema, structured_brief),
        encoding="utf-8",
    )
    return html_path
