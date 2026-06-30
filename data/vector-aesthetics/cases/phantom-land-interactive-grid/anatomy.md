# Anatomy: Phantom.land Interactive Grid and 3D Face Particle System

Primitive: interactive wire grid and particle UI sculpture.

Technique: create a regular wire grid, displace nearby intersections with an ambient cursor field, then pair the field with a sparse face-like particle sculpture. The local rebuild isolates the visible primitive: invisible force becomes visible through grid bend, particle wobble, and cursor offset. The Codrops/Phantom.land case study remains a source link, not copied media, maps, shaders, or production geometry.

Scene structure:
- Grid layer: thin cyan wire lines and visible node points.
- Force layer: cursor point, influence ring, and local grid distortion.
- Sculpture layer: sparse face-like particle bust with cyan, yellow, magenta, and white points.
- Motion layer: cursor orbit creates ambient distortion and particle wobble.
- Evidence layer: local PNG, GIF, and HTML note describe the same primitive.

Construction sequence:
1. Build a regular grid as the rest state.
2. Compute distance from cursor to each node.
3. Push nearby nodes outward and add a small sinusoidal inertia offset.
4. Place a separate particle sculpture to create a spatial UI object.
5. Animate cursor offset and particle wobble together.
6. Review still state and motion state separately before promotion.

Evidence: screenshots/minimal-rebuild-desktop.png, videos/minimal-rebuild-motion.gif, code/minimal-rebuild.html.
