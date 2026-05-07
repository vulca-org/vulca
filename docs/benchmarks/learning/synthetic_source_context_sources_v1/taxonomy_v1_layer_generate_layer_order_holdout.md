# taxonomy_v1_layer_generate_layer_order_holdout source packet

Reviewed synthetic source packet for a layer generation taxonomy holdout.

Source contract:
- semantic_path background.mountains uses z_index 0.
- semantic_path foreground.title_plaque must stay readable above atmosphere.fog.
- semantic_path atmosphere.fog should not cover required title text.
- semantic_path subject.traveler belongs above the background composition.

Decision context:
- The failure is layer_order because fog hides the title plaque.
- Preferred tiny action is manual_review because the source context identifies the z_index ownership issue.

Privacy review: synthetic project packet only; no private local paths or user source files.
