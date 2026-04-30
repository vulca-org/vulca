# Visual Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `/visual-discovery` as the upstream creative-direction layer for Vulca's existing `/visual-brainstorm -> /visual-spec -> /visual-plan` workflow.

**Architecture:** Keep Vulca agent-native: the skill handles dialogue and judgment, while small Python modules provide deterministic schemas, current-state tripwires, tradition-term expansion, prompt composition, artifact writing, and benchmark scaffolding. Discovery produces auditable artifacts under `docs/visual-specs/<slug>/discovery/`; it does not execute real generation unless the user explicitly opts into exploratory sketches.

**Tech Stack:** Python 3.10+, dataclasses, stdlib `json`/`pathlib`, existing `vulca.cultural.loader`, existing `vulca.prompting.compose_prompt_from_design` conventions, pytest, markdown skills under `.agents/skills/`.

---

## Source Spec

- Product spec: `docs/superpowers/specs/2026-04-29-visual-discovery-design.md`
- Existing skill router: `.agents/skills/using-vulca-skills/SKILL.md`
- Existing downstream skills:
  - `.agents/skills/visual-brainstorm/SKILL.md`
  - `.agents/skills/visual-spec/SKILL.md`
  - `.agents/skills/visual-plan/SKILL.md`
- Existing prompt composer: `src/vulca/prompting.py`
- Existing MCP server: `src/vulca/mcp_server.py`

---

## File Structure

Create a focused `vulca.discovery` package. It should contain deterministic helpers only; do not hide agent reasoning or call external image providers from this package.

- Create: `src/vulca/discovery/__init__.py`
  - Public exports for schemas, term expansion, card generation, prompt composition, and artifact writing.
- Create: `src/vulca/discovery/types.py`
  - Dataclasses and validation helpers: `ProviderTarget`, `VisualOps`, `EvaluationFocus`, `DirectionCard`, `TasteProfile`, `SketchPrompt`, `PromptArtifact`.
- Create: `src/vulca/discovery/terms.py`
  - Convert existing tradition YAML terminology and taboos into explicit visual operation hints.
- Create: `src/vulca/discovery/profile.py`
  - Rule-based project profile inference from fuzzy intent.
- Create: `src/vulca/discovery/cards.py`
  - Deterministic direction-card generation and blend/update helpers.
- Create: `src/vulca/discovery/prompting.py`
  - `compose_prompt_from_direction_card`, following `compose_prompt_from_design` artifact-first style.
- Create: `src/vulca/discovery/artifacts.py`
  - Write `discovery.md`, `taste_profile.json`, `direction_cards.json`, and optional `sketch_prompts.json`.
- Create: `.agents/skills/visual-discovery/SKILL.md`
  - Agent-facing workflow, schemas, tool whitelist, bans, turn cap, and handoff string.
- Modify: `.agents/skills/using-vulca-skills/SKILL.md`
  - Add `/visual-discovery` routing before `/visual-brainstorm` when the user's intent is fuzzy or exploratory.
- Create: `scripts/visual_discovery_benchmark.py`
  - Dry-run benchmark condition builder plus optional provider execution hooks.
- Modify: `README.md`
  - Add the Discovery workflow to the skills/tools table and remove stale MCP tool-count claims.
- Modify: `pyproject.toml`
  - Remove stale MCP tool count from the package description.
- Modify: `src/vulca/mcp_server.py`
  - Update docstring count wording so it matches the runtime split: core MCP tools plus Tool Protocol tools.
- Create tests:
  - `tests/test_visual_discovery_current_state.py`
  - `tests/test_visual_discovery_types.py`
  - `tests/test_visual_discovery_terms.py`
  - `tests/test_visual_discovery_cards.py`
  - `tests/test_visual_discovery_prompting.py`
  - `tests/test_visual_discovery_artifacts.py`
  - `tests/test_visual_discovery_skill_contract.py`
  - `tests/test_visual_discovery_benchmark.py`
  - `tests/test_visual_discovery_docs_truth.py`

---

## Task 1: Current-State Audit Tripwires

**Files:**
- Create: `tests/test_visual_discovery_current_state.py`

- [ ] **Step 1: Add current-state tests**

Create `tests/test_visual_discovery_current_state.py` with:

```python
from __future__ import annotations

import asyncio

import pytest

pytest.importorskip("fastmcp", reason="fastmcp is optional; install vulca[mcp]")


def run(coro):
    return asyncio.run(coro)


EXPECTED_CORE_TOOLS = {
    "archive_session",
    "brief_parse",
    "compose_prompt_from_design",
    "create_artwork",
    "evaluate_artwork",
    "generate_concepts",
    "generate_image",
    "get_tradition_guide",
    "inpaint_artwork",
    "layers_composite",
    "layers_edit",
    "layers_evaluate",
    "layers_export",
    "layers_list",
    "layers_paste_back",
    "layers_redraw",
    "layers_split",
    "layers_transform",
    "list_traditions",
    "search_traditions",
    "sync_data",
    "unload_models",
    "view_image",
}

EXPECTED_TOOL_PROTOCOL_TOOLS = {
    "tool_brushstroke_analyze",
    "tool_color_correct",
    "tool_color_gamut_check",
    "tool_composition_analyze",
    "tool_whitespace_analyze",
}

EXPECTED_IMAGE_PROVIDERS = {"mock", "gemini", "nb2", "openai", "comfyui"}
EXPECTED_VLM_PROVIDERS = {"mock", "litellm"}
EXPECTED_TRADITIONS = {
    "african_traditional",
    "brand_design",
    "chinese_gongbi",
    "chinese_xieyi",
    "contemporary_art",
    "default",
    "islamic_geometric",
    "japanese_traditional",
    "photography",
    "south_asian",
    "ui_ux_design",
    "watercolor",
    "western_academic",
}


def test_runtime_mcp_surface_contains_current_expected_tools():
    from vulca.mcp_server import mcp

    names = {tool.name for tool in run(mcp.list_tools())}

    assert EXPECTED_CORE_TOOLS <= names
    assert EXPECTED_TOOL_PROTOCOL_TOOLS <= names
    assert len(names) == len(EXPECTED_CORE_TOOLS | EXPECTED_TOOL_PROTOCOL_TOOLS)


def test_current_image_and_vlm_provider_registries():
    import vulca.providers as providers

    providers._lazy_load_providers()

    assert set(providers._IMAGE_PROVIDERS) == EXPECTED_IMAGE_PROVIDERS
    assert set(providers._VLM_PROVIDERS) == EXPECTED_VLM_PROVIDERS


def test_current_tradition_registry():
    from vulca.cultural.loader import get_all_traditions

    traditions = get_all_traditions()

    assert set(traditions) == EXPECTED_TRADITIONS
```

- [ ] **Step 2: Run the current-state tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_current_state.py -q
```

Expected: `3 passed`. If this fails, update the spec or runtime before continuing; Discovery must not build on stale product facts.

- [ ] **Step 3: Commit**

```bash
git add tests/test_visual_discovery_current_state.py
git commit -m "test: lock visual discovery current-state facts"
```

---

## Task 2: Discovery Schema Types

**Files:**
- Create: `src/vulca/discovery/__init__.py`
- Create: `src/vulca/discovery/types.py`
- Create: `tests/test_visual_discovery_types.py`

- [ ] **Step 1: Write schema tests**

Create `tests/test_visual_discovery_types.py` with:

```python
from __future__ import annotations

import pytest


