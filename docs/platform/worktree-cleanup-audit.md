# Worktree Cleanup Audit

**Status:** Review notes
**Last checked:** 2026-05-01

## Worktrees

| Path | Branch | Status | Recommendation |
|---|---|---|---|
| `/Users/yhryzy/dev/vulca/.worktrees/real-brief-benchmark-design` | `codex/real-brief-benchmark-design` | Clean, ahead of its upstream by 5 commits | Keep separate from platform distribution. Review/push/PR when benchmark design is ready. |
| `/Users/yhryzy/.codex/worktrees/9919/vulca` | detached | Clean | Archive/remove later if no longer needed; no code cleanup needed. |
| `/Users/yhryzy/dev/vulca` | `master` | No tracked edits; untracked demo/spec/research artifacts remain | Do not auto-clean. Decide which generated artifacts matter, then either move to ignored local storage, track intentionally, or remove after backup. |

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

Main previously had a local `.mcp.json` that loaded `/Users/yhryzy/dev/vulca/.env.local` before starting `/opt/homebrew/bin/vulca-mcp`. That user-machine-specific version is preserved in `stash@{0}` as `codex-local-mcp-before-origin-master-ff`; the tracked package uses the portable `vulca-mcp` config.

Main also has many untracked generated or local files, including demo assets, visual-spec outputs, screenshots, `error.log`, `mobileclip_blt.ts`, and `rf-detr-base.pth`. These should be treated as local artifacts until a human decides otherwise.

## v0.22 Notes

v0.22 target-aware mask refinement has merged to `master`. Keep redraw promotion gated on real-image dogfood and final paste-back review; do not market sparse transparent layer outputs as final after-images.

## Cleanup Policy

- Do not run destructive cleanup commands against main or v0.22 without an explicit final decision.
- Commit platform distribution changes separately from v0.22 redraw changes.
- Keep generated showcase artifacts out of commits unless they are part of a documented demo/release asset.
- Keep machine-specific MCP config out of public package defaults; use portable `vulca-mcp` config for plugin manifests.
