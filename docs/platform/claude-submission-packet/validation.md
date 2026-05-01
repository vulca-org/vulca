# Claude Submission Validation

Run from the plugin package root after PR #28 is present.

```bash
/Users/yhryzy/.local/bin/claude plugin validate .
```

Observed on 2026-04-30: validation passed.

Repeated on 2026-05-01 from `master`: validation passed.

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

Focused post-merge validation also ran on 2026-05-01:

```bash
python3 -m pytest tests/test_visual_discovery_docs_truth.py tests/test_prompting.py tests/test_mcp_remote_profile.py tests/test_redraw_review_contract.py tests/test_mask_refine.py -q
```

Observed: 32 tests passed.

The public-doc forbidden phrase scan returned no matches for stale fixed MCP tool counts, unsupported platform-listing claims, or cultural-prompting overclaims.

Standalone plugin repository sync:

- `vulca-plugin` PR #9 synced the public Claude plugin repository to v0.19.0.
- PR #9 merged on 2026-05-01 at `55b6bb371544cd199e43f493b763d34e9cb85f5e`.
