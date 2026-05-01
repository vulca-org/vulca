# Real Brief Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dry-run real-brief benchmark harness that turns public creative briefs into decision packages, production packages, A/B/C/D workflow conditions, workflow handoff artifacts, and a local review surface.

**Architecture:** Add a focused `vulca.real_brief` package for schema, built-in fixtures, condition generation, artifact writing, and HTML review rendering. Keep `scripts/real_brief_benchmark.py` as a thin CLI wrapper. Default execution is dry-run and writes no paid-provider artifacts; real-provider flags fail closed until explicit provider execution is implemented.

**Tech Stack:** Python dataclasses, `json`, `pathlib`, existing `vulca.discovery` direction cards/prompting, pytest, static HTML with localStorage.

---

## File Structure

- Create `src/vulca/real_brief/__init__.py`: public exports for the benchmark package.
- Create `src/vulca/real_brief/types.py`: dataclasses, slug validation, fixture validation, review dimensions.
- Create `src/vulca/real_brief/fixtures.py`: five curated real-brief fixtures as structured data.
- Create `src/vulca/real_brief/conditions.py`: A/B/C/D condition generation using existing discovery internals.
- Create `src/vulca/real_brief/artifacts.py`: dry-run artifact tree writer for packages, handoff, manifest, prompts, review schema, and summary.
- Create `src/vulca/real_brief/review_html.py`: local HTML review board renderer.
- Create `scripts/real_brief_benchmark.py`: CLI entry point.
- Create `tests/test_real_brief_benchmark.py`: focused test coverage for schemas, fixtures, conditions, artifact tree, HTML, CLI, and fail-closed real-provider behavior.
- Modify `docs/product/experiments/cultural-term-efficacy.md`: add a short link from the old prompt test to the new real-brief benchmark.

Implementation boundaries:

- Do not change `/visual-*` skills in Phase 1.
- Do not touch `src/vulca/layers`, redraw, mask refinement, or v0.22 branch-owned files.
- Do not call network APIs in tests.
- Do not write secrets, provider keys, or live endpoint strings into artifacts.

---

### Task 1: Real-Brief Types And Validation

**Files:**
- Create: `src/vulca/real_brief/__init__.py`
- Create: `src/vulca/real_brief/types.py`
- Test: `tests/test_real_brief_benchmark.py`

- [ ] **Step 1: Write failing tests for slug and fixture validation**

Add this to `tests/test_real_brief_benchmark.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_safe_slug_accepts_fixture_style_ids():
    from vulca.real_brief.types import safe_slug

    assert safe_slug("seattle-polish-film-festival-poster") == (
        "seattle-polish-film-festival-poster"
    )
    assert safe_slug("gsm-community-market-campaign") == (
        "gsm-community-market-campaign"
    )


@pytest.mark.parametrize(
    "slug",
    ["", ".", "..", "../escape", "/abs/path", "has space", "UpperCase", "x/y"],
)
def test_safe_slug_rejects_unsafe_ids(slug):
    from vulca.real_brief.types import safe_slug

    with pytest.raises(ValueError, match="safe slug"):
        safe_slug(slug)


def test_fixture_validation_rejects_missing_required_field():
    from vulca.real_brief.types import RealBriefFixture, SourceInfo

    fixture = RealBriefFixture(
        slug="broken-fixture",
        title="Broken Fixture",
        source=SourceInfo(
            url="https://example.test/brief",
            retrieved_on="2026-05-01",
            usage_note="Internal benchmark only",
        ),
        client="",
        context="Context exists",
        audience=["audience"],
        deliverables=[],
        constraints=["constraint"],
        budget="not specified by source",
        timeline="source-specific deadline",
        required_outputs=["decision_package", "production_package"],
        ai_policy="unspecified",
        simulation_only=True,
        risks=["risk"],
        avoid=["avoid"],
        evaluation_dimensions=["brief_compliance"],
    )

    with pytest.raises(ValueError, match="client"):
        fixture.validate()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.real_brief'`.

- [ ] **Step 3: Implement `types.py` and package exports**

Create `src/vulca/real_brief/types.py`:

```python
"""Structured real-brief benchmark data types."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any


_SAFE_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")

AI_POLICIES = {"allowed", "prohibited_for_submission", "unspecified"}
CONDITION_IDS = ("A", "B", "C", "D")
REVIEW_DIMENSIONS = (
    "brief_compliance",
    "audience_fit",
    "deliverable_fit",
    "constraint_handling",
    "cultural_taste_specificity",
    "structural_control",
    "editability_reusability",
    "production_realism",
    "risk_avoidance",
    "decision_usefulness",
)


def safe_slug(slug: str) -> str:
    if (
        not slug
        or slug in {".", ".."}
        or "/" in slug
        or "\\" in slug
        or ".." in slug
        or not _SAFE_SLUG_RE.match(slug)
    ):
        raise ValueError(
            "safe slug required: lowercase letters, digits, '.', '_' or '-' only"
        )
    return slug


@dataclass(frozen=True)
class SourceInfo:
    url: str
    retrieved_on: str
    usage_note: str = "Internal benchmark only"
    deadline: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class Deliverable:
    name: str
    format: str
    channel: str
    required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RealBriefFixture:
    slug: str
    title: str
    source: SourceInfo
    client: str
    context: str
    audience: list[str]
    deliverables: list[Deliverable]
    constraints: list[str]
    budget: str
    timeline: str
    required_outputs: list[str]
    ai_policy: str
    simulation_only: bool
    risks: list[str]
    avoid: list[str]
    evaluation_dimensions: list[str]
    source_brief: str = ""
    domain: str = "brand_visual"
    tags: list[str] = field(default_factory=list)

    def validate(self) -> None:
        safe_slug(self.slug)
        if not self.title.strip():
            raise ValueError(f"{self.slug}: title is required")
        if not self.source.url.startswith(("https://", "http://")):
            raise ValueError(f"{self.slug}: source.url must be absolute http(s)")
        for field_name in (
            "client",
            "context",
            "budget",
            "timeline",
            "ai_policy",
            "domain",
        ):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{self.slug}: {field_name} is required")
        if self.ai_policy not in AI_POLICIES:
            raise ValueError(f"{self.slug}: unsupported ai_policy {self.ai_policy!r}")
        list_fields = {
            "audience": self.audience,
            "deliverables": self.deliverables,
            "constraints": self.constraints,
            "required_outputs": self.required_outputs,
            "risks": self.risks,
            "avoid": self.avoid,
            "evaluation_dimensions": self.evaluation_dimensions,
        }
        for field_name, value in list_fields.items():
            if not value:
                raise ValueError(f"{self.slug}: {field_name} must not be empty")
        unknown_dimensions = [
            item for item in self.evaluation_dimensions if item not in REVIEW_DIMENSIONS
        ]
        if unknown_dimensions:
            joined = ", ".join(unknown_dimensions)
            raise ValueError(f"{self.slug}: unknown evaluation dimensions: {joined}")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": "0.1",
            "slug": self.slug,
            "title": self.title,
            "source": self.source.to_dict(),
            "client": self.client,
            "context": self.context,
            "audience": list(self.audience),
            "deliverables": [item.to_dict() for item in self.deliverables],
            "constraints": list(self.constraints),
            "budget": self.budget,
            "timeline": self.timeline,
            "required_outputs": list(self.required_outputs),
            "ai_policy": self.ai_policy,
            "simulation_only": self.simulation_only,
            "risks": list(self.risks),
            "avoid": list(self.avoid),
            "evaluation_dimensions": list(self.evaluation_dimensions),
            "source_brief": self.source_brief,
            "domain": self.domain,
            "tags": list(self.tags),
        }
```