def test_direction_card_to_dict_round_trip():
    from vulca.discovery.types import DirectionCard, EvaluationFocus, ProviderTarget, VisualOps

    card = DirectionCard(
        id="song-negative-space-premium-tea",
        label="Song negative space + premium tea restraint",
        summary="Quiet premium tea direction.",
        culture_terms=["reserved white space", "spirit resonance and vitality"],
        visual_ops=VisualOps(
            composition="large negative space, off-center subject",
            color="warm off-white, ink gray",
            texture="subtle rice paper grain",
            lighting="soft diffuse",
            camera="front-facing product hierarchy",
            typography="small restrained serif",
            symbol_strategy="abstract atmosphere over literal icons",
            avoid=["dragon motifs", "busy ornament"],
        ),
        provider_hint={
            "sketch": ProviderTarget(provider="gemini", model="gemini-3.1-flash-image-preview"),
            "final": ProviderTarget(provider="openai", model="gpt-image-2"),
            "local": ProviderTarget(provider="comfyui"),
        },
        evaluation_focus=EvaluationFocus(
            L1="negative space reads intentional",
            L2="texture stays subtle",
            L3="xieyi terms are respected",
            L4="not a generic luxury ad",
            L5="quietness creates resonance",
        ),
        risk="May be too quiet for high-conversion social ads.",
    )

    payload = card.to_dict()

    assert payload["provider_hint"]["final"]["provider"] == "openai"
    assert payload["provider_hint"]["final"]["model"] == "gpt-image-2"
    assert payload["visual_ops"]["avoid"] == ["dragon motifs", "busy ornament"]
    assert DirectionCard.from_dict(payload).to_dict() == payload


def test_provider_target_rejects_unknown_provider():
    from vulca.discovery.types import ProviderTarget

    with pytest.raises(ValueError, match="unknown provider"):
        ProviderTarget(provider="midjourney")


def test_sketch_prompt_requires_known_provider():
    from vulca.discovery.types import SketchPrompt

    prompt = SketchPrompt(
        card_id="card-a",
        provider="mock",
        model="",
        prompt="quiet tea packaging",
        negative_prompt="busy ornament",
        size="1024x1024",
        purpose="thumbnail exploration",
    )

    assert prompt.to_dict()["provider"] == "mock"

    with pytest.raises(ValueError, match="unknown provider"):
        SketchPrompt(
            card_id="card-a",
            provider="unknown",
            model="",
            prompt="quiet tea packaging",
            negative_prompt="",
            size="1024x1024",
            purpose="thumbnail exploration",
        )
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_types.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.discovery'`.

- [ ] **Step 3: Implement schema types**

Create `src/vulca/discovery/types.py` with:

```python
"""Structured data types for visual discovery artifacts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


KNOWN_PROVIDERS = {"mock", "gemini", "nb2", "openai", "comfyui"}


def _require_provider(provider: str) -> str:
    if provider not in KNOWN_PROVIDERS:
        raise ValueError(f"unknown provider: {provider!r}")
    return provider


@dataclass(frozen=True)
class ProviderTarget:
    provider: str
    model: str = ""

    def __post_init__(self) -> None:
        _require_provider(self.provider)

    def to_dict(self) -> dict[str, str]:
        payload = {"provider": self.provider}
        if self.model:
            payload["model"] = self.model
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProviderTarget":
        return cls(provider=str(data.get("provider", "")), model=str(data.get("model", "")))


@dataclass(frozen=True)
class VisualOps:
    composition: str = ""
    color: str = ""
    texture: str = ""
    lighting: str = ""
    camera: str = ""
    typography: str = ""
    symbol_strategy: str = ""
    avoid: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "composition": self.composition,
            "color": self.color,
            "texture": self.texture,
            "lighting": self.lighting,
            "camera": self.camera,
            "typography": self.typography,
            "symbol_strategy": self.symbol_strategy,
            "avoid": list(self.avoid),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VisualOps":
        return cls(
            composition=str(data.get("composition", "")),
            color=str(data.get("color", "")),
            texture=str(data.get("texture", "")),
            lighting=str(data.get("lighting", "")),
            camera=str(data.get("camera", "")),
            typography=str(data.get("typography", "")),
            symbol_strategy=str(data.get("symbol_strategy", "")),
            avoid=[str(item) for item in data.get("avoid", [])],
        )


@dataclass(frozen=True)
class EvaluationFocus:
    L1: str = ""
    L2: str = ""
    L3: str = ""
    L4: str = ""
    L5: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"L1": self.L1, "L2": self.L2, "L3": self.L3, "L4": self.L4, "L5": self.L5}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationFocus":
        return cls(
            L1=str(data.get("L1", "")),
            L2=str(data.get("L2", "")),
            L3=str(data.get("L3", "")),
            L4=str(data.get("L4", "")),
            L5=str(data.get("L5", "")),
        )


@dataclass(frozen=True)
class DirectionCard:
    id: str
    label: str
    summary: str
    culture_terms: list[str]
    visual_ops: VisualOps
    provider_hint: dict[str, ProviderTarget]
    evaluation_focus: EvaluationFocus
    risk: str = ""
    status: str = "candidate"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "summary": self.summary,
            "culture_terms": list(self.culture_terms),
            "visual_ops": self.visual_ops.to_dict(),
            "provider_hint": {key: value.to_dict() for key, value in self.provider_hint.items()},
            "evaluation_focus": self.evaluation_focus.to_dict(),
            "risk": self.risk,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DirectionCard":
        return cls(
            id=str(data["id"]),
            label=str(data["label"]),
            summary=str(data.get("summary", "")),
            culture_terms=[str(item) for item in data.get("culture_terms", [])],
            visual_ops=VisualOps.from_dict(data.get("visual_ops", {})),
            provider_hint={
                str(key): ProviderTarget.from_dict(value)
                for key, value in data.get("provider_hint", {}).items()
            },
            evaluation_focus=EvaluationFocus.from_dict(data.get("evaluation_focus", {})),
            risk=str(data.get("risk", "")),
            status=str(data.get("status", "candidate")),
        )


@dataclass(frozen=True)
class TasteProfile:
    slug: str
    initial_intent: str
    domain_primary: str
    candidate_traditions: list[str]
    culture_terms: list[str]
    mood: list[str] = field(default_factory=list)
    confidence: str = "low"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "0.1",
            "slug": self.slug,
            "source": {
                "initial_intent": self.initial_intent,
                "reference_paths": [],
                "conversation_signals": [],
            },
            "domain": {
                "primary": self.domain_primary,
                "candidates": [],
                "confidence": self.confidence,
            },
            "culture": {
                "primary_tradition": self.candidate_traditions[0] if self.candidate_traditions else None,
                "candidate_traditions": list(self.candidate_traditions),
                "terms": list(self.culture_terms),
                "avoid_cliches": [],
                "risk_flags": [],
            },
            "aesthetic": {
                "mood": list(self.mood),
                "composition": [],
                "color": [],
                "material": [],
                "typography": [],
                "symbol_strategy": "",
            },
            "commercial_context": {
                "audience": "",
                "channel": "",
                "conversion_pressure": "unknown",
                "brand_maturity": "unknown",
            },
            "selection_history": [],
            "confidence": {
                "overall": self.confidence,
                "needs_more_questions": self.confidence == "low",
            },
        }


@dataclass(frozen=True)
class SketchPrompt:
    card_id: str
    provider: str
    model: str
    prompt: str
    negative_prompt: str
    size: str
    purpose: str

    def __post_init__(self) -> None:
        _require_provider(self.provider)

    def to_dict(self) -> dict[str, str]:
        return {
            "card_id": self.card_id,
            "provider": self.provider,
            "model": self.model,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "size": self.size,
            "purpose": self.purpose,
        }


@dataclass(frozen=True)
class PromptArtifact:
    provider: str
    model: str
    prompt: str
    negative_prompt: str
    source_card_id: str

    def __post_init__(self) -> None:
        _require_provider(self.provider)

    def to_dict(self) -> dict[str, str]:
        return {
            "provider": self.provider,
            "model": self.model,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "source_card_id": self.source_card_id,
        }
```

