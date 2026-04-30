# ChatGPT Remote MCP Prototype

**Status:** Prototype profile
**Last verified:** 2026-04-30

## Purpose

Expose a conservative Vulca MCP profile for ChatGPT developer mode and OpenAI API remote MCP experiments.

## Allowed Tools

- `list_traditions`
- `get_tradition_guide`
- `search_traditions`
- `compose_prompt_from_design`
- `evaluate_artwork`

`evaluate_artwork` defaults to `mock=True` and `mode="rubric_only"` for the remote profile.

`compose_prompt_from_design` reads a user-supplied `design.md` path. Remote deployments must require approval before calling it and should constrain approved paths to the configured workspace.

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

## Privacy Rules

- Do not pass private images to a remote server without explicit user approval.
- Do not pass private project paths to a remote server unless the path is in the approved workspace.
- Do not enable provider-backed VLM evaluation by default.
- Do not expose filesystem-writing tools in the first prototype.
- Keep all cost-incurring tools behind explicit opt-in.
