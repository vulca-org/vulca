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
> **M0.2 阻塞**：🚫 等投资人 Google Cloud Billing 开通（key 已收到，配额为 0）

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

- [ ] **Gemini 文本测试**：Gemini 2.5 Flash 文本推理（替代 DeepSeek V3.2）
- [ ] **Gemini VLM 测试**：Gemini 2.5 Flash Vision L1-L5 评分（替代 globalai.vip 代理）
- [ ] **NB2 测试**：gemini-3.1-flash-image-preview 图像生成（已有代码，换 key 即可）
- [ ] **端到端真实模式**：NB2 + Gemini VLM 全链路，确认得分与消融实验一致
- [ ] **成本验证**：单任务成本对比（预期 ~$0.04/任务，与 globalai.vip 时期持平）

---

## Milestone 1: 速度优化（1 周）

> **目标**：250s → 60s，Playground 体验的前提
> **依赖**：M0.2 完成（需要真实 API 测速）

- [ ] **启用 ParallelDimensionScorer**：`interactive_full` 模板已配置 `parallel_critic=True`，验证真实模式下并行 L1-L5 评分
  - 文件：`app/prototype/agents/parallel_scorer.py`, `graph/nodes/critic_node.py`
  - 预期：Critic 阶段从 ~150s → ~40s（5 并行 vs 5 串行）
- [ ] **Scout 缓存**：相同 tradition 的 FAISS 检索结果缓存（避免重复检索）
  - 文件：`app/prototype/agents/scout_service.py`
- [ ] **NB2 超时调优**：当前 120s timeout，根据实测调整
  - 文件：`app/prototype/agents/nb2_provider.py`
- [ ] **CLIP 加载优化**：Mock 测试时 CLIP 加载 ~53s/轮，改为全局单例懒加载
  - 文件：`app/prototype/agents/image_scorer.py`（如存在）
- [ ] **端到端计时**：目标 < 60s/任务（NB2 生成 ~15s + VLM Critic ~30s + 其他 ~15s）

---

## Milestone 2: Playground 核心（2-3 周）⭐ 当前重点

> **目标**：从"表单→等待→结果"升级为交互式 Playground
> **参考**：LOVART 的 ChatCanvas + TapNow 的 Node-Wire-Canvas
> **依赖**：M1 完成（速度可接受后才有交互体验）

### 2.1 布局重组

- [ ] **Playground 页面骨架**：`/prototype` 从单列表单重组为三栏布局
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

- [ ] **模板选择联动**：选不同模板 → 动态显示/隐藏参数项
  - `default`: 全参数（tradition/subject/max_rounds/enable_hitl）
  - `fast_draft`: 精简参数（tradition/subject only，无 loop 参数）
  - `critique_only`: 上传图片 + 选 tradition（评审模式，不生成）
  - `interactive_full`: 全参数 + HITL 开关高亮
  - `batch_eval`: 批量输入（多 subject，CSV 或多行文本）
- [ ] **快速预设场景**：一键填充常见参数组合
  - "中国水墨风山水画" → tradition=chinese_xieyi, subject=mountain landscape
  - "浮世绘风格海浪" → tradition=japanese_ukiyoe, subject=ocean waves
  - "波斯细密画花园" → tradition=persian_miniature, subject=garden with birds
  - "非洲面具设计" → tradition=african_tribal, subject=ceremonial mask
  - 预设存储在前端 JSON 中，用户可扩展

### 2.3 Agent 实时面板

- [ ] **事件流美化**：当前 SSE 事件以文本展示，升级为卡片式 Agent 活动日志
  - 每个 Agent（Scout/Draft/Critic/Queen）一个颜色标识
  - 展开/折叠详情（Scout 证据、Critic 评分、Queen 决策理由）
- [ ] **进度可视化**：管线拓扑图实时高亮当前执行节点
  - 复用 `TopologyViewer.tsx`，添加"当前节点"高亮状态
- [ ] **HITL 交互**：暂停时显示操作面板
  - Scout 暂停：展示检索到的证据，用户可编辑/添加
  - Draft 暂停：展示候选图，用户可选择/否决
  - Critic 暂停：展示评分，用户可覆写分数
  - Queen 暂停：展示决策建议，用户确认/修改

### 2.4 结果 Canvas

- [ ] **多变体展示**：候选图网格 + "Best" 标签 + 轮次标注（已有，需美化）
- [ ] **文化解读卡片**：VLM Critic 的文化分析以可读形式展示（不是原始 JSON）
  - L1-L5 各维度的自然语言解读
  - 文化禁忌检测结果（如有）
  - Scout 证据引用（术语来源、构图参考）
