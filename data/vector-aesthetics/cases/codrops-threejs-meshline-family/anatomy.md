# Anatomy: Codrops Three.js MeshLines Demo Family

Primitive: thickened vector routes form a spatial line-sculpture family across grid furrows, orbital ribbons, and vertical fiber bundles.

Technique: treat MeshLine as a family primitive rather than a single curve: separate route geometry, wire-grid scaffolding, shader ribbons, thickness, and sweep motion.

Technique stack:

- Ricefield grid: crossing low-opacity guide lines give the line sculpture a ground plane and make route direction reviewable.
- Venus orbit: nested closed routes teach how thick lines can imply a 3D object without filled mesh surfaces.
- Bamboo fibers: vertical curved strokes teach density, bending, and rhythm across repeated line instances.
- Shader ribbon: wider translucent strokes sit behind the crisp mesh routes to stand in for TSL/WebGPU material glow.
- Runtime discipline: keep route count and line width bounded so the visual remains suitable for browser review.

Construction sequence:

1. Draw a crossed wire grid first so route curvature has a readable coordinate field.
2. Add 18 thick mesh routes, grouped as grid furrows, orbit loops, and vertical fibers.
3. Add 12 wider shader ribbons under the routes to teach material pass separation.
4. Add a small number of route nodes so reviewers can see anchor points.
5. Animate the whole line family with a subtle sweep rather than camera-heavy motion.

Evidence boundary: the canonical Codrops Three.js hub is retained as source-link-only. PNG, GIF, and HTML are local generated learning evidence and do not claim upstream demo geometry, shader code, assets, or camera paths.