Create `src/vulca/real_brief/__init__.py`:

```python
"""Real creative brief benchmark harness."""
from __future__ import annotations

from vulca.real_brief.types import (
    CONDITION_IDS,
    REVIEW_DIMENSIONS,
    Deliverable,
    RealBriefFixture,
    SourceInfo,
    safe_slug,
)

__all__ = [
    "CONDITION_IDS",
    "REVIEW_DIMENSIONS",
    "Deliverable",
    "RealBriefFixture",
    "SourceInfo",
    "safe_slug",
]
```

- [ ] **Step 4: Run tests to verify Task 1 passes**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py -q
```

Expected: PASS for the three Task 1 tests.

- [ ] **Step 5: Commit Task 1**

Run:

```bash
git add src/vulca/real_brief/__init__.py src/vulca/real_brief/types.py tests/test_real_brief_benchmark.py
git commit -m "feat: add real brief benchmark types"
```

---

### Task 2: Built-In Real Brief Fixtures

**Files:**
- Create: `src/vulca/real_brief/fixtures.py`
- Modify: `src/vulca/real_brief/__init__.py`
- Test: `tests/test_real_brief_benchmark.py`

- [ ] **Step 1: Write failing tests for fixture inventory and source hygiene**

Append:

```python
def test_builtin_fixtures_are_valid_and_ordered():
    from vulca.real_brief.fixtures import build_real_brief_fixtures

    fixtures = build_real_brief_fixtures()

    assert [fixture.slug for fixture in fixtures] == [
        "gsm-community-market-campaign",
        "seattle-polish-film-festival-poster",
        "model-young-package-unpacking-taboo",
        "erie-botanical-gardens-public-art",
        "music-video-treatment-low-budget",
    ]
    for fixture in fixtures:
        fixture.validate()
        payload = fixture.to_dict()
        assert payload["schema_version"] == "0.1"
        assert payload["source"]["retrieved_on"] == "2026-04-30"
        assert payload["source"]["usage_note"] == "Internal benchmark only"
        assert payload["simulation_only"] is True


def test_get_real_brief_fixture_rejects_unknown_slug():
    from vulca.real_brief.fixtures import get_real_brief_fixture

    with pytest.raises(ValueError, match="unknown real brief slug"):
        get_real_brief_fixture("missing-brief")


def test_ai_prohibited_fixture_is_marked_for_internal_simulation_only():
    from vulca.real_brief.fixtures import get_real_brief_fixture

    imageout_like = get_real_brief_fixture("seattle-polish-film-festival-poster")

    assert imageout_like.simulation_only is True
    assert imageout_like.source.usage_note == "Internal benchmark only"
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.real_brief.fixtures'`.

- [ ] **Step 3: Implement fixture inventory**

Create `src/vulca/real_brief/fixtures.py` with this structure and these exact fixture slugs:

