# Anatomy: WebGPU Gommage Effect

Primitive: a readable MSDF-like word face crosses a dissolve edge, then releases glyph fragments, dust particles, and petal-shaped vectors into a bloom field.

Technique: stage the dissolve as a layered typography material system, then split outgoing debris into glyph fragments, dust particles, petal vectors, and bloom proxy.

Technique stack:

- Typography layer: keep the word readable first, using offset chromatic shadows to imply an MSDF/vector text material without copying upstream font geometry.
- Shader layer: treat the dissolve edge as a noise threshold that eats through the word from one side, exposing a material transition rather than a simple opacity fade.
- Particle layer: separate rectangular glyph fragments, round dust particles, and petal silhouettes so the learner can distinguish debris roles.
- Bloom layer: use soft pink/gold halos as an MRT/selective-bloom proxy, explicitly marked as a local approximation rather than the original renderer.
- Motion layer: animate particles and petals between a dispersed state and a readable state to teach how timing couples text disappearance to particle release.

Construction sequence:

1. Draw the base word as a stable evidence label.
2. Add two chromatic offset shadows to suggest MSDF edge color and emissive material separation.
3. Place a curved dissolve band through the upper half of the word.
4. Break the outgoing side into glyph fragments with directional offsets.
5. Add smaller dust particles and larger petal vectors on independent arcs.
6. Wrap the event in a soft bloom ellipse and bottom status labels that name the shader proxy.

Evidence boundary: the canonical Codrops article is retained as source-link-only. PNG, GIF, and HTML are local generated learning evidence and do not claim the upstream WebGPU, TSL, MRT, model, font, or shader implementation.
