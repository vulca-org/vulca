# VULCA 产品路线图 v3（2026-03-04 起）

> **定位**：文化 AI 评估框架 — 社区驱动 + 多入口 + Canvas 可视化
> **哲学**：OpenClaw 式松散框架 — TRADITION.yaml = SKILL.md，降低贡献门槛
> **技术栈**：Gemini API 单栈（NB2 + VLM + LLM）
> **对标**：OpenClaw（社区框架）+ ComfyUI（插件生态）+ LOVART/TapNow（Canvas 交互）
> **核心差异**：竞品做"更好的图"，VULCA 做"文化上对不对" — Build/Explore 零竞争
> **维护方式**：每完成一项打 ✅ 并注明日期，阻塞项标 🚫 并说明原因

---

## 前置状态（已完成，不再重复）

| 模块 | 完成度 | 关键产出 |
|------|--------|----------|
| L1-L5 评估框架 | ✅ 100% | EMNLP 2025 发表 |
| 消融实验 | ✅ 480 runs | 16 conditions, peak 0.917, 论文数据锁定 |
| Agent 管线 Phase 0-3 | ✅ 98% | LangGraph 5 模板 + NodeSpec + 拓扑校验 + 并行 Critic |
| 前端 UI 骨架 | ✅ 完整 | 10 React 组件 + SSE + HITL |
| 全链路联调 | ✅ Mock + FLUX + NB2 真实 | 23 SSE events, peak 0.917 |
| ACM MM 论文 | ✅ 润色完成 (2026-03-06) | 29 refs, 160w abstract, 投稿就绪 |

---

## Milestone 0: Gemini 迁移 + 清理（1-2 周）

> **目标**：从 4 供应商统一为 Gemini 单栈，砍掉无效代码路径
> **M0.1 状态**：✅ 代码准备 + 全量审查修复完成 (2026-03-05)
> **M0.2 状态**：✅ 端到端验证通过 (2026-03-05) — wangjindong key 已激活

### 0.1 代码准备（不依赖 key，现在可做）

- [x] **model_router.py 重构**：添加 `gemini_direct` provider 配置，globalai.vip 降级为 fallback ✅ 2026-03-05
  - 文件：`app/prototype/agents/model_router.py`
  - 改动：新增 Gemini 2.5 Flash/Pro 直连路由，保留 globalai.vip 作为过渡期 fallback
- [x] **砍掉 FLUX 生成路径**：`TogetherFluxProvider` 从默认 provider 列表移除 ✅ 2026-03-05
  - 文件：`app/prototype/agents/draft_provider.py`
  - NB2 成为唯一生成器（`NB2Provider` 已完整实现）
  - `TogetherFluxProvider` 代码保留但标记 deprecated（消融实验复现需要）
- [x] **砍掉 FLUX Fill 路径**：`FluxFillProvider` 从 Loop 链路移除 ✅ 2026-03-05
  - 文件：`app/prototype/agents/flux_fill_provider.py`, `orchestrator.py`
  - 依据：Loop +0.002 ns, Ghost Loop 30/30 首轮通过
  - 代码保留但标记 deprecated
- [x] **环境变量清理**：`.env` 中 `TOGETHER_API_KEY` / `FAL_KEY` 标记为 optional/deprecated ✅ 2026-03-05
- [x] **requirements 清理**：`requirements.render.txt` 中移除 fal-client 依赖（如有） ✅ 2026-03-05

### 0.2 Key 激活后验证

- [x] **Gemini 文本测试**：Gemini 2.5 Flash 文本推理（替代 DeepSeek V3.2）✅ 2026-03-05
- [x] **Gemini VLM 测试**：Gemini 2.5 Flash Vision L1-L5 评分（替代 globalai.vip 代理）✅ 2026-03-05
- [x] **NB2 测试**：gemini-3.1-flash-image-preview 图像生成（4张写意山水，127.8s）✅ 2026-03-05
- [x] **端到端真实模式**：NB2 + Gemini VLM 全链路，得分 0.964（首轮 accept）✅ 2026-03-05
- [x] **成本验证**：$0.268/run（4张NB2），符合预期 ✅ 2026-03-05

---

## Milestone 1: 速度优化（1 周）

> **目标**：250s → 60s，Playground 体验的前提
> **依赖**：M0.2 完成（需要真实 API 测速）

- [x] **启用 ParallelDimensionScorer**：PipelineOrchestrator 新增 `enable_parallel_critic` 参数，走 `build_critique_output` + ThreadPoolExecutor 并行路径 ✅ 2026-03-05
  - 文件：`orchestrator.py`, `parallel_scorer.py`, `api/schemas.py`, `api/routes.py`
  - 预期：Critic 阶段从 ~150s → ~40s（5 并行 vs 5 串行）
