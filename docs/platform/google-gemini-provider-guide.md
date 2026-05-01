# Google Gemini Provider Guide

**Status:** Draft provider guide
**Last verified:** 2026-05-01

## Official Path

Google's immediate Vulca role is provider infrastructure plus future MCP-compatible agent wiring. Gemini API and Vertex AI expose image generation and image editing models, Gemini CLI can consume local or remote MCP servers, and Google ADK / Gemini Enterprise Agent Platform are future agent integration targets.

Sources:

- [Gemini image generation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Vertex AI Gemini image generation and editing](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation)
- [Gemini CLI](https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli)
- [Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Gemini Enterprise Agent Platform scale guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale)
- [Google ADK MCP](https://google.github.io/adk-docs/mcp/)

As of 2026-05-01, the Gemini API image-generation docs describe Nano Banana as the public name for Gemini native image generation. They list Nano Banana 2 (`gemini-3.1-flash-image-preview`), Nano Banana Pro (`gemini-3-pro-image-preview`), and Nano Banana (`gemini-2.5-flash-image`) as distinct model families. Keep public Vulca docs at the capability level unless a provider capability test pins an exact model ID.

## Vulca Position

Treat Google as:

- a current image provider path for generation, editing, reference-heavy exploration, and provider comparisons;
- a function-calling, Gemini CLI, ADK, and Agent Platform path to research later;
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
