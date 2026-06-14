# ChatGPT Prompt Studio Preview

Date: 2026-05-31

Prompt Studio is a preview-gated ChatGPT App flow. It lets Vulca package a
prompt, negative constraints, generation notes, and L1-L5 rubric priorities for
ChatGPT native image generation. It does not call Vulca provider image
generation.

## Enable Preview

Run the remote MCP server with:

```bash
VULCA_REMOTE_ENABLE_PROMPT_STUDIO=1 PYTHONPATH=src python3 -m vulca.mcp_remote
```

The default remote profile remains the submitted five-tool profile when the
environment variable is absent.

## Expected Preview Tools

- `list_traditions`
- `search_traditions`
- `get_tradition_guide`
- `compose_prompt_from_design`
- `evaluate_artwork`
- `open_prompt_studio`

## Boundary

Prompt Studio is a handoff UI. The widget calls the ChatGPT Apps bridge with
`sendFollowUpMessage` when the user presses `Generate in ChatGPT`. Vulca does not
receive generated image bytes and does not invoke OpenAI Image API, Responses API
image generation, Gemini, ComfyUI, or local image providers.

## Deployment Note

Do not deploy this preview to the submitted production MCP endpoint until the app
review risk is acceptable and the submission JSON is updated to match the new
tool surface.
