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

Canonical internal review PDF output:

```text
output/pdf/vulca-solution-pack-v1-internal-preview.pdf
```

This PDF is generated from the current `index.html` preview for internal review
only. It is not the customer-facing PDF.

Formal public-example customer sample PDF output:

```text
output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf
```

This PDF was generated after explicit user approval on 2026-06-21 as a review
sample only. It is not emailed or sent by default. It uses the default customer
reader profile: brand, ecommerce, or AI ad workflow owner; Lane C before/after
first, then Lane A and Lane B supporting proof. Named companies appear only as
public examples for workflow discussion, not as customers, partners, endorsers,
authorization sources, or validated findings.

The sample is derived from this internal master preview and the source-safe
evidence cards already recorded in the Lane A/B/C proof folders. Any issue found
in the formal sample should be fixed at the master/source-card level first, then
the same customer sample path should be regenerated. Do not create exploratory
extra PDFs for the same review pass.

Regenerate the sample with a Python environment that includes `reportlab`:

```bash
python3 scripts/build_customer_solution_pack_pdf.py --approval-recorded
```

The script writes to the canonical customer sample path above by default.

## Three-Lane Purpose Map

Use this map to keep Lane B and Lane C separate:

| Lane | Unit of review | Core question | Evidence-card output |
| --- | --- | --- | --- |
| A / Product-truth | Existing commercial material and product claim | Does the campaign, product representation, source, channel reuse, and owner route connect? | Product-truth evidence card |
| B / AI publishability | One generated asset or generated asset set | Can this AI output be published or reused with source, prompt/reference, model context, label posture, and owner route attached? | AI publishability evidence card |
| C / AI ad workflow | Product-to-ad workflow and campaign handoff | How does product URL/listing/brief become candidate creative, review state, export state, and campaign owner handoff? | AI ad workflow handoff card |

Short rule:

```text
Lane A = claim/material level
Lane B = generated-asset level
Lane C = workflow/handoff level
```

Lane C can contain many Lane B-style generated assets, but its main proof is
the workflow and handoff path, not a single generated image or video.

## Page 7/8 PROYA Technical Proof Upgrade

Page 7/8 now include the PROYA Vision Banana fallback proof from:

```text
../proya-deep-proof-v1/vision-banana/
```

The current proof uses the configured Vision Banana compatible fallback:

```text
requested_provider: vision-banana
resolved_provider: palette-mask
fallback_reason: missing_vision_banana_endpoint
```

The contact sheet is treated as the machine mask output. The Page 8 overlay is
a human-reviewed VULCA annotation built from those mask components, not a SAM or
DINO layer split. This is intentional for the current review pass: it is more
legible for source, representation, review-question, and owner-route discussion.

Page 8 also includes a source-safe distilled card candidate:

```text
../proya-deep-proof-v1/vision-banana/proya-source-safe-distilled-card-v1.png
```

That distilled card is the bridge from internal proof to customer-facing PDF:
it removes the raw source photo, people, store crop, and debug labels while
preserving the VULCA field logic.

Customer-facing exports should not use the raw annotated image. They should use
a source-safe crop, redraw, or simplified evidence-card visual derived from the
fields.

## Page 9/10 Seedream / BytePlus Technical Proof Upgrade

Page 9/10 now include the Lane B deep proof from:

```text
../seedream-byteplus-deep-proof-v1/
```

The current proof uses true local screenshots from public Seedream / BytePlus
model and documentation pages. It is a manual VULCA source-field annotation,
not a SAM/DINO/Vision Banana segmentation output.

Current outputs:

```text
../seedream-byteplus-deep-proof-v1/annotations/seedream-byteplus-field-overlay-v1.png
../seedream-byteplus-deep-proof-v1/source-safe/seedream-byteplus-source-safe-distilled-card-v1.png
```

The Page 9 overlay is for internal review: it shows how real source pages are
read into source, model, input, output, label, and owner fields. The Page 10
distilled card is the customer-facing candidate: it removes raw UI screenshots,
cookie overlays, debug labels, and local capture details while preserving the
publishability evidence-card logic.

Customer-facing exports should use the distilled card, a clean recapture, or a
redrawn docs strip. Do not use the raw screenshots as external proof by
default.

## Page 11/12 Creatify Technical Proof Upgrade

Page 11/12 now include the Lane C deep proof from:

```text
../creatify-deep-proof-v1/
```

The current proof uses true local screenshots from public Creatify workflow
pages and a creative-anatomy cue. It is a manual VULCA workflow-field
annotation, not a SAM/DINO/Vision Banana segmentation output.

