# PPT Run 2.6R Visual Repair Design

**Status:** draft for user review
**Date:** 2026-06-01
**Branch:** `codex/vulca-ppt-case-pack`

## Problem

Run 2.6 correctly added data/workflow evidence, but the full-skill visual output still looks like Run 2.5. The trace changed; the picture mostly did not.

That means Run 2.6 is valid as a workflow proof but weak as a visual proof. The next pass must repair the existing Run 2.6 stage rather than advance to Run 3.0.

```text
Run 2.6R = same Run 2.6 data/workflow contracts + visible visual repair
```

## Decision

Run 2.6R must keep the same four-arm experiment:

- `prompt_only`
- `run1_5_skill`
- `run2_6r_visual_repair_full_skill`
- `bad_aesthetic_memory`

The repair should change only the full-skill arm's visual system and trace/result records. The control arms remain useful precisely because they should not improve.

Run 2.6R succeeds only if the full-skill arm is visually distinguishable from Run 2.5 and Run 2.6 in both required comparison images:

- four-arm contact sheet;
- full-skill-series horizontal comparison.

## Non-Goals

- Do not advance to Run 3.0.
- Do not change the research/data layer unless a visual rule needs a stricter field.
- Do not claim public-ready quality.
- Do not copy Figma, Stripe, Google, Apple, Duarte, SlideModel, or any other source brand identity.
- Do not replace the PPT with image generation. The main output remains code-generated, native editable PPT. Backgrounds or illustration accents may be generated/SVG, but text, hierarchy, diagrams, mini-previews, and proof objects must stay native.

## Failure Diagnosis

Run 2.6 failed the visual-delta expectation for four reasons:

1. **Typography was inherited.** The full arm still uses the Run 2.5 title/body scale and does not express the selected typography policy.
2. **Spacing was inherited.** The full arm still uses the same macro layout rhythm and does not visibly apply spacing-token decisions.
3. **Climax composition was inherited.** The climax slide remains the same dark hero-object pattern, so the new workflow policy is invisible.
4. **Theme differentiation was too shallow.** The full arm reuses the Run 2.5 deep green/off-white system instead of deriving a new theme from the selected usecase and benchmark policy.

Gemini artifact review of the Run 2.0-2.6 full-skill series independently observed that Runs 2.4-2.6 share the same dark green/off-white editorial system, with Run 2.6 mostly extending the pattern rather than changing it.

## Repair Principles

Run 2.6R should make the selected workflow policy visible through native PPT construction.

### 1. Typography Must Carry The Workflow

The repaired full arm must introduce a distinct editorial type system:

- cover headline uses a stronger type contrast than Run 2.5;
- slide subtitles become shorter and more decisive;
- support labels are reduced, grouped, or moved into trace-like marginal notes;
- the selected `typography_system_id` appears in trace and corresponds to visible type scale.

Expected visual effect: the deck reads less like an engineering report and more like a designed public-facing product presentation.

### 2. Spacing Must Create Editorial Rhythm

The repaired full arm must introduce visible spacing-token behavior:

- each slide has a clear focal zone, support zone, and trace/provenance zone;
- outer margins and gutters differ by slide role;
- the climax slide receives the largest visual field;
- mini-preview slides use tighter internal precision but larger external whitespace.

Expected visual effect: the viewer can scan the contact sheet and see intentional rhythm, not repeated template reuse.

### 3. Climax Must Be Re-Composed

The climax slide must be rebuilt rather than recolored.

Required change:

- no reuse of the Run 2.5/2.6 hero-object layout;
- the hero object must become an editorial proof spread with one dominant before/after or workflow-to-output transformation;
- the result object must have stronger scale separation from supporting elements;
- secondary detail must be routed to a side rail or bottom proof strip.

Expected visual effect: slide 05 should be the most visibly different slide in the full-skill-series comparison.

### 4. Theme Must Be Derived From Usecase And Benchmark

The repaired full arm must use a new original theme policy derived from:

- `usecase_design_to_production_platform_launch`;
- `benchmark_visual_fidelity_interactive_slide_surface`;
- `benchmark_design_to_production_grid_precision`;
- `benchmark_glance_test_visual_hierarchy`.

The theme should avoid another forest-green product-system look. It should still feel premium and serious, but must use a different palette and material behavior.

Recommended direction:

- light-first editorial canvas;
- dark ink / graphite structural elements;
- one vivid proof color;
- subtle cool material surfaces for mini-previews;
- no source-brand color mimicry.

## Visual System Requirements

### Full Arm Slide Requirements

| Slide | Role | Required Visual Repair |
| --- | --- | --- |
| 01 | Cover | New light-first editorial opening; big promise, native generated proof object, no Run 2.5 dark cover reuse. |
| 02 | Setup | Workflow selection visible as a compact decision surface; usecase/benchmark/policy must be shown as selected states, not paragraphs. |
| 03 | Contrast | Before/after must be larger and more editorial; the "after" side should show clear native PPT construction. |
| 04 | Proof | Route data -> benchmark -> policy -> module as a visual path; remove equal card patterns. |
| 05 | Climax | Rebuilt editorial proof spread; biggest visual object in the deck; visibly different from Run 2.5/2.6. |
| 06 | Gate | Release gate should feel like a product handoff surface, not another dark report slide. |

