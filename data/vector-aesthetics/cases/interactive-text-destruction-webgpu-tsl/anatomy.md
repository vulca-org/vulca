# Anatomy: Interactive Text Destruction with Three.js, WebGPU and TSL

Primitive: interactive 3D text destruction.

Technique: build a readable word as the stable state, split its visible face into rectangular fragments, then apply a pointer-distance field that pushes nearby fragments outward. The motion state uses a spring-back reconstruction so the same object can communicate disruption and recovery. The local rebuild uses generated SVG/PIL evidence to isolate the learning primitive; the Codrops article remains a source link, not copied media or shader code.

Scene structure:
- Stable layer: readable word face with chromatic offset shadows to imply volume.
- Fragment layer: small rectangular shards sampled from the word mask.
- Particle layer: points and trace lines radiating from the pointer zone.
- Field layer: concentric rings make the interaction radius visible.
- Evidence layer: local PNG, GIF, and HTML note describe the same primitive.

Construction sequence:
1. Define the word as the anchor state.
2. Sample visible text into small rectangular fragments.
3. Compute distance from pointer to each fragment.
4. Displace fragments outward with noise so destruction is not uniform.
5. Animate fragments back toward the readable state using spring-like easing.
6. Review still state and motion state separately before promoting the case.

Evidence: screenshots/minimal-rebuild-desktop.png, videos/minimal-rebuild-motion.gif, code/minimal-rebuild.html.
