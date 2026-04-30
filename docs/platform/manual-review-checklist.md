# Platform Manual Review Checklist

**Status:** Human review checklist
**Last verified:** 2026-04-30

Use this checklist before merging or submitting Vulca to a plugin directory.

## Files To Review

- `.claude-plugin/plugin.json`
- `.mcp.json`
- `skills/*/SKILL.md`
- `.agents/plugins/marketplace.json`
- `plugins/vulca/.codex-plugin/plugin.json`
- `plugins/vulca/.mcp.json`
- `plugins/vulca/skills/*/SKILL.md`
- `docs/platform/*.md`
- `docs/platform/release-readiness-status.md`
- `docs/product/platform-distribution-realtime-brief.md`
- `docs/product/provider-capabilities.md`
- `docs/product/roadmap.md`

## Automated Checks

Run:

```bash
python scripts/sync_plugin_skills.py
python -m pytest tests/test_visual_discovery_docs_truth.py tests/test_prompting.py -q
```

Then scan for overclaims:

```bash
grep -RIn "21 MCP tool[s]\|20 MCP tool[s]\|always improves generatio[n]\|proves cultural promptin[g]\|official Codex public listing is liv[e]" README.md pyproject.toml .claude-plugin .agents/skills .claude/skills skills docs/product docs/platform plugins/vulca src/vulca/mcp_server.py
```

Expected: no matches.

## Claude Manual Gate

Run in a clean Claude Code session:

```bash
claude --plugin-dir .
```

Verify:

- the plugin appears as `vulca`;
- skills are namespaced as `/vulca:<skill>`;
- `.mcp.json` starts `vulca-mcp`;
- `/vulca:visual-discovery` can complete a mock/no-cost workflow;
- `/vulca:evaluate` can evaluate an existing local artifact;
- redraw and inpaint are not presented as polished top-level user skills.

## Codex Manual Gate

The installed local CLI in this environment is `codex-cli 0.121.0` and exposes:

```bash
codex marketplace add .
```

Official docs currently show:

```bash
codex plugin marketplace add ./local-marketplace-root
```

Use whichever form the installed CLI supports, then restart Codex and verify:

- `Vulca Plugins` appears as a marketplace source;
- `Vulca` appears as an installable plugin;
- bundled skills are visible after install;
- `vulca-mcp` can start;
- plugin copy does not contain scaffold placeholder markers.

Do not state that official Codex public publishing has opened until OpenAI's docs change from "coming soon."

## Redraw Gate

Before marketplace copy leads with redraw:

- review and merge `codex/v0-22-mask-refinement`;
- run its redraw-focused tests;
- dogfood at least one real image where target-aware masks avoid editing unrelated pixels;
- confirm final user-facing image uses paste-back output, not sparse transparent layer output.
