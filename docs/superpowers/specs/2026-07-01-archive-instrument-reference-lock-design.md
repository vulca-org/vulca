# Archive Instrument Reference Lock Design

**Status:** draft for user review
**Date:** 2026-07-01
**Decision:** create a reference-lock review page for the existing Archive Instrument direction before the next visual implementation pass.
**Follow-up:** after review approval, create an implementation plan for the reference-lock page and then implement it under `docs/product/experiments/`.

## Context

The project direction is already set: a central scroll-driven 3D object that reads as a realistic preserved root specimen inside a high-end instrument or museum vitrine. The current problem is not direction selection. The problem is that implementation has been moving directly from concept to Three.js patches, so each iteration relies too much on local taste adjustment.

The next step should lock visual references, borrowing rules, and rejection rules before another code pass. This avoids continuing the loop:

```text
concept direction -> direct code patch -> still ugly -> local material/color tweaks
```

The desired loop is:

```text
concept direction -> reference lock -> shot/material/state criteria -> implementation -> browser review
```

## Goal

Build one review page that turns the agreed direction into a visible quality gate. The page should help the user and Codex answer:

- Which references define the quality line?
- What exactly do we borrow from each reference?
- What must we avoid copying or repeating?
- Why is the current prototype still below the line?
- What are the next five visual changes for the Archive Instrument prototype?

## Recommended Approach

Create a separate page:

```text
docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html
```

and, if useful, a small adjacent JSON file for structured reference data:

```text
docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock.json
```

This page should not replace the current prototype. It should sit next to it as the review gate for the next implementation pass.

## Alternatives Considered

### A. Add reference notes into the current prototype

This is fast, but it pollutes the prototype with explanation. The prototype should stay focused on the central visual object and scroll states.

### B. Create a separate reference-lock page

This is the recommended option. It creates a dedicated place for source references, borrowing rules, current-prototype diagnosis, and next-pass criteria without making the prototype page heavier.

### C. Build three new A/B/C visual prototypes immediately

This may be useful later, but it is premature. Without a reference lock, the variants would likely repeat the same local-polish problem under three names.

## Page Structure

The reference-lock page should have five sections.

### 1. Direction Statement

Short, non-marketing statement:

```text
Archive Instrument = realistic preserved specimen + luxury instrument object + restrained scientific inspection.
```

The page should explicitly state that the direction is not changing.

### 2. Reference Matrix

Six to eight reference cards. Each card should contain:

- reference label
- source type: website, demo, product reference, museum/science reference, generated reference image, or local prototype
- what to borrow
- what not to copy
- related dimension: glass, specimen, plinth, lighting, scanning, sectioning, annotation, composition
- confidence: high, medium, low

The first version can use existing local reference seeds plus a small number of newly researched current references. It should prefer current official pages, project pages, or source pages over generic image search where possible.

### 3. Current Prototype Diagnosis

Use the current Archive Instrument prototype as the baseline. The diagnosis should be direct:

- improved: central object, warmer materiality, four-state logic, less abstract roots
- still weak: real-world specimen fidelity, glass thickness, bottom support readability, reference-level lighting, lack of high-quality model/texture assets
- risk: continuing to polish procedural shapes instead of introducing better model, texture, or reference-image workflows

### 4. Visual Criteria For Next Pass

Five criteria for deciding whether the next implementation is better:

1. The specimen reads as a real object before reading as a diagram.
2. The glass reads as a vitrine or wet-specimen container, not a transparent UI shell.
3. The root and support geometry cannot be mistaken for legs or random lines.
4. Each scroll state changes inspection logic, not just position or opacity.
5. The palette has warm material contrast and does not collapse into gray-green technical UI.

### 5. Next-Pass Candidate Moves

The page should end with a prioritized action list:

1. replace or supplement procedural plant geometry with a better modeled or generated specimen asset
2. rebuild glass as a believable thick container with edge highlights and refraction cues
3. define one strong hero camera and only modest scroll-state camera changes
4. reduce annotation density and make scan/section states behave like instrument modes
5. add screenshot-based browser review checkpoints for mobile and desktop

## Data And Implementation Notes

The page can start as a static HTML review artifact using the project's current experiment style. It does not need a framework or runtime build. It should include links back to:

- `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html`
- `docs/product/experiments/3d-vector-aesthetic-stage-02-reference-board/index.html`
- `docs/product/experiments/3d-vector-aesthetic-stage-02-reference-discovery.md`

If external references are added, the page should store enough metadata to explain why they are used. It should not copy protected source assets or claim rights to third-party media.

## Testing And Review

Verification should include:

- source tests that assert the page exists and links to the prototype, reference board, and reference discovery document
- assertions for the five visual criteria strings
- browser review at the current in-app page server URL
- at least one desktop screenshot and one narrow screenshot
- console log check for warnings/errors

## Non-Goals

- Do not redesign the current prototype in this step.
- Do not create another abstract concept board.
- Do not create a bulk moodboard or crawler.
- Do not copy a reference site's proprietary 3D model, code, or brand language.
- Do not treat the reference-lock page as final product UI.

## Open Questions

- Which external references are acceptable to include as linked references in the first pass?
- Should the first version include generated reference images as internal visual targets, or only web/project references?
- Should the next implementation pass introduce an external GLB/model pipeline, or continue with procedural Three.js for one more round?
