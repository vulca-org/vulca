"""Workflow-level HTML review surface for adapted real-brief projects."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any


_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]+"),
]
_STATUS_RE = re.compile(r"(?im)^\s*status\s*:\s*([a-z0-9_-]+)\s*$")
_SECTION_RE_TEMPLATE = r"(?ims)^## {heading}\s*\n(.*?)(?=^## |\Z)"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _redact(text: str) -> str:
    scrubbed = text
    for pattern in _SECRET_PATTERNS:
        scrubbed = pattern.sub("[redacted]", scrubbed)
    return scrubbed


def _safe_json_script(payload: dict[str, Any]) -> str:
    return _redact(json.dumps(payload, ensure_ascii=False, sort_keys=True)).replace(
        "</",
        "<\\/",
    )


def _status_from_markdown(path: Path) -> str:
    if not path.exists():
        return "missing"
    match = _STATUS_RE.search(path.read_text(encoding="utf-8"))
    return match.group(1).lower() if match else "unknown"


def _extract_section(markdown: str, heading: str) -> str:
    pattern = re.compile(_SECTION_RE_TEMPLATE.format(heading=re.escape(heading)))
    match = pattern.search(markdown)
    return match.group(1).strip() if match else "none"


def _project_dirs(root: Path) -> list[Path]:
    specs_dir = root / "docs" / "visual-specs"
    if not specs_dir.exists():
        return []
    return sorted(
        path
        for path in specs_dir.iterdir()
        if (path / "real_brief" / "adapter_manifest.json").exists()
    )


def _rubric_lines(review_schema: dict[str, Any]) -> list[str]:
    scale = review_schema.get("scale", {})
    min_score = scale.get("min")
    max_score = scale.get("max")
    score_range = (
        f"{min_score}-{max_score}"
        if min_score is not None and max_score is not None
        else "source scale"
    )
    lines = []
    for dimension in review_schema.get("dimensions", []):
        label = str(dimension.get("label") or dimension.get("id") or "").strip()
        if label:
            lines.append(f"{label} ({score_range})")
    return lines


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _links(root: Path, project_dir: Path, has_proposal: bool) -> str:
    candidates = [
        ("Workflow Seed", project_dir / "workflow_seed.md"),
        ("Decision Package", project_dir / "real_brief" / "decision_package.md"),
        ("Production Package", project_dir / "real_brief" / "production_package.md"),
        ("Review Schema", project_dir / "real_brief" / "review_schema.json"),
        ("Source Brief", project_dir / "real_brief" / "source_brief.md"),
    ]
    if has_proposal:
        candidates.insert(1, ("Proposal", project_dir / "proposal.md"))
    return "\n".join(
        f'<a href="{_escape(_rel(root, path))}">{_escape(_rel(root, path))}</a>'
        for _, path in candidates
        if path.exists()
    )


def _project_payload(root: Path, project_dir: Path) -> dict[str, Any]:
    real_brief_dir = project_dir / "real_brief"
    adapter_manifest = _read_json(real_brief_dir / "adapter_manifest.json")
    structured = _read_json(real_brief_dir / "structured_brief.json")
    review_schema = _read_json(real_brief_dir / "review_schema.json")
    proposal_path = project_dir / "proposal.md"
    proposal_text = (
        _redact(proposal_path.read_text(encoding="utf-8"))
        if proposal_path.exists()
        else ""
    )
    return {
        "slug": structured.get("slug") or adapter_manifest.get("slug"),
        "title": structured.get("title"),
        "client": structured.get("client"),
        "domain": structured.get("domain") or adapter_manifest.get("domain"),
        "source_deadline": structured.get("source", {}).get("deadline"),
        "workflow_status": adapter_manifest.get("workflow_status"),
        "unsupported_reason": adapter_manifest.get("unsupported_reason"),
        "proposal_status": _status_from_markdown(proposal_path),
        "has_proposal": proposal_path.exists(),
        "proposal_excerpt": proposal_text.strip() if proposal_text else "missing",
        "rubric": _rubric_lines(review_schema),
        "proposal_rubric": _extract_section(proposal_text, "Acceptance rubric"),
        "open_questions": _extract_section(proposal_text, "Open questions"),
        "links_html": _links(root, project_dir, proposal_path.exists()),
        "project_rel": _rel(root, project_dir),
    }


def _summary(projects: list[dict[str, Any]]) -> dict[str, int]:
    supported = sum(
        1
        for project in projects
        if project["workflow_status"] == "ready_for_visual_brainstorm"
    )
    unsupported = sum(
        1 for project in projects if project["workflow_status"] == "unsupported_for_visual_chain"
    )
    proposals = sum(1 for project in projects if project["has_proposal"])
    return {
        "total": len(projects),
        "supported": supported,
        "unsupported": unsupported,
        "proposals": proposals,
    }


def _rubric_html(project: dict[str, Any]) -> str:
    if project["proposal_rubric"] != "none":
        return f"<pre>{_escape(project['proposal_rubric'])}</pre>"
    items = "\n".join(f"<li>{_escape(item)}</li>" for item in project["rubric"])
    return f"<ul>{items}</ul>" if items else "<p>none</p>"


def _project_card(project: dict[str, Any]) -> str:
    unsupported = project.get("unsupported_reason") or ""
    return "\n".join(
        [
            '<article class="project-card">',
            '<div class="project-head">',
            "<div>",
            f"<h2>{_escape(project['title'])}</h2>",
            f"<p>{_escape(project['client'])}</p>",
            "</div>",
            f'<span class="status">{_escape(project["workflow_status"])}</span>',
            "</div>",
            '<dl class="meta">',
            f"<div><dt>Domain</dt><dd>{_escape(project['domain'])}</dd></div>",
            f"<div><dt>Deadline</dt><dd>{_escape(project['source_deadline'] or 'not specified')}</dd></div>",
            f"<div><dt>Project</dt><dd><code>{_escape(project['project_rel'])}</code></dd></div>",
            f"<div><dt>Proposal</dt><dd>Proposal: {_escape(project['proposal_status'])}</dd></div>",
            "</dl>",
            (
                f'<p class="warning">{_escape(unsupported)}</p>'
                if unsupported
                else '<p class="gate">Human approval required before /visual-spec</p>'
            ),
            "<h3>Acceptance Rubric</h3>",
            _rubric_html(project),
            "<h3>Open Questions</h3>",
            f"<pre>{_escape(project['open_questions'])}</pre>",
            "<h3>Proposal Excerpt</h3>",
            f"<pre>{_escape(project['proposal_excerpt'])}</pre>",
            '<h3>Artifacts</h3>',
            f'<div class="links">{project["links_html"]}</div>',
            "</article>",
        ]
    )


def _html_document(root: Path, projects: list[dict[str, Any]]) -> str:
    counts = _summary(projects)
    payload = {"schema_version": "0.1", "summary": counts, "projects": projects}
    cards = "\n".join(_project_card(project) for project in projects)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>Real Brief Workflow Review</title>",
            "<style>",
            ":root{font-family:Arial,sans-serif;background:#f7f7f5;color:#17202a}",
            "body{margin:0;padding:28px}",
            "main{max-width:1180px;margin:0 auto}",
            "header{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:20px}",
            "h1{font-size:30px;margin:0 0 8px}",
            "h2{font-size:20px;margin:0 0 4px}",
            "h3{font-size:14px;text-transform:uppercase;margin:18px 0 8px}",
            ".summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:18px 0}",
            ".metric,.project-card{background:#fff;border:1px solid #d7dce0;border-radius:8px}",
            ".metric{padding:14px}.metric strong{display:block;font-size:26px}",
            ".project-card{padding:18px;margin:14px 0}",
            ".project-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start}",
            ".status{font:12px/1.2 monospace;border:1px solid #9fb3c8;border-radius:999px;padding:6px 8px;background:#eef5fb}",
            ".meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin:14px 0}",
            "dt{font-size:12px;color:#5d6b78}dd{margin:2px 0 0}",
            "pre{white-space:pre-wrap;background:#f2f4f5;border:1px solid #dde2e6;border-radius:6px;padding:10px;overflow:auto}",
            ".links{display:flex;flex-wrap:wrap;gap:8px}.links a{color:#155b8a}",
            ".gate{border-left:4px solid #1d7a4d;padding-left:10px}",
            ".warning{border-left:4px solid #a4481b;padding-left:10px}",
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<header>",
            "<div>",
            "<h1>Real Brief Workflow Review</h1>",
            f"<p>Root: <code>{_escape(root)}</code></p>",
            "</div>",
            "</header>",
            '<section class="summary">',
            f'<div class="metric"><strong>{counts["total"]}</strong>Total briefs</div>',
            f'<div class="metric"><strong>{counts["supported"]}</strong>Supported</div>',
            f'<div class="metric"><strong>{counts["unsupported"]}</strong>Unsupported</div>',
            f'<div class="metric"><strong>{counts["proposals"]}</strong>Draft proposals</div>',
            "</section>",
            cards or "<p>No adapted real-brief projects found.</p>",
            f'<script id="workflow-review-data" type="application/json">{_safe_json_script(payload)}</script>',
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def write_workflow_review_html(
    root: str | Path,
    output: str | Path | None = None,
) -> Path:
    """Write a review surface for adapted real-brief workflow projects."""
    root_path = Path(root)
    projects = [_project_payload(root_path, project_dir) for project_dir in _project_dirs(root_path)]
    html_path = Path(output) if output else root_path / "real_brief_workflow_review.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(_html_document(root_path, projects), encoding="utf-8")
    return html_path
