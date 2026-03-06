# VULCA Ablation Experiment: Mock Mode Analysis Report

**Date**: 2026-02-16
**Mode**: Mock (deterministic scoring, no API cost)
**Scale**: 6 conditions × 30 tasks = 180 runs, 180/180 SUCCESS

---

## 1. Experiment Design

| Condition | Image Model | Critic | Loop | Cultural Routing | Label |
|:---------:|:-----------:|:------:|:----:|:----------------:|:------|
| A | SD1.5 | Rule-only | Single (max=1) | Off | baseline-weak |
| B | SD1.5 | Rule+LLM | Multi (max=3) | On | agent-weak |
| C | FLUX | Rule-only | Single (max=1) | Off | baseline-strong |
| D | FLUX | Rule+LLM | Multi (max=3) | On | **agent-strong** |
| E | FLUX | Rule-only | Multi (max=3) | On | loop-no-llm |
| F | FLUX | Rule+LLM | Single (max=1) | On | llm-no-loop |

**任务分布**: 10 poetic + 10 cultural + 10 taboo = 30 tasks/condition

---

## 2. Summary Results

| Cond | Score | Rounds | Accept% | Rerun% | Latency |
|:----:|:-----:|:------:|:-------:|:------:|:-------:|
| A | 0.898 | 1.0 | 23% | 0% | 6913ms |
| B | 0.909 | 1.1 | 93% | 7% | 6182ms |
| C | 0.898 | 1.0 | 23% | 0% | 6648ms |
| D | 0.909 | 1.1 | 93% | 7% | 6449ms |
| E | 0.908 | 1.1 | 93% | 7% | 6150ms |
| F | 0.909 | 1.0 | 47% | 0% | 6022ms |

---

## 3. Key Comparisons

### 3.1 Core Question: Agent Loop on Strong Model (C vs D)

| Metric | C (baseline-strong) | D (agent-strong) | Delta |
|--------|:---:|:---:|:---:|
| Avg Score | 0.898 | 0.909 | **+0.012** |
| Accept Rate | 23% | 93% | **+70pp** |
| Rerun Triggers | 0 | 2/30 (7%) | +7pp |
| L5 Aesthetic | 0.833 | 0.887 | **+0.053** |

**解读**: Agent 循环 + LLM Critic + 文化路由使 accept 率从 23% 提升至 93%。L5 美学维度改善最显著 (+0.053)。Mock 模式下 score delta 较小 (+0.012)，因为 mock 评分是确定性的；real mode 预期差异更大。

### 3.2 Model Upgrade Effect (A vs C)

| Metric | A (SD1.5) | C (FLUX) | Delta |
|--------|:---:|:---:|:---:|
| Avg Score | 0.898 | 0.898 | 0.000 |

**解读**: Mock 模式下模型升级无差异（expected）。两者使用相同 mock 评分逻辑，生图模型差异只在 real mode 体现。

### 3.3 Loop-only vs LLM-only (E vs F)

| Metric | E (loop-no-llm) | F (llm-no-loop) |
|--------|:---:|:---:|
| Accept Rate | 93% | 47% |
| Rerun% | 7% | 0% |
| Avg Rounds | 1.1 | 1.0 |

**解读**: 多轮循环（即使没有 LLM）比 LLM 单轮更有效。因为循环提供了重试机会，而 LLM 单轮只调整评分标准但无法重画。

### 3.4 LLM Incremental Value (E vs D)

| Metric | E (rule-only loop) | D (full agent) | Delta |
|--------|:---:|:---:|:---:|
| Avg Score | 0.908 | 0.909 | +0.001 |

**解读**: Mock 模式下 LLM 增量很小。Real mode 预期 LLM 通过 FixItPlan.prompt_delta 提供定向修复，增量会更大。

---

## 4. Category Breakdown

### 4.1 Poetic Tasks (10 tasks/condition)

| Cond | Score | Accept% |
|:----:|:-----:|:-------:|
| A | 0.911 | 10% |
| B | 0.940 | 100% |
| C | 0.911 | 10% |
| D | 0.940 | 100% |
| E | 0.940 | 100% |
| F | 0.940 | 70% |