```python
"""Built-in public creative brief fixtures for the real-brief benchmark."""
from __future__ import annotations

from vulca.real_brief.types import (
    REVIEW_DIMENSIONS,
    Deliverable,
    RealBriefFixture,
    SourceInfo,
    safe_slug,
)


def _dims() -> list[str]:
    return list(REVIEW_DIMENSIONS)


def build_real_brief_fixtures() -> list[RealBriefFixture]:
    return [
        RealBriefFixture(
            slug="gsm-community-market-campaign",
            title="Glenwood Sunday Market Campaign System",
            source=SourceInfo(
                url=(
                    "https://rpba.org/wp-content/uploads/2026/02/"
                    "Marketing-Creative-Services-for-GSM-RFP-2026.pdf"
                ),
                retrieved_on="2026-04-30",
                usage_note="Internal benchmark only",
            ),
            client="Rogers Park Business Alliance / Glenwood Sunday Market",
            context=(
                "Community farmers market marketing system for a 19-week 2026 "
                "market season."
            ),
            audience=[
                "local shoppers",
                "SNAP and matching-program participants",
                "vendors and community partners",
            ],
            deliverables=[
                Deliverable("content framework", "19-week system", "planning"),
                Deliverable("social templates", "editable Canva templates", "social"),
                Deliverable("banner concepts", "market signage", "print"),
                Deliverable("sticker and tote concepts", "merchandise preview", "print"),
            ],
            constraints=[
                "must use existing logo, colors, and fonts",
                "must use real photography",
                "must avoid illustrations and clip art",
                "must remain Canva-editable",
            ],
            budget="$5,000",
            timeline="2026 market season",
            required_outputs=["decision_package", "production_package"],
            ai_policy="unspecified",
            simulation_only=True,
            risks=[
                "generic farmers market aesthetic",
                "template set not reusable for 19 weeks",
                "visual system not editable by the client",
            ],
            avoid=["clip art", "illustration-first campaign", "single poster only"],
            evaluation_dimensions=_dims(),
            source_brief=(
                "Design a reusable community market campaign system with evergreen "
                "templates, real-photo usage rules, social examples, and print/merch "
                "preview assets."
            ),
            domain="brand_visual",
            tags=["campaign", "community", "templates"],
        ),
        RealBriefFixture(
            slug="seattle-polish-film-festival-poster",
            title="Seattle Polish Film Festival Poster",
            source=SourceInfo(
                url="https://www.polishfilms.org/submit-a-poster",
                retrieved_on="2026-04-30",
                usage_note="Internal benchmark only",
            ),
            client="Seattle Polish Film Festival",
            context="Signature poster concept for the 34th festival edition.",
            audience=[
                "festival attendees",
                "Polish cinema community",
                "Seattle arts audience",
            ],
            deliverables=[
                Deliverable("poster concept", "11 x 17 in vertical", "print/digital"),
                Deliverable("program cover adaptation", "same key art", "print"),
            ],
            constraints=[
                "required festival text must be present",
                "dates, venues, website, and producer line must be accounted for",
                "bottom sponsor or patron logo band must remain available",
                "print output should anticipate CMYK and 300 dpi production",
            ],
            budget="not specified by source",
            timeline="source-specific contest deadline",
            required_outputs=["decision_package", "production_package"],
            ai_policy="unspecified",
            simulation_only=True,
            risks=[
                "broken generated text",
                "unsafe margins",
                "generic Polish national symbolism",
                "missing sponsor band",
            ],
            avoid=["illegible typography", "crowded logo area", "flag-only concept"],
            evaluation_dimensions=_dims(),
            source_brief=(
                "Create layout-safe poster concept directions for a Polish film "
                "festival, including required text strategy, margins, sponsor band, "
                "and print-risk notes."
            ),
            domain="poster",
            tags=["poster", "film", "layout"],
        ),
        RealBriefFixture(
            slug="model-young-package-unpacking-taboo",
            title="Model Young Package 2026: Unpacking Taboo",
            source=SourceInfo(
                url=(
                    "https://www.modelgroup.com/language-masters/en/"
                    "model-young-package.html"
                ),
                retrieved_on="2026-04-30",
                usage_note="Internal benchmark only",
            ),
            client="Model Young Package",
            context=(
                "Paper or cardboard packaging concept around sensitive or "
                "stigmatized topics."
            ),
            audience=["competition jury", "design educators", "social-impact brands"],
            deliverables=[
                Deliverable("packaging concept", "paper/cardboard structure", "product"),
                Deliverable("unboxing flow", "step sequence", "prototype planning"),
                Deliverable("structure diagram prompt", "blueprint-style view", "planning"),
            ],
            constraints=[
                "must be respectful toward taboo-adjacent subject matter",
                "must consider manufacturability",
                "must consider sustainability and material economy",
                "must explain function and ergonomics",
            ],
            budget="competition entry; production budget not specified",
            timeline="2026 competition cycle",
            required_outputs=["decision_package", "production_package"],
            ai_policy="unspecified",
            simulation_only=True,
            risks=[
                "sensationalizing sensitive topics",
                "beautiful render without structural logic",
                "unmanufacturable packaging form",
            ],
            avoid=["shock-value visuals", "decorative box only", "plastic-first concept"],
            evaluation_dimensions=_dims(),
            source_brief=(
                "Design a paper-based packaging proposal for a taboo-adjacent "
                "product with respectful concept, structure, unboxing sequence, "
                "material constraints, and prototype-oriented visuals."
            ),
            domain="packaging",
            tags=["packaging", "structure", "social-design"],
        ),
        RealBriefFixture(
            slug="erie-botanical-gardens-public-art",
            title="Buffalo and Erie County Botanical Gardens Public Art",
            source=SourceInfo(
                url=(
                    "https://www4.erie.gov/publicart/"
                    "2026-call-artists-buffalo-and-erie-county-botanical-gardens"
                ),
                retrieved_on="2026-04-30",
                usage_note="Internal benchmark only",
            ),
            client="Erie County / Buffalo and Erie County Botanical Gardens",
            context=(
                "Site-specific public art proposal for a botanical garden setting."
            ),
            audience=["public art panel", "garden visitors", "local community"],
            deliverables=[
                Deliverable("artist proposal", "concept package", "proposal"),
                Deliverable("site-response rationale", "written narrative", "proposal"),
                Deliverable("installation sketch prompts", "visual thumbnails", "planning"),
            ],
            constraints=[
                "must respond to site history and future",
                "must address durability and maintenance",
                "must include installation and engineering assumptions",
                "must respect public access and safety",
            ],
            budget="up to $75,000",
            timeline="2026 public art process",
            required_outputs=["decision_package", "production_package"],
            ai_policy="unspecified",
            simulation_only=True,
            risks=[
                "gallery object rather than site-specific public work",
                "missing maintenance plan",
                "budget fantasy",
            ],
            avoid=["temporary-looking materials", "unanchored decorative sculpture"],
            evaluation_dimensions=_dims(),
            source_brief=(
                "Create a site-specific public art proposal package with concept, "
                "site rationale, material palette, installation assumptions, "
                "maintenance risks, budget notes, and review thumbnails."
            ),
            domain="public_art",
            tags=["public-art", "site-specific", "proposal"],
        ),
        RealBriefFixture(
            slug="music-video-treatment-low-budget",
            title="Low-Budget Music Video Treatment",
            source=SourceInfo(
                url="https://creative-commission.com/briefs/brief-10642",
                retrieved_on="2026-04-30",
                usage_note="Internal benchmark only",
            ),
            client="Music artist / label brief",
            context=(
                "Director or producer treatment for a low-budget music video, "
                "with AI elements allowed by the brief."
            ),
            audience=["artist team", "label commissioner", "director shortlist panel"],
            deliverables=[
                Deliverable("director treatment", "written concept", "pitch"),
                Deliverable("mood frames", "visual references", "pitch"),
                Deliverable("scene beats", "sequence outline", "production planning"),
            ],
            constraints=[
                "must fit low-budget execution",
                "must disclose AI-use approach",
                "must not assume expensive locations or large crew",
                "must avoid asking for unpaid full treatment before shortlist",
            ],
            budget="about GBP 1,000",
            timeline="source-specific commission window",
            required_outputs=["decision_package", "production_package"],
            ai_policy="allowed",
            simulation_only=True,
            risks=[
                "overproduced concept",
                "moodboard without executable scenes",
                "unclear AI disclosure",
            ],
            avoid=["large crew assumptions", "expensive VFX-heavy production"],
            evaluation_dimensions=_dims(),
            source_brief=(
                "Simulate a shortlisted director treatment with concept, mood "
                "frames, scene structure, production constraints, AI-use disclosure, "
                "and deliverables plan."
            ),
            domain="video_treatment",
            tags=["video", "treatment", "low-budget"],
        ),
    ]


def get_real_brief_fixture(slug: str) -> RealBriefFixture:
    safe = safe_slug(slug)
    for fixture in build_real_brief_fixtures():
        if fixture.slug == safe:
            return fixture
    known = ", ".join(fixture.slug for fixture in build_real_brief_fixtures())
    raise ValueError(f"unknown real brief slug: {slug!r}; expected one of: {known}")
```

Update `src/vulca/real_brief/__init__.py`:

```python
from vulca.real_brief.fixtures import (
    build_real_brief_fixtures,
    get_real_brief_fixture,
)

__all__ += [
    "build_real_brief_fixtures",
    "get_real_brief_fixture",
]
```

