# Run 2.9 Visual Primitive Rerun Result

Status: rerun_completed_public_blocked.

Run 2.9 reran the same four-arm experiment as a same-stage visual-primitive pass, not as Run 3.0:

- `prompt_only`
- `run1_5_skill`
- `run2_9_full_skill`
- `bad_visual_primitive_memory`

The purpose was to make the product loop stricter:

`real commercial usecase -> multimodal tutorial/case data -> visual primitive memory -> visual gate workflow -> code-generated native PPT`.

The full arm uses `run2_9_visual_primitive_repair.json`, `run2_9_executable_visual_modules.json`, and `run2_9_visual_gate_matrix.json`. The visible output now calls these native modules:

- Cover: `drawRun29TypographicField` + `drawRun29EditorialSpread`
- Setup: `drawRun29EditorialSpread` + `drawRun29LayeredProductSurface`
- Contrast: `drawRun29EditorialSpread`
- Proof: `drawRun29LayeredProductSurface` + `drawRun29MotionStoryboard`
- Climax: `drawRun29ClimaxStage` + `drawRun29MotionStoryboard`
- Close: `drawRun29TypographicField` + `drawRun29LayeredProductSurface` + `drawRun29MotionStoryboard`

Two mandatory images were generated locally:

- Four-arm sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-9-four-arm-contact-sheet.png`
- Full-skill-series sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`
- HTML viewer: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html`

Gemini reviews at `.gemini-agent/artifacts/2026-06-02T154311542Z-artifacts.json` and `.gemini-agent/artifacts/2026-06-02T154327740Z-artifacts.json` split the conclusion usefully. The four-arm review judged Run 2.9 full a clear visual winner with stronger asymmetry, hierarchy, layered composition, and climax contrast. The full-series review warned that Run 2.7, 2.8, and 2.9 still share a similar visual system; 2.9 is mainly a structural/compositional improvement, not a fully new aesthetic direction.

## QA Summary

- Focused Run 2.9 tests: 3 passed.
- Full Run 2 data/skill tests: 54 passed.
- Delivery validator tests: 7 passed.
- Case-pack validator: passed with `--profile run2`.
- Generator run: passed.
- Browser viewer check: passed; latest run is 2.9 and no console errors were reported.
- Trace truthfulness guard passed: `run2_9_code_module_ids` comes from actual `visualModuleIds` recorded during native rendering.
- Generated outputs remain untracked and are not committed.

## Decision

Run 2.9 is now the current best internal proof that visual primitive data and workflow gates can change code-generated native PPT output. It is a real rerun, not only a data repair.

It is still not a final public presentation. The next loop should keep the same five layers, but make the visual system itself more distinctive and less rectangle-led while preserving native PPT editability and trace truthfulness.

Do not advance to Run 3.0.
