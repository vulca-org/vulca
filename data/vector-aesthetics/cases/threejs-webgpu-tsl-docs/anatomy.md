# Anatomy: Three.js WebGPURenderer and TSL Documentation

Primitive: implementation constraint map for contemporary Three.js shader aesthetics: renderer backend, TSL node material, fallback route, and resource-buffer contract.

Technique: convert official documentation into a learning diagram. A renderer chooses a backend capability path, node materials define shader responsibilities, fallback routes reveal risk, and buffer blocks make render targets and resource ownership visible.

Technique stack:

- Renderer backend: three panels separate WebGPU path, WebGL2 fallback, and unsupported states.
- Fallback routes: four animated routes show capability negotiation and forced fallback thinking.
- Node material: six blocks map position, normal, color, roughness, emissive, and output responsibilities.
- Buffer contract: eight blocks expose depth, color, normal, MRT, storage, sample, target, and resolve resources.
- Documentation rule: the case teaches constraints and options, not a copied example scene.

Construction sequence:

1. Draw backend decision panels first so runtime capability remains visible.
2. Add fallback routes as active paths rather than prose-only warnings.
3. Draw node material blocks after the renderer contract is clear.
4. Add resource buffers last so the material has an implementation budget.
5. Animate fallback flow subtly; do not animate material output as if it were a demo.
6. Export still, motion, and standalone HTML before promotion.

Evidence boundary: official Three.js documentation is retained as source-link-only. PNG, GIF, and HTML are local generated learning evidence and do not claim docs screenshots, examples, source snippets, renderer code, or demos.
