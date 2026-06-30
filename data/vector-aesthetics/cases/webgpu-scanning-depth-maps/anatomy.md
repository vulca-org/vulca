# Anatomy: WebGPU Scanning Effect with Depth Maps

Primitive: depth-map scanning reveal.

Technique: generate a synthetic depth map, sample it into a dot grid, then sweep a vertical scan plane across the field. Points behind the scan plane become brighter and larger according to their depth class. The local rebuild isolates the visible primitive; the Codrops article remains a source link rather than copied imagery, shader code, or WebGPU pipeline state.

Scene structure:
- Depth source: generated radial relief map with near, mid, and far regions.
- Sample layer: procedural dots sized and colored by depth value.
- Scan layer: cyan reveal plane with a translucent active band.
- Material layer: near points use yellow, mid points use cyan, far points use muted blue-gray.
- Evidence layer: local PNG, GIF, and HTML note describe the same primitive.

Construction sequence:
1. Create a bounded inspection rectangle over a dark technical grid.
2. Generate a depth field from radial relief and ridged bands.
3. Sample the field into dots with depth class labels.
4. Sweep a vertical scan plane across the field.
5. Reveal dots as the scan plane passes them.
6. Review still midpoint and sweep motion separately before promotion.

Evidence: screenshots/minimal-rebuild-desktop.png, videos/minimal-rebuild-motion.gif, code/minimal-rebuild.html.