- [x] **Scout 缓存**：`gather_evidence()` 实例级 dict 缓存 + deepcopy 隔离 ✅ 2026-03-05
  - 文件：`app/prototype/tools/scout_service.py`
- [x] **NB2 超时调优**：`genai.Client` 添加 `http_options={"timeout": self._timeout}` ✅ 2026-03-05
  - 文件：`app/prototype/agents/nb2_provider.py`
- [x] **CLIP 加载优化**：ImageScorer 添加 `threading.Lock` 双重检查锁，线程安全单例 ✅ 2026-03-05
  - 文件：`app/prototype/agents/image_scorer.py`
- [x] **端到端计时**：✅ 2026-03-06 — 全链路 ~50s（目标 < 60s 达成）
  - ✅ NB2 **付费层已确认**（Imagen 4.0 可用 + RPM 无限制 + wangjindong 开通 billing）
  - ✅ google-genai v1.21 API 兼容修复：ImageConfig 移除 + timeout 单位 s→ms + **response.parts→candidates[0].content.parts**
  - ✅ 实测数据：NB2 生成 27-33s + VLM Critic 17.7s = **~50s total**
  - ✅ 评分稳定：japanese_traditional 0.950, islamic_geometric 0.95, western_academic 1.0

---

## Milestone 2: Playground 核心（2-3 周）⭐ 当前重点

> **目标**：从"表单→等待→结果"升级为交互式 Playground
> **参考**：LOVART 的 ChatCanvas + TapNow 的 Node-Wire-Canvas
> **依赖**：M1 完成（速度可接受后才有交互体验）

### 2.1 布局重组

- [x] **Playground 页面骨架**：`/prototype` 从单列表单重组为三栏布局 ✅ 2026-03-05
  ```
  ┌─────────────────────────────────────────────┐
  │  左栏: 控制面板    │  中栏: Canvas/结果   │  右栏: Agent 面板  │
  │  - 模板选择器      │  - 候选图画廊       │  - 实时事件流      │
  │  - 参数配置        │  - 雷达图          │  - 决策时间线      │
  │  - 快速预设        │  - 文化解读        │  - HITL 操作区     │
  └─────────────────────────────────────────────┘
  ```
  - 文件：`wenxin-moyun/src/pages/prototype/PrototypePage.tsx`（重构）
  - 复用：`TemplateSelector.tsx` + `TopologyViewer.tsx`（Phase 3 已有）

### 2.2 模板驱动体验

- [x] **模板选择联动**：选不同模板 → 动态显示/隐藏参数项 ✅ 2026-03-05
  - `TEMPLATE_FIELD_CONFIG`: fast_draft/critique_only/interactive_full/batch_eval 各有字段显隐规则
  - 新增 Parallel Critic 开关（默认开启，Graph Mode 时禁用）
- [x] **快速预设场景**：一键填充常见参数组合 ✅ 2026-03-05
  - 6 个文化预设：水墨山水/工笔花鸟/Ukiyo-e/Persian/African/South Asian
  - 前端 `PRESETS` 数组，用户可扩展

### 2.3 Agent 实时面板

- [x] **事件流美化**：卡片式 Agent 活动日志 ✅ 2026-03-05
  - `PipelineProgress.tsx`: 5 Agent 颜色标识 + emoji + 展开/折叠事件日志
  - 每事件显示：阶段/状态徽标/轮次/耗时/详情摘要
- [x] **进度可视化**：管线拓扑图实时高亮当前执行节点 ✅ 2026-03-05
  - `TopologyViewer` 接收 `currentStage` + `completedStages` + `stageDurations`
- [x] **HITL 交互**：Scout/Draft/Critic/Queen 四阶段暂停点全部实现 ✅ 2026-03-05
  - Scout 暂停：展示检索到的证据，用户可编辑/添加
  - Draft 暂停：展示候选图，用户可选择/否决
  - Critic 暂停：展示评分，用户可覆写分数
  - Queen 暂停：展示决策建议，用户确认/修改
  - 后端 `orchestrator.py` 3 处新增 + 前端 `HitlOverlay.tsx` 已适配

### 2.4 结果 Canvas

- [x] **多变体展示**：CandidateGallery 接入 scoredCandidates + rounds props ✅ 2026-03-05
- [x] **文化解读卡片**：VLM Critic 文化分析 + Scout 证据详情 ✅ 2026-03-05
  - `CriticRationaleCard`: L1-L5 维度颜色编码 + 自然语言解读 + [文化标签] 高亮
  - `ScoutEvidenceCard`: 统计概览 + 可展开术语标签/样本匹配/禁忌详情
