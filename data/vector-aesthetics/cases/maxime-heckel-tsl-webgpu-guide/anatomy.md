# Anatomy: Field Guide to TSL and WebGPU

Primitive: shader-material thinking as a readable node graph, with uniform inputs, material passes, compute lanes, and runtime budget markers.

Technique: turn the tutorial mental model into a visual build order. Shader intent starts as small TSL nodes, uniforms parameterize time/uv/noise/color, compute lanes update state before the render pass, and material passes compose the visible surface.

Technique stack:

- Shader nodes: 20 generated nodes show expression graph composition before renderer details.
- Uniform chips: eight chips expose the inputs that control a material over time.
- Material passes: five pass slabs separate color, normal, displacement, bloom, and output responsibilities.
- Compute lanes: eight lanes show dispatch work as a first-class part of contemporary WebGPU aesthetics.
- Compile motion: node and pass activation teaches that TSL graphs become runtime shader programs.

Construction sequence:

1. Draw the node graph first and keep links visible.
2. Add uniform chips as named inputs rather than hidden constants.
3. Add material passes only after the graph is legible.
4. Add compute lanes below the graph to represent pre-render work.
5. Animate compile flow with small node and pass activation changes.
6. Export still, motion, and standalone HTML before promotion.

Evidence boundary: the canonical article is retained as source-link-only. PNG, GIF, and HTML are local generated learning evidence and do not claim article screenshots, code snippets, shaders, demos, or media.
