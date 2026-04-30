"""Dry-run harness for the cultural-term efficacy experiment."""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import date as date_type
from pathlib import Path
from typing import Any

os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "true")

from vulca.discovery.cards import generate_direction_cards
from vulca.discovery.profile import infer_taste_profile
from vulca.discovery.prompting import compose_prompt_from_direction_card
from vulca.discovery.types import DirectionCard


PROVIDERS = [
    {
        "label": "OpenAI GPT Image",
        "provider": "openai",
        "model": "gpt-image-2",
    },
    {
        "label": "Gemini image",
        "provider": "gemini",
        "model": "gemini-3.1-flash-image-preview",
    },
    {"label": "ComfyUI", "provider": "comfyui", "model": ""},
]


@dataclass(frozen=True)
class ExperimentProject:
    slug: str
    prompt: str
    domain: str
    tradition_terms: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "prompt": self.prompt,
            "domain": self.domain,
            "tradition_terms": list(self.tradition_terms),
        }


def build_experiment_projects() -> list[ExperimentProject]:
    return [
        ExperimentProject(
            slug="premium-tea-packaging",
            prompt="premium tea packaging with xieyi restraint",
            domain="packaging",
            tradition_terms=("chinese_xieyi", "liu bai", "ink restraint"),
        ),
        ExperimentProject(
            slug="spiritual-editorial-poster",
            prompt="editorial poster with spiritual but non-religious atmosphere",
            domain="editorial poster",
            tradition_terms=("sacred atmosphere", "quiet symbolism", "restraint"),
        ),
        ExperimentProject(
            slug="cultural-material-campaign",
            prompt=(
                "product campaign visual with culturally specific material "
                "references"
            ),
            domain="campaign visual",
            tradition_terms=("material culture", "specific craft", "local texture"),
        ),
    ]


def get_experiment_project(slug: str) -> ExperimentProject:
    for project in build_experiment_projects():
        if project.slug == slug:
            return project
    known = ", ".join(project.slug for project in build_experiment_projects())
    raise ValueError(f"unknown project slug: {slug!r}; expected one of: {known}")


def select_direction_card(project: ExperimentProject) -> DirectionCard:
    profile = infer_taste_profile(
        slug=project.slug,
        intent=f"{project.prompt}; {'; '.join(project.tradition_terms)}",
    )
    return generate_direction_cards(profile, count=3)[0]


def _visual_ops_text(card: DirectionCard) -> str:
    ops = card.visual_ops
    return "; ".join(
        part
        for part in [
            ops.composition,
            ops.color,
            ops.texture,
            ops.lighting,
            ops.camera,
            ops.typography,
            ops.symbol_strategy,
        ]
        if part
    )


def build_conditions(base_prompt: str, card: DirectionCard) -> list[dict[str, Any]]:
    raw_terms = ", ".join(card.culture_terms)
    visual_ops = _visual_ops_text(card)
    compiled = compose_prompt_from_direction_card(card, target="final")
    return [
        {
            "id": "A",
            "label": "User prompt only",
            "prompt": base_prompt,
            "negative_prompt": "",
            "source_card_id": "",
            "culture_terms": [],
            "evaluation_focus": {},
        },
        {
            "id": "B",
            "label": "User prompt + cultural terms",
            "prompt": f"{base_prompt}. Cultural terms: {raw_terms}",
            "negative_prompt": "",
            "source_card_id": card.id,
            "culture_terms": list(card.culture_terms),
            "evaluation_focus": {},
        },
        {
            "id": "C",
            "label": "User prompt + cultural terms + visual operations",
            "prompt": (
                f"{base_prompt}. Cultural terms: {raw_terms}. "
                f"Visual operations: {visual_ops}"
            ),
            "negative_prompt": "",
            "source_card_id": card.id,
            "culture_terms": list(card.culture_terms),
            "evaluation_focus": {},
        },
        {
            "id": "D",
            "label": "Full direction-card prompt",
            "prompt": compiled.prompt,
            "negative_prompt": compiled.negative_prompt,
            "source_card_id": card.id,
            "culture_terms": list(card.culture_terms),
            "evaluation_focus": card.evaluation_focus.to_dict(),
        },
    ]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _provider_records() -> list[dict[str, str]]:
    return [
        {
            "label": provider["label"],
            "provider": provider["provider"],
            "model": provider["model"],
            "execution": "not_run",
        }
        for provider in PROVIDERS
    ]


