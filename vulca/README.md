# VULCA

[![PyPI version](https://img.shields.io/pypi/v/vulca.svg)](https://pypi.org/project/vulca/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://pypi.org/project/vulca/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://github.com/vulca-org/vulca/blob/main/LICENSE)
[![Tests](https://img.shields.io/badge/tests-462%20passing-brightgreen.svg)]()

**AI-native cultural art creation organism.** Brief-driven Studio pipeline, L1-L5 evaluation with actionable suggestions, Digestion learning system, and 13+ cultural traditions.

```bash
pip install vulca
export GOOGLE_API_KEY=your-key
vulca studio "水墨山水，远山含烟，留白三成"
```

> Based on peer-reviewed research: [VULCA Framework](https://aclanthology.org/2025.findings-emnlp/) (EMNLP 2025 Findings) and [VULCA-Bench](https://arxiv.org/abs/2601.07986) (7,410 samples, 9 traditions).

## What's New in v0.6.0

**Studio Intelligence** — Gemini LLM extracts implicit elements, palette, and composition from free-text intent. 10/10 simulated users complete sessions successfully.

**Digestion V2** — 4-layer learning system that accumulates user preferences in real-time, analyzes creative trajectories, and evolves tradition weights from real feedback.

## Quick Start

### Studio Pipeline (Brief-driven creation)

```bash
# Interactive creative session
vulca studio "赛博朋克水墨山水，霓虹灯光与传统笔触融合"

# With real image generation
vulca studio "misty mountain landscape" --provider gemini
```

The Studio walks you through 5 phases:

```
Intent → Concept → Generate → Evaluate → Refine
  ↑                                        ↓
  └──── Brief (living creative document) ←─┘
```

### Python SDK

```python
import vulca

# Evaluate any image
result = vulca.evaluate("painting.jpg", tradition="chinese_xieyi")
print(result.score)          # 0.72
print(result.suggestions)    # {"L2": "Replace axe-cut texture with hemp-fiber strokes", ...}

# Studio Pipeline V2
from vulca.studio import Brief, StudioSession
from vulca.studio.phases.intent import IntentPhase

brief = Brief.new("水墨山水，远山含烟，近水有桥")
phase = IntentPhase()
await phase.parse_intent_llm(brief)  # LLM extracts elements, palette, composition
print(brief.elements)  # [Element(name='远山'), Element(name='烟雾'), Element(name='桥')]

# Digestion V2 — learning from sessions
from vulca.digestion import (
    JsonlStudioStorage, SessionPreferences,
    preload_intelligence, build_session_digest,
)

# Pre-load intelligence from past sessions
ctx = preload_intelligence("水墨山水", data_dir="~/.vulca/data")
print(ctx["suggested_traditions"])  # ["chinese_xieyi"]

# Accumulate preferences during session
prefs = SessionPreferences()
prefs.update_from_signal({"action": "evaluate", "weakest": "L2", "strongest": "L5"})
print(prefs.to_prompt_hints())  # ["Pay special attention to L2..."]
```

### CLI

```bash
# Evaluate artwork
vulca evaluate painting.jpg --tradition chinese_xieyi

# Reference mode (advisor, not judge)
vulca evaluate painting.jpg -t chinese_xieyi --mode reference

# Create through pipeline
vulca create "仿倪瓒枯木竹石" --provider gemini -t chinese_xieyi

# List traditions
vulca traditions

# HITL mode with custom weights
vulca create "水墨山水" --hitl --weights "L1=0.3,L2=0.2,L3=0.2,L4=0.15,L5=0.15"

# No API key needed for testing
vulca evaluate painting.jpg --mock
vulca studio "test artwork" --provider mock
```

## L1-L5 Evaluation Framework

Five layers of evaluation, reinterpreted per domain:

| Layer | What it measures | Traditional Art | UI/UX Design |
|-------|-----------------|----------------|--------------|
| **L1** | Surface Perception | Composition, ink harmony | Visual discoverability |
| **L2** | Technical Execution | Brushwork, medium mastery | Pattern compliance, WCAG |
| **L3** | Contextual Fit | Cultural tradition adherence | User mental model match |
| **L4** | Critical Reading | Narrative depth, symbolism | Intent-behavior alignment |
| **L5** | Deeper Meaning | Philosophical aesthetics | Design ethics |

<details>
<summary><strong>Domain Weights (click to expand)</strong></summary>

| Domain | Emphasis | L1 | L2 | L3 | L4 | L5 |
|--------|----------|----|----|----|----|-----|
| Chinese Xieyi | Philosophical | .10 | .15 | .25 | .20 | **.30** |
| Chinese Gongbi | Technical | .15 | **.30** | .25 | .15 | .15 |
| Japanese Traditional | Philosophical | .15 | .20 | .20 | .20 | **.25** |
| Islamic Geometric | Technical | .25 | **.30** | .20 | .15 | .10 |
| Western Academic | Technical | .20 | **.25** | .15 | .25 | .15 |
| African Traditional | Cultural | .15 | .20 | **.30** | .20 | .15 |
| South Asian | Cultural | .15 | .20 | **.25** | .15 | .25 |
| Watercolor | Balanced | .20 | **.25** | .15 | .20 | .20 |
| Contemporary Art | Art-Historical | .10 | .15 | **.30** | .25 | .20 |
| Photography | Balanced | **.25** | .25 | .20 | .20 | .10 |
| Brand Design | Technical | .25 | **.30** | .25 | .15 | .05 |
| UI/UX Design | Technical | .20 | **.30** | .25 | .20 | .05 |

</details>

## Architecture

```
vulca/
├── studio/           # Brief-driven creative collaboration (462 tests)
│   ├── phases/       # Intent (LLM+keyword), Scout, Concept, Generate, Evaluate
│   ��── brief.py      # Living YAML document
│   ├── nl_update.py  # NL instruction parsing (LLM + keyword fallback)
│   └── interactive.py # Terminal UI with preloader + sketch + weight adjustment
├── digestion/        # 4-layer learning system
│   ��── preloader.py  # Layer 0: pre-session intelligence
│   ├── preferences.py # Layer 1: real-time preference accumulation
│   ├── trajectory.py # Layer 2: session completion analysis
│   ├── evolver.py    # Layer 3: cross-session evolution
│   ├── storage.py    # JSONL backend (Supabase-ready)
│   └── archiver.py   # Cold storage for long-term retention
├── pipeline/         # Execution engine + built-in nodes
├── providers/        # Pluggable ImageProvider + VLMProvider protocols
├── cultural/         # 13+ YAML tradition configs with L1-L5 weights
├── cli.py            # CLI entry point
└── mcp_server.py     # MCP server (6 tools, FastMCP)
```

## BYOK (Bring Your Own Key / Model)

```bash
# Gemini (evaluation + image generation)
export GOOGLE_API_KEY=your-key

# OpenAI DALL-E 3 (image generation)
export OPENAI_API_KEY=your-key

# ComfyUI / local Stable Diffusion
vulca create "Oil painting" --provider comfyui --image-base-url http://localhost:8188

# No API key — mock mode
vulca evaluate painting.jpg --mock
```

## Claude Code Plugin

```bash
claude plugin marketplace add vulca-org/vulca-plugin
claude plugin install vulca
```

| Tool | Description |
|------|-------------|
| `create_artwork` | Create through pipeline with L1-L5 scores + suggestions |
| `evaluate_artwork` | Evaluate on L1-L5 with rationale + deviation analysis |
| `studio_create_brief` | Start a Brief-driven Studio session |
| `studio_update_brief` | Update Brief with natural language |
| `list_traditions` | List 13+ traditions with weights |
| `get_tradition_guide` | Full cultural context: terminology, taboos |

## Custom Traditions

```bash
vulca tradition --init pixel_art_retro > pixel_art_retro.yaml
vulca evaluate game.png -t ./pixel_art_retro.yaml
```

## Tests

```bash
pip install vulca[dev]
pytest tests/ -v  # 462 tests, 0 failures
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