### Control Arm Requirements

Control arms should remain structurally valid but not visually repaired:

- `prompt_only`: no Run 2.6R workflow artifacts;
- `run1_5_skill`: no Run 2.6R workflow artifacts;
- `bad_aesthetic_memory`: may receive `commercial_usecase_bank.json`, but must not receive the good benchmark, theme, typography, spacing, or repair policy artifacts.

## New Or Updated Artifacts

Run 2.6R should add one small repair-policy artifact rather than rewriting all data:

### `visual_repair_policy.json`

Purpose: connect existing Run 2.6 workflow policy to visible generator decisions.

Required fields:

- `status`: `run2_6r_visual_repair_policy_public_blocked`
- `stage_policy`: `repeat_same_five_layers_not_run3`
- `repairs`: list of repair records
- each repair record includes:
  - `id`
  - `target_slide_roles`
  - `source_policy_ids`
  - `typography_delta`
  - `spacing_delta`
  - `composition_delta`
  - `theme_delta`
  - `must_differ_from`
  - `native_ppt_requirements`
  - `qa_probe`
  - `release_boundary`

Required repair ids:

- `repair_editorial_typography_system`
- `repair_spacing_token_visibility`
- `repair_climax_editorial_spread`
- `repair_theme_differentiation_from_run2_5`
- `repair_mini_preview_fidelity`

## Generator Requirements

Create `scripts/generate_ppt_run2_6r_visual_repair_arms.mjs` from the Run 2.6 generator, but do not preserve the full arm visual template.

Required generator behavior:

- output slugs use `ppt-run2-6r-*`;
- full arm id is `run2_6r_visual_repair_full_skill`;
- full arm allows `visual_repair_policy.json`;
- prompt-only and Run 1.5 forbid `visual_repair_policy.json`;
- bad-memory forbids `visual_repair_policy.json`;
- full arm trace records `visual_repair_policy_ids`, `visual_delta_from_run2_5`, and `visual_repair_validation_probe`;
- generated full arm uses new drawing functions for cover, setup, contrast, proof, climax, and close.

Do not only rename `run2_6_full_skill` to `run2_6r_visual_repair_full_skill`. The full arm drawing functions must change.

## QA Requirements

Run 2.6R must keep the existing gates:

- layout QA;
- delivery QA;
- trace refresh;
- Gemini artifact review;
- public blocked unless native render and human approval pass.

It must also add visual-delta QA:

- full arm trace contains all Run 2.6 data/workflow fields;
- full arm trace contains repair policy ids;
- contact sheet path exists for all four arms;
- full-skill-series image includes Run 2.6R after Run 2.6;
- comparison report states that Run 2.6R is a visual repair pass, not a new stage.

## Acceptance Criteria

Run 2.6R is accepted as an internal visual repair if:

1. The full arm is visibly distinct from Run 2.5 and Run 2.6 in the full-skill-series image.
2. Slide 05 has a rebuilt editorial climax composition.
3. Typography scale and spacing rhythm are visibly different from Run 2.5.
4. Mini-previews look like intentional native PPT product surfaces rather than placeholders.
5. All text and visual structure remain native editable PPT objects where practical.
6. Prompt-only and Run 1.5 do not gain access to Run 2.6R repair policy.
7. Bad-memory remains a negative control and does not receive good repair policy.
8. Results remain public blocked.

## Testing Strategy

Add tests before implementation:

1. `test_run2_6r_has_visual_repair_policy`
   - validates `visual_repair_policy.json` fields and repair ids.
2. `test_run2_6r_generator_consumes_visual_repair_policy_and_preserves_boundaries`
   - validates allowed/forbidden input boundaries.
3. `test_run2_6r_trace_records_visual_repair_fields`
   - validates `visual_repair_policy_ids`, `visual_delta_from_run2_5`, and `visual_repair_validation_probe`.
4. `test_run2_6r_records_visual_repair_rerun_result`
   - validates result JSON/MD and public-blocked status.

Existing tests should continue to pass.

## Result Recording

Create:

- `results/run2_6r_visual_repair_result.json`
- `results/run2_6r_visual_repair_result.md`

Update:

- `results/README.md`
- `results/comparison_report.md`
- `results/delivery_gate.md`

The result must say:

- Run 2.6R is a same-stage visual repair;
- full arm is best internal visual-repair arm only if the visual delta is visible;
- public-ready remains false;
- generated outputs remain untracked;
- next step is either another same-stage repair or native/human review, not Run 3.0.

## Open Question For User Review

The implementation should default to a light-first editorial system with graphite structure and one vivid proof color. If the user wants a different visual direction, revise this spec before implementation.
