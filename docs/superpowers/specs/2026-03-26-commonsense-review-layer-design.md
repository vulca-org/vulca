# Commonsense Review Layer — Design Spec

**Date**: 2026-03-26
**Phase**: Post-D1 (v0.8.0 target)
**Status**: Approved — ready for implementation planning

## Summary

Pipeline 内置的多轮 VLM 常识审查层。自动检测 AI 生图中的非意图性缺陷（结构、空间、语义），保持黑盒 no-code 体验。**Brief 是最终仲裁者**——常识审查不能越过用户的创意意图。

## Design Decisions

| 决策 | 选择 | 理由 |
|------|------|------|
| 检测范围 | 结构 + 空间 + 语义（全覆盖） | 用户需要全面的常识保障 |
| 修复策略 | 仅检测+报告，修复复用现有循环 | 与现有 generate→decide 循环对齐，最小复杂度 |
| VLM 调用 | 独立调用，与 L1-L5 评分并行 | 不同认知任务需要聚焦 prompt，并行不加延迟 |
| 循环退出 | 共享 max_rounds | 多轮自动循环有 +2.6% 确认偏差，不额外加轮 |
| 决策影响 | critical defect 硬否决 + minor 信息传递 | 六根手指不应因"气韵 0.95"被 accept |
| 检测分类 | 无硬编码类别，VLM agent 开放式发现 | 常识问题无穷，枚举不可行 |
| 创意保护 | Brief 上下文注入 + intentionality 判定 | 超现实悬浮是创意，写实悬浮是缺陷 |

## Architecture

### Pipeline 拓扑变更

```
Before:  generate → evaluate → decide → [loop]
After:   generate → [evaluate ∥ commonsense_review] → decide → [loop]
                          并行执行
```

拓扑分层：
```
Layer 0: [generate]
Layer 1: [evaluate, commonsense_review]  ← asyncio.gather 并行
Layer 2: [decide]
```

### 核心关系：常识 × 文化 × 创意

| 层 | 职责 | 仲裁者 |
|----|------|--------|
| 常识 | 检测视觉缺陷 | VLM agent（开放式） |
| 文化 | L1-L5 文化评分 | Brief + 传统 YAML |
| 创意 | 判定"故意 vs 缺陷" | Brief（用户意图声明） |

Brief 是最终仲裁者——同一个视觉元素在不同创意语境下可以是缺陷、创意选择或传统特征。

## Data Model

### Violation（无硬编码类别）

```python
class Severity(str, Enum):
    CRITICAL = "critical"   # 必须修复：6根手指、断裂肢体、物理不可能
    MAJOR = "major"         # 应该修复：明显透视错误、物件结构异常
    MINOR = "minor"         # 可选修复：轻微比例偏差、微小阴影不一致

@dataclass
class Violation:
    description: str          # VLM 自由描述："左手有6根手指"
    location: str             # "画面左下角人物的左手"
    severity: Severity        # VLM 自行判定
    intentionality: str       # "defect" | "likely_intentional" | "uncertain"
    intent_reasoning: str     # "Brief 要求超现实风格，悬浮可能是创意选择"
    suggestion: str           # 仅 defect 时有修复建议
    confidence: float         # 0.0-1.0，低于 0.7 过滤

@dataclass
class CommonsenseReport:
    violations: list[Violation]
    has_critical: bool        # 仅统计 intentionality=="defect" 的 critical
    summary: str              # VLM 生成的整体评估
    review_model: str         # 使用的 VLM 模型
    review_cost_usd: float    # 本次审查 API 成本
```

## Components

### 1. CommonsenseReviewNode (`commonsense/node.py`)

Pipeline 第四个内置节点。从 `ctx.data` 读取 `image_b64`，调用独立 VLM，输出 `CommonsenseReport`。

```python
class CommonsenseReviewNode(PipelineNode):
    name = "commonsense_review"

    async def run(self, ctx: NodeContext) -> dict[str, Any]:
        image_b64 = ctx.get("image_b64")
        mime = ctx.get("image_mime", "image/png")
        creative_context = self._build_creative_context(ctx)

        report = await review_commonsense(
            img_b64=image_b64, mime=mime,
            creative_context=creative_context, api_key=ctx.api_key,
        )

        return {
            "commonsense_report": report,
            "commonsense_violations": report.violations,
            "has_critical_violation": report.has_critical,
        }
```

