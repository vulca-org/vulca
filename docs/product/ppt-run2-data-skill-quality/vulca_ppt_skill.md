# Vulca PPT Skill

Status: not-run.

Run 2.0 is a staged deck-director workflow for code-generated PowerPoint. It must produce editable native text and native structures wherever possible: text boxes, grouped shapes, tables, charts, diagrams, and SVG objects that remain inspectable in PowerPoint. Bitmap assets may set atmosphere or illustrate a focal object, but they must not carry core claims, labels, evidence, or proof structure.

Run 2.1 makes the workflow contract machine-checkable in `skill_workflow.json`. That file remains declarative: it records stage order, required inputs and outputs, gates, and repair recommendations. It does not authorize automated public-ready promotion or ungated repair changes.

Run 2.2 adds `multimodal_database.json` as the data layer before evidence and aesthetic memory. The database can include text tutorial observations, image-reference analysis, video time anchors, audio pacing observations, transcript paraphrase anchors, and interaction observations. It stores only metadata, locators, short observations, and derived design signals; it must not store copied source prose, screenshots, frames, audio, video, full transcripts, layouts, logos, or brand marks.

Run 2.2 also adds `visual_learning_targets.json`. Targets convert multimodal anchors into concrete generator obligations: before/after visual deltas, slide mini-previews, audio rhythm budgets, transcript-to-headline compression, and public-demo climax requirements. A target is useful only if it changes generated PPT code, trace fields, or QA probes.

Run 2.3 adds `visual_target_components.json`. Components turn the target obligations into reusable native-PPT layout contracts: before/after thumbnail, slide mini-preview, rhythm budget strip, transcript headline route, and public-demo climax object. A component is valid only when it can be drawn with editable native PowerPoint text, shapes, connectors, grouped objects, or editable SVG. It must not be satisfied by screenshots, copied source media, or full-slide raster output.

Run 2.0 workflow:

1. Read `commercial_case.md` and select the narrative spine.
2. Compile the multimodal database into executable anchors, cross-modal design tasks, and visual learning targets.
3. Compile evidence memory into claims and guardrails.
4. Compile aesthetic memory into slide archetypes, rhythm roles, density budgets, and negative rules.
5. Select assets only after the slide role is known.
6. Generate code-first PPT modules with editable text and native structures.
7. Run structural QA before aesthetic repair.
8. Run aesthetic QA against the rubric.
9. Repair the deck with explicit reasons.
10. Emit a release decision: internal only, demo candidate, or public blocked.

## Source And Memory Selection

- Use `sources.json` only for reference-analysis policy and source identity.
- Use `multimodal_database.json` to select text, image-reference, video, audio, transcript, and interaction anchors before selecting evidence or aesthetic memory.
- Use `visual_learning_targets.json` to force the selected anchors into visible native-PPT output requirements before writing slide code.
- Use `visual_target_components.json` to choose the concrete native component that will satisfy each selected target before writing slide code.
- Use `source_cards/` and `video_cards/` as the source-card layer; do not copy screenshots, logos, transcripts, frames, layouts, or brand marks.
- Use `evidence_memory.json` to choose claims, business relevance, allowed use, and evidence QA checks.
- Use `aesthetic_memory.json` to choose visible moves, rhythm roles, density budgets, typography rules, composition rules, and negative rules.
- Use `asset_memory.json` to choose generated backgrounds, editable SVGs, native diagrams, charts, and render/accessibility risks.
- Use `narrative_spine.json` and `slide_archetypes.json` to map each slide to a role before writing code.

## Density And Negative Rules

- Enforce each selected aesthetic move's `density_budget` before generating a slide module.
- A main slide should carry one dominant claim and one dominant proof object.
- Repeated dashboard grids, dense status strips, four-column tables, tiny labels, and decorative filler are failures unless the selected archetype explicitly requires them.
- A visual climax must be visually different from setup and proof slides.
- A close must feel like a decision handoff, not an appendix page.
- Multimodal anchors must become visible generation behavior: before/after slide targets, pacing budgets, native headline compression, slide mini-previews, or release-gate surfaces. If an anchor only restates a design principle, it is not strong enough for Run 2.2.
- Visual learning targets must be implemented with editable native text, native shapes, editable SVG, native charts, or grouped objects. Do not satisfy a target with pasted screenshots or full-slide images.
- Visual target components must be visible in the generated slide code and trace. If a before/after target is represented only by text labels, it is still a failed component.

## Deletion Rule

If a slide has too many proof objects, move detail to appendix, speaker notes, or result reports. Do not compress the same content into smaller text.

## Code-Generated PPT Constraints

- Keep all titles, claims, labels, captions, chart values, and proof annotations as editable native text.
- Prefer native PowerPoint shapes, tables, charts, and grouped objects for structure.
- Generated images may be used for backgrounds or focal atmosphere only after asset provenance is recorded.
- Do not flatten a complete slide into an image.
- Do not use a screenshot as proof of editability.
- Keep generated decks, previews, contact sheets, layout JSON, and copied visual references under `outputs/` unless release packaging is explicitly approved.

## QA And Repair

- Run structural QA before aesthetic repair: file existence, slide count, native text extraction, artifact paths, runtime isolation, native object counts, raster/full-slide-image checks, layout geometry, and renderability.
- Run aesthetic QA against `aesthetic_rubric.md`: commercial specificity, evidence alignment, aesthetic memory usage, visual hierarchy, rhythm variance, density control, asset discipline, editability, and render risk.
- Repair only with explicit reasons tied to a failed check, selected memory entry, or render issue.
- Record any repair that changes evidence claims, asset provenance, or release status.

## Trace Manifest Contract

Every generated arm must persist a per-slide `trace_manifest.json` under its local `outputs/` directory before scoring. The manifest must record:

- Arm id and generation brief path.
- Runtime isolation evidence: output directory, prompt/context reset, cache scope, allowed input files, and forbidden input files.
- Slide id, rhythm role, selected source card ids, evidence claim ids, aesthetic move ids, and asset ids.
- Selected multimodal record ids, multimodal anchor ids, and visual learning target ids.
- Selected visual component ids and the native PPT primitives used to render them.
- Density counts: claims, panels, visible words, and proof objects.
- Deleted or routed content: what moved to appendix, speaker notes, result reports, or trace notes.
- Asset provenance: bitmap prompts, SVG/native object origin, license state, and render risks.
- Editability checks for native text, charts, diagrams, and grouped objects.
- Native PPT QA: native text count, native shape/chart/table/diagram count, raster asset count, image-to-native-object ratio, and full-slide-raster rejection.
- Layout geometry QA: overlap checks, clipping checks, readable type checks, default-table checks, repeated-grid checks, and repair actions.
- Structural QA, aesthetic QA outcomes, repair actions, and release-gate inputs.

If the trace manifest is missing or incomplete, the arm is `internal only` and cannot be used to claim that data, memory, or skill quality improved the deck.

## Public-Ready Rule

Public-ready is a gate, not a vibe. Do not claim public readiness until render, provenance, and human approval gates pass.
