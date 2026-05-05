# Tiny Router Baseline Design

Date: 2026-05-05
Status: approved-for-spec

## Purpose

Tiny router baseline v0 defines a deterministic, provider-free policy for
answering one question from existing and future redraw case records:

```json
{
  "recommended_action": "adjust_mask"
}
```

This baseline is not a model and not a runtime agent. It is an evaluation
control group for future tiny models and tiny agents. It should make current
case records immediately useful for benchmark scoring without calling image
providers, training models, generating images, or changing redraw execution.

## Inputs And Output

The input is a `redraw_case` record from Learning Loop v0, plus the advisory
and review fields already embedded in that record:

- case context: `schema_version`, `case_type`, `case_id`, `layer`,
  `instruction`, `provider`, `model`, `artifacts`
- route/advisory signals: `route.requested`, `route.chosen`,
  `route.redraw_route`, `route.geometry_redraw_route`
- geometry signals: `geometry.area_pct`, `geometry.bbox_fill`,
  `geometry.component_count`, `geometry.sparse_detected`
- quality signals: `quality.gate_passed`, `quality.failures`,
  `quality.metrics`
- refinement signals: `refinement.applied`, `refinement.reason`,
  `refinement.strategy`, `refinement.child_count`,
  `refinement.mask_granularity_score`
- human review labels: `review.human_accept`, `review.failure_type`,
  `review.preferred_action`

The required prediction output is:

```json
{
  "recommended_action": "accept"
}
```

`recommended_action` must use the existing `preferred_actions` vocabulary from
`docs/benchmarks/redraw/failure_taxonomy.json`:

- `accept`
- `rerun`
- `fallback_to_agent`
- `fallback_to_original`
- `manual_review`
- `adjust_route`
- `adjust_mask`
- `adjust_instruction`

Future evaluators may add non-label diagnostics such as `policy_name`,
`failure_hint`, `accept_prediction`, and `rule_reason`, but the benchmarked
action field is `recommended_action`.

## Baseline Policies

Tiny router v0 has two explicit rule policies. They answer different benchmark
questions and must not be mixed in aggregate reports.

### `label_oracle`

`label_oracle` is an offline upper-bound policy. It may read
`review.human_accept`, `review.failure_type`, and `review.preferred_action`.
It is useful for validating the action vocabulary and measuring how much of the
benchmark can be solved once the failure label is known.

Precedence:

1. If `review.human_accept` is `true`, recommend `accept`.
2. If `review.preferred_action` is non-empty, recommend that action.
3. Otherwise map `review.failure_type` to an action.
4. If no review label is present, recommend `manual_review`.

Required v0 mappings:

| Failure type | `recommended_action` |
| --- | --- |
| `mask_too_broad` | `adjust_mask` |
| `route_error` | `adjust_route` |
| `pasteback_mismatch` | `manual_review` |
| `over_split` | `fallback_to_original` |
| `under_split` | `fallback_to_agent` |

Default failure mappings:

| Failure type | `recommended_action` |
| --- | --- |
| `alpha_expansion` | `adjust_mask` |
| `background_bleed` | `adjust_mask` |
| `large_white_component` | `adjust_mask` |
| `wrong_subject` | `adjust_instruction` |
| `missing_detail` | `adjust_instruction` |
| `color_drift` | `rerun` |
| `shape_collapse` | `rerun` |
| `over_smoothing` | `rerun` |
| `texture_leak` | `rerun` |
| `uncertain` | `manual_review` |

### `observable_signal`

`observable_signal` is the deployable-style baseline. It must never read
`review.*`. It uses only the case record, route/advisory, geometry, quality,
refinement, artifact, and pasteback/review-state signals that would be
available before a human label exists.

Precedence:

1. If a source pasteback error exists, or pasteback is expected but missing,
   recommend `manual_review`.
2. If route fields disagree in a way that indicates the requested or chosen
   route did not match geometry, recommend `adjust_route`.
3. If quality failures or metrics show broad, expanded, or bleeding alpha,
   recommend `adjust_mask`.
4. If target-aware refinement was expected but not applied, or child count is
   zero for a broad small-target mask, recommend `adjust_mask`.
5. If `quality.gate_passed` is `true` and `artifacts.source_pasteback_path` is
   present, recommend `accept`.
6. If `quality.gate_passed` is `false` but there is no clear mask or route
   cause, recommend `rerun`.
7. If quality is missing or signals are inconclusive, recommend
   `manual_review`.

Signal aliases should normalize implementation-level quality names into the
taxonomy before routing:

| Observable signal | Failure hint | `recommended_action` |
| --- | --- | --- |
| `mask_too_broad_for_target` | `mask_too_broad` | `adjust_mask` |
| `alpha_bbox_expanded` | `alpha_expansion` | `adjust_mask` |
| `background_bleed` | `background_bleed` | `adjust_mask` |
| `large_white_component` | `large_white_component` | `adjust_mask` |
| route/requested/chosen mismatch | `route_error` | `adjust_route` |
| missing or failed pasteback preview | `pasteback_mismatch` | `manual_review` |

The signal baseline is intentionally conservative. It should prefer
`manual_review` over pretending that weak evidence is a confident accept.

## Tiny Model And Tiny Agent Boundary

Tiny models will learn narrow judgments from case records and labels:

- classify failure
- predict accept/reject
- recommend next action

Tiny agents will make sequential tool decisions after those judgments exist:

- choose the tool/action sequence
- decide whether to rerun, adjust prompt, adjust mask, split, merge, fallback,
  or escalate
- stop before provider calls unless the caller explicitly runs an execution
  workflow

The baseline does not perform agent planning. It emits one recommended next
action so future tiny models and agents have a stable rule-based comparison.

## Benchmark And Eval Plan

Primary data sources:

- JSONL files containing `redraw_case` records from Learning Loop v0.
- `docs/benchmarks/redraw/seed_manifest.json` for small seeded cases and
  taxonomy coverage.
- `docs/benchmarks/redraw/failure_taxonomy.json` as the authoritative enum
  source for allowed failures and actions.

Evaluation splits:

- Seed manifest sanity set: small, hand-readable, used for contract tests.
- Reviewed case set: records with `review.human_accept`,
  `review.failure_type`, or `review.preferred_action`.
- Unreviewed case set: records without labels, used only for coverage and
  routing distribution checks.

Required metrics:

- action accuracy against `review.preferred_action` when present
- accept/reject accuracy against `review.human_accept` when present
- failure classification accuracy and macro F1 when a policy emits
  `failure_hint`
- confusion matrix by failure type and recommended action
- policy coverage: fraction of cases with a non-empty `recommended_action`
- `manual_review` rate and escalation rate
- leakage check: `observable_signal` evaluation must fail if any `review.*`
  field is accessed

Provider and training constraints:

- Do not call image providers.
- Do not generate images.
- Do not train models.
- Do not add CLIP, DINO, VLM, LightGBM, or other ML dependencies for this
  baseline.
- Do not change redraw, decomposition, layered generation, CLI, or MCP runtime
  behavior.

## Success Criteria

A successful v0 baseline spec lets a future implementation score deterministic
router policies against existing `redraw_case` JSONL records, compare those
policies with future tiny models, and keep oracle-label evaluation separate
from deployable signal-only evaluation. The first implementation should be a
small offline benchmark harness, not a provider-facing runtime change.
