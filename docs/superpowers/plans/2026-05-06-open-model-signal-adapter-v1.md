# Open Model Signal Adapter v1

Status: implemented

## Goal

Create the first safe bridge from the open-source model catalog into Vulca learning cases. The adapter prepares reviewable signal records for Florence-2 and SAM-style workflows without downloading weights, calling providers, or adding generated outputs to training data.

## Scope

- Read reviewed tiny learning examples from the combined case source manifest.
- Select only `recommended_pilot` models from `open_source_model_catalog_v1`.
- Generate `learning_open_model_signal_record` JSONL records.
- Write a summary report with coverage by model, case type, and source kind.
- Support injected runners for explicit local experiments and tests.
- Default to dry-run records when no runner is provided.

## Safety Rules

- Runtime is disabled by default.
- Weight download is out of scope.
- Blocked/non-commercial/license-review models cannot be selected by default.
- Output records are not training data.
- Every signal record requires human review before labels can be used for training.
- Signal records summarize inputs and do not serialize raw case records, review labels, learning targets, local absolute paths, or private URI values.

## Initial Models

- `florence_2`: caption, OCR, and dense-region signal families across redraw, decompose, and layer generation cases.
- `segment_anything_sam_vit`: mask proposal, boundary complexity, and mask coverage signal families for redraw and decompose cases.

## Non-Goals

- Do not integrate Hugging Face runtime.
- Do not call Florence-2, SAM, or any provider.
- Do not generate labels automatically.
- Do not update `combined_case_source_manifest_v1`.
- Do not affect redraw/decompose/layer generation runtime.

## Verification

- `tests/test_open_model_signal_adapter.py` covers dry-run export, model blocking, injected runner outputs, and CLI behavior.
