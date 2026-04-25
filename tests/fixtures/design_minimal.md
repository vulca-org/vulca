---
slug: 2026-04-25-fixture-minimal
status: resolved
schema_version: "0.1"
domain: brand_visual
tradition: chinese_gongbi
generated_by: visual-spec@0.1.0
proposal_ref: tests/fixtures/proposal_minimal.md
created: 2026-04-25
updated: 2026-04-25
---

# Minimal design fixture for compose_prompt_from_design tests

This file is a synthetic fixture. It exercises the parser surface of
`vulca.prompting.compose_prompt_from_design` without depending on any
real workspace artifact. Keep it minimal — only the sections that the
parser actually reads (frontmatter, `## A.`, `## C.`).

## A. Provider + generation params

```yaml
reviewed: true
provider: openai
model: gpt-image-2
input_fidelity: high
quality: high
size: 1024x1536
seed: 1337
steps: null
cfg_scale: null
```

## C. Prompt composition

```yaml
reviewed: true
style_treatment: additive
base_prompt: |
  Additive gongbi overlay on a reference photograph. PRESERVE every
  existing photographic element — treat the base photo as immutable
  pixels. Paint NEW gongbi elements INTO the scene only.
negative_prompt: ""
color_constraint_tokens:
  - "cinnabar red 朱砂红"
  - "muted gold 泥金"
  - "stone blue 石青"
sketch_integration: ignore
ref_integration: listed_in_notes
```
