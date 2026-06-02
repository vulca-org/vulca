# PPT Run 2.10 Visual System Thickening Design

Status: draft-for-user-review.

## Context

Run 2.9 is the current best internal generated result. It proved that the five-layer product loop can route visual primitive data into code-generated native PPT:

`real commercial usecase -> multimodal tutorial/case data -> visual primitive memory -> visual gate workflow -> code-generated native PPT`

The full arm called actual native modules such as `drawRun29TypographicField`, `drawRun29EditorialSpread`, `drawRun29LayeredProductSurface`, `drawRun29MotionStoryboard`, and `drawRun29ClimaxStage`. The trace records actual module calls, not inferred memory membership.

The remaining problem is not trace truthfulness. The remaining problem is visual-system quality. Gemini's four-arm review judged Run 2.9 a clear winner, but the full-series review warned that Run 2.7, 2.8, and 2.9 still share a similar visual system. Run 2.9 improves structure and composition, but it is still close to the same light-background, black-block, orange-accent, rectangle-led presentation family.

## Goal

Run 2.10 should thicken the same five layers to make the visual system itself more distinctive and public-demo-grade, without advancing to Run 3.0.

The target is not "make 2.9 prettier." The target is to make the system learn and enforce a stronger design direction before generation.

## Options Considered

### Option A: Tune The Existing Run 2.9 Generator

This would adjust colors, spacing, type sizes, and module geometry inside `generate_ppt_run2_9_visual_primitive_arms.mjs`.

Trade-off: fastest path to visible change, but it risks repeating the same failure pattern: palette changes, larger text, and rearranged rectangles without better data or workflow.

### Option B: Add More Visual Primitive Modules Only

This would add new draw functions, such as full-bleed hero field, diagonal composition, product theater, or kinetic sequence modules.

Trade-off: useful but incomplete. More modules do not guarantee better taste unless the data and workflow decide when and why to use them.

### Option C: Thicken Data, Memory, Workflow, Then Rerun

This keeps the five-layer loop and adds a Run 2.10 layer before generation:

1. Better commercial/public presentation usecase anchors.
2. Better multimodal tutorial/case decomposition focused on visual-system direction.
3. More specific design memory for typography personality, spatial composition, product theater, image/SVG strategy, and climax rhythm.
4. Harder workflow gates that reject visual-system sameness, rectangle-led layouts, and weak public-demo first read.
5. New code-generated four-arm rerun plus the two required comparison images.

This is the recommended path because it tests the product thesis rather than manually styling one deck.

## Chosen Design

Run 2.10 will be a same-stage visual-system-thickening pass. It will add new data/workflow artifacts, update the skill contract, then generate a new four-arm PPT rerun.

The four arms remain:

- `prompt_only`
- `run1_5_skill`
- `run2_10_full_skill`
- `bad_visual_system_memory`

The two required visual outputs remain:

- `run2-10-four-arm-contact-sheet.png`
- `run2-full-skill-series-horizontal.png`

## New Data Layer

Create a Run 2.10 visual-system source pack. It should include derived-only observations from commercial and tutorial references, with no copied screenshots, frames, transcripts, brand marks, source layouts, or raw media.

The data must focus on visual system decisions, not generic design principles:

- Presentation category: product launch, keynote reveal, design-system announcement, platform demo, or commercial narrative deck.
- Visual-system direction: editorial, cinematic, spatial/product theater, interface-native, typographic, or hybrid.
- Typography personality: scale behavior, density, contrast, hierarchy, and word-count discipline.
- Spatial composition: full-bleed fields, asymmetry, off-grid structure, overlap, diagonal rhythm, depth, and negative space.
- Asset strategy: generated background, native SVG, native product object, abstract system object, or no imagery.
- Motion/storyboard grammar: reveal order, scale change, pause, transformation, handoff.
- Climax grammar: what makes the peak slide visually unlike setup/proof slides.

