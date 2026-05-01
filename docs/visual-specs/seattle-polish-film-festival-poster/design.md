---
slug: seattle-polish-film-festival-poster
status: resolved
schema_version: "0.1"
domain: poster
tradition: null
generated_by: visual-spec@0.1.0
proposal_ref: docs/visual-specs/seattle-polish-film-festival-poster/proposal.md
created: 2026-05-01
updated: 2026-05-01
---

# Seattle Polish Film Festival Poster

## A. Provider + generation params

```yaml
reviewed: true
provider: openai
seed: 1337
steps: 30
cfg_scale: 7.5
```

## B. Composition strategy

```yaml
reviewed: true
strategy: series
variation_axis: "adapt one key-art system from 11 x 17 vertical poster to program cover"
variant_count: 2
```

## C. Prompt composition

```yaml
reviewed: true
style_treatment: unified
base_prompt: >-
  Signature key-art poster concept for the 34th Seattle Polish Film Festival,
  vertical 11 x 17 inch poster composition, contemporary Polish cinema mood,
  one strong readable visual idea, clear hierarchy with protected title/date
  area, reserved lower sponsor/patron band, print-aware margins, restrained
  cultural specificity, arts-festival sophistication, no flag-only concept.
negative_prompt: ""
tradition_tokens: []
color_constraint_tokens: []
sketch_integration: ignore
ref_integration: none
```

## D2. Thresholds + batch + rollback

```yaml
reviewed: true
L1_threshold:          {value: 0.7, source: assumed, confidence: low}
L2_threshold:          {value: 0.7, source: assumed, confidence: low}
L3_threshold:          {value: 0.6, source: assumed, confidence: low}
L4_threshold:          {value: 0.55, source: assumed, confidence: low}
L5_threshold:          {value: 0.5, source: assumed, confidence: low}
batch_size:            {value: 4, source: assumed, confidence: med}
rollback_trigger:      {value: "2 consecutive outputs with unsafe text layout or missing sponsor band", source: assumed, confidence: med}
override_rationale: null
```

## F. Cost budget

```yaml
reviewed: true
per_gen_sec: {value: 45, source: assumed, confidence: low}
total_session_sec: {value: 270, source: derived, confidence: low}
fail_fast_consecutive: {value: 2, source: assumed, confidence: low}
provider_used_for_calibration: user-supplied-policy
provider_multiplier_applied: null
```

## Open questions
none

## Notes
- [resume-state] turns_used: 1
- [null-tradition] spike skipped — requires tradition-guide weights for judgment.
- No image provider, redraw provider, evaluator, or spike was invoked by this spec draft.
- `provider: openai` is selected for text/layout-sensitive poster ideation; `/visual-plan` must still verify exact provider/model availability before execution.
- Cost budget is a policy placeholder because no mock or real provider calibration was run in this step.