- [x] **"调整重跑"**：基于当前结果微调参数再跑 ✅ 2026-03-05
  - `RunConfigForm` 新增 `initialValues` prop，完成后预填上次参数
  - Scout 证据缓存自动保留（后端实例级缓存）
  - 用户可修改 subject/tradition/其他参数后重跑

---

## Milestone 3: 弹性管线 Canvas（2-3 周）✅ 完成 2026-03-05

> **目标**：用户可视化编辑管线拓扑，自定义 Agent 组合
> **参考**：TapNow 的 Node-Wire-Group 架构
> **依赖**：M2 完成
> **产出**：8 个新文件 + 5 个修改文件，Playwright 全部测试通过（0 error）

### 3.1 节点拖拽编辑器

- [x] **可视化管线编辑器**：基于 React Flow (`@xyflow/react` v12+) ✅ 2026-03-05
  - 节点 = Agent（Scout/Router/Draft/Critic/Queen/Archivist）
  - 边 = 数据流（含条件边：Queen→rerun 循环）
  - 从预设模板加载初始拓扑，用户可拖拽修改
  - 文件：`editor/PipelineEditor.tsx`(~300行) + `editor/AgentNode.tsx` + `editor/types.ts`
- [x] **实时拓扑校验**：用户修改拓扑时，调用 `POST /topologies/validate` 实时反馈 ✅ 2026-03-05
  - 合法：绿色 "Valid" 徽章
  - 非法：红色 "N errors" 徽章 + 错误描述
  - debounce 500ms 防抖
- [x] **保存/加载自定义模板**：用户创建的管线可保存为自定义模板 ✅ 2026-03-05
  - 前端 localStorage 存储（最多 10 个）
  - Save/Delete 按钮 + 模板下拉选择

### 3.2 参数暴露

- [x] **节点级参数编辑**：点击节点 → 右侧抽屉展开参数面板 ✅ 2026-03-05
  - Scout: 检索深度、术语源选择
  - Draft: 候选数、Seed Base、Enhance Prompt
  - Critic: L1-L5 权重手动覆写（归一化警告）、LLM Scoring 开关
  - Queen: accept 阈值、max_rounds、rerun 策略
  - 文件：`editor/NodeParamPanel.tsx` + `editor/agentParamSchema.ts`（schema-driven）
- [x] **传统权重可视化**：9 传统 × 5 维度的权重矩阵热力图 ✅ 2026-03-05
  - CSS Grid 热力图 + heatColor() 颜色映射
  - 嵌入 Critic NodeParamPanel 底部
  - 文件：`editor/TraditionWeightGrid.tsx`

### 3.3 批量模式

- [x] **batch_eval 模板 UI**：多任务输入（CSV/多行文本）→ 批量执行 → 汇总报告 ✅ 2026-03-05
  - 进度条：N/M 完成 + Abort 按钮
  - 结果表格：每任务 L1-L5 评分 + 总分 + 状态
  - 导出：CSV
  - 文件：`BatchInputPanel.tsx`

---

## Milestone 4: B 端 API + 文化合规服务（1-2 周）

> **目标**：critique_only 模板包装为公开 API
> **依赖**：M1 完成（速度优化后 API 响应时间可接受）
> **状态**：✅ 全部完成 (2026-03-06)

- [x] **文化诊断 API**：`POST /api/v1/evaluate` ✅ 2026-03-06
  - 输入：图片 URL/base64 + tradition（可选，不传则自动识别）
  - 输出：L1-L5 评分 + 自然语言诊断 + 改进建议 + 文化禁忌警告
  - 底层：VLMCritic + CulturalPipelineRouter + ScoutService（直调，不经过 Orchestrator）
- [x] **传统识别 API**：`POST /api/v1/identify-tradition` ✅ 2026-03-06
  - 输入：图片
  - 输出：最可能的文化传统 + 置信度 + 推荐权重配置
  - 底层：VLMCritic prompt + CulturalPipelineRouter
- [x] **API 文档**：OpenAPI/Swagger 自动生成（FastAPI 已支持）✅ 2026-03-06
- [x] **API Key 管理**：Bearer token + 滑动窗口速率限制 30 req/min ✅ 2026-03-06
  - `VULCA_API_KEYS` 环境变量（逗号分隔），`auth.py` 认证中间件
