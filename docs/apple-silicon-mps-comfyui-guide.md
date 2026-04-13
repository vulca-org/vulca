# Apple Silicon MPS + ComfyUI/SDXL Compatibility Guide

> Diagnosed during VULCA v0.15.0 development (April 2026).
> Tested on Apple M5, macOS 26.4.0, PyTorch 2.11.0, ComfyUI b920bdd7.

---

## 1. Problem Statement

SDXL image generation via ComfyUI on Apple Silicon produces **black** (all-zero, ~4 KB) or **noise** (~2 MB random pixels) images.

Key observations:

- KSampler diffusion runs to completion (20 steps, progress bars, no errors)
- VAEDecode output is corrupt despite successful sampling
- Affects **PyTorch 2.10.0+** on the MPS backend
- `--force-fp32` does **NOT** fix it — this is a correctness bug, not a precision issue

---

## 2. Environment Tested

| Component | Version |
|-----------|---------|
| Chip | Apple M5 (unified memory, 32 GB) |
| OS | macOS 26.4.0 (Darwin 25.4.0) |
| ComfyUI | Latest (commit `b920bdd7`) |
| Checkpoint | SDXL Base 1.0 (`sd_xl_base_1.0.safetensors`, 6.5 GB) |
| Python | 3.11 (ComfyUI venv) |
| PyTorch | 2.11.0 (MPS backend) |

---

## 3. Root Cause Analysis

Three compounding PyTorch MPS bugs cause this failure.

### Bug 1: SDPA Non-Contiguous Tensor Regression

