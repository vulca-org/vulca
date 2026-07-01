# Lesson: Spline Contemporary 3D Web References

lesson_goal: Teach spatial UI sculpture as an interaction model: panels, state tracks, hotspots, and morphing layout.

minimal_rebuild_exercise:

1. Start with a simple spatial grid and depth lines.
2. Draw several floating UI panels with clear layer separation.
3. Add spatial nodes to expose object anchors and constraints.
4. Add state tracks to show how panels relate over a timeline.
5. Add hotspots for hover or click states.
6. Animate panel and node offsets with a small morph loop.

review_questions:

- Does the scene read as an interface, not just decorative 3D objects?
- Can a learner separate layers, nodes, tracks, hotspots, and morph states?
- Are Spline assets and runtime kept out of the repo?
- Is the local rebuild useful for code-native implementation rather than product-page imitation?

runtime_target: The checked-in HTML is static SVG/CSS for offline review. A production rebuild would use Three.js/R3F or Spline export concepts only as inspiration, with local code-native assets and explicit interaction states.

verification_command: `PYTHONPATH=src pytest tests/test_vector_aesthetics_gold_cases.py -q`
