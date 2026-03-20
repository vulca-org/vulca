---
name: vulca-test
description: VULCA 多层测试编排 — SDK/Backend/Frontend/E2E 测试运行和报告
user-invocable: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Agent
---

# /vulca-test — 多层测试编排

按层级运行 VULCA 项目测试。

## 用法

```
/vulca-test               # 自动检测变更，运行相关层级测试
/vulca-test --sdk         # 仅 SDK 单测 (vulca/)
/vulca-test --backend     # 仅后端单测 (wenxin-backend/)
/vulca-test --frontend    # 仅前端静态检查 (type-check + lint)
/vulca-test --e2e         # 仅 E2E 测试 (需后端运行)
/vulca-test --smoke       # 仅 smoke 测试 (user-journey)
/vulca-test --changed     # 仅测试变更文件相关的测试
```

## 执行步骤

### 1. 检测变更范围
```bash
CHANGED=$(git diff --name-only HEAD)
```

根据变更文件决定运行哪些层级:
- `vulca/**` → SDK tests
- `wenxin-backend/**` → Backend tests
- `wenxin-moyun/**` → Frontend tests
- 多层变更 → 按顺序全部运行

### 2. 按顺序执行

#### Layer 1: SDK Tests (最快)
```bash
cd /home/yhryzy/projects/website/vulca
.venv/bin/python -m pytest tests/ -v --tb=short 2>&1 | tail -30
```
期望: 218+ tests pass

#### Layer 2: Backend Tests
```bash
cd /home/yhryzy/projects/website/wenxin-backend
venv/bin/python -m pytest tests/ -v --tb=short 2>&1 | tail -30
```
期望: 14+ tests pass

#### Layer 3: Frontend Static
```bash
cd /home/yhryzy/projects/website/wenxin-moyun
npm run type-check 2>&1 | tail -20
npm run lint 2>&1 | tail -20
```
期望: 0 errors

#### Layer 4: E2E (可选，需后端)
```bash
cd /home/yhryzy/projects/website/wenxin-moyun
npm run test:e2e -- --reporter=line 2>&1 | tail -30
```
期望: 95+ tests pass

### 3. 输出报告

```
## vulca-test Results

| Layer | Tests | Pass | Fail | Skip |
|-------|-------|------|------|------|
| SDK   | 218   | 218  | 0    | 0    |
| Backend | 14  | 14   | 0    | 0    |
| Frontend | -  | type-check OK | lint OK | - |
| E2E   | 95    | 95   | 0    | 0    |

### Failures (if any)
- [test_name] error message
```
