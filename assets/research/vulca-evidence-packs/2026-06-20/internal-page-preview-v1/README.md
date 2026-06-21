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

## Reading Map

The page sequence is paired:

- Pages 7, 9, and 11 are commercial case pages. They show why a type of
  company, asset, or workflow needs VULCA.
- Pages 8, 10, and 12 are evidence-card pages. They show what VULCA outputs:
  source fields, review fields, owner routing, and handoff fields.
- The Chinese `读法` notes in `index.html` are internal reviewer aids. They
  should be removed or rewritten before a customer-facing export.
- The Chinese `解释` boxes add the internal reasoning for each page: why the
  page exists, how to read the visuals, and what still needs source-safe
  treatment before customer-facing PDF production.

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

## Review Completion Standard

For this internal preview, "100%" means the page is ready for human review as
the master source for later customer-specific PDFs. It does not mean the raw
images are externally cleared.

Each page should make these points visible without extra verbal explanation:

1. The commercial role of the page: case story, evidence-card pattern, or
   closing handoff.
2. The role of each image: lead visual, source cue, source record, workflow
   context, or redraw target.
3. The evidence chain: source input, claim or generated output, review context,
   owner route, and final handoff.
4. The external-use boundary: no raw crop export, no customer/partner/endorser
   implication, no legal/compliance/certification claim, and no unsupported
   performance claim.
5. Empty image placeholders are not acceptable in the review preview. If a
   source-safe final visual is not available yet, use a labeled semantic diagram
   that shows the intended source record, owner route, label decision, or redraw
   target.

## Source Matrix Status

`manifest.json` now includes a `source_matrix` section. Use it as the working
source/treatment ledger before any customer-facing export.

The matrix records:

1. Local asset paths and the pages where they appear.
2. Public source candidates or verified source pages, with dates where known.
3. The intended customer-visible use of each source group.
4. Required external treatment: redraw, mask, crop, recapture, or internal-only.
5. Claims that must not be made in customer-facing copy.

Current source status:

- PROYA Guardian Malaysia campaign source page is identified, but exact image
  URL and capture timestamp still need local source-log recording.
- PROYA CBE event/award context source pages are identified, but exact image
  URLs and capture timestamps still need local source-log recording.
- Seedream / BytePlus official pages are identified; current screenshots should
  be refreshed or redrawn before customer-facing use.
- Creatify URL-to-video official pages are identified; raw screenshots should
  be redrawn into workflow strips before customer-facing use.
- Creatify / Alibaba case-study material remains internal-only by default.

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

## Current Review Decisions

These decisions are now part of the master-page working logic:

- Keep PROYA as the Lane A public market example.
- Replace severity-style language in customer-visible evidence cards with
  field-completion, review-packet, and owner-route language.
- For Lane B, use version-neutral `Seedream / BytePlus public model context`
  language instead of selecting one customer-facing model version.
- Move Kling out of the customer-facing Lane B page; keep it only as an
  internal video/reference reserve.
- Keep the Creatify / Alibaba case-study material as internal reference by
  default. Do not use Alibaba as customer-facing visual proof unless explicitly
  approved later with source attribution and performance-claim controls.
- Company names may appear only as public examples, never as VULCA customers,
  partners, endorsers, authorization sources, or audit targets.

## Inputs

The source of truth remains:

- `docs/product/2026-06-20-vulca-solution-pack-v1-pdf-storyboard.md`
- `docs/product/2026-06-20-vulca-solution-pack-v1-master-pdf-production-plan.md`
- `docs/product/2026-06-20-vulca-solution-pack-v1-master-pdf-asset-inventory.md`

`manifest.json` lists the exact image sources and crop boxes used by the
preview renderer.
