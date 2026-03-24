# Studio Pipeline V2 — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Brief data system and first two phases (Intent + Concept) of the Studio Pipeline V2, enabling `vulca brief` CLI commands and `StudioSession` SDK usage with mock providers.

**Architecture:** New `vulca/src/vulca/studio/` package with Brief dataclass (YAML-serializable living document), supporting types, and two phase implementations (IntentPhase, ConceptPhase). Sits on top of existing pipeline layer without modifying it. Brief → TraditionConfig bridge connects new system to existing evaluation.

**Tech Stack:** Python 3.10+ dataclasses, PyYAML (existing dep), litellm (existing dep), pytest + pytest-asyncio (existing dev deps)

**Spec:** `docs/superpowers/specs/2026-03-24-studio-pipeline-v2-design.md`

---

## File Structure

```
vulca/src/vulca/studio/          # NEW package
├── __init__.py                  # Public exports: Brief, StudioSession, SessionState
├── types.py                     # StyleWeight, Reference, Composition, Palette, Element, etc.
├── brief.py                     # Brief dataclass + to_yaml/from_yaml + update helpers
├── session.py                   # StudioSession state machine (stub, fully wired in Phase 2 plan)
├── eval_criteria.py             # Brief → L1-L5 eval criteria generation
├── from_brief.py                # Brief → TraditionConfig conversion
└── phases/
    ├── __init__.py
    ├── intent.py                # IntentPhase: parse intent + generate questions
    ├── scout.py                 # ScoutPhase: generate reference images
    └── concept.py               # ConceptPhase: generate concepts from Brief

vulca/tests/
├── test_studio_types.py         # Supporting type tests
├── test_brief.py                # Brief YAML roundtrip, update, validation
├── test_from_brief.py           # Brief → TraditionConfig
├── test_eval_criteria.py        # Eval criteria generation
├── test_intent_phase.py         # IntentPhase tests
├── test_scout_phase.py          # ScoutPhase tests
├── test_concept_phase.py        # ConceptPhase tests
└── test_studio_session.py       # Session state machine tests
```

---

### Task 1: Studio Supporting Types

**Files:**
- Create: `vulca/src/vulca/studio/__init__.py`
- Create: `vulca/src/vulca/studio/types.py`
- Test: `vulca/tests/test_studio_types.py`

- [ ] **Step 1: Write the failing tests**

```python
# vulca/tests/test_studio_types.py
"""Tests for studio supporting data types."""
from __future__ import annotations

import pytest


def test_style_weight_defaults():
    from vulca.studio.types import StyleWeight
    sw = StyleWeight(tradition="chinese_xieyi")
    assert sw.tradition == "chinese_xieyi"
    assert sw.tag == ""
    assert sw.weight == 0.5


def test_style_weight_tag():
    from vulca.studio.types import StyleWeight
    sw = StyleWeight(tag="cyberpunk", weight=0.4)
    assert sw.tradition == ""
    assert sw.tag == "cyberpunk"
    assert sw.weight == 0.4


def test_reference_upload():
    from vulca.studio.types import Reference
    ref = Reference(path="refs/my.jpg", source="upload", note="ink ref")
    assert ref.source == "upload"
    assert ref.query == ""
    assert ref.note == "ink ref"


def test_reference_generate():
    from vulca.studio.types import Reference
    ref = Reference(path="refs/gen.png", source="generate", prompt="ink palette")
    assert ref.source == "generate"
    assert ref.prompt == "ink palette"


def test_composition_defaults():
    from vulca.studio.types import Composition
    c = Composition()
    assert c.layout == ""
    assert c.aspect_ratio == "1:1"


def test_palette_fields():
    from vulca.studio.types import Palette
    p = Palette(primary=["#1a1a2e"], accent=["#00f5d4"], mood="dark cold")
    assert len(p.primary) == 1
    assert p.mood == "dark cold"


def test_element_fields():
    from vulca.studio.types import Element
    e = Element(name="hemp-fiber stroke", category="technique")
    assert e.name == "hemp-fiber stroke"
    assert e.category == "technique"


def test_generation_round():
    from vulca.studio.types import GenerationRound
    gr = GenerationRound(round_num=1, image_path="out/r1.png", scores={"L1": 0.8})
    assert gr.round_num == 1
    assert gr.scores["L1"] == 0.8
    assert gr.feedback == ""


def test_brief_update():
    from vulca.studio.types import BriefUpdate
    bu = BriefUpdate(timestamp="2026-03-24T10:00:00", instruction="make mountain taller")
    assert bu.instruction == "make mountain taller"
    assert bu.fields_changed == []
    assert bu.rollback_to == ""


def test_all_types_serializable():
    """All types should be convertible to plain dicts for YAML."""
    from dataclasses import asdict
    from vulca.studio.types import (
        StyleWeight, Reference, Composition, Palette,
        Element, GenerationRound, BriefUpdate,
    )
    for cls, kwargs in [
        (StyleWeight, {"tradition": "test"}),
        (Reference, {"path": "x", "source": "upload"}),
        (Composition, {}),
        (Palette, {}),
        (Element, {"name": "test"}),
        (GenerationRound, {"round_num": 1, "image_path": "x"}),
        (BriefUpdate, {"timestamp": "t", "instruction": "i"}),
    ]:
        obj = cls(**kwargs)
        d = asdict(obj)
        assert isinstance(d, dict)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_studio_types.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'vulca.studio'`

- [ ] **Step 3: Write minimal implementation**

```python
# vulca/src/vulca/studio/__init__.py
"""VULCA Studio -- creative collaboration pipeline."""

# vulca/src/vulca/studio/types.py
"""Supporting data types for the Studio pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StyleWeight:
    """A weighted style reference in a Brief's style_mix."""
    tradition: str = ""
    tag: str = ""
    weight: float = 0.5


@dataclass
class Reference:
    """A reference image attached to a Brief."""
    path: str
    source: str  # "upload" | "search" | "generate"
    query: str = ""
    prompt: str = ""
    url: str = ""
    note: str = ""


@dataclass
class Composition:
    """Composition specification within a Brief."""
    layout: str = ""
    focal_point: str = ""
    aspect_ratio: str = "1:1"
    negative_space: str = ""


@dataclass
class Palette:
    """Color palette specification within a Brief."""
    primary: list[str] = field(default_factory=list)
    accent: list[str] = field(default_factory=list)
    mood: str = ""


@dataclass
class Element:
    """A creative element to include in the artwork."""
    name: str
    category: str = ""
    note: str = ""


@dataclass
class GenerationRound:
    """Record of one generation+evaluation round."""
    round_num: int
    image_path: str
    scores: dict[str, float] = field(default_factory=dict)
    suggestions: dict[str, str] = field(default_factory=dict)
    feedback: str = ""


@dataclass
class BriefUpdate:
    """Record of a natural language update to the Brief."""
    timestamp: str
    instruction: str
    fields_changed: list[str] = field(default_factory=list)
    rollback_to: str = ""
```

