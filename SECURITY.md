# Security Policy

## Supported Versions

Only the latest released minor version on PyPI (`pip install vulca`) is
supported with security patches. Currently: **v0.17.x**.

## Reporting a Vulnerability

Email **yuhaorui48@gmail.com** with subject `vulca-security: <short title>`.
Please do not open a public issue or Discussion for anything that could
affect users running Vulca locally against their own ComfyUI / Gemini /
Ollama providers.

I aim to acknowledge within **72 hours** and ship a patch release within
**7 days** for high-severity issues (arbitrary file write via layer output
paths, prompt-injection escalation through `evaluate` VLM output,
credential leakage in provider adapters).

## Scope

In scope: the `vulca` PyPI package, the `vulca-org/vulca-plugin` Claude
Code / Cursor plugin, any shipped MCP tool schema, `.claude/skills/*`.

Out of scope: third-party providers (ComfyUI, Gemini, Ollama) —
report those upstream. Vulnerabilities requiring a malicious local
ComfyUI workflow JSON that the user manually installed are out of scope.

## Disclosure

Fixes are announced in `CHANGELOG.md` and tagged releases. Reporters
are credited unless they request otherwise.
