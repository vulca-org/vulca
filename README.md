# VULCA — AI-Native Creation Organism

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/vulca-org/vulca/actions/workflows/deploy-gcp.yml/badge.svg)](https://github.com/vulca-org/vulca/actions)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-green.svg)](https://python.org)
[![Node 20](https://img.shields.io/badge/Node.js-20-green.svg)](https://nodejs.org)

> Create, critique, and evolve cultural art through multi-agent AI pipelines.

VULCA is an open-source creative platform where generation, evaluation, and learning are seamless stages of one process. The core product is **Canvas** -- a unified creation and evaluation playground powered by a 9-node multi-agent pipeline. Eight cultural traditions (Chinese Xieyi, Japanese Wabi-sabi, Persian Miniature, and more) shape how art is generated and scored. No API keys required to start -- the built-in mock provider runs the full pipeline locally.

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

<!-- TODO: Add screenshots -->

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

The Canvas pipeline processes creative intent through 9 specialized agents:

```
Intent --> Scout --> Router --> Draft --> Critic --> Queen --> Archivist
            🔍        🚦        🎨        📊        👑         💾
```

| Agent | Role | Technology |
|-------|------|------------|
| Scout | Cultural evidence retrieval | Gemini 2.5 Flash |
| Router | Tradition routing (8 YAML traditions) | Rule-based + LLM |
| Draft | Image generation | Mock / NB2 / Diffusers / DALL-E / Flux |
| Critic | L1-L5 multi-dimensional scoring | Gemini 2.5 Pro (VLM) |
| Queen | Accept/rerun decision gate | Gemini 2.5 Flash |
| Archivist | Result archival + Gallery | PostgreSQL / JSONL |

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
# wenxin-backend/app/prototype/data/traditions/my_tradition.yaml
name: my_tradition
display_name:
  en: My Tradition
  zh: 我的传统
weights_l:
  visual_perception: 0.20
  technical_analysis: 0.20
  cultural_context: 0.25
  critical_interpretation: 0.20
  philosophical_aesthetic: 0.15
terminology:
  - term: key_concept
    en: Key Concept
    weight: 0.8
taboos:
  - pattern: "inappropriate_element"
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
| Testing | Playwright E2E (132 tests), pytest (824 tests) |

## API

101+ endpoints. Key ones:

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
# Backend (824 tests)
cd wenxin-backend && pytest tests/ -v

# Frontend type check + build
cd wenxin-moyun && npm run build

# E2E (132 tests)
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
