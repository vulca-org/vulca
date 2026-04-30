# Cultural-Term Efficacy Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a no-cost dry-run harness for the cultural-term efficacy experiment so Vulca can test whether culture terms, visual operations, avoid lists, and evaluation criteria actually improve model outputs.

**Architecture:** Extend the existing `scripts/visual_discovery_benchmark.py` into a deterministic experiment artifact writer. The harness produces A/B/C/D prompt conditions, built-in project fixtures, manifest/results skeletons, and product docs, while keeping real providers disabled by default.

**Tech Stack:** Python standard library, existing `vulca.discovery` dataclasses/functions, pytest, Markdown product docs.

---

## File Map

- Modify `scripts/visual_discovery_benchmark.py`: experiment fixtures, A-D condition builder, dry-run artifact writer, fail-closed real-provider stub, CLI.
- Modify `tests/test_visual_discovery_benchmark.py`: TDD contract for fixtures, conditions, artifact skeleton, and real-provider safety.
- Modify `tests/test_visual_discovery_docs_truth.py`: roadmap consistency and public-claim guardrails.
- Modify `docs/product/roadmap.md`: move provider capability matrix into Current.
- Modify `docs/product/experiments/cultural-term-efficacy.md`: document the dry-run harness and explicit opt-in boundary.

## Task 1: Add Roadmap Consistency Tests

**Files:**
- Modify: `tests/test_visual_discovery_docs_truth.py`

- [ ] **Step 1: Write failing docs truth test**

Append this test after `test_readme_and_roadmap_mark_evaluate_skill_current`:

```python
def test_roadmap_marks_provider_matrix_current():
    roadmap = (ROOT / "docs" / "product" / "roadmap.md").read_text(
        encoding="utf-8"
    )
    provider_matrix = (
        ROOT / "docs" / "product" / "provider-capabilities.md"
    ).read_text(encoding="utf-8")

    assert "Vulca Provider and Platform Capability Matrix" in provider_matrix
    assert (
        "`docs/product/provider-capabilities.md`: provider/platform capability matrix"
        in roadmap
    )
    assert "Provider capability matrix for public docs" not in roadmap
```

- [ ] **Step 2: Verify RED**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_docs_truth.py -q
```

Expected: one failure because `docs/product/roadmap.md` still lists the provider matrix under Next instead of Current.

## Task 2: Add Benchmark Harness Contract Tests

**Files:**
- Modify: `tests/test_visual_discovery_benchmark.py`

- [ ] **Step 1: Replace benchmark tests with the A-D harness contract**

Replace `tests/test_visual_discovery_benchmark.py` with:

```python
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_experiment_projects_match_protocol_domains():
    from scripts.visual_discovery_benchmark import build_experiment_projects

    projects = build_experiment_projects()

    assert [project.slug for project in projects] == [
        "premium-tea-packaging",
        "spiritual-editorial-poster",
        "cultural-material-campaign",
    ]
    assert "xieyi restraint" in projects[0].prompt
    assert "spiritual but non-religious" in projects[1].prompt
    assert "material references" in projects[2].prompt


def test_build_conditions_a_through_d():
    from scripts.visual_discovery_benchmark import (
        build_conditions,
        build_experiment_projects,
        select_direction_card,
    )

    project = build_experiment_projects()[0]
    card = select_direction_card(project)

    conditions = build_conditions(project.prompt, card)

    assert [condition["id"] for condition in conditions] == ["A", "B", "C", "D"]
    assert conditions[0]["label"] == "User prompt only"
    assert conditions[0]["source_card_id"] == ""
    assert "cultural terms" in conditions[1]["label"].lower()
    assert card.culture_terms[0] in conditions[1]["prompt"]
    assert "Visual operations:" in conditions[2]["prompt"]
    assert conditions[3]["label"] == "Full direction-card prompt"
    assert conditions[3]["negative_prompt"]
    assert conditions[3]["evaluation_focus"]["L1"]
    assert conditions[3]["source_card_id"] == card.id


