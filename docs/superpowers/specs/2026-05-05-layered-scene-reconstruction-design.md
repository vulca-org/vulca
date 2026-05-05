# Source-Conditioned Layered Generation Design

**Date:** 2026-05-05
**Target version:** v0.24 candidate
**Status:** Draft for user review

---

## Problem

The v0.23 roadside redraw work improved local botanical replacement, but it also
exposed a product boundary: a single local redraw mask is not enough when the
desired result is closer to a cleaned, stylized reconstruction of the whole
scene.

The visible failure mode is old source residue. Small flower edits can generate
better flower heads, but if the original source flower pixels remain outside the
accepted output alpha, the pasteback looks like new flowers were layered on top
of old flowers. Tightening the child prompt helps, but it cannot solve ownership
of adjacent pixels by itself.

The user direction is to explore whether Vulca can reconstruct the same photo as
editable semantic layers: clean sky, vehicle, trees, guardrail, hedge, flowers,
stems, and residual texture. This is not just a bigger mask. It is a workflow
above redraw that assigns each visible surface to a layer, reconstructs or
preserves that layer with a clear prompt contract, and composites the result
back through the existing manifest system.

## Design Question

Can Vulca combine the existing layered-generation architecture with the new
redraw replacement contract to produce a more controllable "source photo ->
editable stylized layer stack" workflow?

## Product Boundary: Layered Generation, Not Decompose

This workflow is not the same product operation as `decompose`.

`decompose` takes an existing flat image and extracts source pixels into
semantic layers. Layered scene reconstruction should instead generate a new
editable layer stack that is source-conditioned by the photo: each layer has its
own prompt, policy, z-order, reference crop, and control/ownership mask. Masks
are scaffolding for generation and compositing, not the product definition.

The MVP can use curated masks to test layer ownership and geometry. That does
not make the workflow a split-image pipeline. The output should be a generated
or preserved semantic stack whose layers are independently editable.

## Recommended Approach

Use **source-conditioned layered generation/reconstruction** as the first
implementation lane. It starts from an existing photo as reference, defines the
semantic layer stack, uses control masks to constrain generation and ownership,
generates or preserves selected layers, and calls redraw only for local
replacement details inside those layers.

This approach fits the current branch because it reuses proven pieces:

- layered manifest output for semantic layer stacks.
- control masks for geometry and pixel ownership.
- target-aware mask refinement for small repeated details.
- source crop padding and OpenAI-compatible `/v1/images/edits`.
- pasteback/composite for visual review.
- quality gates and advisory for unsafe broad texture edits.

It also avoids overextending the small botanical strategy. Broad hedge, grass,
and tree surfaces need layer-specific reconstruction prompts and validation
instead of being treated as giant flower masks.

## Alternatives Considered

### A. Source-conditioned layered generation/reconstruction

Start from a source image, plan named semantic output layers, then use
layer-specific prompts and control masks to generate, preserve, or locally
replace each layer.

Pros:

- Directly addresses old-source residue by assigning pixel ownership.
- Works with user-provided images.
- Lets the current redraw strategy remain narrow and reliable.
- Produces artifacts a designer can inspect and edit per layer.

Cons:

- Depends on control mask quality for geometry and ownership.
- Requires z-index and overlap validation.
- Large layers need different gates than small-object replacement.

### B. Native layered generation from prompt

Generate each layer directly from a high-level intent without relying on a
source photo.

Pros:

- Cleaner alpha extraction for generated assets.
- Better for new illustration creation.
- Matches the earlier dual-path layer architecture.

Cons:

- Does not solve the current "recreate this photo" problem first.
- Harder to preserve source geometry and object identity.
- More likely to drift from the specific roadside image.

### C. Keep improving only local redraw

Continue splitting flower masks and tuning prompts.

Pros:

- Smallest code surface.
- Already has tests and visual evidence.

Cons:

- Cannot fully remove old residue when the surrounding layer still contains old
  target pixels.
- Does not address larger style mismatch across sky, car, trees, hedge, and
  guardrail.
- Keeps pushing broad scene problems into a local edit tool.

## Scope

The first deliverable should be a prototype and then a productized MVP for the
roadside photo class. It should not immediately become a universal scene
editor.

In scope:

- Build a semantic layer plan for a source image.
- Use masks as generation/control scaffolds and normalize them into
  non-overlapping layer ownership.
