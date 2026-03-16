# 文心墨韵后端 API

基于 FastAPI + LangChain 的 AI 艺术创作评测平台后端服务。

## Quick Start

### As a Local App (Full UI + API)

```bash
pip install vulca[app]
vulca serve              # Opens browser to http://localhost:8001
```

### As an SDK (Lightweight, No Server)

```bash
pip install vulca
vulca evaluate painting.jpg                    # CLI evaluation
vulca evaluate painting.jpg --tradition chinese_xieyi  # With cultural context
```

```python
from vulca import evaluate

result = evaluate("painting.jpg")
print(result.score, result.tradition)
print(result.dimensions)  # L1-L5 scores
```

### Development Setup

```bash
git clone https://github.com/vulca-org/vulca.git
cd website/wenxin-backend
pip install -e ".[app,dev]"
vulca serve --port 8001
```

## 技术栈

- **框架**: FastAPI + Pydantic
- **数据库**: PostgreSQL + SQLAlchemy
- **缓存**: Redis
- **向量数据库**: Qdrant
- **任务队列**: Celery
- **AI框架**: LangChain + Transformers

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd wenxin-backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp .env.example .env
# 编辑 .env 文件，配置数据库等信息
```

### 2. 启动基础服务

```bash
# 启动 PostgreSQL, Redis, Qdrant
docker-compose up -d
```

### 3. 数据库迁移

```bash
# 初始化数据库
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. 启动应用

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

访问 http://localhost:8000/docs 查看 API 文档

## API 接口

### 认证相关
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录

### AI模型管理
- `GET /api/v1/models` - 获取模型列表
- `GET /api/v1/models/{id}` - 获取模型详情
- `POST /api/v1/models` - 创建模型 (管理员)
- `PUT /api/v1/models/{id}` - 更新模型 (管理员)
- `DELETE /api/v1/models/{id}` - 删除模型 (管理员)

### 评测系统 (开发中)
- `POST /api/v1/evaluations/start` - 开始评测
- `GET /api/v1/evaluations/{id}` - 获取评测状态
- `GET /api/v1/evaluations/history` - 评测历史

### 作品管理 (开发中)
- `GET /api/v1/works` - 作品列表
- `GET /api/v1/works/{id}` - 作品详情
- `GET /api/v1/works/similar` - 相似作品

## 项目结构

```
wenxin-backend/
├── app/
│   ├── api/           # API路由
│   ├── core/          # 核心配置
│   ├── models/        # 数据库模型
│   ├── schemas/       # Pydantic模式
│   ├── services/      # 业务逻辑
│   │   ├── ai_evaluation/  # AI评测服务
│   │   └── langchain/       # LangChain集成
│   └── tasks/         # Celery任务
├── alembic/           # 数据库迁移
├── tests/             # 测试文件
├── docker-compose.yml # Docker配置
└── requirements.txt   # 依赖列表
```

## 开发计划

- [x] 基础框架搭建
- [x] 用户认证系统
- [x] AI模型CRUD
- [ ] 评测引擎集成
- [ ] 向量数据库集成
- [ ] 任务队列系统
- [ ] WebSocket实时通信
- [ ] 前端API对接

## 环境变量

查看 `.env.example` 了解所需的环境变量配置。

## 测试

```bash
# 运行测试
pytest

# 测试覆盖率
pytest --cov=app tests/
```

## 部署

推荐使用 Docker 部署：

```bash
# 构建镜像
docker build -t wenxin-backend .

# 运行容器
docker run -d -p 8000:8000 --env-file .env wenxin-backend
```

## 许可证

MIT