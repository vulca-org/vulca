# Real Brief Workflow Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Phase 2 adapter that imports Phase 1 real-brief benchmark packages into `docs/visual-specs/<slug>/` as official Vulca workflow seed artifacts without bypassing human gates.

**Architecture:** Add a focused `vulca.real_brief.workflow_adapter` module that validates a Phase 1 package, copies source package artifacts into `real_brief/`, writes `discovery/` artifacts through existing `vulca.discovery` helpers for supported static 2D domains, and writes `workflow_seed.md` plus `adapter_manifest.json`. Keep `scripts/real_brief_workflow_adapter.py` as a thin CLI wrapper. No provider, redraw, mask, decompose, or layer execution happens in this phase.

**Tech Stack:** Python `pathlib`, `json`, `shutil`, dataclasses-free helper functions, existing `vulca.real_brief` schemas, existing `vulca.discovery` artifact writer, pytest, argparse.

---

## File Structure

- Create `src/vulca/real_brief/workflow_adapter.py`: source-package validation, domain mapping, safe copy, discovery artifact generation, adapter manifest, workflow seed writing, and public `adapt_real_brief_package`.
- Create `scripts/real_brief_workflow_adapter.py`: CLI wrapper for the Python API.
- Create `tests/test_real_brief_workflow_adapter.py`: TDD coverage for supported adaptation, unsupported domains, collision policy, validation failures, dry-run, CLI, and secret scanning.
- Modify `src/vulca/real_brief/__init__.py`: lazy-export `adapt_real_brief_package`.
- Optional documentation change only if implementation exposes a user-facing entry point that needs a link from `docs/product/experiments/cultural-term-efficacy.md`.

Implementation boundaries:

- Do not modify redraw, mask, decompose, layer, provider, MCP registration, or existing `/visual-*` skill files.
- Do not call network APIs or real image providers in tests.
- Do not write provider keys, endpoint URLs, or environment variable names into generated adapter artifacts.
- Do not mutate the Phase 1 source package.
- Keep `public_art` and `video_treatment` as `unsupported_for_visual_chain` in Phase 2 v1.

---

### Task 1: Supported Package Adapter Core

**Files:**
- Create: `tests/test_real_brief_workflow_adapter.py`
- Create: `src/vulca/real_brief/workflow_adapter.py`

- [ ] **Step 1: Write the failing supported-flow tests**

Create `tests/test_real_brief_workflow_adapter.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path

import pytest


def _source_package(tmp_path: Path, slug: str) -> Path:
    from vulca.real_brief.artifacts import write_real_brief_dry_run

    result = write_real_brief_dry_run(
        output_root=tmp_path / "source",
        slug=slug,
        date="2026-05-01",
        write_html_review=False,
    )
    return Path(result["output_dir"])


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_adapt_real_brief_package_writes_supported_visual_workflow(tmp_path):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(
        tmp_path,
        "seattle-polish-film-festival-poster",
    )
    original_manifest = (source_package / "manifest.json").read_text(encoding="utf-8")

    result = adapt_real_brief_package(
        source_package=source_package,
        root=tmp_path / "repo",
        date="2026-05-01",
    )

    project_dir = tmp_path / "repo" / "docs" / "visual-specs" / (
        "seattle-polish-film-festival-poster"
    )
    real_brief_dir = project_dir / "real_brief"
    discovery_dir = project_dir / "discovery"

    assert result["slug"] == "seattle-polish-film-festival-poster"
    assert result["status"] == "ready_for_visual_brainstorm"
    assert Path(result["project_dir"]) == project_dir
    assert Path(result["workflow_seed_md"]) == project_dir / "workflow_seed.md"
    assert Path(result["adapter_manifest_json"]) == (
        real_brief_dir / "adapter_manifest.json"
    )
    assert Path(result["discovery_md"]) == discovery_dir / "discovery.md"

    for rel in [
        "discovery/discovery.md",
        "discovery/taste_profile.json",
        "discovery/direction_cards.json",
        "discovery/sketch_prompts.json",
        "real_brief/adapter_manifest.json",
        "real_brief/source_package_manifest.json",
        "real_brief/structured_brief.json",
        "real_brief/workflow_handoff.json",
        "real_brief/decision_package.md",
        "real_brief/production_package.md",
        "real_brief/review_schema.json",
        "real_brief/source_brief.md",
        "real_brief/summary.md",
        "real_brief/conditions/A-one-shot.md",
        "real_brief/prompts/D.txt",
        "workflow_seed.md",
    ]:
        assert (project_dir / rel).exists(), rel

    manifest = _read_json(real_brief_dir / "adapter_manifest.json")
    assert manifest["schema_version"] == "0.1"
    assert manifest["adapter"] == "real-brief-workflow-adapter"
    assert manifest["source_experiment"] == "real-brief-benchmark"
    assert manifest["slug"] == "seattle-polish-film-festival-poster"
    assert manifest["workflow_status"] == "ready_for_visual_brainstorm"
    assert manifest["human_gate_required"] is True
    assert manifest["simulation_only"] is True
    assert manifest["domain"] == "poster"
    assert manifest["visual_workflow_domain"] == "poster"
    assert manifest["created"] == "2026-05-01"
    assert manifest["workflow_artifacts"]["discovery_md"] == (
        "../discovery/discovery.md"
    )
    assert manifest["next_steps"] == [
        "/visual-brainstorm seattle-polish-film-festival-poster",
        "/visual-spec seattle-polish-film-festival-poster",
        "/visual-plan seattle-polish-film-festival-poster",
        "/evaluate seattle-polish-film-festival-poster",
    ]

    discovery_md = (discovery_dir / "discovery.md").read_text(encoding="utf-8")
    assert "ready_for_brainstorm" in discovery_md
    assert "Ready for /visual-brainstorm" in discovery_md
    assert "Seattle Polish Film Festival Poster" in discovery_md

    workflow_seed = (project_dir / "workflow_seed.md").read_text(encoding="utf-8")
    assert "ready_for_visual_brainstorm" in workflow_seed
    assert "/visual-brainstorm seattle-polish-film-festival-poster" in workflow_seed
    assert "/visual-spec must resolve design.md" in workflow_seed
    assert "not a substitute for `proposal.md`" in workflow_seed

    assert (source_package / "manifest.json").read_text(encoding="utf-8") == (
        original_manifest
    )


def test_adapt_real_brief_package_dry_run_writes_nothing(tmp_path):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, "gsm-community-market-campaign")
    root = tmp_path / "repo"

    result = adapt_real_brief_package(
        source_package=source_package,
        root=root,
        date="2026-05-01",
        dry_run=True,
    )

    assert result["slug"] == "gsm-community-market-campaign"
    assert result["status"] == "ready_for_visual_brainstorm"
    assert result["dry_run"] == "true"
    assert not (root / "docs").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_workflow_adapter.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.real_brief.workflow_adapter'`.