- [x] **定价页更新**：4 档定价（Free/Pilot/API/Enterprise）+ 代码示例 + 对比表 ✅ 2026-03-06
- **新建文件**：`evaluate_schemas.py`, `image_utils.py`, `auth.py`, `evaluate_routes.py`
- **修改文件**：`main.py`, `PricingPage.tsx`

---

## Milestone 5: 内容完善 + 生态（持续）

> **目标**：所有文化相关内容集合在平台内
> **M5.1 状态**：✅ 知识库数据+API+前端页面 完成 (2026-03-06)
> **M5.2 状态**：✅ Gallery 页面 完成 (2026-03-06)
> **M5.3 状态**：✅ i18n 三语基础 完成 (2026-03-06)

### 5.1 知识库扩展

- [x] **9 传统知识库审计**：检查每个传统的术语覆盖度、禁忌条目数、构图参考数 ✅ 2026-03-06
  - 审计发现：japanese_traditional 完全空白（0 术语/0 禁忌/0 基准任务），5 传统仅 3 术语
  - 修复：japanese_traditional 新增 6 术语（ukiyo-e/wabi-sabi/ma/sumi-e/kintsugi/Rimpa）+ 2 禁忌
  - 扩展：chinese_gongbi/islamic_geometric/watercolor/african_traditional/south_asian 各 +3 术语
  - 新增 6 条禁忌规则（japanese_traditional×2, islamic_geometric, watercolor, african_traditional, south_asian）
  - 基准任务：tasks-10→12, tasks-20→30（japanese_traditional 5 tasks）
  - **结果**：52 术语 / 20 禁忌 / 30 基准任务，9 传统均有 5-6 术语 + 1-2 禁忌
- [x] **知识库浏览页**：`KnowledgeBasePage.tsx` — 9 传统手风琴展开，含术语/禁忌/L1-L5 权重/管线变体 ✅ 2026-03-06
  - Mock 数据覆盖 9 个传统（中/日/波斯/印度/韩/泰/拜占庭/伊斯兰/藏传）
  - 搜索筛选 + severity/L-level 彩色标签 + 顶部统计卡片
- [x] **知识库 API**：`GET /api/v1/knowledge-base` — 公开只读，聚合 terms+taboos+weights+pipeline 数据 ✅ 2026-03-06
  - 6 个新 Pydantic schema: TermItem/TabooRuleItem/PipelineVariantInfo/TraditionEntry/KnowledgeBaseSummary/KnowledgeBaseResponse
- [ ] **用户贡献接口**：用户可提交新术语/参考（需审核）→ 由 **M7.6 TraditionHub** 承接

### 5.2 社区功能

- [x] **作品展示页**：`GalleryPage.tsx` — 8 个 mock 作品，L1-L5 评分条，传统/分数筛选 ✅ 2026-03-06
  - 渐变色块占位图 + IOSCardGrid 响应式 4 列布局
  - Header 导航已添加 Knowledge Base + Gallery 入口
- [ ] **模板市场**：用户分享自定义管线模板（M3.1 的延伸）→ 由 **M7.6 TraditionHub** 承接
- [ ] **排行榜**：最高文化评分作品 / 最活跃创作者

### 5.3 多语言

- [x] **UI 国际化基础**：react-i18next + i18next, zh/en/ja 三语 80+ 翻译键 ✅ 2026-03-06
  - `src/i18n/index.ts`: 初始化 + localStorage 持久化 + 浏览器语言自动检测
  - `src/i18n/locales/{en,zh,ja}.json`: nav/home/knowledgeBase/gallery/traditions/dimensions/common
  - `main.tsx` 已注入 i18n
- [ ] **页面组件接入 i18n**：将硬编码文案替换为 `useTranslation()` 调用
- [ ] **文化解读多语言**：VLM Critic 输出支持多语言

---

## Milestone 6: 基础设施升级（按需）

> **目标**：从开发环境升级为可对外服务的基础设施
> **触发**：有付费用户或公开 API 流量时
> **M6 代码准备状态**：✅ 部署配置完成 (2026-03-06)

- [x] **Cloud Run 部署包**：`requirements.cloudrun.txt` + `Dockerfile.cloud` 更新 ✅ 2026-03-06
  - 去除 torch/lancedb/sentence-transformers (~2.5GB)，加入 litellm/google-genai/langgraph
  - 新增 `google-cloud-storage` 依赖
- [x] **CI/CD 管线**：`.github/workflows/deploy-backend-cloudrun.yml` ✅ 2026-03-06
  - 自动触发：push to master + wenxin-backend/ 路径变更
  - 手动触发：workflow_dispatch
  - 流程：py_compile 校验 → Docker build → Artifact Registry → Cloud Run deploy → health check