def write_experiment_dry_run(
    *,
    output_root: str | Path,
    slug: str,
    date: str | None = None,
) -> dict[str, str]:
    project = get_experiment_project(slug)
    card = select_direction_card(project)
    conditions = build_conditions(project.prompt, card)
    run_date = date or date_type.today().isoformat()
    out_dir = Path(output_root) / f"{run_date}-{project.slug}"
    prompts_dir = out_dir / "prompts"
    images_dir = out_dir / "images"
    evaluations_dir = out_dir / "evaluations"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    evaluations_dir.mkdir(parents=True, exist_ok=True)

    for condition in conditions:
        prompt_text = condition["prompt"]
        if condition["negative_prompt"]:
            prompt_text += f"\n\nNegative prompt:\n{condition['negative_prompt']}"
        if condition["evaluation_focus"]:
            prompt_text += "\n\nEvaluation focus:\n" + json.dumps(
                condition["evaluation_focus"],
                ensure_ascii=False,
                indent=2,
            )
        (prompts_dir / f"{condition['id']}.txt").write_text(
            prompt_text + "\n",
            encoding="utf-8",
        )

    images_readme = (
        "# Images\n\n"
        "Dry run only. Real provider images are not generated by this harness.\n"
    )
    evaluations_readme = (
        "# Evaluations\n\n"
        "Dry run only. Run `/evaluate` after real images exist.\n"
    )
    (images_dir / "README.md").write_text(images_readme, encoding="utf-8")
    (evaluations_dir / "README.md").write_text(
        evaluations_readme,
        encoding="utf-8",
    )

    _write_json(
        out_dir / "human_ranking.json",
        {
            "schema_version": "0.1",
            "status": "not_collected",
            "rankings": [],
        },
    )
    _write_json(
        out_dir / "provider_costs.json",
        {
            "schema_version": "0.1",
            "status": "not_collected",
            "providers": [],
            "total_usd": 0,
        },
    )

    manifest_conditions = [
        {
            "id": condition["id"],
            "label": condition["label"],
            "prompt_path": f"prompts/{condition['id']}.txt",
            "source_card_id": condition["source_card_id"],
        }
        for condition in conditions
    ]
    manifest = {
        "schema_version": "0.1",
        "experiment": "cultural-term-efficacy",
        "mode": "dry_run",
        "provider_execution": "disabled",
        "project": project.to_dict(),
        "selected_card_id": card.id,
        "conditions": manifest_conditions,
        "providers": _provider_records(),
    }
    _write_json(out_dir / "manifest.json", manifest)

    summary = f"""# Cultural-Term Efficacy Dry Run: {project.slug}

## Status
dry_run

## Provider Execution
disabled

## Project
{project.prompt}

## Conditions
{chr(10).join(f"- {item['id']}: {item['label']}" for item in conditions)}

## Decision Boundary
No image quality conclusion can be drawn from this dry run. It validates prompts,
metadata, and result structure only.
"""
    (out_dir / "summary.md").write_text(summary, encoding="utf-8")

    return {
        "output_dir": str(out_dir),
        "manifest_json": str(out_dir / "manifest.json"),
        "summary_md": str(out_dir / "summary.md"),
    }


def run_real_provider_experiment(*, real_provider: bool = False) -> None:
    if not real_provider:
        raise RuntimeError(
            "Real provider execution requires explicit opt-in and is disabled "
            "for the dry-run harness."
        )
    raise NotImplementedError(
        "Real provider execution is intentionally not implemented in this "
        "harness version."
    )


def write_dry_run_report(path: str | Path) -> str:
    provider_lines = "\n".join(
        f"- {item['label']}: provider={item['provider']} "
        f"model={item['model'] or 'default'}"
        for item in PROVIDERS
    )
    report = f"""# Cultural-Term Efficacy Harness Dry Run

## Providers
{provider_lines}

## Conditions
- A: user prompt only
- B: user prompt + cultural terms
- C: user prompt + cultural terms + visual operations
- D: full direction-card prompt with avoid list and evaluation focus

No image quality conclusion can be drawn from this dry run.
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(report, encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write cultural-term efficacy dry-run artifacts."
    )
    parser.add_argument("--slug", default="all")
    parser.add_argument(
        "--output-root",
        default="docs/product/experiments/results",
    )
    parser.add_argument("--date", default=date_type.today().isoformat())
    parser.add_argument("--real-provider", action="store_true")
    args = parser.parse_args(argv)

    if args.real_provider:
        run_real_provider_experiment(real_provider=True)

    projects = build_experiment_projects()
    slugs = [project.slug for project in projects] if args.slug == "all" else [args.slug]
    for slug in slugs:
        write_experiment_dry_run(
            output_root=args.output_root,
            slug=slug,
            date=args.date,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
