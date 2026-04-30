"""Dry-run harness for the cultural-term efficacy experiment."""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
from dataclasses import dataclass, replace
from datetime import date as date_type
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "true")

from vulca.discovery.cards import generate_direction_cards
from vulca.discovery.profile import infer_taste_profile
from vulca.discovery.prompting import compose_prompt_from_direction_card
from vulca.discovery.types import DirectionCard, TasteProfile
from vulca.providers.openai_provider import OpenAIImageProvider


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


def _taste_profile_for_project(project: ExperimentProject) -> TasteProfile:
    profile = infer_taste_profile(
        slug=project.slug,
        intent=f"{project.prompt}; {'; '.join(project.tradition_terms)}",
    )
    if profile.culture_terms:
        return profile
    return replace(
        profile,
        culture_terms=list(project.tradition_terms),
        confidence="med",
    )


def select_direction_card(project: ExperimentProject) -> DirectionCard:
    profile = _taste_profile_for_project(project)
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


def _sanitize_base_url(base_url: str) -> str:
    raw = (base_url or "").strip()
    if not raw:
        return ""
    if any(char.isspace() or ord(char) < 32 for char in raw):
        raise RuntimeError(
            "VULCA_REAL_PROVIDER_BASE_URL must be a valid absolute http(s) URL."
        )
    parsed = urlsplit(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RuntimeError(
            "VULCA_REAL_PROVIDER_BASE_URL must be a valid absolute http(s) URL."
        )
    hostname = parsed.hostname
    if not hostname:
        raise RuntimeError(
            "VULCA_REAL_PROVIDER_BASE_URL must be a valid absolute http(s) URL."
        )
    if hostname:
        netloc = f"[{hostname}]" if ":" in hostname else hostname
        try:
            port = parsed.port
        except ValueError as exc:
            raise RuntimeError(
                "VULCA_REAL_PROVIDER_BASE_URL must include a valid port."
            ) from exc
        if port:
            netloc = f"{netloc}:{port}"
    return urlunsplit((parsed.scheme, netloc, "", "", "")).rstrip("/")


def _real_provider_config() -> dict[str, str]:
    api_key = os.environ.get("VULCA_REAL_PROVIDER_API_KEY") or os.environ.get(
        "OPENAI_API_KEY"
    )
    if not api_key:
        raise RuntimeError(
            "Real provider execution requires VULCA_REAL_PROVIDER_API_KEY "
            "or OPENAI_API_KEY."
        )
    base_url = (
        os.environ.get("VULCA_REAL_PROVIDER_BASE_URL")
        or os.environ.get("VULCA_OPENAI_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or ""
    )
    model = os.environ.get("VULCA_REAL_PROVIDER_MODEL") or "gpt-image-2"
    return {
        "api_key": api_key,
        "base_url": _sanitize_base_url(base_url),
        "model": model,
    }


def _decode_image_bytes(image_b64: str) -> bytes:
    if not image_b64:
        raise RuntimeError("provider returned an empty image payload")
    return base64.b64decode(image_b64)


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


async def _write_openai_real_provider_run(
    output_root: str | Path,
    slug: str,
    date: str | None,
    config: dict[str, str],
) -> dict[str, str]:
    result = write_experiment_dry_run(
        output_root=output_root,
        slug=slug,
        date=date,
    )
    out_dir = Path(result["output_dir"])
    images_dir = out_dir / "images"
    project = get_experiment_project(slug)
    card = select_direction_card(project)
    conditions = build_conditions(project.prompt, card)
    provider = OpenAIImageProvider(
        api_key=config["api_key"],
        model=config["model"],
        base_url=config["base_url"],
    )

    image_records: list[dict[str, Any]] = []
    cost_records: list[dict[str, Any]] = []
    total_usd = 0.0
    for condition in conditions:
        condition_id = condition["id"]
        image_path = images_dir / f"{condition_id}.png"
        image_result = await provider.generate(
            prompt=condition["prompt"],
            raw_prompt=True,
            width=1024,
            height=1024,
            output_format="png",
            negative_prompt=condition["negative_prompt"],
        )
        image_path.write_bytes(_decode_image_bytes(image_result.image_b64))
        metadata = image_result.metadata or {}
        image_records.append(
            {
                "id": condition_id,
                "image_path": f"images/{condition_id}.png",
                "mime": image_result.mime,
                "metadata": metadata,
            }
        )
        cost_usd = metadata.get("cost_usd")
        if isinstance(cost_usd, (int, float)):
            total_usd += float(cost_usd)
            cost_records.append(
                {
                    "condition_id": condition_id,
                    "cost_usd": float(cost_usd),
                }
            )

    _write_json(
        images_dir / "metadata.json",
        {
            "schema_version": "0.1",
            "provider": "openai",
            "model": config["model"],
            "conditions": image_records,
        },
    )
    _write_json(
        out_dir / "provider_costs.json",
        {
            "schema_version": "0.1",
            "status": "collected" if cost_records else "unavailable",
            "providers": [
                {
                    "provider": "openai",
                    "model": config["model"],
                    "base_url": config["base_url"],
                    "conditions": cost_records,
                }
            ],
            "total_usd": round(total_usd, 6),
        },
    )
    (images_dir / "README.md").write_text(
        "# Images\n\n"
        "Real provider run. Images A-D were generated through the configured "
        "OpenAI-compatible provider. See `metadata.json` for provider metadata.\n",
        encoding="utf-8",
    )

    manifest_path = out_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["mode"] = "real_provider"
    manifest["provider_execution"] = "enabled"
    manifest["real_provider"] = {
        "provider": "openai",
        "model": config["model"],
        "base_url": config["base_url"],
    }
    for provider_record in manifest["providers"]:
        if provider_record["provider"] == "openai":
            provider_record["execution"] = "run"
            provider_record["model"] = config["model"]
    _write_json(manifest_path, manifest)

    summary = f"""# Cultural-Term Efficacy Real Provider Run: {project.slug}

## Status
real_provider

## Provider Execution
enabled

## Provider
openai / {config["model"]}

## Conditions
{chr(10).join(f"- {item['id']}: {item['label']}" for item in conditions)}

## Generated Images
{chr(10).join(f"- {item['id']}: {item['image_path']}" for item in image_records)}

## Decision Boundary
Images were generated, but no quality conclusion can be drawn until human
ranking and `/evaluate` results are collected.
"""
    (out_dir / "summary.md").write_text(summary, encoding="utf-8")
    return result


def run_real_provider_experiment(
    *,
    real_provider: bool = False,
    provider: str = "openai",
    output_root: str | Path = "docs/product/experiments/results",
    slug: str = "premium-tea-packaging",
    date: str | None = None,
) -> dict[str, str]:
    if not real_provider:
        raise RuntimeError(
            "Real provider execution requires explicit opt-in and is disabled "
            "for the dry-run harness."
        )
    if provider != "openai":
        raise ValueError("supported real provider: openai")
    config = _real_provider_config()
    return asyncio.run(
        _write_openai_real_provider_run(
            output_root=output_root,
            slug=slug,
            date=date,
            config=config,
        )
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
    parser.add_argument("--provider", default="openai")
    args = parser.parse_args(argv)

    if args.real_provider:
        projects = build_experiment_projects()
        slugs = [
            project.slug for project in projects
        ] if args.slug == "all" else [args.slug]
        for slug in slugs:
            run_real_provider_experiment(
                real_provider=True,
                provider=args.provider,
                output_root=args.output_root,
                slug=slug,
                date=args.date,
            )
        return 0

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
