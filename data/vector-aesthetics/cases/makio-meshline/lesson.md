# Lesson: Makio MeshLine

lesson_goal: Rebuild the core primitive without copying brand, assets, source geometry, or proprietary shader code.

minimal_rebuild_exercise:
1. Create a 960x540 dark canvas with a low-contrast technical grid.
2. Sketch three cubic-bezier routes with distinct start, crossing, and exit points.
3. Render each route twice: a blurred glow stroke and a crisp thick vector stroke.
4. Add short white dash packets that move along the same route direction.
5. Export one still screenshot and one short motion clip.
6. Write a code note that names the primitive, material stack, motion model, and source boundary.

review_questions:
- Can the learner see the difference between route geometry, material glow, and motion packet?
- Is the local evidence clearly separate from the canonical source?
- Does the primitive transfer to VULCA source-trail or decision-path visualization?

runtime_target: static_html_svg
verified_status: local_artifact_present
verification_command: PYTHONPATH=src pytest tests/test_vector_aesthetics_gold_cases.py -q