- [x] **API 文档可配置**：`ENABLE_API_DOCS=true` 环境变量控制生产环境 Swagger 可见性 ✅ 2026-03-06
- [x] **深度健康检查**：`/health/deep` 端点报告 VLM/Scout/Router/API Key 可用性 ✅ 2026-03-06
- [x] **存储抽象层**：`app/prototype/tools/storage.py` — Local/GCS 双后端 ✅ 2026-03-06
  - `STORAGE_BACKEND=local|gcs` + `GCS_BUCKET` 环境变量控制
- [ ] **数据库迁移**：Supabase → Cloud SQL（已有连接配置，待实际迁移时执行）
- [ ] **CDN**：生成图片 CDN 加速（待 GCS 上线后配置）
- [ ] **监控**：Langfuse 或 Cloud Trace 接入（Langfuse config 已在 settings 中预留）

---

## Milestone 7: 社区框架 + Canvas 升级（4-6 周）

> **目标**：从封闭工具 → OpenClaw 式社区框架，TRADITION.yaml = SKILL.md
> **哲学**：降低贡献门槛，让文化研究者和开发者都能参与
> **依赖**：M5.1（知识库数据）+ M3（Canvas 基础）
> **并行分组**：A 组（Build+Explore，共享 traditions 数据）| B 组（Compare+Run，共享评估引擎）

### 7.1 传统即配置 — TRADITION.yaml（P0 基础，1 周）✅ 完成 2026-03-06

> **前提**：所有后续模块的基础数据格式

- [x] **YAML Schema 定义**：`traditions/*.yaml` 替代硬编码 Python dict ✅ 2026-03-06
  ```yaml
  name: chinese_xieyi            # 唯一 ID
  display_name: {en: "Freehand Ink", zh: "写意", ja: "写意画"}
  weights: {L1: 0.15, L2: 0.15, L3: 0.25, L4: 0.15, L5: 0.30}
  terminology:
    - term: "yi_bi"
      definition: {en: "意筆 - expressive brushwork conveying inner spirit"}
      l_levels: [L3, L5]
  taboos:
    - rule: "Avoid photorealistic rendering"
      severity: high
      l_levels: [L1, L2]
  pipeline:
    template: interactive_full
    overrides: {max_rounds: 2, accept_threshold: 0.85}
  examples:
    - prompt: "Mountain landscape in xieyi style"
      reference_image: "examples/xieyi_mountain.jpg"
  ```
- [x] **YAML Loader**：`tradition_loader.py` — 启动时加载 `traditions/` 目录下所有 `.yaml` ✅ 2026-03-06
  - 替代 `cultural_weights.py` 中硬编码 dict（保留 fallback）
  - 热重载支持：`reload_traditions()` + lazy loading
- [x] **9 传统迁移**：9+1 个 YAML 文件（含 default）+ `_template.yaml` ✅ 2026-03-06
  - 源数据合并：`cultural_weights.py` 权重 + `terms.v1.json` 术语 + `taboo_rules.v1.json` 禁忌 + `pipeline_router.py` 变体
  - 向后兼容：`get_weights()` / `KNOWN_TRADITIONS` / `CulturalPipelineRouter` 全部保持不变
  - 回归验证：py_compile + import chain + 权重一致性测试全部通过
- [x] **JSON Schema 发布**：`traditions/schema.json` — 供社区贡献者验证 YAML ✅ 2026-03-06

### 7.2 Canvas 升级 — Build + Explore 模式 ✅ 完成 2026-03-06

> **与 M3 的关系**：M3 = Run 模式（管线编辑+执行），M7.2 = Build + Explore（传统构建+知识浏览）

- [x] **Build 模式** `TraditionBuilder.tsx` ✅ 2026-03-06
  - 权重滑块：L1-L5 拖动实时归一化到 1.0
  - 术语编辑器：添加/删除，L-level toggle chips，category 下拉
  - 禁忌编辑器：规则 + severity 下拉 + L-level toggle
  - 管线：default/chinese_xieyi/western_academic 选择
  - YAML 预览 + 下载，实时验证（name/weights/terms/taboos）
- [x] **Explore 模式** `TraditionExplorer.tsx` ✅ 2026-03-06
  - 8 传统卡片（展开含权重/术语/禁忌完整详情）
  - 跨传统术语搜索（英文/中文/定义）+ 实时结果
  - 权重对比：选 2-3 传统，SVG 雷达图叠加
- [x] **PrototypePage 五模式切换**：edit/run/build/explore/compare ✅ 2026-03-06

### 7.3 Canvas 升级 — Compare 模式 ✅ 完成 2026-03-06

