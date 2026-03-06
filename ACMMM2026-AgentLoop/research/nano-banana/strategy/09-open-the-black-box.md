# 打开 NB2 黑盒：开源产品战略分析

> 核心问题：NB2 是黑盒 API，我们要做开源产品。能否倒推复现其核心能力？

## 0. 结论先行

**可以。** NB2 的五阶段管线可以用 100% 开源组件拼装复现，且我们有一个 NB2 永远无法获得的护城河：**显式文化知识系统**。

但这不是"复制 NB2"——而是**超越 NB2**。

---

## 1. NB2 的黑盒拆解

NB2 内部做了 5 件事，每件事都有开源替代：

```
NB2 黑盒:                         开源替代:
─────────────────                  ──────────────────────
① Plan (LLM 解析 prompt)          → 任何开源 LLM (Qwen2.5/LLaMA3)
② Generate (GemPix 2 Diffusion)   → Show-o2 / Janus-Pro / FLUX
③ Review (内部自检)               → VLM (Qwen2.5-VL / InternVL3.5)
④ Correct (定向修复)              → Inpainting (SD1.5/ControlNet)
⑤ Output                          → 直接输出
```

### 每个阶段的开源选项

#### ① Plan → 开源 LLM

NB2 的 Plan 用 Gemini 3.1 Flash LLM 内核解析 prompt，规划构图。

**开源替代**:
- Qwen2.5-72B / LLaMA-3.1-70B / DeepSeek-V3 (任选)
- 甚至 7B 级别在 prompt 解析上就足够
- **我们的优势**: Plan 阶段注入 EvidencePack (FAISS 检索的术语、禁忌、范例)
- NB2 的 Plan 只有训练数据里的隐式知识；我们的 Plan 有显式文化知识

#### ② Generate → 开源生成模型

NB2 用 GemPix 2 (AR tokens → Diffusion Head) 生成图像。

**开源替代 (三个层次)**:

| 层次 | 模型 | 接近 NB2 程度 | 可行性 |
|------|------|-------------|--------|
| **最接近** | Show-o2-7B | AR+Flow Matching 混合 = NB 同架构 | ✅ 权重可用, 7B 可在 RTX 2070 跑 |
| **次接近** | Janus-Pro-7B | 统一 AR 理解+生成 | ✅ MIT 协议, 17.7k stars |
| **最实用** | FLUX.1-dev + ControlNet | Flow Matching, 成熟生态 | ✅ 已在 VULCA 验证 |

**关键发现**: **Show-o2** 是最接近 NB2 架构的开源实现——同一 Transformer 内混合使用 AR (文本) 和 Flow Matching (图像)。

#### ③ Review → 开源 VLM

NB2 的 Review 用内部机制检查生成结果（最多 2 张中间图像）。

**开源替代**:
- Qwen2.5-VL-7B (Apache-2.0, 性价比最高)
- InternVL3.5-8B (Apache-2.0, 强推理)
- **我们的优势**: VLM Review 不只检查 prompt 一致性 (NB2 做的事),
  还检查 L3-L5 文化合规性 (NB2 做不到的事)

#### ④ Correct → 开源 Inpainting

NB2 的 Correct 是全局重新生成（没有局部修复能力）。

**开源替代**:
- SD1.5 Inpainting (已验证, 3.8s/张)
- ControlNet Canny/Depth (已验证, 定向修复)
- IP-Adapter (风格迁移)
- **我们的优势**: FixItPlan → MaskGenerator → 定向局部修复
  NB2 只能全局重来；我们可以只修"左上角的禁忌元素"

---

## 2. 不止复现——超越 NB2

### 2.1 NB2 的 5 个结构性缺陷

| # | NB2 缺陷 | 我们的解决方案 |
|---|---------|-------------|
| 1 | **无显式文化知识** — Review 只检查 prompt 一致性 | Scout + FAISS + 术语库 + 禁忌检测 |
| 2 | **不可审计** — 黑盒, thinking 加密 | Trajectory 全链路追溯 + Langfuse 监控 |
| 3 | **不可定制** — 固定 thinking 逻辑 | 9 传统权重表 + 可插拔 pipeline variants |
| 4 | **无局部修复** — 只能全局重新生成 | ControlNet + MaskGenerator 定向修复 |
| 5 | **API 锁定** — 依赖 Google, 不可部署 | 100% 开源, 可本地/私有云部署 |

