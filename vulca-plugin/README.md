# VULCA Claude Code Plugin

AI-native cultural art creation organism for Claude Code. Selective Pipeline, Brief-driven Studio, L1-L5 evaluation with actionable suggestions, Digestion V2 learning system, and 13 cultural traditions.

## Install

```bash
pip install vulca[mcp]
claude plugin install vulca-org/vulca-plugin
```

**For real VLM scoring + image generation** (optional):
```bash
export GOOGLE_API_KEY=your-key-here
```

Mock mode works without any API key.

### MCP Tools (11 tools)

| Tool | Description |
|------|-------------|
| `evaluate_artwork` | L1-L5 cultural evaluation |
| `create_artwork` | Generate culturally-guided artwork |
| `list_traditions` | List 13 cultural traditions |
| `get_tradition_guide` | Detailed tradition reference |
| `resume_artwork` | Resume HITL paused sessions |
| `get_evolution_status` | Check weight evolution |
| **`studio_create_brief`** | Create Brief from creative intent |
| **`studio_update_brief`** | NL update Brief |
| **`studio_generate_concepts`** | Generate concept designs |
| **`studio_select_concept`** | Select + refine concept |
| **`studio_accept`** | Finalize session + digest |

### Skills (4 skills)

| Skill | Trigger | Description |
|-------|---------|-------------|
| evaluate | "evaluate this painting" | Quick L1-L5 evaluation |
| create | "create artwork" | Cultural artwork generation |
| tradition | "show me xieyi guide" | Tradition reference lookup |
| **studio** | "start a studio session" | Brief-driven creative collaboration |

### Agents (1 agent)

| Agent | Description |
|-------|-------------|
| cultural-critic | Deep cross-cultural analysis |

## Studio Pipeline (v0.7.0)

```
Intent → Concept → Generate → Evaluate → Refine
  ↑                                        ↓
  └──── Brief (living creative document) ←─┘
```

- **LLM intent parsing**: Gemini extracts implicit elements, palette, composition
- **Dynamic questions**: Domain-adaptive clarifying questions
- **Natural language updates**: "Put the teapot in the lower center"
- **Digestion V2**: Learns from your preferences across sessions

### Evaluation Modes

- **strict** (default): Judge mode — scores reflect conformance
- **reference**: Advisor mode — shows alignment without judgment
- **fusion**: Compare against multiple traditions at once

## Requirements

- Python 3.10+
- `pip install vulca` (v0.7.0+)
- Gemini API key (for real VLM evaluation)

## License

Apache-2.0

## Links

- SDK: [PyPI](https://pypi.org/project/vulca/) (v0.7.0, 538 tests)
- Paper: [VULCA Framework](https://aclanthology.org/2025.findings-emnlp/) (EMNLP 2025)
