# Lesson: False Earth

lesson_goal: Teach world-scale UI sculpture as a composition of procedural systems rather than a single landscape render.

minimal_rebuild_exercise:

1. Start with a curved horizon and a ground grid so reviewers can read scale.
2. Add a bounded grass field with repeated blades; vary bend, height, and position.
3. Add cosmic beam shapes as a shader layer over the world.
4. Add interaction rings on the ground plane to represent raycast or hover feedback.
5. Add bloom points as flower lifecycle markers; keep them countable and separate from grass.
6. Export still, motion, and standalone HTML before promotion.

review_questions:

- Does the composition read as a technical world interface, not just scenery?
- Can a learner separate terrain scaffold, grass, beams, waves, and lifecycle markers?
- Are WebGPU implementation claims bounded to sourced framing and local proxies?
- Is the world dense enough to teach runtime constraints but small enough to review offline?

runtime_target: The checked-in HTML is static SVG/CSS for offline review. A production rebuild would use Three.js WebGPU, compute shaders, indirect drawing, instancing, and bounded lifecycle buffers.

verification_command: `PYTHONPATH=src pytest tests/test_vector_aesthetics_gold_cases.py -q`
