# Development History

Vault status: source-backed synthesis.

## v0.13 - v0.14: Layered Generation Foundation

The early layer work moved VULCA away from "generate one image, then cut it up"
toward generated layer stacks. The key architecture was a dual path:

- VULCA-generated images: plan layers before generation, generate layers,
  apply alpha/keying, validate, composite.
- External images: use VLM/SAM/DINO split paths and soften masks as best effort.

The important lesson: layer quality is not only a segmentation problem. For
generated images, the best layer quality starts at generation time.

Sources:

- `docs/superpowers/specs/2026-04-08-layers-redesign-design.md`
- `src/vulca/layers/layered_generate.py`
- `src/vulca/layers/layered_prompt.py`

## v0.15 - v0.17: Agent-Native Architecture And Visual Skills

VULCA deliberately moved away from hidden internal "brain" loops. The agent
plans; VULCA performs pixel and artifact operations.

Major outcomes:

- smaller MCP tool surface
- `generate_image`
- `view_image`
- `compose_prompt_from_design`
- `visual-brainstorm`
- `visual-spec`
- `visual-plan`
- style treatment and negative prompt controls

Sources:

- `docs/superpowers/specs/2026-04-16-agent-native-architecture-design.md`
- `docs/superpowers/specs/2026-04-21-visual-brainstorm-skill-design.md`
- `docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md`
- `docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md`

## v0.17.14: Native Mask Inpaint, Redraw Recontract, Pasteback

The redraw line became serious when dogfood exposed destructive and misleading
defaults. v0.17.14 added:

- native `inpaint_artwork(mask_path=...)`
- conservative `layers_redraw` recontract
- `layers_paste_back`
- non-destructive `layers_composite`
- quality gate symmetry on person/DINO paths

Source:

- `CHANGELOG.md`

## v0.18: Safer Redraw Defaults And Multi-Instance Split

v0.18 flipped `layers_redraw` defaults:

- no in-place overwrite by default
- cream background strategy
- preserve original alpha

It also added multi-instance support for orchestrated `layers_split` so repeated
objects such as rows of lanterns can become sibling layers instead of one
fragmented union mask.

Sources:

- `docs/superpowers/specs/2026-04-26-v0.18-layers-redraw-split-design.md`
- `CHANGELOG.md`

## v0.20 - v0.21: Mask-Aware And Crop-Aware Redraw

Sparse-alpha layer redraw initially drifted because unmasked image editing had
no reliable spatial cue. v0.20 introduced mask-aware routing; v0.21 made the
route model-aware and crop-aware:

- provider edit capability declaration
- gpt-image-2 all-edit-mask shim where needed
- sparse single-object padded bbox crop
- sparse multi-component bounded edits
- local quality gates
- advisory fields returned to MCP callers

Sources:

- `docs/superpowers/specs/2026-04-27-v0.20-mask-aware-redraw-routing-design.md`
- `CHANGELOG.md`
- `tests/test_layers_redraw_mask_aware.py`
- `tests/test_layers_redraw_crop_pipeline.py`

## v0.22 - v0.23: Target Refinement, Case Records, Provider Hardening

The next failure was not route selection but mask granularity. v0.22 introduced
target-aware mask refinement for small bright subjects such as flowers. v0.23
continued provider hardening and case logging:

- source-context edit mattes
- refined child masks
- generated evidence gates
- botanical/palette controls
- redraw, decompose, and layer-generate case schemas
- NB2/Gemini visible mask handling
- palette mask split mode

Sources:

- `docs/superpowers/specs/2026-04-30-v0.22-target-aware-mask-refinement-design.md`
- `docs/superpowers/specs/2026-05-05-vulca-learning-loop-v0-design.md`
- `docs/superpowers/specs/2026-05-05-decompose-case-design.md`
- `docs/superpowers/specs/2026-05-05-layer-generate-case-design.md`
- `CHANGELOG.md`

## 2026-06: Workspace And Website Productization

The product direction moved from "agent tool attachment" to "Workspace-first".
The Workspace branch implements a Creative Repo and review workflow. The website
branch implements a commercial homepage and film-led hero.

Sources:

- `source-index.md` Workspace section
- `source-index.md` Website section

## 2026-06: PPT Proof Lab

The PPT work became a large proof lab for usecase-to-deck workflows, visual
quality memory, renderer primitives, and release gates. It remains public
blocked as of Run 2.93 due to visual polish, legibility, and surface realism.

Source:

- `docs/product/ppt-run2-data-skill-quality/results/run2_93_visual_quality_evaluation.md`
  on branch `codex/vulca-ppt-case-pack`
