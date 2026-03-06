# VULCA-Agent vs Nano Banana 架构对比分析

## 1. 管线对齐

```
NB2 内部管线:                    VULCA-Agent 管线:
─────────────                   ──────────────────
① Plan                         Scout (证据检索)
   ├─ 解析 prompt                 ├─ FAISS 语义搜索
   ├─ 构图规划                    ├─ 术语查找
   ├─ 空间布局                    ├─ 禁忌检测
   └─ 技术约束                    └─ → EvidencePack
         │                              │
② Generate                      Draft (图像生成)
   └─ GemPix 2 Diffusion         └─ SD1.5 / FLUX / NB2(?)
         │                              │
③ Review                        Critic (L1-L5 评估)
   ├─ 文字正确性                   ├─ L1 Visual (Rule)
   ├─ 空间一致性                   ├─ L2 Technical (Rule)
   ├─ 构图逻辑                     ├─ L3 Cultural (LLM)
   └─ 技术约束达标                  ├─ L4 Critical (LLM)
         │                         └─ L5 Philosophical (LLM)
         │                              │
④ Correct                       Queen (决策)
   └─ 定向反馈 → ②                ├─ Accept / Rerun / Stop
                                  ├─ FixItPlan
         │                        └─ 跨维度保护
⑤ Output                        Archive (最终输出)
```

## 2. 知识来源对比

| 维度 | NB2 知识 | VULCA-Agent 知识 |
|------|---------|----------------|
| **来源** | 训练数据中的隐式统计共现 | 外部显式知识库 |
| **更新** | 需要重新训练 | 运行时可扩展（添加术语/范例/禁忌） |
| **范围** | 广泛但浅（web-scale 但无结构化文化知识） | 窄但深（9 传统 × L1-L5 × 术语/禁忌/范例） |
| **可审计** | ✗（黑盒） | ✅（EvidencePack 可检查） |
| **可解释** | 有限（thinking text） | ✅（逐层分数 + rationale） |

## 3. 自纠正能力对比

### NB2 能纠正的（L1-L2 层面）

| 问题类型 | NB2 Review 机制 | 示例 |
|---------|----------------|------|
| ✅ 文字拼写 | 逐字符比对 | "Logn" → "Login" |
| ✅ 空间布局 | 空间关系验证 | 人物 A 应在左侧 |
| ✅ 光照物理 | 物理一致性检查 | 阴影方向 vs 光源 |
| ✅ 解剖结构 | 逻辑验证 | 手指数量、关节方向 |
| ✅ 构图规则 | 三分法/黄金比例 | 主体居中偏移 |
| ✅ 镜面反射 | 空间推理 | 镜中元素翻转 |

### NB2 不能纠正的（L3-L5 层面）

| 问题类型 | 为什么不能 | VULCA-Agent 如何处理 |
|---------|-----------|-------------------|
| ❌ 伊斯兰 aniconism | 训练数据未编码禁令 | 禁忌检测 + Taboo_Override 信号 |
| ❌ 写意 yibi 原则 | 无法理解 "意在笔先" | 术语库 + L5 权重放大 (w=0.30) |
| ❌ 工笔工细程度 | 无 L2 技法评判标准 | L2 权重放大 (w=0.30) |
| ❌ 非洲符号体系 | 稀疏训练数据 | 文化术语库 + L3 权重放大 |
| ❌ 日本侘寂美学 | 无法量化 impermanence | L5 评估 + wabi-sabi 术语 |
| ❌ 跨层依赖 | 无 L1→L5 依赖链概念 | bottom-up 评估 + 跨层信号 |

## 4. 维度级别影响矩阵

```
                    NB2 自纠正         VULCA-Agent 路由
L1 Visual          ████████████ 强      ██░░░░░░░░░ 弱(-0.021)
L2 Technical       ████████████ 强      ██░░░░░░░░░ 弱(-0.008)
L3 Cultural        ██░░░░░░░░░ 弱      ██████████░ 强(+0.056)
L4 Critical        ██░░░░░░░░░ 弱      ████████░░░ 中(+0.030)
L5 Philosophical   █░░░░░░░░░░ 极弱    ████████████ 强(+0.134)
```

