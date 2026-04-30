# Vulca Product Positioning Brief

**Date:** 2026-04-30
**Status:** Decision support for product repositioning
**Branch:** `codex/product-positioning-plan`
**Depends on:** `codex/visual-discovery` / PR #21

## Executive Decision

Vulca should reposition from "Claude Code image tools" to:

> **Agent-native visual control layer for creative direction, generation routing, pixel editing, and cultural evaluation.**

The product should not compete with one-click image/video generators on base-model quality. GPT Image, Gemini / Nano Banana, Seedance-style models, Midjourney, Firefly, and similar systems will keep improving. Vulca's defensible role is to make those models usable inside a serious creative workflow:

```text
fuzzy intent
-> taste / cultural tendency analysis
-> direction cards and sketch prompts
-> proposal.md / design.md / plan.md
-> provider-routed generation
-> semantic layers / inpaint / redraw / composite
-> L1-L5 evaluation and provenance
```

The product bet is not "better prompt text." The bet is **auditable creative control**.

## Why This Is Timely

Recent platform moves validate the direction:

- Anthropic is pushing Claude into creative work through connectors with Blender, Autodesk, Adobe, Ableton, Splice, and other creative tools. Their framing is integration with tools creatives already use, not a single model-only workflow. Source: [Claude for Creative Work](https://www.anthropic.com/news/claude-for-creative-work), 2026-04-28.
- Anthropic's Claude Design research preview explicitly targets wide exploration, brand/design-system reuse, fine-grained controls, export, and handoff to Claude Code. Source: [Introducing Claude Design](https://www.anthropic.com/news/claude-design-anthropic-labs), 2026-04-17.
- OpenAI now lists GPT Image 2 as a state-of-the-art image generation and editing model with Image API and edit endpoint support. Source: [GPT Image 2 model page](https://developers.openai.com/api/docs/models/gpt-image-2).
- Google is productizing Gemini / Nano Banana as developer-facing image generation and editing infrastructure through Gemini API, AI Studio, and Vertex AI, including Gemini 3 Pro Image / Nano Banana Pro. Source: [Build with Nano Banana Pro](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-3-pro-image-developers/).
- Claude Code's MCP model is explicitly for connecting tools and data sources so Claude can act in external systems. Source: [Claude Code MCP docs](https://code.claude.com/docs/en/mcp).

Conclusion: the market is moving toward **creative agents connected to toolchains**. Vulca should be the visual-control toolchain for culturally aware, layer-aware creative work.

## What Exists Today

### Shipped or PR-Ready

- `/decompose`: agent-facing semantic layer extraction with real transparent layer artifacts.
- MCP image/pixel tools: `layers_split`, `layers_list`, `layers_edit`, `layers_transform`, `layers_redraw`, `layers_composite`, `layers_export`, `layers_evaluate`, `layers_paste_back`, `inpaint_artwork`, `view_image`.
- Provider layer: `mock`, `gemini`, `nb2`, `openai`, `comfyui`.
- OpenAI provider capability gating: model-aware edit capabilities, `quality`, `output_format`, and MIME handling; `input_fidelity` gated by model support.
- Cultural substrate: 13 traditions, tradition guides, L1-L5 evaluation framework, VULCA research basis.
- Visual workflow skills: `/visual-brainstorm`, `/visual-spec`, `/visual-plan`.
- `/visual-discovery` in PR #21: upstream fuzzy-intent layer with taste profile, direction cards, provider prompt artifacts, safe discovery artifacts, and `/visual-brainstorm` handoff.

### In Parallel

- v0.22 mask/refinement work is running separately in `/Users/yhryzy/dev/vulca/.worktrees/v0-22-mask-refinement`.
- That branch should own redraw robustness, target-aware mask refinement, and local quality gates.
- This product-positioning branch should not touch redraw internals.

## What Vulca Is Not

Vulca is not:

- a hosted image foundation model;
- a "prompt enhancer" that only rewrites user text;
- a Claude-only wrapper;
- a generic design app competing with Figma, Canva, or Adobe;
- a final-image one-shot interface.

Vulca is:

- a workflow and control layer that can run inside Claude Code now;
- a provider router across OpenAI, Gemini, ComfyUI, mock, and future backends;
- a structured artifact pipeline for creative decisions;
- a pixel-editing layer between model output and usable deliverables;
- a cultural evaluation system that gives Vulca a more defensible niche than generic image tooling.

## Platform Strategy

### Recommended Order

1. **Claude Code first.** This is the wedge because MCP + skills + artifacts match Vulca's existing architecture.
2. **OpenAI / Codex second.** Treat OpenAI as both a provider backend and an agent surface. GPT Image 2 should be supported as a provider, while product docs should avoid depending on a single model ID.
3. **Gemini third.** Gemini / Nano Banana is a strong sketch and image-editing backend, especially for low-cost exploration and personalized/reference-heavy image workflows.
4. **Web / Studio later.** A UI becomes important once users need visual card comparison, sketch grids, layer viewers, and evaluation dashboards.

### Do Not Choose Only Claude

Claude is the best initial distribution channel, not the whole product. Vulca's durable asset is the artifact contract:

```text
discovery.md
taste_profile.json
direction_cards.json
proposal.md
design.md
plan.md
manifest.json
evaluation.json
```

Those artifacts should remain platform-independent so the workflow can run under Claude Code, Codex, Gemini/Antigravity-like agents, or a future Vulca Studio UI.

## Where Vulca Can Intervene Around One-Click Models

One-click models reduce the value of raw generation wrappers. They do not remove the need for Vulca.

| Stage | One-click model behavior | Vulca intervention |
|---|---|---|
| Before generation | User prompt is vague; model commits too early | `/visual-discovery`, taste/culture profile, direction cards |
| Prompt compilation | Model receives a flat prompt | structured prompt artifacts, avoid lists, visual ops, provider-specific variants |
| Provider choice | User picks one model manually | provider capability matrix, cost/quality routing, local/cloud fallback |
| Image editing | Model edits entire image or follows vague region prompt | masks, semantic layers, target-aware redraw, paste-back |
| Evaluation | User judges subjectively | L1-L5 cultural scoring, visual quality gates, artifact provenance |
| Iteration | User rerolls blindly | plan.md iterations, selected direction history, comparison artifacts |

## Product Pillars

1. **Discover:** clarify fuzzy intent and cultural/taste tendencies before pixels.
2. **Direct:** convert direction into provider-specific constraints and prompts.
3. **Generate:** route to OpenAI, Gemini, ComfyUI, mock, and future providers.
4. **Control:** decompose, inpaint, redraw, composite, and preserve non-target pixels.
5. **Evaluate:** score cultural/visual quality and record rationale.
6. **Archive:** keep decisions, prompts, images, masks, layers, and evaluations reviewable.

## Required Experiments

The cultural/taste-analysis claim must be proven, not asserted.

### Experiment 1: Do Cultural Terms Help?

Run the same project across providers with four prompt conditions:

- A: naive user prompt only.
- B: user prompt + cultural terms.
- C: user prompt + cultural terms + visual operations.
- D: full direction-card prompt with avoid list, evaluation focus, and provider-specific form.

Measure:

- human preference;
- L1-L5 rubric alignment;
- prompt adherence;
- cultural cliche avoidance;
- editability / layer separability;
- cost and latency.

### Experiment 2: Does Discovery Improve User Choice?

Compare:

- one-shot generation from fuzzy prompt;
- `/visual-discovery` direction cards without sketches;
- `/visual-discovery` direction cards with low-cost sketch prompts;
- full discovery -> brainstorm -> spec -> plan chain.

Measure:

- number of rerolls;
- time to approved direction;
- user's confidence in selected direction;
- final evaluation score;
- ability to explain why the result fits the brief.

### Experiment 3: Which Provider Owns Which Job?

Benchmark OpenAI, Gemini, and ComfyUI across:

- text rendering;
- reference preservation;
- local edits;
- cultural style adherence;
- transparent outputs;
- mask compliance;
- cost/latency;
- failure modes.

The product should route by evidence, not by platform preference.

## README Repositioning

The README first viewport should stop leading only with `/decompose`. Decompose remains the most concrete demo, but the product story should be broader:

```text
Vulca turns fuzzy visual intent into controlled creative production.

Discover the direction, compile the brief, route the model, edit the pixels,
and evaluate the result — all as agent-native artifacts and MCP tools.
```

Recommended first-screen order:

1. One-line product thesis.
2. Workflow diagram: Discover -> Spec -> Generate -> Edit -> Evaluate.
3. Short "Why Vulca exists" paragraph: one-click models generate; Vulca controls.
4. Current capability matrix.
5. Quick start with Claude Code.
6. Provider support matrix.
7. Decompose showcase.
8. Visual discovery example.
9. Roadmap with current vs next vs experiments.

## Roadmap

### Now: Product Coherence

- Write product positioning spec.
- Rewrite README around the full workflow.
- Add platform/provider decision matrix.
- Add benchmark plan for cultural-term efficacy.
- Keep redraw robustness in the separate v0.22 branch.

### Next: Evaluation Skill

- Ship `/evaluate` as the next user-facing skill.
- Convert existing `evaluate_artwork` and traditions into an agent workflow.
- Use evaluation as the proof layer for cultural/taste analysis.

### Next: Redraw Productization

- Merge v0.22 target-aware mask refinement after verification.
- Expose `/inpaint` or `/redraw-layer` as a skill once the underlying route is robust.
- Update README with honest boundaries: sparse multi-instance edits are harder than single-object edits.

### Then: Benchmark and Studio

- Run cultural-term efficacy experiments.
- Build a lightweight local visual review surface only after artifact contracts are stable.
- Consider marketplace/distribution: Claude plugin directory first, then OpenAI/Codex-facing docs, then Gemini/Antigravity-facing examples.

## Strategic Risks

- **Generic creative platforms absorb the workflow.** Claude Design, Figma, Canva, Adobe, and Gemini will keep adding agentic creative loops. Vulca must stay focused on layer control + cultural evaluation, not generic design generation.
- **Cultural analysis may not improve generation.** This is why experiments are required. If culture terms alone do not help, product language must emphasize visual operations and evaluation rather than cultural vocabulary.
- **README overclaims.** Public docs must distinguish implemented, PR-ready, parallel work, and roadmap.
- **Provider drift.** Model IDs and supported parameters change. Product docs should describe provider capabilities, while implementation keeps capability gates.

## Decision

Proceed with a product-positioning and README plan. Treat `/visual-discovery` as the upstream entry point of the complete workflow, not as the final product. Keep the platform strategy multi-provider and agent-surface-neutral, with Claude Code as the first wedge.
