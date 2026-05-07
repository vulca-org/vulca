# taxonomy_v1_redraw_pasteback_mismatch_holdout source packet

Reviewed synthetic source packet for a redraw taxonomy holdout.

Source contract:
- semantic_path background.wall.tiles is the ceramic tile redraw target.
- The pasted-back preview must align with the source grid.
- A visible border or offset means the preview is not trustworthy.

Decision context:
- The failure is pasteback_mismatch because the edited tile was displaced and produced a visible border.
- Preferred tiny action is manual_review because the source context identifies a pasteback validation issue.

Privacy review: synthetic project packet only; no private local paths or user source files.
