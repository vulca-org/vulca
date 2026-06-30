# 3D Vector Technical Aesthetics - Stage 02 Direction Handoff

## Design Read

Reading this as a continuation handoff for a code-native creative-coding stage product for Xiaohongshu design/front-end viewers, with a contemporary 3D vector, shader, typography, and inspection-system language.

- Design variance: 8
- Motion intensity: 8
- Visual density: 3
- Product mode: interactive single-file HTML first, horizontal MP4 second
- Visual baseline: Stage 01 already established the atlas overview. Stage 02 should focus on one stronger interaction grammar instead of another broad collage.

## Baseline Constraints

- Output should remain horizontal and clear enough for posting.
- Final interaction recordings should use real pointer movement through `capture=1` and `scripts/record_vector_stage_live.py`.
- Narration voice should keep the Xiaoxiao curator direction, preferably `zh-CN-XiaoxiaoNeural`.
- Subtitle segments and spoken audio must come from the same source text.
- XHS narration should only cover the visible effect, the next continuation step, and future planning.
- Chinese copy should avoid `不是`, `而是`, `AI 式`, and `反转句`.
- Generated MP4 files stay under `output/video/` and remain ignored unless a separate release decision says otherwise.

## Direction 1: Scan Typography Field

Recommended for Stage 02.

Source cases:

- `webgpu-scanning-depth-maps`
- `webgpu-gommage-msdf-dissolve`
- `interactive-text-destruction-webgpu-tsl`
- `countertype-three-text`

Primitive stack:

- Synthetic depth-dot field
- Vertical or radial scan band
- Readable 3D typography
- Glyph fragments, dust samples, and recovery traces
- Pointer-driven inspection pressure

Product mechanic:

The stage opens with a readable word or short phrase as the stable claim state. Real pointer movement pushes a scan band through the type. The scan reveals depth-coded dots, breaks the active edge into fragments, then lets the text recover into a readable state. The visual should feel like an inspection tool becoming a typographic artwork.

Interaction model:

- Pointer position controls scan center, scan pressure, and fragment displacement.
- Pointer down increases disruption.
- Pointer release triggers recovery.
- `record=1` can still produce deterministic preview motion, but `capture=1` is the publication path.

XHS narration shape:

1. Show the effect: scan band, depth dots, readable text, fragment recovery.
2. Continue the database work: add more typography and shader references.
3. Future plan: turn the primitive into a reusable interaction module and tutorial.

Risks and gates:

- The word must remain readable after disruption.
- The scan field must look spatial, not like flat blinking particles.
- The pointer interaction must be visible in a still frame and obvious in motion.
- Reduced-motion mode should preserve one static scan midpoint.

Why this direction:

Stage 01 was an atlas view. This direction turns the atlas into a single teachable mechanic with a clearer video hook, stronger pointer interaction, and a direct path to tutorial content.

## Direction 2: Particle Reasoning Tunnel

Source cases:

- `matrix-sentinels-particle-trails-tsl`
- `makio-meshline`
- `codrops-threejs-meshline-family`
- `maxime-heckel-tsl-webgpu-guide`

Primitive stack:

- Sentinel heads
- History-buffer trail slices
- Thick route curves
- Data tunnel scaffold
- Shader-node side channel

Product mechanic:

The stage becomes a forward-moving tunnel. Several active particles carry claim states through route curves. Behind each head, history slices show memory and direction. A small shader-node strip can pulse along the side to show how the material system controls confidence, speed, and color.

Interaction model:

- Pointer bends route families and changes flow pressure.
- Pointer down freezes one route and expands its history slices.
- Pointer release restarts the tunnel flow.

XHS narration shape:

1. Show the effect: particle heads, history trails, route tunnel, shader pulse.
2. Continue the database work: add more data tunnel and route-sculpture cases.
3. Future plan: use it for claim paths, evidence memory, and source-trail visualizations.

Risks and gates:

- The result must avoid generic particle-sparkle behavior.
- Head, history, route, and flow layers need to be visually separable.
- Motion should communicate temporal state, not only ambience.

Why this direction:

It extends the strongest Stage 01 motion family and maps cleanly to VULCA's evidence-routing story.

## Direction 3: Spatial Type Interface

Source cases:

- `countertype-three-text`
- `spline-contemporary-3d-web`
- `phantom-land-interactive-grid`
- `false-earth-webgpu-world`

Primitive stack:

- Floating interface panels
- 3D glyph rails
- Geometry-cache cells
- Distorted wire grid
- Hotspot and state-track markers

Product mechanic:

The stage behaves like a spatial control surface. Text becomes geometry, panels carry short evidence states, and the grid bends under pointer pressure. The composition should look like a creative coding tool surfaced as an artwork, with less particle density and more object clarity.

Interaction model:

- Pointer bends grid cells and pulls panel layers forward.
- Pointer down toggles a cache-state overlay.
- Pointer release settles the panels back into a clean stage.

XHS narration shape:

1. Show the effect: spatial typography, floating panels, grid pressure.
2. Continue the database work: collect more type-engine and interface-sculpture references.
3. Future plan: turn these controls into a design system for future creative-code pieces.

Risks and gates:

- The surface must feel like an interactive artwork, not a dashboard.
- Panels should not become fake product screenshots.
- The typographic layer must stay legible in horizontal video.

Why this direction:

It gives the project a product-interface branch, useful when the series needs to connect visual experiments back to VULCA's actual software direction.

## Recommended Next Build

Build Direction 1 first as `docs/product/experiments/3d-vector-aesthetic-stage-02/index.html`.

Implementation outline:

1. Create a single-file canvas HTML with `record=1` deterministic preview and `capture=1` real pointer capture.
2. Reuse the existing video builder structure, but change the source HTML and narration segments for Stage 02.
3. Add tests for self-contained HTML, source-case references, real pointer capture, Xiaoxiao narration, and banned Chinese copy tokens.
4. Validate with browser screenshot checks at 1920x1080 and a mobile-safe crop preview.
5. Generate a horizontal preview MP4 only after the HTML passes visual and structural checks.

Definition of ready:

- The HTML works when opened directly or served locally.
- The live recording path uses real pointer events.
- The video can be produced from the same narration segments used for subtitles.
- The still frame communicates scan, depth, type, and recovery without requiring an explanation.
