# 3D Vector Technical Aesthetics Learning DB Design

**Status:** draft for user review
**Date:** 2026-06-29
**Decision:** build a small, high-dimensional, multimodal learning corpus for 2025+ browser-native 3D vector technical aesthetics before building the final creative-coding prototype.
**Follow-up:** after review approval, create an implementation plan at `docs/superpowers/plans/2026-06-29-3d-vector-aesthetics-learning-db.md`.

## Context

The target is not retro plotter art, ordinary SVG illustration, a static moodboard, or a broad WebGL effects scrape. The target is a contemporary creative-coding aesthetic:

```text
browser-native
interactive
code-generated
2025+ or still-current
3D vector / line / typography / spatial technical systems
usable as a learning path for a later VULCA-flavored artwork
```

Relevant visual families include meshline route sculptures, 3D typography, scan planes, data tunnels, wire grids, particle-vector hybrids, and technical UI sculptures. The database must teach how these works are built. A screenshot gallery is insufficient because many references are defined by motion, interaction, source code, shader behavior, model/font assets, and browser/runtime constraints.

## Product Thesis

The database should be an `Archive + Lab + Course` system:

```text
Archive: preserve provenance, captures, links, and source status.
Lab: expose technique anatomy, implementation risks, and reproducibility.
Course: turn references into primitives, techniques, and rebuild exercises.
```

The core output is a curated learning corpus plus local HTML review pages. The corpus should support the user in deciding which technical aesthetic should become the eventual interactive creative-coding piece.

## Non-Goals

- Do not build a bulk crawler for arbitrary Awwwards, Behance, or social media results.
- Do not archive commercial source code, private assets, paid 3D models, fonts, or textures without explicit permission.
- Do not treat screenshots as sufficient evidence for motion or interaction-heavy work.
- Do not copy a reference project's brand language, models, shaders, or implementation wholesale.
- Do not start building the final artwork until the corpus has produced a shortlist and learning path.
- Do not force every visual family into one flat schema with hundreds of empty columns.

## Professional Reference Models

No single existing database matches this use case. The design borrows patterns from several mature systems:

| Reference model | What to borrow | What not to borrow |
|---|---|---|
| Shadertoy | code-as-art indexing, shader source, author metadata, runtime preview | shader-only scope |
| OpenProcessing | creative coding sketches, remix-oriented learning, source visibility | 2D sketch community bias |
| Art Blocks | deterministic generative traits, script/dependency metadata, output variation thinking | NFT-specific market framing |
| Rhizome ArtBase | digital artwork preservation, provenance, external links, documentation depth | museum archive overhead for v0.1 |
| Rive | interaction state-machine thinking for motion | proprietary editor dependence |
| Lottie | layer/timeline/vector animation structure | 2D animation-only assumptions |
| Storybook | component-like review surfaces and controls | component-library framing |
| Playwright Trace Viewer | screenshots, filmstrip, interaction/event trace thinking | debug-tool UI as final UX |

The VULCA corpus combines these into a cross-media learning database for 3D vector technical aesthetics.

## Core Architecture

The data model must solve the object-difference problem. Meshline, 3D typography, depth scanning, and data tunnel references are visually and technically different, but all can be decomposed into the same learning chain:

```text
Case
  Scene
    Moment
      Primitive
        Technique
          Exercise
```

This is the invariant core. Specialist details live in optional modules.

### Core Entity Definitions

| Entity | Meaning | Required examples |
|---|---|---|
| `Case` | One reference project, tutorial, demo, or product reference | Makio MeshLine, WebGPU Gommage, Countertype three-text |
| `Scene` | A distinct state or page within the case | idle hero, detail mode, text dissolve scene |
| `Moment` | A time-bound interaction or motion event | hover trail, click explode, scroll scan |
| `Primitive` | A reusable aesthetic/technical building block | thick 3D line, MSDF glyph, scan plane, data tunnel segment |
| `Technique` | The implementation mechanism behind a primitive | TSL noise mask, instancing, CatmullRom curve, render target |
| `Exercise` | A minimal rebuild task for learning | animate 12 route nodes with a dashed meshline reveal |

