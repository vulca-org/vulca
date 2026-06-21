# Seedream / BytePlus Deep Proof v1

**Status:** internal technical proof, not customer-facing
**Date:** 2026-06-21
**Lane:** Lane B / AI publishability and generated asset context

This folder records the Lane B proof for the VULCA Solution Pack v1 internal
master preview. It uses true local screenshots from public Seedream and
BytePlus sources to show how VULCA turns public AI-model/tool context into a
publishability evidence packet.

## What This Proves

This proof shows the workflow we want Page 9/10 to express:

```text
public model/tool source pages
-> field-level screenshot annotation
-> source, input, model, output, label, and owner fields
-> source-safe customer evidence-card candidate
```

It does not prove model quality, model safety, copyright clearance, platform
approval, legal approval, benchmark superiority, or any relationship with
Seedream, BytePlus, ByteDance, or ModelArk.

## Internal Artifacts

- `source-and-annotation-ledger.json`:
  source candidates, local asset hashes, annotation boxes, field mapping, and
  customer-use boundary.
- `annotations/seedream-byteplus-field-overlay-v1.png`:
  internal field overlay built from true local screenshots.
- `annotations/seedream-byteplus-field-overlay-v1.json`:
  field manifest for the overlay image.
- `source-safe/seedream-byteplus-source-safe-distilled-card-v1.png`:
  customer-facing candidate distilled from the internal proof.
- `source-safe/seedream-byteplus-source-safe-distilled-card-v1.json`:
  manifest and external-use boundary for the distilled card.

## Reading Guide

The numbered VULCA fields are:

| No. | Field | Meaning |
| --- | --- | --- |
| 1 | `source.record` | URL, page role, capture date, source owner, and source type. |
| 2 | `model.context` | Public model/tool context kept version-neutral in customer copy. |
| 3 | `input.mode` | Prompt, reference, product/source material, region/API route, and missing input packet. |
| 4 | `output.state` | Generated state, output format, demo/export state, and prompt-result pairing needs. |
| 5 | `label.posture` | AI label/disclosure is a decision field, not a legal ruling. |
| 6 | `owner.route` | Product, platform, creative, or release owner receives unresolved questions. |

## Screenshot Limitation

Some BytePlus screenshots contain cookie or feedback overlays. They are marked
as screenshot limitations in the internal overlay. Customer-facing exports
should use a clean recapture, a masked crop, or a redrawn docs strip.

## Customer-Facing Boundary

Customer pages can use the resulting pattern, not the raw internal proof:

- keep Seedream / BytePlus as public examples only;
- avoid model-quality, safety, copyright, policy, benchmark, or legal claims;
- do not imply customer, partner, endorsement, or authorization status;
- prefer version-neutral AI publishability language;
- show source records, prompt/reference requirements, output state, label
  posture, and owner route;
- use the source-safe distilled card or a redraw instead of raw UI screenshots.