- [ ] **Step 4: Run tests to verify Task 2 passes**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py -q
```

Expected: PASS for Task 1 and Task 2 tests.

- [ ] **Step 5: Commit Task 2**

Run:

```bash
git add src/vulca/real_brief/__init__.py src/vulca/real_brief/fixtures.py tests/test_real_brief_benchmark.py
git commit -m "feat: add real brief benchmark fixtures"
```

---

### Task 3: A/B/C/D Condition Generation

**Files:**
- Create: `src/vulca/real_brief/conditions.py`
- Modify: `src/vulca/real_brief/__init__.py`
- Test: `tests/test_real_brief_benchmark.py`

- [ ] **Step 1: Write failing tests for condition generation**

Append:

```python
def test_build_real_brief_conditions_a_through_d():
    from vulca.real_brief.conditions import build_real_brief_conditions
    from vulca.real_brief.fixtures import get_real_brief_fixture

    fixture = get_real_brief_fixture("seattle-polish-film-festival-poster")
    conditions = build_real_brief_conditions(fixture)

    assert [condition["id"] for condition in conditions] == ["A", "B", "C", "D"]
    assert conditions[0]["label"] == "One-shot model baseline"
    assert "Raw real brief" in conditions[0]["purpose"]
    assert "Required deliverables" in conditions[1]["prompt"]
    assert "Missing questions" in conditions[2]["prompt"]
    assert "Preview plan" in conditions[3]["prompt"]
    assert conditions[3]["workflow_stage"] == "vulca-preview-iterate"


def test_condition_generation_preserves_fixture_constraints():
    from vulca.real_brief.conditions import build_real_brief_conditions
    from vulca.real_brief.fixtures import get_real_brief_fixture

    fixture = get_real_brief_fixture("gsm-community-market-campaign")
    conditions = build_real_brief_conditions(fixture)
    joined = "\n".join(condition["prompt"] for condition in conditions)

    assert "Canva-editable" in joined
    assert "real photography" in joined
    assert "19-week" in joined
    assert "clip art" in joined
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.real_brief.conditions'`.

- [ ] **Step 3: Implement condition generation**

Create `src/vulca/real_brief/conditions.py`:

```python
"""A/B/C/D condition generation for real-brief benchmarks."""
from __future__ import annotations

from typing import Any

from vulca.discovery.cards import generate_direction_cards
from vulca.discovery.profile import infer_taste_profile
from vulca.discovery.prompting import compose_prompt_from_direction_card
from vulca.real_brief.types import CONDITION_IDS, RealBriefFixture


def _lines(title: str, values: list[str]) -> str:
    return f"{title}:\n" + "\n".join(f"- {item}" for item in values)


def brief_digest(fixture: RealBriefFixture) -> str:
    deliverables = [
        f"{item.name} ({item.format}, {item.channel})"
        for item in fixture.deliverables
    ]
    return "\n".join(
        [
            f"Client: {fixture.client}",
            f"Context: {fixture.context}",
            _lines("Audience", fixture.audience),
            _lines("Required deliverables", deliverables),
            _lines("Constraints", fixture.constraints),
            f"Budget: {fixture.budget}",
            f"Timeline: {fixture.timeline}",
            _lines("Risks", fixture.risks),
            _lines("Avoid", fixture.avoid),
            f"AI policy: {fixture.ai_policy}",
            f"Simulation only: {fixture.simulation_only}",
        ]
    )


def _direction_text(fixture: RealBriefFixture) -> dict[str, Any]:
    intent = f"{fixture.title}. {fixture.source_brief} {brief_digest(fixture)}"
    profile = infer_taste_profile(slug=fixture.slug, intent=intent)
    cards = generate_direction_cards(profile, count=3)
    selected = cards[0]
    prompt = compose_prompt_from_direction_card(selected, target="final")
    return {
        "profile": profile.to_dict(),
        "cards": [card.to_dict() for card in cards],
        "selected_card": selected.to_dict(),
        "compiled_prompt": prompt.to_dict(),
    }


def build_real_brief_conditions(fixture: RealBriefFixture) -> list[dict[str, Any]]:
    fixture.validate()
    digest = brief_digest(fixture)
    direction = _direction_text(fixture)
    selected = direction["selected_card"]
    compiled = direction["compiled_prompt"]
    conditions = [
        {
            "id": "A",
            "label": "One-shot model baseline",
            "workflow_stage": "one-shot",
            "purpose": "Raw real brief condensed into a single model ask.",
            "prompt": (
                f"Create the requested creative output for this real brief.\n\n{digest}\n\n"
                "Return a polished concept and any visual prompt needed to generate it."
            ),
        },
        {
            "id": "B",
            "label": "Structured brief baseline",
            "workflow_stage": "structured-brief",
            "purpose": "Same brief normalized into structured client, deliverable, and constraint fields.",
            "prompt": (
                "Create a direction from the structured brief below.\n\n"
                f"{digest}\n\n"
                "Success criteria:\n"
                "- satisfy required deliverables\n"
                "- respect every listed constraint\n"
                "- identify the most production-relevant risk"
            ),
        },
        {
            "id": "C",
            "label": "Vulca planning workflow",
            "workflow_stage": "vulca-planning",
            "purpose": "Vulca-style ambiguity detection, direction cards, visual operations, and evaluation focus.",
            "prompt": (
                "Build a Vulca planning package before generating final pixels.\n\n"
                f"{digest}\n\n"
                "Missing questions:\n"
                "- Which stakeholder approves the final direction?\n"
                "- Which deliverable must be most production-ready first?\n"
                "- Which source assets already exist?\n\n"
                f"Selected direction card: {selected['label']}\n"
                f"Direction summary: {selected['summary']}\n"
                f"Visual operations: {selected['visual_ops']}\n"
                f"Evaluation focus: {selected['evaluation_focus']}"
            ),
        },
        {
            "id": "D",
            "label": "Vulca preview-and-iterate workflow",
            "workflow_stage": "vulca-preview-iterate",
            "purpose": "Planning package plus preview prompts, critique pass, refined prompt, and editability notes.",
            "prompt": (
                "Build a Vulca preview-and-iterate package for this brief.\n\n"
                f"{digest}\n\n"
                "Preview plan:\n"
                "- produce 2-3 low-cost thumbnail directions before final comp\n"
                "- critique each direction against constraints and risks\n"
                "- refine the strongest direction into a final comp prompt\n"
                "- document editability, redraw, and reuse notes\n\n"
                f"Final comp prompt: {compiled['prompt']}\n"
                f"Negative prompt: {compiled['negative_prompt']}"
            ),
        },
    ]
    assert tuple(item["id"] for item in conditions) == CONDITION_IDS
    return conditions
```

Update exports in `src/vulca/real_brief/__init__.py`:

