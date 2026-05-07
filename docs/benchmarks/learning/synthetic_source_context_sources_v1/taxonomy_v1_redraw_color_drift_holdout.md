# taxonomy_v1_redraw_color_drift_holdout source packet

Reviewed synthetic source packet for a redraw taxonomy holdout.

Source contract:
- semantic_path midground.storefront.awning is the only redraw target.
- The source palette is muted teal with surrounding storefront texture.
- Preserve the original color relationship while redrawing the painted awning.

Decision context:
- The failure is color_drift because the redrawn awning departs from the source palette.
- Preferred tiny action is adjust_mask because the source context identifies a bounded target with palette preservation requirements.

Privacy review: synthetic project packet only; no private local paths or user source files.
