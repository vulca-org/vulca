# VULCA — AI-Native Creation Organism

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/vulca-org/vulca/actions/workflows/deploy-gcp.yml/badge.svg)](https://github.com/vulca-org/vulca/actions)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-green.svg)](https://python.org)
[![Node 20](https://img.shields.io/badge/Node.js-20-green.svg)](https://nodejs.org)

> Create, critique, and evolve cultural art through multi-agent AI pipelines.

VULCA is an open-source creative platform where generation, evaluation, and learning are seamless stages of one process. The core product is **Canvas** -- a unified creation and evaluation playground powered by a multi-agent pipeline. Nine cultural traditions shape how art is generated and scored. The system **learns from every session** -- evolved weights, few-shot references, and cultural insights feed back into the evaluation prompt automatically. No API keys required to start -- the built-in mock provider runs the full pipeline locally.

**Live:** [vulcaart.art](https://vulcaart.art) | **Papers:** EMNLP 2025, WiNLP 2025, arXiv 2026

```
                          ┌─────────────────────────────────┐
  User Intent ──────────► │  Canvas Pipeline                │
                          │  Scout → Router → Draft          │
                          │    → Critic → Queen → Archivist  │
                          └──────────┬──────────────────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │  Gallery + Feedback   │
                          └──────────┬───────────┘
                                     │
                          ┌──────────▼───────────┐
                          │  Digestion System     │
                          │  (Cultural Emergence) │
                          └──────────┬───────────┘
                                     │
                                     ▼
                          Evolved Context → Pipeline
```


## Four Ways to Use VULCA

```python
# 1. Python SDK
import vulca
result = vulca.evaluate("artwork.png", tradition="chinese_xieyi")
result = vulca.create("水墨山水", provider="mock")
```

```bash
# 2. CLI
vulca evaluate painting.jpg --tradition watercolor
vulca create "Misty mountains" --provider mock --hitl
```

```bash
# 3. MCP Server (for AI agents like Claude Code)
vulca-mcp  # Exposes create_artwork, evaluate_artwork, list_traditions
```

```
# 4. Canvas Web UI (https://vulcaart.art)
Intent → Scout → Draft → Critic → Queen → Gallery → Evolve
```

## Directory Structure

> **Note**: `wenxin-moyun` (frontend) and `wenxin-backend` are the original Chinese names meaning "Heart of Ink and Cloud". They are preserved for backward compatibility.

```
├── vulca/                 # Unified Python SDK (218 tests)
│   └── src/vulca/         #   pipeline/, cultural/, scoring/, storage/, cli, mcp
├── wenxin-moyun/          # Frontend (React 19 + TypeScript)
├── wenxin-backend/        # Backend (FastAPI + Python 3.13)
├── docker-compose.yml     # One-command local setup
├── CONTRIBUTING.md        # How to contribute
└── SECURITY.md            # Vulnerability reporting
```

## Quick Start

```bash
git clone https://github.com/vulca-org/vulca.git vulca
cd vulca
docker-compose up
# Frontend: http://localhost:5173
# Backend API: http://localhost:8001
# Demo account: demo / demo123
```

### Manual Setup

```bash
# Backend
cd wenxin-backend
pip install -r requirements.txt -c constraints.txt
python init_db.py
python -m uvicorn app.main:app --reload --port 8001

# Frontend (separate terminal)
cd wenxin-moyun
npm install --legacy-peer-deps
npm run dev
```

**Test accounts:** `demo` / `demo123` or `admin` / `admin123`

## How It Works

The Canvas pipeline processes creative intent through 6 specialized agents:

```
Intent --> Scout --> Router --> Draft --> Critic --> Queen --> Archivist
            🔍        🚦        🎨        📊        👑         💾
```

| Agent | Role | Technology |
|-------|------|------------|
| Scout | Cultural evidence retrieval | Gemini 2.5 Flash |
| Router | Tradition routing (9 YAML traditions) | Rule-based + LLM |
| Draft | Image generation | Mock / NB2 / Diffusers / DALL-E / Flux |
| Critic | L1-L5 multi-dimensional scoring | Gemini 2.5 Flash (VLM) |
| Queen | Accept/rerun decision gate | Gemini 2.5 Flash |
| Archivist | Result archival + Gallery | PostgreSQL / JSONL |

### Self-Evolution (the closed loop)

Every session feeds back into the system:

1. **ContextEvolver** adjusts L1-L5 weights per tradition (e.g., xieyi L1: 0.10 → 0.35)
2. **FewShotUpdater** selects high-scoring examples as calibration references
3. **VLM prompt** receives evolved weights, few-shot benchmarks, and tradition insights
4. Next evaluation is shaped by all previous sessions -- the system gets culturally smarter

## Extend VULCA

### Add a Provider (like ComfyUI nodes)

```python
from app.prototype.agents.draft_provider import AbstractProvider

class MyProvider(AbstractProvider):
    @property
    def model_ref(self) -> str:
        return "my-model-v1"

    def generate(self, prompt, negative_prompt, seed, width, height, steps, sampler, output_path) -> str:
        # Your generation logic
        return output_path
```

### Add an Agent

```python
from app.prototype.agents.interfaces import BaseAgent, AgentRegistry

@AgentRegistry.register("my_agent")
class MyAgent(BaseAgent):
    name = "my_agent"
    def execute(self, state) -> dict:
        return {"my_result": ...}
```

### Add a Skill

```python
from app.prototype.skills.executors.base import BaseSkillExecutor

class MySkillExecutor(BaseSkillExecutor):
    SKILL_NAME = "my_skill"
    async def execute(self, image_path, context) -> SkillResult:
        return SkillResult(skill_name="my_skill", score=0.85, details={})
```

### Add a Cultural Tradition

```yaml
# vulca/src/vulca/cultural/data/traditions/my_tradition.yaml
name: my_tradition
display_name:
  en: My Tradition
  zh: 我的传统
weights:
  L1: 0.20
  L2: 0.20
  L3: 0.25
  L4: 0.20
  L5: 0.15
terminology:
  - term: key_concept
    term_zh: 核心概念
    definition: A foundational concept in this tradition
    l_levels: [L3, L5]
    category: aesthetics
taboos:
  - rule: Do not apply external standards
    severity: high
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript 5.8, Vite 7.1, Tailwind 4.1 |
| Design System | Art Professional (warm gallery palette, glass morphism) |
| Backend | FastAPI, Python 3.13, LiteLLM, asyncio |
| Database | PostgreSQL (Supabase) / SQLite (local) |
| AI Models | Gemini 2.5 Pro/Flash, NB2, FLUX.2 Pro, DALL-E 3, Diffusers, Mock |
| Deployment | GCP Cloud Run, Firebase Hosting, GitHub Actions |
| Testing | Playwright E2E (95 tests), pytest (218 vulca + backend tests) |

## API

Key endpoints:

```
POST /api/v1/auth/register             -- Register new user
POST /api/v1/auth/login                -- OAuth2 login
GET  /api/v1/auth/me                   -- Current user profile
POST /api/v1/prototype/runs            -- Start a pipeline run
GET  /api/v1/prototype/runs/{id}/events -- SSE event stream
GET  /api/v1/prototype/gallery          -- Browse creations
GET  /api/v1/prototype/traditions       -- List cultural traditions
GET  /api/v1/prototype/capabilities     -- Server capabilities
```

Full API docs: set `ENABLE_API_DOCS=true` and visit `/docs`.

## Production

| Service | URL |
|---------|-----|
| Frontend | https://vulcaart.art |
| Backend | Cloud Run (asia-east1) |
| Database | Supabase PostgreSQL |
| CI/CD | GitHub Actions (test --> deploy) |

## Testing

```bash
# VULCA SDK (218 tests)
cd vulca && .venv/bin/python -m pytest tests/ -v

# Backend
cd wenxin-backend && pytest tests/ -v

# Frontend type check + build
cd wenxin-moyun && npm run build

# E2E (95 tests, 17 spec files)
cd wenxin-moyun && npm run test:e2e
```

## Research

VULCA builds on peer-reviewed research:

- **VULCA Framework** -- EMNLP 2025 Findings (5-dimension evaluation)
- **VULCA-Bench** -- arXiv:2601.07986 (L1-L5 definitions, 7,410 samples)
- **Fire Imagery** -- WiNLP 2025 (cultural symbol reasoning)

## Security Notes

- **Never** commit `.env` files or API keys to the repository
- Use `.env.example` or `.env.production.local` for local overrides
- Rotate API keys regularly — see [SECURITY.md](SECURITY.md) for vulnerability reporting
- CI/CD secrets are managed via GitHub Secrets (not hardcoded in workflows)

## Extending VULCA

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup and PR process
- Adding new cultural traditions (YAML-based, 5-minute quickstart)
- Adding new agents, skills, and providers
- Code conventions and security guidelines

## Citation

```bibtex
@inproceedings{yu2025vulca,
  title={VULCA: A Framework for Culturally-Aware Visual Understanding},
  author={Yu, Haorui},
  booktitle={Findings of EMNLP 2025},
  year={2025}
}

@article{yu2026vulcabench,
  title={VULCA-Bench: A Benchmark for Culturally-Aware Visual Understanding at Five Levels},
  author={Yu, Haorui},
  journal={arXiv preprint arXiv:2601.07986},
  year={2026}
}
```

## License

Apache 2.0 -- see [LICENSE](LICENSE).
