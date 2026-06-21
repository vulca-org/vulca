# Customer Solution Pack Deck Canonical Source Design

**Status:** accepted and implemented
**Date:** 2026-06-21
**Decision:** use a real PPTX/deck as the canonical source for formal customer-facing VULCA Solution Pack material, then export PDF from that deck.

## Context

Before the deck migration, the VULCA Solution Pack work had three different presentation paths:

1. `assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/index.html`
   is a static HTML/CSS internal master preview for page components and proof review.
2. `output/pdf/vulca-solution-pack-v1-internal-preview.pdf` is generated from that HTML preview for internal review.
3. `output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf` was generated directly by
   the legacy ReportLab builder.

The ReportLab customer sample proved the content direction, but it exposes a structural problem:
page balance, density, and slide-to-slide rhythm are being controlled by fixed PDF coordinates rather
than by a real deck layout system.

## Recommendation

Formal customer material should use this source chain:

```text
HTML/CSS internal preview
  -> evidence-card and source-safe component review
  -> PPTX formal customer deck as canonical source
  -> exported PDF customer attachment
```

The HTML preview remains the internal proof lab. The PPTX becomes the source of truth for customer
presentation layout. The PDF becomes a generated delivery artifact.

## Non-Goals

- Do not create another exploratory customer PDF path.
- Do not keep hand-tuning the ReportLab PDF as the long-term production route.
- Do not make raw screenshots, crop boxes, local paths, source-log filenames, Alibaba reserve material,
  internal labels, or debug overlays customer-visible.
- Do not claim that named companies are VULCA customers, partners, endorsers, authorization sources,
  audit targets, or validated findings.
- Do not send email or outreach material from this workflow.

## Output Artifacts

Canonical artifacts:

- PPTX source:
  `output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx`
- Exported PDF:
  `output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf`

The ReportLab PDF route is retained only as a transition reference. The checked-in PPTX is now the
customer-material source of truth, and the PDF path is replaced by the exported deck output.

## Tooling

Use the OpenAI Presentations skill's required implementation route for PPTX:

- JavaScript ES modules.
- `@oai/artifact-tool`.
- Scratch workspace outside the repo, using the Presentations skill workspace convention.
- Final PPTX written under `output/pptx/`.

Use Poppler/PDF tooling only for export verification and page-render QA:

- `pdfinfo` for metadata checks.
- `pdftoppm` for visual render checks.
- `scripts/customer_pdf_preflight.py` for customer-visible text preflight.

The existing VULCA carousel helpers in `scripts/xhs_common.py` may inform layout heuristics such as
safe margins, image fit/contain behavior, and slide rhythm, but they are not the canonical PPTX engine.

## Deck Architecture

The first formal customer sample should be a 7-slide deck matching the approved customer story:

1. Title and positioning.
2. What VULCA produces: the three-lane map.
3. Lane C hero: AI ad workflow before/after handoff.
4. Supporting proof A: product-truth evidence.
5. Supporting proof B: AI publishability context.
6. Bounded pilot shape.
7. Review ask and boundaries.

The deck should stay public-example based and not be customized to a named company in this first pass.

## Layout Rules

Every slide must use the same slide system:

- 16:9 landscape canvas.
- Shared title band, page marker, and footer boundary language.
- Shared safe margins.
- Shared lane colors: teal for source/evidence, amber for owner/boundary, red for not-claims.
- Minimum body text size follows the Presentations skill requirement: 16pt or larger.
- Slide title should be 35pt or larger unless the design uses an inherited template with different
  verified typography.
- No one-off coordinate tuning after export unless the deck source is updated too.

The customer deck should avoid the current imbalance pattern:

- No large empty left-side blocks paired with dense right-side cards.
- No tiny evidence-card screenshots that require zooming to understand.
- No decorative card grids where a single structured diagram or sequence is clearer.
- Page 4 and Page 5 should use readable reconstructed evidence-card views, not raw internal proof
  thumbnails.

## Source And Claim Policy

The formal deck can use named companies only as public examples:

- Company names may appear as public examples for workflow discussion.
- Visuals must be source-safe: redrawn, masked, cropped, or reconstructed as semantic evidence cards.
- Source-safe cards may be derived from the Lane A/B/C proof folders, but internal proof labels must
  not appear in customer-visible slides.

Forbidden customer-visible claims:

- legal advice;
- rights clearance;
- platform approval;
- policy approval;
- model-safety certification;
- release-readiness certification;
- campaign-performance measurement;
- ROI, CPA, CTR, ROAS, or benchmark superiority;
- customer, partner, endorsement, authorization, or audit-target relationship.

## Approval Gate

Generating or replacing the customer-facing PPTX/PDF requires explicit main-review approval.

The generation command preserves the `--approval-recorded` gate in
`scripts/build_customer_solution_pack_deck.mjs`.

Ordinary "continue" instructions are not enough to generate a new formal customer artifact unless the
conversation already contains explicit approval for that artifact type and path.

## QA Gates

Before a PPTX/PDF is presented as ready for user review:

1. Build the PPTX from source.
2. Export or render previews of every slide.
3. Inspect a full contact sheet and key full-size slides.
4. Fix all unintended overlap, clipping, wrapping, and density problems in the PPTX source.
5. Export the PDF from the PPTX.
6. Run `python3 scripts/customer_pdf_preflight.py --json output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf`.
7. Run `pdfinfo` on the exported PDF.
8. Render the exported PDF with `pdftoppm`.
9. Confirm the PDF render matches the reviewed deck layout.
10. Commit the PPTX source, exported PDF, generation script, and docs together as a coherent change.

## Migration Shape

The implementation follows three coherent phases:

1. Add the PPTX builder and generation gate.
2. Port the current 7-page customer sample content into a balanced deck layout.
3. Export and verify the PDF, then retire the ReportLab route from canonical status.

The existing ReportLab script can remain temporarily as a reference, but README language makes the PPTX
route canonical now that the deck exists.

## Success Criteria

The migration is successful when:

- The formal customer sample has a checked-in `.pptx` canonical source.
- The PDF is generated from the PPTX route, not hand-authored in ReportLab.
- The slide contact sheet has visibly balanced content distribution.
- Page 4 and Page 5 are readable without zooming into tiny screenshots.
- Customer preflight reports zero issues.
- The README clearly states the HTML/PPTX/PDF roles and prevents future version confusion.
