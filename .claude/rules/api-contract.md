---
paths:
  - "wenxin-backend/app/**/*.py"
  - "wenxin-moyun/src/utils/**/*.ts"
  - "wenxin-moyun/src/hooks/**/*.ts"
---

# API Contract Rules

编辑后端路由或前端 API 调用时必须遵守以下合约。

## 核心端点

### 认证 (OAuth2)
```
POST /auth/register   — JSON body
POST /auth/login      — form-urlencoded (不是 JSON!)
GET  /auth/me         — Bearer token
```

**login 必须使用 form-urlencoded**:
```typescript
const formParams = new URLSearchParams();
formParams.append('username', username);
formParams.append('password', password);
```

### Canvas Pipeline
```
POST   /prototype/runs/create        — CreateRunRequest → task_id
GET    /prototype/runs/{task_id}      — RunStatusResponse
POST   /prototype/runs/{task_id}/action — HITL Accept/Refine/Reject
POST   /prototype/runs/{task_id}/instruct — 追加指令
GET    /prototype/gallery             — GalleryResponse
GET    /prototype/traditions          — TraditionListResponse
GET    /prototype/evolution/suggestions — EvolutionSuggestionsResponse
POST   /prototype/feedback            — FeedbackRequest
POST   /prototype/runs/create         — image_base64 参数支持图片评估
```

## Status 枚举

**必须使用小写字符串**:
```python
# 正确
status = "running"  # "idle" | "running" | "completed" | "failed" | "waiting_human"

# 错误 — 这个 bug 导致所有创作显示失败
status = RunStatus.COMPLETED.value  # 如果 enum 定义大写，.value 也是大写
```

前端判断时统一转小写:
```typescript
const status = data.status?.toLowerCase();
```

## Schema 同步规则

1. 修改 `wenxin-backend/app/prototype/api/schemas.py` 时，**必须同步**前端 TypeScript 类型
2. 修改前端 API 调用参数时，**必须验证**后端 route handler 接受该参数
3. 新增端点时，必须在 CLAUDE.md 的端点列表中记录

## CORS 调试

后端 500 错误没有 CORS 头 → 浏览器报 CORS 错误。**先看后端日志**，不要改 CORS 配置。

```bash
# 调试步骤
# 1. 看后端日志 (不是前端 console)
docker logs <container> 2>&1 | tail -20
# 2. 确认是 500 不是 CORS
curl -v http://localhost:8001/prototype/runs/create -d '{...}'
```

## 模型接口差异

不同 AI 模型有特殊参数要求:
```python
'gpt-5': max_completion_tokens=500       # 不是 max_tokens
'o1': # 无 system messages，无 temperature
'deepseek-chat': # 用于 R1/V3，不是 deepseek-reasoner
'claude-opus-4-1-20250805': # temperature 和 top_p 不能同时设
```

## 限额

- Guest 每日限额: `_GUEST_DAILY_LIMIT = 50`
- 可通过 `VULCA_DAILY_LIMIT` 环境变量覆盖
- Demo 模式默认使用 mock provider（无 API 成本）
