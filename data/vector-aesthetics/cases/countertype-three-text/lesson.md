# Lesson: Countertype three-text

lesson_goal: Teach 3D typography as an engine problem: shape text into lines, tessellate glyphs into meshes, reuse geometry through a cache, and retessellate when variable-font axes change.

minimal_rebuild_exercise:

1. Start with a paragraph box and five baseline rails.
2. Turn each glyph into a simple mesh block or outline path.
3. Vary glyph widths to show layout work before visual styling.
4. Add a geometry-cache panel and mark reused cells separately from hot cells.
5. Add weight, width, and depth axis handles.
6. Animate a small retessellation loop while keeping baselines stable.

review_questions:

- Does the piece read as text geometry rather than a decorative word mark?
- Can a learner separate layout, glyph mesh, cache, and axis-state responsibilities?
- Are Countertype screenshots, fonts, runtime, adapters, and code kept out of the repo?
- Does the local rebuild teach how to implement type-driven 3D interfaces in HTML/Three.js/R3F rather than copying a demo?

runtime_target: The checked-in HTML is static SVG/CSS for offline review. A production rebuild would use Three.js/R3F/WebGPU text geometry APIs and locally licensed fonts, with explicit shaping, caching, and runtime performance boundaries.

verification_command: `PYTHONPATH=src pytest tests/test_vector_aesthetics_gold_cases.py -q`
