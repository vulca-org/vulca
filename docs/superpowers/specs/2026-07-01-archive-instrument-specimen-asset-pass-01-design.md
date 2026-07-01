# Archive Instrument Specimen Asset Pass 01 Design

**Status:** draft for user review
**Date:** 2026-07-01
**Decision:** create a separate specimen-asset candidate page before replacing the current Archive Instrument prototype asset.
**Follow-up:** after review approval, create an implementation plan for the candidate page and then implement it under `docs/product/experiments/`.

## Context

The Archive Instrument direction is locked:

```text
realistic preserved specimen + luxury instrument object + restrained scientific inspection
```

The reference-lock page identifies the main gap: the current prototype is directionally useful, but the central specimen still reads as procedural geometry before it reads as a real preserved object. The next pass should therefore not start with glass, lighting, or scroll-state tuning. It should first improve the asset basis of the object at the center.

The current prototype builds the specimen inside `createCoreLayer()` and `createRootRouteLayer()` with procedural stem tubes, leaf shapes, pebbles, wires, and root routes. This is fast and controllable, but it has reached the limit of local material tweaks. The next pass should test a stronger specimen asset while keeping the existing prototype intact as a baseline.

## Goal

Build one candidate page for `Specimen Asset Pass 01` that answers a single question:

```text
Does the central specimen read as a preserved real object before it reads as a diagram?
```

The page should compare the current asset logic against one improved specimen candidate in a controlled presentation. It should not redesign the full Archive Instrument page.

## Recommended Approach

Create a separate static Three.js candidate page:

```text
docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01/index.html
```

and a small adjacent JSON contract:

```text
docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01.json
```

The page should render a single upgraded preserved-root specimen inside a minimal neutral inspection frame. It should include a compact side panel or footer that compares the candidate against the current prototype using the five reference-lock criteria. The current prototype should be linked, not modified.

## Alternatives Considered

### A. Continue polishing the current procedural specimen in place

This is fast, but it repeats the problem identified by the reference lock. The current page already has several incremental realism commits. More local tweaks are likely to produce diminishing returns.

### B. Build a separate procedural specimen candidate

This is the recommended first pass. It keeps control inside Three.js, avoids external asset pipeline risk, and allows the candidate to focus on form, silhouette, and material hierarchy. If it succeeds visually, the upgraded asset can later be merged into the main prototype.

### C. Start with a generated GLB or external model pipeline

This may be necessary later, but it is not the first implementation pass. A GLB pipeline adds tool selection, generation quality, cleanup, license, file-size, and loading concerns. The first pass should define the desired specimen anatomy and visual standard before committing to external model generation.

## Specimen Candidate Design

The candidate should be a preserved botanical cutting with visible root logic:

- asymmetric woody stem with subtle taper, knots, scars, and bark rings
- 5 to 7 leaves with varied size, age, bend, pitch, and yaw
- leaves should look attached by petioles, not pasted to the stem
- small root crown or soil plug at the base, with roots emerging from believable sockets
- fine roots and root hairs should be short, branching, and biologically subordinate
- support wires should read as specimen mounting, not as legs
- warm brown, olive, pale vein, and amber material accents should replace gray-green flatness

The specimen should be denser than the current asset, but not decorative. The first read should be:

```text
preserved organic sample
```

not:

```text
plant icon
wireframe diagram
random tubes
technical toy
```

## Page Structure

The candidate page should have four sections.

### 1. Candidate View

Full first viewport with the candidate specimen centered. The background should stay quiet and dark, but the specimen should have enough warm light and edge contrast to be judged.

### 2. Anatomy Tags

Small labels or a compact legend should identify only the asset parts:

- woody stem
- leaf cluster
- petiole
- root crown
- fine roots
- mounting wire

Labels must not dominate the image. They are for review, not decoration.

### 3. Criteria Check

Render the five reference-lock criteria as a checklist, with the first criterion emphasized:

```text
The specimen reads as a real object before reading as a diagram.
```

The page should make it easy to compare the candidate against the existing prototype, but it should not embed a second live prototype scene.

### 4. Handoff Notes

The page should end with a short handoff note:

- if accepted, merge candidate anatomy into the main Archive Instrument prototype
- if still weak, move to generated GLB or modeled-asset exploration
- keep glass/instrument/scroll-state changes for later passes

## Implementation Constraints

- Do not modify `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html` in this pass.
- Do not add external paid assets or copied third-party imagery.
- Do not depend on a network model file for the candidate page.
- Use Three.js from the same CDN pattern as the current prototype.
- Keep generated geometry deterministic so tests and visual review are reproducible.
- Keep the candidate page visually quiet: no hero marketing layout, no decorative blobs, no generic particle show.
- If the candidate uses helper functions, keep them scoped to the candidate page unless a later pass extracts shared modules.

## Testing And Review

Verification should include:

- source tests that assert the candidate page and JSON exist
- assertions that the page links to the current prototype and reference-lock page
- assertions for the required specimen anatomy strings
- assertions for the five reference-lock criteria
- browser review at desktop and narrow viewport
- console log check for warnings/errors
- visual review notes answering whether the candidate beats the current specimen asset

## Non-Goals

- Do not replace the current Archive Instrument prototype yet.
- Do not redesign glass, plinth, lighting system, or scroll-state choreography.
- Do not build the full GLB/model-generation pipeline in this pass.
- Do not create multiple visual directions or another broad reference board.
- Do not solve annotation, scan, or section logic beyond showing how the asset parts would support later passes.

## Acceptance Criteria

The pass is successful only if the candidate is visibly stronger than the current specimen asset on the first reference-lock criterion:

```text
The specimen reads as a real object before reading as a diagram.
```

Secondary success criteria:

- roots no longer read as legs
- leaves have credible attachment and orientation
- root crown feels physically connected to the stem
- material palette is warmer and less gray-green
- the candidate can be moved into the current prototype without changing the direction

## Open Questions

- Should the candidate page include a generated reference image slot later, or keep Pass 01 purely procedural?
- If the candidate still feels weak after browser review, should Pass 02 go directly to GLB/model generation?
- Should the accepted asset become a reusable helper module, or remain inline until the full prototype stabilizes?