- [ ] **Step 3: Implement the first supported adapter path**

Create `src/vulca/real_brief/workflow_adapter.py`:

```python
"""Adapt real-brief benchmark packages into Vulca visual workflow seeds."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from vulca.discovery.artifacts import build_brainstorm_handoff, write_discovery_artifacts
from vulca.discovery.cards import generate_direction_cards
from vulca.discovery.profile import infer_taste_profile
from vulca.discovery.prompting import compose_prompt_from_direction_card
from vulca.discovery.types import SketchPrompt
from vulca.real_brief.types import safe_slug


REQUIRED_SOURCE_FILES = (
    "manifest.json",
    "workflow_handoff.json",
    "structured_brief.json",
    "decision_package.md",
    "production_package.md",
    "review_schema.json",
)

OPTIONAL_SOURCE_FILES = (
    "source_brief.md",
    "summary.md",
)

SUPPORTED_VISUAL_DOMAINS = {
    "poster",
    "packaging",
    "brand_visual",
    "illustration",
    "editorial_cover",
    "photography_brief",
    "hero_visual_for_ui",
}

UNSUPPORTED_DOMAIN_REASONS = {
    "public_art": "source domain is outside /visual-brainstorm static 2D scope",
    "video_treatment": "source domain is outside /visual-brainstorm static 2D scope",
}

SECRET_MARKERS = (
    "sk-",
    "VULCA_REAL_PROVIDER_API_KEY",
    "OPENAI_API_KEY",
    "globalai",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _project_dir(root: Path, slug: str) -> Path:
    return root / "docs" / "visual-specs" / safe_slug(slug)


def _source_rel(path: Path, source_package: Path) -> str:
    return str(path.resolve().relative_to(source_package.resolve()))


def _copy_file(source_package: Path, rel: str, dest_dir: Path, dest_name: str = "") -> None:
    source = (source_package / rel).resolve()
    source_package_resolved = source_package.resolve()
    if source_package_resolved not in source.parents and source != source_package_resolved:
        raise ValueError(f"unsafe source path outside package: {rel}")
    if not source.exists():
        return
    target = dest_dir / (dest_name or rel)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _copy_tree_if_exists(source_package: Path, rel: str, dest_dir: Path) -> None:
    source = (source_package / rel).resolve()
    source_package_resolved = source_package.resolve()
    if not source.exists():
        return
    if source_package_resolved not in source.parents and source != source_package_resolved:
        raise ValueError(f"unsafe source path outside package: {rel}")
    target = dest_dir / rel
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)


def _intent_from_structured_brief(
    structured_brief: dict[str, Any],
    handoff: dict[str, Any],
) -> str:
    seed = handoff.get("visual_discovery_seed", {})
    initial_intent = str(seed.get("initial_intent") or structured_brief.get("source_brief") or "")
    parts = [
        initial_intent,
        f"Client: {structured_brief.get('client', '')}",
        f"Context: {structured_brief.get('context', '')}",
        "Audience: " + ", ".join(str(item) for item in structured_brief.get("audience", [])),
        "Constraints: " + ", ".join(str(item) for item in structured_brief.get("constraints", [])),
        "Risks: " + ", ".join(str(item) for item in structured_brief.get("risks", [])),
        "Avoid: " + ", ".join(str(item) for item in structured_brief.get("avoid", [])),
    ]
    return "\n".join(part for part in parts if part.strip())


def _sketch_prompts_from_cards(cards: list[Any]) -> list[SketchPrompt]:
    sketches: list[SketchPrompt] = []
    for card in cards:
        prompt = compose_prompt_from_direction_card(card, target="sketch")
        payload = prompt.to_dict()
        sketches.append(
            SketchPrompt(
                card_id=card.id,
                provider="mock",
                model="",
                prompt=payload["prompt"],
                negative_prompt=payload["negative_prompt"],
                size="1024x1024",
                purpose="adapter text sketch prompt for real-brief workflow handoff",
            )
        )
    return sketches


def _load_package(source_package: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if not source_package.is_dir():
        raise ValueError(f"source package not found: {source_package}")
    missing = [rel for rel in REQUIRED_SOURCE_FILES if not (source_package / rel).exists()]
    if missing:
        raise ValueError(f"source package missing required files: {', '.join(missing)}")

    manifest = _read_json(source_package / "manifest.json")
    handoff = _read_json(source_package / "workflow_handoff.json")
    structured = _read_json(source_package / "structured_brief.json")

    slug = safe_slug(str(structured.get("slug", "")))
    if manifest.get("schema_version") != "0.1":
        raise ValueError("manifest.schema_version must be 0.1")
    if manifest.get("experiment") != "real-brief-benchmark":
        raise ValueError("source package must be a real-brief-benchmark package")
    if manifest.get("provider_execution") != "disabled":
        raise ValueError("Phase 2 adapter only accepts disabled provider execution")
    if handoff.get("schema_version") != "0.1":
        raise ValueError("workflow_handoff.schema_version must be 0.1")
    if handoff.get("human_gate_required") is not True:
        raise ValueError("workflow_handoff.human_gate_required must be true")

    fixture_slug = manifest.get("fixture", {}).get("slug")
    if fixture_slug != slug or handoff.get("slug") != slug:
        raise ValueError("slug mismatch across manifest, workflow_handoff, and structured_brief")

    return manifest, handoff, structured


def _workflow_status(structured: dict[str, Any]) -> tuple[str, str, str]:
    domain = str(structured.get("domain", "")).strip()
    if domain in SUPPORTED_VISUAL_DOMAINS:
        return "ready_for_visual_brainstorm", domain, ""
    reason = UNSUPPORTED_DOMAIN_REASONS.get(
        domain,
        "source domain is outside /visual-brainstorm static 2D scope",
    )
    return "unsupported_for_visual_chain", "", reason


def _write_real_brief_package(
    *,
    source_package: Path,
    real_brief_dir: Path,
    manifest: dict[str, Any],
) -> None:
    _copy_file(source_package, "manifest.json", real_brief_dir, "source_package_manifest.json")
    for rel in REQUIRED_SOURCE_FILES:
        if rel == "manifest.json":
            continue
        _copy_file(source_package, rel, real_brief_dir)
    for rel in OPTIONAL_SOURCE_FILES:
        _copy_file(source_package, rel, real_brief_dir)
    for rel in ("conditions", "prompts", "images", "evaluations"):
        _copy_tree_if_exists(source_package, rel, real_brief_dir)


def _adapter_manifest(
    *,
    source_package: Path,
    slug: str,
    status: str,
    reason: str,
    date: str,
    structured: dict[str, Any],
    manifest: dict[str, Any],
    visual_domain: str,
) -> dict[str, Any]:
    payload = {
        "schema_version": "0.1",
        "adapter": "real-brief-workflow-adapter",
        "source_experiment": "real-brief-benchmark",
        "source_package_path": str(source_package),
        "slug": slug,
        "workflow_status": status,
        "human_gate_required": True,
        "simulation_only": bool(structured.get("simulation_only", True)),
        "ai_policy": str(structured.get("ai_policy", "")),
        "domain": str(structured.get("domain", "")),
        "visual_workflow_domain": visual_domain or None,
        "created": date,
        "source_files": {
            "manifest": "source_package_manifest.json",
            "structured_brief": "structured_brief.json",
            "workflow_handoff": "workflow_handoff.json",
            "decision_package": "decision_package.md",
            "production_package": "production_package.md",
            "review_schema": "review_schema.json",
        },
        "workflow_artifacts": {},
        "next_steps": [],
    }
    if reason:
        payload["unsupported_reason"] = reason
    if status == "ready_for_visual_brainstorm":
        payload["workflow_artifacts"] = {
            "discovery_md": "../discovery/discovery.md",
            "taste_profile_json": "../discovery/taste_profile.json",
            "direction_cards_json": "../discovery/direction_cards.json",
            "workflow_seed_md": "../workflow_seed.md",
        }
        payload["next_steps"] = [
            f"/visual-brainstorm {slug}",
            f"/visual-spec {slug}",
            f"/visual-plan {slug}",
            f"/evaluate {slug}",
        ]
    return payload


def _workflow_seed_text(
    *,
    title: str,
    slug: str,
    status: str,
    source_package: Path,
    handoff_text: str,
    unsupported_reason: str,
) -> str:
    if status == "ready_for_visual_brainstorm":
        next_step = f"Run /visual-brainstorm {slug} using the discovery handoff below."
        deferred = "none"
        imported_artifacts = [
            "- discovery/discovery.md",
            "- discovery/taste_profile.json",
            "- discovery/direction_cards.json",
            "- real_brief/structured_brief.json",
            "- real_brief/decision_package.md",
            "- real_brief/production_package.md",
        ]
    else:
        next_step = "Do not run /visual-brainstorm for this package in Phase 2 v1."
        deferred = unsupported_reason
        imported_artifacts = [
            "- real_brief/structured_brief.json",
            "- real_brief/decision_package.md",
            "- real_brief/production_package.md",
            "- real_brief/adapter_manifest.json",
        ]
    return "\n".join(
        [
            f"# Real Brief Workflow Seed: {title}",
            "",
            "## Status",
            status,
            "",
            "## Source Package",
            str(source_package),
            "",
            "## Imported Artifacts",
            *imported_artifacts,
            "",
            "## Recommended Next Step",
            next_step,
            "",
            "## Discovery Handoff",
            handoff_text or "none",
            "",
            "## Human Gates Preserved",
            "- /visual-brainstorm must finalize proposal.md",
            "- /visual-spec must resolve design.md",
            "- /visual-plan must review plan.md before generation",
            "",
            "## Unsupported Or Deferred Items",
            deferred,
            "",
            "This workflow seed is not a substitute for `proposal.md`.",
            "",
        ]
    )


def _assert_no_secret_markers(project_dir: Path) -> None:
    for path in project_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        for marker in SECRET_MARKERS:
            haystack = lowered if marker == "globalai" else text
            if marker in haystack:
                raise ValueError(f"secret-like marker found in generated artifact: {path}")


def adapt_real_brief_package(
    *,
    source_package: str | Path,
    root: str | Path,
    date: str,
    force_discovery: bool = False,
    force_real_brief: bool = False,
    dry_run: bool = False,
) -> dict[str, str]:
    """Import a Phase 1 real-brief package into the visual workflow tree."""
    source_package_path = Path(source_package)
    root_path = Path(root)
    manifest, handoff, structured = _load_package(source_package_path)
    slug = safe_slug(str(structured["slug"]))
    status, visual_domain, unsupported_reason = _workflow_status(structured)
    project_dir = _project_dir(root_path, slug)
    discovery_dir = project_dir / "discovery"
    real_brief_dir = project_dir / "real_brief"

    result = {
        "slug": slug,
        "status": status,
        "project_dir": str(project_dir),
        "adapter_manifest_json": str(real_brief_dir / "adapter_manifest.json"),
    }
    if status == "ready_for_visual_brainstorm":
        result["workflow_seed_md"] = str(project_dir / "workflow_seed.md")
        result["discovery_md"] = str(discovery_dir / "discovery.md")
    if dry_run:
        result["dry_run"] = "true"
        return result

    _write_real_brief_package(
        source_package=source_package_path,
        real_brief_dir=real_brief_dir,
        manifest=manifest,
    )

    handoff_text = ""
    if status == "ready_for_visual_brainstorm":
        intent = _intent_from_structured_brief(structured, handoff)
        profile = infer_taste_profile(slug, intent)
        cards = generate_direction_cards(profile, count=3)
        recommended_card = cards[0]
        write_discovery_artifacts(
            root=root_path,
            slug=slug,
            title=str(structured.get("title", slug)),
            original_intent=intent,
            profile=profile,
            cards=cards,
            recommended_card_id=recommended_card.id,
            sketch_prompts=_sketch_prompts_from_cards(cards),
        )
        handoff_text = build_brainstorm_handoff(profile, recommended_card)

    adapter_manifest = _adapter_manifest(
        source_package=source_package_path,
        slug=slug,
        status=status,
        reason=unsupported_reason,
        date=date,
        structured=structured,
        manifest=manifest,
        visual_domain=visual_domain,
    )
    _write_json(real_brief_dir / "adapter_manifest.json", adapter_manifest)
    _write_text(
        project_dir / "workflow_seed.md",
        _workflow_seed_text(
            title=str(structured.get("title", slug)),
            slug=slug,
            status=status,
            source_package=source_package_path,
            handoff_text=handoff_text,
            unsupported_reason=unsupported_reason,
        ),
    )
    _assert_no_secret_markers(project_dir)
    return result
```

