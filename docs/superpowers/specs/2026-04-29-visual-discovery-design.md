# `/visual-discovery` Product + Skill Design Spec

**Date:** 2026-04-29
**Status:** Draft for product review. Not implementation-locked.
**Parent pipeline:** `/visual-discovery` -> `/visual-brainstorm` -> `/visual-spec` -> `/visual-plan`
**Follow-up:** after review approval, create implementation plan at `docs/superpowers/plans/2026-04-29-visual-discovery.md` via `superpowers:writing-plans`.

This spec defines the missing upstream layer for Vulca's visual workflow. Existing Vulca skills start once a project is ready to become a proposal. `/visual-discovery` handles the earlier and harder moment: the user has a fuzzy intent, partial taste, unclear cultural direction, or no confidence that a one-shot generation prompt captures what they mean.

The goal is not to build another image generator. The goal is to make Vulca the creative discovery and visual control layer that helps an agent clarify intent, explore directions, compile culturally meaningful visual rules, run low-cost sketches, and hand a selected direction into the existing proposal/spec/plan chain.

---

## 1. Product Thesis

### 1.1 Problem

Most generative visual tools assume the user already knows what they want. The dominant loop is:

```text
user prompt -> model generates -> user rerolls or edits prompt
```

That loop is weak when the user's intent is vague:

- "I want something high-end and Eastern, but not clichéd."
- "Make a brand visual for tea, but I don't know if it should be traditional or modern."
- "I want a poster that feels spiritual, but not religious."
- "I need several directions before I commit."

In these cases, the model often does premature execution. It picks a single visual interpretation, hides the assumptions, and forces the user to discover taste through expensive rerolls.

### 1.2 Opportunity

Vulca already has cultural evaluation, tradition guides, provider routing, layer decomposition, local/cloud generation, and an agent-native MCP surface. The missing value is an upstream discovery loop:

```text
fuzzy intent
-> taste and culture profile
-> direction cards
-> low-cost sketches
-> selected visual strategy
-> proposal.md
```

This is a stronger product position than "prompt enhancer" because it produces auditable artifacts that downstream agents and tools can use.

### 1.3 Positioning

`/visual-discovery` should be positioned as:

```text
Creative direction discovery for agent-native visual workflows.
```

It discovers and structures what the user wants before any final image generation run. It compiles cultural and aesthetic terms into visual operations, not just prompt words.

---

## 2. Scope

### 2.1 In Scope

First version supports static 2D visual projects that can eventually flow into `/visual-brainstorm`:

- poster
- editorial illustration
- brand visual
- packaging / label visual
- product campaign visual
- social media visual
- cover / hero visual
- photography brief
- UI hero illustration, only when the deliverable is a single visual asset and not an app/page layout

### 2.2 Out of Scope

First version hard-rejects or defers:

- product UI layout, app screens, web flows, component design
- full video generation workflows
- 3D / CAD / industrial design
- full brand strategy systems beyond visual direction
- final production generation without downstream `/visual-plan`
- direct pixel editing, inpainting, layer decomposition, or evaluation during discovery unless explicitly running an experiment mode

### 2.3 Edge-Accept Rule

If the user's request mixes visual asset and product layout, apply the Single Visual Artifact Test:

```text
Can the outcome be judged as one static visual image?
```

If yes, accept and record a scope rationale in `discovery.md`. If no, redirect to UI/product design tooling.

---

## 3. Existing Vulca Assets Reused

`/visual-discovery` should reuse current Vulca capabilities rather than create a separate product stack.

