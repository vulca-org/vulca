# Local Provider Setup (ComfyUI + Ollama)

Zero-cost local pipeline for development and testing. No cloud API keys required.

## Prerequisites

- macOS with Apple Silicon (M1/M2/M3/M4/M5)
- Python 3.10+
- ~20GB disk (SDXL checkpoint + Gemma 3 model)
- 16GB+ unified memory recommended

## 1. ComfyUI (Image Generation)

```bash
# Clone and install
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python3 -m venv venv && source venv/bin/activate
pip install torch torchvision torchaudio
pip install -r requirements.txt

# Download SDXL checkpoint (~7GB)
# Place sd_xl_base_1.0.safetensors in ComfyUI/models/checkpoints/
# Download from: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0

# Start server (--force-fp32 for MPS stability)
python main.py --force-fp32

# Verify
curl http://127.0.0.1:8188/system_stats
```

## 2. Ollama (VLM Scoring)

```bash
brew install ollama
ollama serve &             # Start Ollama server (runs in background)
ollama pull gemma3:12b     # ~8GB, includes vision encoder

# Verify
curl http://localhost:11434/api/tags
```

## 3. Environment Variables

```bash
export VULCA_IMAGE_BASE_URL=http://localhost:8188
export VULCA_VLM_MODEL=ollama_chat/gemma3:12b
export OLLAMA_API_BASE=http://localhost:11434
```

Add to your shell profile (~/.zshrc) for persistence.

## 4. Run Tests

```bash
# Unit tests only (no services needed)
pytest tests/test_local_provider_e2e.py -v

# Full integration tests (requires ComfyUI + Ollama running)
pytest tests/test_local_provider_e2e.py --run-local-provider -v
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| ComfyUI black images | Use `--force-fp32` instead of `--force-fp16` |
| ComfyUI timeout | SDXL on MPS takes 60-120s; timeout is 300s |
| Ollama connection refused | Run `ollama serve` first |
| VLM returns empty scores | Ensure model is `ollama_chat/` not `ollama/` |
| `ValueError: No API key` | Ensure `VULCA_VLM_MODEL` starts with `ollama` |
