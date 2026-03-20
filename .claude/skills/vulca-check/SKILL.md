---
name: vulca-check
description: VULCA 预提交验证 — 检查设计系统、API 合约、Pipeline 规范和代码质量
user-invocable: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Agent
---

# /vulca-check — 预提交验证

对当前变更运行 VULCA 项目规范检查。

## 用法

```
/vulca-check              # 自动检测变更文件，运行所有相关检查
/vulca-check --design     # 仅设计系统检查
/vulca-check --api        # 仅 API 合约检查
/vulca-check --pipeline   # 仅 Pipeline 规范检查
/vulca-check --quick      # 快速检查（仅语法和导入）
/vulca-check --audit      # 全量审计（不限于变更文件）
```

## 执行步骤

### 1. 收集变更文件
```bash
# 获取当前变更
git diff --name-only HEAD
git diff --name-only --cached
git diff --name-only
```

### 2. 分类检查

#### 设计系统检查（前端文件 .tsx/.ts/.css）
使用 design-reviewer agent 或手动检查:
- 搜索硬编码违规颜色 (`#334155`, `#FAF7F2`, `#1e293b`)
- 搜索 `border-` 类名（No-Line Rule）
- 验证 `Object.entries/keys/values` 有 null guard
- 验证 `.toFixed(` 有 null check
- 验证交互元素 ≥44px

#### API 合约检查（后端 routes + schemas + 前端 API 调用）
使用 contract-reviewer agent 或手动检查:
- schemas.py 变更 → 检查前端类型同步
- 前端 fetch/axios 调用 → 检查 URL 和参数匹配
- status 枚举使用小写

#### Pipeline 规范检查（vulca/ + prototype/）
- 搜索禁止导入: `from app.vulca`, `from app.prototype.graph`, `import novita_client`
- 验证新代码走 `vulca.pipeline.execute()` 而非创建新执行路径
- 检查 bcrypt 版本约束 (4.0.x)

### 3. 快速检查
```bash
# Python 语法
cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m py_compile <changed.py>

# TypeScript 类型
cd /home/yhryzy/projects/website/wenxin-moyun && npx tsc --noEmit
```

### 4. 输出报告

```
## vulca-check Results

### Errors (必须修复)
- [file:line] 描述

### Warnings (建议修复)
- [file:line] 描述

### Summary
- 检查文件数: N
- Errors: N
- Warnings: N
```
