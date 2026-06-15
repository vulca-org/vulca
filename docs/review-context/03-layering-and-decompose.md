# Layering And Decompose Memory

Vault status: protected technical memory.

## Core Distinction

VULCA has two layer directions:

1. Existing image -> semantic source layers.
2. Intent / plan -> generated layer stack.

These share vocabulary but are not the same operation.

## Existing Image Decomposition

Decompose starts with a flat source image and extracts source pixels into RGBA
semantic layers. The main contract is:

- source image stays causal source
- layer names and `semantic_path` explain what was extracted
- residual captures unclaimed pixels
- manifest records quality and geometry
- agent reviews manifest and iterates when residual or flags indicate failure

The important lesson from dogfood: residual is not a bug to hide. It is an
honesty artifact that tells the agent what was missed.

Sources:

- `docs/agent-native-workflow.md`
- `src/vulca/layers/split.py`
- `src/vulca/layers/manifest.py`
- `docs/superpowers/specs/2026-05-05-decompose-case-design.md`

## Generated Layer Stack

Layered generation starts from intent, tradition, layer plan, and prompt stack.
It aims to create independently editable output layers. This path exists because
post-hoc segmentation destroys soft ink edges, flying-white effects, and
generation-time style consistency.

Key ideas:

- plan layers before generation
- layer prompts carry spatial and role constraints
- provider calls can happen per layer
- style/reference anchoring can preserve visual unity
- manifest and composite make output inspectable

Sources:

- `docs/superpowers/specs/2026-04-08-layers-redesign-design.md`
- `src/vulca/layers/layered_generate.py`
- `src/vulca/layers/layered_prompt.py`
- `docs/superpowers/specs/2026-05-05-layer-generate-case-design.md`

## Multi-Instance Lessons

Repeated objects are not one object. The Scottish lantern and similar dogfood
cases led to `multi_instance` support:

- DINO returns multiple boxes.
- NMS caps and orders instances.
- each instance becomes a sibling layer when possible.
- under-detection creates a quality flag rather than a false success.

Boundary: multi-instance support is a decomposition improvement. It does not
guarantee successful redraw or generation of every instance.

## Rescue Patterns

Known rescue patterns:

- high residual -> inspect missed entities
- DINO too tight -> simplify label or use `sam_bbox`
- SAM headless torso -> split head/body
- small low-contrast face -> crop, upscale, brighten, rerun
- hero subject eroded -> promote semantic path/order
- already-low residual -> avoid over-splitting

These are part of VULCA's agent-native contract: the SDK surfaces signals; the
agent adjusts the plan.