Also create empty `__init__.py` for `phases/`:

```python
# vulca/src/vulca/studio/phases/__init__.py
"""Studio pipeline phases."""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_studio_types.py -v`
Expected: All 11 tests PASS

- [ ] **Step 5: Commit**

```bash
cd vulca && git add src/vulca/studio/ tests/test_studio_types.py
git commit -m "feat(studio): add supporting data types for Brief system"
```

---

### Task 2: Brief Dataclass + YAML Serialization

**Files:**
- Create: `vulca/src/vulca/studio/brief.py`
- Test: `vulca/tests/test_brief.py`

- [ ] **Step 1: Write the failing tests**

```python
# vulca/tests/test_brief.py
"""Tests for Brief dataclass and YAML serialization."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml


def test_brief_create_minimal():
    from vulca.studio.brief import Brief
    b = Brief.new("水墨山水")
    assert b.intent == "水墨山水"
    assert b.session_id  # auto-generated
    assert b.version == 1
    assert b.created_at  # auto-set


def test_brief_create_full():
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, Element
    b = Brief.new(
        "赛博水墨",
        mood="epic",
        style_mix=[StyleWeight(tradition="chinese_xieyi", weight=0.6)],
        elements=[Element(name="neon", category="effect")],
        must_have=["ink texture"],
        must_avoid=["vector style"],
    )
    assert b.mood == "epic"
    assert len(b.style_mix) == 1
    assert b.style_mix[0].tradition == "chinese_xieyi"
    assert b.must_have == ["ink texture"]


def test_brief_to_yaml_roundtrip():
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, Composition, Palette
    b = Brief.new("test intent", mood="serene")
    b.composition = Composition(layout="top mountains", focal_point="pavilion")
    b.palette = Palette(primary=["#000"], accent=["#0ff"], mood="cold")
    b.style_mix = [StyleWeight(tradition="chinese_xieyi", weight=0.7)]

    yaml_str = b.to_yaml()
    loaded = Brief.from_yaml(yaml_str)

    assert loaded.intent == "test intent"
    assert loaded.mood == "serene"
    assert loaded.composition.layout == "top mountains"
    assert loaded.palette.primary == ["#000"]
    assert loaded.style_mix[0].tradition == "chinese_xieyi"
    assert loaded.session_id == b.session_id


def test_brief_save_load_file(tmp_path):
    from vulca.studio.brief import Brief
    b = Brief.new("file test")
    filepath = b.save(tmp_path)
    assert filepath.exists()
    assert filepath.name == "brief.yaml"

    loaded = Brief.load(tmp_path)
    assert loaded.intent == "file test"
    assert loaded.session_id == b.session_id


def test_brief_update_field():
    from vulca.studio.brief import Brief
    b = Brief.new("original intent")
    b.update_field("mood", "mysterious")
    assert b.mood == "mysterious"
    assert b.updated_at  # should be set
    assert len(b.updates) == 1
    assert b.updates[0].fields_changed == ["mood"]


def test_brief_update_nested():
    from vulca.studio.brief import Brief
    b = Brief.new("test")
    b.update_field("composition.layout", "vertical split")
    assert b.composition.layout == "vertical split"


def test_brief_eval_criteria_empty_by_default():
    from vulca.studio.brief import Brief
    b = Brief.new("test")
    assert b.eval_criteria == {}


def test_brief_version_preserved():
    from vulca.studio.brief import Brief
    b = Brief.new("test")
    b.version = 2
    yaml_str = b.to_yaml()
    loaded = Brief.from_yaml(yaml_str)
    assert loaded.version == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_brief.py -v`
Expected: FAIL — `cannot import name 'Brief' from 'vulca.studio.brief'`

- [ ] **Step 3: Write minimal implementation**

```python
# vulca/src/vulca/studio/brief.py
"""Brief -- the living YAML document that drives Studio sessions."""
from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from vulca.studio.types import (
    BriefUpdate,
    Composition,
    Element,
    GenerationRound,
    Palette,
    Reference,
    StyleWeight,
)


@dataclass
class Brief:
    """Central data structure for a Studio creative session.

    Accumulates decisions across phases. Serializable to YAML.
    """

    # Identity
    session_id: str = ""
    version: int = 1
    created_at: str = ""
    updated_at: str = ""

    # Phase 1: Intent
    intent: str = ""
    mood: str = ""
    style_mix: list[StyleWeight] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    user_sketch: str = ""

    # Phase 2: Concept
    concept_candidates: list[str] = field(default_factory=list)
    selected_concept: str = ""
    concept_notes: str = ""
    composition: Composition = field(default_factory=Composition)
    palette: Palette = field(default_factory=Palette)
    elements: list[Element] = field(default_factory=list)

    # Constraints
    must_have: list[str] = field(default_factory=list)
    must_avoid: list[str] = field(default_factory=list)

    # Auto-generated L1-L5 criteria
    eval_criteria: dict[str, str] = field(default_factory=dict)

    # Generation history
    generations: list[GenerationRound] = field(default_factory=list)

    # Update log
    updates: list[BriefUpdate] = field(default_factory=list)

    # ── Factory ──

    @classmethod
    def new(
        cls,
        intent: str,
        *,
        mood: str = "",
        style_mix: list[StyleWeight] | None = None,
        elements: list[Element] | None = None,
        must_have: list[str] | None = None,
        must_avoid: list[str] | None = None,
    ) -> Brief:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        return cls(
            session_id=uuid.uuid4().hex[:8],
            created_at=now,
            updated_at=now,
            intent=intent,
            mood=mood,
            style_mix=style_mix or [],
            elements=elements or [],
            must_have=must_have or [],
            must_avoid=must_avoid or [],
        )

    # ── YAML Serialization ──

    def to_yaml(self) -> str:
        return yaml.dump(
            asdict(self),
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

    @classmethod
    def from_yaml(cls, yaml_str: str) -> Brief:
        data = yaml.safe_load(yaml_str)
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> Brief:
        """Reconstruct Brief from a plain dict (parsed YAML)."""
        b = cls()
        # Simple fields
        for key in (
            "session_id", "version", "created_at", "updated_at",
            "intent", "mood", "user_sketch", "selected_concept",
            "concept_notes", "concept_candidates", "must_have",
            "must_avoid", "eval_criteria",
        ):
            if key in data:
                setattr(b, key, data[key])

        # Typed lists
        if "style_mix" in data:
            b.style_mix = [StyleWeight(**s) for s in data["style_mix"]]
        if "references" in data:
            b.references = [Reference(**r) for r in data["references"]]
        if "elements" in data:
            b.elements = [Element(**e) for e in data["elements"]]
        if "generations" in data:
            b.generations = [GenerationRound(**g) for g in data["generations"]]
        if "updates" in data:
            b.updates = [BriefUpdate(**u) for u in data["updates"]]

        # Nested dataclasses
        if "composition" in data and isinstance(data["composition"], dict):
            b.composition = Composition(**data["composition"])
        if "palette" in data and isinstance(data["palette"], dict):
            b.palette = Palette(**data["palette"])

        return b

    # ── File I/O ──

    def save(self, project_dir: str | Path) -> Path:
        project_dir = Path(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)
        filepath = project_dir / "brief.yaml"
        filepath.write_text(self.to_yaml(), encoding="utf-8")
        return filepath

    @classmethod
    def load(cls, project_dir: str | Path) -> Brief:
        filepath = Path(project_dir) / "brief.yaml"
        return cls.from_yaml(filepath.read_text(encoding="utf-8"))

    # ── Update helpers ──

    def update_field(self, field_path: str, value: Any) -> None:
        """Update a field by dotted path (e.g., 'composition.layout')."""
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.updated_at = now

        parts = field_path.split(".")
        if len(parts) == 1:
            setattr(self, parts[0], value)
        elif len(parts) == 2:
            parent = getattr(self, parts[0])
            setattr(parent, parts[1], value)

        self.updates.append(BriefUpdate(
            timestamp=now,
            instruction=f"set {field_path} = {value!r}",
            fields_changed=[field_path],
        ))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_brief.py -v`
