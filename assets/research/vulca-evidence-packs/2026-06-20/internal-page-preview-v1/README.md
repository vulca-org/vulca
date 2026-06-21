# VULCA Solution Pack v1 Internal Page Preview

**Status:** internal review preview only; not a final PDF
**Date:** 2026-06-21
**Scope:** pages 7-12 component preview for the master PDF

This directory contains a static HTML preview for the first case-led visual
components in the VULCA Solution Pack v1 master PDF.

Open `index.html` locally to review:

- Page 7: Product-Truth / Claims lane queue strip
- Page 8: Product-Truth evidence-card pattern
- Page 9: AI Publishability lane queue strip
- Page 10: AI Publishability evidence-card pattern
- Page 11: AI Ad Workflow lane strip
- Page 12: AI Ad Workflow evidence-card pattern

## Boundary

This preview intentionally uses source-backed crops as internal evidence
material. It is not customer-facing.

Before any exported PDF or external use:

1. Replace raw source crops with redrawn, masked, cropped annotated-safe, or
   explicitly cleared visuals.
2. Remove raw local paths, filenames, and capture-batch identifiers from
   customer-facing pages.
3. Re-run the PDF safety gate in the canonical storyboard.
4. Keep named companies framed as public market examples only.

## Version Lineage And Feedback Loop

Use this directory as an internal page-component preview for the master PDF,
not as the customer-facing PDF itself.

The expected production path is:

```text
internal master PDF / source-backed visual component preview
-> reviewed master pages and asset decisions
-> customer-specific formal PDF variant
-> customer/version review
-> fixes flow back into the master PDF rules, assets, and page components
-> regenerate the affected formal PDF variant
```

If a customer-specific formal PDF has a problem, do not patch only that formal
PDF in isolation. First decide whether the issue is a master-level issue
(storyline, source policy, visual treatment, evidence-card schema, safety
boundary, or reusable copy). Master-level issues must be corrected in the
internal master PDF/source preview and related production notes, then the
customer-specific PDF should be regenerated from that corrected basis.

Only customer-specific details, such as recipient framing, company-specific
ordering, or a narrow CTA, should live only in the formal variant.

## Inputs

The source of truth remains:

- `docs/product/2026-06-20-vulca-solution-pack-v1-pdf-storyboard.md`
- `docs/product/2026-06-20-vulca-solution-pack-v1-master-pdf-production-plan.md`
- `docs/product/2026-06-20-vulca-solution-pack-v1-master-pdf-asset-inventory.md`

`manifest.json` lists the exact image sources and crop boxes used by the
preview renderer.
