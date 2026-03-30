# VULCA

[![PyPI version](https://img.shields.io/pypi/v/vulca.svg)](https://pypi.org/project/vulca/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://pypi.org/project/vulca/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://github.com/vulca-org/vulca/blob/main/LICENSE)
[![Tests](https://img.shields.io/badge/tests-877%20passing-brightgreen.svg)]()

Cultural AI art evaluation and creation SDK. Score artwork on 5 dimensions (L1-L5) across 13 cultural traditions. Self-evolving — the system learns from every session.

<p align="center">
  <img src="assets/demo-v070.svg" alt="VULCA CLI Demo" width="800">
</p>

## Where to Use

### Claude Code / Cursor (MCP Plugin)

```bash
pip install vulca[mcp]
claude plugin install vulca-org/vulca-plugin
```

Then just ask: *"Evaluate this painting for Chinese xieyi style"* — Claude calls VULCA automatically.

18 MCP tools available: `evaluate_artwork`, `create_artwork`, `studio_create_brief`, `inpaint_artwork`, `analyze_layers`, and more.

### ComfyUI

```bash
# In ComfyUI/custom_nodes/
git clone https://github.com/vulca-org/comfyui-vulca
pip install vulca>=0.9.1
```

11 nodes: Brief, Concept, Generate, Evaluate, Update, Inpaint, Layers Analyze/Composite/Export, Evolution, Traditions.

### CLI

```bash
pip install vulca

vulca evaluate painting.jpg --tradition chinese_xieyi
vulca create "Misty mountains in ink wash" --provider mock
vulca studio                                    # interactive Brief-driven session
vulca layers split artwork.png --output ./layers
vulca inpaint artwork.png --region "sky" --instruction "add clouds"
vulca sessions stats                            # analyze 800+ local sessions
vulca resume <session-id>                       # resume from checkpoint
```

### Python SDK

```python
import vulca

# Evaluate
result = vulca.evaluate("artwork.png", tradition="chinese_xieyi")
print(result.score, result.dimensions, result.suggestions)

# Create
result = vulca.create("Tea packaging with mountain landscape", provider="mock")
print(result.best_image_b64[:50], result.weighted_total)

# Studio (Brief-driven multi-round)
session = vulca.StudioSession.from_intent("Zen garden at dawn")
session.generate_concepts()
session.select(0)
session.accept()
```

## Features

### Evaluation (L1-L5)

5-dimension cultural scoring based on peer-reviewed research:

| Dimension | What it measures |
|-----------|-----------------|
| **L1** Visual Perception | Composition, color harmony, spatial arrangement |
| **L2** Technical Execution | Rendering quality, technique fidelity, craftsmanship |
| **L3** Cultural Context | Tradition-specific motifs, canonical conventions |
| **L4** Critical Interpretation | Cultural sensitivity, contextual framing |
| **L5** Philosophical Aesthetics | Artistic depth, emotional resonance, spiritual qualities |

Each dimension returns: score (0-1), observations, rationale, actionable suggestion, reference technique, deviation type.

### Three Evaluation Modes

- **strict** (default): Judge — scores reflect tradition conformance
- **reference**: Advisor — shows cultural alignment without judgment
- **fusion**: Compare against multiple traditions simultaneously

### Creation Pipeline

```
Generate → Evaluate → Decide → (loop if below threshold)
```

Multi-round with automatic improvement: each round targets the weakest dimensions from the previous evaluation. HITL (Human-in-the-Loop) pause supported.

### Studio (Brief-Driven)

```
Intent → Brief → Concepts → Select → Generate → Evaluate → Refine
```

Natural language throughout: *"Make the teapot larger"*, *"Add more warmth to the color palette"*.

### Layers

Split artwork into semantic layers (Photoshop-style minimal crop + bbox offset), composite back, export as PNG directory with manifest.

### Inpainting

Region-based repaint with pixel-level guarantee: pixels outside the bounding box are 100% preserved (PIL local blend, not full-image regeneration).

### Tool Protocol (v0.9.1)

5 algorithmic analysis tools that run without API calls:

| Tool | What it does |
|------|-------------|
| `whitespace_analyze` | Detect negative space patterns |
| `composition_analyze` | Rule of thirds, center weight, balance |
| `color_gamut_check` | Saturation profiling + fix mode |
| `brushstroke_analyze` | Sobel gradient direction detection |
| `color_correct` | Color correction with check/fix/suggest |

Hybrid pipeline: algorithmic tools run first, VLM evaluation covers remaining dimensions.

### Self-Evolution (Closed Loop)

The system learns from every session:

1. Pipeline scores feed into `LocalEvolver` → evolved weights
2. **GenerateNode** reads evolved weights → strengthens historically weak dimensions
3. **EvaluateNode** reads evolved weights → calibrated scoring
4. **DecideNode** reads evolved threshold → adaptive accept/rerun decisions
5. `eval_mode` aware: strict sessions strengthen tradition; reference sessions track exploration trends
6. `deviation_type` filtering: intentional departures are not treated as weaknesses

### Pipeline Checkpoint

Every round auto-saved to `~/.vulca/data/checkpoints/`. Resume from any round:

```bash
vulca resume <session-id> --from-round 2
```

## 13 Cultural Traditions

`chinese_xieyi` `chinese_gongbi` `japanese_traditional` `western_academic` `islamic_geometric` `watercolor` `african_traditional` `south_asian` `contemporary_art` `photography` `brand_design` `ui_ux_design` + `default`

Custom traditions via YAML:

```bash
vulca tradition --init my_style.yaml   # generate template
vulca evaluate painting.jpg --tradition ./my_style.yaml
```

## Install

```bash
pip install vulca           # core SDK + CLI
pip install vulca[mcp]      # + MCP server for Claude Code / Cursor
```

No API key required for mock mode. For real VLM scoring:

```bash
export GOOGLE_API_KEY=your-key
```

## Citation

```bibtex
@inproceedings{yu2025vulca,
  title={VULCA: A Framework for Culturally-Aware Visual Understanding},
  author={Yu, Haorui},
  booktitle={Findings of EMNLP 2025},
  year={2025}
}
```

## License

Apache 2.0

---

> **Source of truth**: This repository is synced from the [VULCA monorepo](https://github.com/yha9806/website) via `git subtree`. Development happens in the monorepo; this repo is the public distribution mirror. Issues and PRs are welcome here.
