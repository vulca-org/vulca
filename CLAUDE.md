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

## Project Overview

VULCA — AI-native creation organism. Create, critique, and evolve cultural art through multi-agent AI pipelines. The core product is **Canvas** (unified creation + evaluation), not the leaderboard. Features React 19 frontend with Art Professional design system, FastAPI backend with async pipeline (Scout→Draft→Critic→Queen), and production GCP deployment.

**Production URLs:**
- Frontend: https://vulcaart.art (Firebase Hosting)
- Backend API: Cloud Run (asia-east1)
- Database: Supabase PostgreSQL (free tier)

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
# Backend modules
app/vulca/core/vulca_core_adapter.py  # 6D→47D expansion algorithm
app/vulca/services/vulca_service.py   # Async business logic
app/vulca/models/                     # SQLAlchemy models
app/vulca/schemas/                    # Pydantic schemas
app/vulca/vulca.py                    # FastAPI endpoints (8 routes)
```

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
1. **Test Phase**: Frontend build, backend tests (1076+, 60 files), Playwright E2E (95 tests, 17 specs)
2. **Database Init**: Runs `init_db.py` against Supabase
3. **Backend Deploy**: Docker build → Artifact Registry → Cloud Run
4. **Frontend Deploy**: Vite build → Firebase Hosting

## Environment

When working with Python in this project, always use the virtualenv Python (not system Python). Check which python/pip is active before installing packages.

## VULCA Prototype Architecture

### Directory Structure
```
wenxin-backend/app/prototype/
├── agents/              # Scout, Draft, Critic, Queen + providers (8.3K lines)
├── api/                 # REST endpoints: create, evaluate, routes (1.9K lines)
├── cultural_pipelines/  # Cultural weights, YAML tradition loader, pipeline router
├── digestion/           # ContextEvolver, FeatureExtractor, Clusterer, Distiller
├── feedback/            # FeedbackStore + sync_from_sessions
├── intent/              # IntentAgent, SkillSelector, MetaOrchestrator
├── graph/               # GraphOrchestrator (LangGraph, PRODUCTION default since Phase 5D)
├── orchestrator/        # PipelineOrchestrator (legacy, deprecated)
├── pipeline/            # Pipeline types + fallback chain
├── session/             # SessionStore + SessionDigest (JSONL-backed)
├── skills/              # Skill marketplace, executors, discussion
├── tools/               # Scout service, terminology loader, FAISS index
├── ui/                  # Gradio demo UI
├── checkpoints/         # Runtime checkpoint management (data gitignored)
└── data/                # YAML traditions, sessions.jsonl, evolved_context.json
```

### Prototype Dependencies
```bash
pip install -r requirements.prototype.txt  # On top of requirements.render.txt
```

Key packages: litellm, pydantic, pyyaml, faiss-cpu

## Multimodal Architecture (New)

### Media Types
The system supports multiple media types through the `MediaType` enum:
- **Image** (active): Full pipeline support with sub-stages
- **Video** (coming soon): Keyframe → motion → style → interpolation → render
- **3D Model** (coming soon): Concept → mesh → texture → lighting → render
- **Sound** (coming soon): Mood → instruments → melody → arrangement → mix

### Sub-Stage System
Generation (Draft agent) supports fine-grained sub-stages via `CreationRecipe`:
```
CreateRequest → Scout → Router → Draft [sub-stages] → Critic → Queen
                                   ├─ mood_palette
                                   ├─ composition_sketch
                                   ├─ element_studies
                                   ├─ style_reference
                                   ├─ storyboard
                                   └─ final_render
```

Key files:
- `app/prototype/media/types.py` — Core type definitions
- `app/prototype/media/recipes.py` — Creation recipes per media type
- `app/prototype/media/sub_stage_executor.py` — Sub-stage runtime

Sub-stages are disabled by default (`enable_sub_stages=False`).

## Node Editor (Phase 5, 95% complete)

Visual pipeline editor with 30 nodeTypes, 21 DataType, and 6 editor hooks.

### Editor Architecture
```
wenxin-moyun/src/components/prototype/editor/
├── PipelineEditor.tsx        # Main editor canvas (ReactFlow)
├── nodes/                    # 30 custom node types
│   ├── AgentNodes (scout, draft, critic, queen)
│   ├── DataNodes (input, output, merge, filter)
│   ├── SkillNode             # Skill marketplace integration
│   ├── SubStageNode          # Sub-stage expansion
│   └── CustomNode            # User-defined nodes
├── edges/                    # TypedEdge with DataType colors
├── hooks/                    # useEditorState, useNodeSelection, etc.
├── panels/                   # Inspector, SkillBrowser, TemplateManager
└── utils/                    # Validation, topology extraction
```

### Key Features
- **Socket-based connections**: 21 DataType with color coding
- **15 keyboard shortcuts**: Ctrl+Z/Y undo/redo, Del delete, Ctrl+A select all
- **Inline preview**: Image/text preview in nodes
- **Sub-stage expansion**: Expand draft node to show mood_palette → final_render
- **Mute/Bypass**: Per-node mute (skip) and bypass (pass-through) runtime controls
- **Skill drag-and-drop**: Drag skills from browser, auto-connects to nearest node

## Digestion System (Phase 5, closed-loop verified)

Cultural emergence pipeline: sessions → patterns → weight evolution → agent insights.

### Pipeline
```
SessionStore → DigestAggregator → PatternDetector → PreferenceLearner
     ↓               ↓                  ↓                   ↓
  sessions      aggregated stats    patterns         user preferences
     └──────────────────────────┬──────────────────────────────┘
                                ↓
                         ContextEvolver
                         ├── Weight adjustment (±0.05 guardrail)
                         ├── LLM insights (agent_insights, tradition_insights)
                         ├── Queen strategy evolution
                         └── evolution_log.jsonl audit trail
```

### Verified Results
- 112 emerged cultures, 203+ evolutions
- 3 new cultural traditions emerged from 20 seed sessions
- Agent insights updated and injected into system prompts

## Upcoming: Phase 7D — Multimodal Activation

**STATUS: UPCOMING — not yet implemented**

### Video Minimal Loop
1. FFmpeg keyframe extraction → video composition (`final_compose` handler)
2. Frontend Video Player component (HTML5 `<video>` with poster frame)
3. MediaType selector UI activation in Canvas IntentBar

### 3D Model Handlers (deferred)
- Three.js / Babylon.js mesh viewer component
- Concept → mesh → texture → lighting → render pipeline
- GLB/GLTF export support

### Sound/Audio Handlers (deferred)
- Stable Audio API integration
- Mood → instruments → melody → arrangement → mix pipeline
- Waveform visualization component

### Mobile Canvas (deferred)
- ReactFlow tablet adaptation (touch gestures, pinch zoom)
- Responsive node sizes and connection handles
- Mobile-friendly NodeParamPanel drawer

## Academic Paper Workflow

For academic paper edits: always verify terminology/naming against the user's most recent instructions before making global changes. Do not assume prior names are correct — ask if ambiguous (e.g., CPD vs CPSR vs CPC).