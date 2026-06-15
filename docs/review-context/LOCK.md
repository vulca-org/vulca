# Review Context Lock

Vault status: locked by policy.

## Non-Negotiable Rule

`docs/review-context/` is read-mostly project memory. It must not be casually
edited during ordinary feature work, website work, PPT work, release work, or
copywriting work.

Allowed default action:

- Read files in this folder.
- Cite files in this folder.
- Create a request packet proposing a change.

Disallowed default action:

- Editing a vault file directly from a normal product or implementation session.
- Rewriting historical conclusions without source evidence.
- Turning AI synthesis into human-confirmed evidence.
- Marking blocked, draft, internal, or experimental assets as public-ready.
- Moving this vault into another branch without preserving the governance rules.

## Only Curator Sessions May Modify

Direct vault edits are allowed only when all of these are true:

1. The session is explicitly acting as a context-curator session.
2. The work happens on `codex/vulca-context-vault` or a branch created from it.
3. The edit has a request packet or an explicit user instruction naming this
   vault as the target.
4. `MANIFEST.json` and `CHANGELOG.md` are updated when the protected context
   changes.
5. The local gate in `gates/validate_review_context.py` passes.

## Branch Boundary

The vault branch is not a feature branch. It is a protected memory branch.

- SDK implementation branches may read it.
- Platform / Workspace branches may read it.
- Website branches may read it.
- PPT and deck experiment branches may read it.
- None of those branches own the protected context.

## Claim Boundary

When in doubt, downgrade the claim. Use:

- `implemented`
- `tested locally`
- `internal proof`
- `draft`
- `public blocked`
- `requires human review`

Do not use:

- `public-ready`
- `production-quality`
- `human-confirmed`
- `commercially safe`
- `culturally correct`

unless the source evidence and project gate explicitly support it.
