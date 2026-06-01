# PPT Run 2.6 Data And Workflow Thickening Design

**Status:** draft for user review
**Date:** 2026-06-01
**Branch:** `codex/vulca-ppt-case-pack`

## Decision

Run 2.6 should deepen the same five-layer loop rather than add a new stage:

```text
real commercial case
-> multimodal tutorial / case / video data
-> evidence + aesthetic + asset memory
-> skill workflow
-> rerun and evaluation
```

Run 2.5 proved that production reference decompositions, aesthetic memory v2, and visual production modules can visibly change the generated PPT. It did not prove public-video-grade quality. Run 2.6 should therefore thicken the data and workflow layer before changing the generator again.

The next rerun should be driven by explicit usecase selection and benchmark selection:

```text
commercial usecase
-> aesthetic benchmark
-> theme / typography / spacing policy
-> production module selection
-> code-generated PPT
-> trace + QA + contact-sheet comparison
```

## Research Inputs

The sources below are used as public references for derived observations only. They are not asset sources.

| Source id | Source | Role in Run 2.6 |
| --- | --- | --- |
| `figma_config_2025_platform_launch` | https://www.figma.com/blog/config-2025-press-release/ | Design-to-production platform launch; multiple products introduced under one narrative. |
| `figma_config_2025_recap` | https://www.figma.com/blog/config-2025-recap/ | Craft, grid precision, design-to-production workflow, brand artifact scale. |
| `figma_slides_product` | https://www.figma.com/slides/ | Presentation product reference: visual fidelity, collaboration, interaction. |
| `figma_slides_help` | https://help.figma.com/hc/en-us/articles/24170630629911-Explore-Figma-Slides | Slide workflow reference: templates, simplified slide mode, interactive elements. |
| `stripe_sessions_2025_product_keynote` | https://stripe.com/gb/sessions/2025/product-keynote | Fintech/commerce product keynote with multiple launch surfaces and business usecases. |
| `google_cloud_next_2025_wrap` | https://cloud.google.com/blog/topics/google-cloud-next/google-cloud-next-2025-wrap-up/?hl=en | Large-scale AI/cloud keynote with customer proof and demos. |
| `google_cloud_next_2025_sundar` | https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/google-cloud-next-2025-sundar-pichai-keynote/ | Executive AI platform narrative and product capability framing. |
| `apple_liquid_glass_newsroom` | https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/ | Design-language launch reference: dynamic material, cross-platform consistency, content-first surface behavior. |
| `apple_liquid_glass_developer` | https://developer.apple.com/videos/play/wwdc2025/219/ | Design principles reference: dynamic and expressive user experience, where and why to use a material. |
| `duarte_slide_design` | https://www.duarte.com/training/slide-document-design/slide-design/ | Presentation training reference: visual story, audience attention, glance-power, data story. |
| `duarte_visual_storytelling` | https://www.duarte.com/resources/webinars-videos/persuasive-visual-storytelling/ | Storytelling and data emphasis reference. |
| `slidemodel_visual_hierarchy` | https://slidemodel.com/visual-hierarchy-for-presentations/ | Visual hierarchy reference: F-pattern/Z-pattern, typography, contrast, whitespace, positioning. |

## Copyright And Provenance Boundary

Run 2.6 must not copy source visuals, source layouts, screenshots, frames, brand marks, event graphics, full transcripts, course material, proprietary templates, or long prose.

Each reference may only produce:

- short source metadata;
- derived observations;
- usecase constraints;
- aesthetic rules;
- QA probes;
- original native PPT module implications.

The generator must sanitize output so the final deck does not look like an Apple, Stripe, Figma, Google, Duarte, or SlideModel artifact. Reference brand names may appear in trace and research docs; they should not appear as final slide branding unless the deck is explicitly about the reference itself.

## New Data Contracts

### `commercial_usecase_bank.json`

Purpose: convert public commercial references into concrete presentation jobs.

Required usecases:

| Usecase id | Commercial need | Primary sources |
| --- | --- | --- |
| `usecase_design_to_production_platform_launch` | Explain an AI/design platform that moves from idea to production; prove craft and workflow, not only feature count. | Figma Config 2025 sources, Figma Slides sources. |
| `usecase_fintech_product_keynote` | Launch multiple commerce/finance capabilities to executive and developer audiences; show product breadth without becoming a feature grid. | Stripe Sessions 2025 Product Keynote. |
| `usecase_ai_cloud_keynote_demo` | Present an AI platform with infrastructure, model capability, customer proof, and demos; preserve scale and credibility. | Google Cloud Next 2025 sources. |
| `usecase_design_language_public_reveal` | Introduce a visual system or design language; make the design itself the proof object. | Apple Liquid Glass sources. |

Each usecase must store:

- `source_ids`;
- `audience`;
- `business_decision`;
- `deck_mission`;
- `slide_arc`;
- `must_show`;
- `must_not_show`;
- `failure_modes`;
- `visual_risk`;
- `workflow_implications`;
- `qa_probe`;
- `release_boundary`.

### `aesthetic_benchmark_bank.json`

Purpose: convert excellent references into original, executable visual rules.

Required benchmark families:

