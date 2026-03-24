# VULCA — Claude Code Plugin

Cultural art advisor for Claude Code. Score artworks on L1-L5 dimensions with actionable suggestions across 13+ cultural traditions. Supports strict (judge), reference (advisor), and fusion (multi-tradition comparison) modes.

## Install

```bash
# 1. Install the SDK (required)
pip install vulca[mcp]

# 2. Add the plugin marketplace
claude plugin marketplace add vulca-org/vulca-plugin

# 3. Install the plugin
claude plugin install vulca
```

**For real VLM scoring** (optional):
```bash
export GOOGLE_API_KEY=your-key-here
```

Mock mode works without any API key.

## What's Included

| Type | Name | Description |
|------|------|-------------|
| MCP Tool | `evaluate_artwork` | L1-L5 scoring with rationale, suggestions, and deviation analysis |
| MCP Tool | `create_artwork` | Generate → Evaluate → Decide pipeline with mode control |
| MCP Tool | `list_traditions` | Browse 13 cultural traditions |
| MCP Tool | `get_tradition_guide` | Terminology, taboos, weights |
| MCP Tool | `resume_artwork` | HITL: accept / refine / reject |
| MCP Tool | `get_evolution_status` | Weight evolution history |
| Skill | `/evaluate` | "Evaluate this artwork for Chinese xieyi" |
| Skill | `/create` | "Create a Japanese ink wash landscape" |
| Skill | `/tradition` | "What traditions are available?" |
| Agent | cultural-critic | Deep cross-tradition analysis |

## Usage

Just ask Claude Code naturally:

> "Evaluate painting.jpg for Chinese xieyi tradition"

> "Evaluate this image in reference mode — I want to see where it diverges from tradition"

> "Create a misty mountain landscape in ink wash style"

> "Compare how this image scores in watercolor vs photography traditions"

### New in v0.4: Evaluation Modes

- **strict** (default): Judge mode — scores reflect conformance, pipeline reruns to improve
- **reference**: Advisor mode — shows alignment without judgment, no forced reruns
- **fusion**: Compare against multiple traditions at once

## Providers

Image generation: `mock` (no key), `gemini` (Google), `openai` (DALL-E 3), `comfyui` (local SD)

VLM scoring: Gemini (default), or any LiteLLM-supported model via `--vlm-model`

## Links

- SDK: [vulca-org/vulca](https://github.com/vulca-org/vulca) | [PyPI](https://pypi.org/project/vulca/)
- Paper: [VULCA Framework](https://aclanthology.org/2025.findings-emnlp/) (EMNLP 2025)