- [x] **Compare 模式** `ComparePanel.tsx` ✅ 2026-03-06
  - 拖拽/点击上传 2-6 张图片，并行调用 `/api/v1/evaluate`
  - 每图独立评分卡片（缩略图 + L1-L5 进度条 + 传统识别）
  - SVG 叠加雷达图（多色透明多边形）
  - 差异对比表：逐维度得分 + Max Gap 高亮（>0.1 红色加粗）
  - 加权总分并排对比

### 7.4 多入口体验（2 周）

> **策略**：6 层入口，从 10 秒体验到深度集成
> **优先级**：HF Space > CLI > Discord（按开发者获取效率排序）

| 入口 | 体验时间 | 目标用户 | 状态 |
|------|----------|----------|------|
| HF Space | 10s | 研究者/好奇者 | ✅ |
| Discord Bot | 1min | 创作者社区 | ✅ |
| CLI (`vulca evaluate`) | 5min | 开发者 | ✅ |
| Python SDK | 10min | ML 工程师 | [ ] |
| REST API | 15min | 企业集成 | ✅ M4 |
| Canvas | 30min | 深度用户 | ✅ M3 |

- [x] **HF Space Demo** `integrations/hf_space.py` ✅ 2026-03-06
  - Gradio Blocks UI：Evaluate tab（图片+传统→雷达图+报告）+ Identify tab
  - 调用 M4 API，matplotlib 雷达图，CTA → vulcaart.art
  - 启动：`python -m app.prototype.integrations.hf_space`
- [x] **CLI 工具** `integrations/cli.py` ✅ 2026-03-06
  - 4 子命令：evaluate/identify/traditions/validate
  - `--json` 输出模式（CI/CD 集成），`--tradition` 指定传统
  - YAML validate 子命令直接集成 tradition_loader
  - 启动：`python -m app.prototype.integrations.cli evaluate image.png`
- [x] **Discord Bot** `integrations/discord_bot.py` ✅ 2026-03-06
  - 4 slash commands: vulca-evaluate/vulca-identify/vulca-tradition/vulca-ask
  - 富嵌入卡片：L1-L5 分数条 + 传统识别 + 文化诊断
  - vulca-ask 通过 Gemini 2.5 Flash 回答文化知识问题
  - 启动：`python -m app.prototype.integrations.discord_bot`

### 7.5 插件生态（按需）

> **触发**：CLI + SDK 完成后，按社区需求优先级开发

- [ ] **ComfyUI 自定义节点**：`VULCACriticNode` — 接收图片输入，输出 L1-L5 评分
  - 适配 ComfyUI 节点接口（RETURN_TYPES, INPUT_TYPES）
  - 调用 M4 REST API
- [ ] **n8n 集成**：HTTP Request 节点模板（YAML 配置分享）
- [ ] **Figma 插件**：设计师在 Figma 中直接检查文化合规（远期）

### 7.6 TraditionHub — 社区贡献流程（→ 吸收 M5 未完成项）

> **关联**：替代 M5.1 "用户贡献接口" + M5.2 "模板市场"
> **模式**：GitHub PR 流程 + 自动化验证

- [x] **贡献指南** `CONTRIBUTING.md` ✅ 2026-03-06
  - Quick Start 5分钟流程 + YAML 结构说明 + L1-L5 权重指南
  - Quality Checklist + 好/坏贡献标准 + Code of Conduct
- [x] **CI 验证管线** `.github/workflows/validate-traditions.yml` ✅ 2026-03-06
  - PR 触发（`traditions/*.yaml` 路径变更）
  - YAML 解析 + 必填字段 + 权重归一化 + name/filename 一致性
  - 术语/禁忌格式校验 + 重复传统名检测
- [ ] **Tradition Gallery 页面**：展示所有社区贡献的传统
  - 每传统卡片：名称/贡献者/术语数/禁忌数/评分样例
  - 安装：一键导入到个人 Canvas workspace
  - 排序：按使用量 / 评分 / 最新
- [ ] **管线模板市场**：用户分享自定义管线拓扑（复用 M3.1 localStorage 结构 → 云端）

---

## Milestone 8: 画布产品化 — 默认模板 + 渐进式体验（2-3 周）

> **目标**：让画布真正"好用"——新用户 10s 内完成首次评估，全程在画布范式内
> **核心原则**：简化体验 = 预设模板，不是绕过画布；API 是基础设施，不是产品入口
> **参考**：ComfyUI 默认工作流 / Notion 模板 / LOVART 一句话启动
> **依赖**：M3（Canvas Editor）+ M4（B端 API）+ M7.1（TRADITION.yaml）
> **详见**：`product-principles.md`

