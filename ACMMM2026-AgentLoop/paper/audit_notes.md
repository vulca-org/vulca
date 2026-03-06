# ACM MM 2026 论文审核记录

日期：2026-02-24

## 审核目标
确保论文叙事与实际产品（VULCA Agent Loop prototype）严格一致，消除所有 overclaim。

---

## 问题 1: Elimination Argument 来源问题

### 现状
Introduction 第 102-106 行声称：
- "Injecting cultural knowledge into prompts merely provides the model with additional narrative material—the evidence is consumed as stylistic suggestion rather than obeyed as structural constraint."
- "End-to-end reward optimization fares no better: when pressured to improve cultural scores, models exploit the cheapest path—suppressing lower-level detail rather than elevating higher-level understanding."

这两个 claim 来自 PhD 论文 C2/C3 实验，**不是** ACM MM 论文自己的实验。引用的 Madaan (Self-Refine) 也不支持这些 claim。

### 解决方案
1. **删除**对 PhD 实验的 implicit 引用（"consumed as stylistic suggestion"、"suppressing lower-level detail"）
2. **替换为**本文实验可支撑的论述 + 来自其他已发表工作的佐证：
   - Culture-TRIP (NAACL 2025) 发现 prompt engineering 不足以桥接文化差距，需要 iterative refinement
   - "Survey of Bias in T2I Generation" (Wan et al. 2024) 发现 geo-cultural bias 无法通过 dataset filtering 综合解决
   - "Where Culture Fades" (Shi et al. 2025) 发现 T2I 模型在 multilingual prompts 下产生 culturally neutral 输出
3. **保留** elimination argument 的逻辑结构，但改为引用 published work 而非 implicit PhD claims

### 替换引用
- 删除 `\cite{madaan2024self}` 对 "end-to-end optimization suppresses lower-level" 的支持
- 新增: Culture-TRIP (Jeong et al. 2025, NAACL)
- 新增: Wan et al. 2024 (Survey of Bias in T2I)
- 保留 `\cite{madaan2024self}` 仅用于 Related Work 中 self-refinement 的正确用法

---

## 问题 2: L1-L2 下降 vs "Orthogonal" Claim

### 现状
数据：L1 .821→.800 (−.021)，L2 .773→.766 (−.008)
论文声称 eval-side 和 gen-side "operate on largely disjoint domains" 且 L1-L2 "essentially unchanged"。

### 实际分析
L1-L2 下降可能有两种解释：
1. **真正的 trade-off**：文化改进以视觉质量为代价
2. **评分机制效应**：L1-L2 由 rule-based scoring 计算，culturally grounded prompt 更长更具体 → keyword matching 规则的行为改变

关键数据：A (.846/.764) vs C (.821/.773) — SD1.5 的 L1 反而比 FLUX 高！这暗示 L1-L2 差异更多是评分机制效应而非真正的视觉质量差异。

### 解决方案
1. **不修改实验**（数据是真实的）
2. **修改叙事**：
   - "orthogonal" → "largely complementary"
   - 诚实承认 L1-L2 有 minor decrease
   - 解释可能的机制：rule-based L1-L2 scores 对 prompt specificity 敏感，culturally enriched prompts 产生更长更具体的 prompt → rule-based scoring 的 keyword matching 行为变化
   - 强调 L1-L2 decrease 幅度 (−0.021, −0.008) 远小于 L3-L5 increase (+0.056, +0.030, +0.134)

---

## 问题 3: Queen Cross-Dimension Protection

### 代码调研结果（来自 Explore agent）
**实现状态：已实现，但有信息丧失点**

✅ 已实现：
- `PlanState.confirmed_dimensions` 和 `pending_dimensions` 完整实现
- Queen rule-based path: 5b cross-layer signal → rerun_dimensions + preserve_dimensions (补集)
- Queen LLM path: 解析器自动计算 preserve = all_dims - rerun_dims
- HITL path: `_apply_hitl_score_preservation()` 完整保护

⚠️ 信息丧失：
- `LocalRerunRequest.preserve_layers` 字段存在但 **DraftAgent.refine_candidate 未使用**
- 实际保护通过 mask 补集实现（黑色=保留，白色=重绘）
- LLM 响应 schema 不包含 preserve_dimensions 字段（由解析器自动补集）

### 解决方案
论文当前描述："The Queen tracks confirmed vs. pending dimensions, ensuring that improvements in one layer do not degrade another"
→ 这是**准确的**（代码确实实现了）。但需要注意：
- 不能 claim "ControlNet-based targeted inpainting preserves successful regions" — 因为在 ablation 中 ControlNet 未触发
- 可以保留 Queen 维度保护的描述，因为评分级别的保护（HITL score preservation）是真实实现的

---

## 问题 4: 9 Traditions vs 表格 6 行

