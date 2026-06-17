# PPT Delivery QA Report

This report is structural delivery QA. It does not prove native PowerPoint, Keynote, or Google Slides visual fidelity.

## Summary

- Baseline delivery gate: `internal-demo-ok-public-blocked`
- Vulca delivery gate: `internal-demo-ok-public-blocked`
- Hard errors: `0`
- Public publishing: blocked until human review and native/cross-platform inspection.

## Run 1 Baseline Deck

- Delivery gate: `internal-demo-ok-public-blocked`
- PPTX: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/output/ppt-run1-baseline.pptx`
- Layout JSON: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/layout/final`
- Contact sheet: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/preview/contact-sheet.png`
- Slide count: `10`
- Layout file count: `10`
- Media entries: `0`
- Human review required: `True`

### Renderer Availability

- libreoffice: `not detected`
- powerpoint: `not detected`
- keynote: `/Applications/Keynote.app`

### Issues

- `warning` `native_render_not_run`: Renderer availability was checked, but no native PowerPoint, Keynote, or Google Slides render was executed.

### Gate Notes

- Errors: `0`
- Warnings: `1`
- Public publishing remains blocked until human review and native/cross-platform inspection.

## Run 1 Vulca Case-Pack Deck

- Delivery gate: `internal-demo-ok-public-blocked`
- PPTX: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/output/ppt-run1-vulca.pptx`
- Layout JSON: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/layout/final`
- Contact sheet: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/preview/contact-sheet.png`
- Slide count: `10`
- Layout file count: `10`
- Media entries: `0`
- Human review required: `True`

### Renderer Availability

- libreoffice: `not detected`
- powerpoint: `not detected`
- keynote: `/Applications/Keynote.app`

### Issues

- `warning` `native_render_not_run`: Renderer availability was checked, but no native PowerPoint, Keynote, or Google Slides render was executed.

### Gate Notes

- Errors: `0`
- Warnings: `1`
- Public publishing remains blocked until human review and native/cross-platform inspection.

## Next Adapter

The next adapter should execute at least one native render or inspection path and compare it against the artifact-tool preview surface. The first target should be Microsoft PowerPoint 365 because the generated artifact is `.pptx`.