- Reconstruct selected layers using layer-specific image-edit prompts.
- Use `redraw_layer` for small detail layers such as white and yellow flower
  heads.
- Composite all layers back into a full preview.
- Save per-layer input, mask, raw, patch, pasteback, usage, and failure notes.
- Report when a layer is unsafe to regenerate.

Out of scope for this spec:

- Full UI workflow.
- Video.
- Camera relayout or perspective redesign.
- Text or logo editing.
- Full product-grade broad hedge repaint before a dedicated strategy exists.
- Committing large generated provider artifacts by default.

## Roadside Layer Taxonomy

For the current roadside image, start with this semantic stack:

| z-index | semantic path | role | first action |
|---:|---|---|---|
| 0 | `background.sky.clean_blue` | sky plate | reconstruct cleanly |
| 10 | `background.distant_trees` | far green tree mass | preserve or light cleanup |
| 20 | `subject.vehicle.red_car` | red car | reconstruct as isolated vehicle layer |
| 30 | `subject.vehicle.yellow_truck` | distant yellow vehicle | preserve unless mask is good |
| 40 | `foreground.guardrail` | horizontal guardrail | reconstruct or preserve |
| 50 | `foreground.grass_bank` | broad grass area | preserve/residual in MVP |
| 60 | `foreground.hedge_bush` | broad leaf texture | preserve/residual until strategy exists |
| 70 | `detail.dry_stems` | thin foreground stems | preserve or extract as line detail |
| 80 | `detail.white_flower_cluster` | small white flower heads | redraw replacement strategy |
| 90 | `detail.yellow_dandelion_heads` | small yellow flower heads | redraw replacement strategy |
| 100 | `residual.source_texture` | safety layer | fills holes and unknown pixels |

The stack is intentionally conservative: small detail layers can be edited
first, while broad green texture remains source-owned until a broad-texture
strategy exists.

## Data Flow

```text
source image
  -> semantic output layer plan
  -> control/ownership masks per semantic path
  -> ownership normalization for compositing
  -> per-layer reference crop + prompt contract
  -> provider-generated, locally-redrawn, preserved, or residual layer RGBA
  -> manifest
  -> composite preview
  -> per-layer and full-scene evaluation
```

### Mask Ownership

Every source pixel should have one primary owner:

- Foreground detail masks can overlap broad base masks during detection.
- Before compositing, detail masks subtract from their parent base masks.
- Any unassigned pixels go into `residual.source_texture`.
- The residual layer is visible in MVP outputs so holes are obvious.

This matters for the flower problem. If old white or yellow flower pixels remain
inside `foreground.hedge_bush`, then new flower heads will look stacked on top
of old ones. Layer ownership should subtract flower detail from the hedge base
before the final composite.

## Prompt Contract

Prompts should be English by default because current image-edit providers
respond more reliably to precise English spatial constraints. Chinese UI copy
can wrap these prompts later, but the provider prompt should stay direct.

### Global Layer Planning Prompt

Use this with a VLM or planning model before mask creation:

```text
You are planning an editable semantic layer reconstruction of one source image.

Return JSON only. Do not describe the image in prose.

Goal:
- Recreate the source image as a stack of editable visual layers.
- Each layer must own a clear semantic surface or object.
- Prefer fewer stable layers over many fragile fragments.
- Use a residual layer for pixels that are uncertain or not worth editing.

For each layer return:
- semantic_path: dot-separated stable name.
- display_name: short human-readable name.
- z_index: integer, lower means farther back.
- visual_role: background | subject | foreground | detail | residual.
- mask_prompt: concise phrase for segmentation.
- reconstruction_policy: reconstruct | preserve | local_redraw | residual.
- edit_risk: low | medium | high.
- forbidden_content: objects that must not appear in this layer.
- parent_layer: semantic_path or null.

Important:
- White and yellow flower heads should be detail layers, not part of hedge.
- Guardrail should be separate from vehicles and plants.
- Sky should not include trees, vehicles, rail, road, or flowers.
- Broad grass, hedge, and tree texture are high risk unless masks are clean.
```

### Common Edit Prefix

Use this prefix for OpenAI-compatible `/v1/images/edits` masked edits:

