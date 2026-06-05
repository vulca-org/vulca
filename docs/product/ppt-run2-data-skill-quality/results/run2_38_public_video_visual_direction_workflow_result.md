# Run 2.38 Public Video Visual Direction Workflow

Status: Run 2.38 data/workflow pack completed, public blocked.

Run 2.38 is data/workflow-only. It creates no new PPT deck and does not advance to Run 3.0.

It converts the Run 2.37 finding `visual_module_language_too_repetitive_and_card_like` into per-slide visual direction and workflow gates.

Target layer: `public_video_grade_slide_direction_and_per_slide_visual_recipe`.

## What Changed

- `run2_38_public_video_slide_direction_memory.json` gives every slide role a unique visual rhythm and public-video scene type.
- `run2_38_per_slide_visual_recipe_memory.json` defines layout signature, typography, spacing, visual evidence, and motion beat obligations per slide.
- `run2_38_public_video_workflow_gates.json` requires the next generated rerun to consume those direction and recipe ids before native PPT drawing.

## Gate

- Creates new PPT deck: false.
- Public ready: false.
- Public release gate: blocked.
- Run 2.39 four-arm rerun must consume this workflow before any generated slide claims public-video quality.

Next: consume the Run 2.38 public-video visual direction workflow before Run 2.39 four-arm rerun. Do not advance to Run 3.0.
