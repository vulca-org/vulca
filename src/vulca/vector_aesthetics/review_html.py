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


def _asset_manifest_label(status: Any) -> str:
    labels = {
        "present_empty": "Manifest present, no archived assets",
        "present_with_assets": "Manifest present with archived assets",
        "present_unknown": "Manifest present, asset list unknown",
        "present_unreadable": "Manifest present but unreadable",
        "missing": "No asset manifest",
    }
    return labels.get(str(status), str(status or "unknown"))


def _coverage(coverage: dict[str, str]) -> str:
    rows = []
    for key, value in sorted(coverage.items()):
        rows.append(f"<li><strong>{_escape(key)}</strong><span>{_escape(value)}</span></li>")
    return '<ul class="coverage-list">' + "".join(rows) + "</ul>"


def _flag_list(flags: list[str]) -> str:
    if not flags:
        return '<div class="flags flags-clear"><span>gold_candidate_ready</span></div>'
    return '<div class="flags">' + "".join(f"<span>{_visible(flag)}</span>" for flag in flags) + "</div>"


def _is_gold_case(case: dict[str, Any]) -> bool:
    return not case.get("data_quality_flags")


def _case_class(case: dict[str, Any]) -> str:
    return "case-gold" if _is_gold_case(case) else "case-seed"


def _is_release_ready(summary: dict[str, Any]) -> bool:
    case_count = int(summary.get("case_count") or 0)
    return (
        case_count > 0
        and int(summary.get("gold_case_count") or 0) == case_count
        and int(summary.get("multimodal_complete_count") or 0) == case_count
        and int(summary.get("seed_stub_case_count") or 0) == 0
        and int(summary.get("candidate_count") or 0) == 0
    )


def _safe_href(value: Any, output_dir: Path, *, case_path: str | None = None) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "#"
    if raw.startswith("#"):
        return raw
    if raw.startswith(("/", "\\")):
        return "#"

    parsed = urlsplit(raw)
    if parsed.scheme:
        return _redact(raw) if parsed.scheme in SAFE_HREF_SCHEMES else "#"
    if parsed.netloc:
        return "#"
    if not case_path:
        return "#"

    target = Path(case_path) / raw
    return _redact(os.path.relpath(target, output_dir).replace(os.sep, "/"))


def _media_preview(case: dict[str, Any], output_dir: Path) -> str:
    case_path = str(case.get("local_case_path") or case.get("case_rel", "")) or None
    previews = []
    for evidence_type in ["screenshot", "video"]:
        capture = next(
            (
                item
                for item in case.get("captures", [])
                if item.get("evidence_type") == evidence_type
                and item.get("rights_status") == "local_capture"
                and item.get("interaction") != "capture_failed"
            ),
            None,
        )
        if not capture:
            continue
        href = _safe_href(capture.get("path_or_url", ""), output_dir, case_path=case_path)
        label = "video" if evidence_type == "video" else "screenshot"
        previews.append(
            "\n".join(
                [
                    '<a class="preview-tile" href="' + _escape(href) + '">',
                    f'<img src="{_escape(href)}" alt="{_visible(case.get("title", "Case"))} {label} preview" loading="lazy">',
                    f"<span>{_visible(label)}</span>",
                    "</a>",
                ]
            )
        )
    if not previews:
        return '<div class="media-preview media-empty"><span>No local media preview</span></div>'
    return '<div class="media-preview">' + "".join(previews) + "</div>"


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
    case_path = str(case.get("local_case_path") or case.get("case_rel", "")) or None
    href = _safe_href(capture.get("path_or_url", ""), output_dir, case_path=case_path)
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


def _text_panel(title: str, body: Any) -> str:
    if body in ("", None):
        return ""
    return "\n".join(
        [
            '<section class="learning-panel">',
            f"<h3>{_visible(title)}</h3>",
            f"<pre>{_visible(body)}</pre>",
            "</section>",
        ]
    )


