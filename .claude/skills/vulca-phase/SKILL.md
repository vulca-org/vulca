---
name: vulca-phase
description: VULCA Phase 生命周期管理 — 启动、追踪、检查点、关闭开发阶段（支持多 Phase 并行）
user-invocable: true
allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Bash
---

# /vulca-phase — Phase 生命周期管理

## 实时上下文
!`cd /home/yhryzy/projects/website && echo "Active Phases:" && ls .claude/phases/phase-*.json 2>/dev/null | while read f; do python3 -c "import json; d=json.load(open('$f')); print(f\"  {d.get('name','?')}: {d.get('description','')} ({len(d.get('checkpoints',[]))} checkpoints)\")" 2>/dev/null; done || echo "  None" && echo "Recent commits:" && git log --oneline -3 2>/dev/null`

管理 VULCA 项目的开发阶段（Phase）生命周期。支持多 Phase 并行工作。

## 用法

```
/vulca-phase start <name> "<description>"       # 启动新 Phase
/vulca-phase status [name]                       # 查看指定/所有 Phase 状态
/vulca-phase checkpoint <name> "<message>"       # 记录检查点
/vulca-phase close <name>                        # 关闭指定 Phase
```

## Phase 状态文件

每个 Phase 独立持久化在 `.claude/phases/phase-{name}.json`:
```json
{
  "name": "Phase C1",
  "description": "Canvas 交互优化",
  "started_at": "2026-03-20T14:00:00Z",
  "checkpoints": [
    {"time": "2026-03-20T15:00:00Z", "message": "WeightSliders 组件完成"}
  ],
  "files_changed": [],
  "tests_status": {}
}
```

## 执行步骤

### start — 启动新 Phase
1. 确保 `.claude/phases/` 目录存在
2. 检查 `.claude/phases/phase-{name}.json` 是否已存在（如有，提醒该 Phase 已在运行）
3. 创建 `.claude/phases/phase-{name}.json`
4. 运行 `git status` 记录起始状态
5. 输出 Phase 启动确认 + 当前所有活跃 Phase 列表

### status — 查看状态
- **带 name**: 读取 `.claude/phases/phase-{name}.json`，运行 `git diff --stat` 统计变更
- **不带 name**: 列出 `.claude/phases/phase-*.json` 所有活跃 Phase 摘要
- 输出: Phase 名称、描述、已用时间、变更文件、检查点历史

### checkpoint — 记录检查点
1. 读取 `.claude/phases/phase-{name}.json`
2. 运行 `git diff --name-only` 记录变更文件
3. 可选: 运行快速测试验证
4. 追加检查点到对应 phase 文件

### close — 关闭 Phase
1. 运行完整测试 (`/vulca-test`)
2. 统计最终变更
3. 更新 memory 记录（如有必要）
4. 归档 phase 文件内容
5. 删除 `.claude/phases/phase-{name}.json`

## 迁移

如果存在旧版 `.claude/phase-current.json`，在任何命令执行时自动迁移：
1. 读取 `phase-current.json` 中的 `name` 字段，提取 Phase 名称（如 "Phase C1" → "C1"）
2. 移动到 `.claude/phases/phase-{name}.json`
3. 删除 `phase-current.json`

## 注意

- Phase 状态文件在 `.gitignore` 中（不入库）
- 每个 Phase 应有明确的目标和完成标准
- close 前必须确认测试通过
- 多个 session 可以各自操作不同的 Phase，互不干扰
