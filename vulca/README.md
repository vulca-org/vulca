# VULCA SDK

AI-native creation organism. Create, critique, and evolve cultural art.

## Install

```bash
pip install -e vulca/   # From repo root
```

## Quick Start

```python
import vulca

# Evaluate an artwork (mock mode — no API key needed)
result = vulca.evaluate("painting.jpg", tradition="chinese_xieyi", mock=True)
print(result.scores)         # {"L1": 0.85, "L2": 0.78, ...}
print(result.weighted_total) # 0.82

# Create through the full pipeline
result = vulca.create("Misty mountains in ink wash", provider="mock")
print(result.status)         # "completed"

# Human-in-the-loop with custom weights
result = vulca.create(
    "水墨山水",
    provider="mock",
    hitl=True,
    weights={"L1": 0.3, "L2": 0.2, "L3": 0.2, "L4": 0.15, "L5": 0.15},
)
# result.status == "waiting_human"
```

## CLI

```bash
vulca evaluate painting.jpg --tradition watercolor
vulca create "Garden scene" --provider mock
vulca create "水墨山水" --hitl --weights "L1=0.3,L2=0.2,L3=0.2,L4=0.15,L5=0.15"
vulca traditions  # List all 9 cultural traditions
```

## MCP Server

For AI agents (Claude Code, OpenClaw, etc.):

```bash
vulca-mcp  # Exposes 3 tools: create_artwork, evaluate_artwork, list_traditions
```

## Architecture

```
vulca/src/vulca/
├── pipeline/     # Execution engine + 3 built-in nodes + 3 templates
├── cultural/     # 9 YAML tradition configs with L1-L5 weights
├── scoring/      # VLM model routing + L1-L5 evaluation types
├── storage/      # Session/Feedback protocol + JSONL backend
├── intent/       # Natural language → tradition resolution
├── media/        # MediaType enum + creation recipe types
├── _vlm.py       # Gemini Vision L1-L5 scoring (core)
├── _engine.py    # Evaluation engine singleton
├── cli.py        # CLI entry point
└── mcp.py        # MCP server entry point
```

## Cultural Traditions

9 traditions with YAML-defined weights, terminology, and taboos:

| Tradition | L1 | L2 | L3 | L4 | L5 |
|-----------|----|----|----|----|-----|
| Chinese Xieyi | 0.10 | 0.15 | 0.25 | 0.20 | 0.30 |
| Chinese Gongbi | 0.15 | 0.30 | 0.25 | 0.15 | 0.15 |
| Japanese Traditional | 0.15 | 0.20 | 0.20 | 0.20 | 0.25 |
| Western Academic | 0.20 | 0.25 | 0.15 | 0.25 | 0.15 |
| Islamic Geometric | 0.25 | 0.30 | 0.20 | 0.15 | 0.10 |
| Watercolor | 0.20 | 0.25 | 0.15 | 0.20 | 0.20 |
| African Traditional | 0.15 | 0.20 | 0.30 | 0.20 | 0.15 |
| South Asian | 0.15 | 0.20 | 0.25 | 0.15 | 0.25 |
| Default | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 |

Weights evolve automatically through the self-evolution system.

## Self-Evolution

The system learns from every evaluation session:

1. **ContextEvolver** adjusts L1-L5 weights per tradition based on scoring patterns
2. **FewShotUpdater** selects high-scoring examples (≥0.75) as reference benchmarks
3. **VLM prompt** receives evolved weights, few-shot calibration, and tradition insights
4. `get_weights()` returns evolved weights when available, falling back to YAML defaults

## Tests

```bash
cd vulca && .venv/bin/python -m pytest tests/ -v  # 218 tests
```

## License

Apache 2.0