| Existing asset | Reuse in discovery |
|---|---|
| `list_traditions`, `search_traditions`, `get_tradition_guide` | Build culture candidates and term expansions |
| 13 bundled tradition YAML files | Source terminology, taboos, L1-L5 weights, tradition layers, and style keywords |
| `brief_parse` | Seed intent parsing and domain inference |
| `compose_prompt_from_design` | Existing structured prompt composition baseline; discovery should extend this pattern, not replace it |
| `generate_image(provider="mock")` | Optional mock sketch record generation; no final generation |
| `generate_concepts(provider="mock")` | Optional multi-variant mock scaffolding; must pass `provider="mock"` explicitly |
| `evaluate_artwork(mode="rubric_only")` | Explain expected evaluation criteria without image loading or VLM budget |
| `visual-brainstorm` | Downstream handoff after one direction is selected |
| L1-L5 framework | Attach evaluation focus to direction cards; score only generated images or rubric outputs |
| Provider layer (`mock`, `gemini`, `nb2`, `openai`, `comfyui`) | Compile direction cards into provider-specific prompt strategies |
| Tool Protocol analyzers (`tool_whitespace_analyze`, `tool_brushstroke_analyze`, `tool_composition_analyze`, `tool_color_gamut_check`, `tool_color_correct`) | Future benchmark/evaluation support for generated sketches; not used before images exist |
| `layers_*` tools | Not used directly in discovery; referenced as future editability constraints |

Important boundary: discovery may describe layer/edit strategy, but it must not execute layer tools. Pixel work belongs to `/visual-plan`.

### 3.1 Current-State Facts

The implementation plan must preserve these facts from the current repo:

- Runtime MCP surface currently registers 28 tools when Tool Protocol tools are included. Some docs still say 20 or 21 tools; those counts are stale and should be cleaned separately.
- Built-in image providers are `mock`, `gemini`, `nb2`, `openai`, and `comfyui`. `nb2` is an alias for the Gemini provider in the current registry.
- OpenAI GPT Image 2 is supported through `provider="openai", model="gpt-image-2"`. The OpenAI provider default is still `gpt-image-1`. Decision note, 2026-04-30: public docs can lag model/API rollout; keep `gpt-image-2` when current API/provider evidence and Vulca dogfood runs show it is available.
- Gemini's current default model is `gemini-3.1-flash-image-preview`. Public product language may say Gemini / Nano Banana, but implementation should use the provider IDs above.
- `evaluate_artwork(mode="rubric_only")` returns a rubric payload for a built-in tradition. It does not score a direction card.
- Existing tradition YAML entries contain terminology, taboos, weights, layers, and style keywords. They do not yet contain first-class `visual_ops` fields. Discovery v1 must add or derive that expansion layer.
- `compose_prompt_from_design` already composes prompt artifacts from resolved `design.md`; Discovery should reuse its artifact-first philosophy and extend it for direction-card compilation.

---

## 4. User Experience

### 4.1 Default Conversation Loop

```text
1. User gives fuzzy visual intent.
2. Agent infers uncertainty, domain, audience, likely traditions, and risks.
3. Agent asks at most 1-3 targeted questions only if necessary.
4. Agent creates 3-5 direction cards.
5. User selects, rejects, or blends directions.
6. Agent updates taste profile.
7. Agent optionally creates low-cost sketch prompts or rough thumbnails.
8. User chooses a direction.
9. Agent writes discovery.md and proposal-ready handoff.
```

The agent should not interrogate the user with a long questionnaire. It should use inference, show alternatives, and let the user's reaction teach the system.

### 4.2 Direction Card Interaction

Direction cards are the core UI primitive, even if rendered as markdown in v1.

Each card must answer:

- What is the direction?
- Why might it fit this user/project?
- What cultural or aesthetic ideas are involved?
- What concrete visual operations does it imply?
- What should the model avoid?
- Which provider is likely to handle it best?
- What risk or tradeoff does it carry?

Example:

```json
{
  "id": "song-negative-space-premium-tea",
  "label": "Song negative space + premium tea restraint",
  "summary": "A quiet, spare direction using large negative space, paper texture, small product presence, and low-saturation ink atmosphere.",
  "culture_terms": ["Song painting", "liubai", "qi yun"],
  "visual_ops": {
    "composition": "large negative space, small off-center subject, asymmetrical balance",
    "color": "warm off-white, ink gray, muted green, restrained gold accent",
    "texture": "subtle rice paper grain, dry brush edges",
    "symbol_strategy": "abstract atmosphere over literal dragons, lanterns, or red-gold festival motifs",
    "avoid": ["dragon motifs", "red-gold cliché palette", "busy ornament", "generic East Asian fantasy"]
  },
  "best_for": ["premium packaging", "editorial poster", "quiet luxury campaign"],
  "provider_hint": {
    "sketch": {"provider": "gemini", "model": "gemini-3.1-flash-image-preview"},
    "final": {"provider": "openai", "model": "gpt-image-2"},
    "local": {"provider": "comfyui"}
  },
  "risk": "May be too quiet for high-conversion social ads unless typography and product hierarchy are strong."
}
```

