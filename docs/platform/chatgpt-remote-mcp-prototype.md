# ChatGPT Remote MCP

**Status:** Initial remote-safe server
**Last verified:** 2026-05-01

## Purpose

Expose a conservative Vulca MCP profile for ChatGPT developer mode and OpenAI API remote MCP experiments.

This profile now has a dedicated FastMCP server entry point. It is still a deployment prototype: production hosting, TLS, authentication, audit logging, and account-level ChatGPT app setup remain separate gates.

## Allowed Tools

- `list_traditions`
- `get_tradition_guide`
- `search_traditions`
- `compose_prompt_from_design`
- `evaluate_artwork`

`evaluate_artwork` defaults to `mock=True` and `mode="rubric_only"` for the remote profile. In this mode Vulca returns the resolved L1-L5 rubric payload and does not read image pixels or call a VLM. Pixel-reading evaluation is intentionally not exposed by this first remote server.

`compose_prompt_from_design` reads a user-supplied `design.md` path. The remote server constrains that path to `VULCA_REMOTE_WORKSPACE_ROOT`; relative paths resolve inside that root and absolute paths outside that root are rejected.

## Not Exposed By Default

Generation, inpaint, redraw, layer mutation, archive/sync/admin tools, and auto-registered pixel analysis tools are not exposed by the first remote profile.

## Responses API Pattern

```python
tools = [
    {
        "type": "mcp",
        "server_label": "vulca",
        "server_url": "https://example.com/mcp",
        "allowed_tools": [
            "list_traditions",
            "get_tradition_guide",
            "search_traditions",
            "compose_prompt_from_design",
            "evaluate_artwork",
        ],
        "require_approval": "always",
    }
]
```

## Run Locally

Install with the MCP extra, then start the remote-safe profile:

```bash
VULCA_REMOTE_WORKSPACE_ROOT=/absolute/path/to/workspace \
VULCA_REMOTE_MCP_HOST=127.0.0.1 \
VULCA_REMOTE_MCP_PORT=8765 \
VULCA_REMOTE_MCP_PATH=/mcp \
vulca-mcp-remote
```

Default transport is `streamable-http`. For local stdio debugging only:

```bash
VULCA_REMOTE_MCP_TRANSPORT=stdio vulca-mcp-remote
```

Use `http://127.0.0.1:8765/mcp` for local API experiments. ChatGPT developer mode requires a remotely reachable server URL; use HTTPS, auth, and logging before connecting a public endpoint.

## Privacy Rules

- Do not pass private images to a remote server without explicit user approval.
- Do not pass private project paths to a remote server unless the path is inside `VULCA_REMOTE_WORKSPACE_ROOT`.
- Do not enable pixel-reading or provider-backed VLM evaluation by default.
- Do not expose filesystem-writing tools in the first prototype.
- Keep all cost-incurring tools behind explicit opt-in.
