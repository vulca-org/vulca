"""Seed /visual-brainstorm proposal drafts from adapted real-brief packages."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from vulca.real_brief.types import safe_slug
from vulca.real_brief.workflow_adapter import SUPPORTED_STATIC_VISUAL_DOMAINS


_RUN_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_STATUS_RE = re.compile(r"(?im)^\s*status\s*:\s*([a-z0-9_-]+)\s*$")
_ALLOWED_STYLE_TREATMENTS = {"additive", "unified", "collage", "wash"}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_date(date: str) -> str:
    if not _RUN_DATE_RE.fullmatch(date):
        raise ValueError("date must use YYYY-MM-DD")
    return date


def _project_dir(root: Path, slug: str) -> Path:
    return root / "docs" / "visual-specs" / slug


def _status_from_markdown(path: Path) -> str:
    match = _STATUS_RE.search(path.read_text(encoding="utf-8"))
    return match.group(1).lower() if match else ""


def _require_file(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"required brainstorm seed file missing: {path}")
    return path


def _bullet_list(items: list[Any]) -> str:
    values = [str(item).strip() for item in items if str(item).strip()]
    return "\n".join(f"- {item}" for item in values) if values else "none"


def _deliverable_lines(deliverables: list[dict[str, Any]]) -> str:
    lines = []
    for item in deliverables:
        name = str(item.get("name") or "deliverable").strip()
        fmt = str(item.get("format") or "unspecified format").strip()
        channel = str(item.get("channel") or "unspecified channel").strip()
        required = item.get("required", True)
        suffix = "" if required else " (optional)"
        lines.append(f"- {name} ({fmt}, {channel}){suffix}")
    return "\n".join(lines) if lines else "none"


def _color_constraints(constraints: list[str]) -> str:
    matches = [
        item
        for item in constraints
        if any(term in item.casefold() for term in ("color", "colour", "palette"))
    ]
    return _bullet_list(matches) if matches else "none specified"


def _style_treatment(handoff: dict[str, Any]) -> str:
    seed = handoff.get("visual_brainstorm_seed", {})
    value = str(seed.get("style_treatment") or "unified").strip().lower()
    return value if value in _ALLOWED_STYLE_TREATMENTS else "unified"


def _series_plan(deliverables: list[dict[str, Any]]) -> str:
    if len(deliverables) <= 1:
        return "none"
    names = [str(item.get("name") or "deliverable").strip() for item in deliverables]
    return "\n".join(
        [
            f"- Deliverable count: {len(deliverables)}",
            "- Variation axis: adapt one approved key direction across required formats.",
            "- Deliverables:",
            *[f"  - {name}" for name in names],
        ]
    )


def _references(structured: dict[str, Any], project_dir: Path) -> str:
    source = structured.get("source", {})
    lines = [
        f"- source: {source.get('url')}",
        f"- source retrieved on: {source.get('retrieved_on')}",
        "- copied real brief package: real_brief/",
        "- workflow seed: workflow_seed.md",
    ]
    if source.get("deadline"):
        lines.append(f"- source deadline: {source['deadline']}")
    lines.append(f"- project directory: {project_dir}")
    return "\n".join(str(line) for line in lines if "None" not in str(line))


def _intent(structured: dict[str, Any]) -> str:
    parts = [
        str(structured.get("context") or "").strip(),
        str(structured.get("source_brief") or "").strip(),
    ]
    text = " ".join(part for part in parts if part)
    return text or str(structured.get("title") or "none").strip()


def _market(structured: dict[str, Any]) -> str:
    client = str(structured.get("client") or "").strip()
    source = structured.get("source", {})
    source_url = str(source.get("url") or "").strip()
    if client or source_url:
        return (
            "Market not explicitly specified by the source brief. "
            f"Use client/source context only: {client or source_url}."
        )
    return "domestic, no multilingual"


def _budget_deadline(structured: dict[str, Any]) -> str:
    source = structured.get("source", {})
    lines = [
        f"- Budget: {structured.get('budget') or 'none specified'}",
        f"- Timeline: {structured.get('timeline') or 'none specified'}",
    ]
    if source.get("deadline"):
        lines.append(f"- Source deadline: {source['deadline']}")
    return "\n".join(lines)


def _questions_resolved(structured: dict[str, Any], handoff: dict[str, Any]) -> str:
    seed = handoff.get("visual_brainstorm_seed", {})
    return "\n".join(
        [
            "- Q: What is the source brief?",
            f"  A: {structured.get('title')}",
            "- Q: Which workflow stage owns this draft?",
            "  A: /visual-brainstorm owns proposal.md; downstream stages remain gated.",
            "- Q: Which domain should the visual chain use?",
            f"  A: {seed.get('domain') or structured.get('domain')}",
            "- Q: Should provider execution happen now?",
            "  A: No. This is a simulation-only planning seed.",
        ]
    )


def _open_questions() -> str:
    return "\n".join(
        [
            "- Which stakeholder approves the final direction?",
            "- Which deliverable must be most production-ready first?",
            "- Which source assets already exist?",
            "- Should style_treatment remain unified, or change to additive, collage, or wash?",
            "- Should a validated cultural tradition be declared before /visual-spec?",
            "- Human approval required before `/visual-spec`.",
        ]
    )


def _notes(structured: dict[str, Any]) -> str:
    constraints = _bullet_list(list(structured.get("constraints", [])))
    risks = _bullet_list(list(structured.get("risks", [])))
    avoid = _bullet_list(list(structured.get("avoid", [])))
    return "\n".join(
        [
            "Real brief seed imported from a simulation-only benchmark package.",
            "No image provider, redraw provider, or evaluator is invoked by this step.",
            "",
            "Constraints:",
            constraints,
            "",
            "Risks:",
            risks,
            "",
            "Rejected approaches / avoid:",
            avoid,
        ]
    )


def _proposal_markdown(
    *,
    project_dir: Path,
    structured: dict[str, Any],
    handoff: dict[str, Any],
    date: str,
) -> str:
    slug = safe_slug(str(structured.get("slug") or handoff.get("slug") or ""))
    title = str(structured.get("title") or slug)
    domain = str(
        structured.get("domain")
        or handoff.get("visual_brainstorm_seed", {}).get("domain")
        or ""
    )
    style_treatment = _style_treatment(handoff)
    audience = _bullet_list(list(structured.get("audience", [])))
    deliverables = list(structured.get("deliverables", []))
    constraints = list(structured.get("constraints", []))

    return "\n".join(
        [
            "---",
            f"slug: {slug}",
            "status: draft",
            f"domain: {domain}",
            "tradition: null",
            f"style_treatment: {style_treatment}",
            "generated_by: visual-brainstorm@0.1.0",
            f"created: {date}",
            f"updated: {date}",
            "---",
            "",
            f"# {title}",
            "",
            (
                "> Seeded from `real_brief/` artifacts. This is a draft; "
                "human approval is still required before `/visual-spec`."
            ),
            "",
            "## Intent",
            _intent(structured),
            "",
            "## Audience",
            audience,
            "",
            "## Physical form",
            _deliverable_lines(deliverables),
            "",
            "## Market",
            _market(structured),
            "",
            "## Budget & deadline",
            _budget_deadline(structured),
            "",
            "## Color constraints",
            _color_constraints(constraints),
            "",
            "## References",
            _references(structured, project_dir),
            "",
            "## Series plan",
            _series_plan(deliverables),
            "",
            "## Acceptance rubric",
            "none",
            "",
            "## Questions resolved",
            _questions_resolved(structured, handoff),
            "",
            "## Open questions",
            _open_questions(),
            "",
            "## Notes",
            _notes(structured),
            "",
        ]
    )


def _load_seed(project_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    _require_file(project_dir / "workflow_seed.md")
    real_brief_dir = project_dir / "real_brief"
    adapter_manifest = _read_json(
        _require_file(real_brief_dir / "adapter_manifest.json")
    )
    structured = _read_json(_require_file(real_brief_dir / "structured_brief.json"))
    handoff = _read_json(_require_file(real_brief_dir / "workflow_handoff.json"))
    return adapter_manifest, structured, handoff


def _assert_ready_seed(
    adapter_manifest: dict[str, Any],
    structured: dict[str, Any],
    handoff: dict[str, Any],
) -> None:
    status = adapter_manifest.get("workflow_status")
    if status != "ready_for_visual_brainstorm":
        raise RuntimeError(
            f"real brief seed is not ready_for_visual_brainstorm: {status}"
        )
    if adapter_manifest.get("human_gate_required") is not True:
        raise ValueError("adapter_manifest.human_gate_required must be true")
    if handoff.get("human_gate_required") is not True:
        raise ValueError("workflow_handoff.human_gate_required must be true")

    domain = str(
        structured.get("domain")
        or handoff.get("visual_brainstorm_seed", {}).get("domain")
        or adapter_manifest.get("visual_workflow_domain")
        or ""
    )
    if domain not in SUPPORTED_STATIC_VISUAL_DOMAINS:
        raise RuntimeError(f"unsupported visual brainstorm domain: {domain}")


def _assert_can_write(proposal_path: Path, force: bool) -> None:
    if not proposal_path.exists():
        return

    status = _status_from_markdown(proposal_path)
    if status == "ready":
        raise RuntimeError(f"already finalized at {proposal_path}")
    if not force:
        raise RuntimeError(
            f"{proposal_path} already exists; pass force=True to overwrite"
        )


def seed_real_brief_brainstorm_proposal(
    *,
    root: str | Path,
    slug: str,
    date: str,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, str]:
    """Write a draft /visual-brainstorm proposal from an adapted real brief seed."""
    safe = safe_slug(slug)
    safe_date = _safe_date(date)
    root_path = Path(root)
    project_dir = _project_dir(root_path, safe)
    proposal_path = project_dir / "proposal.md"

    adapter_manifest, structured, handoff = _load_seed(project_dir)
    _assert_ready_seed(adapter_manifest, structured, handoff)
    _assert_can_write(proposal_path, force)

    result = {
        "slug": safe,
        "status": "draft",
        "project_dir": str(project_dir),
        "proposal_md": str(proposal_path),
    }
    if dry_run:
        result["dry_run"] = "true"
        return result

    proposal_path.write_text(
        _proposal_markdown(
            project_dir=project_dir,
            structured=structured,
            handoff=handoff,
            date=safe_date,
        ),
        encoding="utf-8",
    )
    return result