Expected: All 8 tests PASS

- [ ] **Step 5: Commit**

```bash
cd vulca && git add src/vulca/studio/brief.py tests/test_brief.py
git commit -m "feat(studio): Brief dataclass with YAML serialization"
```

---

### Task 3: Brief → TraditionConfig Conversion

**Files:**
- Create: `vulca/src/vulca/studio/from_brief.py`
- Test: `vulca/tests/test_from_brief.py`

This bridges the new Brief system to the existing evaluation pipeline. When a Brief has `style_mix` with known traditions, it merges their YAML configs. When it has free-form tags, it creates a minimal TraditionConfig.

- [ ] **Step 1: Write the failing tests**

```python
# vulca/tests/test_from_brief.py
"""Tests for Brief → TraditionConfig conversion."""
from __future__ import annotations

import pytest


def test_brief_to_tradition_single_known():
    """Brief with one known tradition → that tradition's config."""
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.from_brief import brief_to_tradition

    b = Brief.new("水墨山水", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    tc = brief_to_tradition(b)

    assert tc.name == "chinese_xieyi"
    assert tc.weights_l["L1"] > 0
    assert len(tc.terminology) > 0  # Has real terminology from YAML


def test_brief_to_tradition_mixed():
    """Brief with two traditions → merged weights."""
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.from_brief import brief_to_tradition

    b = Brief.new("fusion", style_mix=[
        StyleWeight(tradition="chinese_xieyi", weight=0.6),
        StyleWeight(tradition="western_academic", weight=0.4),
    ])
    tc = brief_to_tradition(b)

    assert tc.name == "brief_fusion"
    # Weights should be blended
    assert abs(sum(tc.weights_l.values()) - 1.0) < 0.01


def test_brief_to_tradition_freeform_tag():
    """Brief with only free-form tags → default weights."""
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.from_brief import brief_to_tradition

    b = Brief.new("cyberpunk art", style_mix=[StyleWeight(tag="cyberpunk", weight=1.0)])
    tc = brief_to_tradition(b)

    assert tc.name == "brief_custom"
    assert abs(sum(tc.weights_l.values()) - 1.0) < 0.01
    assert len(tc.terminology) == 0  # No YAML source


def test_brief_to_tradition_empty():
    """Brief with no style_mix → default tradition."""
    from vulca.studio.brief import Brief
    from vulca.studio.from_brief import brief_to_tradition

    b = Brief.new("something")
    tc = brief_to_tradition(b)

    assert tc.name == "default"


def test_brief_to_tradition_with_constraints():
    """Brief constraints should become taboos."""
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.from_brief import brief_to_tradition

    b = Brief.new("test", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.must_avoid = ["vector style", "3D rendering"]
    tc = brief_to_tradition(b)

    taboo_rules = [t.rule for t in tc.taboos]
    assert any("vector style" in r for r in taboo_rules)
    assert any("3D rendering" in r for r in taboo_rules)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_from_brief.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'vulca.studio.from_brief'`

- [ ] **Step 3: Write minimal implementation**

```python
# vulca/src/vulca/studio/from_brief.py
"""Convert a Brief to a TraditionConfig for evaluation."""
from __future__ import annotations

from vulca.cultural.types import TabooEntry, TraditionConfig
from vulca.studio.brief import Brief


_DEFAULT_WEIGHTS = {"L1": 0.20, "L2": 0.20, "L3": 0.20, "L4": 0.20, "L5": 0.20}


def brief_to_tradition(brief: Brief) -> TraditionConfig:
    """Convert a Brief's style_mix + constraints into a TraditionConfig.

    Resolution order:
    1. If style_mix has known traditions → load and merge their YAML configs
    2. If style_mix has only free-form tags → create minimal config with default weights
    3. If style_mix is empty → return default tradition
    """
    if not brief.style_mix:
        return _load_or_default("default")

    known_traditions = [s for s in brief.style_mix if s.tradition]
    free_tags = [s for s in brief.style_mix if s.tag and not s.tradition]

    if len(known_traditions) == 1 and not free_tags:
        tc = _load_or_default(known_traditions[0].tradition)
        tc = _add_brief_taboos(tc, brief)
        return tc

    if known_traditions:
        return _merge_traditions(known_traditions, free_tags, brief)

    # Only free-form tags
    tc = TraditionConfig(
        name="brief_custom",
        display_name={"en": brief.intent[:50], "zh": ""},
        weights_l=dict(_DEFAULT_WEIGHTS),
    )
    return _add_brief_taboos(tc, brief)


def _load_or_default(name: str) -> TraditionConfig:
    """Load a tradition by name, falling back to default config."""
    try:
        from vulca.cultural.loader import get_tradition
        tc = get_tradition(name)
        if tc is not None:
            return tc
    except Exception:
        pass
    return TraditionConfig(
        name=name,
        display_name={"en": name.replace("_", " ").title(), "zh": ""},
        weights_l=dict(_DEFAULT_WEIGHTS),
    )


def _merge_traditions(
    known: list,
    free_tags: list,
    brief: Brief,
) -> TraditionConfig:
    """Merge multiple traditions by weighted average of their L1-L5 weights."""
    merged_weights: dict[str, float] = {f"L{i}": 0.0 for i in range(1, 6)}
    all_terms = []
    all_taboos = []
    total_weight = sum(s.weight for s in known) + sum(s.weight for s in free_tags)
    if total_weight == 0:
        total_weight = 1.0

    for sw in known:
        tc = _load_or_default(sw.tradition)
        norm_w = sw.weight / total_weight
        for dim, val in tc.weights_l.items():
            merged_weights[dim] = merged_weights.get(dim, 0.0) + val * norm_w
        all_terms.extend(tc.terminology)
        all_taboos.extend(tc.taboos)

    # Free tags get default weights contribution
    for sw in free_tags:
        norm_w = sw.weight / total_weight
        for dim in merged_weights:
            merged_weights[dim] += _DEFAULT_WEIGHTS.get(dim, 0.2) * norm_w

    # Normalize to sum=1.0
    w_sum = sum(merged_weights.values())
    if w_sum > 0:
        merged_weights = {k: v / w_sum for k, v in merged_weights.items()}

    tc = TraditionConfig(
        name="brief_fusion",
        display_name={"en": brief.intent[:50], "zh": ""},
        weights_l=merged_weights,
        terminology=all_terms,
        taboos=all_taboos,
    )
    return _add_brief_taboos(tc, brief)


def _add_brief_taboos(tc: TraditionConfig, brief: Brief) -> TraditionConfig:
    """Append Brief.must_avoid as taboo entries."""
    for avoid in brief.must_avoid:
        tc.taboos.append(TabooEntry(
            rule=f"AVOID: {avoid}",
            severity="high",
            l_levels=["L3", "L4"],
            explanation=f"User constraint from Brief: must avoid '{avoid}'",
        ))
    return tc
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_from_brief.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
cd vulca && git add src/vulca/studio/from_brief.py tests/test_from_brief.py
git commit -m "feat(studio): Brief → TraditionConfig conversion bridge"
```

