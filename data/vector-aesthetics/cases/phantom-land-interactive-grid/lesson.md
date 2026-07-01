# Lesson: Phantom.land Interactive Grid and 3D Face Particle System

lesson_goal: Rebuild the core primitive without copying brand, assets, face maps, particle maps, source geometry, or proprietary shader code.

minimal_rebuild_exercise:
1. Create a 960x540 dark technical canvas with a regular wire grid.
2. Add a cursor influence point and ring.
3. Displace nearby grid nodes with distance-weighted force.
4. Add a sparse face-like particle sculpture beside the grid.
5. Animate cursor offset and particle wobble as one ambient interaction.
6. Export one still screenshot and one short motion clip.
7. Write a code note that names grid field, particle sculpture, interaction state, and source boundary.

review_questions:
- Can the learner distinguish grid rest state, cursor force, and particle sculpture?
- Does the motion show ambient force, not only decorative particles?
- Is the local evidence clearly separated from the Phantom.land/Codrops reference?
- Can the primitive transfer to VULCA review pressure or evidence-cluster visualization?

runtime_target: static_html_svg
verified_status: local_artifact_present
verification_command: PYTHONPATH=src pytest tests/test_vector_aesthetics_gold_cases.py -q