def _payload_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _module_details(modules: list[dict[str, Any]]) -> str:
    rows = []
    for module in modules:
        payload = module.get("payload", {})
        payload_rows = []
        if isinstance(payload, dict):
            for key, value in sorted(payload.items()):
                payload_rows.append(
                    '<div class="module-field">'
                    f"<span>{_visible(key)}</span><span>{_visible(_payload_value(value))}</span>"
                    "</div>"
                )
        rows.append(
            "\n".join(
                [
                    '<section class="module-card">',
                    '<div class="module-head">',
                    f"<strong>{_visible(module.get('module_type', 'module'))}</strong>",
                    f"<span>{_visible(module.get('review_status', ''))} / {_visible(module.get('confidence', ''))}</span>",
                    "</div>",
                    "".join(payload_rows),
                    _text_panel("review_notes", module.get("review_notes", "")),
                    "</section>",
                ]
            )
        )
    return '<div class="module-list">' + "".join(rows) + "</div>"


def _case_card(case: dict[str, Any], output_dir: Path) -> str:
    captures = case.get("captures", [])
    capture_cards = "".join(_capture_card(case, capture, output_dir) for capture in captures)
    modules = [module.get("module_type", "") for module in case.get("modules", [])]
    canonical_url = str(case.get("canonical_url", ""))
    canonical_href = _safe_href(canonical_url, output_dir)
    return "\n".join(
        [
            f'<article class="case-card {_case_class(case)}" data-case-id="{_visible(case.get("id", ""))}">',
            '<div class="case-head">',
            f"<h2>{_visible(case.get('title', 'Untitled'))}</h2>",
            f'<span class="score">{_escape(case.get("quality_score_total", 0))}/18</span>',
            "</div>",
            _media_preview(case, output_dir),
            f"<p>{_visible(case.get('summary', ''))}</p>",
            f'<p><a href="{_escape(canonical_href)}">{_visible(canonical_url)}</a></p>',
            f'<div class="badges">{_badge_list(case.get("visual_families", []))}</div>',
            f'<div class="badges muted-badges">{_badge_list(modules)}</div>',
            f'<p class="manifest-state">{_visible(_asset_manifest_label(case.get("asset_manifest_status")))}</p>',
            _flag_list(case.get("data_quality_flags", [])),
            _coverage(case.get("coverage", {})),
            '<div class="learning-path">',
            _text_panel("Anatomy", case.get("anatomy_excerpt", "")),
            _text_panel("Lesson Path", case.get("lesson_excerpt", "")),
            _text_panel("VULCA Translation", case.get("vulca_translation_excerpt", "")),
            _module_details(case.get("modules", [])),
            "</div>",
            f'<ul class="capture-list">{capture_cards}</ul>',
            "</article>",
        ]
    )


