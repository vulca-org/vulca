# ChatGPT App Resubmission Evidence

**Status:** In progress
**Last updated:** 2026-05-13

This file tracks the evidence needed before resubmitting the Vulca ChatGPT App
after OpenAI review feedback.

## Current Local Evidence

- Remote-safe MCP profile is implemented by `vulca-mcp-remote`.
- The review deployment image installs the published package
  `vulca[mcp]==0.23.1` from PyPI.
- Submitted tool allowlist:
  - `list_traditions`
  - `get_tradition_guide`
  - `search_traditions`
  - `compose_prompt_from_design`
  - `evaluate_artwork`
- `chatgpt-app-submission.json` covers 5 tools, 6 positive test cases, and 4
  negative test cases.
- `docs/platform/chatgpt-app-privacy-policy.md` is present on `master`.
- The public website privacy route is live at
  `https://vulcaart.art/chatgpt-app-privacy`.
- Production browser verification on 2026-05-13 confirmed the desktop and
  mobile routes render `Vulca ChatGPT App Privacy Policy` and the submitted
  tool list, not the SPA fallback 404 page.

Run before submission:

```bash
PYTHONPATH=src python scripts/chatgpt_app_preflight.py \
  --submission chatgpt-app-submission.json \
  --privacy-url https://vulcaart.art/chatgpt-app-privacy \
  --mcp-url https://harryhurry-vulca-openai-mcp.hf.space/mcp
```

## Deployment Evidence

Production MCP URL:

```text
https://harryhurry-vulca-openai-mcp.hf.space/mcp
```

Deployment command or workflow:

```text
Hugging Face Space: harryHURRY/vulca-openai-mcp
SDK: docker
Hardware: cpu-basic
Runtime package: vulca[mcp]==0.23.1 from PyPI
MCP path: /mcp
```

Expected deployed profile:

```text
VULCA_REMOTE_MCP_TRANSPORT=streamable-http
VULCA_REMOTE_MCP_HOST=0.0.0.0
VULCA_REMOTE_MCP_PATH=/mcp
VULCA_REMOTE_WORKSPACE_ROOT=/app/workspace
```

## Screenshot Evidence

Capture from the actual ChatGPT app experience after the production MCP endpoint
is configured. Do not reuse screenshots from local terminal sessions, local
docs, source code, or prior rejected builds.

Required captures:

- `01-vulca-app-connected.png`
- `02-list-traditions.png`
- `03-get-tradition-guide.png`
- `04-search-traditions.png`
- `05-compose-prompt.png`
- `06-evaluate-rubric.png`
- `07-mobile-smoke.png`

For each screenshot, verify:

- Vulca app name and relevant app UI are visible.
- The output comes from the production HTTPS MCP endpoint.
- No local filesystem paths, API keys, OAuth tokens, trace IDs, request IDs,
  session IDs, support inbox content, private images, or debug payloads are
  visible.

## Final Dashboard Values

Use these values unless the dashboard form has a stricter current constraint:

- App name: `Vulca`
- Subtitle: `Structure visual work`
- Category: `DESIGN`
- Privacy policy URL:
  `https://vulcaart.art/chatgpt-app-privacy`
- MCP server URL: `https://harryhurry-vulca-openai-mcp.hf.space/mcp`
- Tools: exactly the five allowlisted tools above.

Release note:

```text
Remediation after OpenAI review feedback. Published a complete Vulca ChatGPT App privacy policy covering collected data, tool inputs and outputs, purposes, recipient categories, retention, and user controls. Audited remote MCP tool responses and removed unnecessary local path and diagnostic metadata from the submitted remote profile. Replaced the prior screenshot set with fresh screenshots of the actual ChatGPT app experience, using the production public MCP endpoint and matching test prompts/responses.
```