Every reviewed case must have at least one `Primitive`, one `Technique`, and one `Exercise`. A case that cannot produce a primitive or exercise is only a mood reference and should not enter the learning shortlist.

## Layered Schema

The design rule is:

```text
core layer unified
specialist layer sparse
review layer shows gaps
learning layer connects by primitive
```

### Core Layer

Core fields exist for every case:

```text
id
title
canonical_url
source_type: demo | github | tutorial | case_study | product_ref | documentation
year
author_or_studio
currentness: 2025_plus | still_current | historical_reference
summary
why_relevant
review_status: candidate | shortlist | needs_deeper_review | metadata_only | rejected
quality_score_total
created_at
updated_at
```

Required relational anchors:

```text
case_id
scene_id
moment_id
primitive_id
technique_id
exercise_id
```

### Specialist Layer

Specialist data is stored as sparse module payloads. A case may have one or more modules. Missing unrelated modules are not a defect.

Module types:

```text
meshline
typography_3d
scan_depth
data_tunnel
wire_grid
particle_vector
ui_sculpture
shader_material
interaction_state
asset_pipeline
performance_runtime
vulca_translation
```

Each module payload has:

```text
module_type
payload_json
evidence_refs
confidence: high | medium | low
review_status: complete | partial | missing | not_applicable
review_notes
```

#### Meshline Module

Use for thick 3D lines, ribbons, trails, routes, paths, or data links.

```json
{
  "path_source": "curve_points | graph_edges | pointer_trail | generated_noise | unknown",
  "line_form": "thick_ribbon | tube | dashed_route | glowing_path | contour_stack",
  "material": ["gradient", "dash", "emissive", "matte", "transparent"],
  "animation": ["trail_reveal", "flowing_dash", "pointer_distortion", "route_rebuild"],
  "spatial_role": "route | sculpture | boundary | graph_edge | orbit",
  "learning_primitive": "animated 3D route line"
}
```

#### 3D Typography Module

Use for spatial text, glyph geometry, MSDF text, text particles, or kinetic technical labels.

```json
{
  "font_pipeline": "MSDF | text_geometry | three_text | troika | browser_font | unknown",
  "glyph_mode": "solid_mesh | surface_shader | particles | fragments | labels",
  "layout": "word_sculpture | field_labels | centered_title | data_annotation",
  "motion": ["dissolve", "explode", "rebuild", "scan", "orbit"],
  "language_support": "latin | cjk | rtl | mixed | unknown",
  "learning_primitive": "interactive 3D technical label"
}
```

#### Scan Depth Module

Use for depth-map reveal, x-ray scanning, slices, technical sweeps, or inspection planes.

```json
{
  "depth_source": "depth_map | mesh_z | generated_field | render_target | unknown",
  "scan_axis": "x | y | z | camera_space | radial | unknown",
  "reveal_logic": "shader_threshold | clipping_plane | mask_texture | particle_gate",
  "visual_effect": ["xray", "technical_sweep", "occlusion_reveal", "slice"],
  "learning_primitive": "review scan plane"
}
```

#### Data Tunnel Module

Use for spatial routes, tunnels, infinite paths, graph corridors, or source-trail travel.

```json
{
  "topology": "tunnel | corridor | radial_graph | branching_path | helix | unknown",
  "camera_model": "flythrough | orbit | fixed_depth | scroll_bound | pointer_bound",
  "route_logic": "source_to_target | timeline | graph_walk | random_walk | unknown",
  "density_strategy": "sparse_nodes | layered_grids | particle_stream | line_field",
  "learning_primitive": "navigable source trail"
}
```

#### Interaction State Module

Use for interaction semantics independent of visual family.

```json
{
  "inputs": ["pointer", "click", "drag", "scroll", "keyboard", "touch", "audio", "parameter_panel"],
  "state_model": "continuous | finite_state_machine | timeline | physics | shader_uniforms",
  "feedback_latency": "instant | eased | delayed | autonomous",
  "user_agency": "observe | perturb | select | navigate | compose",
  "learning_primitive": "interaction-driven aesthetic state"
}
```