- [ ] **"调整重跑"**：基于当前结果微调参数再跑（不从零开始）
  - 保留上一轮的 Scout 证据缓存
  - 用户可修改 subject/tradition/权重后重跑 Draft+Critic

---

## Milestone 3: 弹性管线 Canvas（2-3 周）

> **目标**：用户可视化编辑管线拓扑，自定义 Agent 组合
> **参考**：TapNow 的 Node-Wire-Group 架构
> **依赖**：M2 完成

### 3.1 节点拖拽编辑器

- [ ] **可视化管线编辑器**：基于 React Flow 或类似库
  - 节点 = Agent（Scout/Router/Draft/Critic/Queen/Archivist）
  - 边 = 数据流（含条件边：Queen→rerun 循环）
  - 从预设模板加载初始拓扑，用户可拖拽修改
- [ ] **实时拓扑校验**：用户修改拓扑时，调用 `POST /topologies/validate` 实时反馈
  - 合法：绿色边框 + "Ready" 标识
  - 非法：红色高亮问题边 + 错误描述
- [ ] **保存/加载自定义模板**：用户创建的管线可保存为自定义模板
  - 前端 localStorage 存储（MVP）
  - 后续可升级为服务端存储 + 社区分享

### 3.2 参数暴露

- [ ] **节点级参数编辑**：点击节点 → 展开参数面板
  - Scout: 检索深度、术语源选择、FAISS/Jaccard 模式
  - Draft: 候选数、图像尺寸、NB2 thinking level
  - Critic: L1-L5 权重手动覆写、评分模式（Rules/VLM/混合）
  - Queen: accept 阈值、max_rounds、rerun 策略
- [ ] **传统权重可视化**：9 传统 × 5 维度的权重矩阵可视化编辑
  - 热力图或滑块组
  - 修改后实时预览权重分配

### 3.3 批量模式

- [ ] **batch_eval 模板 UI**：多任务输入（CSV/多行文本）→ 批量执行 → 汇总报告
  - 进度条：N/M 完成
  - 结果表格：每任务 L1-L5 评分 + 总分
  - 导出：CSV / PDF 报告

---

## Milestone 4: B 端 API + 文化合规服务（1-2 周）

> **目标**：critique_only 模板包装为公开 API
> **依赖**：M1 完成（速度优化后 API 响应时间可接受）

- [ ] **文化诊断 API**：`POST /api/v1/evaluate`
  - 输入：图片 URL/base64 + tradition（可选，不传则自动识别）
  - 输出：L1-L5 评分 + 自然语言诊断 + 改进建议 + 文化禁忌警告
  - 底层：critique_only 模板 + VLM Critic
- [ ] **传统识别 API**：`POST /api/v1/identify-tradition`
  - 输入：图片
  - 输出：最可能的文化传统 + 置信度 + 推荐权重配置
  - 底层：Router Agent
- [ ] **API 文档**：OpenAPI/Swagger 自动生成（FastAPI 已支持）
- [ ] **API Key 管理**：简单的 key 生成 + 速率限制（MVP 用环境变量，后续升级）
- [ ] **定价页更新**：网站 Pricing 页面添加 API 定价层

---

## Milestone 5: 内容完善 + 生态（持续）

> **目标**：所有文化相关内容集合在平台内

### 5.1 知识库扩展

- [ ] **9 传统知识库审计**：检查每个传统的术语覆盖度、禁忌条目数、构图参考数
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

- [ ] **后端迁移**：Render 免费层 → GCP Cloud Run（已有 Dockerfile.cloud + CI/CD）
- [ ] **数据库迁移**：Supabase → Cloud SQL（已有连接配置）
- [ ] **存储**：生成图片 → Cloud Storage（当前本地文件系统）
- [ ] **监控**：Langfuse 或 Cloud Trace 接入
- [ ] **CDN**：生成图片 CDN 加速

---

## 阻塞项跟踪

| 阻塞项 | 阻塞了什么 | 状态 | 负责人 |
|--------|-----------|------|--------|
| Google Cloud Billing 未开通 | M0.2 验证 + M1 计时 | 🚫 等投资人（M0.1 代码准备已完成） | wangjindong |
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

---

## 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-03-04 | v3.0 | 初始版本，基于投资人会议 + LOVART/TapNow 调研 |
| 2026-03-05 | v3.1 | M0.1 全部完成 ✅；全量审查修复 12 处（2 critical + 5 medium + 5 low） |
