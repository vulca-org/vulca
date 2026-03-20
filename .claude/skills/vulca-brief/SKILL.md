---
name: vulca-brief
description: VULCA 会话简报 — 汇总项目状态、agent 发现、推荐行动（每次会话自动或手动触发）
user-invocable: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Agent
  - WebSearch
---

# /vulca-brief — 会话简报

汇总项目全貌，给出多维度状态和推荐行动。

## 用法

```
/vulca-brief              # 完整简报
/vulca-brief --quick      # 快速简报（仅 git + phase 状态）
/vulca-brief --growth     # 增长视角简报
/vulca-brief --product    # 产品视角简报
```

## 自动触发条件

当用户以下述方式开始会话时，自动执行简报（无需 /vulca-brief）：
- "现在什么情况"、"项目状态"、"今天做什么"
- 打招呼或提出模糊问题
- 新会话开始时（结合 memory/feedback-session-start.md 规则）

## 执行步骤

### 1. 工程状态（30 秒）
```bash
git log --oneline -5                    # 最近提交
git status --short                       # 工作区状态
git diff --stat HEAD~1 HEAD             # 上次提交规模
```

检查是否有未关闭的 Phase（`.claude/phase-current.json`）。

### 2. 产品视角（可选，spawn product-analyst）
- 读取 memory/ 中的 product 相关记录
- 检查 docs/reports/ 最近的分析报告
- 如果距上次产品分析 >3 天，建议运行 `/vulca-grow`

### 3. 增长视角（可选，spawn growth-strategist）
- 读取 memory/ 中的 growth 相关记录
- 检查 docs/reports/ 最近的增长报告

### 4. 内容机会
- 检查最近几次 commit 是否有用户可见功能变更
- 如有，建议转化为内容（博客/推文/demo）

### 5. 汇总输出

```
## VULCA 简报 [日期]

### 工程
- 最近提交: [1-2 行摘要]
- 工作区: [干净/N 个未提交文件]
- Phase: [当前 phase 或"无活跃 phase"]
- 测试: [上次结果，如已知]

### 产品
- [最近的产品洞察或"无新发现，建议运行 /vulca-grow"]

### 增长
- [最近的增长洞察或"无新发现"]

### 推荐行动
1. [最高优先] 具体行动
2. [次优先] 具体行动
3. [可选] 具体行动
```