#### Shader Material Module

Use for TSL, GLSL, WGSL, material-node, postprocessing, and render-target behavior.

```json
{
  "shader_system": "TSL | GLSL | WGSL | node_material | built_in_material | unknown",
  "driver_uniforms": ["time", "pointer", "scroll", "audio", "progress"],
  "rendering_technique": ["postprocess", "render_target", "mrt", "compute", "storage_buffer", "instancing"],
  "material_effect": ["bloom", "dissolve", "scan", "emissive_line", "holographic", "depth_fade"],
  "fallback_risk": "low | medium | high | unknown",
  "learning_primitive": "shader-driven technical surface"
}
```

#### Asset Pipeline Module

Use for fonts, MSDF atlases, GLB/GLTF models, textures, depth maps, generated geometry, and source assets.

```json
{
  "asset_types": ["font", "msdf_atlas", "glb", "gltf", "texture", "depth_map", "svg_path", "generated_geometry"],
  "asset_origin": "open_source | commercial | project_specific | generated | unknown",
  "local_archive_policy": "archive_allowed | metadata_only | source_link_only",
  "rebuild_dependency": "required | optional | replaceable | unknown",
  "rights_notes": "short source/rights summary",
  "learning_primitive": "asset-to-geometry pipeline"
}
```

#### Performance Runtime Module

Use for runtime feasibility, browser compatibility, and performance constraints.

```json
{
  "renderer": "WebGPU | WebGL2 | WebGL1 | SVG | Canvas2D | unknown",
  "fallback": "webgl2 | static_capture | unsupported | unknown",
  "device_risk": "desktop_only | mobile_risky | broadly_safe | unknown",
  "observed_runtime": "smooth | intermittent | slow | not_tested",
  "known_constraints": ["vertex_count", "draw_calls", "video_texture", "shader_compile", "mobile_safari"],
  "learning_primitive": "performance-aware interactive scene"
}
```

#### VULCA Translation Module

Use for mapping a reference into VULCA-specific creative vocabulary.

```json
{
  "source_trail": "yes | no | partial",
  "evidence_layer": "yes | no | partial",
  "review_gap": "yes | no | partial",
  "route_decision": "yes | no | partial",
  "uncertainty": "yes | no | partial",
  "what_to_borrow": ["interaction mechanism", "motion grammar", "rendering technique"],
  "do_not_copy": ["brand-specific form", "proprietary asset", "surface style without mechanism"],
  "learning_primitive": "VULCA aesthetic transfer"
}
```

## Evidence Layer

The corpus is multimodal. Each case can have screenshots, videos, traces, code notes, asset manifests, and anatomy notes.

Filesystem layout:

```text
data/vector-aesthetics/
  references.sqlite
  cases/
    <case_id>/
      metadata.json
      screenshots/
        desktop_idle.png
        desktop_interaction.png
        detail_material.png
        mobile.png
      videos/
        idle_loop.mp4
        hover_interaction.mp4
        click_or_scroll.mp4
      traces/
        playwright_trace.zip
        interaction_log.json
      code/
        repo_snapshot_notes.md
        package_summary.json
        shader_file_index.json
      assets/
        asset_manifest.json
      anatomy.md
      lesson.md
      vulca_translation.md
```

Capture levels:

| Level | Name | Required evidence |
|---|---|---|
| 0 | metadata only | title, URL, author/studio, year/currentness, source type |
| 1 | visual snapshot | 2-4 screenshots, viewport metadata |
| 2 | motion capture | 8-20 second muted video or interaction clip |
| 3 | technical read | README/package/source summary, stack, core files, shader/model/font signals |
| 4 | reproducibility | local-run notes or minimal rebuild exercise with verified dependencies |

v0.1 target:

```text
12 cases total
12 cases at Level 2 or better
6 cases at Level 3 or better
3 cases at Level 4 or better
```

### Evidence Record Fields

