# Generation-Side vs Evaluation-Side Self-Correction: 完整分析

## 1. 范式定义

### Generation-Side Self-Correction（生成侧）

**定义**：在图像生成模型 **内部** 集成自我审查和修复机制。

**代表**：
- Nano Banana 2 (Plan→Review→Correct loop)
- Nano Banana Pro (Deep Inference thinking)
- 未来可能的 DALL-E 4+ (如果采用类似机制)

**特点**：
- 使用 **训练数据中的隐式知识** 进行验证
- 纠正发生在 **latent space** 或 **token generation** 过程中
- 不依赖外部知识源
- 速度快（集成在生成过程中）
- **局限**：只能纠正模型 "已学过" 的东西

### Evaluation-Side Self-Correction（评估侧）

**定义**：在生成模型 **外部** 搭建独立的评估和决策管线。

**代表**：
- VULCA-Agent (Scout→Draft→Critic→Queen)
- RPG-DiffusionMaster (LLM decompose + diffusion)
- Self-Refine (Madaan et al. 2024, LLM text domain)

**特点**：
- 使用 **外部知识库** 进行评估（术语、禁忌、范例）
- 纠正发生在 **模型外部**（修改 prompt、触发重生成）
- 可审计、可解释
- 速度较慢（额外的检索+评估开销）
- **优势**：可以纠正模型 "没学过" 的东西（通过外部知识注入）

---

## 2. 维度覆盖分析

### L1 Visual Perception (视觉感知)

| 能力 | Gen-Side (NB2) | Eval-Side (VULCA) |
|------|---------------|-------------------|
| 构图合理性 | ✅ Plan 阶段规划 | ⚠️ 规则评分有限 |
| 色彩一致性 | ✅ Diffusion 过程保证 | ⚠️ 规则评分有限 |
| 空间关系 | ✅ Review 阶段验证 | ❌ 不做空间分析 |
| 物体完整性 | ✅ Review 检查 | ❌ 不做物体检测 |

**结论**：Gen-Side 在 L1 上 **显著优于** Eval-Side。

### L2 Technical Analysis (技法分析)

| 能力 | Gen-Side (NB2) | Eval-Side (VULCA) |
|------|---------------|-------------------|
| 文字渲染 | ✅ 94% 准确率 | ❌ 不评估文字 |
| 笔触质感 | ⚠️ 依赖训练数据 | ⚠️ 规则评分 |
| 媒介特征 | ⚠️ 隐式学习 | ✅ 术语匹配 |
| 采样参数 | N/A (API) | ✅ 规则评分 |

**结论**：混合。NB2 在视觉技法上更强，VULCA 在领域特定技法术语上更强。

### L3 Cultural Context (文化语境)

| 能力 | Gen-Side (NB2) | Eval-Side (VULCA) |
|------|---------------|-------------------|
| 传统约定遵守 | ❌ 无结构化文化知识 | ✅ 9 传统权重表 |
| 符号体系正确性 | ❌ 隐式统计共现 | ✅ 术语库 + 语义搜索 |
| 禁忌避免 | ❌ 无禁忌列表 | ✅ 显式禁忌检测 |
| 文化合规评分 | ❌ | ✅ L3 LLM 评估 |

**结论**：Eval-Side **显著优于** Gen-Side。NB2 的 Review 不包含文化规则。

### L4 Critical Interpretation (批判解读)

| 能力 | Gen-Side (NB2) | Eval-Side (VULCA) |
|------|---------------|-------------------|
| 艺术史定位 | ❌ | ✅ LLM + 范例检索 |
| 传统演进理解 | ❌ | ⚠️ 有限 |
| 跨传统对比 | ❌ | ⚠️ 有限 |

**结论**：Eval-Side 优于 Gen-Side（但两者都有局限）。

### L5 Philosophical Aesthetics (哲学美学)

| 能力 | Gen-Side (NB2) | Eval-Side (VULCA) |
|------|---------------|-------------------|
| 侘寂 (wabi-sabi) | ❌ 无法量化 | ⚠️ LLM 评估 |
| 意笔 (yibi) | ❌ 训练数据稀疏 | ✅ 术语 + L5 权重放大 |
| 崇高 (sublime) | ❌ | ⚠️ LLM 评估 |
| 留白 (liu bai) | ❌ 可能填满空白 | ✅ 术语 + 构图约束 |

**结论**：Eval-Side 在 L5 上有结构性优势，但两者都面临哲学概念量化的根本挑战。