### 4.3 Low-Cost Sketch Loop

Sketching is optional. The first version supports two sketch levels:

| Level | Output | Provider | Purpose |
|---|---|---|---|
| Text sketch | prompt + composition notes only | no image provider | fastest clarification |
| Mock thumbnail record | mock image variants | `mock` only | validate artifact shape without API cost |
| Real thumbnail sketch | low-cost image variants | `gemini`, `openai`, or `comfyui` | explicit opt-in only; visual comparison, not final production |

The skill must label sketches as exploratory. It must not present them as final image quality.

### 4.4 User Selection Semantics

The user can respond naturally:

- "Pick B."
- "B but less traditional."
- "Mix A's color with C's composition."
- "No red, more premium."
- "I like the quiet one but make it more commercial."

The agent updates `taste_profile.json` and `direction_cards.json` after selection or blending.

---

## 5. Data Artifacts

All artifacts live under:

```text
docs/visual-specs/<slug>/discovery/
```

### 5.1 `discovery.md`

Human-readable summary and decision record.

Required sections:

```markdown
# Visual Discovery: <title>

## Status
draft | ready_for_brainstorm | abandoned

## Original Intent
<user's initial wording>

## Scope Decision
<accepted / redirected / edge-accepted with rationale>

## Uncertainty
<what is unclear or underdetermined>

## Taste Profile Summary
<plain-language summary>

## Direction Cards
<3-5 concise card summaries>

## User Preference Signals
<selected, rejected, blended, constraints>

## Recommended Direction
<one selected direction or none>

## Handoff
<how to invoke /visual-brainstorm or why not ready>

## Notes
<audit trail>
```

### 5.2 `taste_profile.json`

Machine-readable profile of the user's project-level visual tendencies.

Required schema:

```json
{
  "schema_version": "0.1",
  "slug": "2026-04-29-example",
  "source": {
    "initial_intent": "",
    "reference_paths": [],
    "conversation_signals": []
  },
  "domain": {
    "primary": "brand_visual",
    "candidates": ["poster", "packaging"],
    "confidence": "med"
  },
  "culture": {
    "primary_tradition": null,
    "candidate_traditions": [],
    "terms": [],
    "avoid_cliches": [],
    "risk_flags": []
  },
  "aesthetic": {
    "mood": [],
    "composition": [],
    "color": [],
    "material": [],
    "typography": [],
    "symbol_strategy": ""
  },
  "commercial_context": {
    "audience": "",
    "channel": "",
    "conversion_pressure": "unknown",
    "brand_maturity": "unknown"
  },
  "selection_history": [
    {
      "turn": 1,
      "selected": [],
      "rejected": [],
      "blended": [],
      "notes": ""
    }
  ],
  "confidence": {
    "overall": "low",
    "needs_more_questions": true
  }
}
```

### 5.3 `direction_cards.json`

Machine-readable direction set.

Required schema:

```json
{
  "schema_version": "0.1",
  "slug": "2026-04-29-example",
  "cards": [
    {
      "id": "card-id",
      "label": "Human label",
      "summary": "",
      "culture_terms": [],
      "visual_ops": {
        "composition": "",
        "color": "",
        "texture": "",
        "lighting": "",
        "camera": "",
        "typography": "",
        "symbol_strategy": "",
        "avoid": []
      },
      "provider_hint": {
        "sketch": {"provider": "gemini", "model": "gemini-3.1-flash-image-preview"},
        "final": {"provider": "openai", "model": "gpt-image-2"},
        "local": {"provider": "comfyui"}
      },
      "evaluation_focus": {
        "L1": "",
        "L2": "",
        "L3": "",
        "L4": "",
        "L5": ""
      },
      "risk": "",
      "status": "candidate"
    }
  ]
}
```

