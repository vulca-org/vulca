from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]+"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(token|secret|api[_-]?key)\s*[:=]\s*[A-Za-z0-9_./+=-]{12,}"),
]

SAFE_HREF_SCHEMES = {"http", "https", "mailto"}


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


def _safe_href(value: Any, output_dir: Path, *, case_rel: str | None = None) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "#"
    if raw.startswith("#"):
        return raw
    if raw.startswith(("/", "\\")):
        return "#"

    parsed = urlsplit(raw)
    if parsed.scheme:
        return raw if parsed.scheme in SAFE_HREF_SCHEMES else "#"
    if parsed.netloc:
        return "#"
    if not case_rel:
        return "#"

    target = Path(case_rel) / raw
    return os.path.relpath(target, output_dir).replace(os.sep, "/")


def _capture_details(capture: dict[str, Any]) -> str:
    fields = [
        ("evidence_type", capture.get("evidence_type", "")),
        ("interaction", capture.get("interaction", "")),
        ("rights_status", capture.get("rights_status", "")),
        ("capture_method", capture.get("capture_method", "")),
        ("confidence", capture.get("confidence", "")),
    ]
    optional = [
        ("notes", capture.get("notes", "")),
        ("source_url", capture.get("source_url", "")),
    ]
    detail_rows = [
        f'<div class="capture-field"><span class="capture-label">{_escape(label)}</span><span>{_visible(value)}</span></div>'
        for label, value in fields
    ]
    detail_rows.extend(
        f'<div class="capture-field"><span class="capture-label">{_escape(label)}</span><span>{_visible(value)}</span></div>'
        for label, value in optional
        if value not in ("", None)
    )
    return '<div class="capture-details">' + "".join(detail_rows) + "</div>"


def _capture_card(case: dict[str, Any], capture: dict[str, Any], output_dir: Path) -> str:
    href = _safe_href(capture.get("path_or_url", ""), output_dir, case_rel=str(case.get("case_rel", "")) or None)
    return "\n".join(
        [
            '<li class="capture-item">',
            '<div class="capture-head">',
            f'<a href="{_escape(href)}">{_visible(capture.get("evidence_type", "capture"))}</a>',
            f'<span class="capture-path">{_visible(capture.get("path_or_url", ""))}</span>',
            "</div>",
            _capture_details(capture),
            "</li>",
        ]
    )


def _case_card(case: dict[str, Any], output_dir: Path) -> str:
    captures = case.get("captures", [])
    capture_cards = "".join(_capture_card(case, capture, output_dir) for capture in captures)
    modules = [module.get("module_type", "") for module in case.get("modules", [])]
    canonical_url = str(case.get("canonical_url", ""))
    canonical_href = _safe_href(canonical_url, output_dir)
    return "\n".join(
        [
            '<article class="case-card">',
            '<div class="case-head">',
            f"<h2>{_visible(case.get('title', 'Untitled'))}</h2>",
            f'<span class="score">{_escape(case.get("quality_score_total", 0))}/18</span>',
            "</div>",
            f"<p>{_visible(case.get('summary', ''))}</p>",
            f'<p><a href="{_escape(canonical_href)}">{_visible(canonical_url)}</a></p>',
            f'<div class="badges">{_badge_list(case.get("visual_families", []))}</div>',
            f'<div class="badges muted-badges">{_badge_list(modules)}</div>',
            _coverage(case.get("coverage", {})),
            f'<ul class="capture-list">{capture_cards}</ul>',
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
            "a{color:#8ed7ff}.capture-list{list-style:none;padding:0;margin:12px 0 0;display:grid;gap:10px}.capture-item{border-top:1px solid #222b35;padding-top:10px}.capture-head{display:flex;justify-content:space-between;gap:10px;align-items:baseline}.capture-path{color:#9aa7b4;font:12px/1.3 monospace;word-break:break-word}.capture-details{display:grid;gap:6px;margin-top:8px}.capture-field{display:grid;grid-template-columns:minmax(112px,auto) 1fr;gap:10px}.capture-label{font:12px/1.3 monospace;color:#9aa7b4;text-transform:lowercase}",
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
