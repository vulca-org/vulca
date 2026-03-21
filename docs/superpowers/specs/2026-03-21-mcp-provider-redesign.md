# VULCA MCP Server + Provider Abstraction Redesign

**Date**: 2026-03-21
**Status**: Design approved, pending implementation
**Author**: Yu Haorui + Claude

## Context

VULCA's MCP server currently has 3 tools with incomplete returns (no image data, no rationale, no HITL continuation). The provider system is hardcoded to Gemini. This redesign addresses both gaps to make VULCA a first-class AI agent tool with pluggable model backends.

## Design Decisions (confirmed)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Integration strategy | **W: Three-layer** (CLI full, SDK wraps, MCP lightweight) | CLI is already most complete; MCP should be lightweight for high-frequency ops |
| Agent priority | **B > C > A** (Creation > Analysis > Evaluation) | Creation workflow is the core product |
| MCP tool count | **6 tools** (3 fixed + 3 new) | Enough for full workflow; CLI fallback for complex ops |
| Return format | **Style A: Data-dense** (tables, structured) | Agents need parseable structure for decision-making |
| Tradition guide depth | **Depth 2** (weights + terminology + taboos) | Enough context without token bloat |
| Provider interface | **P2: Protocol pattern** | Users bring their own models; we provide 3-4 built-in implementations |

## Part 1: MCP Server (6 Tools)

### Common Parameters

All tools accept:
- `view: str = "summary"` — `"summary"` (minimal) or `"detailed"` (full)
- `format: str = "json"` — `"json"` (dict) or `"markdown"` (formatted text)

### Tool 1: `create_artwork` (fix existing)

```python
async def create_artwork(
    intent: str,
    tradition: str = "default",
    provider: str = "mock",
    hitl: bool = False,
    weights: str = "",
    view: str = "summary",
    format: str = "json",
) -> dict | str
```

**Changes from current:**
- summary adds: `best_image_url`, `best_candidate_id`
- detailed adds: `scores`, `rationales`, `rounds`, `cost_usd`
- markdown format returns Style A table

**summary response:**
```json
{
  "session_id": "a3f8c1d2",
  "status": "completed",
  "tradition": "chinese_xieyi",
  "weighted_total": 0.84,
  "best_image_url": "mock://94953b1d35b5.svg",
  "best_candidate_id": "94953b1d35b5"
}
```

**detailed response:**
```json
{
  "session_id": "a3f8c1d2",
  "status": "completed",
  "tradition": "chinese_xieyi",
  "weighted_total": 0.84,
  "best_image_url": "mock://94953b1d35b5.svg",
  "best_candidate_id": "94953b1d35b5",
  "scores": {"L1": 0.85, "L2": 0.72, "L3": 0.91, "L4": 0.79, "L5": 0.88},
  "rationales": {
    "L1": "Masterful use of blank space (留白)...",
    "L2": "Hemp-fiber strokes lack variation...",
    "L3": "Strong ink gradation (墨分五色)...",
    "L4": "Narrative coherence could deepen...",
    "L5": "Philosophical resonance is strong..."
  },
  "rounds": [
    {"round_num": 1, "weighted_total": 0.78, "decision": "rerun"},
    {"round_num": 2, "weighted_total": 0.84, "decision": "accept"}
  ],
  "total_rounds": 2,
  "cost_usd": 0.003
}
```

**markdown+detailed:**
```markdown
## VULCA Creation: sess_a3f8c1d2
- Status: completed | Tradition: chinese_xieyi | Rounds: 2 | Cost: $0.003

| Dim | Score | Weight | Rationale |
|-----|-------|--------|-----------|
| L1 | 0.85 | 10% | Masterful use of blank space (留白) |
| L2 | 0.72 | 15% | Hemp-fiber strokes lack variation |
| L3 | 0.91 | 25% | Strong ink gradation (墨分五色) |
| L4 | 0.79 | 20% | Narrative coherence could deepen |
| L5 | 0.88 | 30% | Philosophical resonance is strong |

**Weighted Total**: 0.84
**Image**: mock://94953b1d35b5.svg
**Recommendation**: Strengthen L2 brushwork variation
```

### Tool 2: `evaluate_artwork` (fix existing)

```python
async def evaluate_artwork(
    image_path: str,
    tradition: str = "",
    intent: str = "",
    mock: bool = False,
    view: str = "summary",
    format: str = "json",
) -> dict | str
```

**Changes:** detailed adds `rationales`, `recommendations`, `risk_flags`.

### Tool 3: `list_traditions` (fix existing)

```python
async def list_traditions(
    format: str = "json",
) -> dict | str
```

**Changes:** Each tradition adds `emphasis` and `description` one-liner.

```json
{
  "traditions": {
    "chinese_xieyi": {
      "weights": {"L1": 0.10, ...},
      "emphasis": "Philosophical",
      "description": "Expressive ink wash emphasizing philosophical depth over technical precision"
    }
  }
}
```

