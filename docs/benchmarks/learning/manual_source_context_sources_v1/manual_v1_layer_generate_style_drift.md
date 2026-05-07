# manual_v1_layer_generate_style_drift source packet

Reviewed project source packet for a manually curated layer generation case.

User intent: generate a layered Chinese ink landscape with distinct paper,
midground landscape, and pavilion-pine foreground layers.

Layer contract:
- background.paper: z_index 0, opaque full-canvas paper layer.
- midground.landscape: z_index 20, transparent-subject landscape layer.
- foreground.pavilion_pines: z_index 40, transparent-subject pavilion and pine layer.

Decision context:
- The expected output is semantic layers with stable semantic_path values and
  ascending z_index composition.
- The failure is style_drift: generated layer assets did not preserve the
  requested Chinese xieyi brush economy, soft paper absorption, muted paper,
  ink wash palette, pavilion, pines, and mist.
- Preferred tiny action is adjust_prompt, not agent fallback, because the
  reviewed source contract identifies the missing style constraints directly.

Privacy review:
- Project curated packet only.
- No private local paths or user source files are referenced.
