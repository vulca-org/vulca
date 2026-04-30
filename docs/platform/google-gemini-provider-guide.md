# Google Gemini Provider Guide

**Status:** Draft provider guide
**Last verified:** 2026-04-30

## Official Path

Google's immediate Vulca role is provider infrastructure. Gemini API and Vertex AI expose image generation and image editing models, while Google ADK and Vertex AI Agent Engine are future agent integration targets.

Sources:

- [Gemini image generation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Vertex AI Gemini image generation and editing](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation)
- [Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Vertex AI Agent Engine overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
- [Google ADK MCP](https://google.github.io/adk-docs/mcp/)

## Vulca Position

Treat Google as:

- a current image provider path for generation, editing, reference-heavy exploration, and provider comparisons;
- a function-calling and MCP-compatible agent path to research later;
- not a direct public plugin listing path for Vulca today.

Model names and limits change quickly. Public docs should say "Gemini image models" or "Vertex AI image generation/editing" unless a specific benchmark or provider capability test pins an exact model ID.

## Provider Uses

Use Gemini / Vertex AI for:

- low-cost sketching and broad creative exploration;
- reference-aware image experiments;
- provider comparison against OpenAI and ComfyUI;
- prompt structure experiments where text and image interleave.

Avoid using Gemini docs to claim:

- that Google has a Vulca plugin listing surface;
- that a specific image model is always the best redraw backend;
- that every edit knob is available across every model.

## Release Gate

Before promoting Gemini provider support:

- verify current model IDs and output limits from official docs;
- run a real-provider opt-in smoke test;
- record cost, latency, provider, model, prompt, and output metadata;
- compare against OpenAI and ComfyUI for the same prompt artifacts;
- document provider-specific caveats in `docs/product/provider-capabilities.md`.