Proposed artifact:

- `run2_10_visual_system_sources.json`

## New Design Memory

Create a visual-system memory file that turns the source pack into executable direction families.

Each memory entry should contain:

- `visual_system_id`
- source record ids
- applicable slide roles
- typography contract
- composition contract
- asset strategy contract
- motion/sequence contract
- native PPT module implications
- forbidden sameness patterns
- public-demo first-read probe
- anti-copy boundary

Proposed artifact:

- `run2_10_visual_system_memory.json`

## New Workflow Gate

Create a Run 2.10 workflow gate matrix that selects a visual system before selecting slide modules.

The gate should reject:

- Same visual family as Run 2.7/2.8/2.9 unless explicitly justified.
- Rectangle-led composition where every proof object is a box.
- Palette-only change.
- Large-text-only change.
- Climax slide that is just another dashboard/report slide.
- Product surface that is only a flat rectangle.
- Motion storyboard that is just three equal cards.

Each slide role should record:

- selected visual system id
- selected source ids
- selected memory ids
- required native visual modules
- visual-system delta from Run 2.9
- public-demo first-read probe
- sameness failure probe

Proposed artifact:

- `run2_10_visual_system_gate_matrix.json`

## Generator Changes

Add a new generator instead of mutating the Run 2.9 output in place:

- `scripts/generate_ppt_run2_10_visual_system_arms.mjs`

The full arm must read all Run 2.10 inputs. Controls must forbid them. The negative control may read source/decomposition data but must not read the visual-system memory or gate matrix.

The full arm should introduce at least three stronger native visual-system modules, for example:

- `drawRun210FullBleedVisualField`
- `drawRun210ProductTheater`
- `drawRun210KineticSequence`
- `drawRun210EditorialTypeSystem`
- `drawRun210NonRectangularProofPath`
- `drawRun210CinematicClimax`

The exact module set can change during implementation, but the trace must record actual called module ids.

## Trace Contract

Each full-arm slide trace must include:

- `run2_10_visual_system_source_ids`
- `run2_10_visual_system_memory_ids`
- `run2_10_gate_matrix_ids`
- `run2_10_code_module_ids`
- `run2_10_visual_delta_from_run2_9`
- `run2_10_sameness_failure_probe`
- `run2_10_public_demo_first_read_probe`

The full arm must fail if required modules are absent from actual recorded native module calls.

## Viewer And Result Reporting

The HTML viewer should add Run 2.10 to the version selector and continue to show:

- Four arms view.
- Full series view.
- Sheets view.
- Data / Skill view.

Result docs should record both the improvement and the limitation. If Run 2.10 improves public-demo feel but still depends on the same color/type family, the result must say that plainly.

## QA

Required checks:

- Focused tests for Run 2.10 data, workflow, generator input boundaries, and trace fields.
- Case-pack validator with `--profile run2`.
- Delivery validator tests.
- Generator run.
- HTML viewer rebuild.
- Browser viewer check.
- Gemini artifact review of the four-arm sheet.
- Gemini artifact review of the full-skill series sheet.
- `git diff --check`.

## Non-Goals

- Do not advance to Run 3.0.
- Do not claim public readiness.
- Do not copy source screenshots, source layouts, logos, video frames, transcripts, audio, or brand marks.
- Do not manually edit the generated PPT as the proof of product capability.
- Do not satisfy the pass by changing only palette, font size, or card count.
- Do not use full-slide raster images as proof structure.

## Success Criteria

Run 2.10 is successful if:

1. The full arm is trace-truthful and uses actual Run 2.10 module calls.
2. The four-arm sheet shows a visible full-arm advantage over prompt-only, Run 1.5, and bad-memory controls.
3. The full-skill series shows that Run 2.10 is visually distinguishable from Run 2.7/2.8/2.9, not just denser or recolored.
4. The result remains public blocked unless render, provenance, and human approval gates pass.

