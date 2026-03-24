# VULCA Architecture Overview

VULCA is not an image generator. It is a **creation organism** — a closed-loop system where generation, evaluation, cultural grounding, and learning are stages of one continuous process. The output is not just an image; it is an image with a score, a critique, a cultural lineage, and a contribution to the system's evolving understanding.

This document is for developers extending VULCA, and for anyone comparing it against tools that only do generation.

## What Makes VULCA Different

### VULCA vs Traditional AI Art Tools

| Capability | ComfyUI (+ App Mode) | Midjourney | DALL-E | VULCA |
|------------|----------------------|------------|--------|-------|
| Image Generation | Node graph / App Mode | Prompt | Prompt | Multi-agent pipeline |
| Custom Models | Any .safetensors | No | No | AbstractProvider + ProviderRegistry |
| Distributable Apps | App Builder (Mar 2026) | No | No | No (pipeline-as-a-unit) |
| Automated Critique | No | No | No | L1-L5 Critic (VLM-based) |
| Cultural Awareness | No | No | No | 13 YAML traditions + terminology + taboos + custom YAML |
| Quality Gate | No | No | No | Queen agent (accept/rerun/pause) |
| Evolution / Learning | No | No | No | ContextEvolver + MemRL insights |
| Evaluation Skills | No | No | No | 6 pluggable skill executors |
| Evidence Retrieval | No | No | No | Scout agent + FAISS index |
| Dynamic Weight Modulation | No | No | No | Confidence x round x signal-based |
| Full Provenance | No | No | No | Session → trajectory → gallery lineage |
| Open Source | GPL-3.0 | No | No | Apache 2.0 |

**The key difference**: ComfyUI (even with App Mode and ComfyHub) is a generation tool with community distribution. VULCA is a generation + evaluation + learning loop. ComfyUI asks "did you get an image?" VULCA asks "is this image culturally coherent, and what did we learn from making it?"

## Core Architecture

### The Creation Loop

```
Intent → Scout → Router → Draft → Critic → Queen → Archivist → Gallery
  ↑                                                                 ↓
  └──── ContextEvolver ← Digestion ← Feedback ← Session Store ←────┘
```

Every pipeline run follows this loop. The outer feedback path (Gallery → Feedback → Digestion → ContextEvolver) is what makes VULCA an organism rather than a tool. The `evolved_context.json` file produced by ContextEvolver is injected back into agent system prompts — the model weights are frozen, but the context evolves. This is **MemRL**: Memory-augmented Reinforcement Learning through context injection.

### Pipeline Agents

| Agent | Module | Role |
|-------|--------|------|
| **Scout** | `agents/` + `tools/` | Cultural evidence retrieval. Queries FAISS index + terminology matching before generation starts. Provides tradition-specific context to Draft. |
| **Router** | `cultural_pipelines/pipeline_router.py` | Routes intent to the correct tradition pipeline. Rule-based + LLM fallback. |
| **Draft** | `agents/draft_agent.py` | Image generation. Dispatches to registered providers (mock, diffusers, NB2, OpenAI, Replicate/Flux, Koala). Supports sub-stage execution and local reruns via inpainting. |
| **Critic** | `agents/critic_agent.py` | L1-L5 multi-dimensional scoring via VLM. Produces per-dimension scores, confidence values, cross-layer signals, and natural language critique. |
| **Queen** | `agents/queen_agent.py` | Decision gate. Reads Critic output and decides: accept, rerun (global or local), or pause (HITL). Configurable thresholds via QueenConfig. Strategy parameters evolve over time. |
| **QueenLLM** | `agents/queen_llm.py` | LLM-powered Queen variant. Uses language model reasoning for nuanced accept/rerun decisions beyond threshold rules. |
| **Archivist** | `agents/archivist_agent.py` | Persists results to session store, gallery, and checkpoint system. Tracks full creation lineage. |

### L1-L5 Evaluation Framework

The Critic scores every image on five layers (from the VULCA-Bench paper, arXiv:2601.07986):

| Layer | Dimension | What It Measures |
|-------|-----------|------------------|
| L1 | Visual Perception | Color, composition, form, spatial arrangement |
| L2 | Technical Analysis | Medium mastery, brushwork, material handling |
| L3 | Cultural Context | Tradition fidelity, historical accuracy, symbolism |
| L4 | Critical Interpretation | Meaning, narrative, conceptual depth |
| L5 | Philosophical Aesthetic | Transcendent quality, worldview embodiment |

Each tradition defines its own L1-L5 weight distribution. Chinese Xieyi weights L5 at 0.30 (philosophical depth matters most); Western Academic weights L1 and L2 higher (technique and perception matter more). These weights are not fixed — they are modulated dynamically per evaluation round.

