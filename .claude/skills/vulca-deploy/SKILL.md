---
name: vulca-deploy
description: VULCA 安全部署 — 预检查、构建、部署前端/后端到 GCP
user-invocable: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# /vulca-deploy — 安全部署

## 实时上下文
!`cd /home/yhryzy/projects/website && echo "Branch: $(git branch --show-current)" && echo "Uncommitted: $(git status --porcelain 2>/dev/null | wc -l) files" && echo "Last commit: $(git log --oneline -1)" && echo "bcrypt: $(grep 'bcrypt==' wenxin-backend/constraints.txt 2>/dev/null || echo 'not found')"`

VULCA 项目的安全部署流程。

## 用法

```
/vulca-deploy --preflight   # 仅预检查，不执行部署
/vulca-deploy --frontend    # 仅部署前端 (Firebase Hosting)
/vulca-deploy --backend     # 仅部署后端 (Cloud Run)
/vulca-deploy --full        # 完整部署（前端 + 后端）
```

## 预检查清单

每次部署前自动执行:

### 1. Git 状态
```bash
# 确认所有文件已跟踪
git status
# 确认在正确的分支
git branch --show-current
```

### 2. 测试通过
```bash
# SDK
cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m pytest tests/ -q

# Backend
cd /home/yhryzy/projects/website/wenxin-backend && venv/bin/python -m pytest tests/ -q

# Frontend
cd /home/yhryzy/projects/website/wenxin-moyun && npm run type-check && npm run lint
```

### 3. 构建验证
```bash
# Frontend build
cd /home/yhryzy/projects/website/wenxin-moyun && npm run build
```

### 4. 关键约束
- bcrypt 版本检查: `grep 'bcrypt==' wenxin-backend/constraints.txt` → 必须 4.0.x
- 环境变量: 不包含 `.env` 文件
- 端口绑定: Dockerfile 使用 `${PORT:-8080}` 和 `0.0.0.0`

## 部署步骤

### Frontend (Firebase Hosting)
```bash
cd /home/yhryzy/projects/website/wenxin-moyun
npm run build
# firebase deploy --only hosting (需要 firebase CLI)
```

### Backend (Cloud Run)
```bash
cd /home/yhryzy/projects/website/wenxin-backend
# Docker build + push to Artifact Registry
# gcloud run deploy (需要 gcloud CLI)
```

## GCP 配置参考

- Region: `asia-east1`
- Frontend: Firebase Hosting → vulcaart.art
- Backend: Cloud Run
- Database: Supabase PostgreSQL
- Secrets: Google Secret Manager

## 安全提醒

- **不要**在部署命令中包含敏感信息（API keys, passwords）
- **不要** force push 到 master
- 部署前确认 `init_db.py` 已在目标环境运行
- CI/CD (GitHub Actions) 是推荐的部署方式，手动部署仅用于紧急修复
