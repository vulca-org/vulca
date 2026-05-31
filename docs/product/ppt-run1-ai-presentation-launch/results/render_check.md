# Render Check

Status: baseline and Vulca case-pack deck checked.

## Renderer Availability

Renderer: not available; artifact-tool preview and layout JSON used for Run 1 automated review.

Command:

```bash
if command -v libreoffice >/dev/null 2>&1; then
  echo "Renderer: libreoffice available" > /tmp/ppt-run1-render-check.txt
else
  echo "Renderer: not available; artifact-tool preview and layout JSON used for Run 1 automated review" > /tmp/ppt-run1-render-check.txt
fi
```

## Baseline Outputs

- PPTX: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/output/ppt-run1-baseline.pptx`
- Contact sheet: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/preview/contact-sheet.png`
- Preview PNGs: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/preview`
- Layout JSON: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/layout/final`

## Baseline Automated Checks

Build:

```text
slideCount: 10
outputBytes: 44452
contactSheet: /Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/preview/contact-sheet.png
layoutDir: /Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/layout/final
```

Layout QA:

```text
Checked 10 layout file(s): 0 error(s), 0 warning(s).
```

PPTX integrity:

```text
No errors detected in compressed data of /Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/output/ppt-run1-baseline.pptx.
```

Media asset check:

```text
No ppt/media image entries found in the generated PPTX.
```

## Visual Check Notes

The artifact-tool contact sheet was inspected after baseline generation. No obvious clipped text, blank slides, image dependency, or incoherent element overlap was observed in the baseline contact sheet.

LibreOffice was not available in this environment, so no PDF or Office-rendered image export was produced for the baseline deck.

## Vulca Case-Pack Outputs

- PPTX: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/output/ppt-run1-vulca.pptx`
- Contact sheet: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/preview/contact-sheet.png`
- Preview PNGs: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/preview`
- Layout JSON: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/layout/final`

## Vulca Automated Checks

Build:

```text
slideCount: 10
outputBytes: 60497
contactSheet: /Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/preview/contact-sheet.png
layoutDir: /Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/layout/final
```

Layout QA:

```text
Checked 10 layout file(s): 0 error(s), 0 warning(s).
```

PPTX integrity:

```text
No errors detected in compressed data of /Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/output/ppt-run1-vulca.pptx.
```

Media asset check:

```text
No ppt/media image entries found in the generated PPTX.
```

Renderer availability:

```text
Renderer: not available; artifact-tool preview and layout JSON used for Run 1 automated review
```

## Vulca Visual Check Notes

The artifact-tool contact sheet was inspected after the final rebuild. All ten required slides rendered, the sequence follows the deck outline, and no blank slides, clipped text, image dependency, or incoherent element overlap was observed.

LibreOffice was not available in this environment, so no PDF or Office-rendered image export was produced for the Vulca case-pack deck.