### Provider System (9 Registered)

All image providers implement `AbstractProvider` and register via `@ProviderRegistry.register()`:

| Provider | Registration Name | Backend |
|----------|-------------------|---------|
| MockProvider | `mock` | Deterministic placeholder PNGs (stdlib only, no GPU) |
| DiffusersProvider | `diffusers` | HuggingFace SD 1.5, local GPU |
| NB2Provider | `nb2` | Gemini native image generation |
| OpenAIProvider | `openai` | DALL-E API |
| ReplicateProvider | `replicate` / `flux` | Replicate API (Flux models) |
| KoalaProviderAdapter | `koala` | Koala local inference |
| FallbackProvider | `fallback` | Chain of providers with retry + exponential backoff |
| FaultInjectProvider | `fault_inject` | Programmable failure injection for testing |
| ControlNetInpaintProvider | (internal) | Structure-preserving local reruns via ControlNet canny/depth |

Adding a provider is zero-config beyond the class definition — the `@ProviderRegistry.register("name")` decorator handles discovery. No orchestrator changes needed.

### Cultural Tradition System (9 Traditions)

Each tradition is a single YAML file in `data/traditions/`. Loaded at startup, hot-reloadable via `reload_traditions()`.

**Active traditions**: `chinese_xieyi`, `chinese_gongbi`, `japanese_traditional`, `islamic_geometric`, `western_academic`, `african_traditional`, `south_asian`, `watercolor`, `default`

Each YAML defines:

- **`weights`** — L1-L5 weight distribution (must sum to 1.0, auto-normalized)
- **`terminology`** — Domain terms with multilingual definitions, L-level mappings, aliases, and source citations. Used by Scout for evidence retrieval. Example: `披麻皴` (hemp-fiber texture stroke) mapped to L2+L3 in chinese_xieyi.
- **`taboos`** — Evaluation anti-patterns with severity and trigger patterns. Example: flagging "sloppy brushwork" as a critique of xieyi is a `high` severity taboo because loose brushwork is an intentional aesthetic.
- **`pipeline`** — Pipeline variant overrides (e.g., `scout_focus_layers: [L3, L5]` for chinese_xieyi).

### Dynamic Weight Modulation

Static tradition weights are the starting point. At evaluation time, `compute_dynamic_weights()` applies four modulation stages:

```
w_d = base_w_d × (1 + α × (1 - confidence_d)) × decay(round) × signal_boost(signals)
```

1. **Confidence modulation** — Low-confidence dimensions get weight boosts (need more evaluation attention)
2. **Round decay** — Later evaluation rounds decay toward uniform weights (diminishing returns on emphasis)
3. **Signal boost** — Cross-layer signals (REINTERPRET, CONFLICT, EVIDENCE_GAP) boost target dimensions by `0.2 × strength`
4. **Deviation clamp** — No dimension can deviate more than ±0.20 from its base weight

Output is always normalized to sum = 1.0.

### Skill Marketplace (6 Executors)

Skills are pluggable evaluation capabilities beyond the core L1-L5 Critic. Each implements `BaseSkillExecutor` with `__init_subclass__` auto-registration.

| Skill | Executor | What It Evaluates |
|-------|----------|-------------------|
| `composition_balance` | CompositionExecutor | Visual balance, rule of thirds, golden ratio |
| `color_harmony` | ColorHarmonyExecutor | Color theory compliance, palette coherence |
| `style_transfer` | StyleTransferExecutor | Fidelity to referenced artistic style |
| `brand_consistency` | BrandExecutor | Brand guideline adherence |
| `audience_fit` | AudienceExecutor | Target audience appropriateness |
| `trend_alignment` | TrendExecutor | Alignment with current visual trends |

Each skill also has a YAML definition in `data/skills/` for metadata (tags, version, input types). Tradition YAML configs are auto-registered as `tradition_*` skills by the SkillRegistry.

### Digestion System (Evolution Engine)

The digestion pipeline processes session history into evolved context. Seven components, each with `BaseDigester` auto-registration:

| Component | Role |
|-----------|------|
| **DigestAggregator** | Aggregates per-tradition, per-dimension score distributions |
| **PatternDetector** | Detects scoring patterns: `systematically_low`, `consistently_high`, `negative_feedback_dominant` |
| **PreferenceLearner** | Learns user preference profiles: preferred/avoided dimensions per tradition |
| **CulturalClusterer** | Clusters sessions in cultural feature space |
| **PromptDistiller** | Distills prompt archetypes from high-scoring sessions |
| **ConceptCrystallizer** | Crystallizes emergent cultural concepts from clusters |
| **ContextEvolver** | Orchestrates all digesters. Two-phase evolution: rule-based weight adjustment (±0.05 guardrail, sum=1.0) + LLM-powered agent/tradition insights (MemRL). Atomically saves to `evolved_context.json`. |

