# Generation Protocol

Status: not-run-public-blocked.

This protocol must run before any Run 2.0 deck arm is scored.

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
- Keep image-to-native-object ratio at or below `0.5` unless the image is an approved atmosphere background with all core content still native and editable.

## Layout Geometry QA

- Reject visible text overlap, clipped text, unreadable microtype, or text that escapes its intended shape.
- Reject default-styled tables or charts unless the selected arm is `bad_aesthetic_memory`.
- Reject repeated equal-density grids across adjacent main-story slides unless the selected arm is `bad_aesthetic_memory`.
- Record geometry checks, density counts, and any repair actions in `trace_manifest.json` before scoring.

## Scoring Boundary

The aesthetic rubric can score only generated outputs that pass runtime isolation, trace-manifest completeness, native PPT QA, and layout geometry QA.