### 代码调研结果
`cultural_weights.py` 实际定义了 **9 个传统**：
1. default (回退)
2. chinese_xieyi (L5=0.30)
3. chinese_gongbi (L2=0.30)
4. western_academic (L4=0.25)
5. islamic_geometric (L2=0.30)
6. japanese_traditional (L5=0.25)
7. watercolor (均衡)
8. african_traditional (L3=0.30)
9. south_asian (L5=0.25)

### 论文 vs 代码差异
论文表格有 **6 行**，展示的权重与代码**不完全一致**：

| 传统 | 论文 L1 | 代码 L1 | 匹配？ |
|------|---------|---------|--------|
| chinese_xieyi | .15 | .10 | ❌ |
| islamic | .15 | .25 | ❌ |
| japanese | .20 | .15 | ❌ |
| african | .15 | .15 | ✅ |

### 解决方案
1. 更新表格为 9 行（包含 watercolor 和 south_asian，删 default）或保持 6 行但在 caption 标注 "6 of 9 traditions shown; full table in supplementary"
2. **修正权重数值**以匹配代码实际值

---

## 问题 5: FixItPlan + ControlNet 实际触发

### 代码调研结果（来自 Explore agent）——**重大发现**

**180 个 ablation runs 中，0 个达到第 2 轮。所有运行停在第 1 轮。**

| 条件 | Accept | Stop | Rerun | 实际轮数 |
|------|--------|------|-------|---------|
| A (single) | 0 | 30 | 0 | 1 |
| B (multi) | 26 | 4 | 0 | 1 |
| C (single) | 0 | 30 | 0 | 1 |
| D (multi) | 28 | 2 | 0 | 1 |
| E (multi) | 28 | 2 | 0 | 1 |
| F (single) | 0 | 30 | 0 | 1 |

**原因**：Queen accept_threshold=0.80 相对宽松，大多数首轮分数 ≥ 0.80 → accept。

**ControlNet**：`controlnet_enabled=False`（默认值），ablation config 未启用 → ControlNet 代码路径完全未触发。

### 影响
这意味着论文中关于 "multi-round self-correction" 的核心叙事**在 ablation 中未被验证**：
- C→E 声称的 "+0.037 from multi-round loop" — 但所有 E 运行都是单轮！
- D 的 "self-correction loop" — 但 0/30 runs 触发 rerun！
- FixItPlan、ControlNet inpainting — 完全未执行

**真正被测量的是**：
- 有 Queen 评估+决策 vs 没有 → Queen 的 accept/stop 门控效应
- 有 cultural routing vs 没有 → 权重调整效应
- 有 LLM Critic vs 没有 → 评分严格度效应

### 解决方案
这是最严重的问题。需要：
1. **重新理解实验数据**："multi-round" 条件（B/D/E）实际贡献不是 "多轮修正" 而是 "Queen 门控 + 文化路由权重调整"
2. **修改论文叙事**：不能说 "multi-round self-correction contributes +0.037"，应该说 "the agent evaluation pipeline (Queen gating + cultural routing) contributes +0.037"
3. **或者重新实验**：降低 accept_threshold 使 rerun 真正触发，验证多轮循环的实际效果
4. **FixItPlan/ControlNet claim**：降级为"系统支持但本实验未触发"

---

## 问题 6: 23% Acceptance Rate

### 现状
Introduction: "single-pass FLUX baseline achieves only 23% acceptance rate"
来源：mock ablation 中 unrouted conditions 的 Queen acceptance rate。

### 问题
- Mock scoring ≠ real-mode scoring
- Condition C 是 single-pass，没有 Queen 评估
- 23% 是在 mock 环境下用 Queen threshold 回测的数字

### 解决方案
删除 23% 数字。替换为 real-mode 可支撑的数据：
- Condition C 的 L5 baseline = 0.705（这是 real-mode 数据）
- Condition D vs C 的 acceptance rate 对比（D: 28/30=93%, C 无 Queen 无从判断）
- 或简单说："the single-pass baseline produces culturally shallow outputs with L5 scores averaging 0.705"

---

## 问题 7: Madaan 2024 引用

### 现状
`\cite{madaan2024self}` 用在 Introduction 支持 "end-to-end optimization suppresses lower-level detail"。
Self-Refine 论文讲 LLM text iterative refinement，不涉及 image generation、reward hacking 或 level suppression。

### 替换方案
新增两个引用：
1. **Culture-TRIP** (Jeong et al., NAACL 2025): 发现 standard T2I models 无法处理文化概念，需要 iterative prompt refinement + 外部文化知识
2. **Wan et al. 2024** (Survey of Bias in T2I): "current mitigation methods fail to resolve biases comprehensively", geo-cultural bias under-explored

Madaan 保留在 Related Work 的 self-correction 段落中（用法正确）。

---

## 决策：路径 B — 重做部分实验

**日期**：2026-02-24
**决策**：用户选择路径 B（重做实验），而非路径 A（仅重写叙事）。