### 2.2 产品定位差异

```
NB2 (Google):
  "我给你一个更好的画笔"
  → 更好的 L1-L2 (视觉质量)
  → 但仍然是你自己画, 画错了自己承担

VULCA (开源):
  "我给你一个懂文化的艺术顾问团队"
  → 知道每个文化传统的规则 (L3)
  → 知道艺术史上下文 (L4)
  → 知道哲学美学标准 (L5)
  → 还能帮你局部修改而不是推倒重来
```

---

## 3. 具体技术路线

### 路线 A: "开源 NB2" — 用 Show-o2 复现 AR+Diffusion

```
Show-o2-7B (AR+Flow Matching)
    ↓
Plan: Qwen2.5-7B 解析 prompt + 注入 EvidencePack
    ↓
Generate: Show-o2 生成 (AR tokens → Flow Matching 渲染)
    ↓
Review: Qwen2.5-VL-7B 视觉审查 (L1-L2) + VULCA Critic (L3-L5)
    ↓
Correct: ControlNet Inpainting (定向修复)
    ↓
Output: 带完整 Trajectory 审计链
```

**优势**: 架构上最接近 NB2, 学术故事最强 ("开源复现+超越")
**风险**: Show-o2-7B 的生成质量可能不如 NB2 (Google 的训练数据量级不可比)
**硬件**: RTX 2070 8GB 可跑 7B, 但可能需要量化

### 路线 B: "实用组合" — FLUX + VLM Review Loop

```
FLUX.1-dev (Flow Matching, 成熟稳定)
    ↓
Plan: Qwen2.5-7B + EvidencePack
    ↓
Generate: FLUX.1-dev (本地) 或 FLUX.1-schnell (API, $0.003/张)
    ↓
Review: Qwen2.5-VL-7B (VLM 审查, 替代 CLIP)
    ↓
Correct: ControlNet Inpainting
    ↓
Output: 带 Trajectory
```

**优势**: 最实用, FLUX 生态成熟, 已在 VULCA 验证
**劣势**: 不是 "AR+Diffusion 混合" (学术新颖性较弱)
**关键升级**: VLM 替代 CLIP 做 Review → 解决当前 ablation 中发现的 CLIP 评分精度瓶颈

### 路线 C: "Janus 统一" — 一个模型理解+生成

```
Janus-Pro-7B (统一 AR 模型, MIT 协议)
    ↓
同一个模型做:
  1. 理解 prompt + EvidencePack → 规划
  2. 生成图像
  3. 理解自己生成的图像 → 自审查
  4. 基于审查结果 → 修改 prompt → 重新生成
    ↓
外层: VULCA Critic (L3-L5 文化审查)
    ↓
Output
```

**优势**: 最优雅, 单模型闭环 (像 NB2 一样), MIT 商用友好
**劣势**: Janus-Pro 的图像质量可能不如专用生成模型
**创新点**: "理解自己作品的 AI 画家" — 与 NB2 的 Review 机制最相似

---

## 4. VLM 替代 CLIP — 解决核心瓶颈

这是**最重要的产品升级**。当前 VULCA 的 Critic 用 CLIP 评分，ablation 证明精度不够 (±0.01-0.02)。

### 当前 (CLIP-based Critic)
```
图像 → CLIP 编码 → 与参考向量余弦相似度 → 0.0-1.0 分数
问题: 粒度太粗, "改了一笔" 和 "没改" 的分数差 < 0.02
```

### 升级 (VLM-based Critic)
```
图像 + L1-L5 评估 prompt → Qwen2.5-VL-7B → 结构化 JSON 评分
{
  "L1_visual": {"score": 0.82, "rationale": "构图对称但略显呆板"},
  "L2_technical": {"score": 0.91, "rationale": "笔触流畅, 墨色层次丰富"},
  "L3_cultural": {"score": 0.45, "rationale": "出现了写意画中不应有的西方透视"},
  "L5_philosophical": {"score": 0.33, "rationale": "缺乏留白的哲学深度"}
}
```

