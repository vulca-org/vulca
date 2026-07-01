# Lesson: WebGPU Scanning Effect with Depth Maps

lesson_goal: Rebuild the core primitive without copying brand, assets, source imagery, depth maps, or proprietary shader code.

minimal_rebuild_exercise:
1. Create a 960x540 dark canvas with a bounded inspection area.
2. Generate a synthetic depth field from simple math instead of using a downloaded image.
3. Sample the field into a dot grid.
4. Map depth classes to dot size, color, and opacity.
5. Animate a vertical scan plane across the grid.
6. Export one midpoint screenshot and one short sweep motion clip.
7. Write a code note that names depth source, scan model, material mapping, and source boundary.

review_questions:
- Can the learner distinguish depth source, sampled dots, scan plane, and reveal state?
- Does the motion show inspection progress rather than generic blinking?
- Is the local evidence clearly separated from the Codrops reference?
- Can the primitive transfer to VULCA review-gap inspection or confidence-depth views?

runtime_target: static_html_svg
verified_status: local_artifact_present
verification_command: PYTHONPATH=src pytest tests/test_vector_aesthetics_gold_cases.py -q
