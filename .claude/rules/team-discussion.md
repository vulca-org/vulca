---
paths:
  - "**/*"
---

# Team Discussion Protocol

定义 VULCA 团队讨论的具体执行协议。与 proactive-triggers.md 配合使用。

## 讨论触发阈值

不是每次回复都需要团队讨论。以下是判断标准：

### 必须触发团队快评（模式 B）的场景
- 完成了一个 Phase 或里程碑
- 修复了 3 个以上相关 bug（形成模式）
- 用户明确问"下一步做什么"
- 用户讨论功能优先级或产品方向
- 第一次接触一个新话题领域

### 必须触发深度辩论（模式 C）的场景
- "要不要做 X" 类二选一决策
- 涉及架构方向选择
- 涉及产品定位或目标用户调整
- 资源分配讨论

### 只需内心独白（模式 A）的场景
- 日常 bug 修复（单个小 bug）
- 常规代码重构
- 测试修复
- 文档更新
- 配置调整

## Agent Spawn 规则

### 并行 spawn（效率优先）
当需要 2+ agent 视角且它们的分析不互相依赖时：
```
并行 spawn product-analyst + growth-strategist
→ 各自独立分析
→ 我综合
```

### 串联 spawn（质量优先）
当后一个 agent 需要前一个的输出时：
```
先 spawn product-analyst → 拿到分析结果
→ 把结果传给 growth-strategist 做审查
→ 我综合分歧
```

### 单 agent（效率优先）
明确只需一个视角时，不要多余 spawn：
- 纯竞品查询 → 只 product-analyst
- 纯内容生成 → 只 content-creator
- 纯增长数据 → 只 growth-strategist

## 讨论输出格式

### 团队快评（模式 B）
```
---
📊 **产品**: [1-3 句核心观点]
🚀 **增长**: [1-3 句核心观点]
✍️ **内容**: [1-2 句建议，如果相关]

**→ 行动建议**: [具体可执行的 1-2 个行动]
---
```

### 深度辩论（模式 C）
```
---
## 团队讨论: [主题]

**📊 产品分析** (product-analyst):
[完整分析段落]

**🚀 增长审查** (growth-strategist):
[对上述分析的审查 + 补充观点]

**共识**: [双方同意的部分]
**分歧**: [具体不同意见]
**我的判断**: [综合建议]
**需要你决定**: [列出 1-2 个关键决策点]
---
```

## 讨论质量要求

1. **具体不空泛** — "建议做用户调研" ✗ → "建议在 Canvas 添加反馈按钮收集 HITL 体验数据" ✓
2. **有数据支撑** — agent 必须先读项目文件再发表观点，不能凭空推测
3. **敢于分歧** — growth-strategist 的价值在于挑战 product-analyst，不是附和
4. **尊重时间** — 一人团队时间有限，每个建议必须评估投入产出比
5. **行动导向** — 每次讨论必须产出至少 1 个具体可执行的行动项

## 与 Skills 的融合

讨论产出可以直接转化为 skill 执行：

| 讨论结论 | 自动建议的 skill |
|----------|-----------------|
| "这个功能值得写一篇博客" | "要我执行 /vulca-write --blog 吗？" |
| "建议做一次设计审计" | "要我执行 /vulca-check --design 吗？" |
| "应该启动一个新 Phase" | "要我执行 /vulca-phase start 吗？" |
| "可以准备部署了" | "要我执行 /vulca-deploy --preflight 吗？" |
| "进化权重可能偏移了" | "要我执行 /vulca-evolve compare 吗？" |

## 与 Hooks 的数据流

```
instinct-logger (Stop hook)
  ↓ 记录操作模式
  ↓ 积累后可分析：
  ↓   - 哪些文件最常修改 → 产品热点
  ↓   - 哪些 Phase 耗时最长 → 优先级问题
  ↓   - bug 修复频率 → 质量问题

update-claude-md (Stop hook)
  ↓ 更新项目状态
  ↓ 被 SessionStart 注入
  ↓ 为下次会话的团队讨论提供基线

session-state-inject (SessionStart hook)
  ↓ 注入项目快照
  ↓ 团队讨论基于最新状态展开
```
