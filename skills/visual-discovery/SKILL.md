---
name: visual-discovery
description: "Discover visual direction from fuzzy intent before /visual-brainstorm: taste profile, culture analysis, direction cards, and sketch prompts."
---

You are running `/visual-discovery` - the upstream creative-direction step before `/visual-brainstorm`. Your job is to turn fuzzy visual intent into auditable discovery artifacts: `discovery.md`, `taste_profile.json`, and `direction_cards.json`.

## Triggers

- Slash command: `/visual-discovery <slug>`
- Chinese aliases: `方向探索`, `审美分析`, `文化倾向分析`, `抽卡`, `先聊再出方案`
- Intent auto-match: the user is unsure what visual direction they want, asks for alternatives before a brief, asks why a direction fits a brand/culture/audience, or asks to explore taste/cultural tendencies before generating pixels.

## Scope

Accept static 2D visual projects that can become one `/visual-brainstorm` proposal: poster, editorial illustration, packaging, brand visual, product campaign visual, social asset, cover/hero visual, photography brief, and single hero illustration for UI.

Redirect product UI layout, app screens, web flows, full video workflows, 3D/CAD, industrial design, and full brand strategy systems.

## Tool Rules

Allowed:

- Read existing project docs.
- View user-provided reference images.
- Use `list_traditions`, `search_traditions`, and `get_tradition_guide`.
- Compose prompt artifacts using the existing `compose_prompt_from_design` pattern.
- Write discovery artifacts.
- Use `generate_image(provider="mock")` only for non-final sketch records.
- Use `generate_concepts(provider="mock")` only for non-final multi-card sketch records.

Forbidden:

- real provider `generate_image` / `generate_concepts` unless the user explicitly opts into exploratory sketch generation.
- `layers_*`
- `inpaint_artwork`
- `evaluate_artwork` with a real VLM provider
- final production image generation

## Conversation Loop

1. Parse the user's fuzzy visual intent.
2. Infer domain, likely traditions, uncertainty, mood, commercial context, and risk.
3. Ask at most 1-3 targeted questions only when inference is insufficient.
4. Produce 3-5 direction cards.
5. Let the user select, reject, or blend cards.
6. Update preference signals.
7. Optionally create text sketch prompts or mock sketch records.
8. Write discovery artifacts.
9. Print the handoff string.

Hard cap: 8 user-facing turns. If the user says `deep discovery` or `继续深入`, extend by 4 turns, max 12.

## Direction Card Requirements

Each card must include:

- `id`
- `label`
- `summary`
- `culture_terms`
- `visual_ops.composition`
- `visual_ops.color`
- `visual_ops.texture`
- `visual_ops.symbol_strategy`
- `visual_ops.avoid`
- `provider_hint.sketch`
- `provider_hint.final`
- `provider_hint.local`
- `evaluation_focus.L1` through `evaluation_focus.L5`
- `risk`
- `status`

Provider hints must include model when model matters:

```json
{
  "sketch": {"provider": "gemini", "model": "gemini-3.1-flash-image-preview"},
  "final": {"provider": "openai", "model": "gpt-image-2"},
  "local": {"provider": "comfyui"}
}
```

## Artifact Paths

Write artifacts under:

```text
docs/visual-specs/<slug>/discovery/
```

Required files:

```text
docs/visual-specs/<slug>/discovery/discovery.md
docs/visual-specs/<slug>/discovery/taste_profile.json
docs/visual-specs/<slug>/discovery/direction_cards.json
```

Optional file when sketch prompts are requested:

```text
docs/visual-specs/<slug>/discovery/sketch_prompts.json
```

## Handoff

When one direction is selected, print:

```text
Ready for /visual-brainstorm. Suggested topic:
"<compiled one-paragraph project brief>"
```

Do not auto-invoke `/visual-brainstorm`. The user must approve the transition.
