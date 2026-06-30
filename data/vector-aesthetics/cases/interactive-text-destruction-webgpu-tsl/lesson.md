# Lesson: Interactive Text Destruction with Three.js, WebGPU and TSL

lesson_goal: Rebuild the core primitive without copying brand, assets, source geometry, or proprietary shader code.

minimal_rebuild_exercise:
1. Create a dark 960x540 technical canvas with pointer influence rings.
2. Draw a readable word as the stable evidence state.
3. Break the word into generated rectangular fragments.
4. Add particles and trace lines around the pointer field.
5. Export a still state where the word is partly disrupted.
6. Export a motion clip where fragments spring back toward readable text.
7. Write a code note that names text volume, fragment field, interaction state, and source boundary.

review_questions:
- Can the learner distinguish readable word, fragment layer, particle layer, and pointer field?
- Does the motion show recovery, not only explosion?
- Is the local evidence clearly separated from the Codrops reference?
- Can the primitive transfer to VULCA claim uncertainty or evidence repair states?

runtime_target: static_html_svg
verified_status: local_artifact_present
verification_command: PYTHONPATH=src pytest tests/test_vector_aesthetics_gold_cases.py -q
