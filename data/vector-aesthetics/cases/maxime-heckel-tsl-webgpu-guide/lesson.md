# Lesson: Field Guide to TSL and WebGPU

lesson_goal: Teach TSL/WebGPU as a design grammar: build shader intent from nodes, make uniforms explicit, separate material passes, and treat compute work as part of the visual system.

minimal_rebuild_exercise:

1. Create a dark inspection stage with a visible TSL node graph.
2. Add at least 18 shader nodes and route links between them.
3. Place uniform chips near the graph and name the controlled inputs.
4. Build five material passes from left to right.
5. Add compute lanes below the graph to show work dispatched before rendering.
6. Animate compile flow without importing upstream code or shader snippets.

review_questions:

- Can the learner distinguish TSL node composition from rendered material output?
- Are uniforms and compute work visible rather than hidden behind a pretty surface?
- Does the case explain runtime risk without claiming benchmark results?
- Are article media, code snippets, shaders, and demos kept out of the repo?

runtime_target: The checked-in HTML is static SVG/CSS for offline review. A production rebuild would use local Three.js TSL code, explicit node material ownership, measured compute budgets, and source-controlled shader assumptions.

verification_command: `PYTHONPATH=src pytest tests/test_vector_aesthetics_gold_cases.py -q`
