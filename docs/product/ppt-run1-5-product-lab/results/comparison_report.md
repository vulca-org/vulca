# Comparison Report

Status: reviewed-public-blocked.

Run 1.5 now has three generated arms, qualitative Gemini contact-sheet review, one focused full-Vulca repair pass, and structural delivery QA. The full-Vulca arm is the internal comparison winner, but public publishing remains blocked until native/cross-platform render inspection and human approval pass.

Scores are integer 0-5 values. Higher is better for every category; the `rendering risk` column means risk control and structural confidence, not native visual approval.

## Arm Summary

| Arm | Generation status | Review status | PPTX | Contact sheet | Layout JSON | Media entries | Delivery gate |
| --- | --- | --- | --- | --- | --- | ---: | --- |
| prompt_only | generated | reviewed | `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-prompt-only/output/ppt-run1-5-prompt-only.pptx` | `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-prompt-only/preview/contact-sheet.png` | `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-prompt-only/layout/final` | 0 | `internal-demo-ok-public-blocked` |
| full_vulca | generated-repaired | reviewed | `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-full-vulca/output/ppt-run1-5-full-vulca.pptx` | `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-full-vulca/preview/contact-sheet.png` | `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-full-vulca/layout/final` | 0 | `internal-demo-ok-public-blocked` |
| bad_data | generated | reviewed | `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-bad-data/output/ppt-run1-5-bad-data.pptx` | `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-bad-data/preview/contact-sheet.png` | `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-bad-data/layout/final` | 0 | `internal-demo-ok-public-blocked` |

## Scores

| Arm | Commercial clarity | Learning evidence | Product-surface feel | Visual hierarchy | Editability | QA evidence | Rendering risk | Average |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| prompt_only | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 3.29 |
| full_vulca | 4 | 5 | 4 | 4 | 4 | 5 | 4 | 4.29 |
| bad_data | 2 | 2 | 2 | 2 | 3 | 4 | 4 | 2.71 |

## Decision

Full Vulca beats prompt-only by 1.00 average point and beats bad-data by 1.58 average points. The observed signal supports the hypothesis that design evidence, when compiled into memory and slide primitives, affects generated PPT output quality.

The bad-data arm did not break structural output, which is useful for the experiment: it remained editable and delivery-valid while visibly degrading semantic quality, proof density, hierarchy, and source-boundary discipline.

## Blocking Conditions

- Gemini review is qualitative evidence, not final approval.
- Native PowerPoint, Keynote, or Google Slides render fidelity has not been executed.
- Human review has not approved the final deck.
- Public publishing remains blocked.
