# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Owner Information

**Owner**: 于浩睿 (Yu Haorui)
**Username**: yhryzy
**Email**: yuhaorui48@gmail.com

### Related Research (First Author)

| Paper | Status | Core Contribution |
|-------|--------|-------------------|
| **VULCA Framework** | EMNLP 2025 Findings | 5-dimension evaluation framework |
| **VULCA-Bench** | arXiv:2601.07986 | L1-L5 five-level definitions + 7,410 samples |
| **Fire Imagery** | WiNLP 2025 | Cultural symbol reasoning |
| **Art Critique** | arXiv:2601.07984 | Cross-cultural critique evaluation |

## Live Project Status (auto-updated)

<!-- AUTO-STATUS-START -->
- **Branch**: master | Last commit: a994d0b feat(cli): GREEN — add --residuals and --sparse-eval flags to CLI (5 tests pass)
- **Active Phase**: Phase D1 — Pipeline 可见性修复 — rationale/evolution/instruct/cultural injection
- **Evolution**: 9 traditions evolved (last: 2026-03-24)
- **Sessions logged**: 510
- **Config**: 7 agents / 8 skills / 6 rules
- **Auto-updated**: 2026-03-26 22:51
<!-- AUTO-STATUS-END -->

## Project Overview

VULCA — AI-native creation organism. Create, critique, and evolve cultural art through multi-agent AI pipelines. The core product is **Canvas** (unified creation + evaluation), not the leaderboard. Features React 19 frontend with **Digital Curator** design system (v2.0, 2026-03-19), FastAPI backend with async pipeline (Scout→Draft→Critic→Queen), and production GCP deployment.

**Production URLs:**
- Frontend: https://vulcaart.art (Firebase Hosting)
- Backend API: Cloud Run (asia-east1)
- Database: Supabase PostgreSQL (free tier)

## VULCA Unified Package (vulca/)

The `vulca/` directory is the unified Python SDK (v0.7.0, 538 tests).
This replaces the old `app/vulca/` backend module and consolidates logic from `vulca-pkg`.

### Quick Start
```python
import vulca
result = vulca.evaluate("artwork.png", tradition="chinese_xieyi")
print(result.suggestions)    # per-dimension actionable advice
print(result.deviation_types) # traditional / intentional_departure / experimental

# Reference mode (advisor, not judge)
result = vulca.evaluate("artwork.png", tradition="chinese_xieyi", mode="reference")

# Create with eval_mode
result = vulca.create("水墨山水", provider="mock", eval_mode="reference")
```

### Package Structure
```
vulca/src/vulca/
├── pipeline/     # Execution engine + 3 built-in nodes + 3 templates
├── cultural/     # 13 YAML tradition configs with L1-L5 weights
├── providers/    # Pluggable ImageProvider + VLMProvider protocols
├── scoring/      # VLM model routing + L1-L5 evaluation types
├── storage/      # Session/Feedback protocol + JSONL backend
├── intent/       # Natural language → tradition resolution
├── media/        # MediaType enum + creation recipe types
├── _vlm.py       # Gemini Vision L1-L5 scoring + suggestions + deviation analysis
├── _engine.py    # Evaluation engine singleton
├── cli.py        # vulca evaluate/create/traditions (--mode strict|reference|fusion)
└── mcp_server.py # MCP server (6 tools, FastMCP)
```

### Testing
```bash
cd vulca && .venv/bin/python -m pytest tests/ -v  # 276 tests
```

## Essential Commands

### Quick Start
```bash
# Windows: start.bat | Linux/macOS: ./start.sh
# Starts backend (:8001) + frontend (:5173) + initializes DB
```

