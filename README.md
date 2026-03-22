# VULCA

[![PyPI version](https://img.shields.io/pypi/v/vulca.svg)](https://pypi.org/project/vulca/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://pypi.org/project/vulca/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://github.com/vulca-org/vulca/blob/main/LICENSE)
[![Tests](https://img.shields.io/badge/tests-276%20passing-brightgreen.svg)]()

**Make any image generator culturally accurate.** VULCA scores visual works on 5 dimensions (L1-L5), tells you exactly what's wrong, and guides the next generation to fix it.

```bash
pip install vulca
export GOOGLE_API_KEY=your-key
vulca evaluate painting.jpg --tradition chinese_xieyi
```

```
VULCA Evaluation Result
========================================
Score:     95%
Tradition: chinese_xieyi

Dimensions:
  L1 Visual Perception         ███████████████████░ 95%
  L2 Technical Execution       ██████████████████░░ 90%
  L3 Cultural Context          ████████████████████ 98%
  L4 Critical Interpretation   ███████████████████░ 95%
  L5 Philosophical Aesthetics  ███████████████████░ 95%

Summary: Overall excellent (95%) under Chinese Xieyi tradition.
  Strongest: Cultural Context (98%).
  Room for growth: Technical Execution (90%).
```

> Based on peer-reviewed research: [VULCA Framework](https://aclanthology.org/2025.findings-emnlp/) (EMNLP 2025 Findings) and [VULCA-Bench](https://arxiv.org/abs/2601.07986) (7,410 samples, 9 traditions).

## What VULCA Does

Midjourney can generate a "Chinese ink wash painting" — but it uses the wrong brushstroke technique, has insufficient blank space, and applies Western perspective instead of scatter perspective. **It looks like Chinese painting but isn't culturally correct.**

VULCA fixes this:

```
Your image / Any generator's output
         ↓
    VULCA evaluates (L1-L5 + tradition-specific terminology)
         ↓
    Tells you: "L2: brushwork uses axe-cut texture (斧劈皴),
                xieyi should use hemp-fiber strokes (披麻皴)"
         ↓
    Re-generate with corrected guidance → re-evaluate
         ↓
    Scores improve: 0.34 → 0.72 → 0.89
```

## Install

```bash
pip install vulca
```

**Prerequisites**: Python 3.10+ and a [Google API key](https://aistudio.google.com/apikey) (free tier works for evaluation). No API key needed for `--mock` mode.

```bash
# Set your API key
export GOOGLE_API_KEY=your-key-here

# Verify it works
vulca evaluate painting.jpg --tradition chinese_xieyi
```

## Quick Start — Python SDK

```python
import vulca

# Evaluate any image (file path, URL, or base64)
result = vulca.evaluate("painting.jpg", tradition="chinese_xieyi")
print(result.score)          # 0.82
print(result.dimensions)     # {"L1": 0.75, "L2": 0.82, "L3": 0.86, ...}
print(result.rationales)     # {"L1": "Masterful use of blank space (留白)...", ...}
print(result.recommendations)  # ["Improve technical execution...", ...]

# Evaluate from URL
result = vulca.evaluate("https://example.com/artwork.jpg", tradition="watercolor")

# Create through the full pipeline (Generate → Evaluate → Decide)
result = vulca.create("Misty mountains in ink wash", tradition="chinese_xieyi", provider="gemini")
print(result.weighted_total) # 0.95
print(result.scores)         # {"L1": 0.95, "L2": 0.90, "L3": 0.95, ...}

# Bring your own image generator
from vulca import ImageProvider, ImageResult

class MyLocalSD:
    async def generate(self, prompt, **kwargs):
        image_bytes = my_model.generate(prompt)  # your model
        return ImageResult(image_b64=base64.b64encode(image_bytes).decode())

result = vulca.create("landscape", image_provider=MyLocalSD())

# No API key? Mock mode for testing
result = vulca.evaluate("painting.jpg", mock=True)
```

## Quick Start — CLI

```bash
# Evaluate artwork with real Gemini VLM scoring
vulca evaluate painting.jpg --tradition chinese_xieyi

# Evaluate from URL
vulca evaluate "https://example.com/art.jpg" -t watercolor

# Create artwork via Gemini image generation + evaluation
vulca create "仿倪瓒枯木竹石，干笔淡墨" --provider gemini -t chinese_xieyi

# List all 13 available traditions
vulca traditions

# Get cultural guide (terminology, taboos, weights)
vulca tradition chinese_xieyi

# Check how weights have evolved
vulca evolution chinese_xieyi

# HITL mode with custom L1-L5 weights
vulca create "水墨山水" --hitl --weights "L1=0.3,L2=0.2,L3=0.2,L4=0.15,L5=0.15"

# JSON output for scripting
vulca evaluate painting.jpg --mock --json
```

### Example Output — `vulca traditions`

```
Available Domains (13):
==================================================
  african_traditional       emphasis: Cultural (30%)
  brand_design              emphasis: Technical (30%)
  chinese_gongbi            emphasis: Technical (30%)
  chinese_xieyi             emphasis: Philosophical (30%)
  contemporary_art          emphasis: Cultural (30%)
  islamic_geometric         emphasis: Technical (30%)
  japanese_traditional      emphasis: Philosophical (25%)
  photography               emphasis: Visual (25%)
  south_asian               emphasis: Cultural (25%)
  ui_ux_design              emphasis: Technical (30%)
  watercolor                emphasis: Technical (25%)
  western_academic          emphasis: Technical (25%)
```

## BYOK — Bring Your Own Key / Model

```bash
# Gemini (evaluation + image generation)
export GOOGLE_API_KEY=your-key
vulca evaluate painting.jpg -t chinese_xieyi
vulca create "landscape" --provider gemini -t watercolor

# OpenAI DALL-E 3 (image generation only)
export OPENAI_API_KEY=your-key
vulca create "Zen garden" --provider openai -t japanese_traditional

# ComfyUI / local Stable Diffusion
vulca create "Oil painting" --provider comfyui --image-base-url http://localhost:8188

# Local VLM via Ollama (evaluation only)
vulca evaluate photo.jpg --vlm-model ollama/llava --vlm-base-url http://localhost:11434

# No API key at all — mock mode
vulca evaluate painting.jpg --mock
vulca create "水墨山水" --provider mock
```

## Claude Code Plugin

VULCA is available as a Claude Code plugin with 6 MCP tools + 3 skills + 1 agent.

```bash
# Option 1: Plugin (recommended)
claude plugin marketplace add vulca-org/vulca-plugin
claude plugin install vulca

# Option 2: MCP only
pip install vulca[mcp]
claude mcp add vulca -- vulca-mcp
```

Once installed, ask Claude Code naturally:

> "Evaluate this painting for Chinese xieyi tradition"
> "Create a Japanese ink wash landscape"
> "What traditions are available?"

### MCP Tools

| Tool | Description |
|------|-------------|
| `create_artwork` | Create artwork through the pipeline, returns image + L1-L5 scores |
| `evaluate_artwork` | Evaluate artwork on L1-L5 dimensions with rationale text |
| `list_traditions` | List all 13 domains with weights and emphasis |
| `get_tradition_guide` | Full cultural context: terminology, taboos, weights |
| `resume_artwork` | HITL continuation: accept, refine, or reject |
| `get_evolution_status` | Weight evolution history and insights per domain |

### Other AI Assistants

```bash
# OpenAI Codex CLI
codex mcp add vulca -- vulca-mcp

# OpenHands
[mcp]
stdio_servers = [{ name = "vulca", command = "vulca-mcp", args = [] }]
```

## L1-L5 Evaluation Framework

Five layers of evaluation, each reinterpreted per domain:

| Layer | What it measures | Traditional Art | UI/UX Design |
|-------|-----------------|----------------|--------------|
| **L1** | Surface Perception | Composition, ink harmony | Visual discoverability |
| **L2** | Technical Execution | Brushwork, medium mastery | Pattern compliance, WCAG |
| **L3** | Contextual Fit | Cultural tradition adherence | User mental model match |
| **L4** | Critical Reading | Narrative depth, symbolism | Intent-behavior alignment |
| **L5** | Deeper Meaning | Philosophical aesthetics | Design ethics |

Weights shift per domain — Chinese Xieyi weights L5 (philosophy) at 30%, Brand Design weights L2 (system adherence) at 30%.

### Domain Weights

| Domain | Emphasis | L1 | L2 | L3 | L4 | L5 |
|--------|----------|----|----|----|----|-----|
| Chinese Xieyi (写意) | Philosophical | .10 | .15 | .25 | .20 | **.30** |
| Chinese Gongbi (工笔) | Technical | .15 | **.30** | .25 | .15 | .15 |
| Japanese Traditional | Philosophical | .15 | .20 | .20 | .20 | **.25** |
| Islamic Geometric | Technical | .25 | **.30** | .20 | .15 | .10 |
| Western Academic | Technical | .20 | **.25** | .15 | .25 | .15 |
| African Traditional | Cultural | .15 | .20 | **.30** | .20 | .15 |
| Photography | Balanced | **.25** | .25 | .20 | .20 | .10 |
| Brand Design | Technical | .25 | **.30** | .25 | .15 | .05 |
| UI/UX Design | Technical | .20 | **.30** | .25 | .20 | .05 |

All weights evolve automatically from evaluation sessions. Run `vulca tradition <name>` to see domain-specific terminology and taboos.

## Self-Evolution

The system learns from every evaluation session:

1. **ContextEvolver** adjusts L1-L5 weights per domain based on scoring patterns
2. **FewShotUpdater** selects high-scoring examples (>=0.75) as calibration benchmarks
3. **VLM prompt** receives evolved weights, few-shot references, and domain insights
4. `vulca.get_weights(domain)` returns evolved weights, falling back to YAML defaults

## Contributing a Domain

Add a YAML file to `src/vulca/cultural/data/traditions/`:

```yaml
name: my_domain
display_name:
  en: "My Domain"
  zh: ""
weights:
  L1: 0.20
  L2: 0.20
  L3: 0.20
  L4: 0.20
  L5: 0.20
terminology:
  - term: "key concept"
    definition: "What this means in this domain"
taboos:
  - rule: "Do not judge X as Y in this domain"
    severity: medium
```

See `_template.yaml` for the full schema. PRs welcome.

## Architecture

```
vulca/
├── pipeline/     # Execution engine + 3 built-in nodes + 3 templates
├── providers/    # Pluggable ImageProvider + VLMProvider protocols
├── cultural/     # 13 YAML domain configs with L1-L5 weights
├── scoring/      # VLM model routing + L1-L5 types
├── storage/      # Session/Feedback protocol + JSONL backend
├── intent/       # Natural language → domain resolution
├── _vlm.py       # Gemini Vision L1-L5 scoring (core)
├── cli.py        # CLI entry point
└── mcp_server.py # MCP server (6 tools, FastMCP)
```

## Tests

```bash
pip install vulca[dev]
pytest tests/ -v  # 276 tests
```

## Citation

```bibtex
@inproceedings{yu2025vulca,
  title={VULCA: A Framework for Cultural Art Evaluation},
  author={Yu, Haorui},
  booktitle={Findings of EMNLP 2025},
  year={2025}
}
```

## License

Apache 2.0
