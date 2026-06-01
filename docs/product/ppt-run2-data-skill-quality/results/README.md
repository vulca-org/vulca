# Results

Status: reviewed-public-blocked.

Four local pilot arms were generated under `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/`:

- `ppt-run2-prompt-only`
- `ppt-run2-run1-5-skill`
- `ppt-run2-full-vulca`
- `ppt-run2-bad-aesthetic-memory`

Generated decks, contact sheets, previews, trace manifests, layout JSON, and delivery reports remain local under `outputs/` unless the user explicitly approves release packaging.

The reviewed internal result is that `run2_skill` is visibly stronger than `prompt_only` and `run1_5_skill` on aesthetic memory usage, rhythm variance, and density control. `bad_aesthetic_memory` degrades visual quality while preserving structural validity.

`audit_review.md` is the current release audit. `run2_1_readiness.md` records that the data cards, declarative skill workflow, and trace refresh utility are ready for a new four-arm rerun. Public publishing remains blocked until regenerated arms pass trace refresh, native or cross-platform render inspection, and human approval.
