# Anatomy: Countertype three-text

Primitive: 3D typography layout engine made from glyph meshes, paragraph baselines, geometry-cache cells, and variable-font axis states.

Technique: translate a modern three-text typography pipeline into a code-native lesson: text shaping becomes layout boxes, each glyph becomes a mesh primitive, repeated glyphs flow through a cache, and font-axis changes trigger retessellation while baselines stay readable.

Technique stack:

- Paragraph layout: five baseline rails show multiline text as a spatial volume, not a flat caption.
- Glyph mesh: 30 generated glyph blocks and outline shapes expose the idea that letters are geometry.
- Geometry cache: 18 cells separate repeated glyph instances from new tessellation work.
- Variable axes: six handles model weight, width, and depth controls that change text geometry.
- Retessellation motion: subtle glyph skew and vertical shifts show mesh regeneration while the line layout remains stable.

Construction sequence:

1. Draw the paragraph box and baseline rails first so spacing stays legible.
2. Place glyph meshes on the rails with varied widths to imply text shaping.
3. Add depth duplicates and mesh edges so the letters read as 3D vector material.
4. Add a cache panel that distinguishes reused geometry from freshly computed glyphs.
5. Add variable-axis controls to connect font state changes to retessellation.
6. Export still, motion, and standalone HTML before promotion.

Evidence boundary: the canonical Countertype site is retained as source-link-only. PNG, GIF, and HTML are local generated learning evidence and do not claim Countertype screenshots, runtime code, font files, adapters, demos, or implementation internals.
