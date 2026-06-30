# 3D Vector Technical Aesthetics - Stage 02 Visual Direction Handoff

## Design Read

Reading this as a visual-first creative-coding stage for Xiaohongshu design/front-end viewers. The technical database is already useful; Stage 02 needs a better image: stronger composition, controlled palette, clearer subject, and a more designed first frame.

- Design variance: 8
- Motion intensity: 6
- Visual density: 3
- Product mode: dynamic visual poster HTML first, horizontal MP4 second
- Visual baseline: Stage 01 proved the technical vocabulary, but its screen reads as neon debug spaghetti. Stage 02 should look like a finished visual piece.

## Baseline Constraints

- Output should remain horizontal and clear enough for posting.
- Interaction is optional support only. The main artifact is visualization.
- The first frame must work as a poster without requiring motion or explanation.
- Use fewer colors with stronger hierarchy: one dominant neutral, one cold accent, one warm accent at most.
- Avoid dashboard HUD clutter, tiny telemetry, decorative labels, and fake product panels.
- Narration voice should keep the Xiaoxiao curator direction, preferably `zh-CN-XiaoxiaoNeural`.
- Subtitle segments and spoken audio must come from the same source text.
- XHS narration should only cover the visible effect, the next continuation step, and future planning.
- Generated MP4 files stay under `output/video/` and remain ignored unless a separate release decision says otherwise.

## Visual Problems To Fix From Stage 01

- Too many line families compete for attention.
- The palette uses several saturated neon colors, which makes the work feel like a technical test.
- The typography is present, but it does not own the composition.
- HUD labels and counters make the screen feel like a dashboard.
- The center mass is busy without enough negative space.
- The video hook is technical complexity, not visual beauty.

## Direction 1: Depth Typography Poster

Recommended for Stage 02.

Source cases:

- `webgpu-scanning-depth-maps`
- `webgpu-gommage-msdf-dissolve`
- `countertype-three-text`
- `interactive-text-destruction-webgpu-tsl`

Primitive stack:

- Large readable typography as the visual anchor
- Depth-coded dot field sampled from the typography
- One scan veil or glow plane
- Sparse ribbon accents
- Soft film grain and vignette

Visual mechanic:

The screen is a dynamic poster. A large typographic object sits slightly off-center. Its surface breaks into depth-coded points and fine vector traces, while a slow scan veil passes through it. The composition should feel like a museum-quality technical poster, not a control surface.

Motion role:

- Slow depth shimmer.
- One scan pass.
- Subtle ribbon drift.
- No visible cursor language.

XHS narration shape:

1. Show the effect: large 3D type, depth points, scan veil, restrained vector motion.
2. Continue the database work: add more typography, shader, and scan references.
3. Future plan: turn the best visual primitives into a series of works and tutorials.

Visual gates:

- The poster must read in one still frame.
- The typography must remain legible.
- The palette must stay disciplined and avoid rainbow neon.
- The composition needs negative space around the main mass.

Why this direction:

It directly addresses the user's critique. The technical structure remains, but the visible output becomes a cleaner, more desirable image.

## Direction 2: Mineral Line Sculpture

Source cases:

- `makio-meshline`
- `codrops-threejs-meshline-family`
- `matrix-sentinels-particle-trails-tsl`
- `maxime-heckel-tsl-webgpu-guide`

Primitive stack:

- A small number of thick 3D route curves
- Mineral-toned glow material
- One grounded perspective grid
- A few bright head particles
- A quiet shader-node undertone

Visual mechanic:

Instead of filling the canvas with many trails, this direction treats line work as sculpture. Five to seven carefully weighted routes cross the scene with clear rhythm, negative space, and material depth.

Motion role:

- Slow route breathing.
- Head particles travel along selected curves.
- Grid light shifts gently.

XHS narration shape:

1. Show the effect: sculptural vector routes and mineral glow.
2. Continue the database work: collect more line-sculpture and data-tunnel references.
3. Future plan: use the route language for visual systems and tutorial modules.

Visual gates:

- Fewer, better curves.
- No dense spaghetti field.
- Each line should have material weight, not just stroke color.
- The background must support the sculpture instead of swallowing it.

Why this direction:

It keeps the vector identity of Stage 01 while fixing the biggest visual failure: uncontrolled line density.

## Direction 3: Quiet Interface Still Life

Source cases:

- `spline-contemporary-3d-web`
- `phantom-land-interactive-grid`
- `false-earth-webgpu-world`
- `countertype-three-text`

Primitive stack:

- Floating 3D panels as simple abstract planes
- Type fragments as spatial material
- One deformed grid plane
- Soft depth haze
- Minimal notation, no dashboard counters

Visual mechanic:

The image becomes a still life of interface objects. Panels, glyphs, and grid fragments are arranged like a product photograph of a technical system. It should feel composed and collectible, not operational.

Motion role:

- Slow camera drift.
- Tiny parallax between planes.
- Light haze and shadow movement.

XHS narration shape:

1. Show the effect: abstract interface objects arranged as a visual still life.
2. Continue the database work: collect more spatial UI and typography references.
3. Future plan: turn the style into a visual language for future creative-code pieces.

Visual gates:

- Must not look like a fake app screenshot.
- No tiny labels or status counters as decoration.
- The object arrangement needs a clear foreground, middle ground, and background.

Why this direction:

It connects the series back to product/interface design, but treats UI as visual material instead of workflow.

## Recommended Next Build

Build Direction 1 first as `docs/product/experiments/3d-vector-aesthetic-stage-02/index.html`.

Implementation outline:

1. Create a single-file canvas HTML focused on dynamic poster composition.
2. Keep `record=1` only for deterministic MP4 capture.
3. Do not foreground cursor, clicks, or pointer trails.
4. Use a reduced palette and remove HUD clutter.
5. Validate the first frame at 1920x1080 before generating video.
6. Generate a horizontal preview MP4 only after the still frame looks publishable.

Definition of ready:

- The HTML works when opened directly or served locally.
- The still frame reads as a designed poster.
- The video can be produced from the same narration segments used for subtitles.
- The visual clearly communicates typography, depth, scan, and material restraint.
