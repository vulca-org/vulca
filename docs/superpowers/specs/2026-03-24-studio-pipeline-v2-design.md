# VULCA Studio Pipeline V2 — Design Spec

**Date**: 2026-03-24
**Status**: Approved
**Scope**: SDK/CLI/MCP/ComfyUI — Web App frozen

## Problem Statement

Four experiments (2026-03-23) proved the current pipeline has fundamental issues:

1. **YAML injection is marginal for good images** (+0.028) but critical for wrong-style detection (0.920→0.160)
2. **Multi-round auto-loop has +2.6% self-confirmation bias** — VLM gives higher scores to the same image when told "this is improved"
3. **Evolution flywheel is broken** — trained on mock data, weights collapsed (L1=96.6%)
4. **"Score then what?"** — evaluation output doesn't lead to actionable next steps

Creator pain points that the current pipeline doesn't address:

- Composition validation is slow (draw first, evaluate later)
- Sketch-to-finished-piece gap is huge (most time-consuming part)
- Creativity dies during execution (too many compromises)
- AI generation tools are uncontrollable (prompt lottery)

## Design Philosophy

**Front = Creativity** (randomness, exploration, multimodal dialogue, inspiration)
**Back = Precise Execution** (Brief locked, controlled generation and evaluation)

Like superpowers: settle everything before coding. Like VULCA Studio: settle everything before generating.

"Culture" is no longer predefined YAML traditions — it's the user's creative vision (Brief). YAML traditions become optional fallback templates.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Interface Layer                                        │
│  vulca studio (interactive) │ CLI steps │ MCP │ ComfyUI │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│  Studio Session Orchestration Layer (NEW)                │
│                                                         │
│  StudioSession                                          │
│    ├─ Phase 1: INTENT + SCOUT (parallel)                │
│    ├─ Phase 2: CONCEPT (sketch+composition+palette)     │
│    ├─ Phase 3: GENERATE (precise execution)             │
│    ├─ Phase 4: EVALUATE (Brief-based L1-L5)             │
│    └─ update(NL) → any phase rollback                   │
│                                                         │
│  Brief (living YAML document, cross-phase state)        │
│  Digestion (3-layer: realtime → session → cross-session)│
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│  Existing Pipeline Layer (UNCHANGED)                    │
│  execute(definition, input) → PipelineOutput            │
│  GenerateNode │ EvaluateNode │ DecideNode               │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│  Infrastructure                                         │
│  Providers │ Cultural │ Storage │ Digestion              │
└─────────────────────────────────────────────────────────┘
```

## Data Types

### Brief

The central data structure. A living YAML document that accumulates decisions across phases.

```python
@dataclass
class Brief:
    # Identity
    session_id: str
    version: int = 1
    created_at: str = ""
    updated_at: str = ""

    # Phase 1: Intent
    intent: str = ""                           # User's creative vision (text)
    mood: str = ""                             # Emotional target
    style_mix: list[StyleWeight] = field(default_factory=list)
    # e.g. [{"tradition": "chinese_xieyi", "weight": 0.6}, {"tag": "cyberpunk", "weight": 0.4}]

    # Phase 1: Scout (parallel with intent)
    references: list[Reference] = field(default_factory=list)
    # source: upload | search | generate
    # Each has: path, source, query/prompt, note

    # Phase 1: User sketch (optional)
    user_sketch: str = ""                      # Path to uploaded sketch

    # Phase 2: Concept (merged sketch+composition+palette)
    concept_candidates: list[str] = field(default_factory=list)  # Paths to 4 concept images
    selected_concept: str = ""                 # Path to chosen concept
    concept_notes: str = ""                    # User's NL refinement

    composition: Composition = field(default_factory=Composition)
    # layout, focal_point, aspect_ratio

    palette: Palette = field(default_factory=Palette)
    # primary[], accent[], mood

    elements: list[Element] = field(default_factory=list)
    # name, category (technique|effect|texture|symbol|overlay)

    # Constraints (= custom evaluation criteria)
    must_have: list[str] = field(default_factory=list)
    must_avoid: list[str] = field(default_factory=list)

    # Auto-generated L1-L5 criteria (from Brief content)
    eval_criteria: dict[str, str] = field(default_factory=dict)
    # L1: "Mountain-water composition with 20%+ negative space"
    # L2: "Ink brush texture + neon glow technical quality"
    # etc.

    # Phase 3-4: Generation history
    generations: list[GenerationRound] = field(default_factory=list)
    # round, image_path, scores, feedback

    # Update log
    updates: list[BriefUpdate] = field(default_factory=list)
    # timestamp, instruction (NL), fields_changed