Create `src/vulca/discovery/__init__.py` with:

```python
"""Visual discovery helpers for Vulca agent workflows."""
from vulca.discovery.types import (
    DirectionCard,
    EvaluationFocus,
    PromptArtifact,
    ProviderTarget,
    SketchPrompt,
    TasteProfile,
    VisualOps,
)

__all__ = [
    "DirectionCard",
    "EvaluationFocus",
    "PromptArtifact",
    "ProviderTarget",
    "SketchPrompt",
    "TasteProfile",
    "VisualOps",
]
```

- [ ] **Step 4: Run tests and verify pass**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_types.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/discovery/__init__.py src/vulca/discovery/types.py tests/test_visual_discovery_types.py
git commit -m "feat: add visual discovery schema types"
```

---

## Task 3: Tradition Term Expansion

**Files:**
- Create: `src/vulca/discovery/terms.py`
- Create: `tests/test_visual_discovery_terms.py`

- [ ] **Step 1: Write term expansion tests**

Create `tests/test_visual_discovery_terms.py` with:

```python
from __future__ import annotations


def test_expand_liubai_from_chinese_xieyi_registry():
    from vulca.discovery.terms import expand_terms

    expansions = expand_terms("chinese_xieyi", ["liubai"])

    assert len(expansions) == 1
    payload = expansions[0]
    assert payload["term"] == "reserved white space"
    assert payload["term_zh"] == "留白"
    assert "large negative space" in payload["visual_ops"]["composition"]
    assert "generic minimalism unrelated to subject" in payload["visual_ops"]["avoid"]
    assert payload["evaluation_focus"]["L5"] != ""


def test_expand_unknown_term_returns_operational_fallback():
    from vulca.discovery.terms import expand_terms

    expansions = expand_terms("brand_design", ["quiet luxury"])

    assert expansions[0]["term"] == "quiet luxury"
    assert expansions[0]["visual_ops"]["composition"] != ""
    assert "generic ai aesthetic" in expansions[0]["visual_ops"]["avoid"]


def test_extract_terms_from_intent_uses_registry_aliases():
    from vulca.discovery.terms import extract_terms_from_intent

    terms = extract_terms_from_intent(
        "premium tea packaging with liu bai and ink atmosphere",
        tradition="chinese_xieyi",
    )

    assert "reserved white space" in terms
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_terms.py -q
```

Expected: FAIL with `ModuleNotFoundError` for `vulca.discovery.terms`.

- [ ] **Step 3: Implement term expansion**

Create `src/vulca/discovery/terms.py` with:

```python
"""Expand cultural and aesthetic terms into operational visual guidance."""
from __future__ import annotations

import re
from typing import Any

from vulca.cultural.loader import get_tradition_guide


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", value.lower())


TERM_VISUAL_OPS: dict[str, dict[str, Any]] = {
    "reserved white space": {
        "composition": "large negative space, small off-center focal subject, clear figure-ground relationship",
        "color": "warm paper whites, restrained ink or muted accent colors",
        "texture": "subtle paper grain, quiet low-detail regions",
        "symbol_strategy": "empty space should imply atmosphere or breath, not look unfinished",
        "avoid": [
            "empty background with no intentional balance",
            "generic minimalism unrelated to subject",
            "busy ornament",
        ],
        "evaluation_focus": {
            "L1": "negative space supports the focal hierarchy",
            "L2": "blank regions have controlled edges and stable balance",
            "L3": "liubai connects to the chosen tradition rather than generic minimalism",
            "L4": "emptiness is a compositional argument",
            "L5": "emptiness contributes resonance, breath, and implied meaning",
        },
    },
    "spirit resonance and vitality": {
        "composition": "asymmetrical rhythm with clear visual flow",
        "color": "restrained tonal range with one living accent if needed",
        "texture": "brush or material energy should feel intentional",
        "symbol_strategy": "express living rhythm through movement and spacing",
        "avoid": [
            "static decorative imitation",
            "over-rendered realism with no expressive rhythm",
        ],
        "evaluation_focus": {
            "L1": "viewer can follow the image rhythm",
            "L2": "marks or materials carry energy without chaos",
            "L3": "the term is not reduced to surface ornament",
            "L4": "visual flow supports interpretation",
            "L5": "the image has living spirit beyond literal depiction",
        },
    },
}

GENERIC_VISUAL_OPS = {
    "composition": "clear focal hierarchy, intentional spacing, readable silhouette",
    "color": "limited palette aligned to the project mood",
    "texture": "material treatment supports the concept",
    "symbol_strategy": "prefer specific visual behavior over decorative labels",
    "avoid": ["generic ai aesthetic", "literal cliché symbolism", "unexplained culture mixing"],
    "evaluation_focus": {
        "L1": "visual perception is clear",
        "L2": "execution supports the stated style",
        "L3": "cultural references are grounded",
        "L4": "interpretation matches the project intent",
        "L5": "the aesthetic idea has depth beyond styling",
    },
}


def _term_index(tradition: str) -> dict[str, dict[str, Any]]:
    guide = get_tradition_guide(tradition) or {}
    index: dict[str, dict[str, Any]] = {}
    for entry in guide.get("terminology", []):
        labels = [
            str(entry.get("term", "")),
            str(entry.get("term_zh", "")),
            *[str(alias) for alias in entry.get("aliases", [])],
        ]
        for label in labels:
            if label:
                index[_norm(label)] = entry
    return index


def _entry_for_term(tradition: str, term: str) -> dict[str, Any] | None:
    return _term_index(tradition).get(_norm(term))


def _visual_ops_for_term(term: str) -> dict[str, Any]:
    return TERM_VISUAL_OPS.get(term, GENERIC_VISUAL_OPS)


def expand_terms(tradition: str, terms: list[str]) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for raw_term in terms:
        entry = _entry_for_term(tradition, raw_term)
        canonical = str(entry.get("term", raw_term)) if entry else raw_term
        ops = _visual_ops_for_term(canonical)
        expanded.append(
            {
                "term": canonical,
                "term_zh": str(entry.get("term_zh", "")) if entry else "",
                "definition": entry.get("definition", "") if entry else "",
                "category": str(entry.get("category", "aesthetic")) if entry else "aesthetic",
                "visual_ops": {
                    "composition": ops["composition"],
                    "color": ops["color"],
                    "texture": ops["texture"],
                    "symbol_strategy": ops["symbol_strategy"],
                    "avoid": list(ops["avoid"]),
                },
                "evaluation_focus": dict(ops["evaluation_focus"]),
            }
        )
    return expanded


def extract_terms_from_intent(intent: str, tradition: str) -> list[str]:
    intent_key = _norm(intent)
    terms: list[str] = []
    for entry in _term_index(tradition).values():
        labels = [str(entry.get("term", "")), str(entry.get("term_zh", ""))]
        labels.extend(str(alias) for alias in entry.get("aliases", []))
        if any(label and _norm(label) in intent_key for label in labels):
            term = str(entry.get("term", ""))
            if term and term not in terms:
                terms.append(term)
    return terms
