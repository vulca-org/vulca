"""Dry-run artifact writing for the real-brief benchmark."""
from __future__ import annotations

import json
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


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


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


def _workflow_handoff(fixture: Any, conditions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "human_gate_required": True,
        "simulation_only": True,
        "fixture_slug": fixture.slug,
        "condition_ids": [condition["id"] for condition in conditions],
        "visual_discovery_seed": {
            "slug": fixture.slug,
            "title": fixture.title,
            "domain": fixture.domain,
            "tags": list(fixture.tags),
            "source_usage_note": fixture.source.usage_note,
        },
        "visual_brainstorm_seed": {
            "slug": fixture.slug,
            "domain": fixture.domain,
            "client": fixture.client,
            "audience": list(fixture.audience),
            "deliverables": [item.to_dict() for item in fixture.deliverables],
            "constraints": list(fixture.constraints),
            "risks": list(fixture.risks),
            "avoid": list(fixture.avoid),
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


def write_real_brief_dry_run(
    output_root: str | Path,
    slug: str,
    date: str,
    write_html_review: bool = True,
) -> dict[str, str]:
    """Write dry-run benchmark artifacts without invoking image providers."""
    fixture = get_real_brief_fixture(safe_slug(slug))
    conditions = build_real_brief_conditions(fixture)
    output_root_path = Path(output_root)
    out_dir = output_root_path / f"{date}-{fixture.slug}"
    out_dir.mkdir(parents=True, exist_ok=True)

    structured_brief = fixture.to_dict()
    decision_package = "\n\n".join(
        [
            f"# Decision Package: {fixture.title}",
            f"Client: {fixture.client}",
            f"Domain: {fixture.domain}",
            "## Risks",
            "\n".join(f"- {item}" for item in fixture.risks),
            "## Avoid",
            "\n".join(f"- {item}" for item in fixture.avoid),
        ]
    ) + "\n"
    production_package = "\n\n".join(
        [
            f"# Production Package: {fixture.title}",
            "## Deliverables",
            "\n".join(
                f"- {item.name} ({item.format}, {item.channel})"
                for item in fixture.deliverables
            ),
            "## Constraints",
            "\n".join(f"- {item}" for item in fixture.constraints),
            f"Timeline: {fixture.timeline}",
            f"Budget: {fixture.budget}",
        ]
    ) + "\n"

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
        condition_rel = f"conditions/{_CONDITION_FILENAMES[condition_id]}"
        prompt_rel = f"prompts/{condition_id}.txt"
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

    summary = _summary_markdown(fixture.slug, date, len(conditions))
    _write_text(out_dir / "summary.md", summary)
    manifest = {
        "schema_version": "0.1",
        "fixture_slug": fixture.slug,
        "date": date,
        "simulation_only": True,
        "condition_ids": [condition["id"] for condition in conditions],
        "files": sorted(written_files),
    }
    _write_json(out_dir / "manifest.json", manifest)

    if write_html_review:
        from vulca.real_brief.review_html import write_review_html

        write_review_html(out_dir)

    return {
        "output_dir": str(out_dir),
        "manifest_json": str(out_dir / "manifest.json"),
        "summary_md": str(out_dir / "summary.md"),
    }
