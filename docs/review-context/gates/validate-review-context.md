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

Passing this gate is necessary but not sufficient. A curator must still apply
source and claim judgment.

Repository-level checks:

- `.github/workflows/review-context.yml` runs this gate on pull requests and
  pushes that touch the vault.
- `tests/test_review_context_vault.py` verifies the validator's failure modes.
- `.github/CODEOWNERS` marks `/docs/review-context/` for owner review.