- [ ] **Step 4: Run supported-flow tests**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_workflow_adapter.py::test_adapt_real_brief_package_writes_supported_visual_workflow tests/test_real_brief_workflow_adapter.py::test_adapt_real_brief_package_dry_run_writes_nothing -q
```

Expected: PASS.

- [ ] **Step 5: Commit Task 1**

Run:

```bash
git add src/vulca/real_brief/workflow_adapter.py tests/test_real_brief_workflow_adapter.py
git commit -m "feat: add real brief workflow adapter core"
```

---

### Task 2: Validation, Collision Policy, And Unsupported Domains

**Files:**
- Modify: `tests/test_real_brief_workflow_adapter.py`
- Modify: `src/vulca/real_brief/workflow_adapter.py`

- [ ] **Step 1: Add failing tests for hardening behavior**

Append to `tests/test_real_brief_workflow_adapter.py`:

```python
def test_adapt_real_brief_package_rejects_missing_required_file(tmp_path):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, "seattle-polish-film-festival-poster")
    (source_package / "workflow_handoff.json").unlink()

    with pytest.raises(ValueError, match="missing required files"):
        adapt_real_brief_package(
            source_package=source_package,
            root=tmp_path / "repo",
            date="2026-05-01",
        )

    assert not (tmp_path / "repo" / "docs").exists()


