# taxonomy_v1_decompose_over_segmentation_holdout source packet

Reviewed synthetic source packet for a decompose taxonomy holdout.

Source contract:
- semantic_path subject.face should remain one useful editable region.
- Eye micro-shards are not separate requested layers.
- The source portrait requires merging tiny feature shards back into face ownership.

Decision context:
- The failure is over_segmentation because small facial shards duplicate the parent face mask.
- Preferred tiny action is merge_layers because the source context names the parent layer boundary.

Privacy review: synthetic project packet only; no private local paths or user source files.
