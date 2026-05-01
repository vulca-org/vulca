# Vulca Product Positioning + Platform Intervention Design Spec

**Date:** 2026-04-30
**Status:** Draft for product review
**Scope:** Product positioning, README rewrite, platform strategy, and validation experiments
**Branch:** `codex/product-positioning-plan`
**Depends on:** `codex/visual-discovery` / PR #21

This spec defines how Vulca should reposition after the `/visual-discovery` work. `/visual-discovery` is not the whole product. It is the upstream entry point in a larger agent-native visual control workflow.

---

## 1. Product Thesis

Vulca should be positioned as:

```text
Agent-native visual control layer for creative direction, provider-routed generation,
semantic pixel editing, and cultural evaluation.
```

The product should not compete directly with one-click image/video models on final image quality. Instead, Vulca should intervene around those models:

- before generation, by clarifying fuzzy intent and cultural/taste tendencies;
- during generation, by compiling provider-specific prompts and routing by capability;
- after generation, by decomposing, editing, redrawing, compositing, evaluating, and archiving artifacts.

The defensible product value is **controlled creative workflow**, not "better prompt wording."

---

## 2. External Platform Signals

### 2.1 Anthropic / Claude

Anthropic's April 2026 creative push validates agent-native creative workflows:

- [Claude for Creative Work](https://www.anthropic.com/news/claude-for-creative-work) frames Claude as a connector to tools creatives already use, including Blender, Autodesk, Adobe, Ableton, Splice, Affinity, SketchUp, and Resolume.
- [Claude Design](https://www.anthropic.com/news/claude-design-anthropic-labs) targets polished visual work, broad exploration, brand/design-system reuse, fine-grained controls, export to Canva/PDF/PPTX/HTML, and handoff to Claude Code.
- [Claude Code MCP docs](https://code.claude.com/docs/en/mcp) position MCP as the way Claude connects to external tools and acts directly in those systems.
- [Claude Code subagents docs](https://code.claude.com/docs/en/sub-agents) reinforce the pattern of specialized workers with separate context windows and tool access.

Implication: Claude is the best initial distribution wedge for Vulca, but the real market movement is "creative agent + connected toolchain."

### 2.2 OpenAI

OpenAI is simultaneously a provider backend and an agent platform:

- [GPT Image 2](https://developers.openai.com/api/docs/models/gpt-image-2) is now listed as an image generation and editing model with Image API and edit endpoint support.
- [OpenAI image generation guide](https://developers.openai.com/api/docs/guides/image-generation) distinguishes Image API and Responses API flows and supports customizable quality, size, format, compression, and transparency depending on model support.
- [OpenAI developers homepage](https://developers.openai.com/) positions Codex, Apps SDK, MCP, and GPT Image 2 as developer-facing surfaces.

Implication: Vulca should support GPT Image 2 as a provider where available, but public product language should describe capability classes rather than overfitting to one model ID.

### 2.3 Google / Gemini

Google is turning Gemini image models into developer infrastructure:

- [Gemini 3](https://blog.google/products-and-platforms/products/gemini/gemini-3/) emphasizes multimodal reasoning, planning, AI Studio, Vertex AI, and agentic workflows.
- [Nano Banana Pro / Gemini 3 Pro Image](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-3-pro-image-developers/) is positioned for developers through Gemini API, AI Studio, and Vertex AI, with higher-fidelity images, better text rendering, and creative platform integrations.

Implication: Gemini should remain a first-class provider path, especially for low-cost sketching, reference-heavy generation, and future integration with agentic developer platforms.

---

## 3. Current Vulca Assets

### 3.1 Implemented or PR-Ready

- `/decompose`: semantic layer extraction skill and showcase.
- `/visual-discovery`: PR #21 upstream fuzzy-intent workflow with taste profiles, direction cards, prompt artifacts, and discovery handoff.
- `/visual-brainstorm`, `/visual-spec`, `/visual-plan`: artifact-based production chain.
- MCP tools for generation, evaluation, image viewing, layer operations, inpainting, redraw, paste-back, and Tool Protocol analyzers.
- Provider registry: `mock`, `gemini`, `nb2`, `openai`, `comfyui`.
- OpenAI capability gating and output MIME handling.
- Cultural foundation: 13 traditions, L1-L5 framework, research-backed evaluation.

### 3.2 Parallel Work

- v0.22 target-aware mask refinement runs in `/Users/yhryzy/dev/vulca/.worktrees/v0-22-mask-refinement`.
- This spec does not change redraw internals. It should reference the redraw branch as a dependency for later `/inpaint` or `/redraw-layer` productization.

### 3.3 Gaps

- README still leads with `/decompose`, which undersells the full workflow.
- `/evaluate` is not yet packaged as a user-facing skill.
- There is no public product document explaining Vulca's relationship to Claude Design, OpenAI image models, Gemini / Nano Banana, or future studio UI.
- Cultural/taste-analysis value has not been benchmarked across providers.
- Provider capability matrix is mostly implicit in code and scattered docs.

---

## 4. Product Architecture

### 4.1 Workflow

```text
User fuzzy intent
  -> /visual-discovery
  -> direction cards + taste profile
  -> /visual-brainstorm
  -> proposal.md
  -> /visual-spec
  -> design.md
  -> /visual-plan
  -> plan.md + generation/evaluation iterations
  -> layer edit / redraw / inpaint as needed
  -> archive
```

### 4.2 Product Pillars

1. **Discovery:** infer taste, cultural tendency, audience, uncertainty, and direction alternatives.
2. **Specification:** turn selected direction into reviewable proposal/design/plan artifacts.
3. **Provider routing:** choose OpenAI, Gemini, ComfyUI, mock, or future providers by capability and cost.
4. **Pixel control:** decompose, mask, inpaint, redraw, composite, and paste back without destroying non-target regions.
5. **Evaluation:** apply L1-L5 cultural and visual scoring to generated or edited outputs.
6. **Provenance:** preserve prompts, masks, layers, model IDs, costs, failures, and user overrides.

### 4.3 Data Artifacts

The following artifacts are platform-independent and should become the product contract:

```text
discovery.md
taste_profile.json
direction_cards.json
sketch_prompts.json
proposal.md
design.md
plan.md
manifest.json
evaluation.json
errors.json
```

Agent surfaces may differ. These artifacts should not.

---

## 5. Platform Strategy

### 5.1 Agent Surfaces

| Surface | Priority | Role |
|---|---:|---|
| Claude Code | 1 | Current wedge: MCP + skills + artifacts are already native. |
| OpenAI Codex / ChatGPT developer surfaces | 2 | Future agent surface and distribution path; OpenAI is also a provider backend. |
| Gemini / Antigravity-like developer agents | 3 | Future agent surface for Google-native image and developer workflows. |
| Local CLI / Python SDK | 4 | Power-user and test harness path. |
| Vulca Studio UI | 5 | Needed after artifacts stabilize; not first. |

### 5.2 Provider Backends

| Provider | Product role | Current posture |
|---|---|---|
| `openai` | high-quality final image/edit provider | support GPT Image 2 where available; keep capability gates |
| `gemini` / `nb2` | low-cost sketching and image editing path | keep as first-class sketch/final candidate |
| `comfyui` | local-first, inspectable generation/editing | critical for offline and advanced users |
| `mock` | test, artifact, and cost-free workflow validation | must remain default for discovery sketches |

### 5.3 Key Rule

Do not choose "Claude only" or "OpenAI only." Choose **Claude-first distribution** and **multi-provider execution**.

---

## 6. README Rewrite Design

The README should move from "decompose showcase first" to "full visual control workflow first."

### 6.1 First Viewport

Recommended headline:

```text
Vulca turns fuzzy visual intent into controlled creative production.
```

Recommended subheadline:

```text
Discover the direction, compile the brief, route the model, edit the pixels,
and evaluate the result — as agent-native artifacts and MCP tools.
```

### 6.2 README Sections

1. Product thesis and workflow diagram.
2. "Why Vulca exists": one-click models generate, Vulca controls.
3. Current capability matrix: Discovery, Spec, Generate, Edit, Evaluate, Archive.
4. Quick start for Claude Code.
5. Provider matrix.
6. `/decompose` concrete showcase.
7. `/visual-discovery` example.
8. Layer/edit/redraw status with honest boundaries.
9. Evaluation and cultural framework.
10. Roadmap and experiments.

### 6.3 Documentation Rules

- Do not write fixed MCP tool counts in public docs.
- Separate "implemented", "PR-ready", "parallel branch", and "roadmap."
- Use provider capability language in public docs; keep model IDs in matrices and examples.
- Explicitly state that real provider sketching in discovery is opt-in.
- Do not claim cultural terms improve generation until experiments support it.

---

## 7. Experiment Design

### 7.1 Cultural Term Efficacy

Question: do cultural/taste terms actually guide generation, or do visual operations do the work?

Conditions:

- A: naive prompt.
- B: naive prompt + cultural terms.
- C: cultural terms + visual operations.
- D: full direction-card prompt with avoid list and evaluation focus.

Providers:

- OpenAI GPT Image 2 or current GPT Image provider.
- Gemini / Nano Banana provider.
- ComfyUI local provider.
- Mock only for artifact validation, not quality measurement.

Measures:

- human preference;
- L1-L5 score;
- cliche avoidance;
- instruction adherence;
- editability/layer separability;
- cost and latency;
- failure class.

### 7.2 Discovery Loop Efficacy

Question: does `/visual-discovery` reduce rerolls and increase user confidence?

Compare:

- direct one-shot prompt;
- direction cards without sketches;
- direction cards with sketch prompts;
- full discovery -> brainstorm -> spec -> plan.

Measures:

- turns to approved direction;
- number of generated images;
- user confidence;
- final score;
- explainability of final result.

### 7.3 Provider Capability Benchmark

Question: which provider should own which creative job?

Tasks:

- text rendering;
- reference preservation;
- mask compliance;
- local edits;
- cultural style adherence;
- transparency/background handling;
- multi-image input;
- cost/latency.

Output:

- provider capability matrix;
- route recommendations;
- README support table.

---

## 8. Roadmap

### Phase 0: Product Coherence

- Create product positioning brief.
- Create this design spec.
- Create implementation plan for README/platform docs.
- Keep redraw implementation in its separate v0.22 branch.

### Phase 1: Public Narrative

- Rewrite README around the full workflow.
- Add docs/product/roadmap.md.
- Add docs/product/provider-capabilities.md.
- Add docs/product/experiments/cultural-term-efficacy.md.

### Phase 2: Skill Packaging

- Ship `/evaluate`.
- Productize `/inpaint` or `/redraw-layer` after real-image dogfood validates the v0.22 redraw route.
- Update `using-vulca-skills` routing once these skills exist.

### Phase 3: Evidence and Distribution

- Run benchmark experiments.
- Publish before/after case studies.
- Submit/update Claude plugin distribution.
- Create OpenAI/Codex and Gemini-facing usage guides.

### Phase 4: Studio UI

- Build only after artifact contracts and benchmarks stabilize.
- Initial UI should be a review surface for direction cards, sketch grids, layers, and evaluation, not a full design app.

---

## 9. Acceptance Criteria

The product-positioning work is complete when:

- README first viewport explains the full Vulca workflow, not only `/decompose`.
- A product roadmap doc states current vs next vs later without overclaiming.
- A provider capability doc explains OpenAI/Gemini/ComfyUI/mock roles.
- A benchmark doc defines how to test cultural/taste-analysis impact.
- Public docs cite current platform facts and avoid stale model/tool claims.
- No redraw internals are changed in this branch.

---

## 10. Open Questions

- Should the public tagline emphasize "creative direction" or "visual control" first?
- Should `/evaluate` ship before README rewrite lands, or can README list it as next?
- Should the first Studio UI be a local static HTML report generator instead of a hosted app?
- Should `gpt-image-2` be the default OpenAI final provider after capability/cost checks, or stay an explicit model override?