### Frontend (wenxin-moyun/)
```bash
npm install --legacy-peer-deps  # React 19 compatibility
npm run dev                     # Dev server :5173
npm run build                   # Production build
npm run lint                    # ESLint validation
npm run type-check              # TypeScript validation only

# Vite Cache Issues
npm run dev:clean       # Clear cache and start dev server
npm run dev:fresh       # Complete cache reset and start
npm run cache:clear     # Clear all caches (manual)

# Playwright E2E Testing (95 tests, 17 spec files)
npm run test:e2e               # Run all tests headless
npm run test:e2e:ui            # Interactive test UI
npm run test:e2e:debug         # Debug mode step-by-step
npm run test:e2e:headed        # Run in visible browser
npm run test:e2e:report        # Show HTML test report
npm run test:e2e -- --grep="auth"  # Run specific test pattern
```

### Backend (wenxin-backend/)
```bash
pip install -r requirements.txt -c constraints.txt  # ALWAYS use constraints
python -m uvicorn app.main:app --reload --port 8001
python init_db.py              # Reset DB with 42 models
pytest tests/ -v               # Run all tests verbose
pytest tests/test_auth.py -v   # Run specific test
pytest --cov=app tests/        # Test coverage report
```

### AI Model Testing
```bash
cd wenxin-backend
python test_qwen_complete.py --priority  # Test 6 priority Qwen models
python test_anthropic_final.py          # Test Claude models
python merge_all_results_v2.py          # Merge all test results
```

## Architecture Patterns

### Frontend Architecture

#### Component Structure
```
src/
├── components/
│   ├── ios/              # Complete iOS design system
│   │   ├── core/         # IOSButton, IOSCard, IOSToggle, IOSSlider, IOSAlert
│   │   └── emoji/        # EmojiIcon, StatusEmoji, RankEmoji, TypeEmoji
│   ├── vulca/            # VULCA evaluation components
│   │   ├── VULCAVisualization.tsx
│   │   ├── DimensionToggle.tsx
│   │   └── CulturalPerspectiveSelector.tsx
│   └── common/           # Shared components
├── pages/                # Route-level pages
├── hooks/                # Custom hooks including vulca/useVULCAData
├── utils/                # Utilities including vulca/api.ts
└── types/                # TypeScript definitions
```

#### State Management
- **Zustand**: For global UI state and preferences
- **Custom Hooks**: Business logic abstraction (useVULCAData, useAuth, etc.)
- **React State**: Component-level state management

#### 3D Visualization (VULCA Page)
- **React Three Fiber**: 3D rendering with @react-three/fiber + @react-three/drei
- **Three.js**: WebGL-based 3D graphics for interactive background
- Key file: `src/components/vulca/VULCAVisualization.tsx`

### Backend Architecture

#### OAuth2 Authentication
```
POST /auth/register   — Create new user (JSON body)
POST /auth/login      — OAuth2 token (form-urlencoded)
GET  /auth/me         — Current user profile (Bearer token)
```
```typescript
// Login must use form-urlencoded, NOT JSON
const formParams = new URLSearchParams();
formParams.append('username', username);
formParams.append('password', password);
```

#### Unified Model Interface
```python
# Different models require different parameters
'gpt-5': max_completion_tokens=500  # NOT max_tokens
'o1': # No system messages, no temperature
'deepseek-chat': # Use for R1/R1-distill/V3, NOT deepseek-reasoner
'claude-opus-4-1-20250805': # No temperature AND top_p together
```

#### VULCA Integration
```python
# Unified VULCA package (vulca/)
from vulca import evaluate, create, session  # Public API
# Pipeline engine
from vulca.pipeline import execute, DEFAULT, FAST
# SDK: HITL + custom weights
result = create("水墨山水", provider="mock", hitl=True, weights={"L1": 0.3, "L2": 0.2})
# result.status == "waiting_human", result.interrupted_at == "decide"
```
```bash
# CLI: HITL + custom weights
vulca evaluate image.png --tradition chinese_xieyi
vulca create "水墨山水" --provider mock
vulca create "水墨山水" --hitl --weights "L1=0.3,L2=0.2,L3=0.2,L4=0.15,L5=0.15"
```
```python
# MCP: create_artwork(intent, hitl=True, weights="L1=0.3,L2=0.2,...")
```
Note: The old `app/vulca/` backend module has been deleted. All VULCA logic now lives in the unified `vulca/` package.

