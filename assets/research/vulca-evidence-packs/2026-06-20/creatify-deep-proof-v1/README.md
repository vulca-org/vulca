# Creatify Deep Proof v1

**Status:** internal technical proof, not customer-facing
**Date:** 2026-06-21
**Lane:** Lane C / AI ad workflow and creative automation evidence

This folder records the Lane C proof for the VULCA Solution Pack v1 internal
master preview. It uses true local screenshots from public Creatify workflow
pages and a local creative-anatomy cue to show how VULCA turns a product-to-ad
workflow into a campaign handoff evidence packet.

## What This Proves

This proof shows the workflow we want Page 11/12 to express:

```text
public product-to-video workflow source
-> workflow-field annotation
-> source input, candidate creative, review anatomy, export state, and owner route
-> source-safe campaign handoff card
```

It does not prove ad performance, ROI, CPA, CTR, ROAS, legal approval, platform
approval, vendor endorsement, or replacement of human creative review.

## Internal Artifacts

- `source-and-annotation-ledger.json`:
  source candidates, local asset hashes, field mapping, internal reserve
  treatment, and customer-use boundary.
- `annotations/creatify-workflow-field-overlay-v1.png`:
  internal workflow-field overlay built from true local screenshots.
- `annotations/creatify-workflow-field-overlay-v1.json`:
  field manifest for the overlay image.
- `source-safe/creatify-source-safe-workflow-card-v1.png`:
  customer-facing candidate distilled from the internal proof.
- `source-safe/creatify-source-safe-workflow-card-v1.json`:
  manifest and external-use boundary for the distilled card.

## Reading Guide

The numbered VULCA fields are:

| No. | Field | Meaning |
| --- | --- | --- |
| 1 | `source.input` | Product URL, listing, image, offer, or brief source is preserved. |
| 2 | `candidate.creative` | Generated ad candidate is separated from source and review state. |
| 3 | `review.anatomy` | Hook, body, CTA, scene, product fit, claim fit, and brand fit become review fields. |
| 4 | `edit.export.state` | Draft, edit, export, channel, or seller-flow state is named. |
| 5 | `campaign.handoff` | Growth, creative ops, marketplace, or campaign owner receives unresolved items. |
| 6 | `internal.reserve` | Alibaba case-study material is context only and not default customer proof. |

## Internal Reserve Boundary

The Creatify / Alibaba case-study screenshot is recorded as internal reference
only. It can inform how we think about embedded seller workflows, but it should
not appear as default customer-facing visual proof and should not be used to
claim adoption growth, video volume, ROI, CPA, CTR, ROAS, or VULCA endorsement.

## Customer-Facing Boundary

Customer pages can use the resulting pattern, not the raw internal proof:

- keep Creatify as a public workflow example only;
- avoid vendor-endorsement, customer, partner, authorization, or performance
  claims;
- do not use Alibaba case-study material unless explicitly approved later with
  attribution and metric controls;
- show source input, generated candidate, review anatomy, export state, reuse
  target, and campaign owner route;
- use the source-safe distilled card or a redraw instead of raw vendor UI.