```

### StudioSession

```python
class SessionState(Enum):
    INTENT = "intent"
    CONCEPT = "concept"
    GENERATE = "generate"
    EVALUATE = "evaluate"
    DONE = "done"

class StudioSession:
    session_id: str
    brief: Brief
    state: SessionState
    project_dir: Path          # All outputs saved here

    # Phase methods
    async def intent(self, user_input: str, sketch: str = "") -> Brief
    async def scout(self, queries: list[str] = []) -> list[Reference]
    async def concept(self, count: int = 4) -> list[Path]
    async def select_concept(self, index: int, notes: str = "") -> Brief  # C1 fix
    async def generate(self, provider: str = "gemini") -> Path
    async def evaluate(self) -> EvalResult
    async def update(self, instruction: str) -> Brief  # NL update, any phase
    async def accept(self) -> dict  # Finalize session, trigger digestion

    # Lifecycle
    def save(self) -> Path             # Serialize Brief + state to YAML
    @classmethod
    def load(cls, path: Path) -> "StudioSession"  # Handles partial states (S4)
    async def on_complete(self)        # Trigger digestion
```

### Supporting Types (I1 fix)

```python
@dataclass
class StyleWeight:
    tradition: str = ""      # Predefined tradition name (e.g., "chinese_xieyi")
    tag: str = ""            # Free-form style tag (e.g., "cyberpunk")
    weight: float = 0.5      # 0.0-1.0, weights in style_mix should sum to 1.0

@dataclass
class Reference:
    path: str                # Local file path
    source: str              # "upload" | "search" | "generate"
    query: str = ""          # Search query (if source=search)
    prompt: str = ""         # Generation prompt (if source=generate)
    url: str = ""            # Original URL (if source=search)
    note: str = ""           # User annotation

@dataclass
class Composition:
    layout: str = ""         # e.g., "upper 2/3 mountains, lower 1/3 water reflection"
    focal_point: str = ""    # e.g., "pavilion on cliff"
    aspect_ratio: str = "1:1"  # "1:1" | "4:3" | "16:9" | "3:4" | "9:16"
    negative_space: str = "" # e.g., "20%+ blank space on right"

@dataclass
class Palette:
    primary: list[str] = field(default_factory=list)   # Hex colors ["#1a1a2e"]
    accent: list[str] = field(default_factory=list)     # Highlight colors ["#00f5d4"]
    mood: str = ""           # e.g., "cold dark base + bright accents"

@dataclass
class Element:
    name: str                # e.g., "hemp-fiber texture stroke"
    category: str = ""       # "technique" | "effect" | "texture" | "symbol" | "overlay"
    note: str = ""           # Optional description

@dataclass
class GenerationRound:
    round_num: int
    image_path: str
    scores: dict[str, float] = field(default_factory=dict)  # L1-L5
    suggestions: dict[str, str] = field(default_factory=dict)
    feedback: str = ""       # User's NL feedback for this round

@dataclass
class BriefUpdate:
    timestamp: str
    instruction: str         # Original NL instruction
    fields_changed: list[str] = field(default_factory=list)
    rollback_to: str = ""    # Phase to rollback to
