# taxonomy_v1_redraw_mask_too_broad_holdout source packet

Reviewed synthetic source packet for a redraw taxonomy holdout.

Source contract:
- semantic_path midground.shop.sign is the narrow neon sign target.
- The shop facade and sidewalk are source context that must remain untouched.
- The source target is much smaller than the selected mask area.

Decision context:
- The failure is mask_too_broad because the mask selected the facade instead of the sign.
- Preferred tiny action is adjust_mask because the source context defines a tighter edit boundary.

Privacy review: synthetic project packet only; no private local paths or user source files.
