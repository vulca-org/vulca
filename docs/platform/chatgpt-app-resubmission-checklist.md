# ChatGPT App Resubmission Checklist

**Status:** Privacy-remediation checklist
**Created:** 2026-05-07

## Rejection Reason

OpenAI review rejected Vulca because the submitted privacy policy did not
clearly disclose all data uses. The requested remediation is a complete policy
covering data collected, purposes, recipients, retention, and user controls, and
alignment with current tool inputs and outputs.

Relevant OpenAI requirements:

- ChatGPT app submissions must include a clear, published privacy policy.
- The policy must cover categories of personal data collected, purposes of use,
  recipient categories, retention timelines, and user controls.
- Tool responses should return only data directly relevant to the request and
  avoid diagnostic, telemetry, or internal identifiers unless required.
- MCP tool responses should be audited for nested fields, debug payloads, PII,
  telemetry, internal IDs, and secrets.

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

## Dashboard Resubmission Notes

Use a concise release note:

```text
Privacy remediation after review feedback. Published a complete Vulca ChatGPT App privacy policy covering collected data, purposes, recipient categories, retention, and user controls. Audited remote MCP tool responses and removed unnecessary local path and diagnostic metadata from the submitted remote profile.
```

## Optional Email Reply

```text
Hello OpenAI review team,

Thank you for the review. We have remediated the privacy-policy issue for Vulca.

Changes made:
- Published a complete privacy policy covering data collected, purposes of use, recipient categories, retention timelines, and user controls.
- Audited the submitted ChatGPT App remote MCP profile and confirmed it exposes only the five review-safe tools: list_traditions, get_tradition_guide, search_traditions, compose_prompt_from_design, and evaluate_artwork.
- Removed unnecessary local path and diagnostic metadata from remote tool responses.
- Confirmed the submitted profile does not expose generation, image upload, pixel reading, redraw, inpaint, archive, sync, admin, or filesystem-writing tools.

Privacy policy URL:
<insert published URL>

We will resubmit the app from the OpenAI Platform dashboard.

Best,
Haorui Yu
```