```python
from vulca.real_brief.conditions import (
    brief_digest,
    build_real_brief_conditions,
)

__all__ += [
    "brief_digest",
    "build_real_brief_conditions",
]
```

- [ ] **Step 4: Run tests to verify Task 3 passes**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py -q
```

Expected: PASS for Task 1 through Task 3 tests.

- [ ] **Step 5: Commit Task 3**

Run:

```bash
git add src/vulca/real_brief/__init__.py src/vulca/real_brief/conditions.py tests/test_real_brief_benchmark.py
git commit -m "feat: generate real brief benchmark conditions"
```

---

### Task 4: Dry-Run Artifact Writer

**Files:**
- Create: `src/vulca/real_brief/artifacts.py`
- Modify: `src/vulca/real_brief/__init__.py`
- Test: `tests/test_real_brief_benchmark.py`

- [ ] **Step 1: Write failing tests for artifact tree and contracts**

Append:

```python
def test_write_real_brief_dry_run_artifacts(tmp_path):
    from vulca.real_brief.artifacts import write_real_brief_dry_run

    result = write_real_brief_dry_run(
        output_root=tmp_path,
        slug="seattle-polish-film-festival-poster",
        date="2026-05-01",
        write_html_review=False,
    )

    out_dir = Path(result["output_dir"])
    assert out_dir == tmp_path / "2026-05-01-seattle-polish-film-festival-poster"
    for rel in [
        "source_brief.md",
        "structured_brief.json",
        "decision_package.md",
        "production_package.md",
        "workflow_handoff.json",
        "review_schema.json",
        "conditions/A-one-shot.md",
        "conditions/B-structured-brief.md",
        "conditions/C-vulca-planning.md",
        "conditions/D-vulca-preview-iterate.md",
        "prompts/A.txt",
        "prompts/B.txt",
        "prompts/C.txt",
        "prompts/D.txt",
        "images/README.md",
        "evaluations/README.md",
        "summary.md",
        "manifest.json",
    ]:
        assert (out_dir / rel).exists(), rel

    handoff = json.loads((out_dir / "workflow_handoff.json").read_text())
    assert handoff["schema_version"] == "0.1"
    assert handoff["human_gate_required"] is True
    assert handoff["visual_discovery_seed"]["slug"] == (
        "seattle-polish-film-festival-poster"
    )
    assert handoff["visual_brainstorm_seed"]["domain"] == "poster"

    review = json.loads((out_dir / "review_schema.json").read_text())
    assert review["scale"] == {"min": 0, "max": 2, "step": 1}
    assert "decision_usefulness" in [d["id"] for d in review["dimensions"]]

    summary = (out_dir / "summary.md").read_text(encoding="utf-8")
    assert "No image quality conclusion" in summary
    assert "simulation_only: true" in summary


def test_write_real_brief_dry_run_rejects_secret_like_output_root(tmp_path):
    from vulca.real_brief.artifacts import write_real_brief_dry_run

    out = tmp_path / "safe-output"
    write_real_brief_dry_run(
        output_root=out,
        slug="gsm-community-market-campaign",
        date="2026-05-01",
        write_html_review=False,
    )
    generated = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in out.rglob("*")
        if path.is_file() and path.suffix in {".md", ".json", ".txt", ".html"}
    )
    assert "sk-" not in generated
    assert "VULCA_REAL_PROVIDER_API_KEY" not in generated
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.real_brief.artifacts'`.

- [ ] **Step 3: Implement artifact writer**

Create `src/vulca/real_brief/artifacts.py`:

