# Aesthetic Rubric

Status: not-run-public-blocked.

Scores are 0-5. Higher is better. A score is valid only when the reviewer can point to rendered slides, source-card traceability, and the relevant memory entry. Before generation, this rubric is a contract, not evidence that Run 2.0 has improved.

| Dimension | Checks |
| --- | --- |
| `commercial_specificity` | The deck names a concrete audience, decision, and failure mode. |
| `evidence_alignment` | Claims trace to evidence memory and source cards. |
| `aesthetic_memory_usage` | Visible design moves trace to aesthetic memory ids and multimodal anchors where applicable. |
| `multimodal_learning` | Text, image-reference, video, audio, transcript, or interaction observations produce visible generator behavior rather than abstract process boxes. |
| `visual_learning_target_execution` | The deck visibly executes selected targets such as before/after delta, mini-preview, rhythm budget, transcript compression, or public-demo climax. |
| `visual_hierarchy` | Each slide has one dominant claim and one dominant visual object. |
| `rhythm_variance` | The six-slide sequence includes cover, setup, contrast, proof, climax, and close. |
| `density_control` | Main slides avoid dense tables, repeated dashboard grids, and small-label overload. |
| `asset_discipline` | Assets support atmosphere or diagrams without replacing editable slide structure. |
| `editability` | Core text, claims, labels, and proof objects remain editable. |
| `render_risk` | Native or cross-platform render checks are recorded before public release. |

Run 2.0 must beat Run 1.5 on `aesthetic_memory_usage`, `rhythm_variance`, and `density_control`, or the rerun has not solved the right problem.

## Review Rules

- Score from generated outputs only; do not score intent, prompts, or memory files as deck quality.
- Use the comparison arms exactly as defined in `generation_briefs/`.
- Require a persisted per-slide `trace_manifest.json` for every generated arm before scoring.
- Require any claimed multimodal learning to trace to `multimodal_database.json` anchors and to visible slide behavior.
- Require any claimed visual target execution to trace to `visual_learning_targets.json` and remain native/editable in PPT.
- Require `generation_protocol.md` runtime isolation, native PPT QA, and layout geometry QA before scoring.
- Treat missing native render inspection as a public-release blocker even when screenshots look acceptable.
- Penalize any slide where a bitmap replaces editable text, labels, tables, diagrams, or proof structure.
- Penalize any slide that hides unresolved proof density by shrinking type below a reviewable size.

## Release Thresholds

- `internal only`: any required arm is missing, any trace manifest is missing, runtime isolation is unproven, native PPT QA fails, layout geometry QA fails, or any public-release gate is blocked.
- `demo candidate`: all four arms exist, trace manifests exist, runtime isolation is recorded, native PPT QA passes, layout geometry QA passes, render inspection is complete, and Run 2.0 scores at least 4 on `editability`, `asset_discipline`, and `render_risk`.
- `public blocked`: default status until provenance and human approval are recorded, even when the deck qualifies as a demo candidate.
- `public ready`: only after human approval confirms the generated deck, trace manifest, provenance, and render inspection.