```

### Eval Criteria Generation (C2 fix)

When Phase 2 completes (concept selected), the system auto-generates `Brief.eval_criteria`:

```python
async def generate_eval_criteria(brief: Brief) -> dict[str, str]:
    """Convert Brief content into per-dimension L1-L5 evaluation criteria.

    Uses the same VLM model as scoring (VULCA_VLM_MODEL env var,
    default gemini/gemini-2.5-flash via litellm).

    Fallback: If LLM call fails, derive criteria from Brief.style_mix
    traditions' YAML definitions (get_tradition() for each tradition in mix).
    """
    prompt = f"""Based on this creative brief, generate specific evaluation criteria
for each of the 5 dimensions (L1-L5). Each criterion should be concrete and
measurable against the brief's intent.

Brief:
  Intent: {brief.intent}
  Mood: {brief.mood}
  Style mix: {brief.style_mix}
  Composition: {brief.composition}
  Palette: {brief.palette}
  Elements: {brief.elements}
  Must have: {brief.must_have}
  Must avoid: {brief.must_avoid}

Respond with JSON:
{{
  "L1": "<Visual Perception criterion specific to this brief>",
  "L2": "<Technical Execution criterion>",
  "L3": "<Cultural/Style Context criterion>",
  "L4": "<Interpretation/Constraint criterion>",
  "L5": "<Aesthetic/Emotional criterion>"
}}"""

    # Call via litellm (same model as VLM scoring)
    # On failure: fallback to YAML tradition criteria for each style_mix tradition
    # On fallback: merge criteria from multiple traditions weighted by style_mix.weight
```

### NL Update Schema (I2 fix)

```python
@dataclass
class NLUpdateResult:
    """Structured output from NL instruction parsing."""
    field_updates: dict[str, Any]    # Brief field path → new value
    rollback_to: SessionState        # Determined by rules below
    confidence: float                # 0-1, if < 0.5 ask user to clarify
    explanation: str                 # Why this interpretation

# Rollback determination rules (deterministic, not LLM-decided):
# - If any of {intent, mood, style_mix} changed → rollback to INTENT
# - If any of {composition, palette, elements, must_have, must_avoid} changed → rollback to CONCEPT
# - If only eval_criteria changed → rollback to EVALUATE
# - If only generation params changed (provider, etc.) → rollback to GENERATE
# - LLM only parses WHICH fields change; rollback phase is rule-based

# Validation: parsed field names must exist on Brief dataclass.
# Unknown fields → ask user for clarification, do not apply.
```

## Phase Details

### Phase 1: INTENT + SCOUT (parallel)

**IntentPhase**: Multimodal intent understanding.

Input:
- Text description (required)
- Uploaded sketch (optional) — analyzed via VLM
- Reference images (optional)

Process:
1. If sketch provided → VLM analyzes composition, style, elements
2. LLM generates clarifying questions (style, mood, technique, constraints)
3. In interactive mode: ask questions one at a time
4. In CLI mode: accept all params upfront
5. Form initial Brief with intent, mood, style_mix, constraints

**ScoutPhase** (runs in parallel with intent):

Process:
1. Extract search terms from intent (LLM call)
2. Generate AI reference images via existing provider (mood boards, style samples, palette studies)
3. Web search for reference images (optional, requires API key)
4. Download and save to project directory
5. Add to Brief.references

**Scout dependency strategy (C3 fix)**:
- **V1 (initial)**: Scout supports `source: "upload"` and `source: "generate"` only.
  Generation uses existing ImageProvider (Gemini/mock) with a reference-style prompt.
  No new dependencies. Web search is deferred.
- **V2 (later)**: Add web image search via `httpx` (already a dependency) + a search API.
  Candidate APIs: Google Custom Search (free tier 100/day), or SerpAPI, or Brave Search.
  Added as optional dependency: `pip install vulca[search]`.
- **Failure handling**: Scout is non-blocking. If generation fails, Brief gets empty references.
  IntentPhase continues regardless. User can always `vulca brief upload` manually.

**Key**: Scout starts immediately when user provides intent. By the time intent questions are answered, references are ready.

### Phase 2: CONCEPT (merged sketch+composition+palette)

Input: Brief (from Phase 1) + optional user sketch

Process:
1. Build concept generation prompt from Brief:
   - Style mix, mood, composition hints, palette, elements, constraints
   - If user sketch exists: use as reference image (img2img / ControlNet style)
2. Generate 4 concept images (fast/low-res) via provider
3. Present to user (file paths in CLI, inline in MCP)
4. User selects one + optional NL refinement ("mountain taller", "more negative space")
5. Update Brief: selected_concept, composition, palette, elements
6. Auto-generate eval_criteria from Brief content (LLM call)

**Sketch-to-concept path**: If user uploads a sketch, the 4 concepts are VARIATIONS of their sketch, not from-scratch generations. This addresses the "sketch→finished piece" pain point.

### Phase 3: GENERATE (precise execution)

Input: Brief with locked concept + composition + palette + elements

Process:
1. Build structured prompt from Brief (not a single string — structured sections):
   - Composition directive (layout, focal point, aspect ratio)
   - Palette directive (specific hex colors, mood)
   - Element list (techniques, effects, textures)
   - Constraints (must_have, must_avoid)
   - Reference image: selected_concept (as style/composition guide)
2. Call provider.generate() with full Brief context
3. If provider supports it (ComfyUI): use ControlNet with concept as control image
4. Save to project directory

**No auto-loop**. One generation per explicit user request. User sees result → decides next action.

### Phase 4: EVALUATE (Brief-based L1-L5)

Input: Generated image + Brief

Process:
1. Convert Brief.eval_criteria into VLM system prompt
   - Each L dimension gets custom criteria from the Brief
   - YAML tradition data used as supplementary context (not primary)
2. Call VLM score_image() with Brief-enhanced prompt
3. Return: L1-L5 scores + rationales + suggestions + deviation_types
4. Present to user with actionable next steps

**User decides** (not DecideNode):
- **Accept** → on_complete → digestion
- **Update Brief** → NL instruction → rollback to appropriate phase
- **Regenerate** → back to Phase 3 with updated Brief

### NL Update (any time)

```
User: "把山改成更陡峭的，像黄山那样"