```python
"""Artifact writing for real-brief benchmark dry runs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vulca.real_brief.conditions import build_real_brief_conditions
from vulca.real_brief.fixtures import get_real_brief_fixture
from vulca.real_brief.types import REVIEW_DIMENSIONS, RealBriefFixture, safe_slug


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _review_schema() -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "scale": {"min": 0, "max": 2, "step": 1},
        "condition_ids": ["A", "B", "C", "D"],
        "dimensions": [
            {
                "id": item,
                "label": item.replace("_", " ").title(),
                "description": f"Score {item.replace('_', ' ')} for real brief usefulness.",
            }
            for item in REVIEW_DIMENSIONS
        ],
    }


def _source_brief_md(fixture: RealBriefFixture) -> str:
    return f"""# Source Brief: {fixture.title}

## Source
- URL: {fixture.source.url}
- Retrieved on: {fixture.source.retrieved_on}
- Usage note: {fixture.source.usage_note}

## Client
{fixture.client}

## Context
{fixture.context}

## Source Brief
{fixture.source_brief}

## Constraints
{chr(10).join(f"- {item}" for item in fixture.constraints)}

## Risks
{chr(10).join(f"- {item}" for item in fixture.risks)}
"""


def _decision_package_md(fixture: RealBriefFixture) -> str:
    directions = [
        "Direction 1: compliance-first system",
        "Direction 2: audience-empathy narrative",
        "Direction 3: production-ready visual structure",
    ]
    return f"""# Decision Package: {fixture.title}

## Brief Digest
{fixture.context}

## Assumptions
- Existing brand/source assets may be incomplete at benchmark time.
- Generated outputs are internal simulation artifacts.
- Human approval remains required before any official `/visual-*` workflow advances.

## Missing Questions
- Which stakeholder makes the final decision?
- Which deliverable must be production-ready first?
- Which source assets are available?

## Creative Directions
{chr(10).join(f"- {item}" for item in directions)}

## Direction Rationale
The recommended route should privilege brief compliance, constraint handling,
and decision usefulness over raw visual attractiveness.

## Risks And Rejected Approaches
{chr(10).join(f"- Avoid {item}" for item in fixture.avoid)}

## Recommended Direction
Direction 3: production-ready visual structure.

## Decision Checklist
- [ ] Required deliverables are represented.
- [ ] Constraints are visible in the proposed direction.
- [ ] Risks are named before generation.
- [ ] Next production step is clear.
"""


def _production_package_md(fixture: RealBriefFixture, conditions: list[dict[str, Any]]) -> str:
    prompt_packet = "\n".join(
        f"- {condition['id']}: prompts/{condition['id']}.txt"
        for condition in conditions
    )
    deliverables = "\n".join(
        f"- {item.name}: {item.format} for {item.channel}"
        for item in fixture.deliverables
    )
    return f"""# Production Package: {fixture.title}

## Selected Direction
Production-ready visual structure.

## Prompt Packet
{prompt_packet}

## Visual Operations
- Build around the required deliverables, not a single decorative image.
- Keep constraints visible in composition and copy hierarchy.
- Use preview prompts before final comp generation.

## Layout And Structure Constraints
{chr(10).join(f"- {item}" for item in fixture.constraints)}

## Channel And Deliverable Constraints
{deliverables}

## Preview Or Thumbnail Plan
- Generate rough previews for A/B/C/D only after explicit real-provider opt-in.
- Compare previews against review_schema.json before selecting a final comp.

## Evaluation Checklist
{chr(10).join(f"- {item}" for item in REVIEW_DIMENSIONS)}

## Editability And Reusability Notes
- Prefer reusable systems over one-off hero images.
- Preserve prompt and package provenance for later Studio rendering.

## Redraw And Layer Notes
- Do not depend on v0.22 mask refinement in Phase 1.
- Record likely redraw targets for future `/redraw-layer` integration.

## Next Iteration Plan
- Collect human review scores.
- Promote strongest condition into official workflow adapter in Phase 2.
"""


def _workflow_handoff(fixture: RealBriefFixture) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "slug": fixture.slug,
        "structured_brief_path": "structured_brief.json",
        "visual_discovery_seed": {
            "slug": fixture.slug,
            "title": fixture.title,
            "initial_intent": fixture.source_brief,
            "domain": fixture.domain,
        },
        "visual_brainstorm_seed": {
            "slug": fixture.slug,
            "domain": fixture.domain,
            "physical_form": [item.to_dict() for item in fixture.deliverables],
            "constraints": list(fixture.constraints),
        },
        "visual_spec_seed": {
            "evaluation_dimensions": list(fixture.evaluation_dimensions),
            "provider_policy": "dry_run_default",
        },
        "visual_plan_seed": {
            "condition_ids": ["A", "B", "C", "D"],
            "requires_explicit_real_provider_opt_in": True,
        },
        "evaluate_seed": {
            "review_schema_path": "review_schema.json",
            "mode": "brief_compliance",
        },
        "human_gate_required": True,
    }


def _condition_filename(condition: dict[str, Any]) -> str:
    suffix = {
        "A": "one-shot",
        "B": "structured-brief",
        "C": "vulca-planning",
        "D": "vulca-preview-iterate",
    }[condition["id"]]
    return f"{condition['id']}-{suffix}.md"


def write_real_brief_dry_run(
    *,
    output_root: str | Path,
    slug: str,
    date: str,
    write_html_review: bool = True,
) -> dict[str, str]:
    fixture = get_real_brief_fixture(safe_slug(slug))
    conditions = build_real_brief_conditions(fixture)
    out_dir = Path(output_root) / f"{date}-{fixture.slug}"
    prompts_dir = out_dir / "prompts"
    conditions_dir = out_dir / "conditions"
    images_dir = out_dir / "images"
    evaluations_dir = out_dir / "evaluations"
    for directory in (prompts_dir, conditions_dir, images_dir, evaluations_dir):
        directory.mkdir(parents=True, exist_ok=True)

    _write_text(out_dir / "source_brief.md", _source_brief_md(fixture))
    _write_json(out_dir / "structured_brief.json", fixture.to_dict())
    _write_text(out_dir / "decision_package.md", _decision_package_md(fixture))
    _write_text(
        out_dir / "production_package.md",
        _production_package_md(fixture, conditions),
    )
    _write_json(out_dir / "workflow_handoff.json", _workflow_handoff(fixture))
    _write_json(out_dir / "review_schema.json", _review_schema())

    for condition in conditions:
        _write_text(prompts_dir / f"{condition['id']}.txt", condition["prompt"])
        _write_text(
            conditions_dir / _condition_filename(condition),
            f"# {condition['label']}\n\n"
            f"## Purpose\n{condition['purpose']}\n\n"
            f"## Prompt\n{condition['prompt']}\n",
        )

    _write_text(
        images_dir / "README.md",
        "# Images\n\nDry run only. No provider images were generated.\n",
    )
    _write_text(
        evaluations_dir / "README.md",
        "# Evaluations\n\nDry run only. Run evaluation after real images exist.\n",
    )
    manifest = {
        "schema_version": "0.1",
        "experiment": "real-brief-benchmark",
        "mode": "dry_run",
        "provider_execution": "disabled",
        "fixture": {"slug": fixture.slug, "title": fixture.title},
        "conditions": [
            {
                "id": condition["id"],
                "label": condition["label"],
                "condition_path": f"conditions/{_condition_filename(condition)}",
                "prompt_path": f"prompts/{condition['id']}.txt",
            }
            for condition in conditions
        ],
        "review_schema_path": "review_schema.json",
        "workflow_handoff_path": "workflow_handoff.json",
    }
    _write_json(out_dir / "manifest.json", manifest)
    summary = f"""# Real Brief Benchmark Dry Run: {fixture.slug}

## Status
dry_run

## Fixture
{fixture.title}

## Simulation
simulation_only: {str(fixture.simulation_only).lower()}
ai_policy: {fixture.ai_policy}

## Conditions
{chr(10).join(f"- {item['id']}: {item['label']}" for item in conditions)}

## Decision Boundary
No image quality conclusion can be drawn from this dry run. It validates
brief structure, workflow handoff, review schema, prompts, and package shape.
"""
    _write_text(out_dir / "summary.md", summary)

    if write_html_review:
        from vulca.real_brief.review_html import write_review_html

        write_review_html(out_dir)

    return {
        "output_dir": str(out_dir),
        "manifest_json": str(out_dir / "manifest.json"),
        "summary_md": str(out_dir / "summary.md"),
    }
```

Update exports in `src/vulca/real_brief/__init__.py`:

```python
from vulca.real_brief.artifacts import write_real_brief_dry_run

__all__ += ["write_real_brief_dry_run"]
```

- [ ] **Step 4: Run tests to verify Task 4 passes**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py -q
```

Expected: PASS through Task 4 tests when `write_html_review=False`.

- [ ] **Step 5: Commit Task 4**

Run:

```bash
git add src/vulca/real_brief/__init__.py src/vulca/real_brief/artifacts.py tests/test_real_brief_benchmark.py
git commit -m "feat: write real brief benchmark artifacts"
```

---

### Task 5: Local HTML Review Surface

**Files:**
- Create: `src/vulca/real_brief/review_html.py`
- Test: `tests/test_real_brief_benchmark.py`

- [ ] **Step 1: Write failing tests for HTML review rendering**

Append:

```python
def test_human_review_html_contains_conditions_dimensions_and_export(tmp_path):
    from vulca.real_brief.artifacts import write_real_brief_dry_run

    result = write_real_brief_dry_run(
        output_root=tmp_path,
        slug="model-young-package-unpacking-taboo",
        date="2026-05-01",
        write_html_review=True,
    )

    html = Path(result["output_dir"], "human_review.html").read_text(encoding="utf-8")
    assert "Real Brief Benchmark Review" in html
    assert "A-one-shot.md" in html
    assert "D-vulca-preview-iterate.md" in html
    assert "brief_compliance" in html
    assert "decision_usefulness" in html
    assert "Export JSON" in html
    assert "sk-" not in html
    assert "VULCA_REAL_PROVIDER_API_KEY" not in html
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py::test_human_review_html_contains_conditions_dimensions_and_export -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.real_brief.review_html'`.

