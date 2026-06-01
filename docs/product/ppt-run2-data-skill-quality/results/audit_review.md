# Audit Review

Status: reviewed-public-blocked.

Date: 2026-06-01.

## Verdict

`run2_skill` is the best internal arm, but it is not public-ready. The four-arm comparison now shows a real difference between prompt-only generation, evidence-heavy Run 1.5, full Run 2.0 memory, and the bad-aesthetic-memory negative control. The improvement is not only color styling: the full Run 2.0 arm changes rhythm, density, hierarchy, and visual climax behavior.

## What Passed

- Four PPTX arms exist locally under `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/`.
- Structural delivery QA rerun on 2026-06-01 returned `internal-demo-ok-public-blocked` for all four arms.
- The full Run 2.0 deck uses editable native text and shapes rather than full-slide raster images.
- Gemini artifact review confirms that `run2_skill` visibly separates raw data from active design-memory rules.
- The negative control behaves as expected: similar palette alone does not create taste when layout selection collapses into repetitive boxes.

## Blocking Issues

- trace QA outcome refresh required: generated `trace_manifest.json` files include the required fields, but the per-slide `structural_qa` and `aesthetic_qa` values in local outputs still say `pending` after QA has run. This means trace manifests are contract-present, not final public-release evidence.
- native render inspection blocked: Keynote is installed, but the attempted AppleScript export failed with Keynote error `-609` (`invalid connection`), so native render fidelity is still unverified.
- human approval not recorded: no human acceptance has been written for the PPTX, contact sheet, provenance, or release gate.
- repair loop definition still thin: the deck names QA and repair, but does not yet define exact automated failure triggers for repair in the visible slides.

## Gemini Cross-Check

- `.gemini-agent/artifacts/2026-06-01T152210085Z-artifacts.json`: full Run 2.0 contact-sheet audit.
- `.gemini-agent/artifacts/2026-06-01T152221854Z-artifacts.json`: four-arm comparison audit.

Gemini's useful finding: the four-arm result demonstrates layout and design-skill learning because `run2_skill` changes component selection, density, asymmetry, and visual climax, while `bad_aesthetic_memory` keeps a similar palette but fails structurally.

## Decision

Keep `run2_skill` as the current internal winner. Do not promote it to public video or public demo candidate until trace QA outcome fields are refreshed after validation, native or cross-platform render inspection passes, and human approval is recorded.

## Keynote -609 Recovery

If AppleScript export fails again, treat native render as a manual export gate instead of retrying blind automation. Open `ppt-run2-full-vulca.pptx` in Keynote or PowerPoint, export all slides to PNG or PDF, place the rendered files under the same arm's `outputs/` workspace, and compare them against the artifact-tool contact sheet before changing the release status.

## Next Action

Repair the evidence chain before visual polish: update the generation workflow so post-QA status is written back into each trace manifest, then rerun the full deck and native/cross-platform render inspection.