### 8.1 快速评估模板（P0）

> **目标**：新用户打开画布，3 个节点已连好，拖入图片即可运行

- [ ] **"Quick Evaluate" 预设模板**：3 节点预连
  ```
  [Upload Image] → [Identify Tradition] → [Evaluate + Report]
  ```
  - Upload 节点：拖拽/点击上传，支持 paste 粘贴
  - Identify 节点：自动检测传统，显示传统名+置信度
  - Evaluate 节点：运行评估，展示结果（见 8.2）
  - 画布打开时默认加载此模板（首次用户），老用户恢复上次状态
  - 后端走 Pipeline → SSE 事件流（不直接调 REST API）
- [ ] **节点执行动画**：运行时节点边框逐个亮起（pending→running→done）
  - 视觉反馈：用户看到数据在节点间流动
- [ ] **一键运行按钮**：画布顶部全局 "Run" 按钮，不需要找到具体节点

### 8.2 报告节点 — 人话展示（P0）

> **目标**：评估结果用非专业用户能看懂的方式展示

- [ ] **一句话总结**：根据 weighted_total 生成自然语言
  - >= 0.85: "文化合规度优秀" (绿色)
  - 0.70-0.85: "基本合规，有改进空间" (黄色)
  - < 0.70: "存在文化风险，建议修改" (红色)
- [ ] **红黄绿直觉标记**：每个 L 维度用颜色标识（而非只有数字）
  - 维度名用中文（视觉感知/技术分析/文化语境/批评诠释/哲学美学），不用 L1-L5 编号
- [ ] **风险高亮**：risk_flags 用警告卡片展示，直接说明问题和建议
- [ ] **"深入分析" 展开**：点击后展开完整雷达图 + 每维度 rationale

### 8.3 渐进式模板库

> **目标**：覆盖 5 个核心用户场景，每个场景一个预设模板

- [ ] **场景 A "这图能用吗"**：Quick Evaluate（8.1 已覆盖）
- [ ] **场景 B "哪里不对"**：Quick Evaluate + Scout 证据节点（4 节点）
- [ ] **场景 C "怎么改"**：Compare 模板 — 两个 Upload 节点 → 各自 Evaluate → Diff Report 节点
- [ ] **场景 D "我想学"**：Explore 模板 — 选传统 → 展示术语/禁忌/权重/示例
- [ ] **场景 E "批量审核"**：Batch Evaluate — CSV Upload → 批量 Evaluate → 汇总报告
- [ ] **模板选择器升级**：首次打开时展示模板卡片（带场景描述），而非空画布或下拉菜单

### 8.4 画布内传统切换

- [ ] **传统参数即节点参数**：Evaluate 节点的传统选择可在画布内直接切换
  - 切换后自动重跑评估，对比不同传统视角
  - "换传统再评" 不需要离开画布进入 Explorer 模式
- [ ] **传统对比视图**：同一张图，3 个传统并排评估结果（画布内 3 个 Evaluate 节点扇出）

---

## 阻塞项跟踪

| 阻塞项 | 阻塞了什么 | 状态 | 负责人 |
|--------|-----------|------|--------|
| ~~Google Cloud Billing 未开通~~ | ~~M0.2 验证 + M1 计时~~ | ✅ 已解决 (2026-03-05) | wangjindong |
| ACM MM 投稿 3/25 abstract | 时间分配 | ✅ 润色完成，待提交 | yhryzy |

---

## 决策日志