**HITL / Weights / Evolution across all 4 entry points:**
| Feature | Canvas UI | CLI | SDK | MCP |
|---------|-----------|-----|-----|-----|
| HITL | `enable_hitl` in CreateRunRequest | `--hitl` flag | `hitl=True` | `hitl=True` |
| Custom weights | Canvas weight sliders → `node_params` | `--weights "L1=0.3,..."` | `weights={"L1": 0.3}` | `weights="L1=0.3,..."` |
| Evolution | Auto (throttled, lightweight fallback) | Auto via on_complete | Auto via on_complete | Not yet |

## Design System — "The Digital Curator" (v2.1, 2026-03-19)

以设计稿 HTML 为准（非 Ethos）。Reference: `stitch (2).zip` design files.

**Core colors**: Primary Blue `#005ab4` | Bronze `#C87F4A` | Sage Green `#5F8A50` | Amber Gold `#B8923D` | Coral Red `#C65D4D`

**Background**: Light `#f9f9ff` (Cool White) | Dark `#0F0D0B` (Warm Black)

**Surface layering**: `#f9f9ff` (base) → `#f2f3fd` (sections) → `#ffffff` (cards)

**Typography**: Noto Serif (headlines ≥24px) + Inter (body/UI)

**Radius**: 16px cards | 24px buttons | 48px hero containers

**Components**: IOSButton, IOSCard, IOSToggle, IOSSlider, IOSAlert, IOSSheet, IOSSegmentedControl

**Canvas (Single Interface, No Tabs)**:
- 三栏布局 — AI Collective (w-80) | Artwork HUD (~70%) + Log (~18%) + Chat (~12%) | L1-L5 + Tags + Finalize
- 空闲态：中央放意图输入框 + 配置面板
- 运行态：全出血艺术品大图 + Glass HUD + 分析热点 + Intelligence Log
- 完成态：Finalize Artifact + Feedback + Confidence/Cost
- 底部聊天栏："Instruct the Collective..." + 📎🖼️📊🔗 工具
- Pipeline Editor：左侧 ⚙️ 按钮 → 全屏 Modal（ReactFlow）
- `POST /runs/{task_id}/instruct`：追加指令 API
- HITL 决策：右侧面板 Accept/Refine/Reject + L1-L5 维度锁定
- 多轮候选图：中央显示每轮 4 张候选，用户可点选
- 图片评估：🖼️ 按钮 → POST /create + image_base64
- 权重控制：L1-L5 滑块调节评分权重

**Gallery**: 画廊精选风格
- 竖版大图 3 列，aspect-4/5，rounded-3xl
- 卡片只显示：标题 + 传统 badge（右上）
- 点击卡片 → Modal 详情（大图 + L1-L5 分数 + rationale + log）
- 筛选用 pill 按钮组

**Landing Page**:
- Hero 有流动抽象艺术背景图 + 浮动 glass 终端预览
- Agent Pipeline 有 glass 容器和连接线

**Rules**:
- **No-Line Rule**: No 1px borders — use tonal shifts and negative space
- Demo mode 提示改为右下角 toast，不占 Header 空间
- All interactive elements must meet 44px minimum touch target
- Guard API data with null checks before `Object.entries/keys/values`
- Ambient shadows `rgba(28,28,25,0.06)`
- Serif font (Noto Serif) for text ≥24px, Inter for everything else

## Code Quality & Auditing

When auditing or fixing files, always scope searches to active/current files only — exclude archived, deprecated, or backup directories to avoid false positives.

## Workflow Rules

After any migration or multi-file refactoring, always run a final audit pass for dead code, stale references, and untracked files before considering the task complete.

## Critical Development Patterns

