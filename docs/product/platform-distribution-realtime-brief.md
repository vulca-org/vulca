# Vulca Platform Distribution Realtime Brief

**Status:** Working brief for platform distribution
**Last verified:** 2026-04-30

This brief records current public platform facts for distributing Vulca into Claude, OpenAI/Codex/ChatGPT, and Google/Gemini workflows. It should be refreshed before marketplace submission, remote MCP launch, or public claims about platform support.

## Position

Vulca should ship through platform-native extension surfaces where they exist, while keeping the core artifact contract platform-independent.

- Claude Code: plugin marketplace path first.
- OpenAI Codex / ChatGPT: Codex plugin plus MCP path first; ChatGPT remote MCP app path second.
- Google / Gemini: provider integration now, ADK / Vertex Agent Engine path later.

## Claude Code

Claude Code has a first-class plugin system. Plugins can package skills, commands, agents, hooks, MCP servers, LSP servers, binaries, and settings. Plugin skills are namespaced by plugin name, which means Vulca's public commands should be documented as plugin-scoped when installed from a marketplace.

Current official facts:

- Plugins are for sharing versioned skills, agents, hooks, and MCP servers across projects and teams.
- Plugin structure keeps `.claude-plugin/plugin.json` at plugin root, with `skills/`, `commands/`, `agents/`, `hooks/`, `.mcp.json`, and related files also at plugin root.
- Plugins can be tested locally with `claude --plugin-dir ./my-plugin`.
- The official Anthropic marketplace is `claude-plugins-official`.
- Official marketplace submission is through Claude.ai or Console in-app forms.
- Teams can also create their own marketplace with `.claude-plugin/marketplace.json`, hosted on GitHub or another git host.

Sources:

- [Create plugins](https://code.claude.com/docs/en/plugins)
- [Discover and install prebuilt plugins](https://code.claude.com/docs/en/discover-plugins)
- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)

Vulca implication:

- The existing `.claude-plugin/plugin.json` should be treated as the packaging entry point, but it must not claim fixed MCP tool counts.
- Claude marketplace packaging needs root-level `skills/` and `.mcp.json`; keep those synced from `.agents/skills/` with `scripts/sync_plugin_skills.py`.
- Marketplace submission should wait until plugin install, skill invocation, MCP startup, and at least one no-cost workflow are tested in a fresh Claude Code session.
- The first official submission should emphasize `/decompose`, `/visual-discovery`, `/visual-brainstorm`, `/visual-spec`, `/visual-plan`, and `/evaluate`; `/inpaint` or `/redraw-layer` should wait for v0.22 evidence.

## OpenAI / Codex / ChatGPT

OpenAI exposes both Codex plugins and MCP as relevant integration paths. Codex has a plugin directory / marketplace experience for installing plugins, while Codex and ChatGPT also consume MCP servers. ChatGPT developer mode can create apps from remote MCP servers, and Responses API can call remote MCP servers through the `mcp` tool type.

Current official facts:

- Codex plugins can package skills, MCP servers, agents, hooks, commands, and assets with a `.codex-plugin/plugin.json` manifest.
- Codex has an official plugin marketplace and app directory experience, plus local and Git-backed marketplace sources.
- OpenAI's Codex plugin docs currently describe official public plugin publishing as coming soon; repo-local and personal marketplace testing are the practical near-term path.
- The observed local CLI exposes `codex marketplace add <source>` for adding a marketplace root.
- Codex can add MCP servers with `codex mcp add <name> --url <server-url>` or via `~/.codex/config.toml`.
- ChatGPT developer mode is a beta feature with full MCP client access for read and write tools.
- ChatGPT developer mode supports SSE and streaming HTTP remote MCP servers.
- ChatGPT developer mode can create apps from MCP servers; tools can be toggled and refreshed in app settings.
- Responses API supports remote MCP servers through a `tools` entry with `type: "mcp"`, `server_url`, `allowed_tools`, and `require_approval`.
- OpenAI warns that remote MCP servers can expose sensitive data or unsafe write actions; sensitive actions should require approval and tool exposure should be limited.
- Developer mode does not require `search` and `fetch`; general tools are allowed. Deep research / connector style docs still define `search` and `fetch` for research connectors.

Sources:

- [Codex plugins](https://developers.openai.com/codex/plugins)
- [Build a Codex plugin](https://developers.openai.com/codex/plugins/build)
- [OpenAI Docs MCP](https://platform.openai.com/docs/docs-mcp)
- [Building MCP servers for ChatGPT and API integrations](https://platform.openai.com/docs/mcp/)
- [Connectors and MCP servers](https://platform.openai.com/docs/guides/tools-remote-mcp)
- [ChatGPT Developer mode](https://platform.openai.com/docs/guides/developer-mode)

Vulca implication:

- Ship a Codex repo-local marketplace package first, using `plugins/vulca/.codex-plugin/plugin.json`.
- Keep the Codex plugin self-contained with copied skill files and a local `vulca-mcp` declaration.
- Treat official Codex public listing as a later submission path until OpenAI's public plugin publishing flow is available.
- Ship a local MCP guide for Codex alongside the plugin, using the existing `vulca-mcp` server.
- Design a remote MCP profile separately, with a conservative default tool set and explicit approval guidance.
- Recommended initial remote MCP allowlist: `list_traditions`, `get_tradition_guide`, `search_traditions`, `compose_prompt_from_design`, `evaluate_artwork`, `view_image` only after path/security handling is settled.
- Keep image generation, layer mutation, inpaint, redraw, paste-back, and filesystem-writing tools behind explicit opt-in and clear risk labeling.

## Google / Gemini

Google's immediate value for Vulca is provider infrastructure, not a direct equivalent of the Claude plugin marketplace. Gemini API and Vertex AI support image generation and editing, and Google ADK supports MCP tools for agents.

Current official facts:

- Gemini image generation and editing supports Gemini 2.5 Flash Image and Gemini 3 Pro Image preview on Vertex AI.
- Gemini 2.5 Flash Image supports 1024px output; Gemini 3 Pro Image preview supports up to 4096px.
- Gemini image models support text-to-image, text rendering, interleaved text/image output, and image-plus-text editing.
- Vertex AI Agent Engine supports deploying and managing production agents.
- Gemini API supports function calling with typed function declarations and modes such as AUTO, ANY, NONE, and VALIDATED.
- Google ADK documents MCP as a way to consume or expose tools to agents.

Sources:

- [Gemini image generation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Vertex AI Gemini image generation and editing](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation)
- [Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Vertex AI Agent Engine overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
- [Google ADK MCP](https://google.github.io/adk-docs/mcp/)

Vulca implication:

- Keep Gemini as a first-class provider for sketching, reference-heavy exploration, and provider comparisons.
- Document Google as "provider current, agent distribution planned" until an ADK or Vertex Agent Engine integration is implemented and tested.
- Do not claim Google has a Vulca marketplace-listing path for plugins.

## Redraw Distribution Rule

Redraw should not lead marketplace copy until v0.22 target-aware mask refinement passes a real-image dogfood gate.

Use this public wording until then:

> Redraw and inpaint tools are available for advanced workflows. Polished user-facing `/inpaint` or `/redraw-layer` skills will be promoted after v0.22 target-aware mask refinement evidence lands.

The first public marketplace copy should lead with artifact control, decomposition, discovery, prompt composition, and evaluation.

## Refresh Checklist

Before public launch:

- Re-open the official Claude plugin docs and confirm submission path still exists.
- Re-open the official Codex plugin docs and confirm public publishing status.
- Re-open OpenAI MCP and developer mode docs and confirm protocol/auth/support wording.
- Re-open Gemini / Vertex AI docs and confirm image model names and limits.
- Run plugin install from a clean Claude Code session.
- Run Codex MCP config from a clean Codex session.
- Verify no public docs contain fixed MCP tool counts.