**PyTorch Issue:** [pytorch/pytorch#163597](https://github.com/pytorch/pytorch/issues/163597)

Introduced in PyTorch 2.8.0. MPS SDPA kernels produce wildly incorrect results when given non-contiguous tensors. SDXL's cross-attention performs transpose operations that create non-contiguous views, feeding garbage embeddings into the U-Net.

Error magnitude: **~34.0** vs normal **~0.000006**.

### Bug 2: Conv2d Chunk Correctness Bug

**PyTorch Issue:** [pytorch/pytorch#169342](https://github.com/pytorch/pytorch/issues/169342)

Affects PyTorch 2.9.0+. The `chunk() -> conv()` pattern produces correct results only for the first batch element. SDXL's VAE decoder uses this pattern extensively, causing partially correct latents that decode to noise or black.

### Bug 3: Native Metal Kernel Migration Regressions

**PyTorch Issue:** [pytorch/pytorch#155797](https://github.com/pytorch/pytorch/issues/155797)

PyTorch 2.10-2.11 migrated operators from MPSGraph to native Metal shaders, introducing multiple silent correctness regressions.

**ComfyUI Issue:** [Comfy-Org/ComfyUI#10681](https://github.com/Comfy-Org/ComfyUI/issues/10681) — identical symptoms reported on M3 Ultra.

### Why VAEDecode Is the Failure Point

- VAE decoder uses Conv2d with large channel counts (hit by Bug 2)
- Uses GroupNorm with float16 inputs (NaN propagation)
- Single-pass decoder — no self-correction like iterative KSampler
- Intermediate values explode to **9.5e+25** → GroupNorm cannot recover → all-zero or random output

### Why `--force-fp32` Does Not Help

The bugs are correctness issues in Metal kernel stride handling, not precision issues. Conv2d and SDPA produce wrong results in float32 too.

---

## 4. PyTorch Version Compatibility Matrix

| Version | SDXL on MPS | Notes |
|---------|-------------|-------|
| 2.4.1 | ✅ Stable | Last fully validated version for MPS diffusion |
| 2.5.x | ⚠️ Degraded | Memory +50%, speed -60% ([#139389](https://github.com/pytorch/pytorch/issues/139389)) |
| 2.6.x | ⚠️ Partial | Some SDPA issues, `--force-fp32` can help |
| 2.7.x | ⚠️ Partial | Similar to 2.6 |
| 2.8.0 | ❌ Broken | SDPA non-contiguous bug introduced ([#163597](https://github.com/pytorch/pytorch/issues/163597)) |
| **2.9.0** | **✅ Working** | **Sweet spot**: pre-Metal migration, SDPA bug masked by ComfyUI attention slicing |
| 2.9.1 | ✅ Likely safe | Patch release |
| 2.10.0 | ❌ Broken | Black images confirmed on M3 Ultra ([#10681](https://github.com/Comfy-Org/ComfyUI/issues/10681)) |
| 2.11.0 | ❌ Broken | Black/noise confirmed on M5 (this document) |

---

## 5. Solution: Pin `torch==2.9.0`

```bash
# In ComfyUI venv
cd ~/dev/ComfyUI
./venv/bin/pip install torch==2.9.0 torchvision==0.24.0 torchaudio==2.9.0

# Start ComfyUI with venv (NEVER use system python)
./venv/bin/python main.py --listen 0.0.0.0 --port 8188
```

Verify the fix:

```bash
./venv/bin/python -c "import torch; print(torch.__version__, torch.backends.mps.is_available())"
# Expected: 2.9.0 True
```

---

## 6. Additional Workarounds

If pinning torch is not possible, these partial mitigations may help.

### Force VAE to CPU

```bash
# Bypasses MPS for decode only
./venv/bin/python main.py --vae-cpu
# or
./venv/bin/python main.py --fp32-vae
```

### Disable MPS SDPA Fast Path

```python
import torch
torch.backends.mps.enable_sdpa = False
```

### Environment Variables

```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
```

### Use fp16-fix VAE

Replace the default SDXL VAE with [`madebyollin/sdxl-vae-fp16-fix`](https://huggingface.co/madebyollin/sdxl-vae-fp16-fix), which avoids NaN propagation in GroupNorm.

---

## 7. How We Diagnosed This

1. v3 gallery images (April 11) generated perfectly with simple prompts
2. Phase 2 layered pipeline (April 12) produced noise — initially attributed to CLIP token limit
3. Fixed CLIP prompt compression (< 70 tokens) — still noise
4. Discovered even simple direct ComfyUI API calls produce noise/black
5. System reboot — still broken
6. `--force-fp32` — still broken
7. Downgraded venv torch 2.11.0 → 2.9.0 — **immediately fixed**
8. Root cause research → 3 compounding PyTorch MPS bugs identified

---

## 8. VULCA-Specific Findings

During this investigation we also fixed three VULCA bugs that compound with MPS issues:

- **ANCHOR hallucination** — Prompt section headers `[CANVAS ANCHOR]` caused SDXL to paint literal ship anchors. Renamed to `[CANVAS]`. ([74f9952](../../commit/74f9952))
- **CLIP token overflow** — Structured prompts (120+ tokens) exceed SDXL CLIP's 77-token limit. Added CLIP-aware flat prompt mode for ComfyUI. ([74f9952](../../commit/74f9952))
- **Background keying** — Luminance keying on background layers made white paper transparent. Added `content_type` guard. ([42e0e3d](../../commit/42e0e3d))

---

## 9. References

- [pytorch/pytorch#163597](https://github.com/pytorch/pytorch/issues/163597) — SDPA MPS non-contiguous regression
- [pytorch/pytorch#169342](https://github.com/pytorch/pytorch/issues/169342) — Conv2d chunk correctness
- [pytorch/pytorch#155797](https://github.com/pytorch/pytorch/issues/155797) — Metal kernel migration visual bugs
- [pytorch/pytorch#141471](https://github.com/pytorch/pytorch/issues/141471) — MPS noise regression after 2.4.1
- [pytorch/pytorch#139389](https://github.com/pytorch/pytorch/issues/139389) — MPS memory/speed regression
- [pytorch/pytorch#142836](https://github.com/pytorch/pytorch/issues/142836) — Conv2d silent correctness bug
- [Comfy-Org/ComfyUI#10681](https://github.com/Comfy-Org/ComfyUI/issues/10681) — Black images M3 Ultra + PyTorch 2.10
- [Comfy-Org/ComfyUI#6254](https://github.com/Comfy-Org/ComfyUI/issues/6254) — VAEDecode BFloat16 MPS
- [Civitai: Fixing Black Images on Mac MPS](https://civitai.com/articles/11106/fixing-black-images-in-comfyui-on-mac-m1m2-pytorch-260-and-mps)