- [ ] **Step 3: Implement HTML renderer**

Create `src/vulca/real_brief/review_html.py`:

```python
"""Static HTML review board for real-brief benchmark artifacts."""
from __future__ import annotations

import html
import json
from pathlib import Path


def write_review_html(out_dir: str | Path) -> Path:
    root = Path(out_dir)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    review = json.loads((root / "review_schema.json").read_text(encoding="utf-8"))
    structured = json.loads((root / "structured_brief.json").read_text(encoding="utf-8"))
    condition_cards = "\n".join(
        f"""
        <article class="condition" data-condition="{html.escape(condition['id'])}">
          <h3>{html.escape(condition['id'])}: {html.escape(condition['label'])}</h3>
          <p><a href="{html.escape(condition['condition_path'])}">{html.escape(condition['condition_path'])}</a></p>
          <p><a href="{html.escape(condition['prompt_path'])}">{html.escape(condition['prompt_path'])}</a></p>
        </article>
        """
        for condition in manifest["conditions"]
    )
    metric_rows = "\n".join(
        f"""
        <label class="metric">
          <span>{html.escape(item['id'])}</span>
          <select data-field="{html.escape(item['id'])}">
            <option></option>
            <option value="0">0 weak</option>
            <option value="1">1 usable</option>
            <option value="2">2 strong</option>
          </select>
        </label>
        """
        for item in review["dimensions"]
    )
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Real Brief Benchmark Review</title>
  <style>
    body {{ margin: 0; font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #1f2428; background: #f7f7f4; }}
    header, main {{ max-width: 1280px; margin: 0 auto; padding: 22px; }}
    header {{ border-bottom: 1px solid #d9ded8; }}
    h1 {{ margin: 0 0 8px; font-size: 26px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(180px, 1fr)); gap: 12px; }}
    .condition, .panel {{ border: 1px solid #d9ded8; border-radius: 8px; background: white; padding: 14px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(2, minmax(220px, 1fr)); gap: 10px; }}
    .metric {{ display: grid; grid-template-columns: 1fr 90px; gap: 8px; align-items: center; }}
    select, textarea {{ width: 100%; border: 1px solid #d9ded8; border-radius: 6px; font: inherit; }}
    textarea {{ min-height: 90px; padding: 8px; }}
    button {{ border: 1px solid #0d5f59; border-radius: 6px; background: #0f766e; color: white; padding: 9px 12px; font-weight: 700; }}
    pre {{ white-space: pre-wrap; background: #101418; color: #e6edf3; padding: 14px; border-radius: 8px; }}
    @media (max-width: 900px) {{ .grid, .metrics {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Real Brief Benchmark Review</h1>
    <p>{html.escape(structured['title'])}</p>
    <p>Score A/B/C/D on workflow usefulness, not raw image beauty.</p>
  </header>
  <main>
    <section class="panel">
      <h2>Brief</h2>
      <p><strong>Client:</strong> {html.escape(structured['client'])}</p>
      <p><strong>Context:</strong> {html.escape(structured['context'])}</p>
      <p><strong>AI policy:</strong> {html.escape(structured['ai_policy'])}</p>
    </section>
    <section>
      <h2>Conditions</h2>
      <div class="grid">{condition_cards}</div>
    </section>
    <section class="panel">
      <h2>Review Dimensions</h2>
      <div class="metrics">{metric_rows}</div>
      <h3>Notes</h3>
      <textarea data-field="notes"></textarea>
      <p><button id="exportBtn">Export JSON</button></p>
      <pre id="output">{{}}</pre>
    </section>
  </main>
  <script>
    const storageKey = "vulca-real-brief-review-" + {json.dumps(structured['slug'])};
    function collect() {{
      const data = {{ slug: {json.dumps(structured['slug'])}, scores: {{}}, notes: "" }};
      document.querySelectorAll("[data-field]").forEach((field) => {{
        if (field.dataset.field === "notes") data.notes = field.value || "";
        else data.scores[field.dataset.field] = field.value || "";
      }});
      return data;
    }}
    function save() {{ localStorage.setItem(storageKey, JSON.stringify(collect())); }}
    function load() {{
      const raw = localStorage.getItem(storageKey);
      if (!raw) return;
      const data = JSON.parse(raw);
      document.querySelectorAll("[data-field]").forEach((field) => {{
        if (field.dataset.field === "notes") field.value = data.notes || "";
        else field.value = (data.scores && data.scores[field.dataset.field]) || "";
      }});
    }}
    document.addEventListener("input", save);
    document.addEventListener("change", save);
    document.getElementById("exportBtn").addEventListener("click", async () => {{
      const text = JSON.stringify(collect(), null, 2);
      document.getElementById("output").textContent = text;
      try {{ await navigator.clipboard.writeText(text); }} catch (error) {{}}
    }});
    load();
  </script>
</body>
</html>
"""
    path = root / "human_review.html"
    path.write_text(page, encoding="utf-8")
    return path
```

- [ ] **Step 4: Run tests to verify Task 5 passes**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py -q
```

Expected: PASS through Task 5 tests.

- [ ] **Step 5: Commit Task 5**

Run:

```bash
git add src/vulca/real_brief/review_html.py tests/test_real_brief_benchmark.py
git commit -m "feat: render real brief review board"
```

---

### Task 6: CLI And Docs Link

**Files:**
- Create: `scripts/real_brief_benchmark.py`
- Modify: `docs/product/experiments/cultural-term-efficacy.md`
- Test: `tests/test_real_brief_benchmark.py`

- [ ] **Step 1: Write failing tests for CLI dry-run and fail-closed real-provider mode**

Append:

```python
def test_real_brief_benchmark_cli_writes_all_slugs(tmp_path):
    from scripts.real_brief_benchmark import main

    rc = main([
        "--slug",
        "all",
        "--date",
        "2026-05-01",
        "--output-root",
        str(tmp_path),
        "--no-html-review",
    ])

    assert rc == 0
    assert (tmp_path / "2026-05-01-gsm-community-market-campaign").exists()
    assert (tmp_path / "2026-05-01-music-video-treatment-low-budget").exists()