### Tool 4: `get_tradition_guide` (new — differentiation)

```python
async def get_tradition_guide(
    tradition: str,
    format: str = "json",
) -> dict | str
```

**Returns depth-2 cultural context:**
```json
{
  "tradition": "chinese_xieyi",
  "description": "Xieyi (写意) emphasizes expressive brushwork and philosophical depth...",
  "emphasis": "Philosophical",
  "weights": {"L1": 0.10, "L2": 0.15, "L3": 0.25, "L4": 0.20, "L5": 0.30},
  "evolved_weights": {"L1": 0.35, "L2": 0.08, ...},
  "sessions_count": 47,
  "terminology": [
    {"term": "留白", "translation": "blank space", "meaning": "Deliberate emptiness carrying expressive weight"},
    {"term": "墨分五色", "translation": "five ink gradations", "meaning": "Tonal range from dry to wet ink"},
    {"term": "气韵生动", "translation": "spirit resonance", "meaning": "Vital energy flowing through the composition"}
  ],
  "taboos": [
    "Avoid photorealistic rendering — contradicts xieyi's expressive philosophy",
    "Never fill all negative space — 留白 is structural, not decorative"
  ]
}
```

**Data source:** Reads from existing YAML tradition configs (`vulca/cultural/data/traditions/*.yaml`).

### Tool 5: `resume_artwork` (new — HITL closure)

```python
async def resume_artwork(
    session_id: str,
    action: str,                  # "accept" | "refine" | "reject"
    feedback: str = "",           # guidance for refinement
    locked_dimensions: str = "",  # "L3,L5" — keep these scores
    view: str = "summary",
    format: str = "json",
) -> dict | str
```

**Agent HITL workflow:**
```
1. create_artwork(hitl=True) → {status: "waiting_human", session_id: "xxx", scores: {...}}
2. Agent reviews scores, decides L2 is too low
3. resume_artwork(session_id="xxx", action="refine", feedback="Strengthen brushwork", locked_dimensions="L3,L5")
4. → {status: "completed", weighted_total: 0.87, ...}
```

**Implementation:** Calls `vulca.pipeline.engine.execute()` with the same tradition/subject but adds feedback to the generate prompt and passes locked_dimensions to the evaluate node. Uses a new session (like HITL rerun in Canvas), not truly resuming the old pipeline state.

**On "accept":** Fires `on_complete` hook (session storage + evolution).
**On "reject":** Returns `{status: "rejected"}`, no side effects.

### Tool 6: `get_evolution_status` (new — evolution visibility)

```python
async def get_evolution_status(
    tradition: str,
    format: str = "json",
) -> dict | str
```

**Returns:**
```json
{
  "tradition": "chinese_xieyi",
  "total_sessions": 47,
  "original_weights": {"L1": 0.10, "L2": 0.15, "L3": 0.25, "L4": 0.20, "L5": 0.30},
  "evolved_weights": {"L1": 0.35, "L2": 0.08, "L3": 0.13, "L4": 0.10, "L5": 0.15},
  "weight_changes": {"L1": "+0.25", "L2": "-0.07", "L3": "-0.12", "L4": "-0.10", "L5": "-0.15"},
  "top_insight": "L1 Visual Perception consistently underweighted — boosted based on scoring patterns",
  "few_shot_count": 15,
  "last_evolved": "2026-03-21T20:30:00Z"
}
```

**Data source:** Reads from `evolved_context.json` (ContextEvolver output) and YAML defaults.

## Part 2: Provider Protocol

### ImageProvider Protocol

```python
# vulca/providers/base.py

from typing import Protocol, runtime_checkable
from dataclasses import dataclass

@dataclass
class ImageResult:
    image_b64: str          # base64-encoded image
    mime: str = "image/png" # MIME type
    metadata: dict = None   # optional provider-specific metadata

@runtime_checkable
class ImageProvider(Protocol):
    async def generate(
        self,
        prompt: str,
        *,
        tradition: str = "",
        subject: str = "",
        reference_image_b64: str = "",
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        **kwargs,
    ) -> ImageResult:
        """Generate an image from a text prompt."""
        ...
```

### VLMProvider Protocol

```python
@dataclass
class L1L5Scores:
    L1: float
    L2: float
    L3: float
    L4: float
    L5: float
    rationales: dict[str, str] = None  # {"L1": "reason...", ...}

@runtime_checkable
class VLMProvider(Protocol):
    async def score(
        self,
        image_b64: str,
        *,
        tradition: str = "",
        subject: str = "",
        guidance: str = "",     # tradition-specific scoring prompt
        **kwargs,
    ) -> L1L5Scores:
        """Score an image on L1-L5 cultural dimensions."""
        ...
```

### Built-in Implementations