```

- [ ] **Step 4: Run tests and verify pass**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_terms.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/discovery/terms.py tests/test_visual_discovery_terms.py
git commit -m "feat: expand tradition terms into visual operations"
```

---

## Task 4: Profile Inference and Direction Cards

**Files:**
- Create: `src/vulca/discovery/profile.py`
- Create: `src/vulca/discovery/cards.py`
- Modify: `src/vulca/discovery/__init__.py`
- Create: `tests/test_visual_discovery_cards.py`

- [ ] **Step 1: Write profile and card tests**

Create `tests/test_visual_discovery_cards.py` with:

```python
from __future__ import annotations


def test_infer_profile_detects_packaging_and_xieyi_terms():
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )

    payload = profile.to_dict()
    assert payload["domain"]["primary"] == "packaging"
    assert "chinese_xieyi" in payload["culture"]["candidate_traditions"]
    assert "reserved white space" in payload["culture"]["terms"]


def test_generate_direction_cards_returns_operational_cards():
    from vulca.discovery.cards import generate_direction_cards
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )
    cards = generate_direction_cards(profile, count=3)

    assert len(cards) == 3
    assert cards[0].provider_hint["final"].provider == "openai"
    assert cards[0].provider_hint["final"].model == "gpt-image-2"
    assert cards[0].visual_ops.composition != ""
    assert cards[0].evaluation_focus.L5 != ""
    assert cards[0].status == "candidate"
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_cards.py -q
```

Expected: FAIL with `ModuleNotFoundError` for `vulca.discovery.profile`.

- [ ] **Step 3: Implement profile inference**

Create `src/vulca/discovery/profile.py` with:

```python
"""Rule-based taste profile inference for visual discovery."""
from __future__ import annotations

from vulca.discovery.terms import extract_terms_from_intent
from vulca.discovery.types import TasteProfile


DOMAIN_HINTS = {
    "packaging": {"packaging", "label", "bottle", "box", "tea"},
    "poster": {"poster", "exhibition", "event"},
    "brand_visual": {"brand", "campaign", "launch"},
    "editorial_cover": {"cover", "magazine", "book"},
    "photography_brief": {"photo", "photography", "shoot"},
    "hero_visual_for_ui": {"hero", "splash"},
}

TRADITION_HINTS = {
    "chinese_xieyi": {"ink", "liubai", "liu bai", "xieyi", "negative space", "水墨", "留白"},
    "chinese_gongbi": {"gongbi", "fine line", "工笔"},
    "japanese_traditional": {"ukiyo", "wabi", "sabi", "japanese"},
    "brand_design": {"brand", "logo", "campaign"},
    "photography": {"photo", "camera", "shoot"},
}


def _pick_domain(intent: str) -> str:
    lowered = intent.lower()
    for domain, hints in DOMAIN_HINTS.items():
        if any(hint in lowered for hint in hints):
            return domain
    return "illustration"


def _pick_traditions(intent: str) -> list[str]:
    lowered = intent.lower()
    traditions = [
        tradition for tradition, hints in TRADITION_HINTS.items()
        if any(hint in lowered for hint in hints)
    ]
    return traditions or ["brand_design"]


def infer_taste_profile(slug: str, intent: str) -> TasteProfile:
    traditions = _pick_traditions(intent)
    terms: list[str] = []
    for tradition in traditions:
        for term in extract_terms_from_intent(intent, tradition):
            if term not in terms:
                terms.append(term)
    if not terms and "chinese_xieyi" in traditions:
        terms.append("reserved white space")

    mood = []
    lowered = intent.lower()
    if "premium" in lowered or "luxury" in lowered:
        mood.append("premium")
    if "quiet" in lowered or "restrained" in lowered:
        mood.append("quiet")

    return TasteProfile(
        slug=slug,
        initial_intent=intent,
        domain_primary=_pick_domain(intent),
        candidate_traditions=traditions,
        culture_terms=terms,
        mood=mood,
        confidence="med" if terms else "low",
    )
```

- [ ] **Step 4: Implement direction-card generation**

Create `src/vulca/discovery/cards.py` with:

```python
"""Direction-card generation for visual discovery."""
from __future__ import annotations

from vulca.discovery.terms import expand_terms
from vulca.discovery.types import DirectionCard, EvaluationFocus, ProviderTarget, TasteProfile, VisualOps


def _provider_hint() -> dict[str, ProviderTarget]:
    return {
        "sketch": ProviderTarget(provider="gemini", model="gemini-3.1-flash-image-preview"),
        "final": ProviderTarget(provider="openai", model="gpt-image-2"),
        "local": ProviderTarget(provider="comfyui"),
    }


def _card_from_expansion(profile: TasteProfile, idx: int, expansion: dict) -> DirectionCard:
    ops = expansion["visual_ops"]
    focus = expansion["evaluation_focus"]
    label = f"{expansion['term']} direction for {profile.domain_primary}"
    return DirectionCard(
        id=f"{profile.slug}-{idx + 1}-{expansion['term'].replace(' ', '-')}",
        label=label,
        summary=f"Use {expansion['term']} as the governing visual idea for {profile.initial_intent}.",
        culture_terms=[expansion["term"]],
        visual_ops=VisualOps(
            composition=ops["composition"],
            color=ops["color"],
            texture=ops["texture"],
            lighting="soft diffuse lighting unless the brief asks for drama",
            camera="clear product or subject hierarchy",
            typography="restrained and legible when text is required",
            symbol_strategy=ops["symbol_strategy"],
            avoid=list(ops["avoid"]),
        ),
        provider_hint=_provider_hint(),
        evaluation_focus=EvaluationFocus.from_dict(focus),
        risk="Direction may become generic if the visual operations are dropped from the prompt.",
    )


def _fallback_card(profile: TasteProfile, idx: int, label: str, composition: str) -> DirectionCard:
    return DirectionCard(
        id=f"{profile.slug}-{idx + 1}-{label.lower().replace(' ', '-')}",
        label=label,
        summary=f"A {label.lower()} route for {profile.initial_intent}.",
        culture_terms=list(profile.culture_terms),
        visual_ops=VisualOps(
            composition=composition,
            color="limited palette aligned to the brand and medium",
            texture="material treatment supports the selected direction",
            lighting="clear subject readability",
            camera="stable hierarchy with no accidental crop",
            typography="legible and secondary to the visual concept",
            symbol_strategy="specific visual behavior over decorative symbols",
            avoid=["generic ai aesthetic", "literal cliché symbolism"],
        ),
        provider_hint=_provider_hint(),
        evaluation_focus=EvaluationFocus(
            L1="composition is readable",
            L2="execution supports the visual direction",
            L3="cultural references are grounded",
            L4="interpretation matches the project intent",
            L5="the visual idea has depth beyond styling",
        ),
        risk="Needs a selected culture term or reference to become more specific.",
    )


def generate_direction_cards(profile: TasteProfile, count: int = 3) -> list[DirectionCard]:
    count = max(1, min(count, 5))
    tradition = profile.candidate_traditions[0] if profile.candidate_traditions else "brand_design"
    expansions = expand_terms(tradition, profile.culture_terms)
    cards = [_card_from_expansion(profile, idx, expansion) for idx, expansion in enumerate(expansions)]

    fallback_specs = [
        ("Commercial clarity", "large readable subject, product-first hierarchy, high scan speed"),
        ("Editorial atmosphere", "more negative space, slower reading, stronger mood"),
        ("Modern restraint", "simple geometry, low ornament, sharp hierarchy"),
    ]
    while len(cards) < count:
        label, composition = fallback_specs[len(cards) % len(fallback_specs)]
        cards.append(_fallback_card(profile, len(cards), label, composition))

    return cards[:count]
```