def test_real_brief_benchmark_cli_real_provider_fails_closed(tmp_path):
    from scripts.real_brief_benchmark import main

    with pytest.raises(RuntimeError, match="not implemented"):
        main([
            "--slug",
            "gsm-community-market-campaign",
            "--date",
            "2026-05-01",
            "--output-root",
            str(tmp_path),
            "--real-provider",
        ])
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py::test_real_brief_benchmark_cli_writes_all_slugs tests/test_real_brief_benchmark.py::test_real_brief_benchmark_cli_real_provider_fails_closed -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.real_brief_benchmark'`.

- [ ] **Step 3: Implement CLI**

Create `scripts/real_brief_benchmark.py`:

```python
"""CLI for writing real-brief benchmark dry-run artifacts."""
from __future__ import annotations

import argparse
from datetime import date as date_type
from pathlib import Path

from vulca.real_brief.artifacts import write_real_brief_dry_run
from vulca.real_brief.fixtures import build_real_brief_fixtures, get_real_brief_fixture


def _slugs(raw: str) -> list[str]:
    if raw == "all":
        return [fixture.slug for fixture in build_real_brief_fixtures()]
    get_real_brief_fixture(raw)
    return [raw]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write real-brief benchmark dry-run artifacts."
    )
    parser.add_argument("--slug", default="all")
    parser.add_argument("--date", default=date_type.today().isoformat())
    parser.add_argument(
        "--output-root",
        default="docs/product/experiments/real-brief-results",
    )
    parser.add_argument("--real-provider", action="store_true")
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--max-images", type=int, default=0)
    parser.add_argument("--write-html-review", action="store_true", default=True)
    parser.add_argument("--no-html-review", action="store_true")
    args = parser.parse_args(argv)

    if args.real_provider:
        raise RuntimeError(
            "real-provider execution is not implemented for real-brief benchmark "
            "Phase 1; dry-run artifacts are available without credentials"
        )
    if args.provider not in {"openai", "gemini", "comfyui"}:
        raise ValueError("provider must be one of: openai, gemini, comfyui")
    if args.max_images < 0:
        raise ValueError("max-images must be >= 0")

    write_html = args.write_html_review and not args.no_html_review
    for slug in _slugs(args.slug):
        write_real_brief_dry_run(
            output_root=Path(args.output_root),
            slug=slug,
            date=args.date,
            write_html_review=write_html,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Add docs link from cultural-term experiment**

Append to `docs/product/experiments/cultural-term-efficacy.md`:

````markdown

## Successor: Real-Brief Benchmark

The cultural-term experiment is a prompt-signal test. It is intentionally weaker
than a real creative brief because strong image models can make broad prompts
look good. The successor benchmark is `scripts/real_brief_benchmark.py`, which
uses public creative briefs/RFPs and evaluates workflow usefulness, constraint
handling, production realism, and decision quality.

Dry run:

```bash
PYTHONPATH=src python3 scripts/real_brief_benchmark.py \
  --date 2026-05-01 \
  --slug all \
  --output-root docs/product/experiments/real-brief-results
```
````

- [ ] **Step 5: Run tests to verify Task 6 passes**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py -q
```

Expected: PASS through Task 6 tests.

- [ ] **Step 6: Commit Task 6**

Run:

```bash
git add scripts/real_brief_benchmark.py docs/product/experiments/cultural-term-efficacy.md tests/test_real_brief_benchmark.py
git commit -m "feat: add real brief benchmark CLI"
```

---

### Task 7: End-To-End Dry Run And Regression Verification

**Files:**
- Modify only if verification reveals a defect in files created by Tasks 1-6.

- [ ] **Step 1: Run focused real-brief tests**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py -q
```

Expected: all tests pass.

- [ ] **Step 2: Run existing visual discovery regression tests**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_visual_discovery_benchmark.py tests/test_visual_discovery_artifacts.py tests/test_visual_discovery_cards.py tests/test_visual_discovery_types.py -q
```

Expected: all tests pass.

- [ ] **Step 3: Run dry-run CLI into a temporary output root**

Run:

```bash
PYTHONPATH=src python3 scripts/real_brief_benchmark.py \
  --date 2026-05-01 \
  --slug all \
  --output-root /private/tmp/vulca-real-brief-benchmark-check
```

Expected:

- five output directories under `/private/tmp/vulca-real-brief-benchmark-check`;
- each contains `structured_brief.json`, `decision_package.md`, `production_package.md`, `workflow_handoff.json`, `review_schema.json`, `manifest.json`, and `summary.md`;
- `summary.md` says no image quality conclusion can be drawn.

- [ ] **Step 4: Scan temporary artifacts for secret-like strings**

Run:

```bash
grep -R -n -E "sk-|VULCA_REAL_PROVIDER_API_KEY|OPENAI_API_KEY|globalai" /private/tmp/vulca-real-brief-benchmark-check
```

Expected: exit code 1 and no matches.

- [ ] **Step 5: Inspect git status**

Run:

```bash
git status --short
```

Expected: only intended files from Tasks 1-6 are tracked or modified before the final commit.

- [ ] **Step 6: Commit final verification fixes if any were needed**

If Task 7 required code changes, run:

```bash
git add src/vulca/real_brief scripts/real_brief_benchmark.py tests/test_real_brief_benchmark.py docs/product/experiments/cultural-term-efficacy.md
git commit -m "test: verify real brief benchmark harness"
```

If no code changes were needed, do not create an empty commit.

---

## Final Verification Checklist

Before claiming implementation complete, run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py -q
PYTHONPATH=src python3 -m pytest tests/test_visual_discovery_benchmark.py tests/test_visual_discovery_artifacts.py tests/test_visual_discovery_cards.py tests/test_visual_discovery_types.py -q
PYTHONPATH=src python3 scripts/real_brief_benchmark.py --date 2026-05-01 --slug all --output-root /private/tmp/vulca-real-brief-benchmark-check
grep -R -n -E "sk-|VULCA_REAL_PROVIDER_API_KEY|OPENAI_API_KEY|globalai" /private/tmp/vulca-real-brief-benchmark-check
```

Expected:

- focused real-brief tests pass;
- existing visual discovery tests pass;
- dry-run CLI writes five brief directories;
- grep exits 1 with no secret-like matches.

## Spec Coverage Review

- Real brief fixtures: Task 2.
- Structured brief schema: Task 1 and Task 4.
- A/B/C/D conditions: Task 3 and Task 4.
- Decision package: Task 4.
- Production package: Task 4.
- Workflow handoff bridge for Phase 2: Task 4.
- Review schema bridge for Phase 3: Task 4.
- Local HTML review surface: Task 5.
- CLI dry-run: Task 6.
- Real-provider fail-closed behavior: Task 6.
- No redraw/v0.22 dependency: File structure and Task 4 package text.
- No secrets in artifacts: Task 4 test and Task 7 scan.