### 理由
- 路径 A 会导致叙事力度大幅下降（"pipeline with gating" 不如 "self-correction loop"）
- 路径 B 能保留核心叙事并用真实多轮数据支撑
- ACM MM deadline 4/1，还有 5 周时间

---

## 实验 v2 设计

### 阈值调整

```python
# 新阈值 (queen_config.py)
accept_threshold = 0.90    # 从 0.80 提高 → 更多 rerun 触发
early_stop_threshold = 0.95 # 微调
max_rounds = 3             # 不变
min_improvement = 0.02     # 从 0.05 降低 → 避免过早 stagnation stop
```

### 需要重跑的条件

| 条件 | 配置 | Runs | 资源 | 目的 |
|------|------|------|------|------|
| C' | FLUX / Rule / Single / **+Route** | 30 | FLUX API | 隔离 routing-only 效果 |
| D' | FLUX / Rule+LLM / Multi / Route | 30 | FLUX API + DeepSeek | 完整系统（真正多轮） |
| E' | FLUX / Rule / Multi / Route | 30 | FLUX API | Loop-only（真正多轮） |
| **总计** | | **90** | ~$3 Together.ai | |

原条件 A/B/C/F 数据保留不变。

### 新增条件 C' 的作用
- C 没有 routing，E' 有 routing + loop
- C' 有 routing，没有 loop
- C→C': 纯 routing 贡献
- C'→E': 纯 loop 贡献（控制了 routing）
- 这彻底隔离了 routing 和 loop 的效应

### 预期 rerun 触发率
- 当前 D 条件 mean=0.847，首轮分布大约 0.75-0.95
- accept_threshold 提到 0.90 后：
  - score < 0.90 → rerun（预估 ~50-60% 的任务）
  - score ≥ 0.90 → accept（预估 ~40-50%）
  - 总 rerun 触发率 ~50%，合理范围

### ControlNet 决策
**暂不启用** ControlNet：
- FLUX 条件走 API，无法使用 ControlNet（ControlNet 是 SD1.5 本地 GPU 功能）
- Rerun 机制：prompt 修改 + FixItPlan prompt delta + 重新 FLUX 生成
- 如果 rerun 走的是 full regeneration（非 inpainting），论文描述需要对应调整
- ControlNet inpainting 留给 future work 或 SD1.5 条件的后续实验

### 实验后论文更新

重跑完成后需要更新：
1. **Table 2 (ablation)**：新增 C'/D'/E' 行（或替换 C/D/E）
2. **Core narrative**："multi-round self-correction" 有真实多轮数据支撑
3. **Rerun statistics**：展示实际 rerun 触发率、轮次分布、per-round improvement
4. **Qualitative examples**：从 D' 中选取多轮改进最显著的案例更新 Figure 1

### 三种可能的 Outcome

| Outcome | 结果 | 叙事影响 |
|---------|------|---------|
| 1 (最好) | D' > D，多轮确实提升质量 | "iteration beats intelligence" 完美支撑 |
| 2 (中性) | D' ≈ D，多轮无显著提升 | 改为 "structured evaluation pipeline with safety-net iteration" |
| 3 (最差) | D' < D，多轮导致退化 | 系统循环机制需改进，论文大幅重写 |

---

## Demo 视频 v4 计划

**决策**：录屏 Prototype 前端页面（思路 A），展示真实多轮循环效果。

### 为什么选录屏而非 Pillow 渲染
- Prototype 前端已有完整 UI：Round Timeline、L1-L5 Radar Chart、FixItPlan 面板、Queen Decision Panel、HITL Controls
- 录屏 = 真实操作 = 审稿人/投资者可信度最高
- SSE 实时事件流让页面有"活"的感觉（进度条逐步亮绿、分数逐维度填充）
- 无需额外渲染脚本，降低维护成本

### Prototype 前端 UI 能力确认（2026-02-24 调研）

页面从上到下包含以下面板：

| 面板 | 功能 | 录屏价值 |
|------|------|---------|
| **RunConfigForm** | 选 tradition/provider/candidates/max_rounds/agent_critic/HITL | 展示用户可配置性 |
| **Pipeline Progress** | 5 阶段串联进度（Scout→Draft→Critic→Queen→Archive）| 直观展示管道流转 |
| **Round Timeline** | 水平轮次卡片，每卡含 L1-L5 mini bar + 加权分 + Queen 决策图标 + FixItPlan 标签 + cross-layer signal 标签 | **核心**：多轮循环的视觉证据 |
| **Scout Evidence** | 3 统计卡片（Sample Matches / Terminology Hits / Taboo Violations）| 展示证据检索 |
| **Draft Candidates** | 2×4 图像网格，标注 Best/Selected | 展示候选多样性 |
| **Critic Score Table** | L1-L5 分数条 + rationale 展开 + gate PASS/FAIL + risk tags | 展示逐层评估深度 |
| **Critic Radar Chart** | 五边形雷达图，多轮叠加（R1 蓝、R2 翠、R3 琥珀）| **核心**：per-round improvement 可视化 |
| **FixItPlan** | 靛蓝卡片，每项含 target_layer + priority + issue + fix + mask_hint | 展示定向修复机制 |
| **Queen Decision** | 大色块卡片（绿=accept/蓝=rerun/红=stop）+ rerun_dimensions 列表 | **核心**：决策可追溯 |
| **HITL Controls** | Lock/Rerun dimensions toggle + Force Accept + Advanced | 展示人机协作 |
| **Final Summary** | Rounds + Time + Cost 统计 | 结尾总结 |