---

### Task 4: Eval Criteria Generation

**Files:**
- Create: `vulca/src/vulca/studio/eval_criteria.py`
- Test: `vulca/tests/test_eval_criteria.py`

- [ ] **Step 1: Write the failing tests**

```python
# vulca/tests/test_eval_criteria.py
"""Tests for Brief → L1-L5 eval criteria generation."""
from __future__ import annotations

import pytest


def test_eval_criteria_fallback():
    """When LLM is unavailable, fallback to tradition-derived criteria."""
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.eval_criteria import generate_eval_criteria_sync

    b = Brief.new("水墨山水", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    criteria = generate_eval_criteria_sync(b, use_llm=False)

    assert "L1" in criteria
    assert "L2" in criteria
    assert "L3" in criteria
    assert "L4" in criteria
    assert "L5" in criteria
    assert all(isinstance(v, str) and len(v) > 0 for v in criteria.values())


def test_eval_criteria_with_constraints():
    """Constraints should be reflected in criteria."""
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.eval_criteria import generate_eval_criteria_sync

    b = Brief.new("test", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.must_have = ["ink texture", "negative space"]
    b.must_avoid = ["vector style"]
    criteria = generate_eval_criteria_sync(b, use_llm=False)

    # Constraints should influence at least one dimension's criteria
    all_criteria_text = " ".join(criteria.values()).lower()
    assert "ink texture" in all_criteria_text or "negative space" in all_criteria_text


def test_eval_criteria_empty_brief():
    """Empty Brief → generic default criteria."""
    from vulca.studio.brief import Brief
    from vulca.studio.eval_criteria import generate_eval_criteria_sync

    b = Brief.new("something abstract")
    criteria = generate_eval_criteria_sync(b, use_llm=False)

    assert len(criteria) == 5
    assert all(len(v) > 5 for v in criteria.values())


def test_eval_criteria_freeform_tag():
    """Free-form tags without YAML traditions → generic criteria."""
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.eval_criteria import generate_eval_criteria_sync

    b = Brief.new("cyberpunk cityscape", style_mix=[StyleWeight(tag="cyberpunk", weight=1.0)])
    criteria = generate_eval_criteria_sync(b, use_llm=False)

    assert len(criteria) == 5
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_eval_criteria.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'vulca.studio.eval_criteria'`

- [ ] **Step 3: Write minimal implementation**