Current outputs:

```text
../creatify-deep-proof-v1/annotations/creatify-workflow-field-overlay-v1.png
../creatify-deep-proof-v1/source-safe/creatify-source-safe-workflow-card-v1.png
```

The Page 11 overlay is for internal review: it shows how product-link input,
generated candidates, hook/body/CTA anatomy, export state, campaign handoff,
and internal reserve material become VULCA fields. The Page 12 distilled card
is the customer-facing candidate: it removes raw vendor UI, people/ad example
thumbnails, local capture details, and Alibaba case-study proof.

Customer-facing exports should use the distilled card, a clean redraw, or a
masked source cue. Do not use raw vendor UI or Alibaba case-study material as
default external proof.

## Redraw And Masking State

For this review preview, source-safe cards are manually distilled from VULCA
fields. They prove the expected customer-facing structure and safety boundary.

Automated redraw, automatic screenshot masking, and automatic vendor-UI
sanitization are not represented as completed production capabilities in this
directory. If those features are implemented later, they should write their own
machine-output artifact and manifest instead of replacing the current manual
distillation record.

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
  be refreshed or redrawn before customer-facing use. Page 9/10 now include a
  completed internal field overlay and a source-safe distilled card candidate.
- Creatify URL-to-video official pages are identified; raw screenshots should
  be redrawn into workflow strips before customer-facing use. Page 11/12 now
  include a completed workflow-field overlay and source-safe handoff card
  candidate.
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

## Customer Variant Default

The narrative branch has been folded into the master preview as a planning
input, not as a ready-to-send artifact.

Current default for the first customer-specific formal PDF:

1. Lead with brand, ecommerce, and AI ad workflow owners.
2. Use named companies only as public examples, with source-safe visuals and
   explicit boundary copy.
3. Use Lane C as the clearest before/after customer story, supported by Lane A
   product-truth proof and Lane B AI-publishability proof.
4. Keep the first email as a feedback request. Bounded pilot discussion is a
   follow-on step, not the opening ask.
5. Keep full source matrices, raw crops, crop boxes, local paths, debug labels,
   and treatment ledgers internal.

Do not generate a separate customer-facing PDF without explicit user approval.
When approved, derive it from this master source and regenerate the formal
variant after any master-level fix.

## Formal Customer PDF Gate

Before creating a formal customer PDF, confirm these items in the main review
session:

1. Recipient type: brand/ecommerce owner, AI ad workflow owner, AI creative
   platform, or a named company-specific recipient.
2. Example strategy: named public examples in the body, or neutral redrawn
   workflow examples with source notes in a smaller supporting section.
3. Lane order: default is Lane C first, with Lane A and Lane B as supporting
   proof unless the recipient needs a different order.
4. Visual treatment: every customer-visible visual must be source-safe: redraw,
   clean recapture, crop, mask, or semantic evidence card.
5. Copy boundary: no legal advice, compliance certification, model-safety
   certification, platform approval, performance guarantee, customer
   relationship, endorsement, authorization source, or finding.
6. Preflight scan: run `python3 scripts/customer_pdf_preflight.py <artifact>`
   on the customer-visible PDF, markdown, HTML, or text export before sharing.
7. Output path: use one clear customer-specific filename and record that it was
   derived from this master preview. Do not create exploratory extra PDFs.

## Inputs

Current canonical inputs checked into this branch:

- `docs/product/2026-06-21-vulca-solution-pack-v1-customer-narrative-and-copy-brief.md`
- `docs/product/2026-06-21-vulca-solution-pack-v1-customer-narrative-and-copy-brief-cn.md`
- `docs/product/2026-06-21-vulca-reference-company-deep-research-brief.md`
- `assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/README.md`
- `assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/manifest.json`
- `assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/index.html`

`manifest.json` lists the exact image sources and crop boxes used by the
preview renderer.

Earlier planning branches referenced these filenames, but they are not present
in this current branch and should not be treated as canonical unless imported
later:

- `docs/product/2026-06-20-vulca-solution-pack-v1-pdf-storyboard.md`
- `docs/product/2026-06-20-vulca-solution-pack-v1-master-pdf-production-plan.md`
- `docs/product/2026-06-20-vulca-solution-pack-v1-master-pdf-asset-inventory.md`
- checked-in `docs/product/lane-work/*production-brief.md` files

The narrative and reference-company briefs are customer-version planning
inputs. They should inform the future formal PDF opening, short outreach note,
CTA, terminology, and buyer framing. They do not override the source matrix,
external-use boundaries, or internal proof manifests.
