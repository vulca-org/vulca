"""Dry-run artifact writing for the real-brief benchmark."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from vulca.real_brief.conditions import build_real_brief_conditions
from vulca.real_brief.fixtures import get_real_brief_fixture
from vulca.real_brief.types import CONDITION_IDS, REVIEW_DIMENSIONS, safe_slug


_CONDITION_FILENAMES = {
    "A": "A-one-shot.md",
    "B": "B-structured-brief.md",
    "C": "C-vulca-planning.md",
    "D": "D-vulca-preview-iterate.md",
}
_RUN_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _safe_run_date(date: str) -> str:
    if not _RUN_DATE_RE.fullmatch(date):
        raise ValueError("run date must use YYYY-MM-DD")
    return date


def _condition_markdown(condition: dict[str, Any]) -> str:
    return "\n\n".join(
        [
            f"# Condition {condition['id']}: {condition['label']}",
            f"workflow_stage: {condition['workflow_stage']}",
            f"purpose: {condition['purpose']}",
            "## Prompt",
            condition["prompt"],
        ]
    ) + "\n"


def _summary_markdown(fixture_slug: str, date: str, condition_count: int) -> str:
    return "\n".join(
        [
            f"# Real Brief Dry Run: {fixture_slug}",
            "",
            f"date: {date}",
            "simulation_only: true",
            f"condition_count: {condition_count}",
            "",
            "No image quality conclusion is made by this dry run.",
            "It writes benchmark prompts, handoff data, and review scaffolding only.",
            "",
        ]
    )


def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _deliverable_list(fixture: Any) -> str:
    return "\n".join(
        f"- {item.name} ({item.format}, {item.channel})"
        for item in fixture.deliverables
    )


def _missing_questions() -> list[str]:
    return [
        "Which stakeholder approves the final direction?",
        "Which deliverable must be most production-ready first?",
        "Which source assets already exist?",
    ]


def _physical_form(fixture: Any) -> str:
    return fixture.deliverables[0].name if fixture.deliverables else fixture.domain


def _condition_paths(condition: dict[str, Any]) -> dict[str, str]:
    condition_id = condition["id"]
    return {
        "condition_path": f"conditions/{_CONDITION_FILENAMES[condition_id]}",
        "prompt_path": f"prompts/{condition_id}.txt",
    }


def _condition_manifest(conditions: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "id": condition["id"],
            "label": condition["label"],
            "purpose": condition["purpose"],
            **_condition_paths(condition),
        }
        for condition in conditions
    ]


def _selected_card(conditions: list[dict[str, Any]]) -> dict[str, Any]:
    for condition in conditions:
        if condition.get("selected_direction_card"):
            return condition["selected_direction_card"]
    return {}


def _decision_package(fixture: Any, conditions: list[dict[str, Any]]) -> str:
    selected = _selected_card(conditions)
    directions = conditions[2].get("direction_cards", []) if len(conditions) > 2 else []
    direction_lines = [
        f"- {card['label']}: {card['summary']}" for card in directions
    ] or ["- Direction cards are unavailable in this dry run."]
    checklist = [
        "Required deliverables represented",
        "Constraints acknowledged",
        "Known risks documented",
        "Human approval required before provider execution",
    ]
    return "\n\n".join(
        [
            f"# Decision Package: {fixture.title}",
            "## Brief Digest",
            "\n".join(
                [
                    f"Client: {fixture.client}",
                    f"Domain: {fixture.domain}",
                    f"Context: {fixture.context}",
                    "Audience:",
                    _bullet_list(fixture.audience),
                    "Deliverables:",
                    _deliverable_list(fixture),
                    "Constraints:",
                    _bullet_list(fixture.constraints),
                ]
            ),
            "## Assumptions",
            _bullet_list(
                [
                    "This package is a simulation-only planning artifact.",
                    "No image provider is invoked by this dry run.",
                    "Final production requires a human gate and source-asset review.",
                ]
            ),
            "## Missing Questions",
            _bullet_list(_missing_questions()),
            "## Creative Directions",
            "\n".join(direction_lines),
            "## Direction Rationale",
            selected.get("summary", "Use the strongest generated direction card."),
            "## Risks And Rejected Approaches",
            "\n".join(
                [
                    "Risks:",
                    _bullet_list(fixture.risks),
                    "Rejected approaches:",
                    _bullet_list(fixture.avoid),
                ]
            ),
            "## Recommended Direction",
            selected.get("label", conditions[0]["label"]),
            "## Decision Checklist",
            _bullet_list(checklist),
        ]
    ) + "\n"


def _production_package(fixture: Any, conditions: list[dict[str, Any]]) -> str:
    selected = _selected_card(conditions)
    visual_ops = selected.get("visual_ops", {})
    visual_ops_lines = [
        f"- {key.replace('_', ' ').title()}: {value}"
        for key, value in visual_ops.items()
    ] or ["- Use condition C/D visual operation notes."]
    prompt_paths = [
        f"- Condition {condition['id']}: {_condition_paths(condition)['prompt_path']}"
        for condition in conditions
    ]
    return "\n\n".join(
        [
            f"# Production Package: {fixture.title}",
            "## Selected Direction",
            selected.get("label", conditions[0]["label"]),
            "## Prompt Packet",
            "\n".join(prompt_paths),
            "## Visual Operations",
            "\n".join(visual_ops_lines),
            "## Layout And Structure Constraints",
            _bullet_list(fixture.constraints),
            "## Channel And Deliverable Constraints",
            _deliverable_list(fixture),
            "## Preview Or Thumbnail Plan",
            _bullet_list(
                [
                    "Produce 2-3 low-cost thumbnail directions before final comp.",
                    "Critique thumbnails against constraints, risks, and deliverables.",
                    "Refine the strongest route into a final comp prompt.",
                ]
            ),
            "## Evaluation Checklist",
            _bullet_list(fixture.evaluation_dimensions),
            "## Editability And Reusability Notes",
            _bullet_list(
                [
                    "Document reusable components before final execution.",
                    "Keep source constraints visible in the handoff package.",
                ]
            ),
            "## Redraw And Layer Notes",
            _bullet_list(
                [
                    "No redraw or mask provider runs in dry-run mode.",
                    "Layer decisions should wait for explicit real-provider opt-in.",
                ]
            ),
            "## Next Iteration Plan",
            _bullet_list(
                [
                    "Review human scoring schema.",
                    "Select one direction for Task 5 review rendering.",
                    "Proceed only after the human gate is cleared.",
                ]
            ),
        ]
    ) + "\n"


def _workflow_handoff(fixture: Any, conditions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "slug": fixture.slug,
        "structured_brief_path": "structured_brief.json",
        "human_gate_required": True,
        "simulation_only": True,
        "fixture_slug": fixture.slug,
        "condition_ids": [condition["id"] for condition in conditions],
        "visual_discovery_seed": {
            "slug": fixture.slug,
            "title": fixture.title,
            "initial_intent": fixture.source_brief or fixture.context,
            "domain": fixture.domain,
            "tags": list(fixture.tags),
            "source_usage_note": fixture.source.usage_note,
        },
        "visual_brainstorm_seed": {
            "slug": fixture.slug,
            "domain": fixture.domain,
            "physical_form": _physical_form(fixture),
            "constraints": list(fixture.constraints),
            "client": fixture.client,
            "audience": list(fixture.audience),
            "deliverables": [item.to_dict() for item in fixture.deliverables],
            "risks": list(fixture.risks),
            "avoid": list(fixture.avoid),
        },
        "visual_spec_seed": {
            "evaluation_dimensions": list(fixture.evaluation_dimensions),
            "provider_policy": "dry_run_default",
        },
        "visual_plan_seed": {
            "condition_ids": [condition["id"] for condition in conditions],
            "requires_explicit_real_provider_opt_in": True,
        },
        "evaluate_seed": {
            "review_schema_path": "review_schema.json",
            "mode": "brief_compliance",
        },
    }


def _review_schema() -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "scale": {"min": 0, "max": 2, "step": 1},
        "condition_ids": list(CONDITION_IDS),
        "dimensions": [
            {
                "id": dimension,
                "label": dimension.replace("_", " "),
            }
            for dimension in REVIEW_DIMENSIONS
        ],
    }


def _write_html_review(out_dir: Path) -> None:
    try:
        from vulca.real_brief.review_html import write_review_html
    except ModuleNotFoundError as exc:
        if exc.name != "vulca.real_brief.review_html":
            raise
        _write_text(
            out_dir / "human_review.html",
            "\n".join(
                [
                    "<!doctype html>",
                    "<html><head><meta charset=\"utf-8\"><title>Human Review</title></head>",
                    "<body>",
                    "<h1>Full renderer pending</h1>",
                    "<p>Task 5 will provide the full review renderer.</p>",
                    "<p>Use <a href=\"manifest.json\">manifest.json</a> and "
                    "<a href=\"review_schema.json\">review_schema.json</a> for "
                    "this dry-run review.</p>",
                    "</body></html>",
                    "",
                ]
            ),
        )
        return

    write_review_html(out_dir)


def write_real_brief_dry_run(
    output_root: str | Path,
    slug: str,
    date: str,
    write_html_review: bool = True,
) -> dict[str, str]:
    """Write dry-run benchmark artifacts without invoking image providers."""
    fixture = get_real_brief_fixture(safe_slug(slug))
    conditions = build_real_brief_conditions(fixture)
    safe_date = _safe_run_date(date)
    output_root_path = Path(output_root)
    out_dir = output_root_path / f"{safe_date}-{fixture.slug}"
    out_dir.mkdir(parents=True, exist_ok=True)

    structured_brief = fixture.to_dict()
    decision_package = _decision_package(fixture, conditions)
    production_package = _production_package(fixture, conditions)

    written_files = [
        "source_brief.md",
        "structured_brief.json",
        "decision_package.md",
        "production_package.md",
        "workflow_handoff.json",
        "review_schema.json",
        "summary.md",
        "manifest.json",
    ]

    _write_text(out_dir / "source_brief.md", fixture.source_brief + "\n")
    _write_json(out_dir / "structured_brief.json", structured_brief)
    _write_text(out_dir / "decision_package.md", decision_package)
    _write_text(out_dir / "production_package.md", production_package)
    _write_json(out_dir / "workflow_handoff.json", _workflow_handoff(fixture, conditions))
    _write_json(out_dir / "review_schema.json", _review_schema())

    for condition in conditions:
        condition_id = condition["id"]
        paths = _condition_paths(condition)
        condition_rel = paths["condition_path"]
        prompt_rel = paths["prompt_path"]
        _write_text(out_dir / condition_rel, _condition_markdown(condition))
        _write_text(out_dir / prompt_rel, condition["prompt"] + "\n")
        written_files.extend([condition_rel, prompt_rel])

    _write_text(
        out_dir / "images/README.md",
        "# Images\n\nDry-run placeholder. No images are generated here.\n",
    )
    _write_text(
        out_dir / "evaluations/README.md",
        "# Evaluations\n\nDry-run placeholder. No image evaluations are run here.\n",
    )
    written_files.extend(["images/README.md", "evaluations/README.md"])

    summary = _summary_markdown(fixture.slug, safe_date, len(conditions))
    _write_text(out_dir / "summary.md", summary)
    if write_html_review:
        written_files.append("human_review.html")

    manifest = {
        "schema_version": "0.1",
        "experiment": "real-brief-benchmark",
        "mode": "dry_run",
        "provider_execution": "disabled",
        "fixture": {
            "slug": fixture.slug,
            "title": fixture.title,
        },
        "conditions": _condition_manifest(conditions),
        "review_schema_path": "review_schema.json",
        "workflow_handoff_path": "workflow_handoff.json",
        "fixture_slug": fixture.slug,
        "date": safe_date,
        "simulation_only": True,
        "condition_ids": [condition["id"] for condition in conditions],
        "files": sorted(written_files),
    }
    _write_json(out_dir / "manifest.json", manifest)
    if write_html_review:
        _write_html_review(out_dir)

    return {
        "output_dir": str(out_dir),
        "manifest_json": str(out_dir / "manifest.json"),
        "summary_md": str(out_dir / "summary.md"),
    }