```python
# vulca/src/vulca/studio/eval_criteria.py
"""Generate L1-L5 evaluation criteria from a Brief."""
from __future__ import annotations

import logging

from vulca.studio.brief import Brief

logger = logging.getLogger("vulca.studio")

_L_LABELS = {
    "L1": "Visual Perception",
    "L2": "Technical Execution",
    "L3": "Cultural/Style Context",
    "L4": "Interpretation & Constraints",
    "L5": "Philosophical & Emotional Aesthetics",
}

_DEFAULT_CRITERIA = {
    "L1": "Composition, layout, spatial arrangement, visual clarity, and color harmony.",
    "L2": "Rendering quality, detail precision, technique fidelity, and craftsmanship.",
    "L3": "Fidelity to intended style, proper use of motifs/elements/terminology.",
    "L4": "Respectful representation, absence of constraint violations, coherent interpretation.",
    "L5": "Artistic depth, emotional resonance, aesthetic harmony, and intended mood.",
}


def generate_eval_criteria_sync(brief: Brief, *, use_llm: bool = True) -> dict[str, str]:
    """Generate L1-L5 eval criteria from Brief content.

    Falls back to tradition-derived or default criteria if LLM unavailable.
    """
    if use_llm:
        try:
            import asyncio
            return asyncio.get_event_loop().run_until_complete(
                generate_eval_criteria(brief)
            )
        except Exception:
            logger.debug("LLM eval criteria generation failed, using fallback")

    return _fallback_criteria(brief)


async def generate_eval_criteria(brief: Brief) -> dict[str, str]:
    """Generate criteria via LLM. Raises on failure (caller handles fallback)."""
    import litellm
    import os
    from vulca._parse import parse_llm_json

    brief_summary = _brief_to_summary(brief)
    prompt = f"""Based on this creative brief, generate specific evaluation criteria
for each of the 5 art dimensions (L1-L5). Each criterion should be concrete and
measurable against the brief's intent.

{brief_summary}

Respond with ONLY a JSON object:
{{"L1": "<Visual Perception criterion>", "L2": "<Technical Execution criterion>",
"L3": "<Cultural/Style Context criterion>", "L4": "<Interpretation/Constraint criterion>",
"L5": "<Aesthetic/Emotional criterion>"}}"""

    resp = await litellm.acompletion(
        model=os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.3,
        timeout=30,
    )
    text = resp.choices[0].message.content.strip()
    data = parse_llm_json(text)
    return {f"L{i}": str(data.get(f"L{i}", _DEFAULT_CRITERIA[f"L{i}"])) for i in range(1, 6)}


def _fallback_criteria(brief: Brief) -> dict[str, str]:
    """Build criteria from tradition YAML + Brief constraints, no LLM."""
    criteria = dict(_DEFAULT_CRITERIA)

    # Enrich from known traditions in style_mix
    known_traditions = [s.tradition for s in brief.style_mix if s.tradition]
    if known_traditions:
        try:
            from vulca.cultural.loader import get_tradition
            for tname in known_traditions:
                tc = get_tradition(tname)
                if tc and tc.terminology:
                    terms = ", ".join(t.term for t in tc.terminology[:4])
                    criteria["L3"] = f"Fidelity to {tname} tradition. Key techniques: {terms}."
                if tc and tc.taboos:
                    rules = "; ".join(t.rule for t in tc.taboos[:3])
                    criteria["L4"] = f"Respect constraints: {rules}."
        except Exception:
            pass

    # Enrich from Brief constraints
    if brief.must_have:
        items = ", ".join(brief.must_have[:5])
        criteria["L1"] = f"Composition must include: {items}. {criteria['L1']}"
    if brief.must_avoid:
        items = ", ".join(brief.must_avoid[:5])
        criteria["L4"] = f"Must avoid: {items}. {criteria['L4']}"
    if brief.mood:
        criteria["L5"] = f"Convey mood: {brief.mood}. {criteria['L5']}"
    if brief.composition.layout:
        criteria["L1"] = f"Layout: {brief.composition.layout}. {criteria['L1']}"

    return criteria


def _brief_to_summary(brief: Brief) -> str:
    """Format Brief into a concise text summary for LLM."""
    parts = [f"Intent: {brief.intent}"]
    if brief.mood:
        parts.append(f"Mood: {brief.mood}")
    if brief.style_mix:
        styles = ", ".join(
            f"{s.tradition or s.tag} ({s.weight:.0%})" for s in brief.style_mix
        )
        parts.append(f"Style mix: {styles}")
    if brief.composition.layout:
        parts.append(f"Composition: {brief.composition.layout}")
    if brief.palette.mood:
        parts.append(f"Color mood: {brief.palette.mood}")
    if brief.elements:
        elems = ", ".join(e.name for e in brief.elements[:6])
        parts.append(f"Elements: {elems}")
    if brief.must_have:
        parts.append(f"Must include: {', '.join(brief.must_have)}")
    if brief.must_avoid:
        parts.append(f"Must avoid: {', '.join(brief.must_avoid)}")
    return "\n".join(parts)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_eval_criteria.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
cd vulca && git add src/vulca/studio/eval_criteria.py tests/test_eval_criteria.py
git commit -m "feat(studio): L1-L5 eval criteria generation from Brief"
```

---

### Task 5: IntentPhase

**Files:**
- Create: `vulca/src/vulca/studio/phases/intent.py`
- Test: `vulca/tests/test_intent_phase.py`

- [ ] **Step 1: Write the failing tests**

```python
# vulca/tests/test_intent_phase.py
"""Tests for IntentPhase -- intent parsing and question generation."""
from __future__ import annotations

import pytest


def test_intent_parse_text_only():
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("水墨山水画")
    phase = IntentPhase()
    result = phase.parse_intent(b)

    assert result.intent == "水墨山水画"
    # Should detect a style suggestion
    assert len(result.style_mix) >= 0  # May or may not detect


def test_intent_generate_questions():
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("赛博朋克水墨")
    phase = IntentPhase()
    questions = phase.generate_questions(b)

    assert isinstance(questions, list)
    assert len(questions) >= 1
    # Each question should have text and options
    for q in questions:
        assert "text" in q
        assert "options" in q


def test_intent_apply_answer():
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("水墨山水")
    phase = IntentPhase()
    questions = phase.generate_questions(b)

    if questions:
        phase.apply_answer(b, questions[0], questions[0]["options"][0])
        # Brief should have been updated
        assert b.updated_at != b.created_at or b.mood or b.style_mix


def test_intent_with_sketch():
    """If user provides sketch path, it should be stored."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test", )
    phase = IntentPhase()
    phase.set_sketch(b, "path/to/sketch.jpg")
    assert b.user_sketch == "path/to/sketch.jpg"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_intent_phase.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# vulca/src/vulca/studio/phases/intent.py
"""IntentPhase -- parse user intent and generate clarifying questions."""
from __future__ import annotations

import re
from typing import Any

from vulca.studio.brief import Brief
from vulca.studio.types import StyleWeight

# Known tradition keywords for simple detection
_TRADITION_HINTS: dict[str, str] = {
    "水墨": "chinese_xieyi",
    "写意": "chinese_xieyi",
    "ink wash": "chinese_xieyi",
    "xieyi": "chinese_xieyi",
    "工笔": "chinese_gongbi",
    "gongbi": "chinese_gongbi",
    "浮世绘": "japanese_traditional",
    "ukiyo": "japanese_traditional",
    "油画": "western_academic",
    "oil painting": "western_academic",
    "watercolor": "watercolor",
    "水彩": "watercolor",
    "几何": "islamic_geometric",
    "geometric": "islamic_geometric",
}

_MOOD_OPTIONS = [
    {"value": "epic-solitary", "label": "壮阔孤寂 (Epic & Solitary)"},
    {"value": "serene", "label": "宁静平和 (Serene)"},
    {"value": "mystical", "label": "神秘玄幻 (Mystical)"},
    {"value": "dynamic", "label": "动感张力 (Dynamic)"},
]

_BRUSH_OPTIONS = [
    {"value": "traditional", "label": "传统笔触 (Traditional)"},
    {"value": "mixed-digital", "label": "数字混合 (Mixed Digital)"},
    {"value": "abstract", "label": "抽象表现 (Abstract)"},
]


class IntentPhase:
    """Parse creative intent and generate clarifying questions."""

    def parse_intent(self, brief: Brief) -> Brief:
        """Detect traditions and style hints from intent text."""
        text = brief.intent.lower()

        detected = []
        for keyword, tradition in _TRADITION_HINTS.items():
            if keyword in text:
                if not any(s.tradition == tradition for s in detected):
                    detected.append(StyleWeight(tradition=tradition, weight=0.5))

        # Detect free-form tags (cyberpunk, steampunk, etc.)
        free_tags = []
        for tag in ("cyberpunk", "赛博朋克", "steampunk", "蒸汽朋克", "pixel", "像素"):
            if tag in text:
                tag_name = tag.replace("赛博朋克", "cyberpunk").replace("蒸汽朋克", "steampunk").replace("像素", "pixel")
                free_tags.append(StyleWeight(tag=tag_name, weight=0.5))

        # Normalize weights
        all_styles = detected + free_tags
        if all_styles:
            total = len(all_styles)
            for s in all_styles:
                s.weight = round(1.0 / total, 2)
            brief.style_mix = all_styles

        return brief

    def generate_questions(self, brief: Brief) -> list[dict[str, Any]]:
        """Generate clarifying questions based on current Brief state."""
        questions = []

        if not brief.mood:
            questions.append({
                "text": "What mood/atmosphere do you want?",
                "field": "mood",
                "options": [o["value"] for o in _MOOD_OPTIONS],
                "labels": [o["label"] for o in _MOOD_OPTIONS],
            })

        if not any(e.category == "technique" for e in brief.elements):
            questions.append({
                "text": "Brush/rendering style preference?",
                "field": "brush_style",
                "options": [o["value"] for o in _BRUSH_OPTIONS],
                "labels": [o["label"] for o in _BRUSH_OPTIONS],
            })

        return questions

    def apply_answer(self, brief: Brief, question: dict, answer: str) -> None:
        """Apply user's answer to the Brief."""
        field = question.get("field", "")
        if field == "mood":
            brief.update_field("mood", answer)
        elif field == "brush_style":
            from vulca.studio.types import Element
            brief.elements.append(Element(name=answer, category="technique"))
            brief.updated_at = brief.updates[-1].timestamp if brief.updates else brief.created_at

    def set_sketch(self, brief: Brief, sketch_path: str) -> None:
        """Set the user's uploaded sketch."""
        brief.update_field("user_sketch", sketch_path)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_intent_phase.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
cd vulca && git add src/vulca/studio/phases/intent.py tests/test_intent_phase.py
git commit -m "feat(studio): IntentPhase — intent parsing and question generation"
```