| 日期 | 决策 | 理由 | 影响 |
|------|------|------|------|
| 2026-03-04 | 技术栈统一为 Gemini API | 投资人提供足量 API + 单一供应商简化运维 | 砍掉 Together/fal.ai/globalai.vip |
| 2026-03-04 | 砍掉 FLUX + FLUX Fill | NB2 > FLUX (+0.028***), Loop 无效 (+0.002 ns) | draft_provider/flux_fill_provider deprecated |
| 2026-03-04 | 产品方向：文化 AI 助手 | 投资人要求宽泛市场+好操作性 | Phase 4 Playground 优先 |
| 2026-03-04 | 对标 LOVART + TapNow | Agent 驱动 + Node-Wire-Canvas 透明架构 | Playground + 弹性管线设计 |
| 2026-03-04 | 基础设施暂不迁移 | 开发阶段本地够用 | M6 延后到有用户时 |
| 2026-03-05 | M0.1 全量审查修复 | 3 agent 并行审查发现 12 处遗漏 | vlm_critic/prompt_enhancer 运行时 bug 修复 + 10 处清理 |
| 2026-03-06 | M5.1 知识库覆盖 ≥5 术语/传统 | japanese_traditional 空白影响 API 质量 | 52 术语 + 20 禁忌 + 30 基准任务 |
| 2026-03-06 | M6 部署配置先行 | 代码准备与实际部署解耦，降低切换成本 | Dockerfile + CI/CD + 存储抽象，实际迁移按需执行 |
| 2026-03-06 | i18n 用 react-i18next | JSON 嵌套适合 VULCA 层级术语; localStorage 持久化 | zh/en/ja 三语, 页面组件逐步接入 |
| 2026-03-06 | OpenClaw 式社区框架 | OpenClaw 13K+ 社区技能 = TRADITION.yaml PR 流程; 降低贡献门槛 | M7 新增: YAML 重构 + Canvas 四模式 + 多入口 + TraditionHub |
| 2026-03-06 | Canvas 四模式架构 | Build(传统构建) + Run(管线执行,已有) + Explore(知识浏览) + Compare(多图对比) | A 组(Build+Explore)共享数据, B 组(Compare+Run)共享引擎, 可并行 |
| 2026-03-06 | 画布+节点=核心范式 | 简化体验=预设模板，不是绕过画布；API 是基础设施不是产品入口 | M8 全部在画布内实现，不做独立 API 调用页面 |
| 2026-03-06 | 工具先行，生态跟随 | ComfyUI 10K 节点是结果不是原因；文化知识是社区共建公共资产非护城河 | 产品好用优先于生态建设 |
| 2026-03-06 | 多入口优先级: HF > CLI > Discord | HF Space 10s 体验 → 研究者获取效率最高; CLI 面向开发者 CI/CD 集成 | REST API(M4) + Canvas(M3) 已完成,补齐轻量入口 |

---

## 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-03-04 | v3.0 | 初始版本，基于投资人会议 + LOVART/TapNow 调研 |
| 2026-03-05 | v3.1 | M0.1 全部完成 ✅；全量审查修复 12 处（2 critical + 5 medium + 5 low） |
| 2026-03-05 | v3.2 | M0.2 key 验证 ✅（0.964, $0.268）；M2.1 三栏布局 ✅（5新组件+移动端Tab） |
| 2026-03-05 | v3.3 | M1: NB2超时+CLIP线程安全 ✅；M2.3 HITL四阶段 ✅；M2.4 Props接线 ✅；Mock E2E通过 |
| 2026-03-05 | v3.4 | M3 Canvas Editor 全部完成 ✅：React Flow 编辑器 + 5模板切换 + NodeParamPanel + TraditionWeightGrid + BatchInputPanel + localStorage |
| 2026-03-06 | v3.5 | M4 B端 API ✅ (2端点+认证+速率限制+Pricing页) |
| 2026-03-06 | v3.6 | M5.1 知识库扩展 ✅ (52术语/20禁忌/30任务, japanese_traditional从0→6); M6 部署配置 ✅ (Dockerfile.cloud+CI/CD+存储抽象+深度健康检查) |
| 2026-03-06 | v3.7 | M5 内容页面 ✅ (KnowledgeBasePage+GalleryPage+知识库API+Header导航); M5.3 i18n ✅ (react-i18next, zh/en/ja 三语80+键) |
| 2026-03-06 | v3.8 | ACM MM 润色完成 ✅ (29 refs, 160w abstract); M7 社区框架里程碑新增 (TRADITION.yaml + Canvas 四模式 + 多入口 + TraditionHub); M5 未完成项交叉引用到 M7.6 |
| 2026-03-06 | v3.9 | M7.1 TRADITION.yaml ✅: 10 YAML文件(9传统+default) + JSON Schema + tradition_loader.py + _template.yaml; cultural_weights.py YAML-first加载+hardcoded fallback; PyYAML加入render/cloudrun依赖; 全量回归通过 |
| 2026-03-06 | v3.10 | M7.2-7.4+7.6 全部完成 ✅: TraditionBuilder+TraditionExplorer+ComparePanel 3前端组件; PrototypePage 五模式(edit/run/build/explore/compare); HF Space+CLI+Discord Bot 3入口; CONTRIBUTING.md+validate-traditions.yml CI; TypeScript 0 error |
| 2026-03-06 | v3.11 | 产品原则确立 + M8 画布产品化里程碑: 画布+节点=核心范式; TTFV<=10s; 预设模板(Quick Evaluate 3节点); 报告节点人话展示(红黄绿+一句话); 5场景模板库; 竞品分析(6家); `product-principles.md` 新建 |
