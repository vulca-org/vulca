# [任务-11-25-19-50] Didot Exhibition API - Echoes and Returns 展览数据与对话生成

**创建时间**: 2025-11-25 19:50
**状态**: 计划中
**优先级**: 高

## 需求来源
用户需要将 Didot_exhibition_Dec 文件夹中的 "Echoes and Returns" 展览数据（87件艺术作品）：
1. 使用Claude Agent生成多角色视角的艺术评论对话
2. 存储到LanceDB向量数据库
3. 提供RESTful API供第三方开发者使用

## 目标和范围

**主要目标**:
- 为87件展览作品生成9种对话版本（1个basic + 8个角色视角）
- 使用LanceDB存储所有数据和向量嵌入
- 创建完整的RESTful API

**范围**:
- 数据源: `<project-root>/Didot_exhibition_Dec/Echoes and Returns.json`
- 角色: 沿用EMNLP2025-VULCA的8个personas
- 后端: `<project-root>/wenxin-backend/`
- 新模块: `app/exhibition/`

**排除**:
- 前端页面（数据和API完成后再开发）
- 图片上传（使用现有阿里云OSS链接）

## 关键约束

### 技术约束
- 使用LanceDB作为向量数据库（本地嵌入式）
- 使用现有anthropic SDK (v0.64.0)生成对话
- 遵循现有FastAPI项目结构
- 图片通过阿里云OSS URL访问，支持resize参数

### 数据约束
- 87件作品 × 9个对话版本 = 783个对话记录
- 每个对话包含多个TEXT段落 + JSON结构化评价
- 需要生成向量嵌入用于语义搜索

### 业务约束
- API需要对外开放，需考虑认证和限流
- 对话生成需要调用Claude API，需考虑成本和速率限制

## 架构影响评估

### 新增组件
```
wenxin-backend/
├── app/
│   └── exhibition/              # 新模块
│       ├── __init__.py
│       ├── models/              # LanceDB数据模型
│       │   ├── __init__.py
│       │   ├── artwork.py
│       │   ├── conversation.py
│       │   └── persona.py
│       ├── services/            # 业务逻辑
│       │   ├── __init__.py
│       │   ├── lancedb_service.py
│       │   ├── dialogue_generator.py
│       │   └── image_processor.py
│       ├── schemas/             # Pydantic schemas
│       │   ├── __init__.py
│       │   └── exhibition_schema.py
│       └── api/                 # FastAPI路由
│           ├── __init__.py
│           └── exhibition_routes.py
├── data/
│   └── exhibition/              # LanceDB数据存储
│       └── echoes_returns.lance
└── scripts/
    └── generate_dialogues.py    # 对话生成脚本
```

### 依赖变更
- 新增: `lancedb>=0.4.0`
- 新增: `sentence-transformers` (已有，用于向量嵌入)

### 与现有系统集成
- 复用现有认证系统 (OAuth2)
- 可选：集成到主API路由

## 关键决策记录

### 决策1: 使用LanceDB而非扩展PostgreSQL
**理由**:
- LanceDB是嵌入式向量数据库，无需额外服务
- 原生支持向量搜索和多模态数据
- 与Python生态集成良好
**权衡**: 无法使用SQL关联查询，但展览数据独立性强，影响不大

### 决策2: 对话生成采用批处理模式
**理由**:
- 87件作品 × 9个版本 = 783次API调用
- 批处理可以更好地处理速率限制和失败重试
- 生成结果持久化，避免重复调用
**权衡**: 初始生成时间较长，但一次生成多次使用

### 决策3: 向量嵌入使用sentence-transformers本地模型
**理由**:
- 无需额外API调用成本
- 项目已有该依赖
- 支持中英文多语言
**权衡**: 本地计算需要一定资源，但在可接受范围内

## 执行计划

### Phase 1: 基础设施搭建
1. [ ] 安装LanceDB依赖
2. [ ] 创建exhibition模块目录结构
3. [ ] 定义LanceDB数据模型
4. [ ] 实现LanceDB服务层

### Phase 2: 数据导入
5. [ ] 解析Echoes and Returns.json数据
6. [ ] 导入作品和艺术家信息到LanceDB
7. [ ] 复制8个persona定义文件

### Phase 3: 对话生成
8. [ ] 实现Claude对话生成服务
9. [ ] 定义对话输出结构（TEXT + JSON）
10. [ ] 实现批量生成脚本（支持断点续传）
11. [ ] 生成basic版本对话
12. [ ] 生成8个角色视角对话

### Phase 4: 向量嵌入
13. [ ] 为对话内容生成向量嵌入
14. [ ] 存储嵌入到LanceDB

### Phase 5: API开发
15. [ ] 创建FastAPI路由模块
16. [ ] 实现作品列表/详情API
17. [ ] 实现对话获取API
18. [ ] 实现语义搜索API
19. [ ] 添加API认证和限流

### Phase 6: 测试与文档
20. [ ] 编写API测试用例
21. [ ] 生成API文档（OpenAPI/Swagger）
22. [ ] 编写使用说明

## 数据模型设计

