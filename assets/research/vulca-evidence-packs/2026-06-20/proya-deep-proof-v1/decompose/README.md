# PROYA Decompose Attempt

**Status:** blocked by missing local SAM checkpoint
**Date:** 2026-06-21
**Input image:** `proya-lead-1600.jpg`
**Plan:** `proya-lead-1600-plan.json`

## What Ran

The local typed VULCA pipeline entrypoint was invoked:

```text
PYTHONPATH=src
from vulca.pipeline.segment import run
run(plan_path, image_path, out_dir, force=True)
```

The run used a resized 1600px-wide version of the PROYA source image and a
hint-driven `sam_bbox` plan with five semantic entities:

1. `foreground.signage.campaign_banner`
2. `foreground.signage.retail_channel`
3. `foreground.product.display_packshots`
4. `foreground.panel.model_campaign`
5. `foreground.panel.product_pdp`

`proya-decompose-plan-preview.jpg` visualizes these planned semantic regions.
It is not a segmentation output.

## Result

The run failed before writing a layer manifest because the local SAM checkpoint
was missing:

```text
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/sam_vit_l.pth'
```

The exact captured result is in `decompose-run-summary.json`.

## Interpretation

This is an environment dependency blocker, not a source-image or evidence-card
blocker. The current proof still verifies:

- true PROYA source image is available locally;
- source and annotation ledger exists;
- semantic entity plan is authored;
- field-level annotation maps are generated;
- the VULCA decompose pipeline entrypoint is reachable;
- actual layer split requires the SAM ViT-L checkpoint before it can complete.

## Next Step

To produce a true VULCA layer manifest, provide or download the expected SAM
checkpoint at:

```text
/tmp/sam_vit_l.pth
```

Do not present `proya-decompose-plan-preview.jpg` as a completed layer split.
It is only the planned layer-ownership map for review before rerunning the real
pipeline.