### 5.4 `sketch_prompts.json`

Optional. Created only when sketches are requested.

Required schema:

```json
{
  "schema_version": "0.1",
  "slug": "2026-04-29-example",
  "prompts": [
    {
      "card_id": "card-id",
      "provider": "gemini",
      "model": "gemini-3.1-flash-image-preview",
      "prompt": "",
      "negative_prompt": "",
      "size": "1024x1024",
      "purpose": "thumbnail exploration"
    }
  ]
}
```

---

## 6. Cultural and Aesthetic Guidance Model

### 6.1 Key Principle

Cultural and aesthetic terms are intermediate semantic controls, not final prompts.

```text
culture term
-> Vulca tradition ontology
-> visual operations
-> provider-specific prompt
-> generated sketch or final image
-> L1-L5 evaluation
```

The product must avoid claiming that rare cultural terms directly and reliably steer every model. The honest claim is:

```text
Vulca expands cultural concepts into concrete visual operations, constraints, and evaluation criteria.
```

In the current repo, the tradition registry provides the ontology input: terminology, taboos, weights, tradition layers, and style keywords. The missing v1 product layer is the compiler from those fields into explicit visual operations such as composition, palette, texture, symbol strategy, and avoid constraints.

### 6.2 Term Expansion

Each cultural or aesthetic term should expand into:

- definition
- visual implications
- composition implications
- material or texture implications
- color implications
- common clichés to avoid
- evaluation signals
- provider notes

Example:

```yaml
term: liubai
display: "留白"
definition: "Strategic empty space that creates rhythm, breath, and implied form."
visual_implications:
  - "large low-detail regions"
  - "small off-center focal subject"
  - "clear figure-ground relationship"
avoid:
  - "empty background with no intentional balance"
  - "generic minimalism unrelated to subject"
evaluation_signals:
  L1: "negative space supports composition rather than appearing unfinished"
  L5: "emptiness contributes to mood, resonance, and implied meaning"
```

### 6.3 Culture Risk Handling

Discovery must surface risk when the requested direction may collapse into stereotype or misuse.

Risk flags:

- `cliche_symbolism`
- `religious_symbol_misuse`
- `mixed_culture_without_rationale`
- `brand_mismatch`
- `over_exoticized`
- `generic_ai_aesthetic`
- `text_legibility_risk`
- `low_commercial_clarity`

Risk flags do not block the project. They become constraints and evaluation criteria.

---

## 7. Prompt and Provider Strategy

### 7.1 Provider Roles

| Provider/platform | Discovery role |
|---|---|
| Claude | Dialogue, inference, card generation, MCP orchestration |
| OpenAI / GPT Image 2 | High-fidelity final candidate for typography, layout-heavy, commercial images; use `provider="openai", model="gpt-image-2"` when GPT Image 2 is required |
| Gemini / Nano Banana | Fast sketching, multi-reference exploration, style transfer; current provider IDs are `gemini` and `nb2` |
| ComfyUI | Local/private generation and reproducible provider path |
| Veo / Seedance | Future video branch; not in v1 execution |
| Adobe / Figma / Canva | Future handoff targets; not v1 dependencies |

### 7.2 Provider-Specific Compilation

The compiler must support different prompt outputs for the same card:

- OpenAI: concise, high-fidelity, strong layout/text constraints, explicit preservation instructions.
- Gemini: more conversational, multi-reference friendly, good for exploration and remix.
- ComfyUI: shorter CLIP-safe text, compressed style tokens, no overlong cultural explanation.

This should extend the existing `compose_prompt_from_design` approach instead of creating an unrelated compiler. v1 can introduce a sibling function such as `compose_prompt_from_direction_card`, then later converge both into a shared prompt assembly module.

The same card may compile differently:

