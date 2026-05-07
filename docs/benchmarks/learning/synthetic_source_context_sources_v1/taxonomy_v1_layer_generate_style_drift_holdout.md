# taxonomy_v1_layer_generate_style_drift_holdout source packet

Reviewed synthetic source packet for a layer generation taxonomy holdout.

Source contract:
- semantic_path background.paper uses z_index 0.
- semantic_path subject.crane uses z_index 30.
- semantic_path detail.pine uses z_index 40.
- The requested tradition is chinese_gongbi with gongbi line discipline, controlled wash, mineral blue, muted red seal, crane, pine, and paper ground.

Decision context:
- The failure is style_drift because the generated layers drifted toward glossy mascot styling.
- Preferred tiny action is adjust_prompt because the source context names the missing style constraints.

Privacy review: synthetic project packet only; no private local paths or user source files.
