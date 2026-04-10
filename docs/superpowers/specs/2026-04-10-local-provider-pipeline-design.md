# Local Provider Pipeline Validation Design

**Date:** 2026-04-10
**Status:** Approved, ready for implementation plan

## Background

v0.14.0 shipped with an E2E spec (`2026-04-10-e2e-readme-rewrite-design.md`) that requires ~31-38 Gemini API calls. The Gemini API is currently unavailable. We need to validate the full SDK/pipeline chain using local, zero-cost providers before expanding to the full E2E suite.

## Goals

1. **Local image generation** via ComfyUI + SDXL on Apple Silicon (MPS backend).
2. **Local VLM scoring** via Ollama + Gemma 3 vision, routed through existing LiteLLM integration.
3. **Pipeline unblocking** — remove Gemini-specific API key gates so local providers can flow through the pipeline without a cloud key.
4. **Validation tests** — pytest-based `@pytest.mark.local_provider` tests covering single-image create, VLM scoring, and full e2e chain.

## Non-Goals

- Full E2E suite (Phases 1-8) — that comes after this validation passes.
- README rewrite — blocked until we have real output artifacts.
- Modifying ComfyUI provider workflow logic.
- Adding Ollama as a new image generation provider.

## Architecture

### Local Stack

```
pytest --run-local-provider
    ├── ComfyUI (localhost:8188) ── SDXL checkpoint ── real PNG
    └── Ollama  (localhost:11434) ── gemma3:12b ──── real L1-L5 scores
```

### Environment Variables

```bash
# Image generation
export VULCA_IMAGE_BASE_URL=http://localhost:8188

# VLM scoring (must use ollama_chat/ prefix for vision support)
export VULCA_VLM_MODEL=ollama_chat/gemma3:12b
export OLLAMA_API_BASE=http://localhost:11434
```

### Pipeline Changes (3 files)

The pipeline currently hard-gates on Gemini API keys. Three targeted changes unblock local providers:

**1. `src/vulca/pipeline/engine.py` — `_resolve_api_key()`**

Currently only checks `GEMINI_API_KEY` / `GOOGLE_API_KEY`. When `VULCA_VLM_MODEL` starts with `ollama`, return sentinel `"local"` so downstream pipeline code sees a non-empty key.

**2. `src/vulca/_engine.py` — `Engine.__init__()`**

Currently raises `ValueError` if no Gemini key and not mock. Add same `ollama` model detection to skip the key requirement.

**3. `src/vulca/_vlm.py` — `score_image()`**

Currently doesn't pass `api_base` to `litellm.acompletion()`. Read `OLLAMA_API_BASE` env var and pass it when model starts with `ollama`.

### What Doesn't Need Changing

- **ComfyUI provider** (`comfyui.py`) — already works, `__init__` accepts `**kwargs` and ignores `api_key`.
- **LiteLLM VLM provider** (`vlm_litellm.py`) — used by SDK path, not pipeline path. Pipeline uses `_vlm.score_image()` directly.
- **Provider registry** (`__init__.py`) — ComfyUI already registered.
- **Capabilities** (`capabilities.py`) — "comfyui" falls through to `_DEFAULT_CAPABILITIES` which includes `VLM_SCORING`. This is correct: ComfyUI provides images, and the separate Ollama VLM handles scoring.
- **EvaluateNode** (`evaluate.py:77`) — checks `not ctx.api_key`, which passes because `_resolve_api_key` now returns `"local"` for Ollama setups.

## Test Plan

4 pytest tests in `tests/test_local_provider_e2e.py`, gated behind `@pytest.mark.local_provider` + `--run-local-provider` flag.

| Test | What it validates |
|------|-------------------|
| `test_comfyui_single_create_xieyi` | ComfyUI generates chinese_xieyi image; result is valid PNG, >10KB |
| `test_comfyui_single_create_western` | ComfyUI generates western_academic image; result is valid PNG |
| `test_ollama_vlm_score` | Ollama scores a test image via `_vlm.score_image()`; returns L1-L5 in 0.0-1.0 |
| `test_local_e2e_create_then_evaluate` | Full chain: ComfyUI create → Ollama evaluate → valid scores |

Assertions:
- Image is valid PNG (magic bytes `\x89PNG`), dimensions > 0, file size > 10KB
- L1-L5 scores all in 0.0-1.0 range
- At least one rationale is non-empty string

## Environment Setup

### ComfyUI (Image Generation)

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git && cd ComfyUI
python3 -m venv venv && source venv/bin/activate
pip install torch torchvision torchaudio
pip install -r requirements.txt
# Download sd_xl_base_1.0.safetensors into models/checkpoints/
python main.py --force-fp32
# Verify: curl http://127.0.0.1:8188/system_stats
```

### Ollama (VLM Scoring)

```bash
brew install ollama
ollama serve &  # or: ollama will auto-serve on pull
ollama pull gemma3:12b
# Verify: curl http://localhost:11434/api/tags
```

### Key Facts

- **LiteLLM routing**: `ollama_chat/` prefix required for vision (uses `/api/chat` endpoint). `ollama/` silently drops images.
- **Apple Silicon**: ComfyUI uses MPS backend automatically. `--force-fp32` avoids fp16 MPS operator gaps.
- **Gemma 3**: All variants include vision encoder. 12b needs ~8-10GB RAM (Q4 quantized).
- **No Gemma 4**: Does not exist as of 2026-04-10. Gemma 3 is the latest.

## Risks

| Risk | Mitigation |
|------|-----------|
| ComfyUI MPS generates slowly (~60-120s/image) | Tests have 300s timeout (already in comfyui.py) |
| Gemma 3 12b JSON output inconsistent | Existing `_vlm.py` has lenient JSON parsing with regex fallback |
| `"local"` sentinel key leaks to cloud providers | Only set when `VULCA_VLM_MODEL` starts with `ollama`; Gemini provider checks its own key independently |
| LiteLLM doesn't auto-resolve `OLLAMA_API_BASE` | Explicitly pass `api_base` in `score_image()` as fallback |