### Artwork (作品)
```python
class Artwork:
    id: int                    # 原始ID
    title: str                 # 作品标题
    description: str           # 作品描述
    chapter_id: int            # 章节ID
    chapter_name: str          # 章节名称
    categories: str            # 分类标签
    medium: str                # 媒介
    material: str              # 材料
    size: str                  # 尺寸
    create_year: str           # 创作年份
    image_urls: List[str]      # 图片URL列表
    custom_url: str            # 外部链接
    artist_id: int             # 艺术家ID
    vector: List[float]        # 描述向量嵌入
```

### Artist (艺术家)
```python
class Artist:
    id: int                    # 用户ID
    first_name: str
    last_name: str
    nickname: str
    school: str                # 学校
    major: str                 # 专业
    graduation_year: str       # 毕业年份
    profile: str               # 简介
    bio: str                   # 详细介绍
    email: str
    avatar_url: str
    vector: List[float]        # profile向量嵌入
```

### Conversation (对话)
```python
class Conversation:
    id: str                    # UUID
    artwork_id: int            # 作品ID
    persona_id: str            # 角色ID (basic/su_shi/guo_xi/...)
    persona_name: str          # 角色名称
    text_segments: List[str]   # TEXT段落列表
    structured_analysis: dict  # JSON结构化分析
    created_at: datetime
    vector: List[float]        # 对话内容向量嵌入
```

### Persona (角色)
```python
class Persona:
    id: str                    # 角色ID
    name: str                  # 角色名称
    name_cn: str               # 中文名
    type: str                  # real/fictional
    description: str           # 简介
    style: str                 # 批评风格
    attributes: dict           # 数值属性
    sample_phrases: List[str]  # 典型语录
    system_prompt: str         # 完整prompt
```

## API端点设计

### 作品相关
```
GET  /api/v1/exhibition/artworks              # 作品列表（分页、筛选）
GET  /api/v1/exhibition/artworks/{id}         # 作品详情
GET  /api/v1/exhibition/artworks/search       # 语义搜索
GET  /api/v1/exhibition/chapters              # 章节列表
```

### 对话相关
```
GET  /api/v1/exhibition/artworks/{id}/conversations           # 作品所有对话
GET  /api/v1/exhibition/artworks/{id}/conversations/{persona} # 特定角色对话
GET  /api/v1/exhibition/conversations/search                  # 对话语义搜索
```

### 角色相关
```
GET  /api/v1/exhibition/personas              # 所有角色
GET  /api/v1/exhibition/personas/{id}         # 角色详情
```

### 艺术家相关
```
GET  /api/v1/exhibition/artists               # 艺术家列表
GET  /api/v1/exhibition/artists/{id}          # 艺术家详情
GET  /api/v1/exhibition/artists/{id}/artworks # 艺术家作品
```

## 当前进度
- [x] 需求分析完成
- [x] 数据结构理解
- [x] 技术选型确定
- [x] LanceDB安装和配置
- [x] exhibition模块创建完成
- [x] 数据导入完成 (87件作品, 72位艺术家)
- [x] Claude多模态对话生成服务实现
- [x] 测试对话生成成功
- [x] FastAPI路由和API Key认证完成
- [ ] 生成全部87件作品的对话数据 (待用户启动)

## 已解决问题
1. ✅ 对话生成使用Claude多模态分析图片
2. ✅ API认证方式：简单API Key (X-API-Key header)
3. ✅ 多模态输入：成功实现图片分析

## 生成对话命令
```bash
# 生成全部对话 (87作品 x 9角色 = 783个对话)
cd <project-root>/wenxin-backend
source .env && python3 scripts/generate_dialogues.py --db-path data/exhibition

# 只生成特定作品
python3 scripts/generate_dialogues.py --artwork-id 1759494368418

# 只生成特定角色
python3 scripts/generate_dialogues.py --persona su_shi --persona guo_xi
```

## 用户对话记录

### 第1轮 [2025-11-25 19:30] - 研究模式
**用户原文**: 我现在需要使用 Didot_exhibition_Dec 里面的数据，继续生成对话的数据，这是我的另一个展览，也需要在现在的主网站上面，添加一个这个新的展览的板块。然后，把这个板块分出一个api，让其他的开发者去使用。数据在这个Didot_exhibition_Dec 文件夹里面，有json, csv数据。然后： https://help.aliyun.com/zh/oss/user-guide/resize-images-4 具体看一下这个文档。先理解一下我的需求
**关键要点**:
- 数据源: Didot_exhibition_Dec/Echoes and Returns.json (87件作品)
- 需求: 生成对话数据 + 主网站展览板块 + 独立API
- 图片处理: 阿里云OSS支持resize参数

### 第2轮 [2025-11-25 19:40] - 研究模式
**用户原文**: 参考目前这个项目之前的 潮汐的赋性 的这个板块里面的对话数据
**关键要点**:
- 参考EMNLP2025-VULCA项目的对话数据格式
- 包含knowledge_base.json + personas + mllm_outputs结构
- 对话格式: TEXT段落 + JSON结构化评价

### 第3轮 [2025-11-25 19:50] - 任务确认模式
**用户原文**: 1. 沿用现有8个角色 2. 对话内容使用claude agent生成 3. 对话数据+API，前端板块可以这些数据和api能够正确的使用了之后再搭建。数据要使用lanceDB 来存储。
**关键要点**:
- 角色: 沿用8个personas（苏轼、郭熙、John Ruskin等）
- 生成方式: Claude Agent (anthropic SDK)
- 优先级: 对话数据 + API优先，前端后续
- 存储: LanceDB向量数据库
