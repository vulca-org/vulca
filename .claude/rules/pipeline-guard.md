---
paths:
  - "vulca/**/*.py"
  - "wenxin-backend/app/prototype/**/*.py"
---

# Pipeline Guard Rules

编辑 pipeline 或 prototype 代码时必须遵守以下规则。

## ONE PIPELINE 原则

所有入口（Canvas UI / CLI / SDK / MCP）必须走 `vulca.pipeline.execute()`。
**禁止创建新的执行路径**。

```python
# 唯一正确的调用方式
from vulca.pipeline import execute
result = await execute(topology, context)
```

## 禁止导入清单

以下模块已删除，**任何文件不得导入**:
```python
# 全部已删除，导入会直接报错
from app.vulca import ...              # 已删除 (Phase 5)
from app.prototype.graph import ...    # 已删除 (Phase 6)
from app.prototype.orchestrator.orchestrator import ...  # 已删除
import novita_client                   # 废弃 API
```

## L1-L5 评分系统

VULCA 使用 5 维度评分（不是 6D，不是 47D）:
- **L1**: Cultural Authenticity（文化真实性）
- **L2**: Technical Mastery（技术精通）
- **L3**: Creative Synthesis（创意综合）
- **L4**: Emotional Resonance（情感共鸣）
- **L5**: Contemporary Relevance（当代关联）

权重通过 `get_weights(tradition)` 获取，优先读 `evolved_context.json`，fallback 到 YAML。

### 权重流转

```
Canvas 滑块 → CreateRunRequest.node_params.critic → EvaluateNode → _vlm.py
CLI --weights "L1=0.3,L2=0.2" → create() → execute() → EvaluateNode
evolved_context.json → get_weights() → _build_tradition_guidance() → VLM prompt
```

## 关键约束

### bcrypt 版本
```
bcrypt==4.0.1  # 必须 4.0.x，4.1+ 破坏 passlib 兼容性
```
修改 `requirements.txt` 或 `constraints.txt` 时验证此约束。

### evolved_context.json
**禁止手动编辑**。此文件由 ContextEvolver 自动维护:
- 位置: `wenxin-backend/app/prototype/data/evolved_context.json`
- 更新频率: 每 5 分钟（有新 session 数据时）
- 包含: 进化权重、tradition insights、few-shot benchmarks

### YAML Tradition 配置
- 位置: `vulca/src/vulca/cultural/*.yaml`
- 包含: terminology + taboos（被 `_vlm.py` 注入评分 prompt）
- 修改 YAML 后需运行 `vulca traditions` 验证加载

## Pipeline 节点

3 个内置节点:
1. **ScoutNode** — 文化侦察 + 参考检索
2. **GenerateNode** — 图像生成（支持 Gemini 多模态 + 参考图）
3. **EvaluateNode** — L1-L5 VLM 评分

Canvas NodeSearchPopup 只显示 8 个有后端的节点。**不要添加没有后端实现的节点**。
