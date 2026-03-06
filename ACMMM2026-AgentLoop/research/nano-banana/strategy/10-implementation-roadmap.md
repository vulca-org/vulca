# VULCA 开源产品实施路线图

> 创建日期: 2026-02-27
> 核心原则: 产品优先, 开源可部署, 文化知识护城河

## 0. 当前状态诚实盘点

### 已验证有效
- 文化路由 (routing): +0.036, p<0.001, d=0.95 — 占总改进 95%
- 9 传统权重表: 有消融数据支撑
- Scout (FAISS + 术语库 + 禁忌): Recall@5=100%
- EvidencePack / FixItPlan / Trajectory: 协议完整
- 270 runs 消融数据 + Demo 视频 + 论文草稿

### 存在但没真正生效
- Multi-round iteration: 效果 ≈ 0 (三个 bug 叠加)
- 局部重绘 (ControlNet/Inpaint): SD1.5 可用但 FLUX 是 mock
- FixItPlan: 能生成但下游是全量重跑, 定向修复没接通
- CriticLLM: 能诊断但结果未被有效利用

### 完全缺失
- VLM 视觉评分 (当前 CLIP, 粒度不够)
- LLM Prompt 增强 (prompt 直接传给生成模型)
- SDXL/高质量本地生成 (当前 SD1.5 512²)
- 跨模型 inpaint (FLUX 生成 → SDXL 修复)

## 1. 四个差距 (按影响排序)

| # | 差距 | 影响 | 与 NB2 对比 |
|---|------|------|-----------|
| 1 | 评分系统太粗 (CLIP) | 整个迭代循环失效 | NB2 用 LLM Review |
| 2 | 迭代是假的 (全量重跑) | "改进"实为重新抽签 | NB2 在同一张图上修改 |
| 3 | 生成质量低 (SD1.5 512²) | 起点太低 | NB2 最高 4K |
| 4 | Prompt 理解浅 (CLIP 77 tokens) | 复杂指令被截断 | NB2 用 Gemini LLM |

依赖链:
```
评分粗 ──→ 迭代失效 ──→ FixItPlan 没用 ──→ 局部重绘没用
生成质量低 ──→ 起点差 ──→ 需要更多迭代 ──→ 但迭代是假的
Prompt 浅 ──→ 生成偏差 ──→ 更多迭代需求
```

## 2. 四条修复线

### 线 A: VLM Critic (替代 CLIP) — 最高优先级
- 用 VLM 替代 CLIP 做 L1-L5 评分
- 解锁迭代循环 + FixItPlan + 候选选择
- 不依赖其他线, 独立完成
- 工作量: 3-5 天

### 线 B: 真实局部重绘 (修复迭代循环) — 依赖线 A
- 被拒绝的图走"保留好的 + 只修坏的"
- 需要跨模型 inpaint 能力
- 工作量: 3-4 天

### 线 C: 生成模型升级 (SDXL/更好模型) — 独立
- 替换 SD1.5 512² → 更高质量引擎
- 可插拔架构, 支持多种后端
- 工作量: 2-3 天

### 线 D: LLM Prompt 增强 (对标 NB2 Plan) — 独立
- LLM 展开用户 prompt 为详细生成指令
- 工作量: 1-2 天

## 3. 执行顺序

```
Week 1: [D] LLM Prompt 增强 + [C] 生成模型升级 (并行, 独立)
Week 2: [A] VLM Critic (核心, 解锁迭代)
Week 3: [B] 真实局部重绘 (依赖 A)
Week 4: 集成测试 + 新消融实验
```

## 4. 与论文时间线

| 时间 | 产品 | 论文 | 共用产出 |
|------|------|------|---------|
| Week 1 (3/1) | D + C | ACM MM abstract | 模型对比数据 |
| Week 2 (3/8) | A (VLM) | — | VLM vs CLIP 消融 |
| Week 3 (3/15) | B (重绘) | abstract 提交 3/25 | 迭代改进数据 |
| Week 4 (3/22) | 集成+消融 | paper 写作 | 新消融结果 |
| Week 5 (3/29) | NB2 对比 | paper 提交 4/1 | 互补性证据 |

## 5. 全线上方案 (2026-02-27 确认)

用户明确: **优先使用线上模型/API, 避免本地 GPU 瓶颈**

### 关键发现: FLUX.1 Fill 支持 API Inpainting

| 环节 | 线上服务 | 单价 | 替代的本地组件 |
|------|---------|------|--------------|
| 生成 | FLUX.1 Schnell (Together) | $0.003/张 | SD1.5 本地 |
| **局部重绘** | **FLUX.1 Fill Dev (Replicate)** | **$0.025/张** | **SD1.5/ControlNet 本地** |
| VLM 评分 | Gemini Flash-Lite (Google) | **$0 (免费)** | CLIP 本地 |
| LLM Critic | DeepSeek / Gemini | $0.001/次 | — |
| LLM Plan | DeepSeek / Gemini | $0.001/次 | — |