def test_adapt_real_brief_package_rejects_slug_mismatch(tmp_path):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, "seattle-polish-film-festival-poster")
    handoff_path = source_package / "workflow_handoff.json"
    handoff = _read_json(handoff_path)
    handoff["slug"] = "different-slug"
    handoff_path.write_text(json.dumps(handoff), encoding="utf-8")

    with pytest.raises(ValueError, match="slug mismatch"):
        adapt_real_brief_package(
            source_package=source_package,
            root=tmp_path / "repo",
            date="2026-05-01",
        )


@pytest.mark.parametrize(
    "filename",
    ["proposal.md", "design.md", "plan.md"],
)
def test_adapt_real_brief_package_rejects_finalized_workflow_collisions(
    tmp_path,
    filename,
):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, "seattle-polish-film-festival-poster")
    project_dir = tmp_path / "repo" / "docs" / "visual-specs" / (
        "seattle-polish-film-festival-poster"
    )
    project_dir.mkdir(parents=True)
    statuses = {
        "proposal.md": "ready",
        "design.md": "resolved",
        "plan.md": "completed",
    }
    (project_dir / filename).write_text(
        f"---\nstatus: {statuses[filename]}\n---\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="refuse to overwrite finalized workflow"):
        adapt_real_brief_package(
            source_package=source_package,
            root=tmp_path / "repo",
            date="2026-05-01",
        )


def test_adapt_real_brief_package_requires_force_for_adapter_owned_dirs(tmp_path):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, "gsm-community-market-campaign")
    root = tmp_path / "repo"
    adapt_real_brief_package(
        source_package=source_package,
        root=root,
        date="2026-05-01",
    )

    with pytest.raises(RuntimeError, match="discovery already exists"):
        adapt_real_brief_package(
            source_package=source_package,
            root=root,
            date="2026-05-01",
        )

    result = adapt_real_brief_package(
        source_package=source_package,
        root=root,
        date="2026-05-01",
        force_discovery=True,
        force_real_brief=True,
    )

    assert result["status"] == "ready_for_visual_brainstorm"


