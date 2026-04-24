---
name: Bug report
about: Something broken or unexpected in Vulca
title: "[bug] "
labels: bug
assignees: ''
---

## Summary

<!-- One-sentence description of the bug. -->

## Reproduction

```bash
# Commands / code that triggered the bug.
# Please paste exact args, environment variables, and any agent dialog excerpt.
```

## Expected vs actual

- **Expected**:
- **Actual**:

## Environment

- Vulca version: (run `pip show vulca | grep Version` or `python -c "import vulca; print(vulca.__version__)"`)
- Python: `python --version`
- OS: macOS / Linux / Windows — version + chip (Apple Silicon / Intel / AMD / etc.)
- Provider in play (if relevant): `mock` / `openai` (gpt-image-1.5/2) / `gemini` / `comfyui`
- Invocation: Claude Code MCP / direct SDK import / CLI (`vulca-mcp`) / plugin via `uvx`

## Logs

```
# Paste the full traceback or error output here.
# Redact API keys / personal paths if any.
```

## Additional context

<!-- Anything else: which skill was running (/visual-brainstorm, /visual-spec, /visual-plan, /decompose),
     relevant design.md / plan.md slug, recent config changes, etc. -->