```text
id
case_id
evidence_type: screenshot | video | trace | code_note | asset_manifest | external_doc
path_or_url
capture_method: playwright | manual_browser | downloaded_metadata | source_read | user_supplied
viewport
interaction
captured_at
source_url
confidence: high | medium | low
rights_status: local_capture | source_link_only | open_asset | unclear
notes
```

## Learning Layer

Each shortlisted case must produce a lesson card:

```text
lesson_goal
why_it_matters
required_concepts
primitive_to_learn
minimal_rebuild_exercise
difficulty: 1 | 2 | 3 | 4 | 5
time_estimate
implementation_recipe
common_failure_modes
vulca_translation
```

Example:

```text
lesson_goal: Build a 3D source route as a living meshline.
required_concepts: CatmullRomCurve3, wide-line mesh material, dash animation, pointer raycast.
minimal_rebuild_exercise: Render 12 nodes connected by animated thick lines in 3D space.
difficulty: 3
time_estimate: 2-4 hours for a focused prototype.
vulca_translation: source trail, evidence route, owner handoff.
```

Learning paths are primitive-first rather than project-first:

```text
Path A: 3D Vector Route
  1. draw 3D polyline
  2. turn line into thick meshline
  3. add gradient and dash
  4. animate trail reveal
  5. attach labels to route nodes
  6. add pointer distortion
  7. translate to VULCA source trail

Path B: Technical Typography Sculpture
  1. load font or MSDF glyphs
  2. place text in 3D space
  3. convert glyphs into particles or fragments
  4. animate dissolve, explode, or rebuild
  5. bind interaction state
  6. translate to VULCA evidence labels

Path C: Review Scan Plane
  1. create a depth or scalar field
  2. render a moving scan threshold
  3. reveal hidden geometry or labels
  4. add uncertainty bands
  5. translate to VULCA review gap inspection
```

### Exercise Runtime Boundary

The v0.1 corpus can describe exercises before it executes them. A case reaches Level 4 only when the
exercise has a concrete runtime target:

```text
runtime_target: static_note | local_vite_three | local_r3f | local_canvas | external_demo_only
verified_status: described | scaffolded | runs_locally | blocked
verification_command: exact command or "none"
```

`Archive + Lab + Course` is therefore staged:

```text
Archive: required in v0.1
Course: required for shortlisted cases in v0.1
Lab: starts as runnable exercises for the 3 Level-4 cases, not for every reference
```

The implementation plan should not promise a full live-code environment for every case. The first
runtime path should be a small local Vite + Three.js/WebGPU or Three.js/WebGL2 sandbox only for the
selected rebuild exercises.

## Quality And Review Model

Each case receives six 0-3 scores:

| Score | Meaning |
|---|---|
| `aesthetic_relevance` | fits 2025+ 3D vector technical aesthetics |
| `technical_learnability` | reveals concrete implementation mechanisms |
| `multimodal_completeness` | has enough still, motion, code, and asset evidence |
| `interaction_clarity` | interaction model is legible and reviewable |
| `vulca_transfer_value` | can translate into source, evidence, gap, route, layer, or uncertainty primitives |
| `license_safety` | source/asset rights are clear enough for the intended use |

Decision bands:

```text
16-18: shortlist
12-15: needs deeper review
8-11: metadata only or weak candidate
0-7: reject
```

Any case with unclear licensing can still be studied as `metadata_only`, but it cannot be used as a direct implementation source.

### Coverage Matrix

The HTML review page must expose research completeness:

```text
metadata: complete | partial | missing
screenshots: complete | partial | missing
video: complete | partial | missing
trace: complete | partial | missing | not_applicable
code_anatomy: complete | partial | missing
asset_manifest: complete | partial | missing | not_applicable
license_review: clear | unclear | restricted
lesson: complete | draft | missing
vulca_translation: complete | needs_review | missing
```

This prevents a visually attractive reference from being mistaken for a technically useful case.

## HTML Review Experience

The review output should live under:

```text
output/review/3d-vector-aesthetics-learning-db/
  index.html
  assets/
  data/
```

Design read:

```text
internal research atlas for creative technologists, with a precise contemporary technical-aesthetic language, leaning toward a dense but readable dark technical review surface.
```

