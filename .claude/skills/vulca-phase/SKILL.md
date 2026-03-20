---
name: vulca-phase
description: VULCA Phase 生命周期管理 — 启动、追踪、检查点、关闭开发阶段
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

管理 VULCA 项目的开发阶段（Phase）生命周期。

## 用法

```
/vulca-phase start <name> "<description>"   # 启动新 Phase
/vulca-phase status                          # 查看当前 Phase 状态
/vulca-phase checkpoint "<message>"          # 记录检查点
/vulca-phase close                           # 关闭当前 Phase
```

## Phase 状态文件

状态持久化在 `.claude/phase-current.json`:
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
1. 检查是否有未关闭的 Phase（如有，提醒先关闭）
2. 创建 `.claude/phase-current.json`
3. 运行 `git status` 记录起始状态
4. 输出 Phase 启动确认

### status — 查看状态
1. 读取 `.claude/phase-current.json`
2. 运行 `git diff --stat` 统计当前变更
3. 输出:
   - Phase 名称和描述
   - 已用时间
   - 变更文件列表
   - 检查点历史

### checkpoint — 记录检查点
1. 读取当前 Phase
2. 运行 `git diff --name-only` 记录变更文件
3. 可选: 运行快速测试验证
4. 追加检查点到 `phase-current.json`

### close — 关闭 Phase
1. 运行完整测试 (`/vulca-test`)
2. 统计最终变更
3. 更新 memory 记录（如有必要）
4. 归档 `phase-current.json` 内容
5. 删除 `phase-current.json`

## 注意

- Phase 状态文件在 `.gitignore` 中（不入库）
- 每个 Phase 应有明确的目标和完成标准
- close 前必须确认测试通过
