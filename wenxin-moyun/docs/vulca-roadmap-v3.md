# VULCA 产品路线图 v3（2026-03-04 起）

> **定位**：面向创作者的文化 AI 助手 — Playground + Canvas + Agent 集群
> **技术栈**：Gemini API 单栈（NB2 + VLM + LLM）
> **对标**：LOVART（Agent 驱动设计）+ TapNow（Node-Wire-Canvas 透明架构）
> **投资人要求**：宽泛市场 + 多场景 + 好操作性 + 可维护可扩展
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
| ACM MM 论文 | ✅ 写完 | 3/25 abstract, 4/1 投稿（半天润色） |

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
> **M5.1 状态**：✅ 知识库审计+扩展完成 (2026-03-06)

### 5.1 知识库扩展

- [x] **9 传统知识库审计**：检查每个传统的术语覆盖度、禁忌条目数、构图参考数 ✅ 2026-03-06
  - 审计发现：japanese_traditional 完全空白（0 术语/0 禁忌/0 基准任务），5 传统仅 3 术语
  - 修复：japanese_traditional 新增 6 术语（ukiyo-e/wabi-sabi/ma/sumi-e/kintsugi/Rimpa）+ 2 禁忌
  - 扩展：chinese_gongbi/islamic_geometric/watercolor/african_traditional/south_asian 各 +3 术语
  - 新增 6 条禁忌规则（japanese_traditional×2, islamic_geometric, watercolor, african_traditional, south_asian）
  - 基准任务：tasks-10→12, tasks-20→30（japanese_traditional 5 tasks）
  - **结果**：52 术语 / 20 禁忌 / 30 基准任务，9 传统均有 5-6 术语 + 1-2 禁忌
- [ ] **知识库可视化**：用户可浏览 Scout 知识库内容（术语字典、构图参考、禁忌列表）
- [ ] **用户贡献接口**：用户可提交新术语/参考（需审核）

### 5.2 社区功能

- [ ] **作品展示页**：用户生成的作品 + L1-L5 评分 + 使用的模板/传统
- [ ] **模板市场**：用户分享自定义管线模板（M3.1 的延伸）
- [ ] **排行榜**：最高文化评分作品 / 最活跃创作者

### 5.3 多语言

- [ ] **UI 国际化**：中/英/日（匹配核心文化传统覆盖）
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

## 阻塞项跟踪

| 阻塞项 | 阻塞了什么 | 状态 | 负责人 |
|--------|-----------|------|--------|
| ~~Google Cloud Billing 未开通~~ | ~~M0.2 验证 + M1 计时~~ | ✅ 已解决 (2026-03-05) | wangjindong |
| ACM MM 投稿 3/25 abstract | 时间分配 | ⏰ 半天润色 | yhryzy |

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
