---
name: vulca-grow
description: VULCA 增长与产品分析 — 竞品追踪、功能优先级、增长策略、定位验证
user-invocable: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Agent
  - WebSearch
  - WebFetch
---

# /vulca-grow — 增长与产品分析

多维度分析 VULCA 的产品和增长状况。

## 用法

```
/vulca-grow                       # 综合分析（产品+增长）
/vulca-grow --compete             # 竞品分析
/vulca-grow --position            # 定位验证
/vulca-grow --priorities          # 功能优先级评估
/vulca-grow --github              # GitHub 增长分析
/vulca-grow --academic            # 学术渗透分析
/vulca-grow "Midjourney v7 更新"  # 专题分析
```

## 自动触发条件

当用户自然语言提到以下话题时自动触发（无需 /vulca-grow）：
- 竞品动态："Midjourney 最近..."、"DALL-E 有什么新功能"
- 产品方向："下一步做什么"、"这个功能值不值得做"
- 增长策略："怎么推广"、"怎么获取用户"、"stars 增长"
- 定位讨论："我们和 X 有什么区别"、"VULCA 的优势是什么"

## 执行步骤

### 1. 上下文收集
- 读取 memory/ 中产品和增长相关记录
- 读取 docs/reports/ 最近的分析报告
- 读取 CLAUDE.md 了解当前产品状态

### 2. 分析执行（并行）

#### 产品分析（spawn product-analyst agent）
提供上下文 + 具体分析问题：
- 当前功能完成度
- 用户旅程断点
- 功能优先级建议

#### 增长策略（spawn growth-strategist agent）
提供上下文 + product-analyst 的初步发现：
- 审查产品分析结论
- 补充增长视角
- 给出策略建议

### 3. 综合汇总

将两个 agent 的发现合并，输出：

```
## VULCA 增长分析 [日期]

### 产品发现
- [product-analyst 的关键发现]

### 增长策略
- [growth-strategist 的策略建议]

### 行动清单
1. [立即] 具体行动
2. [本周] 具体行动
3. [长期] 方向性建议

### 风险提醒
- [需要注意的风险]
```

### 4. 持久化
- 关键结论 → memory/ 中更新相关记录
- 完整报告 → `docs/reports/growth-{date}-{topic}.md`