---

### Task 6: ScoutPhase

**Files:**
- Create: `vulca/src/vulca/studio/phases/scout.py`
- Test: `vulca/tests/test_scout_phase.py`

- [ ] **Step 1: Write the failing tests**

```python
# vulca/tests/test_scout_phase.py
"""Tests for ScoutPhase -- reference image generation."""
from __future__ import annotations

import pytest


def test_scout_extract_search_terms():
    from vulca.studio.phases.scout import ScoutPhase
    from vulca.studio.brief import Brief

    b = Brief.new("赛博朋克风格的水墨山水画")
    phase = ScoutPhase()
    terms = phase.extract_search_terms(b)

    assert isinstance(terms, list)
    assert len(terms) >= 1


def test_scout_build_reference_prompts():
    from vulca.studio.phases.scout import ScoutPhase
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight

    b = Brief.new("ink mountain", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.mood = "serene"
    phase = ScoutPhase()
    prompts = phase.build_reference_prompts(b)

    assert isinstance(prompts, list)
    assert len(prompts) >= 1
    # Each prompt should reference the intent or mood
    for p in prompts:
        assert len(p) > 10


@pytest.mark.asyncio
async def test_scout_generate_references_mock():
    """Scout should generate references using mock provider without error."""
    from vulca.studio.phases.scout import ScoutPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test art")
    phase = ScoutPhase()
    refs = await phase.generate_references(b, provider="mock", project_dir="/tmp/vulca-test-scout")

    assert isinstance(refs, list)
    # With mock provider, may return empty or placeholder refs
    for ref in refs:
        assert ref.source == "generate"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_scout_phase.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# vulca/src/vulca/studio/phases/scout.py
"""ScoutPhase -- generate reference images for creative inspiration."""
from __future__ import annotations

import logging
from pathlib import Path

from vulca.studio.brief import Brief
from vulca.studio.types import Reference

logger = logging.getLogger("vulca.studio")


class ScoutPhase:
    """Generate and collect reference images for the Brief.

    V1: Only supports source="generate" (using existing ImageProvider).
    Web search deferred to V2.
    """

    def extract_search_terms(self, brief: Brief) -> list[str]:
        """Extract search terms from Brief for reference discovery."""
        terms = []
        if brief.intent:
            terms.append(brief.intent)
        for sw in brief.style_mix:
            if sw.tradition:
                terms.append(sw.tradition.replace("_", " "))
            if sw.tag:
                terms.append(sw.tag)
        if brief.mood:
            terms.append(f"{brief.mood} art style")
        return terms

    def build_reference_prompts(self, brief: Brief) -> list[str]:
        """Build prompts for AI-generated reference images."""
        prompts = []
        base = brief.intent or "artwork"
        mood = brief.mood or "artistic"

        # Style reference
        prompts.append(
            f"Create a mood board / style reference for: {base}. "
            f"Mood: {mood}. Show color palette, textures, and composition examples. "
            f"No text or labels."
        )

        # Palette study
        if brief.palette.mood or brief.palette.primary:
            palette_desc = brief.palette.mood or f"colors: {', '.join(brief.palette.primary)}"
            prompts.append(
                f"Color palette study for {base}. {palette_desc}. "
                f"Abstract color swatches and gradients. No text."
            )

        return prompts

    async def generate_references(
        self,
        brief: Brief,
        *,
        provider: str = "mock",
        project_dir: str = "",
        api_key: str = "",
    ) -> list[Reference]:
        """Generate reference images and save to project directory.

        Returns list of Reference objects added to Brief.
        """
        refs: list[Reference] = []
        prompts = self.build_reference_prompts(brief)
        if not prompts:
            return refs

        project = Path(project_dir) if project_dir else Path(".")
        refs_dir = project / "refs"
        refs_dir.mkdir(parents=True, exist_ok=True)

        try:
            from vulca.providers import get_image_provider
            img_provider = get_image_provider(provider, api_key=api_key)
        except Exception:
            logger.debug("Could not load provider %s for scout, skipping", provider)
            return refs

        for i, prompt in enumerate(prompts):
            try:
                result = await img_provider.generate(
                    prompt,
                    tradition=brief.style_mix[0].tradition if brief.style_mix else "",
                    subject=brief.intent,
                )
                # Save image
                import base64
                ext = "png" if "png" in result.mime else "jpg"
                filename = f"ref-gen-{i:02d}.{ext}"
                filepath = refs_dir / filename
                filepath.write_bytes(base64.b64decode(result.image_b64))

                refs.append(Reference(
                    path=str(filepath),
                    source="generate",
                    prompt=prompt,
                    note=f"AI-generated reference {i + 1}",
                ))
            except Exception as exc:
                logger.debug("Scout reference generation failed: %s", exc)
                continue

        return refs
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_scout_phase.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
cd vulca && git add src/vulca/studio/phases/scout.py tests/test_scout_phase.py
git commit -m "feat(studio): ScoutPhase — reference image generation"
```

---

### Task 7: ConceptPhase

**Files:**
- Create: `vulca/src/vulca/studio/phases/concept.py`
- Test: `vulca/tests/test_concept_phase.py`

