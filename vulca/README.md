# VULCA

[![PyPI version](https://img.shields.io/pypi/v/vulca.svg)](https://pypi.org/project/vulca/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://pypi.org/project/vulca/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://github.com/vulca-org/vulca/blob/main/LICENSE)
[![Tests](https://img.shields.io/badge/tests-276%20passing-brightgreen.svg)]()

**Multi-dimensional creative evaluation with cultural awareness.** L1-L5 scoring across 13+ domains, self-evolving weights, pluggable model backends.

VULCA evaluates visual works — from traditional ink wash paintings to UI mockups — using a five-layer framework (L1-L5) that goes beyond surface aesthetics into cultural context, critical interpretation, and philosophical depth. Each domain has its own weights, terminology, and taboos. The system learns from every evaluation session.

> Based on peer-reviewed research: [VULCA Framework](https://aclanthology.org/2025.findings-emnlp/) (EMNLP 2025 Findings) and [VULCA-Bench](https://arxiv.org/abs/2601.07986) (7,410 samples across 9 traditions).

## Install

```bash
pip install vulca
```

## Quick Start

```python
import vulca

# Evaluate traditional art
result = vulca.evaluate("painting.jpg", tradition="chinese_xieyi")
print(result.score)          # 0.82
print(result.dimensions)     # {"L1": 0.75, "L2": 0.82, "L3": 0.86, "L4": 0.79, "L5": 0.84}
print(result.rationales)     # {"L1": "Masterful use of blank space (留白)...", ...}

# Evaluate a UI design
result = vulca.evaluate("mockup.png", tradition="ui_ux_design")

# Evaluate a photograph
result = vulca.evaluate("photo.jpg", tradition="photography")

# Create through the full pipeline (Scout → Draft → Critic → Decide)
result = vulca.create("Misty mountains in ink wash", tradition="chinese_xieyi")
print(result.status)         # "completed"
print(result.weighted_total) # 0.82

# Human-in-the-loop with custom dimension weights
result = vulca.create(
    "水墨山水",
    provider="mock",
    hitl=True,
    weights={"L1": 0.3, "L2": 0.2, "L3": 0.2, "L4": 0.15, "L5": 0.15},
)
# result.status == "waiting_human" — pipeline pauses for human review

# Mock mode — no API key needed, great for testing
result = vulca.evaluate("painting.jpg", mock=True)
```

## CLI

```bash
# List all available domains (traditions + design + contemporary)
vulca traditions

# Get cultural guide for a domain (terminology, taboos, weights)
vulca tradition chinese_xieyi
vulca tradition photography
vulca tradition brand_design

# Evaluate artwork with L1-L5 scores
vulca evaluate painting.jpg --tradition chinese_xieyi
vulca evaluate mockup.png --tradition ui_ux_design
vulca evaluate photo.jpg --tradition photography

# Create through the pipeline
vulca create "Garden scene" --provider mock

# Check evolution status (how weights have shifted)
vulca evolution chinese_xieyi

# HITL mode with custom weights
vulca create "水墨山水" --hitl --weights "L1=0.3,L2=0.2,L3=0.2,L4=0.15,L5=0.15"

# Use different image/VLM providers
vulca create "landscape" --image-provider openai
vulca evaluate photo.jpg --vlm-model ollama/llava

# JSON output for scripting
vulca evaluate painting.jpg --mock --json
```

## AI Agent Integration (MCP)

VULCA ships a built-in [MCP](https://modelcontextprotocol.io/) server for AI coding assistants. 6 tools with `view` (summary/detailed) and `format` (json/markdown) parameters.

```bash
vulca-mcp  # Starts MCP server (stdio transport)
```

### Claude Code

```bash
claude mcp add vulca -- vulca-mcp
```

### OpenAI Codex CLI

```bash
codex mcp add vulca -- vulca-mcp
```

### OpenHands

```toml
[mcp]
stdio_servers = [{ name = "vulca", command = "vulca-mcp", args = [] }]
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `create_artwork` | Create artwork through the pipeline, returns image + L1-L5 scores + rationale |
| `evaluate_artwork` | Evaluate artwork on L1-L5 dimensions with rationale text |
| `list_traditions` | List all domains with emphasis and description |
| `get_tradition_guide` | Full cultural context: terminology, taboos, weights, evolution |
| `resume_artwork` | HITL continuation: accept, refine (with feedback), or reject |
| `get_evolution_status` | Weight evolution history and insights per domain |

## L1-L5 Evaluation Framework

Five layers of evaluation, each reinterpreted per domain:

| Layer | General | Traditional Art | UI/UX Design | Photography |
|-------|---------|----------------|--------------|-------------|
| **L1** | Surface Perception | Composition, ink harmony | Visual discoverability | Composition, light |
| **L2** | Technical Execution | Brushwork, medium mastery | Pattern compliance, WCAG | Exposure, focus, processing |
| **L3** | Contextual Fit | Cultural tradition adherence | User mental model match | Genre conventions |
| **L4** | Critical Reading | Narrative depth, symbolism | Intent-behavior alignment | Narrative power |
| **L5** | Deeper Meaning | Philosophical aesthetics | Design ethics | Artistic vision |

The same scoring engine handles all domains. L3-L5 weights shift dramatically — Chinese Xieyi weights L5 (philosophy) at 30%, while Brand Design weights L2 (system adherence) at 30%.

## Domains

### Cultural Traditions

| Tradition | Emphasis | L1 | L2 | L3 | L4 | L5 |
|-----------|----------|----|----|----|----|-----|
| Chinese Xieyi (写意) | Philosophical | 0.10 | 0.15 | 0.25 | 0.20 | 0.30 |
| Chinese Gongbi (工笔) | Technical | 0.15 | 0.30 | 0.25 | 0.15 | 0.15 |
| Japanese Traditional | Philosophical | 0.15 | 0.20 | 0.20 | 0.20 | 0.25 |
| Western Academic | Technical | 0.20 | 0.25 | 0.15 | 0.25 | 0.15 |
| Islamic Geometric | Technical | 0.25 | 0.30 | 0.20 | 0.15 | 0.10 |
| Watercolor | Cultural | 0.20 | 0.25 | 0.15 | 0.20 | 0.20 |
| African Traditional | Cultural | 0.15 | 0.20 | 0.30 | 0.20 | 0.15 |
| South Asian | Cultural | 0.15 | 0.20 | 0.25 | 0.15 | 0.25 |

### Design & Contemporary

| Domain | Emphasis | L1 | L2 | L3 | L4 | L5 |
|--------|----------|----|----|----|----|-----|
| Contemporary Art | Art-Historical | 0.10 | 0.15 | 0.30 | 0.25 | 0.20 |
| Photography | Balanced | 0.25 | 0.25 | 0.20 | 0.20 | 0.10 |
| Brand Design | Technical | 0.25 | 0.30 | 0.25 | 0.15 | 0.05 |
| UI/UX Design | Technical | 0.20 | 0.30 | 0.25 | 0.20 | 0.05 |

All weights evolve automatically through the self-evolution system. Run `vulca tradition <name>` to see domain-specific terminology and taboos.

## Pluggable Providers

Bring your own models for image generation and VLM scoring:

```python
from vulca.providers import ImageProvider, ImageResult

class MyLocalSD(ImageProvider):
    async def generate(self, prompt, **kwargs):
        # Call your model
        return ImageResult(image_b64="...", mime="image/png")

result = vulca.create("landscape", image_provider=MyLocalSD())
```

Built-in providers: `mock`, `gemini` (Google), `openai` (DALL-E 3), `comfyui` (local).

### BYOK Quick Start

**Gemini** (Google AI):
```bash
export GOOGLE_API_KEY=your-key-here
vulca create "Misty mountains" --provider gemini --tradition chinese_xieyi
vulca evaluate painting.jpg --tradition chinese_xieyi  # VLM scoring uses same key
```

**OpenAI** (DALL-E 3):
```bash
export OPENAI_API_KEY=your-key-here
vulca create "Zen garden" --provider openai --tradition japanese_traditional
```

**ComfyUI** (local Stable Diffusion):
```bash
# Start ComfyUI server first, then:
vulca create "Oil painting" --provider comfyui --image-base-url http://localhost:8188
```

**Local VLM** (Ollama, vLLM, etc.):
```bash
vulca evaluate photo.jpg --vlm-model ollama/llava --vlm-base-url http://localhost:11434
```

**No API key?** Use mock mode for testing:
```bash
vulca create "水墨山水" --provider mock
vulca evaluate painting.jpg --mock
```

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

## Canvas UI

The full web experience is live at [vulcaart.art](https://vulcaart.art):

- Real-time pipeline visualization with Intelligence Log
- HITL decision panel with L1-L5 rationale display
- Weight sliders for custom evaluation
- Reference image upload for guided creation
- Gallery with domain filtering

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