Modify `src/vulca/discovery/__init__.py`:

```python
"""Visual discovery helpers for Vulca agent workflows."""
from vulca.discovery.cards import generate_direction_cards
from vulca.discovery.profile import infer_taste_profile
from vulca.discovery.types import (
    DirectionCard,
    EvaluationFocus,
    PromptArtifact,
    ProviderTarget,
    SketchPrompt,
    TasteProfile,
    VisualOps,
)

__all__ = [
    "DirectionCard",
    "EvaluationFocus",
    "PromptArtifact",
    "ProviderTarget",
    "SketchPrompt",
    "TasteProfile",
    "VisualOps",
    "generate_direction_cards",
    "infer_taste_profile",
]
```

- [ ] **Step 5: Run tests and verify pass**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_cards.py tests/test_visual_discovery_terms.py tests/test_visual_discovery_types.py -q
```

Expected: `8 passed`.

- [ ] **Step 6: Commit**

```bash
git add src/vulca/discovery/__init__.py src/vulca/discovery/profile.py src/vulca/discovery/cards.py tests/test_visual_discovery_cards.py
git commit -m "feat: infer visual discovery profiles and direction cards"
```

---

## Task 5: Direction-Card Prompt Composition

**Files:**
- Create: `src/vulca/discovery/prompting.py`
- Modify: `src/vulca/discovery/__init__.py`
- Create: `tests/test_visual_discovery_prompting.py`

- [ ] **Step 1: Write prompt composition tests**

Create `tests/test_visual_discovery_prompting.py` with:

```python
from __future__ import annotations


def _card():
    from vulca.discovery.cards import generate_direction_cards
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )
    return generate_direction_cards(profile, count=1)[0]


def test_openai_prompt_artifact_uses_gpt_image_2_hint():
    from vulca.discovery.prompting import compose_prompt_from_direction_card

    artifact = compose_prompt_from_direction_card(_card(), target="final")
    payload = artifact.to_dict()

    assert payload["provider"] == "openai"
    assert payload["model"] == "gpt-image-2"
    assert "large negative space" in payload["prompt"]
    assert "avoid:" not in payload["prompt"].lower()
    assert "generic minimalism unrelated to subject" in payload["negative_prompt"]


def test_gemini_prompt_artifact_uses_sketch_hint():
    from vulca.discovery.prompting import compose_prompt_from_direction_card

    artifact = compose_prompt_from_direction_card(_card(), target="sketch")

    assert artifact.provider == "gemini"
    assert artifact.model == "gemini-3.1-flash-image-preview"
    assert "exploratory thumbnail" in artifact.prompt


def test_unknown_target_rejected():
    import pytest
    from vulca.discovery.prompting import compose_prompt_from_direction_card

    with pytest.raises(ValueError, match="unknown provider target"):
        compose_prompt_from_direction_card(_card(), target="video")
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_prompting.py -q
```

Expected: FAIL with `ModuleNotFoundError` for `vulca.discovery.prompting`.

- [ ] **Step 3: Implement prompt composition**

Create `src/vulca/discovery/prompting.py` with:

```python
"""Prompt composition for visual discovery direction cards."""
from __future__ import annotations

from vulca.discovery.types import DirectionCard, PromptArtifact


def _join_nonempty(parts: list[str], sep: str = ". ") -> str:
    return sep.join(part.strip() for part in parts if part and part.strip())


def compose_prompt_from_direction_card(card: DirectionCard, target: str = "final") -> PromptArtifact:
    provider_target = card.provider_hint.get(target)
    if provider_target is None:
        raise ValueError(f"unknown provider target: {target!r}")

    ops = card.visual_ops
    base_parts = [
        card.summary,
        f"Composition: {ops.composition}",
        f"Color: {ops.color}",
        f"Texture/material: {ops.texture}",
        f"Lighting: {ops.lighting}",
        f"Camera/layout: {ops.camera}",
        f"Typography: {ops.typography}",
        f"Symbol strategy: {ops.symbol_strategy}",
        f"Culture terms: {', '.join(card.culture_terms)}",
    ]
    if target == "sketch":
        base_parts.insert(0, "Create an exploratory thumbnail for visual direction comparison")
    elif target == "local":
        base_parts.insert(0, "CLIP-friendly local generation prompt")
    else:
        base_parts.insert(0, "Create a high-fidelity commercial visual candidate")

    return PromptArtifact(
        provider=provider_target.provider,
        model=provider_target.model,
        prompt=_join_nonempty(base_parts),
        negative_prompt=", ".join(card.visual_ops.avoid),
        source_card_id=card.id,
    )
```

Replace `src/vulca/discovery/__init__.py` with:

```python
"""Visual discovery helpers for Vulca agent workflows."""
from vulca.discovery.cards import generate_direction_cards
from vulca.discovery.profile import infer_taste_profile
from vulca.discovery.prompting import compose_prompt_from_direction_card
from vulca.discovery.types import (
    DirectionCard,
    EvaluationFocus,
    PromptArtifact,
    ProviderTarget,
    SketchPrompt,
    TasteProfile,
    VisualOps,
)

__all__ = [
    "DirectionCard",
    "EvaluationFocus",
    "PromptArtifact",
    "ProviderTarget",
    "SketchPrompt",
    "TasteProfile",
    "VisualOps",
    "compose_prompt_from_direction_card",
    "generate_direction_cards",
    "infer_taste_profile",
]
```

- [ ] **Step 4: Run tests and verify pass**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_prompting.py tests/test_visual_discovery_cards.py -q
```

Expected: `5 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/discovery/__init__.py src/vulca/discovery/prompting.py tests/test_visual_discovery_prompting.py
git commit -m "feat: compose prompts from visual discovery cards"
```

---

## Task 6: Discovery Artifact Writer

**Files:**
- Create: `src/vulca/discovery/artifacts.py`
- Modify: `src/vulca/discovery/__init__.py`
- Create: `tests/test_visual_discovery_artifacts.py`

- [ ] **Step 1: Write artifact tests**

Create `tests/test_visual_discovery_artifacts.py` with:

```python
from __future__ import annotations

import json


def test_write_discovery_artifacts(tmp_path):
    from vulca.discovery.artifacts import build_brainstorm_handoff, write_discovery_artifacts
    from vulca.discovery.cards import generate_direction_cards
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )
    cards = generate_direction_cards(profile, count=2)
    result = write_discovery_artifacts(
        root=tmp_path,
        slug="tea",
        title="Premium Tea",
        original_intent=profile.initial_intent,
        profile=profile,
        cards=cards,
        recommended_card_id=cards[0].id,
    )

    assert result["discovery_md"].endswith("discovery.md")
    discovery_dir = tmp_path / "docs" / "visual-specs" / "tea" / "discovery"
    assert (discovery_dir / "discovery.md").exists()
    assert (discovery_dir / "taste_profile.json").exists()
    assert (discovery_dir / "direction_cards.json").exists()

    cards_payload = json.loads((discovery_dir / "direction_cards.json").read_text())
    assert cards_payload["schema_version"] == "0.1"
    assert cards_payload["cards"][0]["id"] == cards[0].id

    handoff = build_brainstorm_handoff(profile, cards[0])
    assert "Ready for /visual-brainstorm" in handoff
    assert "premium tea packaging" in handoff.lower()
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_artifacts.py -q
```

Expected: FAIL with `ModuleNotFoundError` for `vulca.discovery.artifacts`.

