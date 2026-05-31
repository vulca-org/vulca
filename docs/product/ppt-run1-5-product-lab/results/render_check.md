# Render Check

Status: reviewed-public-blocked.

Native PowerPoint, Keynote, or Google Slides rendering was not executed. The artifact-tool preview renderer produced PNG previews and contact sheets, and the structural delivery validator checked renderer availability only. The full-Vulca arm was repaired and rebuilt during Task 5.

## Local Workspaces

| Arm | Workspace |
| --- | --- |
| prompt_only | `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-prompt-only` |
| full_vulca | `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-full-vulca` |
| bad_data | `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-bad-data` |

## Structural Checks

| Arm | Slides | Layout QA | PPTX integrity | Media entries | Delivery gate |
| --- | ---: | --- | --- | ---: | --- |
| prompt_only | 10 | `0 error(s)`, 24 warning(s) | `unzip -t` passed with no compressed-data errors | 0 | `internal-demo-ok-public-blocked` |
| full_vulca | 10 | `0 error(s)`, 25 warning(s) after repair | `unzip -t` passed with no compressed-data errors | 0 | `internal-demo-ok-public-blocked` |
| bad_data | 10 | `0 error(s)`, 26 warning(s) | `unzip -t` passed with no compressed-data errors | 0 | `internal-demo-ok-public-blocked` |

## Full-Vulca Repair Evidence

- PPTX: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-full-vulca/output/ppt-run1-5-full-vulca.pptx`
- Contact sheet: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-full-vulca/preview/contact-sheet.png`
- Layout JSON: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-full-vulca/layout/final`
- Delivery report: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e805d-ace6-7490-8141-a3315b6d096d/presentations/ppt-run1-5-full-vulca/qa/delivery_report.md`

## Renderer Availability

| Renderer | Availability |
| --- | --- |
| LibreOffice | not detected |
| Microsoft PowerPoint | not detected |
| Keynote | `/Applications/Keynote.app` |

Renderer availability was checked by `scripts/validate_pptx_delivery.py`. Native render fidelity remains pending, and public publishing remains blocked until human review and native/cross-platform inspection.
