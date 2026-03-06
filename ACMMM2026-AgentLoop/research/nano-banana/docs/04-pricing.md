# Nano Banana 定价 + 实验成本估算

## 1. 官方定价（2026-02-27 数据）

### NB2 (gemini-3.1-flash-image-preview)

| 分辨率 | 标准价格 | 批量价格 (半价) |
|--------|---------|---------------|
| 0.5K (512px) | $0.045 | $0.022 |
| **1K (1024px)** | **$0.067** | **$0.034** |
| 2K (2048px) | $0.101 | $0.050 |
| 4K (4096px) | $0.151 | $0.076 |

Token 定价：Input $0.25/1M, Text Output $1.50/1M, Image Output $60/1M

### NB Pro (gemini-3-pro-image-preview)

| 分辨率 | 标准价格 | 批量价格 |
|--------|---------|---------|
| 1K/2K | $0.134 | $0.067 |
| 4K | $0.240 | $0.120 |

Token 定价：Input $2.00/1M, Text Output $12/1M, Image Output $120/1M

### NB1 (gemini-2.5-flash-image)

| 分辨率 | 标准价格 | 批量价格 |
|--------|---------|---------|
| 1024px | $0.039 | $0.020 |

### 对比参考

| 模型 | 价格/张 | 速度 |
|------|---------|------|
| FLUX.1-schnell (Together.ai) | ~$0.003 | ~1s |
| Imagen 4 Fast | $0.020 | ~3s |
| Imagen 4 Standard | $0.040 | ~5s |
| NB1 | $0.039 | ~3s |
| **NB2 1K** | **$0.067** | **~5s** |
| NB Pro | $0.134 | ~10s |

### Web Grounding 额外费用
- 免费：5,000 prompts/month
- 超出后：$14/1,000 queries

---

## 2. VULCA-Agent 实验成本估算

### 场景 1：NB2 作为 Draft Provider (30 tasks)

假设：每 task 4 candidates × 1K 分辨率

| 条件 | Tasks | Candidates/task | 总图像 | 单价 | 总成本 |
|------|-------|----------------|--------|------|--------|
| G (NB2 baseline) | 30 | 4 | 120 | $0.067 | **$8.04** |
| G+ (NB2 + routing) | 30 | 4 | 120 | $0.067 | **$8.04** |
| **总计** | | | 240 | | **$16.08** |

加上 LLM Critic (Gemini Flash Lite) 和多轮（假设平均 2 轮）：
- 多轮图像生成：~240 × 0.7(rerun rate) = +168 images = +$11.26
- LLM Critic：~$0.50
- **总估算：~$28**

### 场景 2：NB2 + NB Pro 对比 (30 tasks each)

| 条件 | 图像数 | 单价 | 总成本 |
|------|--------|------|--------|
| NB2 baseline | 120 | $0.067 | $8.04 |
| NB2 + routing | 120 | $0.067 | $8.04 |
| NB Pro baseline | 120 | $0.134 | $16.08 |
| NB Pro + routing | 120 | $0.134 | $16.08 |
| **总计** | 480 | | **$48.24** |

### 场景 3：最小验证 (5 tasks)

| 条件 | 图像数 | 成本 |
|------|--------|------|
| NB2 baseline | 20 | $1.34 |
| NB2 + routing | 20 | $1.34 |
| **验证总计** | 40 | **$2.68** |

---

## 3. 与当前实验的成本对比

| 实验 | Runs | 成本 | 备注 |
|------|------|------|------|
| v1 Ablation (A-F) | 180 | ~$3 | FLUX ($0.003) + SD1.5 (free) |
| v2 Supplementary (Cp/Dp/Ep) | 90 | ~$5 | FLUX + Gemini Flash Lite |
| **NB2 新实验 (G/G+)** | **60** | **~$28** | NB2 ($0.067) 比 FLUX 贵 22x |

**结论**：NB2 成本显著高于 FLUX，但仍在可接受范围内（<$30 for full experiment）。如果用批量 API，可降至 ~$14。

---

## 4. API Key 获取

1. 访问 [Google AI Studio](https://aistudio.google.com/)
2. 创建 API Key
3. 设置环境变量：`GOOGLE_API_KEY=your-key`
4. 免费额度：2 RPM, 32K tokens/min（足够验证，不够批量实验）
5. 付费 tier：需绑定 Google Cloud Billing Account

---

## 5. 成本优化策略

1. **先用 0.5K 做快速验证**（$0.045 vs $0.067 for 1K）
2. **批量 API**：24 小时内完成，价格减半
3. **减少 candidates**：4→2 per task（成本减半，但可能降低最佳候选质量）
4. **选择性多轮**：只对 routing 后仍低分的 tasks 触发 rerun
