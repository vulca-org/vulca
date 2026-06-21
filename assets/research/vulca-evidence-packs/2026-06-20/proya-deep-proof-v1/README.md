# PROYA Deep Proof v1

**Status:** internal technical proof, not customer-facing
**Date:** 2026-06-21
**Lane:** Lane A / Product-truth and claim evidence

This folder records the first PROYA deep proof for the VULCA Solution Pack v1
internal master preview. It uses true local PROYA assets and public source
candidates to show how VULCA turns a campaign/product visual into evidence-card
fields.

## What This Proves

This proof shows the internal workflow we want the master PDF to express:

```text
public source-backed visual
-> visual annotation
-> field extraction
-> evidence-card draft
-> owner route
-> customer-safe visual treatment decision
```

It does not prove legal, rights, platform, or claim-truth status. It does not
make any finding against PROYA, Guardian, CBE, or any source publisher.

## Internal Artifacts

- `source-and-annotation-ledger.json`:
  source candidates, local asset hashes, annotation boxes, evidence-card fields,
  and customer-use boundaries.
- `annotations/proya-lead-source-map-annotated.jpg`:
  full-frame internal source map.
- `annotations/proya-page8-evidence-crop-annotated.jpg`:
  Page 8 candidate evidence-card crop.
- `decompose/`:
  reserved for the attempted VULCA decompose result.

## Reading Guide

The numbered visual annotations map to VULCA fields:

| No. | Visual cue | VULCA field | Meaning |
| --- | --- | --- | --- |
| 1 | Campaign / claim text | `claim` | Record visible language as a source item, not as a judged issue. |
| 2 | Product representation / packshot | `representation` | Separate product display from campaign, channel, and promotion context. |
| 3 | Guardian / retail context | `source_context` | Record channel context without implying relationship or authorization. |
| 4 | Promotion / reuse cue | `reuse_context` | Needs source and owner routing before cross-channel reuse. |
| 5 | People / likeness area | `rights_or_likeness_review_question` | Route as a review question; do not conclude rights status. |
| 6 | Product/PDP owner route | `owner_route` | Route unresolved questions to brand, ecommerce, channel, or release owner. |

## Customer-Facing Boundary

Customer pages can use the resulting pattern, not the raw internal proof:

- use source-safe redraw, crop, or masked visual treatment;
- keep company names framed as public examples only;
- avoid finding-style language;
- avoid severity scoring;
- prefer field-completion and owner-route language;
- attach source note and capture date before external export.

## Next Technical Step

Attempt VULCA decompose on the main campaign/product image:

```text
assets/research/vulca-evidence-packs/2026-06-20/real-asset-batch-02/proya/images/05-9b8dd65d5aa4.jpg
```

If the orchestrated decompose pipeline is unavailable or too heavy in this
environment, record the blocker in `decompose/README.md` and keep the annotation
proof as the minimum verified technical output.