LLM parses → {
  field: "composition.focal_point",
  change: "steep peaks like Huangshan",
  field: "elements",
  add: {"name": "steep cliff faces", "category": "technique"},
  rollback_to: "concept"  # Need new concept images
}

Brief updated → state rolls back to CONCEPT → regenerate concepts
```

The LLM determines which phase to rollback to based on what changed:
- Intent/mood changed → rollback to INTENT
- Composition/elements changed → rollback to CONCEPT
- Minor refinement → rollback to GENERATE
- Evaluation criteria changed → rollback to EVALUATE

## CLI Interface

### Interactive Mode

```bash
$ vulca studio "赛博朋克水墨山水"

VULCA Studio — session a1b2c3
Project: ./vulca-studio/a1b2c3/

[Intent] Analyzing your creative vision...
  Style detected: chinese_xieyi (60%) + cyberpunk (40%)

  Searching references...  ← (Scout running in parallel)
  → refs/search-001.jpg (cyberpunk ink wash)
  → refs/search-002.jpg (neon mountain)
  → refs/gen-palette.png (generated palette study)

  A few questions to refine:
  Mood? (1) epic-solitary  (2) mystical  (3) dystopian  (4) other
> 1

  Brush style? (1) traditional ink  (2) mixed digital  (3) abstract
> 1

[Concept] Generating 4 concepts...
  → concepts/c1.png
  → concepts/c2.png
  → concepts/c3.png
  → concepts/c4.png
  Select (1-4, or describe changes): 3 但山更高更陡

[Concept] Refining concept 3...
  → concepts/c3-refined.png
  Brief updated: composition, focal_point

[Generate] Creating final artwork via gemini...
  → output/final-r1.png

[Evaluate] L1-L5 (based on your Brief):
  L1 Visual    ████████████████░░░░ 82%  composition matches brief
  L2 Technical ██████████████░░░░░░ 71%  ink texture needs work
  L3 Cultural  ██████████████████░░ 90%  strong xieyi elements
  L4 Interpret ████████████████░░░░ 85%  cyber-ink fusion natural
  L5 Aesthetic ███████████████░░░░░ 78%  mood partially achieved

  Suggestions:
    L2: Ink strokes too uniform — vary pressure for 墨分五色 effect
    L5: Add more atmospheric depth in background for 壮阔 mood

  Next: (a)ccept  (u)pdate  (r)egenerate  (q)uit
> u 背景加更多雾气层次

[Generate] Regenerating with updated Brief...
  → output/final-r2.png
  ...
```

### Step Commands

```bash
# Each step is independent, Brief file is the state
vulca brief "赛博朋克水墨山水" --mood epic-solitary --save project/
vulca brief update project/ "加入黄山的陡峭山峰元素"
vulca brief search project/ "cyberpunk ink wash painting" --count 5
vulca brief upload project/ my-sketch.jpg --note "基础构图"

