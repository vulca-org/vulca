# PROYA Vision Banana Fallback Review

**Status:** internal technical proof only
**Date:** 2026-06-21

This folder stores the PROYA semantic-region review generated from
`gemini-agent design perceive`.

Run summary:

```text
requested_provider: vision-banana
resolved_provider: palette-mask
fallback_reason: missing_vision_banana_endpoint
```

The output is useful for internal annotation review, but it is not a dedicated
Vision Banana endpoint result and not a SAM/DINO layer split.

## Files

- `proya-vision-banana-contact-sheet.png`:
  machine mask contact sheet from the compatible fallback.
- `proya-vision-banana-perception.json`:
  raw perception output from the run.
- `proya-vision-banana-tight-semantic-overlay-v3.png`:
  human-tightened VULCA field overlay derived from mask components.
- `proya-vision-banana-tight-semantic-overlay-v3.json`:
  field manifest for the v3 overlay.
- `proya-source-safe-distilled-card-v1.png`:
  customer-view candidate distilled from the internal proof.
- `proya-source-safe-distilled-card-v1.json`:
  manifest and external-use boundary for the distilled card.

## Use

Use the v3 overlay to review the Page 7/8 PROYA evidence-card logic:

- claim/source text surfaces;
- product representation;
- retail and source-context cues;
- likeness and promotion review questions;
- owner-route cue.

Do not use the raw annotated image in a customer-facing PDF. Customer variants
should use a source-safe crop, simplified evidence card, mask, or redraw.

The distilled card is the current source-safe candidate for that customer
variant. It keeps the public-example frame and VULCA field structure while
removing the raw source photo, people, store crop, and debug labels.
