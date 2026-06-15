# Review Context Validation Gate

Vault status: gate definition.

Run this before committing any direct vault modification:

```bash
python3 docs/review-context/gates/validate_review_context.py
```

The gate checks:

- required files from `MANIFEST.json` exist
- core markdown files include vault status metadata
- core history files include source references
- protected claim phrases do not appear outside allowed boundary files
- request template contains required gate checklist items
- release-readiness template contains required Gates 1-6, evidence index,
  owner, and decision controls
- M3 bridge fixture contains an asset bridge record, Workspace projection,
  visible missing evidence, blocked release gate, and RR2 acceptance flags
- RR3 durable review fixture contains reload-preserved review item, evidence,
  blockers, decision state, permission checks, and human decision history
- RR4 public example gate contains EvidencePack, visual/evidence reviews,
  release-owner decision, example-specific public copy, and RR4 acceptance flags
- RR5 copy gate contains website/README/PPT R-level statuses, bounded proof-lab
  status, translation claim-level preservation, and no forbidden upgrades

Passing this gate is necessary but not sufficient. A curator must still apply
source and claim judgment.

Repository-level checks:

- `.github/workflows/review-context.yml` runs this gate on pull requests and
  pushes that touch the vault.
- `tests/test_review_context_vault.py` verifies the validator's failure modes.
- `.github/CODEOWNERS` marks `/docs/review-context/` for owner review.