vulca concept project/ --count 4 --output project/concepts/
vulca concept select project/ 3 --notes "山更高"

vulca create project/ --provider gemini --output project/output/
vulca evaluate project/output/r1.png --brief project/

# Shorthand for full pipeline
vulca studio project/ --resume   # Resume from saved state
```

### SDK API

```python
import vulca
from vulca.studio import StudioSession

# Full session
session = StudioSession.new("赛博朋克水墨山水", project_dir="./my-project")

# Phase 1: Intent + Scout (parallel internally)
await session.intent("偏传统水墨，加少量赛博元素", sketch="my-sketch.jpg")

# Phase 2: Concept
concepts = await session.concept(count=4)
# → ["./my-project/concepts/c1.png", ..., "c4.png"]
await session.select_concept(2, notes="山更高更陡")

# Phase 3: Generate
result_path = await session.generate(provider="gemini")

# Phase 4: Evaluate
evaluation = await session.evaluate()
# → EvalResult with Brief-based L1-L5

# NL Update (any time)
await session.update("背景加更多雾气层次")
# → Brief updated, state rolled back to GENERATE

# Accept and trigger digestion
await session.accept()

# Save/Load
session.save()
restored = StudioSession.load("./my-project")
```

### MCP Tools (I3 fix: backward compatible)

Existing tools remain unchanged. New Studio tools are ADDED, not replaced:

```
# NEW Studio tools
studio_create_brief(intent, mood?, sketch_path?, references?) → brief_id
studio_update_brief(brief_id, instruction) → updated_brief
studio_search_references(brief_id, query, count?) → [reference_paths]
studio_generate_concepts(brief_id, count?) → [concept_paths]
studio_select_concept(brief_id, index, notes?) → updated_brief
studio_accept(brief_id) → session_summary

# EXISTING tools — enhanced with optional brief_id parameter
create_artwork(intent, tradition, ..., brief_id?) → result    # brief_id optional
evaluate_artwork(image_path, tradition, ..., brief_id?) → EvalResult  # brief_id optional

# When brief_id is provided, the existing tools use Brief-based criteria.
# When brief_id is omitted, they work exactly as before (backward compatible).
```

### ComfyUI Nodes (I4 fix: preliminary)

> **Note**: ComfyUI node specifications are preliminary. Detailed input/output
> socket types and ComfyUI-specific data flow will be defined during
> implementation step 11, following ComfyUI custom node conventions.

```
VULCABriefNode:       STRING (intent) → STRING (brief_yaml path)
VULCAConceptNode:     STRING (brief_yaml) + IMAGE? (sketch) → IMAGE[] (4 concepts)
VULCAGenerateNode:    STRING (brief_yaml) + IMAGE (concept) → IMAGE (final)
VULCAEvaluateNode:    IMAGE (artwork) + STRING (brief_yaml) → STRING (scores JSON)
VULCAUpdateNode:      STRING (brief_yaml) + STRING (instruction) → STRING (updated brief_yaml)
```

## File Structure

```
vulca/src/vulca/
├── studio/                    # NEW: Orchestration layer
│   ├── __init__.py            # Public API: StudioSession
│   ├── session.py             # StudioSession state machine
│   ├── brief.py               # Brief dataclass + YAML serialization
│   ├── types.py               # Reference, Composition, Palette, Element, etc.
│   ├── phases/
│   │   ├── __init__.py
│   │   ├── intent.py          # IntentPhase: multimodal intent parsing
│   │   ├── scout.py           # ScoutPhase: reference search/download/generate
│   │   ├── concept.py         # ConceptPhase: sketch+composition+palette
│   │   ├── generate.py        # GeneratePhase: Brief→structured prompt→provider
│   │   └── evaluate.py        # EvaluatePhase: Brief-based L1-L5
│   ├── nl_update.py           # NL instruction → Brief field updates
│   └── interactive.py         # Terminal interactive UI (vulca studio)
│
├── cultural/
│   ├── from_brief.py          # NEW: Brief → TraditionConfig conversion
│   └── ... (existing unchanged)
│
├── digestion/                 # NEW: Moved from backend, restructured
│   ├── __init__.py
│   ├── evolver.py             # ContextEvolver (restructured for Brief data)
│   ├── pattern_detector.py    # Cross-session pattern detection
│   ├── preference_learner.py  # User preference learning
│   └── brief_templates.py     # NEW: Auto-generate tradition templates from Briefs
│
├── pipeline/                  # UNCHANGED
├── providers/                 # UNCHANGED
├── cli.py                     # MODIFIED: add studio + brief commands
├── mcp_server.py              # MODIFIED: add brief-related MCP tools
└── ...
```

## Digestion System

### Layer 1: Realtime Feedback (during session)

No digestion needed. EvaluatePhase provides immediate L1-L5 scores + suggestions based on Brief. This is the existing VLM scoring, just with Brief-enhanced prompts.

### Layer 2: Session-Level Digestion (on_complete)

```python
async def on_complete(session: StudioSession):
    # 1. Save full session data
    store = SessionStore.get()
    store.save_session({
        "brief": session.brief.to_dict(),
        "generations": session.brief.generations,
        "final_scores": session.latest_scores,
        "user_satisfaction": session.user_feedback,
        "style_mix": session.brief.style_mix,
        "update_log": session.brief.updates,
    })

    # 2. Extract signals
    signals = {
        "concept_preference": which_concept_chosen_vs_rejected,
        "dimension_difficulty": which_L_dimensions_needed_most_iterations,
        "effective_elements": elements_in_highest_scored_generation,
        "style_mix_viability": final_score_for_this_style_combination,
    }

    # 3. Update evolved_context.json (throttled)
    evolver = ContextEvolver()
    await evolver.ingest_session(signals)
