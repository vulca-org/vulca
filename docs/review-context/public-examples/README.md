# Public Example Gates

Vault status: protected public-example gate reference.

This folder contains protected fixtures for RR4: clearing one specific public
example without upgrading broader product claims.

The public-example gate is example-scoped. A passing example can support that
specific artifact and its attached copy. It does not clear every provider,
deck, Workspace flow, or product-level claim.

## Current Gates

- `m3-public-example-gate.json`: RR4 reference gate for the M3 key visual
  example. It records evidence, visual quality review, source-backed evidence
  review, release-owner decision, and example-specific public copy scope.

## Rules

- EvidencePack must exist and be complete for the example.
- Visual quality review must pass for the specific artifact.
- Evidence review must be source-backed.
- Release owner must record the decision.
- Public copy must remain example-specific.
- Product-level public claims remain gated by M5 closeout.

## Sources

- `docs/review-context/12-complete-demo-path.md`
- `docs/review-context/13-website-ppt-claim-spine.md`
- `docs/review-context/14-release-readiness-evidence-gate.md`
- `docs/review-context/workspace-durable/m3-durable-review-fixture.json`
