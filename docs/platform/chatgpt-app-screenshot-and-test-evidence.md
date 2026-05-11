# ChatGPT App Screenshot And Test Evidence Plan

**Status:** Capture plan for OpenAI App resubmission
**Created:** 2026-05-11

Use this plan after the privacy policy URL is live and before resubmitting Vulca
from the OpenAI Platform dashboard.

## Source Requirements

OpenAI's submission guide says the dashboard submission form requires app name,
logo, description, company and privacy policy URLs, MCP and tool information,
screenshots, test prompts and responses, and localization information.

OpenAI's review guidance also says common rejection reasons include test cases
that do not produce correct results, UI or image-loading errors, undisclosed
user-related fields in tool responses, and inaccurate tool hint annotations.

The rejection email for Vulca specifically says the included screenshots did
not meet publishing requirements. The public docs do not currently list exact
pixel dimensions for screenshots, so any dashboard upload validation for file
type, dimensions, aspect ratio, or file size is the source of truth.

Official references:

- `https://developers.openai.com/apps-sdk/deploy/submission`
- `https://developers.openai.com/apps-sdk/app-submission-guidelines`

## Capture Principles

- Capture from the production public MCP endpoint, not `localhost`, a LAN
  address, a tunnel, or a temporary test endpoint.
- Capture the actual ChatGPT app experience. Do not upload terminal-only
  screenshots, source code, local docs, dashboards, or placeholder mockups.
- Keep the app name, icon, prompt, tool result, and relevant ChatGPT UI visible.
- Use realistic but non-private prompts and sample content.
- Do not show API keys, OAuth tokens, PyPI tokens, support inbox content,
  private user images, local filesystem paths, request IDs, trace IDs, session
  IDs, internal account IDs, raw logs, or debug payloads.
- Preserve raw full-size PNG captures before creating upload-ready versions.
- If cropping is needed for the dashboard preview, crop only to remove browser
  chrome or irrelevant margins; do not stretch, blur, or obscure the UI.

## Required Screenshot Set

| File | Scenario | Prompt Or Screen | Acceptance Criteria |
| --- | --- | --- | --- |
| `01-vulca-app-connected.png` | App identity and connection state | Vulca app listing, enabled app screen, or direct app selection in ChatGPT | Shows Vulca name, icon, and connected or available state. No private account details are visible. |
| `02-list-traditions.png` | Discovery | `@Vulca list the supported visual traditions and summarize the L1-L5 rubric families.` | Output shows public tradition names or identifiers and L1-L5 rubric framing. |
| `03-get-tradition-guide.png` | Tradition guide | `@Vulca show the guide for chinese_xieyi and keep it concise.` | Output shows terminology, weights, taboos, or layer guidance for one tradition. |
| `04-search-traditions.png` | Search | `@Vulca find traditions related to ink wash, negative space, and restrained color.` | Output shows ranked public matches and matched terms. |
| `05-compose-prompt.png` | Prompt composition | `@Vulca compose a provider prompt from the approved design.md in the review workspace.` | Output shows composed prompt fields and does not reveal `source_design_path` or any local absolute path. |
| `06-evaluate-rubric.png` | Rubric-only evaluation | `@Vulca evaluate this artwork reference for chinese_xieyi using rubric-only mode: misty mountain ink study.` | Output shows an L1-L5 rubric payload or summary and does not reveal `image_path`, `latency_ms`, raw image bytes, or provider metadata. |
| `07-mobile-smoke.png` | Mobile smoke test | Repeat one discovery or guide prompt in ChatGPT mobile | Confirms the app produces correct, readable output on mobile. Use as evidence even if the dashboard only asks for desktop screenshots. |

If the dashboard allows only a smaller number of screenshots, upload the best
set in this order: `01`, `02`, `03`, `05`, `06`. Keep the remaining captures as
review evidence.

## Test Prompts And Expected Responses

Use these prompts in the dashboard test prompt/response fields or as reviewer
evidence.

| Prompt | Expected Tool | Expected Response Boundary |
| --- | --- | --- |
| `@Vulca list the supported visual traditions and summarize the L1-L5 rubric families.` | `list_traditions` | Public tradition identifiers, display names, categories, and L1-L5 weights only. |
| `@Vulca show the guide for chinese_xieyi and keep it concise.` | `get_tradition_guide` | Public guide content for `chinese_xieyi`; no user-related data. |
| `@Vulca find traditions related to ink wash, negative space, and restrained color.` | `search_traditions` | Ranked public matches and matched terms; may echo the supplied tags as `query_tags`. |
| `@Vulca compose a provider prompt from the approved design.md in the review workspace.` | `compose_prompt_from_design` | Prompt fields derived from approved design content; no `source_design_path` or absolute filesystem paths. |
| `@Vulca evaluate this artwork reference for chinese_xieyi using rubric-only mode: misty mountain ink study.` | `evaluate_artwork` | Rubric-only L1-L5 evaluation payload; no `image_path`, `latency_ms`, image bytes, VLM provider response, or trace metadata. |

## Pre-Upload QA

- Privacy policy URL opens without login and matches
  `docs/platform/chatgpt-app-privacy-policy.md`.
- Tool list in the dashboard matches the submitted remote profile exactly:
  `list_traditions`, `get_tradition_guide`, `search_traditions`,
  `compose_prompt_from_design`, and `evaluate_artwork`.
- Tool annotations are read-only, non-destructive, and not open-world.
- Raw tool responses were inspected for nested debug payloads and internal
  identifiers.
- Screenshots are captured after any metadata or server changes, not from an
  older rejected build.
- Uploaded screenshots remain readable in the dashboard preview.
- ChatGPT web and mobile test prompts both pass before clicking submit.

## Evidence Log Template

```text
Capture date:
Reviewer:
Production MCP URL:
Privacy policy URL:
Dashboard screenshot constraints observed:

Uploaded screenshots:
- 01-vulca-app-connected.png:
- 02-list-traditions.png:
- 03-get-tradition-guide.png:
- 05-compose-prompt.png:
- 06-evaluate-rubric.png:

Additional evidence retained:
- 04-search-traditions.png:
- 07-mobile-smoke.png:

Web test pass:
- Prompt:
- Tool selected:
- Result summary:
- Unexpected fields checked:

Mobile test pass:
- Prompt:
- Tool selected:
- Result summary:
- Unexpected fields checked:
```
