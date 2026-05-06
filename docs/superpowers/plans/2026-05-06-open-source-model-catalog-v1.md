# Open Source Model Catalog v1

Status: implemented

## Goal

Record the open and open-weight model candidates that can support Vulca learning workflows without silently changing runtime behavior, downloading weights, or treating model outputs as reviewed training labels.

## Scope

- Add a static model catalog under `docs/benchmarks/learning/`.
- Separate permissive pilots from non-commercial or license-review-blocked references.
- Require explicit enablement before runtime use.
- Require manual review before any model output can become training data.

## Initial Pilot Order

1. `qwen_image_edit`: image editing provider candidate for `redraw_case` and `layer_generate_case`.
2. `segment_anything_sam_vit`: mask proposal and layer boundary signal candidate for `decompose_case` and `redraw_case`.
3. `grounding_dino`: text-grounded detection signal candidate for layer coverage review.
4. `florence_2`: caption, OCR, and dense-region signal candidate for case review features.

## Blocked References

- `flux_kontext_dev`: non-commercial license, keep as reference only until license review or commercial terms.
- `stable_diffusion_3_5_large`: community/commercial license boundary requires review before product runtime or training use.

## Non-Goals

- Do not download model weights.
- Do not integrate runtime providers.
- Do not add model outputs to `combined_case_source_manifest_v1`.
- Do not train from generated outputs without human-reviewed conversion into case logs.

## Verification

- `tests/test_open_source_model_catalog_v1.py` validates schema, safety defaults, pilot priorities, and blocked models.