```text
Edit only the transparent mask pixels where mask alpha=0.
Leave every opaque pixel unchanged.
Use the source crop only as geometry, lighting, edge, and scale context.
Do not create a full miniature scene.
Do not add objects outside the requested layer.
Return a clean layer-compatible result with no rectangular thumbnail, black
background, hard pasted block, or unrelated scene content.
```

### Sky Layer Prompt

```text
Reconstruct only the sky layer.

Create a clean, calm blue sky plate matching the source camera angle and light.
Keep it simple and graphic, suitable for a polished illustrated roadside scene.
Do not include trees, vehicles, guardrail, road, hedge, flowers, stems, clouds,
text, birds, buildings, or silhouettes.
The sky should be smooth enough to sit behind all other layers.
```

Use policy: reconstruct. This can be a background plate rather than transparent
RGBA because it is the bottom layer.

### Distant Tree Layer Prompt

```text
Reconstruct only the distant tree canopy layer.

Keep the tree mass behind the vehicles and guardrail. Preserve the broad shape,
height, light direction, and soft depth of the source. Render it as cohesive
illustrated foliage, not detailed noisy leaf texture.
Do not include sky, cars, trucks, guardrail, road, foreground hedge, flowers,
or stems.
Avoid black fill, rectangular patches, and photo-real leaf noise.
```

Use policy: preserve first, reconstruct only if the mask is clean and layer area
is stable.

### Vehicle Layer Prompt

```text
Reconstruct only the red car as a separate visual layer.

Preserve the car's source position, scale, side profile, roofline, windows,
wheels, and perspective. Make the styling cleaner and more graphic while still
recognizable as the same roadside vehicle.
Do not include sky, trees, guardrail, road, hedge, flowers, stems, or other
vehicles.
Keep edges crisp enough for compositing, with natural antialiasing.
```

Use policy: reconstruct if the mask has clean vehicle boundaries; otherwise
preserve.

### Guardrail Layer Prompt

```text
Reconstruct only the metal roadside guardrail layer.

Preserve the long horizontal rail direction, post rhythm, perspective, and
occlusion relationship with the vehicles and plants. Use a clean illustrated
metal surface with subtle highlights.
Do not include cars, sky, trees, road, hedge, grass, flowers, or stems.
Avoid thick blocky bands, broken floating rail pieces, and dark background fill.
```

Use policy: reconstruct or preserve. Guardrail is a good early candidate because
it has strong geometry and clear z-order.

### Hedge And Bush Base Prompt

```text
Reconstruct only the broad foreground hedge and bush mass.

Preserve the overall silhouette, density, light direction, and roadside depth.
Create a cohesive illustrated green plant mass with controlled texture.
Do not generate individual white flowers, yellow flowers, car parts, guardrail,
sky, road, or tree trunks unless those pixels are explicitly inside the mask.
Avoid noisy photo leaves, black fill, rectangular pasted blocks, and large color
shifts.
```

Use policy: preserve in the first MVP. This prompt is included for later broad
texture strategy work, not for immediate unrestricted use.

### White Flower Detail Prompt

```text
Reconstruct only the small white flower heads inside the transparent mask.

Paint separated tiny white wildflower heads with warm centers, varied spacing,
and a clean illustrated style. Match the source footprint, scale, lighting, and
edge softness.
Do not repaint hedge texture, grass, stems, guardrail, vehicles, sky, road, or
any broad background area.
Do not stack new flowers on top of visible old flower residue; the flower layer
owns these pixels.
```

Use policy: local_redraw with target-aware child masks.

### Yellow Dandelion Detail Prompt

```text
Reconstruct only the yellow dandelion or buttercup flower heads inside the
transparent mask.

Paint exactly {head_count} separated yellow flower head{plural_suffix}. Match
the original head size, footprint, and spacing. Use warm yellow petals with
slightly deeper centers and natural edge softness.
Do not add extra heads. Do not repaint hedge texture, grass, stems, guardrail,
vehicles, sky, road, or any broad background area.
Do not create a whole roadside scene, thumbnail, sticker sheet, black
background, or rectangular patch.
```

Use policy: local_redraw with target-aware child masks and yellow palette gates.

### Dry Stem Detail Prompt