**互补性一目了然**：NB2 强在 L1-L2，VULCA 强在 L3-L5。

## 5. 集成方案分析

### 方案 A：NB2 作为 Draft Provider（推荐）

```
Scout → EvidencePack → Draft(NB2) → Critic(L1-L5) → Queen → Archive
                         ↑
                    NB2 内部已做 Plan→Review→Correct
                    我们利用其 L1-L2 优势
                    然后外部 Critic 补充 L3-L5 评估
```

**优势**：
- NB2 的 L1-L2 质量 >> FLUX/SD1.5
- NB2 的内部自纠正处理了文字/构图/光照
- VULCA 的 Critic + routing 处理文化层面
- 真正的 "best of both worlds"

**技术实现**：
- 新建 `nb2_provider.py` 继承 `DraftProvider`
- 使用 `google-genai` SDK
- 将 EvidencePack 中的 anchor_terms + style_directives 融入 prompt
- 可选：传入参考图像（NB2 支持最多 14 张）

### 方案 B：NB2 Multi-Turn 替代我们的 Multi-Round

```
Round 1: NB2.generate(prompt + evidence)
Round 2: NB2.chat("Improve L3 cultural adherence: add xieyi brushwork")
Round 3: NB2.chat("Enhance L5: more philosophical depth in composition")
```

**优势**：利用 NB2 的 multi-turn editing 能力
**风险**：NB2 可能不理解 L3-L5 级别的修复指令
**评估**：需要实验验证

### 方案 C：双层自纠正

```
外层循环 (VULCA-Agent):
  Round 1:
    内层循环 (NB2): Plan→Generate→Review→Correct→Output
    → Critic: L1-L5 评估
    → Queen: rerun if L3-L5 too low
  Round 2:
    内层循环 (NB2): Plan→Generate(with FixItPlan)→Review→Correct→Output
    → Critic: L1-L5 评估
    → Queen: accept
```

**复杂度最高，但理论上最优**：NB2 处理 L1-L2 纠正，VULCA 处理 L3-L5 纠正。

## 6. 实验设计建议

### 最小验证实验（5 tasks, ~$3）

| 条件 | 配置 | 目的 |
|------|------|------|
| C (existing) | FLUX / Rule / Single / No Route | FLUX baseline |
| C+ (existing) | FLUX / Rule / Single / +Route | FLUX + routing |
| **G** | **NB2 / Rule / Single / No Route** | **NB2 baseline** |
| **G+** | **NB2 / Rule / Single / +Route** | **NB2 + routing** |

**核心假设**：
1. G > C（NB2 内部自纠正 → L1-L2 更高）
2. G+ > G（routing 仍有效 → L3-L5 提升）
3. G→G+ 的 L3-L5 gain ≈ C→C+ 的 L3-L5 gain（routing 效果与 generator 无关）

### 完整实验（30 tasks, ~$28）

如果验证通过，扩展到 30 tasks 获得统计显著性。

## 7. 论文叙事升级路径

### 当前叙事（routing-only）

> "Cultural routing accounts for 95% of improvement"

### 升级叙事（routing + NB2 互补）

> "We demonstrate that evaluation-side cultural routing is complementary to
>  generation-side self-correction: even Nano Banana 2, with its built-in
>  Plan→Review→Correct pipeline, still requires external cultural routing
>  for L3-L5 improvement. The two paradigms improve orthogonal dimensions:
>  NB2 improves L1-L2 visual quality, while cultural routing improves
>  L3-L5 cultural quality."

这个叙事比现在的**强得多**，因为：
1. 直接对标 Google DeepMind 最新模型
2. 证明了 "即使最先进的 generation-side 也不够"
3. 提供了清晰的互补性证据
4. ACM MM 审稿人会被 NB2 的 novelty 吸引
