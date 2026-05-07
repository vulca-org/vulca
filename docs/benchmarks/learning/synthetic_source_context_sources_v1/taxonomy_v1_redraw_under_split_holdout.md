# taxonomy_v1_redraw_under_split_holdout source packet

Reviewed synthetic source packet for a redraw taxonomy holdout.

Source contract:
- semantic_path subject.chandelier.flames contains eight candle flame instances.
- Each flame should be a separate editable child target.
- The chandelier body is source context and should not be collapsed with the flames.

Decision context:
- The failure is under_split because eight flame instances were collapsed into one edit group.
- Preferred tiny action remains fallback_to_agent because source context removes the source gap but multi-instance split ownership still needs agent judgment.

Privacy review: synthetic project packet only; no private local paths or user source files.
