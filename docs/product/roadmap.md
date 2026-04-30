# Vulca Product Roadmap

**Status:** Public product roadmap
**Last updated:** 2026-04-30

Vulca is an agent-native visual control layer. The product turns fuzzy visual intent into controlled creative production through reviewable artifacts, provider-routed generation, semantic pixel editing, and cultural evaluation.

## Current

- `/decompose`: semantic layer extraction into transparent PNG artifacts.
- `/visual-discovery`: fuzzy intent -> taste profile -> direction cards -> discovery artifacts.
- `/visual-brainstorm`, `/visual-spec`, `/visual-plan`: proposal/design/plan workflow for controlled generation.
- `/evaluate`: user-facing evaluation skill over existing `evaluate_artwork`.
- Provider registry: `mock`, `gemini`, `nb2`, `openai`, `comfyui`.
- `docs/product/provider-capabilities.md`: provider/platform capability matrix.
- `plugins/vulca`: repo-local Codex plugin package for marketplace validation.
- `.agents/plugins/marketplace.json`: repo marketplace entry for Codex plugin testing.
- MCP tools for image generation, image viewing, evaluation, inpainting, layers, redraw, compositing, paste-back, and Tool Protocol analysis.
- 13 cultural traditions and L1-L5 evaluation framework.

## Next

- Claude plugin marketplace packaging and submission checklist.
- Codex plugin marketplace validation and MCP usage guide.
- ChatGPT remote MCP prototype scope.
- Cultural-term efficacy benchmark real-provider opt-in.
- v0.22 target-aware mask refinement review and merge gate.

## In Parallel

- v0.22 target-aware mask refinement in `.worktrees/v0-22-mask-refinement`.
- This work owns redraw robustness and should land before `/inpaint` or `/redraw-layer` is marketed as a polished user-facing skill.

## Later

- `/inpaint` or `/redraw-layer` skill once redraw routes are robust.
- Official Codex public plugin listing, once OpenAI opens the public publishing flow.
- Google ADK / Vertex Agent Engine prototype.
- Lightweight Studio review UI for direction cards, sketch grids, layers, and evaluation reports.

## Non-Goals

- Hosting a foundation image/video model.
- Competing with one-click image models on raw generation quality.
- Building a general-purpose design app before artifact contracts stabilize.
