# Contributing to Vulca

Vulca is a solo-maintained, dogfooding-driven project: every feature ships
only after the maintainer uses it on a real cultural-evaluation workflow.
PRs are welcome but will be judged against that bar.

## Before you start

1. Skim `README.md` and the active plan in `docs/superpowers/plans/`.
2. Confirm the change is **agent-native** — Vulca is an agent's hands and
   eyes, not its brain. Features that hide decisions from the agent or
   centralise prompt logic in Python are unlikely to land.
3. For anything non-trivial, open a Discussion first.

## Dev loop

```bash
pip install -e ".[dev]"
pytest tests/               # ~12 cv2/layered baseline failures are expected locally
ruff check src/ tests/
```

The MCP surface lives in `src/vulca/mcp_server.py`. Any new tool must:
- have a schema test under `tests/test_mcp_parity.py` or `tests/test_mcp_new_tools.py`
- be listed in the plugin manifest at `vulca-org/vulca-plugin`
- survive a live ship-gate (see `docs/superpowers/plans/*.md`)

## PR checklist

- One logical change per PR; commit messages follow existing style
  (see `git log` — `feat(...)`, `fix(...)`, `docs(plan): ...`).
- Tests added/updated; `pytest` passes (modulo pre-existing baseline).
- `CHANGELOG.md` updated under the next unreleased section.
- No binary artefacts (`gen_*.png`, `*.pth`) committed — see `.gitignore`.

By contributing you agree your work is licensed Apache-2.0.