```text
Reconstruct only the thin dry foreground stems and small branch lines.

Preserve the source position, direction, taper, and overlap relationship with
flowers and hedge. Render as delicate natural line details with transparent
surrounding pixels.
Do not include flower heads, leaves, sky, vehicles, guardrail, or broad hedge
texture.
```

Use policy: preserve first. Reconstruct only if line masks are reliable.

### Negative Prompt Block

Append this block when a provider tends to leak scene content:

```text
Forbidden: black background, gray background, rectangular thumbnail, full scene,
roadside panorama, car, truck, guardrail, sky, road, hedge, grass, tree, stems,
extra flowers, sticker sheet, poster, text, watermark, logo, frame, border.
Only include the requested layer.
```

For layer prompts, remove terms from the forbidden list when they are the
requested layer. For example, do not forbid `guardrail` in the guardrail prompt.

## Product API Shape

The eventual API should be a new workflow above individual redraw:

```python
result = await source_layered_generate(
    source_image="source.png",
    layer_contract="roadside_source_layered_generation_v0_24",
    control_masks="curated_masks/",
    policies={
        "background.sky.clean_blue": "reconstruct",
        "foreground.guardrail": "reconstruct",
        "detail.white_flower_cluster": "local_redraw",
        "detail.yellow_dandelion_heads": "local_redraw",
        "foreground.hedge_bush": "preserve",
    },
    provider="openai",
    model="gpt-image-2",
    max_cost_usd=1.50,
)
```

This should not replace `redraw_layer` or `decompose`. It should call
`redraw_layer` for layers whose policy is `local_redraw`, use mask-aware
provider edits for larger generated semantic layers, and treat decompose/split
outputs only as optional sources of control masks.

## Quality Gates

Layered reconstruction needs gates at two levels.

### Per-layer Gates

- Alpha is non-empty and not a full rectangle unless the layer is a background.
- Output bbox is close to mask bbox.
- Outside-mask color drift stays below threshold.
- No black or dark fill artifacts unless the source layer is actually dark.
- No forbidden semantic content for that layer.
- Crop edge seams are below threshold after pasteback.
- For small botanical details, generated head count is close to expected count.
- For broad layers, texture frequency must not become noisy or blocky.

### Full-composite Gates

- No visible holes after residual layer fill.
- Detail layers are not duplicated in parent broad layers.
- Z-order is visually coherent: sky behind trees, trees behind vehicles,
  guardrail in front of or behind objects according to source, flowers in front
  of hedge.
- Composite preserves source layout unless user requests redesign.
- Before/after preview shows style improvement without object identity loss.

## Evaluation Targets

The first prototype should produce these artifacts:

- `layer_plan.json`
- `manifest.json`
- per-layer `input.png`
- per-layer `mask.png`
- per-layer `raw.png`
- per-layer `patch.png`
- per-layer `pasteback.png`
- full `source_pasteback.png`
- full `layered_composite.png`
- `summary.json` with usage, cost, layer policies, failures, and gate results
- focused before/after crops for the flowers, guardrail, and vehicle zone

## MVP Sequence

1. Write this design and review it.
2. Create an implementation plan before code changes.
3. Prototype outside the repo artifact path on the current roadside source.
4. Start with four active layers: sky, guardrail, white flowers, yellow flowers.
5. Preserve hedge, grass, trees, vehicles, and residual as source layers.
6. Add mask ownership subtraction so flower pixels are removed from the hedge
   base before compositing.
7. Evaluate whether old flower residue disappears.
8. Only then consider reconstructing vehicle or tree layers.

## Success Criteria

The workflow is successful when:

- The full preview looks like a deliberate stylized reconstruction, not a set
  of pasted local edits.
- Old white/yellow flower residue is not visible under regenerated flower
  heads at 2x zoom.
- Layer outputs are separately useful: sky can be hidden, guardrail can be
  replaced, flowers can be regenerated without touching the car.
- Broad hedge texture is either cleanly preserved or explicitly refused, not
  silently degraded.
- `summary.json` makes cost, failures, and skipped layers auditable.

## Implementation Starting Point

The first implementation plan should start with existing or hand-curated
control masks for the current roadside image. These masks are not the product
output and should not be treated as a `decompose` result. The visual question is
whether source-conditioned generated layers plus ownership subtraction produce
a better editable composite.

A general planner pass can come after the prototype proves that subtracting
detail layers from broad parent layers removes old-source residue and produces a
better editable composite.
