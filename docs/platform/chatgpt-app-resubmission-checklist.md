# ChatGPT App Resubmission Checklist

**Status:** Privacy and screenshot remediation checklist
**Created:** 2026-05-07
**Last updated:** 2026-05-11

## Rejection Reasons

OpenAI review rejected Vulca for two issues:

1. The submitted privacy policy did not clearly disclose all data uses. The
   requested remediation is a complete policy covering data collected, purposes,
   recipients, retention, user controls, and alignment with current tool inputs
   and outputs.
2. The included screenshots did not meet OpenAI publishing requirements.

Relevant OpenAI requirements:

- ChatGPT app submissions must include a clear, published privacy policy.
- The policy must cover categories of personal data collected, purposes of use,
  recipient categories, retention timelines, and user controls.
- Tool responses should return only data directly relevant to the request and
  avoid diagnostic, telemetry, or internal identifiers unless required.
- MCP tool responses should be audited for nested fields, debug payloads, PII,
  telemetry, internal IDs, and secrets.
- The dashboard submission form requires app name, logo, description, company
  and privacy policy URLs, MCP and tool information, screenshots, test prompts
  and responses, and localization information.
- MCP server submissions must use a publicly accessible hosted domain, not a
  local or testing endpoint.
- Test cases should produce correct, relevant results on ChatGPT web and mobile
  apps, with no UI or image-loading errors.

## Code/Docs Remediation

- Publish `docs/platform/chatgpt-app-privacy-policy.md` at a stable public URL,
  for example:
  `https://github.com/vulca-org/vulca/blob/master/docs/platform/chatgpt-app-privacy-policy.md`
- Keep the submitted remote profile limited to:
  - `list_traditions`
  - `get_tradition_guide`
  - `search_traditions`
  - `compose_prompt_from_design`
  - `evaluate_artwork`
- Confirm `compose_prompt_from_design` does not echo `source_design_path`.
- Confirm remote `evaluate_artwork` does not echo `image_path` or `latency_ms`.
- Re-run remote-profile tests before resubmission.
- Run the submission preflight script before resubmission:
  ```bash
  PYTHONPATH=src python scripts/chatgpt_app_preflight.py \
    --submission chatgpt-app-submission.json \
    --privacy-url https://github.com/vulca-org/vulca/blob/master/docs/platform/chatgpt-app-privacy-policy.md \
    --mcp-url https://harryhurry-vulca-openai-mcp.hf.space/mcp
  ```
- Deploy the review-safe MCP profile to a public HTTPS host. The current
  resubmission endpoint is the Hugging Face Docker Space
  `https://harryhurry-vulca-openai-mcp.hf.space/mcp`, running
  `vulca[mcp]==0.23.1` from PyPI.
- If using Cloud Run instead, deploy `deploy/chatgpt-mcp/` to a direct Cloud Run
  service URL. The deployed command must run `vulca-mcp-remote`, not the full
  local `vulca-mcp` server.
- Do not use `https://vulcaart.art/mcp` for this resubmission unless Firebase
  Hosting has first been explicitly rewired to the deployed Cloud Run service
  and the production preflight command passes against that domain.
- Capture new app screenshots and test evidence using
  `docs/platform/chatgpt-app-screenshot-and-test-evidence.md`.

## Tool Response Audit

Run representative tool calls in ChatGPT developer mode or via MCP/API
Playground and record the raw responses.

Check that responses do not include:

- local filesystem paths;
- raw image bytes;
- full chat transcripts;
- precise location;
- API keys, OAuth tokens, passwords, or other secrets;
- request IDs, trace IDs, session IDs, internal account IDs;
- timestamps or latency diagnostics;
- unrelated debug payloads;
- provider raw responses.

Expected allowed response categories:

- public tradition identifiers and L1-L5 weights;
- public tradition guide content;
- user-supplied search tags echoed as `query_tags`;
- composed prompt fields derived from a user-approved design document;
- rubric-only L1-L5 evaluation payload.

## Screenshot Remediation

The previous screenshot set should be discarded and replaced. Use fresh
screenshots captured from the production public MCP endpoint and the actual
ChatGPT app experience.

Required checks before upload:

- The app name, icon, and relevant ChatGPT app UI are visible.
- Screenshots show real Vulca tool use, not terminal-only captures, source code,
  local docs, placeholders, or unrelated screens.
- No API keys, OAuth tokens, PyPI tokens, support emails, private user files,
  local filesystem paths, private images, trace IDs, or internal debug data are
  visible.
- The MCP URL is public HTTPS, not `localhost`, a LAN address, or a temporary
  testing endpoint.
- Text is readable after the dashboard upload preview.
- At least one test pass is recorded for ChatGPT web and one for mobile before
  resubmission.

If the dashboard displays stricter dimensions, aspect ratio, file size, or file
type constraints during upload, treat the dashboard validation as the source of
truth and update the screenshot evidence notes.

## Dashboard Resubmission Notes

Use a concise release note:

```text
Remediation after OpenAI review feedback. Published a complete Vulca ChatGPT App privacy policy covering collected data, tool inputs and outputs, purposes, recipient categories, retention, and user controls. Audited remote MCP tool responses and removed unnecessary local path and diagnostic metadata from the submitted remote profile. Replaced the prior screenshot set with fresh screenshots of the actual ChatGPT app experience, using the production public MCP endpoint and matching test prompts/responses.
```

## Optional Email Reply

```text
Hello OpenAI review team,

Thank you for the review. We have remediated the privacy-policy and screenshot issues for Vulca.

Changes made:
- Published a complete privacy policy covering data collected, current tool inputs and outputs, purposes of use, recipient categories, retention timelines, and user controls.
- Audited the submitted ChatGPT App remote MCP profile and confirmed it exposes only the five review-safe tools: list_traditions, get_tradition_guide, search_traditions, compose_prompt_from_design, and evaluate_artwork.
- Removed unnecessary local path and diagnostic metadata from remote tool responses.
- Confirmed the submitted profile does not expose generation, image upload, pixel reading, redraw, inpaint, archive, sync, admin, or filesystem-writing tools.
- Replaced the previous screenshot set with screenshots captured from the actual ChatGPT app experience against the production public MCP endpoint.
- Re-ran the representative test prompts/responses on ChatGPT web and mobile before resubmission.

Privacy policy URL:
<insert published URL>

Screenshot/test evidence:
<insert dashboard evidence or internal capture notes if useful>

We will resubmit the app from the OpenAI Platform dashboard.

Best,
Haorui Yu
```
