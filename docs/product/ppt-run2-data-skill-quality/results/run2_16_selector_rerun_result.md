# Run 2.16 Selector-Driven Rerun Result

Status: rerun completed, internal demo only, public blocked.

Run 2.16 is the four-arm rerun after Run 2.15. It is the first generated PPT pass where the Run 2.15 layout selector sources, layout module memory, and selector gate matrix execute before native PPT code generation.

What changed:

- `run2_16_full_skill` may read Run 2.15 selector sources, layout module memory, and selector gate matrix, plus the Run 2.10 aesthetic shell.
- `bad_selector_memory` may read selector sources but must not read Run 2.15 layout module memory or selector gate matrix.
- The selector gate file is `run2_15_layout_selector_gate_matrix.json`; it is required before the full arm writes native PPT code.
- The full arm trace records selected module ids, selector gate ids, text resilience, hidden trace policy, product surface probe, metric reveal climax probe, and actual native module calls.
- The public slide surface still follows `manifest_viewer_qa_only_for_public_surface`: selector proof is inspectable in trace/viewer/QA, not printed as workflow machinery on the slide.

Artifacts:

- Four-arm sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-16-four-arm-contact-sheet.png`
- Full-skill series sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`
- HTML viewer: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html`
- Delivery QA: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-16-delivery-qa-report.md`

Gemini artifact review judged the Run 2.16 full arm as more editorial and polished than the controls, while the `bad_selector_memory` arm remains weaker and more crowded. It also flagged that the four-arm contact sheet labels are ambiguous and the full-series horizontal image is too wide for reading fine text.

Conclusion: Run 2.16 proves that the selector data/workflow layer can drive code-generated PPT. It is still public blocked because visual quality, native render inspection, real product/demo media handling, and human approval are not complete. Do not advance to Run 3.0.