### VULCA 47D Dimension Names Issue
When working with VULCA dimension names in visualization:
- Dimensions come in various formats: snake_case (creative_synthesis), camelCase (CreativeSynthesis), or with spaces (Creative Synthesis)
- The VULCAVisualization component requires special handling:
  ```typescript
  // Helper function to convert camelCase to spaced format
  const camelCaseToWords = (text: string): string => {
    return text.replace(/([a-z])([A-Z])/g, '$1 $2')
             .replace(/^[a-z]/, c => c.toUpperCase());
  };
  ```
- Key files: `src/components/vulca/VULCAVisualization.tsx`, `src/utils/vulca-dimensions.ts`

### Vite Module Export Errors
When encountering "The requested module does not provide an export named 'XXX'":
1. First try: `npm run dev:clean`
2. If persists: `npm run dev:fresh`
3. Last resort: Clear caches manually and restart

### TypeScript Module Resolution
When Vite module errors occur, define types locally as temporary workaround:
```typescript
// Temporary fix: define types locally
interface VULCAScore6D {
  creativity: number;
  technique: number;
  emotion: number;
  context: number;
  innovation: number;
  impact: number;
}
```

### NULL Score Handling
```typescript
// Image models have intentional NULL scores
{score != null ? score.toFixed(1) : 'N/A'}
```

## Git / Deployment

Before deploying or committing, verify all new/modified files are git-tracked (`git status`). This is a recurring issue with untracked component files breaking deploys.

## Common Deployment Issues

### Port Binding
- Check `${PORT:-8080}` environment variable
- Bind to `0.0.0.0` not localhost

### Database Migrations
```bash
alembic upgrade head  # NOT alembic stamp
# Run via Cloud Run Jobs, not inline
```

### Package Versions
Always use constraints.txt for Python dependencies

### Missing Columns
Run proper alembic upgrade, not manual schema changes

## Test Accounts
- Demo: `demo` / `demo123`
- Admin: `admin` / `admin123`

## GCP Configuration
- Region: `asia-east1`
- Services: Cloud Run, Firebase Hosting, Secret Manager
- Database: Supabase PostgreSQL
- Domain: vulcaart.art (Firebase Hosting custom domain)
- Note: GCP Project IDs and service URLs are managed via GitHub Secrets and environment variables, not hardcoded.

## Critical Dependency Issues

### bcrypt Version Compatibility
```python
# requirements.txt - MUST use bcrypt 4.0.x
bcrypt==4.0.1  # 4.1+ breaks passlib compatibility
```
The passlib library is incompatible with bcrypt 4.1+. Always pin to 4.0.x.

### BrowserRouter
The frontend uses BrowserRouter (React Router DOM). Firebase Hosting has rewrite rules for SPA routing.

## Database Initialization

The `init_db.py` script creates both admin and demo users:
```bash
cd wenxin-backend
python init_db.py  # Creates admin/admin123 and demo/demo123
```

For production (Supabase), the CI/CD pipeline runs this automatically via GitHub Actions.

## Deployment Pipeline

### GitHub Actions Workflow (.github/workflows/deploy-gcp.yml)
1. **Test Phase**: Frontend build, backend tests (~920, 51 files), Playwright E2E (95 tests, 17 specs)
2. **Database Init**: Runs `init_db.py` against Supabase
3. **Backend Deploy**: Docker build → Artifact Registry → Cloud Run
4. **Frontend Deploy**: Vite build → Firebase Hosting

## Environment

When working with Python in this project, always use the virtualenv Python (not system Python). Check which python/pip is active before installing packages.

## Architecture Status (2026-03-18, Phase F1 complete)

**ONE PIPELINE + EVOLUTION LOOP achieved**: All API routes use `vulca.pipeline.execute()`. The self-evolution feedback loop is fully closed — evolved weights, few-shot examples, and tradition insights are injected into VLM scoring prompts.

### 6 Systemic Break Chains — Resolution Status