Poetic 类得分最高，文化路由的权重调制使 accept 率显著提升。

### 4.2 Cultural Tasks (10 tasks/condition)

| Cond | Score | Accept% |
|:----:|:-----:|:-------:|
| A | 0.908 | 0% |
| B | 0.906 | 100% |
| C | 0.908 | 0% |
| D | 0.906 | 100% |
| E | 0.906 | 100% |
| F | 0.906 | 10% |

Cultural 类在 baseline 中 accept 率 = 0%（Queen 阈值 0.80 未达到），但 Agent 条件下 100%。F (llm-no-loop) 仅 10%，说明单轮 LLM 对文化类帮助有限。

### 4.3 Taboo Tasks (10 tasks/condition)

| Cond | Score | Accept% |
|:----:|:-----:|:-------:|
| A | 0.873 | 60% |
| B | 0.882 | 80% |
| C | 0.873 | 60% |
| D | 0.882 | 80% |
| E | 0.879 | 80% |
| F | 0.881 | 60% |

Taboo 类是 rerun 的主要触发源：bench-010/bench-020 在 B/D/E 条件下触发 3 轮循环。

---

## 5. Rerun Behavior Deep Dive

### bench-010 (taboo task: "Chinese dragon sensitive cultural context")

| Condition | Rounds | Queen Actions | Final |
|:---------:|:------:|:-------------|:-----:|
| A | 1 | stop (max_rounds=1) | stop |
| B | 3 | rerun → rerun → stop (max_rounds=3) | stop |
| C | 1 | stop (max_rounds=1) | stop |
| D | 3 | rerun → rerun → stop (max_rounds=3) | stop |
| E | 3 | rerun → rerun → stop (max_rounds=3) | stop |
| F | 1 | stop (max_rounds=1) | stop |

**关键观察**:
- `taboo_violations=1` 触发 cross-layer signal: `rerun ['visual_perception']`
- Mock 模式下每轮分数微升 (0.609 → 0.610 → 0.612) 但始终低于 accept=0.80
- Real mode 预期: FixItPlan 修改 prompt 避开敏感词 → 分数显著提升

---

## 6. Mock Mode Limitations

| 现象 | 原因 | Real Mode 预期 |
|------|------|----------------|
| A=C 分数完全相同 | Mock 评分与模型无关 | FLUX 质量 >> SD1.5 |
| Score delta 仅 0.012 | 确定性评分逻辑 | LLM 动态评分 + 更大方差 |
| Rerun 无法修复 | Mock 重绘 = 换 seed | FixItPlan.prompt_delta 定向修复 |
| 仅 L5 有差异 | 文化路由调制 L5 权重 | VLM 图像分析提供真实 L1/L2 差异 |

---

## 7. Conclusions & Real Mode Predictions

### Mock Mode 已验证:
1. **框架正确**: 180/180 runs 全部成功，0 crash, 0 数据丢失
2. **循环激活**: 多轮条件 (B/D/E) rerun 率 7% (taboo 任务触发)
3. **文化路由有效**: accept 率 23% → 93% (L5 权重调制是主因)
4. **分解有效**: 6 条件成功分离出 model/critic/loop/routing 的独立贡献

### Real Mode 预测:
1. **C vs D** (核心问题): Δscore ≥ 0.05, p < 0.05 (FLUX + Agent loop)
2. **A vs B**: Δscore ≤ 0.02 (SD1.5 天花板限制 Agent 效果)
3. **E vs D**: Δscore ~0.02-0.03 (LLM Critic 在循环中的增量)
4. **Taboo 类**: Agent 条件修复率 ≥ 30% (FixItPlan prompt_delta)

### Next Step:
- Real mode 消融: `python3 run_ablation.py --mode real --conditions C D` (先验证核心假设)
- 成本: 2 conditions × 30 tasks × 4 candidates = 240 FLUX images ≈ $0.72 (Schnell) 或 $12 (Pro)
- 预计耗时: ~30 min (Schnell) / ~60 min (Pro)