```

### Layer 3: Cross-Session Evolution (periodic)

```python
class ContextEvolver:
    async def evolve(self):
        sessions = await store.get_recent_sessions(limit=100)

        # 1. Pattern detection
        patterns = PatternDetector.detect(sessions)
        # e.g., "cyberpunk+xieyi sessions average 3.2 rounds, L2 is consistently lowest"

        # 2. Preference learning
        preferences = PreferenceLearner.learn(sessions)
        # e.g., "users prefer high-contrast compositions for cyberpunk mixes"

        # 3. Brief template generation
        if enough_sessions_for_style("cyberpunk_ink"):
            template = BriefTemplateGenerator.generate("cyberpunk_ink", sessions)
            # → new tradition YAML auto-created from user data

        # 4. Weight adjustment (based on REAL feedback, not mock)
        weights = self.adjust_weights(sessions)
        # Uses actual user accept/reject signals, not VLM self-evaluation

        # 5. Save
        self.save_evolved_context({
            "tradition_weights": weights,
            "patterns": patterns,
            "brief_templates": templates,
            "concept_preferences": preferences,
        })
```

## What Changes vs Current Pipeline

| Component | Current | V2 | Why |
|-----------|---------|-----|-----|
| Entry point | `vulca.create()` | `StudioSession` | Orchestration needed |
| Evaluation basis | YAML tradition | Brief + YAML fallback | User intent > predefined rules |
| Multi-round loop | Auto (DecideNode) | User-driven | Self-confirmation bias fix |
| DecideNode | Auto accept/rerun | Suggest only, user decides | Bias fix |
| Cultural injection | Always full YAML | Brief-first, YAML supplementary | Experiment C data |
| Evolution data | Mock feedback | Real Brief + scores + feedback | Flywheel fix |
| Sketch input | Not supported | First-class (Phase 2) | Creator pain point |
| Reference images | Not supported | Search + generate + upload | Inspiration support |
| NL updates | Not supported | Any-time Brief modification | Iterative refinement |

## What Does NOT Change

- `pipeline/engine.py` — execution engine stays as-is
- `pipeline/nodes/` — GenerateNode, EvaluateNode, DecideNode unchanged
- `providers/` — all providers unchanged
- `cultural/loader.py` — YAML loading unchanged
- `_vlm.py` — VLM scoring core unchanged (prompt enhanced by Brief)
- `types.py` — EvalResult, CreateResult unchanged
- Existing `vulca.evaluate()` and `vulca.create()` APIs — backward compatible

## Testing Strategy (TDD)

Tests written BEFORE implementation, in this order:

### Phase 0: Brief System (foundation)
```
test_brief.py
  - test_brief_create_minimal
  - test_brief_create_full
  - test_brief_to_yaml_roundtrip
  - test_brief_load_from_yaml
  - test_brief_update_field
  - test_brief_eval_criteria_generation