**Creative context 构建**——两种入口：
- **Studio 模式**（有 Brief）：注入 intent, style_mix, must_have, concept_notes
- **SDK/CLI 模式**（无 Brief）：注入 subject, intent, tradition
- **进化上下文**：注入 `evolved_commonsense.json` 中该传统/风格的已知例外

### 2. VLM Prompt 策略 (`commonsense/prompt.py`)

开放式 agent prompt，不给 checklist：

```markdown
You are a visual commonsense reviewer. Find UNINTENTIONAL defects
in AI-generated images — things that violate physical reality,
biological structure, spatial logic, or semantic consistency.

## Creative Context
{creative_context}

## Critical Rule
The artist's creative intent is ABOVE commonsense.
If the Brief explicitly pursues surrealism, abstraction, or stylistic
exaggeration, do NOT flag those as violations.
Only flag things that are clearly UNINTENDED errors.

## Task
1. Observe the image carefully and holistically
2. Identify unintentional errors
3. For each: description, location, severity, intentionality, suggestion
4. If no issues, say so explicitly
```

### 3. VLM 调用核心 (`commonsense/review.py`)

```python
async def review_commonsense(
    img_b64: str, mime: str, creative_context: str, api_key: str,
) -> CommonsenseReport:
```

- 模型：`VULCA_REVIEW_MODEL` 环境变量，默认 `gemini/gemini-2.5-flash`
- temperature: 0.1（低随机性，高一致性）
- max_tokens: 2048
- 响应解析：复用 `parse_llm_json()`，鲁棒处理
- 置信度过滤：`confidence < threshold` 的 violation 丢弃（默认 0.7，可通过 `VULCA_COMMONSENSE_CONFIDENCE` 环境变量配置）

### 4. Pipeline Engine 并行改造 (`pipeline/engine.py`)

拓扑排序后检测同层节点（in-degree 同时降为 0），用 `asyncio.gather` 并行执行：

```python
for layer in topo_layers:
    if len(layer) == 1:
        output = await layer[0].run(ctx)
        ctx.data.update(output)
    else:
        results = await asyncio.gather(
            *(node.run(ctx) for node in layer)
        )
        for output in results:
            ctx.data.update(output)
```

约束：
- 并行节点读同一个 `ctx.data`（只读 generate 输出），写不同 key，无冲突
- 成本追踪：并行 VLM 调用的 cost 各自累加（需线程安全）
- 事件流：两个 `STAGE_STARTED`/`STAGE_COMPLETED` 会交错发出

### 5. DecideNode 扩展 (`pipeline/nodes/decide.py`)

前置常识硬否决，minor 作为补充信息：

```python
async def run(self, ctx):
    report = ctx.get("commonsense_report")

    # 硬否决：critical defect → 强制 rerun
    if report and report.has_critical:
        defects = [v for v in report.violations
                   if v.severity == Severity.CRITICAL
                   and v.intentionality == "defect"]
        return {
            "decision": "rerun",
            "reason": "critical_commonsense_violation",
            "improvement_focus": "; ".join(v.description for v in defects),
        }

    # 原有 L1-L5 分数逻辑不变
    ...

    # minor/major defect 追加到 improvement_focus
    if report and report.violations:
        non_critical = [v for v in report.violations
                        if v.intentionality == "defect"
                        and v.severity != Severity.CRITICAL]
        if non_critical:
            extra = "; ".join(v.description for v in non_critical)
            improvement_focus += f"; Commonsense: {extra}"
```

行为总结：
- `has_critical` (defect only) → 强制 rerun
- major/minor defect → 追加到 `improvement_focus`
- `likely_intentional` / `uncertain` → 不影响决策，仅记录
- 最后一轮 (`round_num == max_rounds`) 即使 critical 也 stop——不突破硬上限

### 6. 消化系统联动 (`digestion/signals.py`)

扩展现有信号提取：

