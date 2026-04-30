# Vulca Provider and Platform Capability Matrix

**Status:** Public product guide
**Last updated:** 2026-04-30

Vulca separates agent surfaces from image providers.

## Agent Surfaces

| Surface | Role | Status |
|---|---|---|
| Claude Code | Primary agent surface for MCP tools and skills | Current |
| OpenAI Codex / ChatGPT developer surfaces | Future agent surface; OpenAI is already a provider backend | Planned |
| Gemini / Antigravity-like developer agents | Future agent surface for Google-native workflows | Planned |
| Python SDK / CLI | Power-user and test harness path | Current |
| Vulca Studio UI | Review surface for cards, sketches, layers, and evaluations | Later |

## Image Providers

| Provider | Current role | Use it for | Avoid using it for |
|---|---|---|---|
| `mock` | Cost-free artifact validation | tests, discovery sketch records, workflow dry-runs | quality claims |
| `openai` | High-quality generation/editing backend | final candidates, image edits, text-heavy visuals when model supports it | assuming every model supports every edit knob |
| `gemini` / `nb2` | Gemini image backend | sketching, reference-heavy exploration, alternative provider comparisons | treating marketing names as implementation IDs |
| `comfyui` | Local generation/editing backend | local-first workflows, inspectable pipelines, advanced users | assuming cloud-model prompt behavior |

## Documentation Rules

- Describe capability classes in public prose.
- Put model IDs in examples and matrices.
- Keep capability gates in code.
- Do not write fixed MCP tool counts in public docs.
- Treat real-provider discovery sketches as explicit opt-in.