```text
Card: Song negative space premium tea
OpenAI: layout and typography emphasis
Gemini: reference/image remix emphasis
ComfyUI: compact style token + negative prompt
```

### 7.3 No Provider Lock-In

Discovery must not hard-code one winner. It should produce provider hints and let `/visual-spec` make technical decisions.

Provider hints should include both provider and model when model matters:

```json
{
  "sketch": {"provider": "gemini", "model": "gemini-3.1-flash-image-preview"},
  "final": {"provider": "openai", "model": "gpt-image-2"},
  "local": {"provider": "comfyui"}
}
```

---

## 8. Skill Behavior

### 8.1 Frontmatter

```yaml
---
name: visual-discovery
description: Discover visual direction from fuzzy intent before /visual-brainstorm: taste profile, culture analysis, direction cards, and sketch prompts.
---
```

### 8.2 Activation

Invoke when the user:

- asks for visual direction before knowing final style
- says they are unsure what they want
- asks for "抽卡", "方向探索", "审美分析", "文化倾向分析", "先聊再出方案"
- wants moodboard-like alternatives
- asks why a visual direction should fit a brand/culture/audience

Do not invoke for:

- direct image generation where the user explicitly wants no discovery
- image decomposition from a supplied image; use `/decompose`
- a ready proposal; use `/visual-spec`
- an approved design; use `/visual-plan`

### 8.3 Tool Whitelist

Allowed in v1 skill:

- Read existing project docs
- view user-provided reference images
- list/search/get tradition guides
- compose prompt artifacts from discovery cards using the existing `compose_prompt_from_design` pattern
- write discovery artifacts
- optional `generate_image(provider="mock")` only for non-final sketch records
- optional `generate_concepts(provider="mock")` only for non-final multi-card sketch records

Forbidden:

- real provider `generate_image` / `generate_concepts` unless the user explicitly opts into sketch generation
- `layers_*`
- `inpaint_artwork`
- `evaluate_artwork` with real VLM provider
- final production image generation

### 8.4 Turn Cap

Default discovery loop:

- Hard cap: 8 user-facing turns
- Soft extension: user says "deep discovery" or "继续深入" -> +4, max 12

At cap:

```text
Show current direction cards and ask: choose one, blend, or deep discovery.
```

---

## 9. Handoff to `/visual-brainstorm`

When one direction is selected, `/visual-discovery` writes or updates:

```text
docs/visual-specs/<slug>/discovery/discovery.md
docs/visual-specs/<slug>/discovery/taste_profile.json
docs/visual-specs/<slug>/discovery/direction_cards.json
```

Then it prints:

```text
Ready for /visual-brainstorm. Suggested topic:
"<compiled one-paragraph project brief>"
```

It must not auto-invoke `/visual-brainstorm`. The user must approve the transition.

The suggested topic includes:

- selected domain
- target audience
- selected direction
- cultural/tradition intent
- visual operations
- avoid constraints
- intended output format

---

## 10. Benchmark and Validation Plan

Discovery is a product hypothesis. It must be validated against direct prompting.

### 10.1 Guidance Benchmark

Create a benchmark with the following conditions:

| Condition | Description |
|---|---|
| A | baseline user prompt |
| B | baseline + raw cultural/aesthetic terms |
| C | baseline + visual operations only |
| D | raw terms + visual operations |
| E | raw terms + visual operations + reference images |
| F | `/visual-discovery` card compiled prompt |

Providers:

- OpenAI GPT Image 2 via `provider="openai", model="gpt-image-2"`
- Gemini / Nano Banana via `provider="gemini"` or `provider="nb2"`
- ComfyUI via `provider="comfyui"`

Domains:

- brand visual
- poster
- editorial illustration
- packaging
- social asset

Traditions / aesthetic clusters:

- chinese_xieyi
- japanese_traditional
- islamic_geometric
- western_academic
- brand_design
- contemporary_art

### 10.2 Metrics

Required metrics:

- L1-L5 score
- optional algorithmic signals from Tool Protocol analyzers when an image exists
- human blind preference
- prompt adherence
- cultural cliché risk
- brand/style consistency
- text rendering quality, when text is required
- editability/decomposition suitability
- reroll count
- cost
- latency