- [ ] **Step 3: Implement artifact writer**

Create `src/vulca/discovery/artifacts.py` with:

```python
"""Artifact writing for visual discovery sessions."""
from __future__ import annotations

import json
from pathlib import Path

from vulca.discovery.types import DirectionCard, TasteProfile


def _project_dir(root: Path, slug: str) -> Path:
    return root / "docs" / "visual-specs" / slug / "discovery"


def build_brainstorm_handoff(profile: TasteProfile, card: DirectionCard) -> str:
    brief = (
        f"{profile.initial_intent}; selected direction: {card.label}; "
        f"visual operations: {card.visual_ops.composition}; "
        f"avoid: {', '.join(card.visual_ops.avoid)}; "
        f"domain: {profile.domain_primary}."
    )
    return f"Ready for /visual-brainstorm. Suggested topic:\n\"{brief}\""


def _discovery_markdown(
    title: str,
    original_intent: str,
    profile: TasteProfile,
    cards: list[DirectionCard],
    recommended_card_id: str,
) -> str:
    card_lines = "\n".join(f"- `{card.id}`: {card.label} — {card.summary}" for card in cards)
    selected = next((card for card in cards if card.id == recommended_card_id), None)
    selected_text = selected.label if selected else "none"
    return f"""# Visual Discovery: {title}

## Status
ready_for_brainstorm

## Original Intent
{original_intent}

## Scope Decision
accepted

## Uncertainty
{profile.confidence}

## Taste Profile Summary
Domain: {profile.domain_primary}. Traditions: {", ".join(profile.candidate_traditions)}.

## Direction Cards
{card_lines}

## User Preference Signals
recommended: {recommended_card_id}

## Recommended Direction
{selected_text}

## Handoff
{build_brainstorm_handoff(profile, selected or cards[0])}

## Notes
generated_by: visual-discovery@0.1.0
"""


def write_discovery_artifacts(
    *,
    root: str | Path,
    slug: str,
    title: str,
    original_intent: str,
    profile: TasteProfile,
    cards: list[DirectionCard],
    recommended_card_id: str,
) -> dict[str, str]:
    root_path = Path(root)
    out_dir = _project_dir(root_path, slug)
    out_dir.mkdir(parents=True, exist_ok=True)

    discovery_md = out_dir / "discovery.md"
    taste_profile_json = out_dir / "taste_profile.json"
    direction_cards_json = out_dir / "direction_cards.json"

    discovery_md.write_text(
        _discovery_markdown(title, original_intent, profile, cards, recommended_card_id),
        encoding="utf-8",
    )
    taste_profile_json.write_text(
        json.dumps(profile.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    direction_cards_json.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "slug": slug,
                "cards": [card.to_dict() for card in cards],
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    return {
        "discovery_md": str(discovery_md),
        "taste_profile_json": str(taste_profile_json),
        "direction_cards_json": str(direction_cards_json),
    }
```

Replace `src/vulca/discovery/__init__.py` with:

```python
"""Visual discovery helpers for Vulca agent workflows."""
from vulca.discovery.artifacts import build_brainstorm_handoff, write_discovery_artifacts
from vulca.discovery.cards import generate_direction_cards
from vulca.discovery.profile import infer_taste_profile
from vulca.discovery.prompting import compose_prompt_from_direction_card
from vulca.discovery.types import (
    DirectionCard,
    EvaluationFocus,
    PromptArtifact,
    ProviderTarget,
    SketchPrompt,
    TasteProfile,
    VisualOps,
)

__all__ = [
    "DirectionCard",
    "EvaluationFocus",
    "PromptArtifact",
    "ProviderTarget",
    "SketchPrompt",
    "TasteProfile",
    "VisualOps",
    "build_brainstorm_handoff",
    "compose_prompt_from_direction_card",
    "generate_direction_cards",
    "infer_taste_profile",
    "write_discovery_artifacts",
]
```

The final file must include these imports exactly:

```python
from vulca.discovery.artifacts import build_brainstorm_handoff, write_discovery_artifacts
```

- [ ] **Step 4: Run tests and verify pass**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_artifacts.py tests/test_visual_discovery_prompting.py -q
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/discovery/__init__.py src/vulca/discovery/artifacts.py tests/test_visual_discovery_artifacts.py
git commit -m "feat: write visual discovery artifacts"
```

---

## Task 7: Skill Artifact and Router

**Files:**
- Create: `.agents/skills/visual-discovery/SKILL.md`
- Modify: `.agents/skills/using-vulca-skills/SKILL.md`
- Create: `tests/test_visual_discovery_skill_contract.py`

- [ ] **Step 1: Write skill contract tests**

Create `tests/test_visual_discovery_skill_contract.py` with:

```python
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".agents" / "skills" / "visual-discovery" / "SKILL.md"
ROUTER = ROOT / ".agents" / "skills" / "using-vulca-skills" / "SKILL.md"


def test_visual_discovery_skill_declares_scope_and_bans():
    body = SKILL.read_text(encoding="utf-8")

    assert "name: visual-discovery" in body
    assert "direction cards" in body
    assert "taste_profile.json" in body
    assert "direction_cards.json" in body
    assert "generate_image(provider=\"mock\")" in body
    assert "generate_concepts(provider=\"mock\")" in body
    assert "real provider `generate_image` / `generate_concepts`" in body
    assert "`layers_*`" in body
    assert "`inpaint_artwork`" in body
    assert "Ready for /visual-brainstorm" in body


def test_router_mentions_visual_discovery_before_visual_brainstorm():
    body = ROUTER.read_text(encoding="utf-8")

    discovery_idx = body.index("visual-discovery")
    brainstorm_idx = body.index("visual-brainstorm")
    assert discovery_idx < brainstorm_idx
    assert "抽卡" in body
    assert "文化倾向分析" in body
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_skill_contract.py -q
```

Expected: FAIL because `.agents/skills/visual-discovery/SKILL.md` does not exist yet.

- [ ] **Step 3: Create visual-discovery skill**

Create `.agents/skills/visual-discovery/SKILL.md` with:

```markdown
---
name: visual-discovery
description: Discover visual direction from fuzzy intent before /visual-brainstorm: taste profile, culture analysis, direction cards, and sketch prompts.
---

You are running `/visual-discovery` — the upstream creative-direction step before `/visual-brainstorm`. Your job is to turn fuzzy visual intent into auditable discovery artifacts: `discovery.md`, `taste_profile.json`, and `direction_cards.json`.

## Triggers

- Slash command: `/visual-discovery <slug>`
- Chinese aliases: `方向探索`, `审美分析`, `文化倾向分析`, `抽卡`, `先聊再出方案`
- Intent auto-match: the user is unsure what visual direction they want, asks for alternatives before a brief, asks why a direction fits a brand/culture/audience, or asks to explore taste/cultural tendencies before generating pixels.

## Scope

Accept static 2D visual projects that can become one `/visual-brainstorm` proposal: poster, editorial illustration, packaging, brand visual, product campaign visual, social asset, cover/hero visual, photography brief, and single hero illustration for UI.

Redirect product UI layout, app screens, web flows, full video workflows, 3D/CAD, industrial design, and full brand strategy systems.

## Tool Rules

Allowed:

- Read existing project docs.
- View user-provided reference images.
- Use `list_traditions`, `search_traditions`, and `get_tradition_guide`.
- Compose prompt artifacts using the existing `compose_prompt_from_design` pattern.
- Write discovery artifacts.
- Use `generate_image(provider="mock")` only for non-final sketch records.
- Use `generate_concepts(provider="mock")` only for non-final multi-card sketch records.