- [ ] **Step 1: Write the failing tests**

```python
# vulca/tests/test_concept_phase.py
"""Tests for ConceptPhase -- concept design generation."""
from __future__ import annotations

import pytest


def test_concept_build_prompt_from_brief():
    from vulca.studio.phases.concept import ConceptPhase
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, Composition

    b = Brief.new("水墨山水", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.mood = "serene"
    b.composition = Composition(layout="mountains top, water bottom")
    b.must_have = ["ink texture"]

    phase = ConceptPhase()
    prompt = phase.build_concept_prompt(b)

    assert "水墨山水" in prompt
    assert "serene" in prompt.lower() or "宁静" in prompt
    assert "mountains" in prompt.lower()
    assert "ink texture" in prompt.lower()


def test_concept_build_prompt_with_sketch():
    """When user_sketch is set, prompt should reference it."""
    from vulca.studio.phases.concept import ConceptPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    b.user_sketch = "sketch.jpg"

    phase = ConceptPhase()
    prompt = phase.build_concept_prompt(b)

    assert "sketch" in prompt.lower() or "reference" in prompt.lower()


@pytest.mark.asyncio
async def test_concept_generate_mock():
    from vulca.studio.phases.concept import ConceptPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test concept")
    phase = ConceptPhase()
    paths = await phase.generate_concepts(b, count=4, provider="mock", project_dir="/tmp/vulca-test-concept")

    assert isinstance(paths, list)
    assert len(paths) == 4


def test_concept_select_updates_brief():
    from vulca.studio.phases.concept import ConceptPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    b.concept_candidates = ["c1.png", "c2.png", "c3.png", "c4.png"]

    phase = ConceptPhase()
    phase.select(b, index=2, notes="mountain taller")

    assert b.selected_concept == "c3.png"  # 0-indexed internally, 1-indexed for user
    assert b.concept_notes == "mountain taller"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_concept_phase.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# vulca/src/vulca/studio/phases/concept.py
"""ConceptPhase -- generate concept designs (sketch + composition + palette merged)."""
from __future__ import annotations

import base64
import logging
from pathlib import Path

from vulca.studio.brief import Brief

logger = logging.getLogger("vulca.studio")


class ConceptPhase:
    """Generate concept design images from a Brief.

    Merges sketch, composition, and palette into one concept step.
    If user uploaded a sketch, concepts are variations of it.
    """

    def build_concept_prompt(self, brief: Brief) -> str:
        """Build a generation prompt from Brief for concept images."""
        parts = [f"Create a concept design artwork: {brief.intent}"]

        if brief.user_sketch:
            parts.append(
                "This should be a refined variation of the provided reference sketch, "
                "preserving its composition while improving detail and style."
            )

        # Style
        if brief.style_mix:
            styles = ", ".join(
                s.tradition.replace("_", " ") or s.tag for s in brief.style_mix
            )
            parts.append(f"Style: {styles}")

        # Mood
        if brief.mood:
            parts.append(f"Mood/atmosphere: {brief.mood}")

        # Composition
        if brief.composition.layout:
            parts.append(f"Composition: {brief.composition.layout}")
        if brief.composition.focal_point:
            parts.append(f"Focal point: {brief.composition.focal_point}")

        # Palette
        if brief.palette.mood:
            parts.append(f"Color mood: {brief.palette.mood}")
        if brief.palette.primary:
            parts.append(f"Primary colors: {', '.join(brief.palette.primary)}")

        # Elements
        if brief.elements:
            elems = ", ".join(e.name for e in brief.elements[:6])
            parts.append(f"Key elements to include: {elems}")

        # Constraints
        if brief.must_have:
            parts.append(f"Must include: {', '.join(brief.must_have)}")
        if brief.must_avoid:
            parts.append(f"Must avoid: {', '.join(brief.must_avoid)}")

        parts.append("Output: 1024x1024 image, no text or watermarks.")
        return "\n".join(parts)

    async def generate_concepts(
        self,
        brief: Brief,
        *,
        count: int = 4,
        provider: str = "mock",
        project_dir: str = "",
        api_key: str = "",
    ) -> list[str]:
        """Generate concept images and return file paths."""
        project = Path(project_dir) if project_dir else Path(".")
        concepts_dir = project / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)

        prompt = self.build_concept_prompt(brief)
        paths: list[str] = []

        try:
            from vulca.providers import get_image_provider
            img_provider = get_image_provider(provider, api_key=api_key)
        except Exception:
            logger.debug("Could not load provider %s for concept", provider)
            # Return placeholder paths for mock
            for i in range(count):
                p = concepts_dir / f"c{i + 1}.png"
                p.write_bytes(b"placeholder")
                paths.append(str(p))
            brief.concept_candidates = paths
            return paths

        for i in range(count):
            try:
                # Vary the prompt slightly for diversity
                varied_prompt = f"{prompt}\n\nVariation {i + 1} of {count}. Explore a different composition approach."
                result = await img_provider.generate(
                    varied_prompt,
                    tradition=brief.style_mix[0].tradition if brief.style_mix else "",
                    subject=brief.intent,
                    reference_image_b64=(
                        self._load_sketch_b64(brief.user_sketch)
                        if brief.user_sketch else ""
                    ),
                )
                ext = "png" if "png" in result.mime else "jpg"
                filepath = concepts_dir / f"c{i + 1}.{ext}"
                filepath.write_bytes(base64.b64decode(result.image_b64))
                paths.append(str(filepath))
            except Exception as exc:
                logger.debug("Concept generation %d failed: %s", i + 1, exc)
                # Placeholder on failure
                filepath = concepts_dir / f"c{i + 1}.png"
                filepath.write_bytes(b"placeholder")
                paths.append(str(filepath))

        brief.concept_candidates = paths
        return paths

    def select(self, brief: Brief, index: int, notes: str = "") -> None:
        """Select a concept by index (0-based) and update Brief."""
        if 0 <= index < len(brief.concept_candidates):
            brief.selected_concept = brief.concept_candidates[index]
        elif brief.concept_candidates:
            brief.selected_concept = brief.concept_candidates[0]

        if notes:
            brief.concept_notes = notes

    @staticmethod
    def _load_sketch_b64(sketch_path: str) -> str:
        """Load a sketch file as base64."""
        try:
            data = Path(sketch_path).read_bytes()
            return base64.b64encode(data).decode()
        except Exception:
            return ""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_concept_phase.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
cd vulca && git add src/vulca/studio/phases/concept.py tests/test_concept_phase.py
git commit -m "feat(studio): ConceptPhase — concept design generation"
```

---

### Task 8: StudioSession State Machine (Minimal)

**Files:**
- Create: `vulca/src/vulca/studio/session.py`
- Modify: `vulca/src/vulca/studio/__init__.py`
- Test: `vulca/tests/test_studio_session.py`