### 10.3 Decision Criteria

Discovery is validated if condition F beats A and B on:

- human preference
- L1-L5 weighted score
- fewer rerolls
- lower cliché risk
- clearer downstream proposal quality

If F does not beat D/E, the product should position discovery as UX and workflow improvement, not generation-quality improvement.

If raw terms B do not beat baseline A, the product must avoid claims that cultural terms alone control models.

---

## 11. Implementation Units

The implementation plan should split into independent units:

1. Current-state audit tripwires
   - runtime MCP tool count / expected tool set
   - provider registry shape
   - tradition registry shape
   - README / pyproject count cleanup, if product docs are updated in the same release

2. Schema models and validators
   - `TasteProfile`
   - `DirectionCard`
   - `SketchPrompt`

3. Term expansion library
   - derive cultural terms from existing tradition YAML
   - aesthetic terms
   - cliché/risk mappings
   - visual operation mappings

4. Profile inference
   - parse fuzzy intent
   - infer candidate domains/traditions
   - identify uncertainty and risk

5. Direction card generator
   - produce 3-5 cards
   - enforce visual_ops and avoid constraints
   - produce provider hints

6. Prompt compiler extension
   - reuse `compose_prompt_from_design` parser/composition conventions
   - add direction-card prompt composition
   - compile OpenAI prompt + model hints
   - compile Gemini prompt + model hints
   - compile ComfyUI prompt + negative prompt

7. Skill artifact
   - `.agents/skills/visual-discovery/SKILL.md`
   - routing updates in `.agents/skills/using-vulca-skills/SKILL.md`

8. Benchmark harness
   - conditions A-F
   - provider runner
   - optional Tool Protocol analyzer runner
   - metrics collection
   - markdown report

9. Documentation and demo
   - README workflow section
   - one end-to-end sample discovery project

---

## 12. Superpowers Workflow

### 12.1 Product Design

Use `superpowers:brainstorming` before implementation. This spec is the product design artifact. It remains draft until reviewed and approved.

### 12.2 Implementation Plan

After approval, use `superpowers:writing-plans` to create:

```text
docs/superpowers/plans/2026-04-29-visual-discovery.md
```

The plan must include exact file paths, tests, commands, and task-level commits.

### 12.3 Development

Use `superpowers:test-driven-development` for all behavior changes:

- current-state audit tripwires
- schema validation
- term expansion
- card generation
- compiler outputs
- handoff behavior
- benchmark result parsing

Use `superpowers:systematic-debugging` for provider failures, prompt drift, benchmark anomalies, and evaluation mismatch.

Use `superpowers:requesting-code-review` after major tasks and before merge.

Use `superpowers:verification-before-completion` before claiming any milestone is complete.

### 12.4 Subagents

When executing the implementation plan, use `superpowers:subagent-driven-development` if available. Recommended ownership split:

- Worker 1: current-state audit tripwires, schemas, and validators
- Worker 2: term expansion and risk mappings from tradition YAML
- Worker 3: prompt compiler extension based on `compose_prompt_from_design`
- Worker 4: skill artifact and routing
- Worker 5: benchmark harness and research report

Workers must not edit overlapping files.

---

## 13. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Cultural terms become decorative prompt fluff | Always expand terms into visual operations and evaluation criteria |
| Product becomes too broad | v1 only supports static 2D visual discovery |
| User gets trapped in endless discussion | 8-turn cap and direction-card selection |
| Agent over-asks questions | Prefer inferred defaults and show alternatives |
| Benchmarks become subjective | Combine human blind preference, L1-L5 scoring, and operational metrics |
| Provider prompts diverge silently | Snapshot compiled prompts in artifacts |
| Discovery duplicates `/visual-brainstorm` | Discovery ends at selected direction; brainstorm creates proposal |
| Claims overstate model control | Public docs must say "guidance and evaluation", not "guaranteed control" |
| Existing repo docs disagree on MCP tool count | Add audit tripwires and update README / pyproject counts in the implementation release |

