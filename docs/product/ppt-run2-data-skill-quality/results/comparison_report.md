# Comparison Report

Status: reviewed-public-blocked.

| Arm | Generation status | Review status | Delivery gate | Average |
| --- | --- | --- | --- | ---: |
| `prompt_only` | generated | reviewed | `internal-demo-ok-public-blocked` | 2.50 |
| `run1_5_skill` | generated | reviewed | `internal-demo-ok-public-blocked` | 3.17 |
| `run2_skill` | generated | reviewed | `internal-demo-ok-public-blocked` | 4.27 |
| `bad_aesthetic_memory` | generated | reviewed | `internal-demo-ok-public-blocked` | 2.64 |

Public publishing remains blocked until trace QA outcome refresh, native or cross-platform render inspection, and human approval pass.

## Score Table

Scores are 0-5. They combine Gemini artifact review, contact-sheet inspection, trace-manifest contract checks, structural delivery QA, and layout QA. These are internal pilot scores, not public-release claims. The current local trace manifests are contract-present but require outcome refresh because per-slide QA fields still carry pre-QA `pending` values; they are not public-release evidence.

| Dimension | `prompt_only` | `run1_5_skill` | `run2_skill` | `bad_aesthetic_memory` |
| --- | ---: | ---: | ---: | ---: |
| `commercial_specificity` | 3.0 | 3.5 | 4.5 | 3.5 |
| `evidence_alignment` | 1.0 | 4.0 | 4.5 | 3.8 |
| `aesthetic_memory_usage` | 0.0 | 2.0 | 4.5 | 1.5 |
| `visual_hierarchy` | 2.5 | 3.0 | 4.2 | 1.5 |
| `rhythm_variance` | 2.0 | 2.5 | 4.2 | 1.5 |
| `density_control` | 3.0 | 2.5 | 4.0 | 1.0 |
| `asset_discipline` | 4.0 | 4.0 | 4.5 | 3.5 |
| `editability` | 4.0 | 4.0 | 4.5 | 4.0 |
| `render_risk` | 3.0 | 3.0 | 3.5 | 3.0 |

## Review Findings

- `prompt_only`: structurally valid and useful as a baseline, but it lacks runtime rules, source cards, aesthetic memory, asset policy, and a meaningful visual climax.
- `run1_5_skill`: stronger evidence traceability than prompt-only, but the deck remains table-shaped and report-like.
- `run2_skill`: visibly stronger rhythm, lower density, clearer public-demo gate, and a real visual peak on the measured-result slide.
- `bad_aesthetic_memory`: successfully degrades into dense process boxes, equal-weight comparisons, and no visual climax while keeping a valid PPTX structure.
- Audit correction: the Run 2.0 arm is the best internal arm, but the score is not public-release evidence until trace QA outcome refresh, native render inspection, and human approval pass.

## Review Artifacts

- `.gemini-agent/artifacts/2026-06-01T145003901Z-artifacts.json`
- `.gemini-agent/artifacts/2026-06-01T145015548Z-artifacts.json`
- `.gemini-agent/artifacts/2026-06-01T145033149Z-artifacts.json`
- `.gemini-agent/artifacts/2026-06-01T145051076Z-artifacts.json`
- `.gemini-agent/artifacts/2026-06-01T152210085Z-artifacts.json`
- `.gemini-agent/artifacts/2026-06-01T152221854Z-artifacts.json`

## Local Contact Sheets

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-prompt-only/preview/contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-run1-5-skill/preview/contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-full-vulca/preview/contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-bad-aesthetic-memory/preview/contact-sheet.png`

## Blockers

- Trace QA outcome refresh has not been written back into local `trace_manifest.json` files after validation.
- Native PowerPoint, Keynote, or Google Slides render inspection has not passed. A Keynote export attempt failed with error `-609`.
- Human approval has not been recorded.
- Public-ready status is therefore blocked.
