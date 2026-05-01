# Claude Plugin Marketplace Checklist

**Status:** Pre-submission checklist
**Last verified:** 2026-05-01

## Official Path

Claude Code has a first-class plugin system. A plugin can package skills, commands, agents, hooks, MCP servers, LSP servers, binaries, and settings. The plugin root uses `.claude-plugin/plugin.json`.

Official docs describe:

- local plugin testing with `claude --plugin-dir ./my-plugin`;
- an official Anthropic marketplace;
- custom team marketplaces with `.claude-plugin/marketplace.json`;
- marketplace submission through Claude.ai or Anthropic Console forms.

Sources:

- [Create plugins](https://code.claude.com/docs/en/plugins)
- [Discover and install prebuilt plugins](https://code.claude.com/docs/en/discover-plugins)
- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)

## Vulca Submission Scope

Lead with the workflows that are already product-ready:

- `/decompose`
- `/visual-discovery`
- `/visual-brainstorm`
- `/visual-spec`
- `/visual-plan`
- `/evaluate`

Do not lead marketplace copy with redraw. Redraw and inpaint can be described as advanced MCP tools, but polished user-facing `/inpaint` or `/redraw-layer` promotion should wait for real-image dogfood evidence from the v0.22 target-aware mask refinement route.

## Package Layout

The marketplace plugin root is the repository root:

- `.claude-plugin/plugin.json`
- `skills/`
- `.mcp.json`

The source of truth for skill authoring remains `.agents/skills/`. Run this after changing a skill:

```bash
python scripts/sync_plugin_skills.py
```

That syncs:

- `.claude/skills/` for project-local Claude iteration;
- `skills/` for Claude plugin packaging;
- `plugins/vulca/skills/` for Codex plugin packaging.

## Pre-Submission Gate

Run before official submission:

```bash
claude --plugin-dir .
```

Then verify in a clean Claude Code session:

- the Vulca plugin appears with the expected name and description;
- the skill list includes the six promoted workflows;
- the MCP server starts without manual path repair;
- a no-cost workflow succeeds with `mock` provider artifacts;
- a real-provider workflow clearly requires explicit opt-in;
- public copy does not include fixed MCP tool counts.

## Submission Packet

Prepare:

- one-sentence value proposition;
- three workflow screenshots or terminal captures;
- install and authentication notes;
- privacy note for local files and optional provider API keys;
- v0.22 redraw status note;
- support contact and repository URL.

## Fallback

If official review takes longer than launch timing, create a Git-backed custom marketplace with `.claude-plugin/marketplace.json` and publish it as a private or community install path. Keep the official marketplace submission as the primary distribution target.