Safety guardrails in ContextEvolver:
- Minimum 5 sessions before any evolution runs
- Single weight adjustment capped at ±0.05
- No dimension can drop below 0.05
- Atomic file writes (tempfile + `os.replace`) to prevent corruption
- Full audit trail in `evolution_log.jsonl`

### Dual Orchestration

| Orchestrator | Module | Status | Architecture |
|-------------|--------|--------|--------------|
| **PipelineOrchestrator** | `orchestrator/orchestrator.py` | **Production** | Monolithic while-loop. All entry points (CLI, Gradio, API) use this by default. |
| **GraphOrchestrator** | `graph/graph_orchestrator.py` | **Production-candidate** | LangGraph StateGraph. Template-based topologies, custom node/edge definitions, agent plugin registry. Same `run_stream()` API. |

Both support: SSE streaming, HITL pause/resume, checkpoint resume, cost gate ($2.00/run), trajectory recording.

Switch via: `get_orchestrator(mode="pipeline")` or `get_orchestrator(mode="graph")`.

## Extension Points

VULCA has four primary extension mechanisms. Each uses auto-registration — no orchestrator modification required.

### 1. Provider (Image Generation)

```python
@ProviderRegistry.register("my_provider")
class MyProvider(AbstractProvider):
    @property
    def model_ref(self) -> str:
        return "my-model-v1"

    def generate(self, prompt, negative_prompt, seed, width, height, steps, sampler, output_path) -> str:
        # Your generation logic
        return output_path
```

### 2. Agent (Pipeline Stage)

```python
@AgentRegistry.register("my_agent")
class MyAgent(BaseAgent):
    name = "my_agent"
    description = "What this agent does"

    def execute(self, state) -> dict:
        return {"my_result": ...}
```

### 3. Skill (Evaluation Capability)

```python
class MySkillExecutor(BaseSkillExecutor):
    SKILL_NAME = "my_skill"  # auto-registers on class definition

    async def execute(self, image_path, context=None) -> SkillResult:
        return SkillResult(skill_name="my_skill", score=0.85, summary="...", details={})
```

### 4. Tradition (Cultural Configuration)

Create `data/traditions/my_tradition.yaml`:

```yaml
name: my_tradition
display_name:
  en: My Tradition
  zh: 我的传统
weights:
  L1: 0.20
  L2: 0.20
  L3: 0.20
  L4: 0.20
  L5: 0.20
terminology:
  - term: key_concept
    term_zh: 关键概念
    definition:
      en: What this concept means
    category: technique
    l_levels: [L2, L3]
taboos:
  - rule: "Do not misinterpret X as Y"
    severity: high
    l_levels: [L3, L4]
    trigger_patterns: ["wrong interpretation"]
pipeline:
  variant: my_tradition
```

Validated at load time (weight sum, required fields, name format). Hot-reloadable without restart.

### 5. Digester (Evolution Step)

```python
class MyDigester(BaseDigester):
    STEP_NAME = "my_step"  # auto-registers on class definition

    def digest(self, sessions, ctx: DigestContext) -> DigestContext:
        ctx.set("my_analysis", {"finding": "..."})
        return ctx
```

## Key File Paths

| Area | Path |
|------|------|
| Agent interfaces | `wenxin-backend/app/prototype/agents/interfaces.py` |
| Provider base + registry | `wenxin-backend/app/prototype/agents/draft_provider.py` |
| Critic agent | `wenxin-backend/app/prototype/agents/critic_agent.py` |
| Queen agent | `wenxin-backend/app/prototype/agents/queen_agent.py` |
| Pipeline orchestrator | `wenxin-backend/app/prototype/orchestrator/orchestrator.py` |
| Graph orchestrator | `wenxin-backend/app/prototype/graph/graph_orchestrator.py` |
| Tradition loader | `wenxin-backend/app/prototype/cultural_pipelines/tradition_loader.py` |
| Dynamic weights | `wenxin-backend/app/prototype/cultural_pipelines/dynamic_weights.py` |
| Skill base executor | `wenxin-backend/app/prototype/skills/executors/base.py` |
| Skill registry | `wenxin-backend/app/prototype/skills/skill_registry.py` |
| Context evolver | `wenxin-backend/app/prototype/digestion/context_evolver.py` |
| Base digester | `wenxin-backend/app/prototype/digestion/base.py` |
| Tradition YAMLs | `wenxin-backend/app/prototype/data/traditions/*.yaml` |
| Skill YAMLs | `wenxin-backend/app/prototype/data/skills/*.yaml` |
| Evolved context | `wenxin-backend/app/prototype/data/evolved_context.json` |
