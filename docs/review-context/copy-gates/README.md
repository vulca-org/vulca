# Website And PPT Copy Gates

Vault status: protected copy-gate reference.

This folder contains protected fixtures for RR5: applying the website/PPT claim
spine after implementation and example evidence exists.

The copy gate aligns public website, README-facing copy, public decks, internal
PPT proof-lab summaries, and translations. It prevents copy from upgrading
preview, example-specific, or public-blocked evidence into broader product
claims.

## Current Gates

- `website-ppt-copy-gate.json`: RR5 reference gate for website, README, PPT,
  and translations after the M3/RR4 example gate.

## Rules

- Public copy must state the current R-level.
- One cleared public example stays example-specific.
- PPT proof-lab outputs remain internal or blocked unless separately cleared.
- Translations must preserve the same claim level as the source copy.
- Copy cannot upgrade missing implementation evidence.

## Sources

- `docs/review-context/13-website-ppt-claim-spine.md`
- `docs/review-context/14-release-readiness-evidence-gate.md`
- `docs/review-context/public-examples/m3-public-example-gate.json`