Forbidden:

- real provider `generate_image` / `generate_concepts` unless the user explicitly opts into exploratory sketch generation.
- `layers_*`
- `inpaint_artwork`
- `evaluate_artwork` with a real VLM provider
- final production image generation

## Conversation Loop

1. Parse the user's fuzzy visual intent.
2. Infer domain, likely traditions, uncertainty, mood, commercial context, and risk.
3. Ask at most 1-3 targeted questions only when inference is insufficient.
4. Produce 3-5 direction cards.
5. Let the user select, reject, or blend cards.
6. Update preference signals.
7. Optionally create text sketch prompts or mock sketch records.
8. Write discovery artifacts.
9. Print the handoff string.

Hard cap: 8 user-facing turns. If the user says `deep discovery` or `继续深入`, extend by 4 turns, max 12.

## Direction Card Requirements

Each card must include:

- `id`
- `label`
- `summary`
- `culture_terms`
- `visual_ops.composition`
- `visual_ops.color`
- `visual_ops.texture`
- `visual_ops.symbol_strategy`
- `visual_ops.avoid`
- `provider_hint.sketch`
- `provider_hint.final`
- `provider_hint.local`
- `evaluation_focus.L1` through `evaluation_focus.L5`
- `risk`
- `status`

Provider hints must include model when model matters:

```json
{
  "sketch": {"provider": "gemini", "model": "gemini-3.1-flash-image-preview"},
  "final": {"provider": "openai", "model": "gpt-image-2"},
  "local": {"provider": "comfyui"}
}
```

## Artifact Paths

Write artifacts under:

```text
docs/visual-specs/<slug>/discovery/
```

Required files:

```text
docs/visual-specs/<slug>/discovery/discovery.md
docs/visual-specs/<slug>/discovery/taste_profile.json
docs/visual-specs/<slug>/discovery/direction_cards.json
```

Optional file when sketch prompts are requested:

```text
docs/visual-specs/<slug>/discovery/sketch_prompts.json
```

## Handoff

When one direction is selected, print:

```text
Ready for /visual-brainstorm. Suggested topic:
"<compiled one-paragraph project brief>"
```

Do not auto-invoke `/visual-brainstorm`. The user must approve the transition.
```

- [ ] **Step 4: Update router**

Modify `.agents/skills/using-vulca-skills/SKILL.md` routing table so the `visual-discovery` row appears before `visual-brainstorm`:

```markdown
| explore fuzzy visual direction, taste, culture tendency, "抽卡", "方向探索", "审美分析", "文化倾向分析"; no discovery artifacts yet | `visual-discovery` |
| define / scope / brainstorm a 2D visual project (poster / illustration / packaging / brand / editorial / photo brief / hero art); no proposal.md yet | `visual-brainstorm` |
```

Also update the chain rule sentence to:

```markdown
**Chain rule**: never skip ahead. Pre-conditions gate each step — `/visual-brainstorm` follows selected discovery direction when discovery was needed; `/visual-spec` refuses without a ready proposal.md; `/visual-plan` refuses without a resolved design.md. If the user's intent lands on a stage whose precondition is missing, say so and invoke the earliest unmet stage.
```

- [ ] **Step 5: Run tests and verify pass**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_skill_contract.py -q
```

Expected: `2 passed`.

- [ ] **Step 6: Commit**

```bash
git add .agents/skills/visual-discovery/SKILL.md .agents/skills/using-vulca-skills/SKILL.md tests/test_visual_discovery_skill_contract.py
git commit -m "feat: add visual discovery skill routing"
```

---

## Task 8: Benchmark Harness

**Files:**
- Create: `scripts/visual_discovery_benchmark.py`
- Create: `tests/test_visual_discovery_benchmark.py`

- [ ] **Step 1: Write benchmark tests**

Create `tests/test_visual_discovery_benchmark.py` with:

```python
from __future__ import annotations


def test_build_conditions_a_through_f():
    from scripts.visual_discovery_benchmark import build_conditions
    from vulca.discovery.cards import generate_direction_cards
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )
    card = generate_direction_cards(profile, count=1)[0]

    conditions = build_conditions(profile.initial_intent, card)

    assert [condition["id"] for condition in conditions] == ["A", "B", "C", "D", "E", "F"]
    assert "raw cultural" in conditions[1]["label"].lower()
    assert card.id in conditions[-1]["source_card_id"]


def test_dry_run_report_contains_provider_matrix(tmp_path):
    from scripts.visual_discovery_benchmark import write_dry_run_report

    report = write_dry_run_report(tmp_path / "report.md")

    assert "OpenAI GPT Image 2" in report
    assert "Gemini / Nano Banana" in report
    assert "ComfyUI" in report
    assert (tmp_path / "report.md").exists()
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_benchmark.py -q
```

Expected: FAIL with `ModuleNotFoundError` for `scripts.visual_discovery_benchmark`.

- [ ] **Step 3: Implement benchmark harness**

Create `scripts/visual_discovery_benchmark.py` with:

```python
"""Benchmark scaffolding for visual-discovery prompt guidance."""
from __future__ import annotations

from pathlib import Path

from vulca.discovery.prompting import compose_prompt_from_direction_card
from vulca.discovery.types import DirectionCard


PROVIDERS = [
    {"label": "OpenAI GPT Image 2", "provider": "openai", "model": "gpt-image-2"},
    {"label": "Gemini / Nano Banana", "provider": "gemini", "model": "gemini-3.1-flash-image-preview"},
    {"label": "ComfyUI", "provider": "comfyui", "model": ""},
]


def build_conditions(base_prompt: str, card: DirectionCard) -> list[dict[str, str]]:
    ops = card.visual_ops
    compiled = compose_prompt_from_direction_card(card, target="final")
    raw_terms = ", ".join(card.culture_terms)
    visual_ops = "; ".join(
        part for part in [
            ops.composition,
            ops.color,
            ops.texture,
            ops.symbol_strategy,
        ] if part
    )
    return [
        {"id": "A", "label": "Baseline user prompt", "prompt": base_prompt, "source_card_id": ""},
        {"id": "B", "label": "Baseline + raw cultural terms", "prompt": f"{base_prompt}. Raw cultural terms: {raw_terms}", "source_card_id": card.id},
        {"id": "C", "label": "Baseline + visual operations", "prompt": f"{base_prompt}. Visual operations: {visual_ops}", "source_card_id": card.id},
        {"id": "D", "label": "Raw terms + visual operations", "prompt": f"{base_prompt}. Terms: {raw_terms}. Visual operations: {visual_ops}", "source_card_id": card.id},
        {"id": "E", "label": "Raw terms + visual operations + references", "prompt": f"{base_prompt}. Terms: {raw_terms}. Visual operations: {visual_ops}. Use provided references when available.", "source_card_id": card.id},
        {"id": "F", "label": "Visual-discovery card compiled prompt", "prompt": compiled.prompt, "source_card_id": card.id},
    ]


def write_dry_run_report(path: str | Path) -> str:
    provider_lines = "\n".join(
        f"- {item['label']}: provider={item['provider']} model={item['model'] or 'default'}"
        for item in PROVIDERS
    )
    report = f"""# Visual Discovery Benchmark Dry Run

## Providers
{provider_lines}

## Conditions
- A: baseline user prompt
- B: baseline + raw cultural/aesthetic terms
- C: baseline + visual operations only
- D: raw terms + visual operations
- E: raw terms + visual operations + reference images
- F: visual-discovery card compiled prompt
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(report, encoding="utf-8")
    return report


if __name__ == "__main__":
    write_dry_run_report("docs/visual-discovery-benchmark-dry-run.md")
```