后端通过 SSE (`/api/v1/prototype/runs/{taskId}/events`) 实时推送每阶段完成事件，前端动态更新。

### 录屏脚本（3-4 分钟）

```
S1 (0:00-0:20) — 配置与启动
  - 页面加载，展示 RunConfigForm
  - 填入: Subject="Bada Shanren style of two fish expressing cosmic solitude"
  - Tradition: Chinese Xieyi
  - Provider: together_flux (真实 FLUX)
  - Candidates: 4, Max Rounds: 3
  - ✓ Agent Critic (LLM)
  - 点击 "Run Pipeline"

S2 (0:20-1:00) — Round 1: 首轮评估
  - Pipeline Progress: Scout 亮绿 → Draft 亮绿（4 候选图像加载）
  - Critic: Score Table 逐维度填充，Radar 图表绘制 R1 多边形
  - 关键画面：L3 Cultural = 0.65（黄色警告）, L5 = 0.72
  - FixItPlan 出现：target L3 + L5, issue "Insufficient xieyi brushwork texture"
  - Queen Decision: 🔄 RERUN (蓝色), reason "L3+L5 below threshold"
  - Round Timeline: R1 卡片出现，蓝色 rerun 图标

S3 (1:00-1:50) — Round 2: 自我修正
  - Pipeline Progress: Draft R2 亮绿（新 4 候选）
  - Critic: Score Table 更新，Radar 添加 R2 多边形（翠色，外扩）
  - 关键画面：L3 从 0.65→0.78 (+0.13), L5 从 0.72→0.85 (+0.13)
  - 加权总分: 0.81→0.88 (+0.07)
  - Queen Decision: ✅ ACCEPT (绿色)
  - Round Timeline: R2 卡片出现，绿色 accept 图标
  - **核心镜头**：R1→R2 Radar 叠加对比，外层明显扩大

S4 (1:50-2:30) — 详情展示
  - 展开 Critic Score Table 的 L3 rationale（LLM 分析文本）
  - 展开 FixItPlan 详情（target_layer, issue, fix, mask_hint）
  - 点击 🔍 打开 CriticDetailModal（Agent 元数据 + 跨层信号矩阵）
  - 展示 Scout Evidence（terminology hits + taboo violations）

S5 (2:30-3:00) — HITL 演示（可选）
  - 新开一个 run，启用 HITL
  - Queen 决策后显示 "Waiting for Human" 状态
  - 手动 Lock L1+L2 维度 → Rerun L5
  - 点击 "Approve" → 系统继续第三轮
  - 展示 HITL Constraints Applied 面板

S6 (3:00-3:30) — 总结
  - Final Summary 绿色卡片：Rounds=2, Time=45s, Cost=$0.012
  - 对比 R1 候选图 vs R2 最终图（side-by-side）
  - 标注 L1-L5 分数变化
```

### 录制要求

**环境准备**：
- 后端: `uvicorn` 运行在 localhost:8001，启用 prototype API
- 前端: `npm run dev` 运行在 localhost:5173
- FLUX API: Together.ai key 有效（~$0.003/image × 8 images × 2 rounds = ~$0.05/run）
- DeepSeek API: key 有效（LLM critic）
- **Queen 阈值已调为 0.90**（确保 rerun 触发）

**录制工具**：
- OBS Studio 或 Windows Game Bar
- 分辨率: 1920×1080
- 浏览器: Chrome, 缩放 90%（确保所有面板可见）

**预录制测试**：
- 先用 mock provider 跑 2-3 次，确认 UI 流转正常
- 再用 together_flux 跑 1 次，确认 rerun 真正触发
- 选分数变化最大、视觉差异最明显的 tradition（推荐 Chinese Xieyi 或 Taboo 类）

### 依赖关系
```
实验 v2 阈值调整 (queen_config.py)
    ↓
验证 rerun 触发 (mock + 1 real run)
    ↓
正式录制 (2-3 次取最佳)
    ↓
后期: 字幕 + 标注 + 剪辑
    ↓
输出: VULCA_Demo_v4.mp4
```

**关键依赖**：Queen accept_threshold 必须先调到 0.90，否则录屏和 v1 实验一样——首轮 accept，看不到循环。

