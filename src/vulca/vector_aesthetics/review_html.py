from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from typing import Any


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]+"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(token|secret|api[_-]?key)\s*[:=]\s*[A-Za-z0-9_./+=-]{12,}"),
]


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _visible(value: Any) -> str:
    return _escape(_redact(str(value)))


def _redact(text: str) -> str:
    result = text
    for pattern in SECRET_PATTERNS:
        result = pattern.sub("[redacted]", result)
    return result


def _safe_json_script(payload: dict[str, Any]) -> str:
    return _redact(json.dumps(payload, ensure_ascii=False, sort_keys=True)).replace("</", "<\\/")


def _badge_list(items: list[str]) -> str:
    return "".join(f"<span>{_visible(item)}</span>" for item in items)


def _coverage(coverage: dict[str, str]) -> str:
    rows = []
    for key, value in sorted(coverage.items()):
        rows.append(f"<li><strong>{_escape(key)}</strong><span>{_escape(value)}</span></li>")
    return '<ul class="coverage-list">' + "".join(rows) + "</ul>"


def _capture_href(case: dict[str, Any], capture: dict[str, Any], output_dir: Path) -> str:
    path_or_url = str(capture.get("path_or_url", ""))
    if path_or_url.startswith(("https://", "http://", "#", "mailto:")):
        return path_or_url

    case_rel = str(case.get("case_rel", ""))
    if case_rel:
        target = Path(case_rel) / path_or_url
        return os.path.relpath(target, output_dir).replace(os.sep, "/")

    return path_or_url


def _case_card(case: dict[str, Any], output_dir: Path) -> str:
    captures = case.get("captures", [])
    capture_links = "".join(
        (
            f'<a href="{_escape(_capture_href(case, capture, output_dir))}">'
            f"{_escape(capture.get('evidence_type', 'capture'))}</a>"
        )
        for capture in captures[:4]
    )
    modules = [module.get("module_type", "") for module in case.get("modules", [])]
    canonical_url = str(case.get("canonical_url", ""))
    return "\n".join(
        [
            '<article class="case-card">',
            '<div class="case-head">',
            f"<h2>{_visible(case.get('title', 'Untitled'))}</h2>",
            f'<span class="score">{_escape(case.get("quality_score_total", 0))}/18</span>',
            "</div>",
            f"<p>{_visible(case.get('summary', ''))}</p>",
            f'<p><a href="{_visible(canonical_url)}">{_visible(canonical_url)}</a></p>',
            f'<div class="badges">{_badge_list(case.get("visual_families", []))}</div>',
            f'<div class="badges muted-badges">{_badge_list(modules)}</div>',
            _coverage(case.get("coverage", {})),
            f'<div class="links">{capture_links}</div>',
            "</article>",
        ]
    )


def _html(payload: dict[str, Any], output_dir: Path) -> str:
    cases = payload.get("cases", [])
    cards = "\n".join(_case_card(case, output_dir) for case in cases)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>3D Vector Aesthetics Learning Atlas</title>",
            "<style>",
            ":root{color-scheme:dark;font-family:Arial,sans-serif;background:#0d1014;color:#e8edf2}",
            "body{margin:0;padding:28px;background:#0d1014}",
            "main{max-width:1280px;margin:0 auto}",
            "header{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:22px}",
            "h1{font-size:32px;margin:0 0 8px}h2{font-size:18px;margin:0}p{color:#aeb8c4;line-height:1.5}",
            ".views{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin:18px 0}",
            ".view-pill,.case-card{border:1px solid #27313d;background:#131922;border-radius:8px}",
            ".view-pill{padding:12px;color:#d8e4ef}",
            ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}",
            ".case-card{padding:16px}.case-head{display:flex;justify-content:space-between;gap:12px}",
            ".score{font:12px/1.2 monospace;border:1px solid #415061;border-radius:999px;padding:5px 8px;color:#c9f3ff}",
            ".badges{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}.badges span{font:12px/1.2 monospace;background:#1e2a36;border:1px solid #32404f;border-radius:999px;padding:5px 7px}",
            ".muted-badges span{color:#b3bcc6}.coverage-list{list-style:none;padding:0;margin:12px 0;display:grid;gap:5px}.coverage-list li{display:flex;justify-content:space-between;gap:12px;border-top:1px solid #222b35;padding-top:5px}",
            "a{color:#8ed7ff}.links{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}",
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            '<header><div><h1>3D Vector Aesthetics Learning Atlas</h1><p>Archive + Lab + Course review surface for contemporary technical vector references.</p></div></header>',
            '<section class="views">',
            '<div class="view-pill">Atlas View</div>',
            '<div class="view-pill">Anatomy View</div>',
            '<div class="view-pill">Compare View</div>',
            '<div class="view-pill">Coverage View</div>',
            '<div class="view-pill">Lesson Path View</div>',
            "</section>",
            f'<section class="grid">{cards}</section>',
            f'<script id="review-data" type="application/json">{_safe_json_script(payload)}</script>',
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def write_review_html(review_json_path: Path, html_path: Path) -> Path:
    payload = json.loads(review_json_path.read_text(encoding="utf-8"))
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(_html(payload, html_path.parent), encoding="utf-8")
    return html_path