**这直接解决了 ablation 发现的两个问题**:
1. CLIP 精度不够 → VLM 可以给出细粒度评分 + 自然语言理由
2. Multi-round iteration 无效 → 因为 CLIP 无法区分改进; VLM 可以

**成本**: Qwen2.5-VL-7B 本地推理 = $0 (RTX 2070 可跑)

---

## 5. 产品护城河分析

### 5.1 NB2 不可能做到的事

| 能力 | 为什么 NB2 做不到 |
|------|------------------|
| 检测伊斯兰 aniconism 禁忌 | 训练数据无结构化禁令 |
| 区分写意 vs 工笔的技法标准 | 无 L2 传统专属权重 |
| 理解 "留白" 是哲学而非空白 | 训练数据中 "empty space" ≠ "philosophical void" |
| 为非洲 Adinkra 符号提供正确上下文 | 稀疏训练数据 |
| 给出可审计的多维度评分报告 | 黑盒, 只有最终图像 |
| 用户自定义评估标准和权重 | API 固定行为 |

### 5.2 开源产品的独特卖点

1. **文化可审计性**: 每个决策都有 Trajectory 记录, 可回溯为什么选了这张图
2. **可定制权重**: 客户可以说 "我的日本侘寂项目, L5 权重要 0.40"
3. **私有部署**: 博物馆/画廊不想把艺术品发到 Google API
4. **域内知识扩展**: 添加新的文化传统 = 添加一张权重表 + 术语文件
5. **局部修复**: "只改这个角落的禁忌符号" 而不是整张图重画

---

## 6. 执行优先级

### Phase 1 (立即可做, 1-2 周): VLM Critic 升级
- 用 Qwen2.5-VL-7B 替代 CLIP 做 L1-L5 评分
- 这一步直接解决 ablation 发现的 CLIP 瓶颈
- 硬件: RTX 2070 可跑 (4-bit 量化)
- 代码量: 新建 `vlm_critic.py`, 修改 `critic_rules.py`

### Phase 2 (2-4 周): 开源生成引擎集成
- 评估 Show-o2 / Janus-Pro / FLUX.1-dev 作为本地生成引擎
- 建立统一的 `DraftProvider` 接口适配
- 对比实验: 开源引擎 vs NB2 API

### Phase 3 (4-6 周): 完整开源管线
- Plan (Qwen2.5) → Generate (Show-o2/FLUX) → Review (VLM) → Correct (ControlNet) → Output
- 100% 本地运行, 无 API 依赖
- 文化路由 + FixItPlan + Trajectory 全链路

---

## 7. 与论文的关系

这个开源产品路线不与论文冲突, 反而互相增强:

- **ACM MM 论文**: 用 NB2 API 做对比实验 (G/G+ 条件), 证明 routing 在 NB2 上也有效
- **开源产品**: 用 Show-o2 + VLM 构建完全开源版, 不依赖任何 API
- **EMNLP 论文**: 加入 VLM Critic 的 ablation, 证明 VLM > CLIP 评分

三者可以并行推进。

---

## 8. 图像生成质量控制策略 (2026-02-27)

### 8.1 NB2 图像质量的 4 层来源

1. **训练数据** (最难复现): Google 数十亿级高质量图文对 vs 开源 LAION-5B 噪声数据
2. **Prompt 理解深度** (可追平): Gemini LLM 32K tokens 理解 vs CLIP 77 tokens; 我们用 LLM Prompt 增强
3. **内部迭代** (可超越): NB2 内部 3 次尝试; 我们 4+ 候选 + VLM 文化选择
4. **AR+Diffusion 架构** (Show-o2 部分复现): 先规划结构再填充细节

### 8.2 质量控制 4 层策略

