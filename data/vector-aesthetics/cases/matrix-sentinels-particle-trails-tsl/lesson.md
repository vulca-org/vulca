# Lesson: Matrix Sentinels Dynamic Particle Trails

lesson_goal: Teach particle trails as a history-buffer data tunnel, not as decorative sparkles.

minimal_rebuild_exercise:

1. Start with a tunnel scaffold that establishes depth and flow direction.
2. Draw several sentinel routes through the tunnel.
3. Sample history slices along each route to show the stored previous positions.
4. Place one bright head per route so the current simulation state is obvious.
5. Add flow vectors to show what drives the trajectories.
6. Animate route, history, and head offsets together to approximate a compute update.

review_questions:

- Can a reviewer identify head, history, route, and flow-field layers separately?
- Does the case teach data-tunnel structure, not only particle decoration?
- Are TSL/WebGPU implementation claims bounded to sourced framing?
- Is the motion clip enough to show temporal state rather than a static graphic?

runtime_target: The checked-in HTML is static SVG/CSS for offline review. A production rebuild would use Three.js TSL, compute-style updates, storage buffers, and a position-history texture or equivalent buffer.

verification_command: `PYTHONPATH=src pytest tests/test_vector_aesthetics_gold_cases.py -q`
