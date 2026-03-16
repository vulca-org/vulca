# Contributing to VULCA

Thank you for your interest in contributing to VULCA! This guide covers development setup, contribution workflows, and extension points.

## Development Setup

```bash
# 1. Clone and enter the project
git clone https://github.com/vulca-org/vulca.git vulca
cd vulca

# 2. Backend setup
cd wenxin-backend
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt -c constraints.txt
python init_db.py
python -m uvicorn app.main:app --reload --port 8001

# 3. Frontend setup (separate terminal)
cd wenxin-moyun
npm install --legacy-peer-deps
npm run dev

# 4. Verify
# Frontend: http://localhost:5173
# Backend: http://localhost:8001/health
# Login: demo / demo123
```

## PR Process

1. **Branch naming**: `feat/<description>`, `fix/<description>`, `docs/<description>`
2. **Commit messages**: Use conventional format — `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
3. **Before submitting**:
   - Backend: `cd wenxin-backend && python -m pytest tests/ -x -q`
   - Frontend: `cd wenxin-moyun && npx tsc --noEmit && npm run build`
4. **PR description**: Include what changed, why, and how to test
5. **Review**: Maintainer will review within 48 hours

## Security Guidelines

- **Never** commit `.env` files, API keys, or credentials
- Use `.env.example` files with placeholder values for new environment variables
- Store secrets in GitHub Secrets or your cloud provider's secret manager
- If you discover a security issue, see [SECURITY.md](SECURITY.md)

## Code Conventions

### Backend (Python)

- Use `from __future__ import annotations` in all new files
- Wrap optional imports in `try/except ImportError`
- Use `logger.debug()` for non-critical logs, `logger.warning()` for important ones
- Pin dependency versions with `==` in `requirements.txt`
- Run `python -m pytest tests/ -x -q` before submitting

### Frontend (TypeScript/React)

- Art Professional palette only (warm gallery tones — no blue/purple/indigo)
- Tailwind CSS with `dark:` prefix for dark mode support
- Guard all API-fetched data with null checks before `Object.entries/keys/values`
- Use `memo()` on components, `useCallback` on handlers
- Use `react-hot-toast` for user notifications

## Adding New Agent Types

```python
# wenxin-backend/app/prototype/agents/interfaces.py
from app.prototype.agents.interfaces import BaseAgent, AgentRegistry

@AgentRegistry.register("my_agent")
class MyAgent(BaseAgent):
    name = "my_agent"
    def execute(self, state) -> dict:
        return {"my_result": ...}
```

Register the agent, add a port contract in `pipeline/port_contract.py`, and create a node component in `wenxin-moyun/src/components/prototype/editor/nodes/`.

## Adding New Skills

```python
# wenxin-backend/app/prototype/skills/executors/
from app.prototype.skills.executors.base import BaseSkillExecutor

class MySkillExecutor(BaseSkillExecutor):
    SKILL_NAME = "my_skill"
    async def execute(self, image_path, context) -> SkillResult:
        return SkillResult(skill_name="my_skill", score=0.85, details={})
```

Skills auto-register via the executor base class and appear in the Skill Browser panel.

## Adding New Traditions

This is the most impactful way to contribute. VULCA evaluates AI-generated art across cultural dimensions using `TRADITION.yaml` files.

## Adding a New Tradition

VULCA evaluates AI-generated art across cultural dimensions using `TRADITION.yaml` files. Each tradition defines evaluation weights, terminology, and cultural taboos.

### Quick Start (5 minutes)

1. **Fork** this repository
2. **Copy** the template:
   ```bash
   cp wenxin-backend/app/prototype/data/traditions/_template.yaml \
      wenxin-backend/app/prototype/data/traditions/your_tradition.yaml
   ```
3. **Edit** the YAML file with your tradition's data
4. **Validate** locally:
   ```bash
   cd wenxin-backend
   python -c "
   from app.prototype.cultural_pipelines.tradition_loader import validate_tradition_yaml
   errors = validate_tradition_yaml('app/prototype/data/traditions/your_tradition.yaml')
   print('PASS' if not errors else errors)
   "
   ```
5. **Submit** a Pull Request

### TRADITION.yaml Structure

```yaml
name: korean_minhwa              # snake_case unique ID
display_name:
  en: "Korean Folk Painting"     # required
  zh: "韩国民画"                  # optional
  ja: "韓国民画"                  # optional

