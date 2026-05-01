"""Adapter from real-brief dry-run packages into visual workflow seeds."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from vulca.discovery.artifacts import write_discovery_artifacts
from vulca.discovery.cards import generate_direction_cards
from vulca.discovery.profile import infer_taste_profile
from vulca.discovery.prompting import compose_prompt_from_direction_card
from vulca.discovery.types import SketchPrompt
from vulca.real_brief.types import safe_slug


SUPPORTED_STATIC_VISUAL_DOMAINS = {
    "poster",
    "packaging",
    "brand_visual",
    "illustration",
    "editorial_cover",
    "photography_brief",
    "hero_visual_for_ui",
}

_RUN_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SOURCE_FILES = [
    "structured_brief.json",
    "workflow_handoff.json",
    "decision_package.md",
    "production_package.md",
    "review_schema.json",
    "source_brief.md",
    "summary.md",
    "human_review.html",
]
_SOURCE_DIRS = ["conditions", "prompts", "images", "evaluations"]
_REQUIRED_SOURCE_FILES = [
    "manifest.json",
    "workflow_handoff.json",
    "structured_brief.json",
    "decision_package.md",
    "production_package.md",
    "review_schema.json",
]
_FINALIZED_STATUSES = {
    "proposal.md": {"ready"},
    "design.md": {"resolved"},
    "plan.md": {"completed", "partial", "aborted"},
}
_STATUS_RE = re.compile(r"(?im)^\s*status\s*:\s*([a-z0-9_-]+)\s*$")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _safe_date(date: str) -> str:
    if not _RUN_DATE_RE.fullmatch(date):
        raise ValueError("date must use YYYY-MM-DD")
    return date


def _project_dir(root: Path, slug: str) -> Path:
    return root / "docs" / "visual-specs" / slug


def _status_from_markdown(path: Path) -> str:
    match = _STATUS_RE.search(path.read_text(encoding="utf-8"))
    return match.group(1).lower() if match else ""


def _load_source_package(
    source_package: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    for filename in _REQUIRED_SOURCE_FILES:
        path = source_package / filename
        if not path.exists():
            raise FileNotFoundError(f"required source package file missing: {path}")

    manifest_path = source_package / "manifest.json"
    structured_path = source_package / "structured_brief.json"
    handoff_path = source_package / "workflow_handoff.json"
    manifest = _read_json(manifest_path)
    structured = _read_json(structured_path)
    handoff = _read_json(handoff_path)
    if manifest.get("schema_version") != "0.1":
        raise ValueError("manifest.schema_version must be 0.1")
    if manifest.get("experiment") != "real-brief-benchmark":
        raise ValueError("source package is not a real-brief benchmark package")
    if manifest.get("mode") != "dry_run":
        raise ValueError("source package must be a dry-run package")
    if manifest.get("provider_execution") != "disabled":
        raise ValueError("manifest.provider_execution must be disabled")
    if handoff.get("schema_version") != "0.1":
        raise ValueError("workflow_handoff.schema_version must be 0.1")
    if handoff.get("human_gate_required") is not True:
        raise ValueError("workflow_handoff.human_gate_required must be true")

    slugs = {
        "manifest.fixture.slug": manifest.get("fixture", {}).get("slug"),
        "workflow_handoff.slug": handoff.get("slug"),
        "structured_brief.slug": structured.get("slug"),
    }
    normalized = {key: safe_slug(str(value)) for key, value in slugs.items()}
    if len(set(normalized.values())) != 1:
        raise ValueError(f"source package slug mismatch: {normalized}")
    return manifest, structured, handoff


def _initial_intent(structured: dict[str, Any], handoff: dict[str, Any]) -> str:
    discovery_seed = handoff.get("visual_discovery_seed", {})
    return str(
        discovery_seed.get("initial_intent")
        or structured.get("source_brief")
        or structured.get("context")
        or structured.get("title")
        or ""
    )


def _build_sketch_prompts(cards: list[Any]) -> list[SketchPrompt]:
    prompts: list[SketchPrompt] = []
    for card in cards:
        prompt = compose_prompt_from_direction_card(card, target="sketch")
        prompts.append(
            SketchPrompt(
                card_id=card.id,
                provider=prompt.provider,
                model=prompt.model,
                prompt=prompt.prompt,
                negative_prompt=prompt.negative_prompt,
                size="1024x1024",
                purpose="visual workflow adapter discovery thumbnail seed",
            )
        )
    return prompts


def _next_steps(slug: str) -> list[str]:
    return [
        f"/visual-brainstorm {slug}",
        f"/visual-spec {slug}",
        f"/visual-plan {slug}",
        f"/evaluate {slug}",
    ]


def _adapter_manifest(
    *,
    slug: str,
    domain: str,
    date: str,
    source_manifest: dict[str, Any],
    status: str,
) -> dict[str, Any]:
    discovery_path = (
        "../discovery/discovery.md" if status == "ready_for_visual_brainstorm" else None
    )
    supported = status == "ready_for_visual_brainstorm"
    manifest = {
        "schema_version": "0.1",
        "adapter": "real-brief-workflow-adapter",
        "source_experiment": source_manifest.get("experiment"),
        "source_mode": source_manifest.get("mode"),
        "slug": slug,
        "workflow_status": status,
        "human_gate_required": True,
        "simulation_only": True,
        "domain": domain,
        "visual_workflow_domain": domain if supported else None,
        "created": date,
        "workflow_artifacts": {
            "discovery_md": discovery_path,
            "workflow_seed_md": "../workflow_seed.md",
        },
        "source_package_manifest": "source_package_manifest.json",
        "next_steps": _next_steps(slug) if supported else [],
    }
    if not supported:
        manifest["unsupported_reason"] = (
            "source domain is outside /visual-brainstorm static 2D scope"
        )
    return manifest


def _workflow_seed_md(
    *,
    slug: str,
    title: str,
    domain: str,
    source_package: Path,
    status: str,
) -> str:
    next_step_lines = [f"- {step}" for step in _next_steps(slug)]
    if status == "ready_for_visual_brainstorm":
        status_section = [
            "This file preserves the real-brief handoff context for the visual workflow.",
            "It is not a substitute for `proposal.md`; /visual-brainstorm must still "
            "create and resolve the human-reviewed proposal.",
            "",
            "## Human Gates",
            "- Review the copied real_brief source package before using any production workflow.",
            "- /visual-brainstorm must produce `proposal.md` and wait for human approval.",
            "- /visual-spec must resolve design.md before planning or generation.",
            "- /visual-plan must not execute production work without explicit human approval.",
            "",
            "## Suggested Next Steps",
            *next_step_lines,
        ]
    else:
        status_section = [
            "This file preserves the real-brief source context, but this domain is "
            "unsupported_for_visual_chain.",
            "The adapter stops here and does not start `/visual-brainstorm`.",
            "It is not a substitute for `proposal.md`.",
            "",
            "## Human Gates",
            "- Review the copied real_brief source package before choosing another workflow.",
            "- Choose a domain-specific workflow manually before any production work.",
        ]
    return "\n".join(
        [
            f"# Real Brief Workflow Seed: {title}",
            "",
            f"status: {status}",
            "human_gate_required: true",
            "simulation_only: true",
            f"slug: {slug}",
            f"domain: {domain}",
            f"source_package: {source_package}",
            "",
            *status_section,
            "",
        ]
    )


def _copy_source_package(source_package: Path, real_brief_dir: Path) -> None:
    real_brief_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        source_package / "manifest.json",
        real_brief_dir / "source_package_manifest.json",
    )
    for filename in _SOURCE_FILES:
        source = source_package / filename
        if source.exists():
            shutil.copy2(source, real_brief_dir / filename)
    for dirname in _SOURCE_DIRS:
        source_dir = source_package / dirname
        if source_dir.exists():
            target_dir = real_brief_dir / dirname
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(source_dir, target_dir)


def _assert_source_path_safe(source_package: Path, path: Path) -> None:
    if path.is_symlink():
        raise ValueError(f"source package path must not be a symlink: {path}")
    source_root = source_package.resolve()
    resolved = path.resolve(strict=True)
    if source_root != resolved and source_root not in resolved.parents:
        raise ValueError(f"source package path escapes package: {path}")


def _validate_copy_sources(source_package: Path) -> None:
    source_package_root = source_package.resolve()
    _assert_source_path_safe(source_package, source_package)
    for filename in ["manifest.json", *_SOURCE_FILES]:
        source = source_package / filename
        if source.exists() or source.is_symlink():
            _assert_source_path_safe(source_package_root, source)
    for dirname in _SOURCE_DIRS:
        source_dir = source_package / dirname
        if not source_dir.exists() and not source_dir.is_symlink():
            continue
        _assert_source_path_safe(source_package_root, source_dir)
        for child in source_dir.rglob("*"):
            _assert_source_path_safe(source_package_root, child)


def _assert_destination_can_write(
    *,
    project_dir: Path,
    status: str,
    force_discovery: bool,
    force_real_brief: bool,
) -> None:
    for filename, terminal_statuses in _FINALIZED_STATUSES.items():
        path = project_dir / filename
        if path.exists() and _status_from_markdown(path) in terminal_statuses:
            raise RuntimeError(
                f"refusing finalized workflow overwrite: {path} has terminal status"
            )

    if status == "ready_for_visual_brainstorm":
        discovery_dir = project_dir / "discovery"
        if discovery_dir.exists() and not force_discovery:
            raise RuntimeError(
                f"{discovery_dir} already exists; pass force_discovery=True to overwrite"
            )

    real_brief_dir = project_dir / "real_brief"
    if real_brief_dir.exists() and not force_real_brief:
        raise RuntimeError(
            f"{real_brief_dir} already exists; pass force_real_brief=True to overwrite"
        )


def adapt_real_brief_package(
    *,
    source_package: str | Path,
    root: str | Path,
    date: str,
    dry_run: bool = False,
    force_discovery: bool = False,
    force_real_brief: bool = False,
) -> dict[str, str]:
    """Adapt a real-brief dry-run package into visual workflow seed artifacts."""
    source_package_path = Path(source_package)
    root_path = Path(root)
    safe_date = _safe_date(date)
    if not source_package_path.exists():
        raise FileNotFoundError(f"source package not found: {source_package_path}")
    _validate_copy_sources(source_package_path)
    source_manifest, structured, handoff = _load_source_package(source_package_path)
    slug = safe_slug(str(structured.get("slug") or source_manifest.get("fixture_slug")))
    domain = str(
        structured.get("domain")
        or handoff.get("visual_discovery_seed", {}).get("domain")
        or ""
    )
    project_dir = _project_dir(root_path, slug)
    real_brief_dir = project_dir / "real_brief"
    discovery_md = project_dir / "discovery" / "discovery.md"
    workflow_seed_md = project_dir / "workflow_seed.md"
    adapter_manifest_json = real_brief_dir / "adapter_manifest.json"
    status = (
        "ready_for_visual_brainstorm"
        if domain in SUPPORTED_STATIC_VISUAL_DOMAINS
        else "unsupported_for_visual_chain"
    )

    result = {
        "slug": slug,
        "status": status,
        "project_dir": str(project_dir),
        "adapter_manifest_json": str(adapter_manifest_json),
        "workflow_seed_md": str(workflow_seed_md),
    }
    if status == "ready_for_visual_brainstorm":
        result.update(
            {
                "discovery_md": str(discovery_md),
            }
        )
    if dry_run:
        result["dry_run"] = "true"
        return result

    title = str(structured.get("title") or slug)
    _assert_destination_can_write(
        project_dir=project_dir,
        status=status,
        force_discovery=force_discovery,
        force_real_brief=force_real_brief,
    )
    if status != "ready_for_visual_brainstorm":
        _copy_source_package(source_package_path, real_brief_dir)
        _write_json(
            adapter_manifest_json,
            _adapter_manifest(
                slug=slug,
                domain=domain,
                date=safe_date,
                source_manifest=source_manifest,
                status=status,
            ),
        )
        workflow_seed_md.write_text(
            _workflow_seed_md(
                slug=slug,
                title=title,
                domain=domain,
                source_package=source_package_path,
                status=status,
            ),
            encoding="utf-8",
        )
        return result

    intent = _initial_intent(structured, handoff)
    profile = infer_taste_profile(slug, intent)
    cards = generate_direction_cards(profile)
    recommended_card_id = cards[0].id
    sketch_prompts = _build_sketch_prompts(cards)

    write_discovery_artifacts(
        root=root_path,
        slug=slug,
        title=title,
        original_intent=intent,
        profile=profile,
        cards=cards,
        recommended_card_id=recommended_card_id,
        sketch_prompts=sketch_prompts,
    )
    _copy_source_package(source_package_path, real_brief_dir)
    _write_json(
        adapter_manifest_json,
        _adapter_manifest(
            slug=slug,
            domain=domain,
            date=safe_date,
            source_manifest=source_manifest,
            status=status,
        ),
    )
    workflow_seed_md.write_text(
        _workflow_seed_md(
            slug=slug,
            title=title,
            domain=domain,
            source_package=source_package_path,
            status=status,
        ),
        encoding="utf-8",
    )
    return result