test_brief_tradition.py
  - test_brief_to_tradition_config
  - test_brief_with_style_mix
  - test_brief_fallback_to_yaml_tradition
```

### Phase 1: Intent + Scout
```
test_intent_phase.py
  - test_intent_parse_text_only
  - test_intent_parse_with_sketch (mock VLM)
  - test_intent_generate_questions
  - test_intent_update_brief

test_scout_phase.py
  - test_scout_extract_search_terms
  - test_scout_generate_reference (mock provider)
  - test_scout_parallel_with_intent
```

### Phase 2: Concept
```
test_concept_phase.py
  - test_concept_generate_from_brief (mock)
  - test_concept_generate_from_sketch (mock, sketch as reference)
  - test_concept_select_and_update_brief
  - test_concept_nl_refinement
```

### Phase 3-4: Generate + Evaluate (enhanced)
```
test_generate_phase.py
  - test_generate_from_brief_structured_prompt
  - test_generate_uses_concept_as_reference
  - test_generate_respects_constraints

test_evaluate_phase.py
  - test_evaluate_with_brief_criteria (mock VLM)
  - test_evaluate_brief_vs_yaml_comparison
  - test_evaluate_suggestions_actionable
```

### Phase 5: Session + NL Update
```
test_studio_session.py
  - test_session_state_transitions
  - test_session_save_load_roundtrip
  - test_session_nl_update_rollback
  - test_session_on_complete_triggers_digestion

test_nl_update.py
  - test_nl_update_composition
  - test_nl_update_elements
  - test_nl_update_determines_rollback_phase
```

### Phase 6: Digestion
```
test_digestion.py
  - test_session_level_signal_extraction
  - test_cross_session_pattern_detection
  - test_brief_template_generation
  - test_weight_adjustment_from_real_data
```

### Phase 7: CLI + MCP + ComfyUI
```
test_cli_studio.py
  - test_cli_brief_create
  - test_cli_brief_update
  - test_cli_concept
  - test_cli_studio_interactive (mock stdin)

test_mcp_studio.py
  - test_mcp_create_brief
  - test_mcp_update_brief
  - test_mcp_generate_concepts
  - test_mcp_evaluate_with_brief
```

### Phase 8: Integration + Backward Compatibility (I5 fix)
```
test_studio_integration.py
  - test_full_session_intent_to_accept (end-to-end with mocks)
  - test_session_save_load_resume (file I/O roundtrip)
  - test_session_nl_update_mid_flow (update during concept phase)
  - test_session_with_user_sketch_input

test_backward_compat.py
  - test_existing_evaluate_unchanged (same API signature, same result)
  - test_existing_create_unchanged (same API signature, same result)
  - test_existing_mcp_create_artwork_no_brief (brief_id omitted)
  - test_existing_mcp_evaluate_artwork_no_brief
  - test_existing_cli_evaluate_no_brief
```

## Implementation Order

1. Brief data types + YAML serialization (foundation)
2. Brief → TraditionConfig conversion (bridges old and new)
3. IntentPhase + ScoutPhase (parallel capable)
4. ConceptPhase (with sketch input support)
5. GeneratePhase (Brief → structured prompt)
6. EvaluatePhase (Brief-based criteria)
7. StudioSession state machine + NL update
8. CLI commands (brief, concept, studio)
9. MCP tools (brief-related)
10. Digestion restructure (3-layer)
11. ComfyUI nodes
12. Interactive terminal UI (vulca studio)

## Success Criteria

1. `vulca studio "水墨山水"` produces a complete creative session with Brief, concepts, generation, and Brief-based evaluation
2. User can upload a sketch and get variations that preserve their composition
3. NL updates modify the Brief and rollback to the correct phase
4. Session data feeds into digestion system with real Brief + score data
5. All existing `vulca evaluate` / `vulca create` commands continue to work unchanged
6. ComfyUI nodes can be composed into custom workflows
7. 100% of new code is test-covered (TDD)