---

## 3. 互补性证据

### 已有实验数据（VULCA v1+v2, FLUX baseline）

| 维度 | C (FLUX baseline) | C→C+ Δ (routing) | 解读 |
|------|--------------------|-------------------|------|
| L1 | 0.821 | -0.007 | routing 对 L1 略有负面 |
| L2 | 0.773 | -0.002 | routing 对 L2 基本无影响 |
| L3 | 0.816 | **+0.067** | routing 显著提升文化 |
| L4 | 0.933 | 0.000 | L4 已经很高 |
| L5 | 0.705 | **+0.109** | routing 大幅提升哲学美学 |

### 预期 NB2 实验数据

| 维度 | G (NB2 baseline) | G→G+ Δ (routing) | 预期 |
|------|-------------------|-------------------|------|
| L1 | 预期 > C（NB2 更强） | ~0 或略负 | NB2 自纠正已优化 L1 |
| L2 | 预期 > C | ~0 或略负 | NB2 自纠正已优化 L2 |
| L3 | 预期 ≈ C（无文化知识） | **预期 +0.05~0.07** | routing 仍然有效 |
| L4 | 预期 ≈ C | **预期 +0.01~0.03** | routing 仍然有效 |
| L5 | 预期 ≈ C（无哲学知识） | **预期 +0.08~0.12** | routing 仍然有效 |

**关键预测**：NB2 的内部自纠正不会显著提升 L3-L5，因为这些层面的知识不在其训练数据中。

---

## 4. 理论框架

### 4.1 知识边界定理（我们的核心论点）

> **一个模型的自纠正能力受限于其训练数据中的知识边界。**
>
> 如果 K_train 是训练数据中的知识集，K_required 是正确评估所需的知识集，
> 则自纠正只能在 K_train ∩ K_required 上有效。
> 对于 K_required \ K_train（所需但未学习的知识），
> 必须通过外部知识注入才能实现纠正。

### 4.2 维度正交性

```
Gen-Side 优化空间:  {L1, L2} — 视觉保真度
Eval-Side 优化空间: {L3, L4, L5} — 文化认知深度

交集: {L2 中的领域特定技法} — 两者都可以改进但机制不同
互补: {L1 ∪ L5} — 几乎无重叠
```

### 4.3 成本-效果权衡

```
Gen-Side:  成本 ∈ [生成价格]，无额外 API 调用
Eval-Side: 成本 = 生成 + 检索 + LLM评估 + 可能的重生成

但：
Gen-Side:  L3-L5 收益 ≈ 0（无文化知识）
Eval-Side: L3-L5 收益 显著（有外部知识）

结论：Eval-Side 的额外成本换来了 Gen-Side 无法达到的文化质量提升
```

---

## 5. 对论文的影响

### 如果 NB2 实验验证了互补性

这将是论文最强的卖点之一：

1. **直接对标 Google DeepMind 最新技术** — NB2 刚发布，ACM MM 审稿人会很感兴趣
2. **清晰的互补性证据** — 同一组任务、同一评估标准、不同 Draft provider
3. **实践价值** — 告诉从业者："用 NB2 生成 + VULCA routing 评估 = 最优"
4. **理论贡献** — 知识边界定理解释了为什么两者互补

### 如果 NB2 实验不支持互补性

可能的原因：
- NB2 的训练数据实际包含了足够的文化知识（web-scale 数据可能覆盖部分）
- 我们的 L3-L5 评分机制不够精细（CLIP 瓶颈问题延续）
- 样本量不足

应对策略：
- 分析 per-tradition 结果（某些传统可能互补，某些不互补）
- 作为 future work 讨论

---

## 6. 相关工作补充

如果加入 NB2 实验，需要在 Related Work 中补充：

```latex
\paragraph{Generation-Side Self-Correction.}
Recent image generation models have begun incorporating internal
self-correction mechanisms. Nano Banana Pro~\cite{nanobanana2025}
introduced ``Deep Inference'' mode where the model reasons about
spatial relationships and composition before rendering.
Nano Banana 2~\cite{nanobanana2_2026} extends this with an explicit
Plan-Evaluate-Improve loop connected via a shared latent intent vector.
These generation-side approaches excel at visual quality (\Lx{1}--\Lx{2})
but lack access to external cultural knowledge required for
\Lx{3}--\Lx{5} evaluation, motivating our complementary
evaluation-side approach.
```
