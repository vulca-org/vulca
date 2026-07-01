# Anatomy: Makio MeshLine

Primitive: routed thick 3D vector line.

Technique: define a small set of cubic-bezier routes, render each route as a wide ribbon stroke, duplicate it as a blurred glow layer, then animate short dash packets along the same path. The local rebuild uses SVG strokes to isolate the learning primitive; the canonical source remains a reference link rather than copied geometry or shader code.

Scene structure:
- Background: dark technical grid with low contrast so curvature and crossings remain legible.
- Route layer: three high-chroma paths, each with rounded caps and different crossing order.
- Glow layer: blurred duplicate strokes below the crisp route strokes.
- Motion layer: white dash packets travelling along each path to show direction and speed.
- Evidence layer: local PNG, GIF, and HTML note point to the same primitive.

Construction sequence:
1. Start with three route intentions: inbound signal, crossing route, and foreground sweep.
2. Place control points so the routes cross once or twice without becoming tangled.
3. Draw a thick base stroke first, then a blurred glow stroke behind it.
4. Add short white dash segments with animated dash offset.
5. Review still state and motion state separately before promoting the case.

Evidence: screenshots/minimal-rebuild-desktop.png, videos/minimal-rebuild-motion.gif, code/minimal-rebuild.html.
