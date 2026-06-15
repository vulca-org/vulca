# Artifact Bridge Fixtures

Vault status: protected bridge fixture reference.

This folder contains protected fixtures for applying
`11-artifact-bridge-spec.md` to the M3 demo path in
`12-complete-demo-path.md`.

The fixtures are not production data and are not public release evidence. They
define the minimum adapter shape that product branches must preserve when
SDK/MCP outputs enter Workspace review.

## Current Fixtures

- `m3-demo-bridge-fixture.json`: RR2 reference fixture showing one generated
  key visual becoming bridge records, Workspace projection objects, an
  EvidencePack, a ReviewRequest, and a blocked ReleaseGate.

## Rules

- Asset paths stay as strings; do not embed image bytes.
- `public_ready` remains false inside bridge records.
- `ReleaseGate.publicReady` remains false in Workspace projection.
- Missing evidence must stay visible in the EvidencePack and ReleaseGate.
- Human release approval is not represented by this fixture.

## Sources

- `docs/review-context/11-artifact-bridge-spec.md`
- `docs/review-context/12-complete-demo-path.md`
- `docs/review-context/14-release-readiness-evidence-gate.md`