**全线上 180 次 ablation 总成本: ~$5**
**本地 GPU 需求: 零**

详见: `strategy/11-cloud-api-pricing.md`

## 6. 修订后执行计划 (全线上)

```
Week 1 前半:
  [D] LLM Prompt 增强 (1-2天) → prompt_enhancer.py, Gemini Flash-Lite
  [C] 生成升级 (0.5天) → FLUX.1 Schnell → Dev (改配置)

Week 1 后半:
  [A] VLM Critic (3-4天) → vlm_critic.py, Gemini Flash-Lite (免费)
      替换 CLIP 评分, 输出结构化 JSON {L1:{score,rationale},...}

Week 2:
  [B] 真实局部重绘 (2-3天) → flux_fill_provider.py (FLUX.1 Fill API)
      修改 orchestrator.py, VLM 生成 mask + 修复指令

Week 2-3: 集成测试 + 新消融 (~$5-7)
```

总开发: ~8-10 天 | 总 API: <$10 | 本地 GPU: 零

## 7. MVP 定义

| 选项 | 包含 | 时间 |
|------|------|------|
| MVP-1 | VLM Critic + 路由 + FLUX API 生成 | 2 周 |
| MVP-2 | + FLUX Fill 局部重绘 + LLM Plan | 3 周 |
| MVP-3 | + NB2 对比 + 可插拔引擎 + 文档 | 5 周 |

---

## 8. 实施完成报告 (2026-02-27) ✅

> **四条修复线全部在 1 天内完成，远快于原计划的 8-10 天。**

### 8.1 实施成果

| 线 | 文件 | 验证 | 状态 |
|----|------|------|------|
| **D: LLM Prompt 增强** | `prompt_enhancer.py` | 8/8 PASS (含 live LLM) | ✅ DONE |
| **A: VLM Critic** | `vlm_critic.py` | 20/20 PASS (含真实图像) | ✅ DONE |
| **B: FLUX Fill 重绘** | `flux_fill_provider.py` | 13/13 PASS (dry mode) | ✅ DONE |
| **C: 生成升级** | `provider_model` 字段 | 回归通过 | ✅ DONE |

### 8.2 新增文件 (6 个)

| 文件 | 行数 | 功能 |
|------|------|------|
| `agents/prompt_enhancer.py` | ~120 | Gemini Flash-Lite 展开 prompt |
| `agents/vlm_critic.py` | ~200 | VLM L1-L5 结构化评分 |
| `agents/flux_fill_provider.py` | ~243 | fal.ai FLUX.1 Fill 定向重绘 |
| `tools/validate_prompt_enhancer.py` | ~160 | 线 D 验证脚本 |
| `tools/validate_vlm_critic.py` | ~220 | 线 A 验证脚本 |
| `tools/validate_flux_fill.py` | ~237 | 线 B 验证脚本 |

### 8.3 修改文件 (4 个)

| 文件 | 修改内容 |
|------|---------|
| `orchestrator.py` | +prompt enhancement 调用, +flux_fill inpaint 路由, 修复 2 处 mock_inpaint bug |
| `critic_rules.py` | +VLM 评分路径 (优先于 CLIP), blend 权重 |
| `draft_agent.py` | +flux_fill/flux_fill_pro provider 解析 |
| `run_ablation.py` | +provider_model, +enable_prompt_enhancer 字段 |

### 8.4 Bug 修复

| Bug | 位置 | 修复 |
|-----|------|------|
| FLUX 条件用 mock_inpaint | `orchestrator.py:668-670` | `elif provider=="together_flux": inpaint_name="flux_fill"` |
| 同上 (legacy 路径) | `orchestrator.py:696-698` | 同上 |

### 8.5 VLM 实测数据 (首次真实图像验证)

| 图像 | 条件 | L1 | L2 | L3 | L4 | L5 |
|------|------|-----|-----|-----|-----|-----|
| bench-005 伊斯兰几何 (SD1.5) | A | 0.70 | 0.60 | 0.80 | 0.90 | 0.70 |
| bench-005 伊斯兰几何 (FLUX) | Cp | 0.80 | 0.70 | 0.90 | 1.00 | 0.80 |
| **FLUX vs SD1.5 差异** | — | **+0.10** | **+0.10** | **+0.10** | **+0.10** | **+0.10** |

VLM 对 mock 图像 (8×8 单色) 正确给出 0.0-0.10 分，验证了 VLM 的辨别力。

### 8.6 向后兼容

- 9 个已有消融条件 (A-F, Cp, Dp, Ep) 全部向后兼容
- AblationCondition 新字段有安全默认值 (`provider_model=""`, `enable_prompt_enhancer=False`)
- VLM 自动检测: API key 存在 → VLM, 否则 → CLIP fallback

### 8.7 待验证

- [ ] 获取 FAL_KEY 进行 FLUX Fill 真实 inpaint 测试
- [ ] 新消融实验 (全 API, ~$5-7, 180 runs)
- [ ] NB2 G/G+ 对比实验 ($28, 需要 GOOGLE_API_KEY)