@pytest.mark.parametrize(
    "slug",
    ["erie-botanical-gardens-public-art", "music-video-treatment-low-budget"],
)
def test_adapt_real_brief_package_marks_unsupported_domains(tmp_path, slug):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, slug)

    result = adapt_real_brief_package(
        source_package=source_package,
        root=tmp_path / "repo",
        date="2026-05-01",
    )

    project_dir = tmp_path / "repo" / "docs" / "visual-specs" / slug
    manifest = _read_json(project_dir / "real_brief" / "adapter_manifest.json")

    assert result["status"] == "unsupported_for_visual_chain"
    assert manifest["workflow_status"] == "unsupported_for_visual_chain"
    assert manifest["visual_workflow_domain"] is None
    assert manifest["unsupported_reason"] == (
        "source domain is outside /visual-brainstorm static 2D scope"
    )
    assert not (project_dir / "discovery").exists()
    assert (project_dir / "workflow_seed.md").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_workflow_adapter.py -q
```

Expected: FAIL on collision behavior because Task 1 implementation has not enforced destination policy.

- [ ] **Step 3: Add destination collision helpers**

Add these helpers to `src/vulca/real_brief/workflow_adapter.py` above `adapt_real_brief_package`:

```python
def _frontmatter_status(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---"):
        return ""
    for line in text.splitlines()[1:20]:
        if line.strip() == "---":
            break
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return ""


def _check_destination_policy(
    *,
    project_dir: Path,
    force_discovery: bool,
    force_real_brief: bool,
) -> None:
    terminal_files = {
        "proposal.md": {"ready"},
        "design.md": {"resolved"},
        "plan.md": {"completed", "partial", "aborted"},
    }
    for filename, terminal_statuses in terminal_files.items():
        status = _frontmatter_status(project_dir / filename)
        if status in terminal_statuses:
            raise RuntimeError(
                f"refuse to overwrite finalized workflow: {project_dir / filename}"
            )
    if (project_dir / "discovery").exists() and not force_discovery:
        raise RuntimeError("discovery already exists; pass --force-discovery")
    if (project_dir / "real_brief").exists() and not force_real_brief:
        raise RuntimeError("real_brief already exists; pass --force-real-brief")


def _replace_adapter_owned_dir(target: Path, force: bool) -> None:
    if target.exists():
        if not force:
            raise RuntimeError(f"{target.name} already exists")
        shutil.rmtree(target)
```

- [ ] **Step 4: Apply destination policy in `adapt_real_brief_package`**

In `adapt_real_brief_package`, after computing `project_dir`, `discovery_dir`, and `real_brief_dir`, insert:

```python
    _check_destination_policy(
        project_dir=project_dir,
        force_discovery=force_discovery,
        force_real_brief=force_real_brief,
    )
```

Before `_write_real_brief_package(...)`, insert:

```python
    _replace_adapter_owned_dir(discovery_dir, force_discovery)
    _replace_adapter_owned_dir(real_brief_dir, force_real_brief)
```

- [ ] **Step 5: Run hardening tests**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_workflow_adapter.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

Run:

```bash
git add src/vulca/real_brief/workflow_adapter.py tests/test_real_brief_workflow_adapter.py
git commit -m "fix: harden real brief workflow adapter"
```

---

### Task 3: CLI And Public Export

**Files:**
- Modify: `tests/test_real_brief_workflow_adapter.py`
- Create: `scripts/real_brief_workflow_adapter.py`
- Modify: `src/vulca/real_brief/__init__.py`

- [ ] **Step 1: Add failing CLI and export tests**

Append to `tests/test_real_brief_workflow_adapter.py`:

```python
def test_real_brief_workflow_adapter_cli_dry_run(tmp_path, capsys):
    from scripts.real_brief_workflow_adapter import main

    source_package = _source_package(tmp_path, "seattle-polish-film-festival-poster")

    rc = main(
        [
            "--source-package",
            str(source_package),
            "--root",
            str(tmp_path / "repo"),
            "--date",
            "2026-05-01",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 0
    assert payload["slug"] == "seattle-polish-film-festival-poster"
    assert payload["status"] == "ready_for_visual_brainstorm"
    assert payload["dry_run"] == "true"
    assert not (tmp_path / "repo" / "docs").exists()


def test_real_brief_workflow_adapter_cli_writes_files(tmp_path, capsys):
    from scripts.real_brief_workflow_adapter import main

    source_package = _source_package(tmp_path, "gsm-community-market-campaign")

    rc = main(
        [
            "--source-package",
            str(source_package),
            "--root",
            str(tmp_path / "repo"),
            "--date",
            "2026-05-01",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    project_dir = tmp_path / "repo" / "docs" / "visual-specs" / (
        "gsm-community-market-campaign"
    )

    assert rc == 0
    assert payload["status"] == "ready_for_visual_brainstorm"
    assert (project_dir / "workflow_seed.md").exists()


def test_real_brief_workflow_adapter_can_resolve_source_root_slug_date(tmp_path):
    from scripts.real_brief_workflow_adapter import main

    _source_package(tmp_path, "gsm-community-market-campaign")

    rc = main(
        [
            "--source-root",
            str(tmp_path / "source"),
            "--slug",
            "gsm-community-market-campaign",
            "--root",
            str(tmp_path / "repo"),
            "--date",
            "2026-05-01",
            "--dry-run",
        ]
    )

    assert rc == 0


def test_real_brief_workflow_adapter_public_export_is_lazy():
    from vulca.real_brief import adapt_real_brief_package

    assert callable(adapt_real_brief_package)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_workflow_adapter.py -q
```

Expected: FAIL with `ModuleNotFoundError` for `scripts.real_brief_workflow_adapter` and missing export from `vulca.real_brief`.

- [ ] **Step 3: Implement the CLI wrapper**

Create `scripts/real_brief_workflow_adapter.py`:

```python
"""CLI wrapper for importing real-brief packages into visual workflow seeds."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _resolve_source_package(args: argparse.Namespace) -> Path:
    if args.source_package:
        return Path(args.source_package)
    if not args.source_root or not args.slug or not args.date:
        raise RuntimeError(
            "--source-package or all of --source-root, --slug, and --date is required"
        )
    return Path(args.source_root) / f"{args.date}-{args.slug}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Import a real-brief benchmark package into Vulca visual workflow seeds."
    )
    parser.add_argument("--source-package")
    parser.add_argument("--source-root")
    parser.add_argument("--slug")
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", required=True)
    parser.add_argument("--force-discovery", action="store_true")
    parser.add_argument("--force-real-brief", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    result = adapt_real_brief_package(
        source_package=_resolve_source_package(args),
        root=args.root,
        date=args.date,
        force_discovery=args.force_discovery,
        force_real_brief=args.force_real_brief,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _cli() -> int:
    try:
        return main()
    except (RuntimeError, ValueError) as exc:
        raise SystemExit(f"error: {exc}") from None


if __name__ == "__main__":
    raise SystemExit(_cli())
```

- [ ] **Step 4: Add lazy export**

Modify `src/vulca/real_brief/__init__.py`:

Add `"adapt_real_brief_package"` to `__all__`.

Add this entry to `_LAZY_EXPORTS`:

```python
    "adapt_real_brief_package": (
        "vulca.real_brief.workflow_adapter",
        "adapt_real_brief_package",
    ),
```

- [ ] **Step 5: Run CLI/export tests**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_workflow_adapter.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit Task 3**

Run:

```bash
git add scripts/real_brief_workflow_adapter.py src/vulca/real_brief/__init__.py tests/test_real_brief_workflow_adapter.py
git commit -m "feat: add real brief workflow adapter cli"
```

---

### Task 4: Secret Scan, Regression Tests, And Documentation Link

**Files:**
- Modify: `tests/test_real_brief_workflow_adapter.py`
- Optionally modify: `docs/product/experiments/cultural-term-efficacy.md`

- [ ] **Step 1: Add generated-artifact secret scan test**

Append to `tests/test_real_brief_workflow_adapter.py`:

```python
def test_adapt_real_brief_package_generated_artifacts_do_not_contain_secret_markers(
    tmp_path,
):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, "seattle-polish-film-festival-poster")
    root = tmp_path / "repo"

    adapt_real_brief_package(
        source_package=source_package,
        root=root,
        date="2026-05-01",
    )

    project_dir = root / "docs" / "visual-specs" / (
        "seattle-polish-film-festival-poster"
    )
    generated = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in project_dir.rglob("*")
        if path.is_file() and path.suffix in {".md", ".json", ".txt"}
    )

    assert "sk-" not in generated
    assert "VULCA_REAL_PROVIDER_API_KEY" not in generated
    assert "OPENAI_API_KEY" not in generated
    assert "globalai" not in generated.lower()
```

- [ ] **Step 2: Run adapter tests**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_workflow_adapter.py -q
```

Expected: PASS.

- [ ] **Step 3: Run Phase 1 and visual-discovery regressions**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py tests/test_real_brief_workflow_adapter.py -q
```

Expected: PASS.

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_visual_discovery_benchmark.py tests/test_visual_discovery_artifacts.py tests/test_visual_discovery_cards.py tests/test_visual_discovery_types.py -q
```

Expected: PASS.

- [ ] **Step 4: Add a short documentation link only if missing**

Check:

```bash
grep -n "real-brief workflow adapter" docs/product/experiments/cultural-term-efficacy.md
```

If there is no Phase 2 link, add this short paragraph near the existing real-brief benchmark section:

```markdown
Phase 2 workflow adapter: `scripts/real_brief_workflow_adapter.py` imports a Phase 1 real-brief package into `docs/visual-specs/<slug>/` as `discovery/`, `real_brief/`, and `workflow_seed.md` artifacts. It preserves `/visual-brainstorm`, `/visual-spec`, and `/visual-plan` human gates and does not call image providers.
```

- [ ] **Step 5: Run docs grep to verify no secret marker was introduced**

Run:

```bash
grep -R -nE 'sk-|VULCA_REAL_PROVIDER_API_KEY|OPENAI_API_KEY|globalai' src/vulca/real_brief scripts/real_brief_workflow_adapter.py tests/test_real_brief_workflow_adapter.py docs/product/experiments/cultural-term-efficacy.md
```

Expected: no output, except the intentional string literals inside the secret scan test. If grep shows only the four assertion strings inside `tests/test_real_brief_workflow_adapter.py`, that is acceptable because they are test sentinels and not credentials.

- [ ] **Step 6: Commit Task 4**

Run:

```bash
git add tests/test_real_brief_workflow_adapter.py docs/product/experiments/cultural-term-efficacy.md
git commit -m "test: cover real brief workflow adapter artifacts"
```

If the documentation file was unchanged, omit it from `git add`.

---

### Task 5: End-To-End Dry Run And Branch Completion

**Files:**
- No planned code changes.

- [ ] **Step 1: Run a CLI dry-run from a generated Phase 1 package**

Run:

```bash
PYTHONPATH=src python3 scripts/real_brief_benchmark.py --slug seattle-polish-film-festival-poster --date 2026-05-01 --output-root /private/tmp/vulca-real-brief-phase2-source --no-html-review
```

Expected: exit 0 and source package at:

```text
/private/tmp/vulca-real-brief-phase2-source/2026-05-01-seattle-polish-film-festival-poster
```

Run:

```bash
PYTHONPATH=src python3 scripts/real_brief_workflow_adapter.py --source-package /private/tmp/vulca-real-brief-phase2-source/2026-05-01-seattle-polish-film-festival-poster --root /private/tmp/vulca-real-brief-phase2-target --date 2026-05-01
```

Expected JSON includes:

```json
{
  "slug": "seattle-polish-film-festival-poster",
  "status": "ready_for_visual_brainstorm"
}
```

- [ ] **Step 2: Inspect generated files**

Run:

```bash
find /private/tmp/vulca-real-brief-phase2-target/docs/visual-specs/seattle-polish-film-festival-poster -maxdepth 3 -type f | sort
```

Expected includes:

```text
discovery/discovery.md
discovery/taste_profile.json
discovery/direction_cards.json
discovery/sketch_prompts.json
real_brief/adapter_manifest.json
real_brief/structured_brief.json
real_brief/workflow_handoff.json
workflow_seed.md
```

- [ ] **Step 3: Run final regression suite**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py tests/test_real_brief_workflow_adapter.py -q
```

Expected: PASS.

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_visual_discovery_benchmark.py tests/test_visual_discovery_artifacts.py tests/test_visual_discovery_cards.py tests/test_visual_discovery_types.py -q
```

Expected: PASS.

- [ ] **Step 4: Check git status and commit any final docs-only adjustment**

Run:

```bash
git status --short --branch
```

Expected: clean branch ahead of `origin/master` by the Phase 2 commits. If a small docs-only adjustment remains, commit it with:

```bash
git add <changed-doc-file>
git commit -m "docs: link real brief workflow adapter"
```

- [ ] **Step 5: Prepare PR**

Run:

```bash
git push -u origin codex/real-brief-workflow-adapter
```

Then create a PR titled:

```text
feat: add real brief workflow adapter
```

PR summary:

```markdown
## Summary
- add Phase 2 adapter from real-brief benchmark packages to `docs/visual-specs/<slug>/`
- write `discovery/`, `real_brief/`, and `workflow_seed.md` artifacts without provider execution
- preserve `/visual-brainstorm`, `/visual-spec`, and `/visual-plan` human gates
- mark `public_art` and `video_treatment` as unsupported for static visual workflow v1

## Tests
- `PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py tests/test_real_brief_workflow_adapter.py -q`
- `PYTHONPATH=src python3 -m pytest tests/test_visual_discovery_benchmark.py tests/test_visual_discovery_artifacts.py tests/test_visual_discovery_cards.py tests/test_visual_discovery_types.py -q`
```

---

## Review Checklist

- Adapter writes no generated pixels.
- Adapter never calls real providers.
- Adapter preserves human gates and never finalizes proposal/design/plan.
- Adapter marks `public_art` and `video_treatment` unsupported.
- Phase 1 benchmark tests still pass.
- Visual discovery regression tests still pass.
- Source packages are copied, not mutated.
- Generated artifacts do not contain provider keys or live endpoint strings.