def test_write_experiment_dry_run_artifacts(tmp_path):
    from scripts.visual_discovery_benchmark import write_experiment_dry_run

    result = write_experiment_dry_run(
        output_root=tmp_path,
        slug="premium-tea-packaging",
        date="2026-04-30",
    )

    out_dir = Path(result["output_dir"])
    assert out_dir == tmp_path / "2026-04-30-premium-tea-packaging"
    for condition_id in ["A", "B", "C", "D"]:
        assert (out_dir / "prompts" / f"{condition_id}.txt").exists()
    assert (out_dir / "images" / "README.md").exists()
    assert (out_dir / "evaluations" / "README.md").exists()

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "0.1"
    assert manifest["experiment"] == "cultural-term-efficacy"
    assert manifest["mode"] == "dry_run"
    assert manifest["provider_execution"] == "disabled"
    assert manifest["project"]["slug"] == "premium-tea-packaging"
    assert [condition["id"] for condition in manifest["conditions"]] == [
        "A",
        "B",
        "C",
        "D",
    ]
    assert {provider["execution"] for provider in manifest["providers"]} == {
        "not_run"
    }

    human_ranking = json.loads(
        (out_dir / "human_ranking.json").read_text(encoding="utf-8")
    )
    provider_costs = json.loads(
        (out_dir / "provider_costs.json").read_text(encoding="utf-8")
    )
    assert human_ranking["status"] == "not_collected"
    assert provider_costs["status"] == "not_collected"
    assert "No image quality conclusion" in (
        out_dir / "summary.md"
    ).read_text(encoding="utf-8")


def test_real_provider_execution_fails_closed():
    from scripts.visual_discovery_benchmark import run_real_provider_experiment

    with pytest.raises(RuntimeError, match="explicit opt-in"):
        run_real_provider_experiment(real_provider=False)
```

- [ ] **Step 2: Verify RED**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_benchmark.py -q
```

Expected: failures because the script still emits A-F conditions and lacks the project fixtures, dry-run artifact writer, and fail-closed real-provider function.

## Task 3: Implement the Dry-Run Harness

**Files:**
- Modify: `scripts/visual_discovery_benchmark.py`

- [ ] **Step 1: Replace the benchmark script implementation**

Replace `scripts/visual_discovery_benchmark.py` with:

```python
"""Dry-run harness for the cultural-term efficacy experiment."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date as date_type
from pathlib import Path
from typing import Any

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
```

- [ ] **Step 2: Verify benchmark tests pass**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_benchmark.py -q
```

Expected: pass.

## Task 4: Update Product Docs

**Files:**
- Modify: `docs/product/roadmap.md`
- Modify: `docs/product/experiments/cultural-term-efficacy.md`

- [ ] **Step 1: Update roadmap**

In `docs/product/roadmap.md`, under `## Current`, add:

```markdown
- `docs/product/provider-capabilities.md`: provider/platform capability matrix.
```

Under `## Next`, remove:

```markdown
- Provider capability matrix for public docs.
```

- [ ] **Step 2: Update cultural-term efficacy docs**

In `docs/product/experiments/cultural-term-efficacy.md`, add this section after `## Providers`:

```markdown
## Harness

Run the no-cost dry-run harness with:

```bash
PYTHONPATH=src python3 scripts/visual_discovery_benchmark.py --date 2026-04-30
```

The harness writes prompts, manifests, empty result records, and summaries. It does not call OpenAI, Gemini, ComfyUI, or `mock` for quality evidence. Real provider execution is a future explicit opt-in path and is disabled in this version.
```

- [ ] **Step 3: Verify docs truth tests pass**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_docs_truth.py -q
```

Expected: pass.

## Task 5: Final Verification and Commit

**Files:**
- All files above.

- [ ] **Step 1: Run focused tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_benchmark.py tests/test_visual_discovery_docs_truth.py tests/test_visual_discovery_prompting.py tests/test_visual_discovery_artifacts.py -q
```

Expected: pass.

- [ ] **Step 2: Run dry-run CLI into a temporary directory**

Run:

```bash
PYTHONPATH=src python3 scripts/visual_discovery_benchmark.py --output-root /private/tmp/vulca-cultural-term-efficacy --date 2026-04-30
```

Expected: command exits 0 and writes three result directories under `/private/tmp/vulca-cultural-term-efficacy`.

- [ ] **Step 3: Scan for unfinished markers**

Run:

```bash
grep -RInE "TB[D]|TO[D]O|lo[r]em|coming soo[n]" scripts/visual_discovery_benchmark.py tests/test_visual_discovery_benchmark.py docs/product/roadmap.md docs/product/experiments/cultural-term-efficacy.md docs/superpowers/specs/2026-04-30-cultural-term-efficacy-harness-design.md docs/superpowers/plans/2026-04-30-cultural-term-efficacy-harness.md
```

Expected: no matches.

- [ ] **Step 4: Check whitespace**

Run:

```bash
git diff --check
```

Expected: no output.

- [ ] **Step 5: Commit implementation**

Run:

```bash
git add scripts/visual_discovery_benchmark.py tests/test_visual_discovery_benchmark.py tests/test_visual_discovery_docs_truth.py docs/product/roadmap.md docs/product/experiments/cultural-term-efficacy.md docs/superpowers/plans/2026-04-30-cultural-term-efficacy-harness.md
git commit -m "feat: add cultural term efficacy harness"
```
