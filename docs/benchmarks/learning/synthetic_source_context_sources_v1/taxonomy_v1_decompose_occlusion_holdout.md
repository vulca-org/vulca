# taxonomy_v1_decompose_occlusion_holdout source packet

Reviewed synthetic source packet for a decompose taxonomy holdout.

Source contract:
- semantic_path foreground.glass_reflection is an occluding reflection layer.
- semantic_path subject.people contains interior figures behind the glass.
- Reflection and people can overlap visually but require separate layer ownership.

Decision context:
- The failure is occlusion because glass reflection and interior figures have overlapping ownership.
- Preferred tiny action remains fallback_to_agent because source context removes the source gap but occlusion ordering still needs agent review.

Privacy review: synthetic project packet only; no private local paths or user source files.
