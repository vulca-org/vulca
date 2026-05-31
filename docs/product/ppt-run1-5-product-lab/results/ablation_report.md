# Ablation Report

Status: reviewed.

Run 1.5 tested whether a memory-backed case pack changes generated PPT output versus a prompt-only baseline and a deliberately degraded bad-data arm. The ablation signal is positive for internal product-lab evidence, but it is not public-release approval.

## Input Boundary

| Arm | Input boundary | Expected signal | Observed signal |
| --- | --- | --- | --- |
| prompt_only | `baseline_prompt.md` only; design memory, tutorial notes, Vulca generation brief, and Vulca PPT skill excluded while writing slide modules. | Structurally valid baseline, comparatively generic because it receives only the compact prompt. | Valid editable deck with named experiment arms and gates, but Gemini characterized it as more technical specification/testing dashboard than polished product surface. |
| full_vulca | `vulca_generation_brief.md`, `design_memory.json`, `deck_outline.json`, tutorial-derived rules, and product-lab slide primitives. | Stronger product-lab surfaces: Brief Cockpit, Learning Map, Design Memory Compiler, Experiment Lab, QA Gate, and Product Decision. | Strongest arm. Gemini found a specific technical product-lab run report with schemas, source boundaries, pipeline stages, memory compiler, code-generation anatomy, and QA gate. Focused repair made slide 7 a score delta and slide 8 an ablation proof. |
| bad_data | `bad_data_generation_brief.md` with deliberately weak but structurally valid rules. | Remain structurally valid while visibly weaker through generic card grids, mismatched hierarchy, weak source boundaries, and poor product-surface feel. | Valid editable deck, but semantically degraded: weak generic workflows, poor claim-to-proof relationship, non-committal content, and weaker source-boundary discipline. |

## Expected Signal

The case-pack hypothesis was that design evidence should become design memory, design memory should select stricter slide primitives, and those primitives should produce a more concrete product-lab deck than a prompt-only baseline. The negative control should degrade content quality without relying on broken artifacts.

## Observed Signal

The data-to-rule path appears to affect output:

- Full Vulca scored 4.29 average, above prompt-only at 3.29.
- Bad-data scored 2.71 average, below full Vulca while remaining structurally valid.
- Full Vulca was strongest on learning evidence and QA evidence because the deck exposed the brief cockpit, memory compiler, workflow surface, editable anatomy, QA gate, and decision table.
- Bad-data did not trigger a hard structural failure, but it did trigger semantic warnings through visibly generic workflows and weak proof relationships.

## Remaining Uncertainty

This run is still local and structurally validated only. Gemini review is qualitative evidence, not final approval. Native PowerPoint, Keynote, or Google Slides render fidelity has not been executed, and human review has not approved public publishing.

## Warnings

- Public publishing remains blocked.
- Native/cross-platform render inspection remains required.
- Human review remains required.
- The bad-data arm demonstrates semantic degradation, but it does not yet prove automatic detection of corrupted design memory.
