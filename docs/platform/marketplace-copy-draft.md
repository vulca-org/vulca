# Marketplace Copy Draft

**Status:** Draft for human review
**Last verified:** 2026-04-30

## One-Liner

Vulca is an agent-native visual control layer for turning fuzzy creative intent into reviewable direction cards, structured prompts, semantic layers, provider-routed image work, and cultural evaluation.

## Short Description

Plan, generate, inspect, and evaluate visual work from inside an agent workflow. Vulca packages discovery, prompt structure, decomposition, and L1-L5 cultural evaluation as skills backed by MCP tools.

## Long Description

Vulca helps creative agents work with images through auditable artifacts instead of one-shot prompting. It can clarify fuzzy visual intent, create direction cards, compose provider-aware prompts, decompose images into semantic layers, route generation through configured providers, and evaluate results against cultural and visual criteria.

The first marketplace release should emphasize:

- `/visual-discovery` for taste, culture, and direction exploration;
- `/visual-brainstorm`, `/visual-spec`, and `/visual-plan` for proposal/design/plan artifacts;
- `/decompose` for semantic layer extraction;
- `/evaluate` for structured review against Vulca's L1-L5 framework.

Redraw and inpaint tools are available for advanced workflows. Polished user-facing `/inpaint` or `/redraw-layer` skills will be promoted after v0.22 target-aware mask refinement evidence lands.

## Claude Marketplace Notes

Recommended install promise:

> Install Vulca to add visual discovery, decomposition, planning, and cultural evaluation workflows to Claude Code.

Do not promise raw image model quality. Vulca orchestrates and audits provider-backed workflows; it does not host a foundation model.

## Codex Plugin Notes

Recommended install promise:

> Install Vulca to add visual workflow skills and a local Vulca MCP server to Codex.

Codex public plugin publishing should stay future-facing until OpenAI's docs show that public submission is open. Current copy should point to repo-local marketplace validation and local MCP use.

## Safety And Privacy Copy

Vulca works with local image files and optional external image providers. Real-provider generation, editing, or evaluation should be explicit opt-in, because prompts, images, and provider metadata may leave the local machine depending on the configured provider.

## Avoid These Claims

- "Vulca guarantees better images."
- "Cultural terms always improve generation."
- "The public Codex listing has already launched."
- "Google marketplace listing is available."
- "Redraw is fully polished for every image."
- "Transparent layer output is the final after-image."
