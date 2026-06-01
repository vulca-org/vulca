# Generation Protocol

Status: not-run-public-blocked.

This protocol must run before any Run 2.0 deck arm is scored.

Run 2.1 adds `skill_workflow.json` as the declarative stage contract. The file is not a new orchestration engine; it defines the order, inputs, outputs, gates, and human-gated repair triggers that generation and QA must satisfy.

Run 2.2 adds `multimodal_database.json` as the layer-2 data contract. The file records text, image-reference, video, audio, transcript, and interaction anchors as derived observations only. It does not authorize storing raw media, copied tutorial prose, screenshots, video frames, audio files, full transcripts, source layouts, logos, or brand marks.

Run 2.2 adds `visual_learning_targets.json` as the target contract for the next rerun. A target is not a source asset; it is an original, native-PPT behavior requirement derived from allowed observations.

Run 2.3 adds `visual_target_components.json` as the component contract for the next rerun. A component is not decorative metadata; it is the exact native-PPT object family the generator must draw to satisfy a target.

Run 2.4 adds `video_demo_beat_map.json`, `motion_learning_targets.json`, and `presentation_sequence_components.json` as the motion grammar contract for the next rerun. Motion grammar is not rendered video or decorative animation. It is derived tutorial/video observation converted into ordered native-PPT reveal, scale, build, pause, and handoff requirements that code generation and trace QA can inspect.

## Multimodal Data Boundary

- Treat all tutorial pages, videos, audio, transcripts, screenshots, and product references as sources for derived design signals only.
- Store source identity, short locator anchors, observations, executable design signals, allowed use, and QA gates.
- Keep any temporary media processing cache under untracked `outputs/`; do not commit downloaded media or extracted frames.
- Convert audio/video/tutorial observations into code-generation behavior: density budgets, pacing rules, before/after slide targets, native headline compression, and visual-climax requirements.
- Select visual learning target ids before writing slide code, and record them in the trace manifest.
- Select visual component ids after target selection and before slide-code generation. If a target has no visible native component in the rendered slide, treat the target as failed.
- Select video beat ids, motion target ids, and sequence component ids before writing slide code. If a deck claims to use tutorial/video motion learning but does not record these ids and ordered native reveal steps, treat the claim as failed.
- If an arm cannot trace a visible design move back to `multimodal_database.json`, source/video cards, and memory ids, it can be inspected internally but cannot be used as evidence that the database improved design quality.

## Motion Grammar Boundary

- Treat motion grammar as code-generation metadata until native PPT objects and static layout quality are proven.
- Do not store downloaded videos, extracted frames, audio files, full transcript text, source screenshots, or copied animation timing files in the pack.
- Represent a tutorial/demo beat as source id, locator, short observation, derived presentation rule, motion role, ordered native reveal sequence, QA probe, and release boundary.
- Use sequence components for presentation rhythm: attention reset, before/after reveal, proof build, climax scale emphasis, and release handoff.
- Public video or actual PowerPoint animation can be explored only after the generated deck passes native object checks, trace completeness, render checks, provenance, and human approval.

## Runtime Isolation

- Run each arm in a separate output directory under `outputs/<thread-id>/presentations/<arm-id>/`.
- Start each arm from a fresh generation prompt and load only the files allowed by its generation brief.
- Do not reuse chat context, cached memory summaries, generated slide code, SVG assets, layout JSON, screenshots, or repair notes across arms.
- Record model/provider, tool versions, cache directory, allowed input files, and forbidden input files in the arm's `trace_manifest.json`.
- If a generator cannot prove that forbidden inputs were unavailable, mark the arm `internal_only` and exclude it from winner claims.

## Native PPT QA

- Reject any slide that is flattened into one full-slide raster image.
- Reject any core title, claim, label, chart value, gate statement, or proof annotation that exists only inside a bitmap.
- Record native text box count, native shape/chart/table/diagram count, raster asset count, and image-to-native-object ratio for every slide.
- Record selected visual component ids and the native primitives used for the component.
- Record selected motion target ids, sequence component ids, ordered reveal steps, and the native primitives used for each step.
- Keep image-to-native-object ratio at or below `0.5` unless the image is an approved atmosphere background with all core content still native and editable.

## Layout Geometry QA

- Reject visible text overlap, clipped text, unreadable microtype, or text that escapes its intended shape.
- Reject default-styled tables or charts unless the selected arm is `bad_aesthetic_memory`.
- Reject repeated equal-density grids across adjacent main-story slides unless the selected arm is `bad_aesthetic_memory`.
- Record geometry checks, density counts, and any repair actions in `trace_manifest.json` before scoring.

## Trace Outcome Refresh

- After structural and aesthetic QA run, refresh per-slide `structural_qa` and `aesthetic_qa` outcomes in `trace_manifest.json`.
- The refresh step must support dry-run review, preserve a backup manifest, and keep the release decision public-blocked unless native render and human approval gates pass.
- If trace outcome refresh is missing, the arm can be inspected internally but cannot be used as public-release evidence.

## Scoring Boundary

The aesthetic rubric can score only generated outputs that pass runtime isolation, trace-manifest completeness, native PPT QA, and layout geometry QA.
