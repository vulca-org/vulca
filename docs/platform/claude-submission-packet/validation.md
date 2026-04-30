# Claude Submission Validation

Run from the plugin package root after PR #28 is present.

```bash
/Users/yhryzy/.local/bin/claude plugin validate .
```

Observed on 2026-04-30: validation passed.

```bash
/Users/yhryzy/.local/bin/claude --plugin-dir . --print --max-budget-usd 0.20 --permission-mode dontAsk "Reply with only the Vulca plugin skill names you can see from loaded plugins; do not use tools."
```

Observed on 2026-04-30: output included all seven plugin skills:

- `vulca:visual-discovery`
- `vulca:decompose`
- `vulca:evaluate`
- `vulca:visual-spec`
- `vulca:visual-brainstorm`
- `vulca:using-vulca-skills`
- `vulca:visual-plan`

PR #28 platform package validation also ran:

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_prompting.py tests/test_visual_discovery_docs_truth.py tests/test_visual_discovery_prompting.py tests/test_visual_discovery_benchmark.py tests/test_gemini_image_size.py tests/test_generate_image_extended_signature.py -q
```

Observed on 2026-04-30: 60 tests passed.

The public-doc forbidden phrase scan returned no matches for stale fixed MCP tool counts, unsupported platform-listing claims, or cultural-prompting overclaims.
