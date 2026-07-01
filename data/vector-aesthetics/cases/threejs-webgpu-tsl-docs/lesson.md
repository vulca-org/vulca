# Lesson: Three.js WebGPURenderer and TSL Documentation

lesson_goal: Teach WebGPU/TSL implementation constraints before visual polish: backend choice, fallback behavior, node material ownership, and render-resource budgeting.

minimal_rebuild_exercise:

1. Create three backend panels: WebGPU, WebGL2 fallback, and unsupported state.
2. Draw four fallback routes so capability changes are visible.
3. Add six node-material blocks for common shader responsibilities.
4. Add eight resource-buffer blocks for output and storage thinking.
5. Keep the scene diagrammatic rather than pretending to be a live renderer.
6. Animate fallback flow only enough to show state transition.

review_questions:

- Can the learner tell which part is renderer capability and which part is shader material?
- Are fallback routes visible enough to guide implementation planning?
- Does the case teach resource contracts, not just a pretty shader?
- Are official docs screenshots, examples, source snippets, and renderer files kept out of the repo?

runtime_target: The checked-in HTML is static SVG/CSS for offline review. A production rebuild would use current Three.js WebGPURenderer and TSL APIs, verify device support, and make fallback behavior explicit in code.

verification_command: `PYTHONPATH=src pytest tests/test_vector_aesthetics_gold_cases.py -q`