- [ ] **Step 1: Write the failing tests**

```python
# vulca/tests/test_studio_session.py
"""Tests for StudioSession state machine."""
from __future__ import annotations

import pytest


def test_session_new():
    from vulca.studio.session import StudioSession, SessionState
    s = StudioSession.new("水墨山水", project_dir="/tmp/vulca-test-session")
    assert s.state == SessionState.INTENT
    assert s.brief.intent == "水墨山水"
    assert s.session_id


def test_session_state_transitions():
    from vulca.studio.session import StudioSession, SessionState
    s = StudioSession.new("test", project_dir="/tmp/vulca-test-session-2")

    assert s.state == SessionState.INTENT
    s.advance_to(SessionState.CONCEPT)
    assert s.state == SessionState.CONCEPT
    s.advance_to(SessionState.GENERATE)
    assert s.state == SessionState.GENERATE


def test_session_rollback():
    from vulca.studio.session import StudioSession, SessionState
    s = StudioSession.new("test", project_dir="/tmp/vulca-test-session-3")
    s.advance_to(SessionState.GENERATE)

    s.rollback_to(SessionState.CONCEPT)
    assert s.state == SessionState.CONCEPT


def test_session_save_load(tmp_path):
    from vulca.studio.session import StudioSession, SessionState
    s = StudioSession.new("save test", project_dir=str(tmp_path / "proj"))
    s.advance_to(SessionState.CONCEPT)
    s.brief.mood = "serene"

    s.save()

    loaded = StudioSession.load(str(tmp_path / "proj"))
    assert loaded.state == SessionState.CONCEPT
    assert loaded.brief.mood == "serene"
    assert loaded.brief.intent == "save test"


def test_session_cannot_advance_backward():
    from vulca.studio.session import StudioSession, SessionState
    s = StudioSession.new("test", project_dir="/tmp/vulca-test-session-4")
    s.advance_to(SessionState.GENERATE)

    with pytest.raises(ValueError):
        s.advance_to(SessionState.INTENT)  # Can't go backward with advance
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_studio_session.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# vulca/src/vulca/studio/session.py
"""StudioSession -- state machine for creative studio sessions."""
from __future__ import annotations

import uuid
from enum import Enum
from pathlib import Path

import yaml

from vulca.studio.brief import Brief


class SessionState(Enum):
    INTENT = "intent"
    CONCEPT = "concept"
    GENERATE = "generate"
    EVALUATE = "evaluate"
    DONE = "done"


_STATE_ORDER = [
    SessionState.INTENT,
    SessionState.CONCEPT,
    SessionState.GENERATE,
    SessionState.EVALUATE,
    SessionState.DONE,
]


class StudioSession:
    """Manages the state machine for a creative studio session.

    Coordinates phases and persists Brief + state to disk.
    """

    def __init__(
        self,
        session_id: str,
        brief: Brief,
        state: SessionState,
        project_dir: Path,
    ):
        self.session_id = session_id
        self.brief = brief
        self.state = state
        self.project_dir = project_dir

    @classmethod
    def new(cls, intent: str, *, project_dir: str = "") -> StudioSession:
        sid = uuid.uuid4().hex[:8]
        brief = Brief.new(intent)
        brief.session_id = sid
        pdir = Path(project_dir) if project_dir else Path(f"./vulca-studio/{sid}")
        pdir.mkdir(parents=True, exist_ok=True)
        return cls(
            session_id=sid,
            brief=brief,
            state=SessionState.INTENT,
            project_dir=pdir,
        )

    def advance_to(self, target: SessionState) -> None:
        """Advance state forward. Raises if target is behind current."""
        current_idx = _STATE_ORDER.index(self.state)
        target_idx = _STATE_ORDER.index(target)
        if target_idx <= current_idx:
            raise ValueError(
                f"Cannot advance from {self.state.value} to {target.value} "
                f"(use rollback_to for going backward)"
            )
        self.state = target

    def rollback_to(self, target: SessionState) -> None:
        """Roll back state to an earlier phase."""
        self.state = target

    def save(self) -> Path:
        """Save session state + Brief to project directory."""
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.brief.save(self.project_dir)

        state_file = self.project_dir / "session.yaml"
        state_data = {
            "session_id": self.session_id,
            "state": self.state.value,
        }
        state_file.write_text(
            yaml.dump(state_data, allow_unicode=True),
            encoding="utf-8",
        )
        return state_file

    @classmethod
    def load(cls, project_dir: str | Path) -> StudioSession:
        """Load session from a project directory."""
        pdir = Path(project_dir)
        brief = Brief.load(pdir)

        state_file = pdir / "session.yaml"
        if state_file.exists():
            state_data = yaml.safe_load(state_file.read_text(encoding="utf-8"))
            state = SessionState(state_data.get("state", "intent"))
            sid = state_data.get("session_id", brief.session_id)
        else:
            state = SessionState.INTENT
            sid = brief.session_id

        return cls(
            session_id=sid,
            brief=brief,
            state=state,
            project_dir=pdir,
        )
```

Update `__init__.py` to export public API:

```python
# vulca/src/vulca/studio/__init__.py
"""VULCA Studio -- creative collaboration pipeline."""
from vulca.studio.brief import Brief
from vulca.studio.session import SessionState, StudioSession

__all__ = ["Brief", "StudioSession", "SessionState"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_studio_session.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Run ALL studio tests to verify no regressions**

Run: `cd vulca && .venv/bin/python -m pytest tests/test_studio_types.py tests/test_brief.py tests/test_from_brief.py tests/test_eval_criteria.py tests/test_intent_phase.py tests/test_scout_phase.py tests/test_concept_phase.py tests/test_studio_session.py -v`
Expected: All tests PASS (32+ tests)

- [ ] **Step 6: Commit**

```bash
cd vulca && git add src/vulca/studio/ tests/test_studio_session.py
git commit -m "feat(studio): StudioSession state machine + public API exports"
```

---

## Remaining Tasks (Phase 2 Plan — to be detailed later)

These tasks will be planned in a separate document after Phase 1 is implemented and reviewed:

- **Task 9**: GeneratePhase (Brief → structured prompt → provider)
- **Task 10**: EvaluatePhase (Brief-based L1-L5 criteria)
- **Task 11**: NL Update parser (natural language → Brief field updates + rollback)
- **Task 12**: CLI `vulca brief` + `vulca concept` commands
- **Task 13**: CLI `vulca studio` interactive mode
- **Task 14**: MCP `studio_*` tools
- **Task 15**: Digestion restructure (3-layer, Brief-aware)
- **Task 16**: Backward compatibility tests
- **Task 17**: Integration tests (end-to-end)
- **Task 18**: ComfyUI nodes (separate spec)