---

## 行动优先级（更新后）

| # | 问题 | 严重性 | 行动 | 状态 |
|---|------|--------|------|------|
| 5 | Multi-round 实际未触发 | **致命** | 重做实验 v2 (D'/E'/C', 90 runs) | **待执行** |
| Demo | 视频需要展示真实多轮效果 | 高 | 实验 v2 完成后制作 v4 | **待执行** |
| 1 | Elimination argument 来源 | 高 | 重写 Intro + 新增 Culture-TRIP/Wan 引用 | 待修复 |
| 2 | L1-L2 trade-off | 高 | "orthogonal" → "largely complementary" | 待修复 |
| 6 | 23% mock 数据 | 高 | 删除，替换为 L5=0.705 | 待修复 |
| 7 | Madaan 引用 | 中 | 移回 Related Work，Intro 用新引用 | 待修复 |
| 4 | 权重表不一致 | 中 | 更新为代码实际值，补齐 9 传统 | 待修复 |
| 3 | Queen 保护 | 低 | 当前描述基本准确，微调措辞 | 可暂缓 |

### 执行顺序
1. **Phase 1 (2/24-2/28)**：修改 queen_config.py + run_ablation.py，跑实验 v2 (90 runs)
2. **Phase 2 (3/1-3/3)**：分析 v2 数据，更新论文 Table 2 + 叙事
3. **Phase 3 (3/3-3/7)**：修复问题 1/2/4/6/7（论文文本层面）
4. **Phase 4 (3/7-3/14)**：制作 demo v4
5. **Phase 5 (3/14-3/25)**：最终审核 + abstract submission (3/25)
6. **Phase 6 (3/25-4/1)**：paper submission (4/1)

---

## Phase 1 执行记录（2026-02-24）

### 代码修改

#### 1. `run_ablation.py` — 新增 v2 条件 + 阈值覆盖

**修改文件**：`wenxin-backend/app/prototype/blind_eval/run_ablation.py`

**变更内容**：
1. `AblationCondition` dataclass 新增 3 个可选字段：
   - `accept_threshold: float | None = None`
   - `min_improvement: float | None = None`
   - `early_stop_threshold: float | None = None`
2. `_build_ablation_orchestrator` 使用条件中的阈值覆盖 QueenConfig 默认值
3. `_make_conditions` 新增 3 个 v2 条件：
   - **Cp** (routing-baseline): FLUX + Rule + Single + Routing, accept=0.90
   - **Dp** (full-system-v2): FLUX + Rule+LLM + Multi(3) + Routing, accept=0.90, min_improve=0.02, early_stop=0.95
   - **Ep** (loop-only-v2): FLUX + Rule + Multi(3) + Routing, accept=0.90, min_improve=0.02, early_stop=0.95
4. v2 阈值常量: `V2_ACCEPT=0.90, V2_MIN_IMPROVE=0.02, V2_EARLY_STOP=0.95`
5. Report comparisons 新增 5 条 v2 对比

**设计决策**：
- **不修改 `queen_config.py` 默认值**：避免破坏现有 50+ 验证测试
- **通过 `AblationCondition` 传递阈值**：v1 条件使用默认值 (0.80)，v2 条件使用新阈值 (0.90)
- **v1 数据保留**：原始 180 runs 不重新运行，只增量添加 90 runs

#### 2. `orchestrator.py` — 无永久修改

**曾添加又撤回的修改**：在 Queen 调用前向 `plan_state.history` 写入分数。

**撤回原因**：Queen Agent 在 `decide()` 内部已经执行 `plan_state.history.append()` (queen_agent.py:71-78)。
Orchestrator 的重复写入导致 Round 1 就有 2 条 history 记录，使 stagnation 检测误判 delta=0 提前终止。

**结论**：Orchestrator 不需要修改。Queen 的 history 追踪机制原本正确，v1 的问题纯粹是 accept_threshold=0.80 太低。

### Mock 验证结果

#### 测试 1: v2 条件单独测试（3 tasks）

```
Cp  routing-baseline   1.0 rounds  score=0.736  ✓ 单轮
Dp  full-system-v2     3.0 rounds  score=0.742  ✓ 多轮触发，跑满 3 轮
Ep  loop-only-v2       2.0 rounds  score=0.740  ✓ 多轮触发，Round 2 stagnation stop
```

#### 测试 2: v1+v2 混合测试（5 tasks × 7 conditions = 35 runs）

```
C   baseline-strong    1.0 rounds  score=0.740  ✓ v1 行为不变
D   agent-strong       3.0 rounds  score=0.736  ✓ v1 LLM 创造分数波动
E   loop-no-llm        2.0 rounds  score=0.743  ✓ v1 stagnation stop
F   llm-no-loop        1.0 rounds  score=0.734  ✓ v1 单轮
Cp  routing-baseline   1.0 rounds  score=0.737  ✓ v2 单轮 baseline
Dp  full-system-v2     3.0 rounds  score=0.745  ✓ v2 多轮，最高分
Ep  loop-only-v2       2.0 rounds  score=0.744  ✓ v2 多轮
```

**35/35 成功，0 失败，v1 行为向后兼容**。

### 关键发现

1. **Dp 多轮行为**：LLM Critic 在每轮评估中引入足够的分数变化（因为 LLM 评估有随机性），避免 stagnation 检测。这是正确且符合预期的——LLM 发现新问题 → 分数维度变化 → 避免停滞。

2. **Ep 2 轮行为**：Rule-only 评分对同任务不同图像的变化很小（mock 模式下 delta < 0.02），Round 2 后正确 stagnation stop。在 real mode 中，FLUX 生成的不同图像应产生更大分数差异，Ep 可能运行 2-3 轮。

3. **v1 问题确认**：v1 的 accept_threshold=0.80 在 real mode 下 FLUX 平均分 ~0.847，大部分任务首轮 score ≥ 0.80 直接 accept，完全跳过循环。v2 的 0.90 阈值使 ~50-60% 的任务触发 rerun。

### Real Mode 验证（1 task × 3 conditions）

**DeepSeek API 问题**：globalai.vip 代理的 DeepSeek 路由超时（600s timeout）。
**解决方案**：临时将 L3-L5 模型从 `deepseek_v3` 切换到 `gemini_flash_lite`。
**修改文件**：`agents/model_router.py` DEFAULT_LAYER_MODELS

```
Cp  routing-baseline   1 round   score=0.832  121s  $0.012  ✓
Dp  full-system-v2     3 rounds  score=0.815  291s  $0.036  ✓ 多轮触发！
Ep  loop-only-v2       2 rounds  score=0.835   17s  $0.024  ✓ 多轮触发！
```

**真实分数范围**：FLUX + routing 下约 0.81-0.84。V2 阈值 0.90 使 100% 任务触发 rerun。

**注意**：Dp (0.815) < Ep (0.835) 在单个 task 上。LLM 动态权重可能引入波动。需 30 tasks 统计验证。

### Full v2 Experiment Results

#### Cp + Ep (60 runs, no LLM) — ✅ 完成

**时间**：2026-02-24 16:00-16:15, ~15 分钟
**报告**：`reports/ablation-real-20260224_160053.md`

| Cond | Label | Tasks | Avg Score | Avg Rounds | Accept% | Rerun% | Cost |
|:----:|:------|:-----:|:---------:|:----------:|:-------:|:------:|:----:|
| Cp | routing-baseline | 30/30 | 0.846 | 1.0 | 3% | 0% | $0.360 |
| Ep | loop-only-v2 | 30/30 | 0.848 | 1.8 | 23% | 77% | $0.660 |

**L1-L5 维度**：

| Cond | L1 | L2 | L3 | L4 | L5 |
|:----:|:--:|:--:|:--:|:--:|:--:|
| Cp | 0.814 | 0.771 | 0.883 | 0.933 | 0.814 |
| Ep | 0.812 | 0.773 | 0.884 | 0.933 | 0.824 |

**Category Breakdown**：

| Category | Cp Score | Ep Score | Ep Accept% |
|:--------:|:--------:|:--------:|:----------:|
| Poetic | 0.891 | 0.897 | 60% |
| Cultural | 0.851 | 0.848 | 0% |
| Taboo | 0.794 | 0.797 | 10% |

**关键发现**：
1. v2 阈值成功激活多轮：**Ep rerun rate = 77%** (vs v1 的 0%)
2. 但 Cp→Ep 整体分数差仅 **+0.002** — 没有 LLM 引导的规则多轮改进有限
3. L5 Aesthetic 是唯一显著改进维度：0.814 → 0.824 (+0.010)
4. Poetic 类别从多轮受益最大：accept 率从 10% 提升到 60%
5. Cultural 类别多轮无帮助（accept 0%→0%），说明文化任务需要 LLM 指导

#### Dp (30 runs, Gemini LLM Critic) — ✅ 完成 (26/30)

**时间**：2026-02-24 19:21-21:36, ~134 分钟
**报告**：`reports/ablation-real-20260224_192133.md`
**失败**：4 个 taboo 任务因 CUDA NVML 崩溃（GPU VRAM 累积泄漏），补跑 2 次均失败

| Cond | Label | Tasks | Avg Score | Avg Rounds | Accept% | Rerun% | Cost |
|:----:|:------|:-----:|:---------:|:----------:|:-------:|:------:|:----:|
| Dp | full-system-v2 | 26/30 | 0.841 | 2.4 | 27% | 73% | ~$1.08 |

**L1-L5 维度**：

| Cond | L1 | L2 | L3 | L4 | L5 |
|:----:|:--:|:--:|:--:|:--:|:--:|
| Dp | 0.810 | 0.771 | 0.877 | 0.934 | 0.822 |

**Category Breakdown**：

| Category | Dp Score | Dp Rounds | Dp Rerun% | Tasks |
|:--------:|:--------:|:---------:|:---------:|:-----:|
| Cultural | 0.846 | 2.9 | 100% | 10/10 |
| Poetic | 0.881 | 1.8 | 40% | 10/10 |
| Taboo | 0.769 | 2.5 | 83% | 6/10 |

**异常低分**：bench-010 (taboo)=0.587, bench-020 (taboo)=0.651 — CLIP 与 taboo 主题匹配度低，合法数据

---

## Phase 1 统计分析结果（2026-02-24 22:15）

### 统一分析（9 条件 × 30 任务 = 266 有效结果）

#### v1 对比（仍然有效）

| 对比 | Δ Score | p-value | Cohen's d | 显著性 |
|------|---------|---------|-----------|--------|
| C→D (CORE) | **+0.038** | 0.00002 | 0.94 | *** |
| A→B (SD1.5) | +0.022 | 0.008 | 0.52 | ** |
| C→E (loop) | +0.037 | 0.00001 | 1.03 | *** |
| F→D (add loop) | +0.018 | 0.007 | 0.53 | ** |

#### v2 新条件（关键发现）

| 对比 | Δ Score | p-value | Cohen's d | 显著性 |
|------|---------|---------|-----------|--------|
| C→Cp (routing only) | **+0.036** | 0.00002 | 0.95 | *** |
| Cp→Dp (v2 full vs baseline) | **−0.005** | 0.21 | −0.25 | ns |
| Cp→Ep (v2 loop effect) | +0.002 | 0.35 | 0.18 | ns |
| Ep→Dp (LLM in loop) | −0.006 | 0.13 | −0.31 | ns |

#### v2 Per-Dimension (Cp vs Dp, n=26)

| Dim | Cp | Dp | Δ | p-value | Sig |
|-----|-----|-----|---|---------|-----|
| L1 | 0.823 | 0.810 | −0.013 | 0.13 | ns |
| L2 | 0.770 | 0.772 | +0.001 | 0.82 | ns |
| L3 | 0.888 | 0.877 | −0.011 | 0.16 | ns |
| L4 | 0.923 | 0.934 | +0.011 | 0.16 | ns |
| L5 | 0.820 | 0.822 | +0.002 | 0.82 | ns |

### 核心解读

1. **Cultural routing 是 C→D 效果的主要来源**：
   - C→Cp (纯 routing) = +0.036***
   - C→D (routing + loop + LLM) = +0.038***
   - 差值仅 0.002 → routing 贡献了 ~95% 的效果

2. **多轮循环在 v2 阈值下未产生显著提升**：
   - Ep rerun rate = 77%（v2 阈值成功激活了循环）
   - 但 Cp→Ep Δ = +0.002 (ns)
   - 原因：CLIP scoring 对同一 prompt 不同图像的变异很小，重新生成不产生质量提升

3. **LLM Critic 在循环中反而略有负面效应**：
   - Dp (0.841) < Cp (0.846)，虽然 ns
   - LLM 动态权重引入了评分波动，加上 Gemini Flash Lite 的评分不够精准

4. **v1 数据的"多轮效果"实际是 routing 效果**：
   - v1 的 C→E +0.037*** 看似是多轮贡献
   - 但 v1 的 E 条件实际只跑了 1.1 轮（accept_threshold=0.80 太低）
   - E 和 Cp 的唯一区别是 max_rounds 设置，但 E 根本没触发第二轮
   - 所以 C→E 的效果 = C→Cp 的效果 = **纯 routing**

### 对论文叙事的影响

**不能继续声称"multi-round self-correction loop"是核心贡献**。

**可以声称的**：
1. Cultural routing (tradition-specific weight tables) 显著提升文化质量 (+0.036, p<0.001)
2. 整体 agent pipeline (routing + evaluation + gating) 显著优于 baseline (+0.038, p<0.001)
3. L5 Aesthetic 和 L3 Cultural 是最大受益维度
4. Multi-round 机制作为 safety net 存在，但本实验的 scoring 粒度不足以驱动有效迭代

**论文重写方向**：
- 核心贡献 = "Cultural-Aware Evaluation Pipeline" 而非 "Self-Correction Loop"
- Multi-round 降级为系统能力描述（"supports iterative refinement"），不作为核心贡献
- 强调 routing + dimension-weighted evaluation 的创新性
- 保留 C→D 作为 CORE 对比（+0.038***），但诚实分解贡献来源

### Dp 补跑结果（2026-02-25 00:35）

4 个 CUDA 崩溃任务通过逐个运行 + GPU 清理成功补跑：

| Task | Score | Rounds | Decision |
|------|-------|--------|----------|
| vulca-bench-0010 | 0.727 | 3 | stop |
| vulca-bench-0011 | 0.805 | 3 | stop |
| vulca-bench-0012 | 0.843 | 3 | stop |
| vulca-bench-0024 | 0.867 | 3 | stop |

Dp 现在 **30/30 完整**。更新后统计：Dp avg=0.837, rounds=2.5, rerun=77%, accept=23%

### 最终统计分析（30/30 × 9 条件 = 270 results）

核心对比更新（含 4 个补跑任务）：

| 对比 | Δ Score | p-value | Cohen's d |
|------|---------|---------|-----------|
| C→Cp (routing) | +0.036 | <0.001*** | 0.95 |
| Cp→Ep (loop) | +0.002 | 0.35 ns | 0.18 |
| Cp→Dp (full-baseline) | −0.008 | 0.09 ns | −0.32 |

---

## Phase 2 决策：路线 A — 诚实重定位（2026-02-25）

**用户决策**：选择路线 A（诚实重定位论文叙事），而非路线 B（补强多轮实验）。
**理由**：完善产品比做实验更重要；后续可以再优化系统设计。

### 核心定位转变

```
旧叙事: "Multi-Agent Self-Correction Loop" — 多轮迭代修正是核心贡献
新叙事: "Cultural-Aware Evaluation Pipeline with Tradition-Specific Routing" — 文化路由是核心贡献
```

### 论文修改清单

| # | 修改项 | 位置 | 状态 |
|---|--------|------|------|
| P2-1 | 标题 + Abstract 重写 | 标题, L70-83 | ✅ 完成 |
| P2-2 | Introduction 重写 (elimination arg + 23% + contributions) | L102-122 | ✅ 完成 |
| P2-3 | Table 2 扩展 + 结果叙事 + Conditions 表 | L386-424 | ✅ 完成 |
| P2-4 | Analysis 重写 ("Iteration Beats Intelligence" → "Why Routing Dominates") + Conclusion | L430-495 | ✅ 完成 |
| P2-5 | 引用修复 (Madaan 移出 Intro, 新增 Culture-TRIP/Wan/Shi) | references.bib + Intro | ✅ 完成 |
| P2-6 | 权重表修正 (匹配代码值, 8→9 传统) + L1-L2 trade-off 措辞 | Section 3/4 | ✅ 完成 |
| P2-7 | DeepSeek→Gemini, 13%→77% rerun rate, 180→270, orthogonal→complementary | 多处 | ✅ 完成 |

### Phase 2 修改摘要 (2026-02-25 完成)

**标题**: "Cultural-Aware Self-Correction: Multi-Agent Loops..." → "Cultural-Aware Art Generation via Tradition-Specific Evaluation Routing"

**核心叙事转变**:
- 旧: "multi-round self-correction loop" 是核心贡献
- 新: "tradition-specific evaluation routing" 是核心贡献 (95% of effect)
- Multi-round 降级为系统能力 + CLIP 瓶颈分析

**具体修改**:
1. Abstract 完全重写, 新增 v2 发现 (CLIP bottleneck)
2. Introduction: 删除 PhD-sourced elimination arg, 新增 Culture-TRIP/Wan/Shi 引用
3. Introduction: 23% mock → L5=0.705 real-mode
4. 三条贡献重排: Routing (核心) > Grounding > Empirical Decomposition
5. Conditions 表: 6→9 条件 (A-F + C+/D+/E+), 含 θ 列
6. Table 2: 新增 C+/D+/E+ 行 + routing per-dim breakdown
7. 结果叙事: routing 为主 + iteration 无效 + CLIP granularity
8. Analysis: "Why Iteration Beats Intelligence" → "Why Routing Dominates"
9. Conclusion: 删除 "iteration beats intelligence", 新增 routing insight
10. 权重表: 6→8 行, 数值匹配代码 (cultural_weights.py)
11. Limitations: 新增 CLIP scoring granularity 作为首要限制
12. DeepSeek → Gemini 2.5 Flash Lite (全文)
13. 180 → 270 runs (全文)
14. "orthogonal" → "complementary"

**编译验证**: 8 页正文 + refs, 0 TODO, 0 undefined refs, 0 errors

### 下一步

1. ~~修改 run_ablation.py~~ ✅
2. ~~Mock 验证~~ ✅
3. ~~Real mode 验证~~ ✅
4. ~~Cp + Ep full experiment~~ ✅ (60/60)
5. ~~Dp full experiment~~ ✅ (30/30, 含 4 补跑)
6. ~~统计分析~~ ✅ (9 条件, 270 结果)
7. ~~论文更新 Phase 2~~ ✅ (全部 7 项完成)
8. **待办**: 生成 qualitative.pdf 对比图（目前引用但文件不存在）
9. **待办**: Architecture diagram (figures/architecture_inline.tex)
10. **待办**: 最终页数精简（如有需要）