```python
def extract_commonsense_signal(session) -> list[CommonsenseSignal]:
    """从完整 session 提取常识审查信号"""
    for round in session.rounds:
        for violation in round.commonsense_report.violations:
            yield CommonsenseSignal(
                tradition=session.tradition,
                style=session.style_mix,
                violation_desc=violation.description,
                intentionality=violation.intentionality,
                severity=violation.severity,
                user_accepted=(round == final_round and outcome == "accept"),
                confidence=violation.confidence,
            )
```

三种进化场景：

| 用户行为 | violation 状态 | 进化动作 |
|---------|---------------|---------|
| accept | `uncertain` | 加入 `style_exceptions` |
| accept | `defect` + minor | 降低此类 violation 权重 |
| reject | 无 violation | 记录 `missed_detection` 供分析 |

进化输出 `evolved_commonsense.json`：

```json
{
  "tradition_exceptions": {
    "chinese_xieyi": ["exaggerated proportions", "incomplete distant objects"]
  },
  "style_exceptions": {
    "surrealism": ["floating objects", "melting forms"]
  },
  "confidence_adjustments": {
    "minor_shadow_inconsistency": 0.5,
    "extra_fingers": 1.0
  }
}
```

闭环：`evolved_commonsense.json` → 注入 VLM prompt → 更准确的审查。

## Entry Points & Toggle

| 入口 | 开启（默认） | 关闭 |
|------|------------|------|
| SDK | `vulca.create(...)` | `vulca.create(..., commonsense=False)` |
| CLI | `vulca create "..."` | `vulca create "..." --no-commonsense` |
| MCP | `create_artwork(...)` | `create_artwork(..., commonsense=False)` |
| Studio | Brief `commonsense: true` | NL 指令 "关闭常识审查" |
| Pipeline | `PipelineInput(commonsense=True)` | `PipelineInput(commonsense=False)` |

Pipeline 层实现：`commonsense=False` 时，engine 跳过 `commonsense_review` 节点。

独立 MCP 工具（不走 Pipeline）：
```python
@mcp.tool()
async def review_commonsense(image_path, intent="", tradition="") -> CommonsenseReport
```

## File Organization

```
vulca/src/vulca/
├── commonsense/              # 新模块
│   ├── __init__.py           # 公共 API: review_commonsense()
│   ├── types.py              # Violation, CommonsenseReport, Severity
│   ├── node.py               # CommonsenseReviewNode (PipelineNode)
│   ├── review.py             # review_commonsense() VLM 调用核心
│   └── prompt.py             # prompt 构建 + creative_context
├── pipeline/
│   ├── engine.py             # 改造：拓扑分层 + 并行执行
│   ├── types.py              # PipelineInput += commonsense: bool
│   └── nodes/
│       └── decide.py         # 扩展：常识硬否决
├── digestion/
│   └── signals.py            # 扩展：extract_commonsense_signal()
├── cli.py                    # += --no-commonsense flag
└── mcp_server.py             # += review_commonsense tool
```

## Pipeline Definition

```python
DEFAULT = PipelineDefinition(
    name="default",
    entry_point="generate",
    nodes=("generate", "evaluate", "commonsense_review", "decide"),
    edges=(
        ("generate", "evaluate"),
        ("generate", "commonsense_review"),
        ("evaluate", "decide"),
        ("commonsense_review", "decide"),
    ),
)
```

## Cost Impact

每轮新增一次 VLM 调用（与 evaluate 并行，不加延迟）：
- Gemini 2.5 Flash: ~$0.01-0.03/轮（图片 + 2K output tokens）
- 3 轮 max_rounds 最坏情况: +$0.09
- 可通过 `commonsense=False` 完全关闭

## Testing Strategy

1. **Unit tests**: Violation 数据模型、severity 过滤、confidence 阈值
2. **VLM mock tests**: mock VLM 响应，测试 prompt 构建 + 响应解析 + 边界情况
3. **Node tests**: CommonsenseReviewNode 在 Pipeline 中的集成
4. **Engine tests**: 并行层执行正确性、事件流顺序
5. **DecideNode tests**: critical 硬否决、minor 信息传递、intentionality 过滤
6. **Digestion tests**: 信号提取、进化数据写入/读取
7. **E2E tests**: 完整 Pipeline 带常识审查的端到端流程
