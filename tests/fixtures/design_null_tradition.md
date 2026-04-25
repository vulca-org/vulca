---
slug: 2026-04-25-fixture-null-tradition
status: resolved
schema_version: "0.1"
domain: photography
tradition: null
generated_by: visual-spec@0.1.0
proposal_ref: tests/fixtures/proposal_null.md
created: 2026-04-25
updated: 2026-04-25
---

# Null-tradition fixture (pure photo brief, no cultural mapping)

Exercises the resolved-design path where `tradition: null` is the intended
state — a photo brief with no cultural overlay. Composition should still
produce a valid prompt from `base_prompt` + `color_constraint_tokens`.

## A. Provider + generation params

```yaml
reviewed: true
provider: openai
model: gpt-image-2
size: 1024x1024
seed: 1337
```

## C. Prompt composition

```yaml
reviewed: true
style_treatment: additive
base_prompt: |
  Crisp documentary photograph at golden hour. Preserve all photographic
  elements; do not stylize.
negative_prompt: ""
color_constraint_tokens:
  - "warm sunset palette"
  - "preserve natural skin tones"
sketch_integration: ignore
ref_integration: listed_in_notes
```
