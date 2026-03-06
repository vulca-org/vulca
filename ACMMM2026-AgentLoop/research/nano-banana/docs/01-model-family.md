# Nano Banana 模型族谱

## 三代模型对比

### NB1 — Nano Banana (Gemini 2.5 Flash Image)

| 属性 | 值 |
|------|-----|
| Model ID | `gemini-2.5-flash-image` |
| 内部代号 | GEMPIX |
| 底层 LLM | Gemini 2.5 Flash |
| 架构 | **Multimodal Diffusion Transformer (MMDiT)** |
| 参数量 | 450M - 8B (依任务缩放) |
| 处理块数 | 15-38 blocks |
| 生成方式 | **Autoregressive**：每张图生成 ~1,290 tokens，解码成图像 |
| 训练方式 | Sparse Mixture-of-Experts，不同网络部分为不同任务激活 |
| 训练数据 | 网页文档、代码、图像、音频、视频（多模态从头训练，非后嫁接） |
| 最高分辨率 | 1024×1024 |
| 速度 | ~3s (P50: 0.8s, P99: 1.5s) |
| 文字渲染 | ~80% 准确率 |
| 价格 | $0.039/张 (1024px) |
| 知识截止 | 2025-06 |
| 特点 | 多轮对话编辑、风格迁移、照片合成 |
| 限制 | 角色一致性有限、低分辨率偶发、水印可移除 |

**关键技术发现**：NB1 不是纯 diffusion，而是 **autoregressive token 生成 + 解码**。这意味着它的生成过程更类似 GPT 生成文本（next-token prediction），然后将 token 序列解码为图像。这与 Imagen（纯 diffusion）和 FLUX（Flow Matching）都不同。

### NB Pro — Nano Banana Pro (Gemini 3 Pro Image)

| 属性 | 值 |
|------|-----|
| Model ID | `gemini-3-pro-image-preview` |
| 底层 LLM | Gemini 3 Pro |
| 架构 | LLM 推理 + GemPix Diffusion Head |
| 最高分辨率 | 4K (4096×4096) |
| 速度 | 8-12s (Deep Inference mode) |
| 文字渲染 | ~94% 准确率 |
| 角色一致性 | 5 角色 |
| 价格 | $0.134/张 (1K/2K), $0.24/张 (4K) |
| 上下文窗口 | 65k input / 32k output |
| 特点 | Deep Inference — "thinks through" generation |

**关键特性**：NB Pro 首次引入 "思考" 机制。模型在生成前会考虑空间关系、光照物理、构图规则和创意意图。这是 generation-side self-correction 的第一个成熟实现。

### NB2 — Nano Banana 2 (Gemini 3.1 Flash Image)

| 属性 | 值 |
|------|-----|
| Model ID | `gemini-3.1-flash-image-preview` |
| 内部代号 | **GEMPIX 2** |
| 底层 LLM | **Gemini 3.1 Flash** |
| 架构 | **Gemini 3 Pro 推理 + GemPix 2 Diffusion Head + shared latent intent vector** |
| 最高分辨率 | **4K** |
| 速度 | **4-6s**（目标 <2s for standard） |
| 文字渲染 | ~90%+ |
| 角色一致性 | **5 角色 + 14 物体** |
| 价格 | $0.045 (0.5K) / $0.067 (1K) / $0.101 (2K) / $0.151 (4K) |
| 批量价格 | 半价：$0.022 / $0.034 / $0.050 / $0.076 |
| 上下文窗口 | 128k input / 32k output |
| Web Grounding | ✅ 支持 Google Search + Image Search |
| 发布日期 | **2026-02-26** |

**定位**：Pro 的推理质量 + Flash 的速度 + 更低成本。

## 演进路线

```
NB1 (2025-09)                NB Pro (2025-12)              NB2 (2026-02-26)
Gemini 2.5 Flash             Gemini 3 Pro                  Gemini 3.1 Flash
Autoregressive tokens        + Deep Inference              + 5-stage pipeline
~1,290 tokens/image          + thinking mechanism          + Plan-Evaluate-Improve
MMDiT 450M-8B               + 4K support                  + shared latent vector
1024×1024 max                + 94% text accuracy           + web grounding
~$0.039/image                ~$0.134/image                 + 5 char + 14 obj
                                                           ~$0.067/image (1K)
```

## 与竞品对比

| 模型 | 架构 | 速度 | 最高分辨率 | 文化推理 | 自纠正 | 价格 |
|------|------|------|-----------|---------|--------|------|
| SD 1.5 | Latent Diffusion | ~3s (local GPU) | 512×512 | ✗ | ✗ | Free (local) |
| FLUX.1-schnell | Flow Matching | ~1s (API) | 1024×1024 | ✗ | ✗ | ~$0.003 |
| DALL-E 3 | Diffusion | ~10s | 1024×1792 | 有限 | ✗ | $0.04 |
| Imagen 4 | Diffusion | ~5s | 4K | 有限 | ✗ | $0.02-0.06 |
| NB1 | AR + Diffusion | ~3s | 1024 | 有限 | 隐式 thinking | $0.039 |
| NB Pro | LLM + Diffusion | ~10s | 4K | 中等 | Deep Inference | $0.134 |
| **NB2** | **LLM + GemPix 2** | **~5s** | **4K** | **中等** | **5-stage loop** | **$0.067** |