---

## 14. Success Criteria

V1 is successful when:

- Current-state tripwires confirm the expected MCP tools, providers, and traditions before Discovery ships.
- A fuzzy user intent produces a valid `taste_profile.json`.
- The system produces 3-5 valid direction cards with visual operations and avoid constraints.
- The user can select or blend directions in natural language.
- A selected direction compiles into a proposal-ready brief.
- The workflow hands off cleanly to `/visual-brainstorm`.
- The benchmark harness can compare direct prompt vs discovery-compiled prompt.
- Docs make an honest claim: cultural/aesthetic concepts are expanded into operational constraints and evaluated, not magically guaranteed.

---

## 15. Open Questions for Product Review

1. Should v1 include real thumbnail sketch generation, or only text sketch prompts?
   - Recommendation: text sketch prompts by default; real thumbnail generation behind explicit user opt-in.

2. Should `taste_profile.json` be per-project only or reusable across projects?
   - Recommendation: per-project in v1; reusable user taste profiles later.

3. Should `/visual-discovery` write directly under `docs/visual-specs/<slug>/discovery/` before a proposal exists?
   - Recommendation: yes. This creates a stable slug earlier and keeps all downstream artifacts in one project directory.

4. Should the first benchmark include external tools like Recraft/Krea/Midjourney?
   - Recommendation: no for automated benchmark; yes for a manual competitive comparison report.

5. Should Discovery support video directions?
   - Recommendation: not in v1. Add a later `/motion-discovery` or video branch after image workflow is validated.

---

## 16. References

- Existing sibling specs:
  - `docs/superpowers/specs/2026-04-21-visual-brainstorm-skill-design.md`
  - `docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md`
  - `docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md`
- Existing Vulca docs:
  - `README.md`
  - `docs/agent-native-workflow.md`
  - `docs/research/2026-04-14-segmentation-landscape.md`
  - `docs/tools-readiness-matrix.md`
- Competitive/product references considered in prior research:
  - Adobe Firefly Boards
  - Lovart AI Design Agent
  - FLORA canvas
  - Krea realtime canvas
  - Recraft design-forward generation
  - Midjourney personalization and moodboards
  - Google Whisk
  - Figma Buzz

---

## 17. Repo Audit Evidence

Checked on 2026-04-29 against the local checkout.

Current runtime facts:

- MCP runtime registered 28 tools with the current optional imports available:
  - core workflow tools: `archive_session`, `brief_parse`, `compose_prompt_from_design`, `create_artwork`, `evaluate_artwork`, `generate_concepts`, `generate_image`, `get_tradition_guide`, `inpaint_artwork`, `layers_composite`, `layers_edit`, `layers_evaluate`, `layers_export`, `layers_list`, `layers_paste_back`, `layers_redraw`, `layers_split`, `layers_transform`, `list_traditions`, `search_traditions`, `sync_data`, `unload_models`, `view_image`
  - Tool Protocol tools: `tool_brushstroke_analyze`, `tool_color_correct`, `tool_color_gamut_check`, `tool_composition_analyze`, `tool_whitespace_analyze`
- Image providers registered: `comfyui`, `gemini`, `mock`, `nb2`, `openai`.
- VLM providers registered: `litellm`, `mock`.
- Bundled traditions registered: `african_traditional`, `brand_design`, `chinese_gongbi`, `chinese_xieyi`, `contemporary_art`, `default`, `islamic_geometric`, `japanese_traditional`, `photography`, `south_asian`, `ui_ux_design`, `watercolor`, `western_academic`.
- Focused verification passed: `tests/test_visual_brainstorm_discovery_integration.py`, `tests/test_prompting.py`, `tests/test_mcp_studio.py`, `tests/test_generate_image_extended_signature.py`.

Known repo-doc mismatch:

- `README.md`, `pyproject.toml`, and `src/vulca/mcp_server.py` still contain older MCP tool-count language. This spec records the runtime count for Discovery planning, but the implementation plan should decide whether to update public docs in the same release or leave that as a separate documentation cleanup task.
