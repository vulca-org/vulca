# Lesson: Codrops Three.js MeshLines Demo Family

lesson_goal: Teach MeshLine as a contemporary 3D vector construction system: route first, material second, camera last.

minimal_rebuild_exercise:

1. Start with a wire-grid scaffold so route direction and density can be audited.
2. Draw three route families: furrow lines, orbital ribbons, and vertical fibers.
3. Give the routes visible thickness; avoid hairline-only line art.
4. Add a translucent shader-ribbon pass below the crisp lines to approximate emissive material.
5. Use a subtle sweep animation to show that the object is procedural and alive.
6. Export one still, one short motion clip, and one standalone HTML note before promotion.

review_questions:

- Can the learner distinguish route geometry from shader material?
- Does the line system read as spatial, or only as flat decoration?
- Are grid, orbit, and fiber subfamilies visibly separated?
- Are upstream demo assets and implementation details kept as source-link-only?

runtime_target: The checked-in HTML is static SVG/CSS for offline review. A production rebuild would use Three.js MeshLine-style geometry, TSL/WebGPU material nodes, and bounded line counts for performance.

verification_command: `PYTHONPATH=src pytest tests/test_vector_aesthetics_gold_cases.py -q`