```
Layer 0 (基础): 升级生成模型 (SD1.5 → SDXL/FLUX.1-dev)
Layer 1 (Plan): LLM 增强 prompt (Qwen2.5 + EvidencePack)
Layer 2 (Select): 多候选 + VLM 评分选择
Layer 3 (Fix): ControlNet/IP-Adapter 定向修复
```

### 8.3 关键认知

- **最终输出质量 = 基础生成质量 × 选择质量 × 修复质量**
- NB2 靠基础生成质量高取胜; 我们靠选择+修复弥补基础差距
- 图片质量 = 像素精度 × 语义正确性 × 文化合规性; NB2 只有前两项, 我们三项都有
- LLM Prompt 增强 (DALL-E 3 验证): FID 提升 20-30%, 不改模型本身

### 8.4 基础模型质量对比

| 模型 | 分辨率 | 质量 | VRAM | 成本 | 备注 |
|------|--------|------|------|------|------|
| SD1.5 | 512² | ⭐⭐ | 2GB | $0 | 当前 VULCA 使用 |
| SDXL | 1024² | ⭐⭐⭐½ | 8GB | $0 | RTX 2070 可跑 |
| FLUX.1-schnell | 1024² | ⭐⭐⭐ | API | $0.003 | 快但质量有限 |
| FLUX.1-dev | 1024² | ⭐⭐⭐⭐ | 24GB | $0 | 需要更大 GPU |
| SD3-Medium | 1024² | ⭐⭐⭐⭐ | 10GB | $0 | 需量化 |
| NB2 API | 4096² | ⭐⭐⭐⭐⭐ | N/A | $0.067 | 黑盒 API |

### 8.5 核心问题: SDXL 能否达到 NB2 质量?

**诚实答案: 单张直出不能。但通过 4 层策略叠加后有竞争力。**
- SDXL 单张 vs NB2 单张: 差距明显 (训练数据量级差)
- SDXL + LLM Plan + 4候选VLM选择 + 定向修复 vs NB2 单张: 可竞争
- 在文化合规性维度: 必然超越 NB2 (NB2 无文化知识系统)

**需要实验验证的核心假设**:
- SDXL + 完整 VULCA 管线 的 L1-L5 总分 是否 ≥ NB2 单张的 L1-L5 总分
- 预期: L1-L2 可能略低, L3-L5 显著更高, 加权总分有竞争力

### 8.6 产品策略结论 (2026-02-27 讨论)

**SDXL 单张 ≠ NB2 单张 (像素质量差距来自训练数据规模)**

但: SDXL + 完整 VULCA 管线 ≈ NB2 单张 (L3-L5 补偿 L1-L2)

正确的产品策略:
1. **生成引擎可插拔** — 不绑定任何一个模型, 让用户选择
2. **护城河在文化知识系统** — 术语库/禁忌表/权重矩阵/Trajectory 审计
3. 基础生成质量随开源模型进步自动提升 (每 6-12 月一代)
4. 投入重点: VLM Critic > LLM Prompt 增强 > 风格化 LoRA > 引擎可插拔

实际预期加权总分:
- NB2 单张 (无路由): ~0.84
- SDXL + VULCA 管线: ~0.85 (L3-L5 补偿)
- NB2 + VULCA 管线: ~0.89 (理论最优, 但 API 依赖)

### 8.7 待确认: 局部重绘是否生效?

核心疑问: Agent 被拒绝后是全量重跑 (one-shot) 还是真的在做局部重绘?
需要检查 orchestrator.py 的 rerun_local vs rerun 路径实际执行情况。
### §9 代码审计结论 (2026-02-27)

**结论: FLUX 条件下局部重绘是假的，multi-round 实际是全量重跑。**

三个叠加 bug:

1. **FLUX 用 mock_inpaint**: `orchestrator.py:655-657`, `rerun_local` 只在
   `provider=="diffusers"` (SD1.5) 时用真实 inpaint; FLUX (`together_flux`) 走
   `mock_inpaint` — 只做随机颜色涂抹, 不是真正修复

2. **全局 rerun = 完全从零**: `orchestrator.py:724-731`, 全局 rerun 只是把
   `fix_it_plan.to_prompt_delta()` 追加到 prompt, 然后 Draft 从零生成 4 张全新图;
   上一轮的好构图/好色彩/好笔触全部丢失

