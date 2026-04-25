---
slug: 2026-04-25-fixture-artifact-tokens
status: resolved
schema_version: "0.1"
domain: brand_visual
tradition: chinese_gongbi
generated_by: visual-spec@0.1.0
proposal_ref: tests/fixtures/proposal_artifact.md
created: 2026-04-25
updated: 2026-04-25
---

# Artifact-frozen tradition_tokens fixture

Exercises the path where `C.tradition_tokens` is present in the design.md.
The composer must prefer these frozen tokens over re-deriving from the
live registry (the registry can drift after a design is frozen).

The custom token list below intentionally differs from what
`get_tradition_guide("chinese_gongbi")` would produce, so a registry-derived
implementation will fail the assertion.

## A. Provider + generation params

```yaml
reviewed: true
provider: openai
model: gpt-image-2
```

## C. Prompt composition

```yaml
reviewed: true
style_treatment: additive
base_prompt: |
  Test artifact-tokens path.
negative_prompt: ""
tradition_tokens:
  - "FROZEN_TOKEN_A"
  - "FROZEN_TOKEN_B"
color_constraint_tokens:
  - "test color"
sketch_integration: ignore
ref_integration: listed_in_notes
```