- [ ] **Step 4: Run tests and verify pass**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_benchmark.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/visual_discovery_benchmark.py tests/test_visual_discovery_benchmark.py
git commit -m "feat: add visual discovery benchmark scaffold"
```

---

## Task 9: Documentation Truth Cleanup

**Files:**
- Modify: `README.md`
- Modify: `pyproject.toml`
- Modify: `src/vulca/mcp_server.py`
- Create: `tests/test_visual_discovery_docs_truth.py`

- [ ] **Step 1: Write documentation truth tests**

Create `tests/test_visual_discovery_docs_truth.py` with:

```python
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_stale_tool_count_claims_removed_from_public_docs():
    public_text = "\n".join(
        [
            (ROOT / "README.md").read_text(encoding="utf-8"),
            (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
            (ROOT / "src" / "vulca" / "mcp_server.py").read_text(encoding="utf-8"),
        ]
    )

    assert "20 MCP tools" not in public_text
    assert "21 MCP tools" not in public_text


def test_readme_mentions_visual_discovery_and_mock_boundary():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "/visual-discovery" in readme
    assert "mock sketch" in readme.lower()
    assert "real provider sketch" in readme.lower()
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_docs_truth.py -q
```

Expected: FAIL because current docs still contain stale count language and do not mention `/visual-discovery`.

- [ ] **Step 3: Update README**

In `README.md`, change the headline sentence that currently says `21 MCP tools` to avoid a fixed count. Use:

```markdown
**Agents can plan image edits but can't cut pixels. Vulca is the hands — semantic layer splits, cultural scoring, inpainting, structured prompt composition, and visual discovery — as MCP tools for Claude Code.**
```

In the `What Vulca takes off your agent's hands` table, replace the Brief / Studio row with:

```markdown
| **Discovery / Brief / Studio** | Turn fuzzy intent into direction cards, then a reviewable proposal.md; mock sketch records by default, real provider sketch only after explicit opt-in. | ✅ `/visual-discovery`, ✅ `/visual-brainstorm` | `brief_parse`, `generate_concepts(provider="mock")`, `compose_prompt_from_design` |
```

In the Support section, add:

```markdown
- **Skill source:** [`.agents/skills/visual-discovery/SKILL.md`](.agents/skills/visual-discovery/SKILL.md) — **`/visual-discovery`** explores fuzzy visual intent into taste profile, culture analysis, direction cards, and proposal-ready handoff. It is text/artifact-first: mock sketch records are allowed by default; real provider sketch generation requires explicit opt-in.
```

- [ ] **Step 4: Update pyproject description**

In `pyproject.toml`, replace the `description` value with:

```toml
description = "Agent-native cultural art SDK for image generation, L1-L5 evaluation, layer editing, visual discovery, and cultural traditions. Agents drive creative decisions; Vulca provides hands + eyes."
```

- [ ] **Step 5: Update mcp_server docstring**

In `src/vulca/mcp_server.py`, replace the top docstring count line with:

```python
"""VULCA MCP Server — agent-native surface for cultural art creation, evaluation, and layer editing.

Core workflow tools are organized into five workflow stages. Additional Tool
Protocol analyzers are auto-registered when optional tool dependencies import
successfully.
```

Keep the five-stage list below it, and add `compose_prompt_from_design` to the discovery stage:

```python
  1. Discovery:    list_traditions, search_traditions, get_tradition_guide,
                   brief_parse, compose_prompt_from_design
```

- [ ] **Step 6: Run docs truth tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_docs_truth.py -q
```

Expected: `2 passed`.

- [ ] **Step 7: Commit**

```bash
git add README.md pyproject.toml src/vulca/mcp_server.py tests/test_visual_discovery_docs_truth.py
git commit -m "docs: align visual discovery and MCP tool surface wording"
```

---

## Task 10: Final Integration Verification

**Files:**
- No new files.

- [ ] **Step 1: Run focused visual-discovery suite**

Run:

```bash
PYTHONPATH=src pytest \
  tests/test_visual_discovery_current_state.py \
  tests/test_visual_discovery_types.py \
  tests/test_visual_discovery_terms.py \
  tests/test_visual_discovery_cards.py \
  tests/test_visual_discovery_prompting.py \
  tests/test_visual_discovery_artifacts.py \
  tests/test_visual_discovery_skill_contract.py \
  tests/test_visual_discovery_benchmark.py \
  tests/test_visual_discovery_docs_truth.py \
  -q
```

Expected: all tests pass.

- [ ] **Step 2: Run adjacent regression tests**

Run:

```bash
PYTHONPATH=src pytest \
  tests/test_visual_brainstorm_discovery_integration.py \
  tests/test_prompting.py \
  tests/test_mcp_studio.py \
  tests/test_generate_image_extended_signature.py \
  -q
```

Expected: all tests pass.

- [ ] **Step 3: Scan docs for incomplete markers**

Run:

```bash
python3 -c 'import re, pathlib, sys; pats=["TB"+"D","TO"+"DO","FIX"+"ME","place"+"holder","fill"+" in",r"later\?",r"\?\?\?"]; files=["docs/superpowers/specs/2026-04-29-visual-discovery-design.md","docs/superpowers/plans/2026-04-29-visual-discovery.md",".agents/skills/visual-discovery/SKILL.md"]; bad=[]; [bad.append((f,i+1,line)) for f in files if pathlib.Path(f).exists() for i,line in enumerate(pathlib.Path(f).read_text(encoding="utf-8").splitlines()) if any(re.search(p,line) for p in pats)]; [print(f"{f}:{i}:{line}") for f,i,line in bad]; sys.exit(1 if bad else 0)'
```

Expected: exit code `0` with no output.

- [ ] **Step 4: Check changed files**

Run:

```bash
git status --short
```

Expected: only files changed by this plan appear in the working tree, plus any pre-existing dirty files that were already present before implementation.

- [ ] **Step 5: Commit final verification note if docs changed during verification**

If verification edits were required, commit them:

```bash
git add docs/superpowers/specs/2026-04-29-visual-discovery-design.md docs/superpowers/plans/2026-04-29-visual-discovery.md .agents/skills/visual-discovery/SKILL.md
git commit -m "docs: finalize visual discovery implementation plan"
```

If no verification edits were required, do not create an empty commit.

---

## Self-Review Checklist

- Spec coverage:
  - Current-state facts: Task 1 and Task 9.
  - Schemas: Task 2.
  - Tradition term expansion and visual operations: Task 3.
  - Profile and direction cards: Task 4.
  - Existing prompt composer reuse: Task 5.
  - Discovery artifacts and handoff: Task 6.
  - Skill routing and tool bans: Task 7.
  - Benchmark validation: Task 8.
  - Public docs cleanup: Task 9.
  - Final verification: Task 10.
- Type consistency:
  - `ProviderTarget`, `VisualOps`, `EvaluationFocus`, `DirectionCard`, `TasteProfile`, `SketchPrompt`, and `PromptArtifact` are defined in Task 2 before later tasks import them.
  - `infer_taste_profile`, `generate_direction_cards`, `compose_prompt_from_direction_card`, `write_discovery_artifacts`, and `build_brainstorm_handoff` are introduced before tests depend on them.
- Scope control:
  - No new MCP tool is added in v1.
  - No real provider call is made by default.
  - `layers_*`, `inpaint_artwork`, and real VLM evaluation stay outside discovery.