1. ~~**Canvas topology never executes**~~ — **MITIGATED**: Graph code deleted, NodeSearchPopup hides unsupported nodes. Custom topologies not supported (by design: Apple principle).
2. ~~**Sub-stages are dead path**~~ — **FIXED**: `sub_stage_executor.py` deleted, `enable_sub_stages` disabled.
3. ~~**Explicit feedback dead end**~~ — **FIXED (9D)**: `FeedbackStore.sync_from_sessions()` reads from SessionStore (DB).
4. ~~**Production JSONL blindspot**~~ — **FIXED (9D)**: `FewShotUpdater._load_sessions()` reads from SessionStore (DB).
5. ~~**LangGraph vs Legacy dual-track**~~ — **FIXED**: Both `graph/` and `orchestrator.py` deleted. Only `vulca/` engine.
6. ~~**47D expansion is random noise**~~ — **FIXED**: `app/vulca/` deleted. Replaced by `vulca/_vlm.py`.

### SDK/CLI/MCP Architecture

```
┌─────────────────────────────────────┐
│  MCP Server / ComfyUI Nodes        │  ← Pending (independent task)
├─────────────────────────────────────┤
│  CLI  (vulca create / evaluate)     │  ← Working (vulca/cli.py)
├─────────────────────────────────────┤
│  Python SDK  (from vulca import *)  │  ← Working (vulca/ package)
├─────────────────────────────────────┤
│  Canvas UI → FastAPI → execute()    │  ← Working (Phase 9B)
└─────────────────────────────────────┘
```
All entry points share ONE engine: `vulca.pipeline.execute()`.

## VULCA Prototype Architecture (post Phase 9)

### Directory Structure
```
wenxin-backend/app/prototype/
├── agents/              # Draft providers (NB2/Mock) — reference code
├── api/                 # REST endpoints → call vulca.pipeline.execute()
├── cultural_pipelines/  # Cultural weights, YAML tradition configs
├── digestion/           # ContextEvolver, PatternDetector, FewShotUpdater
├── feedback/            # FeedbackStore (reads from SessionStore DB)
├── intent/              # IntentAgent, MetaOrchestrator
├── observability/       # LangfuseObserver
├── orchestrator/        # Events + RunState types only (orchestrator.py deleted)
├── pipeline/            # Pipeline types + fallback chain
├── session/             # SessionStore (Supabase DB in prod, JSONL in dev)
├── skills/              # Skill API routes + executors
├── tools/               # Scout service, terminology loader
└── data/                # YAML traditions
```
**Deleted**: `orchestrator.py`, `agent_factory.py`, `critic_agent/llm/rules.py`, `queen_agent/llm.py`, `vlm_critic.py`, `graph/`, `trajectory/`, `ui/`, `community/`, `integrations/`, `blind_eval/`, `app/vulca/`.

### Prototype Dependencies
```bash
pip install -r requirements.prototype.txt  # On top of requirements.render.txt
```

Key packages: litellm, pydantic, pyyaml, faiss-cpu

## Node Editor (Canvas)

Visual pipeline editor. NodeSearchPopup shows only 8 backend-connected nodes (agent nodes + utility). Topology validation runs locally (no remote API dependency).

Canvas purpose: transparent pipeline visualization + evolution feedback interface. Not a general-purpose node editor.

## Digestion System (✅ connected, Phase F1)

Self-evolution pipeline fully connected:
- **ContextEvolver**: Adjusts L1-L5 weights per tradition (e.g., xieyi L1: 0.10→0.35) every 5 minutes
- **FewShotUpdater**: Selects high-scoring examples (≥0.75) as calibration references (15 examples)
- **PreferenceLearner**: Consumes explicit feedback from FeedbackStore (1176 entries)
- **VLM prompt**: Receives evolved weights, few-shot benchmarks, and tradition insights
- **get_weights()**: Returns evolved weights from evolved_context.json, falling back to YAML
- **Feedback**: POST /feedback → feedback.jsonl → PreferenceLearner → weight adjustments

## Academic Paper Workflow

For academic paper edits: always verify terminology/naming against the user's most recent instructions before making global changes. Do not assume prior names are correct — ask if ambiguous (e.g., CPD vs CPSR vs CPC).