3. **CLIP 评分精度不够**: ±0.01-0.02 的粒度无法区分 "改了" 和 "没改"

这解释了 ablation 中 multi-round 效果极弱 (+0.002, ns) 的真实原因。

触发条件分析:
- 9 条件中只有 B/D/Dp 能触发 rerun_local (需要 enable_agent_critic=True + max_rounds>1)
- B (SD1.5): provider=diffusers → 真实 inpaint ✅ (但 SD1.5 质量本身低)
- D/Dp (FLUX): provider=together_flux → mock_inpaint ❌ (假的!)

修复方向:
- 修复 1: FLUX 初始生成 + SDXL Inpaint 局部修复 (两模型各司其职)
- 修复 2: VLM Critic 提供精确修复指令 (替代模糊的 "improve L5")
- 修复 3: VLM 评分替代 CLIP (足够粒度驱动迭代改进)

### §9.1 修复完成状态 (2026-02-27) ✅

**三个叠加 bug 已全部修复:**

| Bug | 修复方案 | 文件 | 验证 |
|-----|---------|------|------|
| ① FLUX 用 mock_inpaint | **线 B**: `flux_fill_provider.py` + orchestrator 路由修复 | `orchestrator.py:668,698` | 13/13 ✅ |
| ② 全局 rerun = 从零 | **线 B**: FLUX Fill mask-based 定向重绘 | `flux_fill_provider.py` | 13/13 ✅ |
| ③ CLIP 精度不够 | **线 A**: VLM L1-L5 结构化评分替代 CLIP | `vlm_critic.py` + `critic_rules.py` | 20/20 ✅ |

**额外修复:**
- **线 D**: `prompt_enhancer.py` — LLM 展开 prompt, 注入文化术语 (8/8 ✅)
- **线 C**: `provider_model` 字段支持 FLUX.1 Dev 升级 (回归通过)

**VLM 首次真实图像验证** (Gemini Flash-Lite):
- SD1.5 伊斯兰几何: L1=0.70, L2=0.60, L3=0.80, L4=0.90, L5=0.70
- FLUX 伊斯兰几何: L1=0.80, L2=0.70, L3=0.90, L4=1.00, L5=0.80
- 对 8×8 mock 图像正确给出 0.0-0.10 分 (有效辨别力确认)

**关键结论**: 修复前 multi-round 效果为 +0.002 (ns); 修复后预期 multi-round 可产生有意义改进 (待新消融验证)。

---

## 10. 实施后产品定位修订 (2026-02-27)

修复前后的产品能力变化:

```
修复前 (2026-02-27 AM):
  Generate: FLUX Schnell (API) / SD1.5 (本地)
  Critic:   CLIP (粗粒度, ±0.02)
  Inpaint:  mock_inpaint (假的)
  Plan:     原始 prompt 直传
  → Multi-round = 4次全量随机重跑, 与 1 次无显著差异

修复后 (2026-02-27 PM):
  Generate: FLUX Dev/Schnell (可切换)
  Critic:   VLM L1-L5 (细粒度, 结构化理由)  [CLIP fallback]
  Inpaint:  FLUX.1 Fill (真实 mask 重绘)   [mock fallback]
  Plan:     LLM 增强 prompt + 文化术语注入
  → Multi-round = 每轮 VLM 精确诊断 + 定向区域修复 (理论可行, 待验证)
```

**对照 NB2 五阶段**:
| NB2 阶段 | 修复前 VULCA | 修复后 VULCA | 差距变化 |
|----------|-------------|-------------|---------|
| ① Plan | 无 | LLM + EvidencePack | **从缺失到持平/超越** |
| ② Generate | FLUX Schnell | FLUX Dev 可选 | 缩小 |
| ③ Review | CLIP (粗) | VLM L1-L5 (细) | **从劣势到超越** |
| ④ Correct | mock (假) | FLUX Fill (真) | **从无到有** |
| ⑤ Output | 同 | 同 | 不变 |
