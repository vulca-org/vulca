# NB2 架构逆向工程 (2026-02-27)

## 核心结论

**Google 从未发布 Nano Banana / Gemini 图像生成的正式技术论文。**
Latent Space: "there's no research detail or paper whatsoever"

## 已确认的技术事实

### 1. Token 消耗量 (从定价反推)

| 模型 | 分辨率 | 输出 Token 数 |
|------|--------|--------------|
| NB1 (2.5 Flash Image) | 1K | 1,290 tokens |
| NB Pro (3 Pro Image) | 1K | 1,120 tokens |
| NB Pro | 4K | 2,000 tokens |
| **NB2 (3.1 Flash Image)** | **0.5K** | **747 tokens** |
| **NB2** | **1K** | **1,120 tokens** |
| **NB2** | **2K** | **1,680 tokens** |
| **NB2** | **4K** | **2,520 tokens** |

来源: Max Woolf (minimaxir.com), Google pricing docs

### 2. Thinking 机制

- 强制生成**最多 2 张中间图像** (thought images)
- 中间图像**不计费**
- 最终图像 = 第 2 张中间图像的优化版
- **不可禁用** (架构内置)
- NB2 支持 `thinkingLevel: "minimal"` 或 `"high"`
- `includeThoughts=true` 可获取思考摘要文本
- `thought_signature` 加密上下文用于多轮一致性

### 3. 架构推断 (多源收敛)

```
阶段 1: 自回归 Transformer 生成离散视觉 token 序列
         ├─ 编码全局构图、语义布局、空间关系
         └─ 32K token 上下文 >> CLIP 77 tokens / T5 512 tokens

阶段 2: Diffusion Head 精炼
         ├─ 视觉 token → 高保真像素
         └─ 可能基于 Imagen 4 变体
```

### 4. 基座

- Sparse Mixture-of-Experts (MoE) Transformer
- Grouped-Query Attention (GQA)
- Gemini 2.5 Technical Report (arxiv:2507.06261) 确认 MoE

## Google 前置研究谱系

```
Parti (2022, AR, 20B)
  ├─ 序列到序列 text→image
  ├─ ViT-VQGAN 图像 tokenizer
  └─ FID 7.23 MS-COCO
         ↓
Muse (2023, Masked Generation)
  ├─ 掩码建模 (比 AR 更高效)
  └─ 预训练 LLM 文本嵌入
         ↓
Imagen 3 (2024, Diffusion)
  ├─ 级联扩散 64→256→1024
  └─ T5-XXL 文本编码
         ↓
Gemini Native Image (2025)
  = AR Transformer (Gemini LLM) + Diffusion Head (Imagen 衍生)
         ↓
NB1 → NB Pro → NB2
```

## 未知的核心细节

1. **视觉 Tokenizer**: 使用什么 VQ/VAE? 词汇量多大? (Parti 用 ViT-VQGAN 8192 词汇)
2. **Diffusion Head 架构**: 是 U-Net? DiT? 几步去噪?
3. **Shared Latent Intent Vector**: 具体维度? 如何在 LLM 和 Diffusion Head 之间传递?
4. **Review 的实现**: 是第二次前向推理? 还是 LLM 层面的 CoT?
5. **训练数据**: 包含哪些文化/艺术数据?
6. **MoE 专家数量和激活比例**

## 关键参考 URL

### 官方
- Google AI Docs: https://ai.google.dev/gemini-api/docs/image-generation
- Gemini Thinking: https://ai.google.dev/gemini-api/docs/thinking
- Gemini 2.5 Tech Report: https://arxiv.org/html/2507.06261v1

### 第三方分析
- Max Woolf NB Prompts: https://minimaxir.com/2025/11/nano-banana-prompts/
- Max Woolf NB Pro: https://minimaxir.com/2025/12/nano-banana-pro/
- Apiyi NB Pro Thinking: https://help.apiyi.com/en/nano-banana-pro-api-temporary-images-thinking-process-explained-en.html
- Apiyi NB2 Findings: https://help.apiyi.com/en/nano-banana-2-released-gemini-3-1-flash-image-en.html
- Latent Space NB2: https://www.latent.space/p/ainews-nano-banana-2-aka-gemini-31

### 前置研究
- Parti: https://arxiv.org/abs/2206.10789
- Muse: https://muse-model.github.io/
- UniFluid: https://arxiv.org/abs/2503.13436
- Unified Multimodal Survey: https://arxiv.org/html/2505.02567v1