- `benchmark_design_to_production_grid_precision`
- `benchmark_visual_fidelity_interactive_slide_surface`
- `benchmark_fintech_keynote_breadth_without_grid`
- `benchmark_ai_platform_demo_climax`
- `benchmark_content_first_dynamic_material`
- `benchmark_glance_test_visual_hierarchy`
- `benchmark_story_driven_data_emphasis`

Each benchmark must store:

- `source_ids`;
- `allowed_use`;
- `composition_rules`;
- `typography_rules`;
- `spacing_rules`;
- `theme_rules`;
- `motion_or_interaction_rules`;
- `native_ppt_implications`;
- `anti_copy_rules`;
- `qa_probe`;
- `trace_fields`;
- `release_boundary`.

### `workflow_decision_policy.json`

Purpose: make data selection executable rather than decorative.

The policy should define this selection chain:

```text
commercial_case
-> usecase_id
-> benchmark_ids
-> theme_policy_id
-> typography_system_id
-> spacing_token_set_id
-> visual_production_module_ids
-> QA probes
```

The policy must include:

- allowed mappings from usecase to benchmark;
- light/dark theme selection rules;
- typography scale constraints;
- spacing token constraints;
- module selection rules;
- forbidden source-brand imitation rules;
- fallback behavior;
- trace fields required before generation;
- QA gates required after generation.

## Workflow Changes

Update `skill_workflow.json` with Run 2.6 stages:

1. `select_commercial_usecase`
   - Inputs: `commercial_case.md`, `commercial_usecase_bank.json`
   - Output: selected `usecase_id`
   - Gate: selected usecase is concrete and references valid sources.

2. `select_aesthetic_benchmarks`
   - Inputs: `aesthetic_benchmark_bank.json`, selected `usecase_id`
   - Output: selected `benchmark_ids`
   - Gate: benchmarks are allowed for the selected usecase.

3. `select_theme_typography_spacing_policy`
   - Inputs: `workflow_decision_policy.json`, selected `benchmark_ids`
   - Output: `theme_policy_id`, `typography_system_id`, `spacing_token_set_id`
   - Gate: source-brand imitation is forbidden and fallback is defined.

4. Existing production-module selection
   - Inputs now include selected usecase, benchmarks, theme, type, and spacing policy.
   - Output still selects native editable visual modules.

5. Existing generation and QA
   - Trace must record selected usecase, benchmark, theme, typography, spacing, and workflow decision ids.
   - QA must check the selected policy against the contact sheet.

## Trace Additions

Run 2.6 traces should add these per-arm or per-slide fields:

- `commercial_usecase_id`;
- `aesthetic_benchmark_ids`;
- `theme_policy_id`;
- `typography_system_id`;
- `spacing_token_set_id`;
- `workflow_decision_ids`;
- `source_brand_sanitization`;
- `benchmark_validation_probe`;
- `theme_validation_probe`.

The control arms must keep these fields empty or explicitly forbidden. The full arm must record them. The bad aesthetic memory arm may keep `commercial_usecase_id` but must not receive the good benchmark, theme, typography, or spacing policy.

## Testing Strategy

Before changing the generator:

1. Add schema/cross-reference tests for `commercial_usecase_bank.json`.
2. Add schema/cross-reference tests for `aesthetic_benchmark_bank.json`.
3. Add schema/cross-reference tests for `workflow_decision_policy.json`.
4. Add workflow tests requiring the new selection stages in `skill_workflow.json`.
5. Add trace contract tests requiring the new fields.
6. Add generator source tests once `generate_ppt_run2_6_arms.mjs` exists.

Generator tests should assert:

- prompt-only and Run 1.5 forbid Run 2.6 usecase/benchmark/policy data;
- full arm allows all Run 2.6 artifacts;
- bad aesthetic memory receives the commercial usecase but not good benchmark/theme/type/spacing policies;
- trace records source-brand sanitization and selected policy ids.

## Rerun Requirements

After data and workflow tests pass:

1. Create `scripts/generate_ppt_run2_6_arms.mjs`.
2. Rerun four arms:
   - `prompt_only`
   - `run1_5_skill`
   - `run2_6_full_skill`
   - `bad_aesthetic_memory`
3. Run layout QA, delivery QA, trace refresh, Gemini artifact review, and human review.
4. Produce two mandatory images:
   - four-arm contact sheet;
   - full-skill-series horizontal comparison.
5. Record results as public blocked unless native render and human approval pass.

## Acceptance Criteria

Run 2.6 succeeds as a data/workflow thickening pass if:

- new data files pass schema and referential-integrity tests;
- workflow stages prove usecase and benchmark are selected before module generation;
- full arm trace records usecase, benchmark, theme, typography, spacing, and workflow decisions;
- bad aesthetic memory proves the negative control boundary still holds;
- generated full arm visibly changes because of the selected usecase/benchmark policy;
- docs avoid public-ready claims;
- outputs remain untracked under `outputs/`;
- the two required comparison images are generated for review.

Run 2.6 still fails public release if:

- native render has not passed;
- human visual approval is missing;
- output imitates a source brand too closely;
- typography, spacing, or theme policy is recorded but not visible;
- climax remains weaker than proof/setup slides.

## Open User Decision

Recommended scope: implement Run 2.6 in two commits.

1. Data/workflow commit: add the new banks, workflow policy, workflow stages, trace contract, and tests.
2. Rerun commit: add generator, run four arms, QA, Gemini review, two images, and result docs.

This keeps data/workflow quality auditable before visual generation starts.