Required views:

| View | Purpose |
|---|---|
| Atlas View | cards with video preview, tags, score, status, and key capture |
| Anatomy View | primitive, technique, asset, motion, and interaction breakdown |
| Compare View | compare two cases by primitive, stack, motion, and transfer value |
| Coverage View | show missing evidence and review depth |
| Lesson Path View | organize exercises by primitive learning sequence |

The review page must not be a landing page. It should behave like a research instrument:

- filter by visual family, stack, interaction, capture level, score, and review status;
- display video clips inline when available;
- show screenshots as supporting evidence, not the primary truth;
- link out to canonical sources and local evidence files;
- display confidence and rights status near every technical claim;
- show `what_to_borrow` and `do_not_copy` side by side.

## Seed Reference Set

v0.1 should start with 12 curated cases. These are seeds; each still needs ingestion and review.

| Case | Primary reason |
|---|---|
| Makio MeshLine | modern 3D wide-line / route primitive |
| Codrops MeshLines bamboooo / venus / ricefield family | 2025 Three.js/WebGPU/TSL line sculptures |
| Interactive Text Destruction with Three.js, WebGPU and TSL | 3D typography destruction/rebuild |
| WebGPU Gommage Effect | MSDF text dissolve into particles/petals |
| WebGPU Scanning Effect with Depth Maps | scan plane and depth reveal |
| Matrix Sentinels | TSL compute-style particle trails |
| Countertype three-text | modern 3D typography pipeline |
| Phantom.land case study | interactive grid and spatial technical surface |
| False Earth | WebGPU-driven world logic and technical atmosphere |
| Spline selected examples | aesthetic reference only; no implementation dependency |
| Three.js WebGPURenderer + TSL docs | technical baseline and fallback risk |
| Maxime Heckel TSL/WebGPU guide | teaching reference for TSL/WebGPU mental model |

Seed source URLs:

| Case | Canonical source URL |
|---|---|
| Makio MeshLine | `https://meshline.makio.io/` and `https://github.com/Makio64/makio-meshline` |
| Codrops Three.js demo family | `https://tympanus.net/codrops/hub/tag/three-js/` |
| Interactive Text Destruction | `https://tympanus.net/codrops/2025/07/22/interactive-text-destruction-with-three-js-webgpu-and-tsl/` |
| WebGPU Gommage Effect | `https://tympanus.net/codrops/2026/01/28/webgpu-gommage-effect-dissolving-msdf-text-into-dust-and-petals-with-three-js-tsl/` |
| WebGPU Scanning Effect | `https://tympanus.net/codrops/2025/03/31/webgpu-scanning-effect-with-depth-maps/` |
| Matrix Sentinels | `https://tympanus.net/codrops/2025/05/05/matrix-sentinels-building-dynamic-particle-trails-with-tsl/` |
| Countertype three-text | `https://countertype.com/` |
| Phantom.land case study | `https://tympanus.net/codrops/2025/06/30/invisible-forces-the-making-of-phantom-lands-interactive-grid-and-3d-face-particle-system/` |
| False Earth | `https://tympanus.net/codrops/2026/04/21/false-earth-from-webgl-limits-to-a-webgpu-driven-world/` |
| Spline | `https://spline.design/` |
| Three.js WebGPURenderer docs | `https://threejs.org/docs/pages/WebGPURenderer.html` |
| Three.js TSL docs | `https://threejs.org/docs/pages/TSL.html` |
| Maxime Heckel TSL/WebGPU guide | `https://blog.maximeheckel.com/posts/field-guide-to-tsl-and-webgpu/` |

## Ingestion Workflow

Each case moves through a controlled ingestion process:

1. Create metadata seed with canonical URL, source type, author/studio, currentness, and expected visual family.
2. Capture screenshots for desktop idle, interaction, material/detail, and mobile when the page supports it.
3. Capture 8-20 seconds of motion for idle and one representative interaction.
4. Read available public technical sources: README, package manifest, tutorial, docs, or case study.
5. Create `anatomy.md` describing scenes, moments, primitives, and techniques.
6. Create `asset_manifest.json` listing fonts, GLB/GLTF, textures, depth maps, shaders, generated geometry, and rights status.
7. Create `lesson.md` with at least one minimal rebuild exercise.
8. Add VULCA translation notes: source trail, evidence layer, review gap, route decision, uncertainty, layer state.
9. Score the case and set `review_status`.
10. Rebuild the HTML review page.

## Rights And Source Policy

The corpus may store:

- local screenshots of publicly visible pages for internal review;
- short interaction captures for internal review;
- metadata, links, and technical notes;
- license summaries and dependency names;
- source file indexes for open repositories;
- local copies of open assets only when the license permits it.

The corpus must not store:

- commercial models, fonts, textures, or source bundles without explicit permission;
- private or authenticated content;
- large mirrored copies of project source when a link and anatomy note are sufficient;
- proprietary shader/model assets extracted from production pages.

If rights are unclear, record:

```text
rights_status: source_link_only
license_safety: 0 or 1
review_status: metadata_only or needs_deeper_review
```

## Data Storage

Use SQLite for structured metadata and local files for multimodal evidence.

Core tables:

```text
cases
scenes
moments
primitives
techniques
exercises
captures
assets
reviews
module_payloads
sources
```

`module_payloads` preserves specialist flexibility:

```text
id
case_id
module_type
payload_json
evidence_refs_json
confidence
review_status
created_at
updated_at
```

The database should export a bounded JSON snapshot for the HTML review page:

```text
output/review/3d-vector-aesthetics-learning-db/data/references.json
```

The HTML page should not query SQLite directly.

### Source Of Truth And Sync

The filesystem case folders are the authoring source of truth. SQLite is a compiled index.

```text
case folders + JSON/Markdown notes
  -> validation step
  -> references.sqlite
  -> bounded review JSON
  -> static HTML review page
```

This avoids dual-maintenance drift. Manual edits should happen in:

```text
data/vector-aesthetics/cases/<case_id>/metadata.json
data/vector-aesthetics/cases/<case_id>/anatomy.md
data/vector-aesthetics/cases/<case_id>/lesson.md
data/vector-aesthetics/cases/<case_id>/vulca_translation.md
```

The implementation plan must include validators for:

- required core fields;
- module payload enum values;
- capture file existence;
- coverage matrix consistency;
- SQLite row count matching the case folder manifest;
- review JSON generation from SQLite.

## Implementation Phases

### Phase 1: Schema And Seed Data

Create the SQLite schema, seed JSON/YAML, and validation checks. Add 12 reference seed records with no misleading completeness claims.

### Phase 2: Capture And Ingestion

Add capture scripts for screenshots and short video clips. Add manual fallback fields for pages that resist automation. Record capture failures as evidence, not as silent omissions.

### Phase 3: Anatomy And Lesson Authoring

Write anatomy and lesson notes for each seed. Promote only cases with useful primitives and exercises into the shortlist.

### Phase 4: HTML Review Atlas

Generate the review page with atlas, anatomy, compare, coverage, and lesson-path views.

### Phase 5: Prototype Direction Handoff

Use the reviewed shortlist to propose 2-3 prototype directions for the eventual VULCA 3D vector artwork.

## Success Criteria

The v0.1 corpus is successful when:

- 12 curated cases exist in the local database.
- every case has metadata, screenshots, and at least one motion capture or explicit capture failure note;
- at least 6 cases have technical anatomy;
- at least 3 cases have rebuild exercises;
- every shortlisted case has VULCA translation notes;
- the HTML review page exposes score, status, coverage, source links, local captures, and lesson paths;
- rights status is visible for every case;
- the user can reject, shortlist, or request deeper review based on evidence rather than memory or taste alone.

## Deferred Decisions

These decisions should be made after v0.1 review:

- whether to add embeddings for visual/code/lesson search;
- whether to add a browser-based annotation editor or keep annotations file-based;
- whether to implement live Storybook-style controls for selected exercises;
- whether to run local rebuild exercises inside the same repo or in a separate creative-coding sandbox.