def _quality_gate(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    release_ready = _is_release_ready(summary)
    items = [
        ("Total cases", summary.get("case_count", 0)),
        ("Gold cases", summary.get("gold_case_count", 0)),
        ("Seed/stub cases", summary.get("seed_stub_case_count", 0)),
        ("Multimodal complete", summary.get("multimodal_complete_count", 0)),
    ]
    rows = "".join(
        '<div class="quality-metric">'
        f"<strong>{_visible(value)}</strong><span>{_visible(label)}</span>"
        "</div>"
        for label, value in items
    )
    heading = "Release-ready atlas" if release_ready else "Data Quality Gate"
    description = (
        "All tracked cases are gold-ready and multimodal complete. Source links remain attribution-only; local PNG, GIF, HTML, module payloads, lessons, and VULCA translations are present for review."
        if release_ready
        else "Seed/stub flags are intentionally visible here: a case is not learning-ready until local visual evidence, module payloads, and verified rebuild notes are present."
    )
    section_class = "quality-gate quality-complete" if release_ready else "quality-gate"
    return "\n".join(
        [
            f'<section class="{section_class}">',
            f"<h2>{_visible(heading)}</h2>",
            f"<p>{_visible(description)}</p>",
            f'<div class="quality-grid">{rows}</div>',
            "</section>",
        ]
    )


def _filter_controls(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    seed_count = int(summary.get("seed_stub_case_count") or 0)
    seed_control = (
        '<label for="filter-seed">Seed gaps</label>'
        if seed_count
        else '<span class="filter-static">No active seed gaps</span>'
    )
    return "\n".join(
        [
            '<section class="review-filters">',
            "<h2>Review Filters</h2>",
            '<div class="filter-row">',
            '<label for="filter-all">All cases</label>',
            '<label for="filter-gold">Gold only</label>',
            seed_control,
            "</div>",
            "</section>",
        ]
    )


def _family_matrix(cases: list[dict[str, Any]]) -> str:
    families: dict[str, dict[str, int]] = {}
    for case in cases:
        for family in case.get("visual_families", []):
            family_key = str(family)
            record = families.setdefault(family_key, {"total": 0, "gold": 0})
            record["total"] += 1
            if _is_gold_case(case):
                record["gold"] += 1
    rows = []
    for family, record in sorted(families.items()):
        rows.append(
            "\n".join(
                [
                    "<tr>",
                    f"<th>{_visible(family)}</th>",
                    f"<td>{_visible(str(record['gold']) + ' / ' + str(record['total']) + ' gold')}</td>",
                    "</tr>",
                ]
            )
        )
    return "\n".join(
        [
            '<section class="coverage-matrix">',
            "<h2>Family Coverage Matrix</h2>",
            "<table>",
            "<thead><tr><th>Family</th><th>Gold Coverage</th></tr></thead>",
            f"<tbody>{''.join(rows)}</tbody>",
            "</table>",
            "</section>",
        ]
    )


def _gap_queue(cases: list[dict[str, Any]]) -> str:
    rows = []
    for case in cases:
        flags = case.get("data_quality_flags", [])
        if not flags:
            continue
        flag_badges = '<span class="gap-flags">' + "".join(f"<span>{_visible(flag)}</span>" for flag in flags) + "</span>"
        rows.append(
            "\n".join(
                [
                    '<li class="gap-item">',
                    f"<strong>{_visible(case.get('title', 'Untitled'))}</strong>",
                    flag_badges,
                    "</li>",
                ]
            )
        )
    has_gaps = bool(rows)
    body = (
        "".join(rows)
        if has_gaps
        else '<li class="gap-item gap-clear"><strong>No active gaps</strong><span>All tracked cases are gold-ready and multimodal complete.</span></li>'
    )
    heading = "Gap Queue" if has_gaps else "Completion Checklist"
    return "\n".join(
        [
            '<section class="gap-queue">',
            f"<h2>{heading}</h2>",
            f"<ul>{body}</ul>",
            "</section>",
        ]
    )


def _compare_matrix(cases: list[dict[str, Any]]) -> str:
    rows = []
    for case in cases:
        modules = ", ".join(module.get("module_type", "") for module in case.get("modules", []))
        families = ", ".join(str(item) for item in case.get("visual_families", []))
        coverage = case.get("coverage", {})
        rows.append(
            "\n".join(
                [
                    "<tr>",
                    f"<th>{_visible(case.get('title', 'Untitled'))}</th>",
                    f"<td>{_visible(case.get('source_type', ''))}</td>",
                    f"<td>{_visible(families)}</td>",
                    f"<td>{_visible(modules)}</td>",
                    f"<td>{_visible(str(case.get('quality_score_total', 0)) + '/18')}</td>",
                    f"<td>{_visible(str(coverage.get('screenshots', '')) + ' / ' + str(coverage.get('video', '')))}</td>",
                    "</tr>",
                ]
            )
        )
    return "\n".join(
        [
            '<section class="compare-matrix">',
            "<h2>Compare Matrix</h2>",
            "<table>",
            "<thead><tr><th>Case</th><th>Source</th><th>Family</th><th>Modules</th><th>Score</th><th>Screenshot / Video</th></tr></thead>",
            f"<tbody>{''.join(rows)}</tbody>",
            "</table>",
            "</section>",
        ]
    )


def _html(payload: dict[str, Any], output_dir: Path) -> str:
    cases = payload.get("cases", [])
    cards = "\n".join(_case_card(case, output_dir) for case in cases)
    quality = _quality_gate(payload)
    filters = _filter_controls(payload)
    family_matrix = _family_matrix(cases)
    gap_queue = _gap_queue(cases)
    compare = _compare_matrix(cases)
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
            ".filter-toggle{position:absolute;inline-size:1px;block-size:1px;opacity:0;pointer-events:none}",
            "#filter-gold:checked ~ .grid .case-seed{display:none}#filter-seed:checked ~ .grid .case-gold{display:none}",
            "#filter-all:checked ~ .review-filters label[for=filter-all],#filter-gold:checked ~ .review-filters label[for=filter-gold],#filter-seed:checked ~ .review-filters label[for=filter-seed]{background:#d8e4ef;color:#10151b;border-color:#d8e4ef}",
            "header{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:22px}",
            "h1{font-size:32px;margin:0 0 8px}h2{font-size:18px;margin:0}p{color:#aeb8c4;line-height:1.5}",
            ".views{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin:18px 0}",
            ".view-pill,.case-card{border:1px solid #27313d;background:#131922;border-radius:8px}",
            ".view-pill{padding:12px;color:#d8e4ef}",
            ".active-view{background:#d8e4ef;color:#10151b;border-color:#d8e4ef}",
            ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}",
            ".case-card{padding:16px}.case-head{display:flex;justify-content:space-between;gap:12px}",
            ".media-preview{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:12px 0}.media-empty{display:block;border-top:1px solid #222b35;padding-top:10px;color:#7f8b99;font:12px/1.3 monospace}.preview-tile{position:relative;display:block;aspect-ratio:16/9;overflow:hidden;border:1px solid #2c3947;background:#0a0f15}.preview-tile img{width:100%;height:100%;object-fit:cover;display:block}.preview-tile span{position:absolute;left:8px;bottom:8px;background:#0b1118cc;border:1px solid #334353;color:#d8e4ef;font:11px/1.2 monospace;padding:4px 6px}",
            ".score{font:12px/1.2 monospace;border:1px solid #415061;border-radius:999px;padding:5px 8px;color:#c9f3ff}",
            ".badges{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}.badges span{font:12px/1.2 monospace;background:#1e2a36;border:1px solid #32404f;border-radius:999px;padding:5px 7px}",
            ".flags{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}.flags span{font:12px/1.2 monospace;color:#ffd4bd;background:#3a211b;border:1px solid #684032;border-radius:999px;padding:5px 7px}.flags-clear span{color:#bfe8c4;background:#193120;border-color:#345a3d}",
            ".muted-badges span{color:#b3bcc6}.coverage-list{list-style:none;padding:0;margin:12px 0;display:grid;gap:5px}.coverage-list li{display:flex;justify-content:space-between;gap:12px;border-top:1px solid #222b35;padding-top:5px}",
            ".manifest-state{font:12px/1.4 monospace;color:#d7c98d;margin:8px 0 0}.learning-path{display:grid;gap:10px;margin:12px 0}.learning-panel,.module-card{border-top:1px solid #222b35;padding-top:10px}.learning-panel h3{font-size:13px;margin:0 0 6px;color:#d8e4ef}.learning-panel pre{white-space:pre-wrap;word-break:break-word;margin:0;color:#aeb8c4;font:12px/1.45 monospace}.module-list{display:grid;gap:8px}.module-head{display:flex;justify-content:space-between;gap:10px;color:#d8e4ef;font:12px/1.4 monospace}.module-field{display:grid;grid-template-columns:minmax(120px,auto) 1fr;gap:10px;font:12px/1.4 monospace;color:#aeb8c4}",
            ".quality-gate{border:1px solid #4d3626;background:#1a1613;border-radius:8px;padding:16px;margin:18px 0}.quality-gate h2{margin:0 0 8px}.quality-gate p{margin:0 0 12px;color:#d0b8a6}.quality-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}.quality-metric{border-top:1px solid #4d3626;padding-top:10px}.quality-metric strong{display:block;font-size:22px}.quality-metric span{color:#d0b8a6;font:12px/1.3 monospace}",
            ".quality-gate{border:1px solid #4d3626;background:#1a1613;border-radius:8px;padding:16px;margin:18px 0}.quality-complete{border-color:#345a3d;background:#111d16}.quality-gate h2{margin:0 0 8px}.quality-gate p{margin:0 0 12px;color:#d0b8a6}.quality-complete p{color:#bfe8c4}.quality-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}.quality-metric{border-top:1px solid #4d3626;padding-top:10px}.quality-complete .quality-metric{border-top-color:#345a3d}.quality-metric strong{display:block;font-size:22px}.quality-metric span{color:#d0b8a6;font:12px/1.3 monospace}.quality-complete .quality-metric span{color:#bfe8c4}",
            ".review-filters,.coverage-matrix,.gap-queue,.compare-matrix{margin:22px 0;overflow:auto}.review-filters h2,.coverage-matrix h2,.gap-queue h2,.compare-matrix h2{margin:0 0 10px}.filter-row{display:flex;flex-wrap:wrap;gap:8px}.filter-row label,.filter-static{border:1px solid #344353;background:#121922;color:#d8e4ef;border-radius:8px;padding:8px 10px;font:12px/1.2 monospace}.filter-row label{cursor:pointer}.filter-static{color:#bfe8c4;background:#142118;border-color:#345a3d}.coverage-matrix table,.compare-matrix table{width:100%;border-collapse:collapse;font-size:12px}.coverage-matrix th,.coverage-matrix td,.compare-matrix th,.compare-matrix td{border-top:1px solid #27313d;padding:8px;text-align:left;vertical-align:top}.coverage-matrix th,.compare-matrix th{color:#e8edf2}.coverage-matrix td,.compare-matrix td{color:#aeb8c4}.gap-queue ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}.gap-item{border-top:1px solid #27313d;padding-top:8px;display:grid;grid-template-columns:minmax(180px,auto) 1fr;gap:12px}.gap-item strong{color:#e8edf2}.gap-flags{display:flex;flex-wrap:wrap;gap:6px}.gap-flags span{color:#ffd4bd;background:#3a211b;border:1px solid #684032;border-radius:999px;padding:4px 6px;font:12px/1.2 monospace}.gap-clear span{color:#bfe8c4}",
            "a{color:#8ed7ff}.capture-list{list-style:none;padding:0;margin:12px 0 0;display:grid;gap:10px}.capture-item{border-top:1px solid #222b35;padding-top:10px}.capture-head{display:flex;justify-content:space-between;gap:10px;align-items:baseline}.capture-path{color:#9aa7b4;font:12px/1.3 monospace;word-break:break-word}.capture-details{display:grid;gap:6px;margin-top:8px}.capture-field{display:grid;grid-template-columns:minmax(112px,auto) 1fr;gap:10px}.capture-label{font:12px/1.3 monospace;color:#9aa7b4;text-transform:lowercase}",
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            '<header><div><h1>3D Vector Aesthetics Learning Atlas</h1><p>Archive + Lab + Course review surface for contemporary technical vector references.</p></div></header>',
            '<input class="filter-toggle" type="radio" name="case-filter" id="filter-all" checked>',
            '<input class="filter-toggle" type="radio" name="case-filter" id="filter-gold">',
            '<input class="filter-toggle" type="radio" name="case-filter" id="filter-seed">',
            '<section class="views">',
            '<div class="view-pill active-view">Atlas View</div>',
            '<div class="view-pill">Anatomy View</div>',
            '<div class="view-pill">Compare View</div>',
            '<div class="view-pill">Coverage View</div>',
            '<div class="view-pill">Lesson Path View</div>',
            "</section>",
            filters,
            quality,
            family_matrix,
            gap_queue,
            compare,
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
