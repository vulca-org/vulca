# Iteration Log

Status: reviewed-public-blocked.

Task 5 recorded qualitative Gemini contact-sheet reviews, applied one focused local repair pass to the full-Vulca arm, rebuilt the full-Vulca deck with artifact-tool scripts, and reran structural QA. Gemini review is treated as qualitative evidence only; it is not final human approval and does not satisfy the native-render gate.

## Gemini Review Artifacts

| Arm | Artifact | Qualitative summary |
| --- | --- | --- |
| prompt_only | `.gemini-agent/artifacts/2026-05-31T234706549Z-artifacts.json` | Baseline is structurally useful but reads more like a technical specification or testing dashboard than a polished product surface. It remains repetitive and meta-level, with mid-strength specificity, hierarchy, editability cues, learning evidence, and QA clarity. |
| full_vulca | `.gemini-agent/artifacts/2026-05-31T234720384Z-artifacts.json` | Strongest arm. It avoids generic GPT-style explanation and reads as a specific product-lab run report with schemas, boundaries, pipeline stages, design-memory compiler, code-generation anatomy, and QA gate. Main risks were slide 7 and slide 8 redundancy, an abstract opening grid, and a flat decision table. |
| bad_data | `.gemini-agent/artifacts/2026-05-31T234733731Z-artifacts.json` | Structurally valid but semantically degraded. Gemini identified generic workflows, weak claim-to-proof relationship, non-committal content, and poorer source-boundary discipline, supporting the negative-control signal. |

## Repair Pass

| Slide | Local repair | Verification status |
| --- | --- | --- |
| 7 | Converted `Prompt-Only vs Full Vulca` into `Score Delta: Prompt vs Vulca`, showing prompt-only average, full-Vulca average, and observed delta. | Rebuilt in full-Vulca workspace; layout QA reported 0 errors. |
| 8 | Converted `Experiment Lab` into `Ablation Proof`, explicitly naming prompt-only, full Vulca, and bad-data observed signals. | Rebuilt in full-Vulca workspace; layout QA reported 0 errors. |
| 10 | Updated the decision table rows and footer decision to state `reviewed-public-blocked`, positive internal memory signal, degraded negative control, and native-render/human-review blockers. | Rebuilt in full-Vulca workspace; layout QA reported 0 errors. |

## Rebuild Evidence

- Build script: `/Users/yhryzy/.codex/plugins/cache/openai-primary-runtime/presentations/26.521.10419/skills/presentations/scripts/build_artifact_deck.mjs`
- Repaired PPTX: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-full-vulca/output/ppt-run1-5-full-vulca.pptx`
- Repaired contact sheet: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-full-vulca/preview/contact-sheet.png`
- Repaired layout JSON: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-full-vulca/layout/final`
- Delivery report: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-full-vulca/qa/delivery_report.md`

## Structural QA

- Layout QA: 10 layout files checked, 0 errors, 25 warnings.
- PPTX integrity: `unzip -t` passed with no compressed-data errors.
- Media check: no `ppt/media/` entries.
- Delivery QA: `internal-demo-ok-public-blocked`.

## Remaining Gates

- Native PowerPoint, Keynote, or Google Slides visual fidelity render has not been executed.
- Human review has not approved the deck.
- Public publishing remains blocked.
