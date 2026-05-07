# taxonomy_v1_redraw_mask_leak_holdout source packet

Reviewed synthetic source packet for a redraw taxonomy holdout.

Source contract:
- semantic_path subject.jacket.buttons covers five pearl buttons.
- Jacket fabric, stitch shadows, and dark gaps are surrounding context, not edit targets.
- The mask is sparse and multi-instance; each button should remain isolated.

Decision context:
- The failure is mask_leak because background fabric was contaminated by button redraw.
- Preferred tiny action is adjust_mask because the source context names the protected surrounding areas.

Privacy review: synthetic project packet only; no private local paths or user source files.
