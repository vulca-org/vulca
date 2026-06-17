# Run 2.13 Thick Data Rerun Result

Status: rerun completed, internal demo only, public blocked.

Run 2.13 is the first formal rerun after Run 2.12 thick data. It generated the four arms again: `prompt_only`, `run1_5_skill`, `run2_13_full_skill`, and `bad_thick_data_memory`.

What changed:

- `run2_12_thick_multimodal_evidence.json` is now a required full-arm input.
- `run2_12_design_memory_seed.json` is now a required full-arm input.
- `run2_12_workflow_gate_seed.json` is now a required full-arm input.
- The full arm trace records actual native code modules: `drawRun213LaunchArcRoute`, `drawRun213TypeWhitespaceSystem`, `drawRun213ProductDemoSequence`, `drawRun213MetricClimaxObject`, and `drawRun213WorkflowGateRail`.
- The bad control is evidence-only, so it can test whether raw tutorial/case evidence is enough without design memory and workflow gates.

Artifacts:

- Four-arm sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-13-four-arm-contact-sheet.png`
- Full-skill series sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`
- HTML viewer: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html`

Gemini artifact review agreed that the Run 2.13 full arm is visually more asymmetrical, route-driven, and distinct from prompt-only/run1.5/evidence-only controls. It also flagged the main remaining weakness: thumbnail-scale text and truncation risk remain too weak for public-video-grade output.

Conclusion: thick data, memory, and workflow are now in the generated PPT loop, but the deck is still public blocked. Do not advance to Run 3.0; keep deepening the same five layers.
