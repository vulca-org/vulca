# Vulca Telemetry Policy

Vulca runtime telemetry is off by default. SDK, CLI, and MCP behavior must be identical when telemetry is disabled, and network failures must never affect a user workflow.

## Enabling And Disabling

Telemetry can be enabled by either:

- setting `VULCA_TELEMETRY=1`; or
- running `vulca telemetry enable`, which writes local config under the Vulca config directory.

Telemetry is disabled by default, by `VULCA_TELEMETRY=0`, by `vulca telemetry disable`, and always by `DO_NOT_TRACK=1`. `DO_NOT_TRACK=1` wins over every opt-in source.

Use `vulca telemetry status` to inspect the current state, config path, and anonymous install id status. Use `vulca telemetry reset-id` to delete the local anonymous install id.

## Event Envelope

Every emitted event uses this envelope:

- `event`
- `vulca_version`
- `python_version`
- `platform`
- `interface`: `cli`, `mcp`, or `sdk`
- `session_id`
- `anonymous_install_id`
- `timestamp`
- `properties`

The anonymous install id is a locally generated random UUID string. It is not derived from usernames, hostnames, file paths, API keys, prompts, images, or hardware identifiers.

## Allowed Events

Current runtime events:

- `cli_invoked`: command group only, such as `create`, `evaluate`, or `telemetry`.
- `mcp_server_started`: transport only.
- `mcp_tool_called`: tool name, status, and duration bucket only.

Future provider events may record provider id, success/failure, duration bucket, and usage/cost presence booleans, but not request content.

## Forbidden Fields

Telemetry must never include:

- prompts or user creative intent text;
- image paths or other local file paths;
- image bytes, masks, base64 payloads, or generated media;
- API keys, tokens, credentials, or account identifiers;
- local usernames, hostnames, or direct contact/payment identifiers;
- full stack traces or raw exception payloads.

The telemetry client uses an allowlist for event properties. Unknown property keys are dropped instead of scrubbed heuristically.

## Sink Behavior

If `VULCA_TELEMETRY_ENDPOINT` is unset, the default sink is a no-op even when telemetry is enabled. Tests and deployments may pass an explicit sink for controlled collection. Sink exceptions and network failures are swallowed and reported as an unsent event to the caller.

## Usage Runbook

To answer whether people are actually using Vulca:

1. Compare GitHub and PyPI awareness/install signals with runtime opt-in events.
2. Count `cli_invoked`, `mcp_server_started`, and first `mcp_tool_called` by anonymous install id.
3. Segment MCP depth by tool name, especially `layers_split`, `evaluate_artwork`, provider-backed generation, and remote profile starts.
4. Treat missing telemetry as unknown, not zero usage, because telemetry is opt-in.
5. Publish only aggregate counts; do not expose anonymous install ids in public reports.
