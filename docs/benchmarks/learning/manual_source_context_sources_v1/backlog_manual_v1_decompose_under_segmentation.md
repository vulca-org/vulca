# backlog_manual_v1_decompose_under_segmentation source packet

Reviewed project source packet for a backlog manual decompose case.

Source intent: split a nature editorial panel into editable semantic layers
without collapsing repeated subjects into one layer.

Layer contract:
- semantic_path background.garden: z_index 0, garden ground layer.
- semantic_path foreground.flower_stems: z_index 40, flower stems separated from wings.
- semantic_path subject.butterflies: z_index 50, each butterfly remains separable.

Decision context:
- The requested target layer hints mark butterflies and flower stems as
  multi_instance segmentation targets.
- The observed output merged multiple butterflies into a single subject layer,
  creating an under_segmentation failure.
- Preferred tiny action is split_layer_further, not agent fallback, because the
  reviewed source contract names the missed multi_instance boundary.

Privacy review:
- Project curated packet only.
- No private local paths or user source files are referenced.
