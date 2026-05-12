# ChatGPT App Resubmission Evidence

**Status:** In progress
**Last updated:** 2026-05-12

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
- `docs/platform/chatgpt-app-privacy-policy.md` is present on `master` and is
  reachable at:
  `https://github.com/vulca-org/vulca/blob/master/docs/platform/chatgpt-app-privacy-policy.md`

Run before submission:

```bash
PYTHONPATH=src python scripts/chatgpt_app_preflight.py \
  --submission chatgpt-app-submission.json \
  --privacy-url https://github.com/vulca-org/vulca/blob/master/docs/platform/chatgpt-app-privacy-policy.md \
  --mcp-url https://<production-service-url>/mcp
```

## Deployment Evidence

Production MCP URL:

```text
TODO: https://<cloud-run-service-url>/mcp
```

Deployment command or workflow:

```text
Use deploy/chatgpt-mcp/Dockerfile with deploy/chatgpt-mcp/cloudbuild.yaml.
The image installs vulca[mcp]==0.23.1 from PyPI and runs vulca-mcp-remote.
Deploy the built image directly to Cloud Run with VULCA_REMOTE_MCP_* environment
values and submit the Cloud Run service URL plus /mcp.
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
  `https://github.com/vulca-org/vulca/blob/master/docs/platform/chatgpt-app-privacy-policy.md`
- MCP server URL: `TODO: https://<cloud-run-service-url>/mcp`
- Tools: exactly the five allowlisted tools above.

Release note:

```text
Remediation after OpenAI review feedback. Published a complete Vulca ChatGPT App privacy policy covering collected data, tool inputs and outputs, purposes, recipient categories, retention, and user controls. Audited remote MCP tool responses and removed unnecessary local path and diagnostic metadata from the submitted remote profile. Replaced the prior screenshot set with fresh screenshots of the actual ChatGPT app experience, using the production public MCP endpoint and matching test prompts/responses.
```
