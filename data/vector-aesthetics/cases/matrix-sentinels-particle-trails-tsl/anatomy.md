# Anatomy: Matrix Sentinels Dynamic Particle Trails

Primitive: a data tunnel made from sentinel heads, position-history slices, flow vectors, and thick particle trail routes.

Technique: separate live head position from stored history; draw the route as a temporal buffer rather than as a single static curve.

Technique stack:

- Tunnel scaffold: concentric ellipses and diagonal guides show the 3D field that the sentinels move through.
- Trail routes: eight thick vector paths represent live agent paths through the field.
- History buffer: small slices along the paths expose previous positions, similar to a position-history texture or storage buffer.
- Sentinel heads: bright leading particles make direction and state readable.
- Flow vectors: small arrows reveal the noise/flow field that pushes trajectories.
- Trace animation: subtle offset motion stands in for compute-driven history updates.

Construction sequence:

1. Draw the tunnel scaffold first so trajectory depth is readable.
2. Add eight sentinel routes with distinct material colors.
3. Sample history slices along the routes; keep them smaller and dimmer than heads.
4. Add one bright head per route to expose the current simulation state.
5. Add flow vectors as a separate field, not as decorative ticks.
6. Export still, motion, and standalone HTML before promotion.

Evidence boundary: the canonical Codrops tutorial is retained as source-link-only. PNG, GIF, and HTML are local generated learning evidence and do not claim the upstream TSL compute code, storage buffers, particles, camera, or demo assets.
