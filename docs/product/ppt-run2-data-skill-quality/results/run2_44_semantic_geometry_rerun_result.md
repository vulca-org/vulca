# Run 2.44 Semantic Geometry Rerun

Status: four-arm rerun completed, public blocked.

Run 2.44 consumes Run 2.43 before native PPT drawing. The full arm binds semantic visual asset ids, editorial typography memory, and workflow gates, then turns those records into data-bound geometry slots.

This fixes the suspected workflow bug from the preflight audit: the latest visible PPT is no longer only Run 2.41 with post-hoc data notes. The generated full arm now carries `run2_43_semantic_visual_asset_ids`, `run2_43_editorial_typography_memory_id`, `run2_43_visual_asset_semantics_gate_id`, and `run2_44_data_bound_geometry` in trace.

## Arms

- `prompt_only`
- `run1_5_skill`
- `run2_44_full_semantic_geometry_compiler`
- `bad_run2_43_name_only_geometry`

## Result

Best internal arm: `run2_44_full_semantic_geometry_compiler`.

Quality delta: `semantic_visual_asset_geometry_binding`. All six full-arm slides contain three Run 2.43 semantic visual asset ids and data-bound geometry slots.

The negative control `bad_run2_43_name_only_geometry` can repeat surface names, but it has no semantic visual asset ids, no gate id, and no data-bound geometry.

Public release remains blocked. This proves dataflow and workflow consumption, not final public-video-grade aesthetics.

## Required Images

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-44-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Do not advance to Run 3.0.
