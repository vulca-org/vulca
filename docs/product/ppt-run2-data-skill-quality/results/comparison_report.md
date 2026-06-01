# Comparison Report

Status: rerun-reviewed-public-blocked.

Run 2.1 has now been regenerated as a four-arm local experiment. The result is clear but bounded:

- `run2_1_full_skill` wins on product learning: tutorial/case observations now become executable rules, guards, and QA probes.
- It does not yet win as a public-video-grade presentation: the deck is cleaner and more intentional, but still reads as a product/system proof more than a high-aesthetic public demo.
- The negative control confirms the failure mode: weak aesthetic memory keeps valid PPT structure but flattens the story into dashboard-like process boxes.

| Arm | Generation status | Review status | Delivery gate | Average |
| --- | --- | --- | --- | ---: |
| `prompt_only` | generated | reviewed | `internal-demo-ok-public-blocked` | 2.50 |
| `run1_5_skill` | generated | reviewed | `internal-demo-ok-public-blocked` | 3.17 |
| `run2_skill` | generated | reviewed | `internal-demo-ok-public-blocked` | 4.27 |
| `bad_aesthetic_memory` | generated | reviewed | `internal-demo-ok-public-blocked` | 2.64 |

Public publishing remains blocked until native or cross-platform render inspection and human approval pass.

## Run 2.1 Rerun Score Table

Scores are 0-5 internal pilot scores. They combine local contact-sheet inspection, Gemini artifact review, trace refresh state, structural delivery QA, and layout QA. They are not public-release claims.

| Dimension | `prompt_only` | `run1_5_skill` | `run2_1_full_skill` | `bad_aesthetic_memory` |
| --- | ---: | ---: | ---: | ---: |
| `commercial_specificity` | 3.0 | 3.5 | 4.2 | 3.2 |
| `evidence_alignment` | 1.0 | 4.0 | 4.6 | 3.2 |
| `aesthetic_memory_usage` | 0.0 | 2.0 | 4.2 | 1.0 |
| `visual_hierarchy` | 2.3 | 3.0 | 3.8 | 1.7 |
| `rhythm_variance` | 2.0 | 2.5 | 3.7 | 1.4 |
| `density_control` | 2.8 | 2.4 | 3.6 | 1.6 |
| `public_video_taste` | 1.8 | 2.2 | 3.2 | 1.3 |
| `trace_closure` | 2.0 | 3.8 | 4.5 | 3.5 |
| **Average** | **1.86** | **2.93** | **3.98** | **2.11** |

## Run 2.1 Findings

- `prompt_only`: still useful as a baseline because it can produce valid PPTX files, but it has no learned rules, no runtime aesthetic memory, and no proof that tutorial data changed behavior.
- `run1_5_skill`: better traceability and stronger system framing, but it remains evidence-heavy and table-shaped.
- `run2_1_full_skill`: best evidence that the product learned from data. It uses `extraction_units`, `skill_workflow.json`, and refreshed trace QA to connect source observations to generator behavior.
- `bad_aesthetic_memory`: confirms that bad memory can satisfy structure while damaging taste, hierarchy, and climax.
- Audit correction: Run 2.1 is a stronger product experiment, not a final public deck and not a reason to advance to Run 3.0. The next pass repeats the same five layers and replaces abstract proof boxes with real side-by-side slide diffs, realistic mini-previews, and a visible design transformation.

## Score Table

This is the older Run 2.0 internal score table retained for comparison.

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
- Audit correction: the Run 2.0 arm is the best older internal arm, but the score is superseded by the Run 2.1 rerun for product-learning evidence.

## Review Artifacts

- `.gemini-agent/artifacts/2026-06-01T145003901Z-artifacts.json`
- `.gemini-agent/artifacts/2026-06-01T145015548Z-artifacts.json`
- `.gemini-agent/artifacts/2026-06-01T145033149Z-artifacts.json`
- `.gemini-agent/artifacts/2026-06-01T145051076Z-artifacts.json`
- `.gemini-agent/artifacts/2026-06-01T152210085Z-artifacts.json`
- `.gemini-agent/artifacts/2026-06-01T152221854Z-artifacts.json`
- `.gemini-agent/artifacts/2026-06-01T161711306Z-artifacts.json`
- `.gemini-agent/artifacts/2026-06-01T161738825Z-artifacts.json`

## Local Contact Sheets

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-prompt-only/preview/contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-run1-5-skill/preview/contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-full-vulca/preview/contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-bad-aesthetic-memory/preview/contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-1-prompt-only/preview/contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-1-run1-5-skill/preview/contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-1-full-vulca/preview/contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-1-bad-aesthetic-memory/preview/contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-1-four-arm-contact-sheet.png`

## Blockers

- Trace QA outcome refresh has been written back for the regenerated local Run 2.1 arms; those outputs remain untracked under `outputs/`.
- Native PowerPoint, Keynote, or Google Slides render inspection has not passed.
- Human approval has not been recorded.
- Public-video-grade visual proof is still weak: the current best arm uses abstract diagrams instead of real slide diffs or realistic design previews.
- Public-ready status is therefore blocked.
