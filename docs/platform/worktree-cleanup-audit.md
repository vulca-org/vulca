# Worktree Cleanup Audit

**Status:** Review notes
**Last checked:** 2026-04-30

## Worktrees

| Path | Branch | Status | Recommendation |
|---|---|---|---|
| `/Users/yhryzy/dev/vulca/.worktrees/platform-distribution-realtime-plan` | `codex/platform-distribution-realtime-plan` | Dirty by design | Keep for manual review, then stage/commit as the platform distribution package. |
| `/Users/yhryzy/dev/vulca/.worktrees/v0-22-mask-refinement` | `codex/v0-22-mask-refinement` | Dirty with redraw code/test changes plus showcase artifacts | Keep separate. Review and commit code/test changes before merging; decide separately whether showcase artifacts should be tracked. |
| `/Users/yhryzy/dev/vulca/.worktrees/cultural-term-benchmark-signal` | `codex/cultural-term-benchmark-signal` | Clean | No cleanup needed. |
| `/Users/yhryzy/.codex/worktrees/9919/vulca` | detached | Clean | Archive/remove later if no longer needed; no code cleanup needed. |
| `/Users/yhryzy/dev/vulca` | `master` | Dirty with local `.mcp.json` and many untracked demo/assets/log/model files | Do not auto-clean. Decide which generated artifacts matter, then either move to ignored local storage, track intentionally, or remove after backup. |

## Platform Branch Dirty Set

These files are expected for the current platform distribution work:

- `.claude-plugin/plugin.json`
- `.mcp.json`
- `.agents/skills/*/SKILL.md`
- `.claude/skills/*/SKILL.md`
- `skills/*/SKILL.md`
- `.agents/plugins/marketplace.json`
- `plugins/vulca/**`
- `scripts/sync_plugin_skills.py`
- `docs/platform/**`
- `docs/product/platform-distribution-realtime-brief.md`
- `docs/product/provider-capabilities.md`
- `docs/product/roadmap.md`
- `docs/superpowers/plans/2026-04-30-platform-distribution-redraw-hardening.md`
- `tests/test_visual_discovery_docs_truth.py`

## Main Worktree Notes

Main has a local `.mcp.json` that loads `/Users/yhryzy/dev/vulca/.env.local` before starting `/opt/homebrew/bin/vulca-mcp`. That may be useful for local development, but it is user-machine-specific and should not be blindly committed into a public package.

Main also has many untracked generated or local files, including demo assets, visual-spec outputs, screenshots, `error.log`, `mobileclip_blt.ts`, and `rf-detr-base.pth`. These should be treated as local artifacts until a human decides otherwise.

## v0.22 Notes

The v0.22 worktree has dirty changes in:

- `src/vulca/layers/redraw.py`
- `tests/test_layers_redraw_refinement.py`
- `.superpowers/`
- `docs/visual-specs/2026-04-27-ipad-cartoon-roadside/v0_22_gpt_image_2/`

The redraw test gates pass, but this branch should be reviewed independently from platform distribution. Do not mix these files into the platform branch.

## Cleanup Policy

- Do not run destructive cleanup commands against main or v0.22 without an explicit final decision.
- Commit platform distribution changes separately from v0.22 redraw changes.
- Keep generated showcase artifacts out of commits unless they are part of a documented demo/release asset.
- Keep machine-specific MCP config out of public package defaults; use portable `vulca-mcp` config for plugin manifests.
