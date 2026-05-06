# External Dataset Intake Catalog v1

## Status

ready

## Goal

Create a reviewed catalog of external public datasets that could expand Vulca's
learning cases without silently mixing unreviewed public data into the default
training/eval path.

## Scope

- Add `docs/benchmarks/learning/external_dataset_catalog_v1.json`.
- Track each dataset's license, license risk, supervision kind, target Vulca
  case type, candidate field mapping, recommended use, and intake status.
- Keep every external dataset out of default training until it has been
  converted into reviewed Vulca case logs.
- Add focused tests for the catalog safety contract.

## Non-goals

- Do not download external images or annotations.
- Do not create external candidate JSONL in this branch.
- Do not change the default tiny training/eval gate inputs.
- Do not train or tune a model from external data yet.

## Pilot Order

1. MagicBrush -> redraw candidate cases.
2. ADE20K -> decompose candidate cases.
3. ImageRewardDB -> layer generation quality/preference candidate cases.

Each pilot should sample at most 300 records, write
`external_candidate_cases.jsonl`, and require manual review before producing a
reviewed case source manifest.

## Effectiveness Gate

External data is useful only if it improves coverage without hurting the real
workflow holdout. The gate should compare:

- `preferred_action` accuracy.
- failure-type macro coverage.
- accept/reject precision.
- regression count on `local + manual + real_user` cases.
- bucket coverage for redraw, decompose, and layer generation.