| Provider | Class | What it wraps |
|----------|-------|---------------|
| `GeminiImageProvider` | ImageProvider | Gemini 3.1 Flash Image (current nb2 code) |
| `OpenAIImageProvider` | ImageProvider | DALL-E 3 via OpenAI API |
| `ComfyUIImageProvider` | ImageProvider | ComfyUI REST API (local) |
| `MockImageProvider` | ImageProvider | Deterministic SVG placeholders (current mock code) |
| `LiteLLMVLMProvider` | VLMProvider | Any LiteLLM-supported model (current _vlm.py code) |
| `MockVLMProvider` | VLMProvider | Deterministic scores (current mock code) |

### Usage in SDK

```python
import vulca

# Default (Gemini/LiteLLM)
result = vulca.create("水墨山水")

# Custom image provider
from vulca.providers import ComfyUIImageProvider
result = vulca.create("水墨山水", image_provider=ComfyUIImageProvider(base_url="http://localhost:8188"))

# Custom VLM
from vulca.providers import LiteLLMVLMProvider
result = vulca.evaluate("painting.jpg", vlm_provider=LiteLLMVLMProvider(model="ollama/llava"))

# Fully custom
class MyProvider(ImageProvider):
    async def generate(self, prompt, **kwargs):
        # call my model
        return ImageResult(image_b64="...", mime="image/png")

result = vulca.create("水墨山水", image_provider=MyProvider())
```

### Usage in CLI

```bash
# Default
vulca create "水墨山水"

# Switch image provider
vulca create "水墨山水" --image-provider openai
vulca create "水墨山水" --image-provider comfyui --image-base-url http://localhost:8188

# Switch VLM
vulca evaluate painting.jpg --vlm-model ollama/llava --vlm-base-url http://localhost:11434
```

### Usage in MCP

```python
create_artwork(
    intent="水墨山水",
    provider="comfyui",           # matches built-in name
    provider_base_url="http://localhost:8188",  # optional override
)
```

MCP only supports built-in provider names (string). Custom Protocol implementations require SDK.

### Environment Variable Configuration

```bash
# Image generation
VULCA_IMAGE_PROVIDER=openai          # default: gemini
VULCA_IMAGE_BASE_URL=http://...      # for comfyui/a1111
VULCA_IMAGE_API_KEY=sk-...           # provider-specific key

# VLM scoring
VULCA_VLM_MODEL=ollama/llava         # default: gemini/gemini-2.5-flash
VULCA_VLM_BASE_URL=http://...        # for local models
```

## Part 3: CLI Sync

| Command | Change |
|---------|--------|
| `vulca evaluate ... --json` | Add `rationales` to JSON output |
| `vulca create ... --json` | Add `best_image_url` to JSON output |
| `vulca traditions` | Add `description` per tradition |
| `vulca tradition <name>` (new) | Maps to `get_tradition_guide` |
| `vulca evolution <name>` (new) | Maps to `get_evolution_status` |
| `vulca create --image-provider X` (new) | Provider selection |
| `vulca evaluate --vlm-model X` (new) | VLM model selection |

## Part 4: What We Are NOT Doing

- No `vulca_` namespace prefix on MCP tools (only 6 tools, not needed yet)
- No batch APIs (agent can loop or use CLI)
- No session history query via MCP (CLI `--json` covers this)
- No Markdown format for `list_traditions` (too simple)
- No TextProvider protocol (intent resolution uses LiteLLM directly, not worth abstracting)
- No streaming in MCP (create/evaluate are fast enough synchronously)

## File Changes Estimate

| File | Change |
|------|--------|
| `vulca/mcp_server.py` | Rewrite: 3 tools → 6 tools + view/format params (~200 lines) |
| `vulca/providers/__init__.py` | New: provider registry + re-exports |
| `vulca/providers/base.py` | New: ImageProvider + VLMProvider protocols + dataclasses (~60 lines) |
| `vulca/providers/gemini.py` | New: extract from generate.py (~80 lines) |
| `vulca/providers/openai.py` | New: DALL-E 3 adapter (~50 lines) |
| `vulca/providers/comfyui.py` | New: ComfyUI REST adapter (~60 lines) |
| `vulca/providers/mock.py` | New: extract from generate.py (~40 lines) |
| `vulca/providers/vlm.py` | New: extract from _vlm.py + LiteLLM wrapper (~80 lines) |
| `vulca/pipeline/nodes/generate.py` | Refactor: use ImageProvider protocol |
| `vulca/_vlm.py` | Refactor: use VLMProvider protocol |
| `vulca/cli.py` | Add: `tradition` + `evolution` commands, provider flags |
| `vulca/create.py` | Add: `image_provider` + `vlm_provider` params |
| `vulca/evaluate.py` | Add: `vlm_provider` param |
| `tests/test_providers.py` | New: provider protocol tests |
| `tests/test_mcp_v2.py` | New: 6-tool MCP tests |

Estimated: ~15 files, ~800 lines new code, ~200 lines refactored.
