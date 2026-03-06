# 全线上方案：云 API 定价调研 (2026-02-27)

## 1. 图像生成 API

| 模型 | 提供商 | 价格/张 (1K) | 速度 | 推荐 |
|------|--------|-------------|------|------|
| FLUX.1 Schnell | Together.ai | **$0.003** | ~0.7s | ★ 最便宜 |
| SDXL | Replicate | $0.0043 | ~2s | |
| FLUX.2 Dev | fal.ai | $0.008 | | |
| FLUX.2 Klein 4B | BFL | $0.014 | 快 | |
| Imagen 4.0 Fast | Together.ai | $0.020 | | |
| FLUX.1 Dev | Together/Replicate | $0.025 | ~3s | ★ 高质量 |
| FLUX.2 Pro | BFL | $0.030 | | |
| NB2 | Google | $0.067 | ~5s | ★ 最高质量 |

## 2. Inpainting API — 关键发现

**FLUX.1 Fill 支持 API 定向 Inpainting！**

| 模型 | 提供商 | 价格/张 | mask 支持 | 推荐 |
|------|--------|---------|----------|------|
| SD Inpainting | Replicate | **$0.002** | ✅ | 最便宜但质量低 |
| **FLUX.1 Fill Dev** | Replicate/fal | **$0.025** | **✅ image+mask** | **★ 推荐** |
| FLUX.1 Fill Pro | BFL/Replicate | $0.050 | ✅ image+mask | 最高质量 |
| FLUX Dev Inpaint+LoRA | fal.ai | $0.035 | ✅ + LoRA | 可定制 |

输入: 原图 + mask 图 (白=重绘区域) + prompt
→ 完全支持 targeted local inpainting, 无需本地 GPU!

## 3. VLM 评估 API

| 模型 | 提供商 | 每次评估成本 | 免费额度 | 推荐 |
|------|--------|-------------|---------|------|
| **Gemini 2.5 Flash-Lite** | Google | **$0** | **1000次/天** | **★ 免费之王** |
| GPT-4o-mini | OpenAI | $0.0002 | 无 | ★ 稳定备选 |
| Qwen2.5-VL-32B | DeepInfra | $0.0003 | 无 | 开源 VLM |
| Gemini 2.5 Flash | Google | $0.0009 | 有 | |
| Llama 4 Maverick | Together | $0.0005 | 无 | |

**Gemini Flash-Lite 免费额度 = 每天 1000 次图像评估 = $0**

## 4. 全 API 方案成本估算

### 180 次 ablation (6条件 × 30任务)

| 环节 | 服务 | 单价 | 总价 |
|------|------|------|------|
| Draft (4候选/次) | FLUX.1 Schnell | $0.003×4 | $2.16 |
| Inpaint (50%触发) | FLUX.1 Fill Dev | $0.025 | $2.25 |
| VLM Critic | Gemini Flash-Lite | $0 (免费) | **$0** |
| Scout LLM | DeepSeek | $0.001 | $0.18 |
| **总计** | | | **~$4.59** |

### 高质量版

| 环节 | 服务 | 单价 | 总价 |
|------|------|------|------|
| Draft | FLUX.1 Dev | $0.025×4 | $18.00 |
| Inpaint | FLUX.1 Fill Pro | $0.050 | $4.50 |
| VLM Critic | GPT-4o-mini | $0.0002 | $0.036 |
| **总计** | | | **~$22.54** |

## 5. Cloud GPU (如需本地模型)

最便宜 24GB VRAM:
- Vast.ai RTX 3090: $0.18-0.22/hr
- RunPod RTX 3090: $0.22/hr
- Modal A10G serverless: $0.000306/秒 ($30/月免费额度)

## 参考 URL

- Together.ai: https://www.together.ai/pricing
- fal.ai: https://fal.ai/pricing
- BFL: https://bfl.ai/pricing
- Replicate: https://replicate.com/pricing
- Gemini: https://ai.google.dev/gemini-api/docs/pricing
- OpenAI: https://platform.openai.com/docs/pricing
- DeepInfra: https://deepinfra.com/pricing
- RunPod: https://www.runpod.io/gpu-pricing
- Vast.ai: https://vast.ai/pricing
- Modal: https://modal.com/pricing