weights:                          # must sum to 1.0
  L1: 0.15                       # Visual Perception
  L2: 0.20                       # Technical Analysis
  L3: 0.25                       # Cultural Context
  L4: 0.15                       # Critical Interpretation
  L5: 0.25                       # Philosophical Aesthetic

terminology:                      # minimum 3 entries
  - term: "chaesaek"
    term_zh: "五方色"
    definition:
      en: "The five-color system (blue, white, red, black, yellow) based on yin-yang cosmology."
    category: technique           # technique|aesthetics|composition|philosophy|material
    l_levels: [L2, L3]
    aliases: ["five cardinal colors"]
    source: "Korean painting tradition"

taboos:                           # minimum 1 entry
  - rule: "Do not apply Japanese ukiyo-e standards to Korean minhwa"
    severity: high                # low|medium|high|critical
    l_levels: [L3, L4]
    explanation: "Korean folk painting has distinct aesthetic values from Japanese woodblock prints."

pipeline:
  variant: default                # default|chinese_xieyi|western_academic
```

### L1-L5 Weight Guidelines

Choose weights that reflect your tradition's evaluative priorities:

| Dimension | What it measures | High weight when... |
|-----------|-----------------|---------------------|
| **L1** Visual Perception | Color, form, spatial layout | Visual precision is paramount (e.g., geometric art) |
| **L2** Technical Analysis | Medium mastery, brushwork, craft | Technical virtuosity defines quality (e.g., gongbi) |
| **L3** Cultural Context | Tradition-specific knowledge, symbolism | Cultural meaning is central (e.g., African traditional) |
| **L4** Critical Interpretation | Meaning-making, narrative | Interpretive depth matters (e.g., Western academic) |
| **L5** Philosophical Aesthetic | Worldview, beauty concept | Philosophical dimension is key (e.g., Chinese xieyi) |

Weights must sum to **1.0**. The CI will reject PRs where they don't.

### Quality Checklist

Before submitting your PR, verify:

- [ ] `name` is unique snake_case (check existing files in `traditions/`)
- [ ] `weights` L1-L5 sum to exactly 1.0
- [ ] At least 3 terminology entries with `term`, `definition`, and `l_levels`
- [ ] At least 1 taboo rule with `rule` and `severity`
- [ ] `definition` is accurate and sourced (cite references where possible)
- [ ] No duplicate terms across existing traditions (check with search)
- [ ] Taboo rules are specific, not generic platitudes

### What Makes a Good Contribution

**Excellent traditions include:**
- Terms with authoritative sources (academic texts, historical documents)
- Taboos that catch real evaluation mistakes AI systems make
- Weights that reflect genuine evaluative priorities of practitioners
- Multi-language display names (en + at least one other language)

**We will request changes if:**
- Definitions are vague or unsourced
- Taboos are too generic ("don't be insensitive")
- Weights seem arbitrary (explain your reasoning in the PR description)
- Content duplicates an existing tradition

## Other Contributions

### Bug Reports
Open an issue with reproduction steps and expected vs actual behavior.

### Code Contributions
For code changes beyond tradition YAML:
1. Open an issue describing the proposed change
2. Wait for maintainer feedback before implementing
3. Follow existing code style and patterns
4. Include tests for new functionality

### Translation
Help translate `display_name` and `definition` fields in existing traditions to more languages.

## Code of Conduct

Be respectful of all cultural traditions. VULCA exists to celebrate cultural diversity in art, not to rank cultures against each other. Contributions that demean, stereotype, or misrepresent any culture will be rejected.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
