# Lesson: WebGPU Gommage Effect

lesson_goal: Rebuild the gommage primitive as a readable typography-to-particle material transition, not as a generic particle explosion.

minimal_rebuild_exercise:

1. Start with a single word and two offset color shadows so the learner can see an MSDF-like edge treatment.
2. Draw one irregular dissolve threshold through the word and name it as the noise phase.
3. Convert only the outgoing side into rectangular glyph fragments.
4. Add dust particles as small round samples and petals as larger curved vectors; do not merge them into one undifferentiated particle field.
5. Add a bloom proxy around the active zone and label it as a rendering approximation.
6. Produce one still state and one short motion clip before promotion.

review_questions:

- Is the word still readable after adding dissolve debris?
- Can a reviewer separate glyph fragments, dust particles, and petals?
- Does the case teach shader-material thinking, or only decorative scatter?
- Are upstream implementation claims avoided unless they are explicitly sourced?

runtime_target: The checked-in HTML is intentionally static SVG/CSS so review works offline. A production rebuild would use Three.js WebGPU/TSL for noise thresholding, particle buffers, and MRT selective bloom.

verification_command: `PYTHONPATH=src pytest tests/test_vector_aesthetics_gold_cases.py -q`
