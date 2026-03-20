---
name: vulca-evolve
description: VULCA 进化系统交互 — 查看/比较/运行权重进化和消化系统状态
user-invocable: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# /vulca-evolve — 进化系统交互

查看和管理 VULCA 自进化系统状态。

## 用法

```
/vulca-evolve status    # 查看进化系统当前状态
/vulca-evolve weights   # 查看各传统的当前权重（YAML vs evolved）
/vulca-evolve run       # 触发一次进化运算
/vulca-evolve compare   # 对比 YAML 基线和进化后权重
/vulca-evolve reset     # 重置进化权重为 YAML 基线（需确认）
```

## 关键文件

| 文件 | 用途 |
|------|------|
| `wenxin-backend/app/prototype/data/evolved_context.json` | 进化权重存储（自动维护，禁止手动编辑） |
| `vulca/src/vulca/cultural/*.yaml` | YAML 基线权重 + 术语 + 禁忌 |
| `wenxin-backend/app/prototype/digestion/context_evolver.py` | ContextEvolver 进化引擎 |
| `wenxin-backend/app/prototype/digestion/few_shot_updater.py` | FewShotUpdater 校准样本 |
| `wenxin-backend/app/prototype/digestion/preference_learner.py` | PreferenceLearner 偏好学习 |
| `vulca/src/vulca/_vlm.py` | VLM 评分 + 进化上下文注入 |

## 执行步骤

### status — 进化系统状态
1. 读取 `evolved_context.json`，显示最后更新时间
2. 统计: 多少传统有进化权重
3. 检查消化系统组件状态:
   - ContextEvolver: 最后运行时间
   - FewShotUpdater: 校准样本数量
   - PreferenceLearner: feedback 条目数
4. 检查 VLM prompt 是否注入进化上下文

### weights — 查看权重
```bash
cd /home/yhryzy/projects/website/vulca
.venv/bin/python -c "
from vulca.cultural import get_weights, load_tradition
for t in ['chinese_xieyi', 'japanese_ukiyoe', 'islamic_geometric']:
    yaml_w = load_tradition(t).get('weights', {})
    evolved_w = get_weights(t)
    print(f'{t}: YAML={yaml_w} | Evolved={evolved_w}')
"
```

### run — 触发进化
```bash
cd /home/yhryzy/projects/website/wenxin-backend
venv/bin/python -c "
import asyncio
from app.prototype.digestion.context_evolver import ContextEvolver
evolver = ContextEvolver()
result = asyncio.run(evolver.evolve())
print(f'Evolution result: {result}')
"
```

### compare — 权重对比
读取 YAML 基线和 evolved_context.json，以表格展示差异:
```
| Tradition     | Dim | YAML  | Evolved | Delta  |
|---------------|-----|-------|---------|--------|
| chinese_xieyi | L1  | 0.10  | 0.347   | +0.247 |
| chinese_xieyi | L5  | 0.15  | 0.220   | +0.070 |
```

### reset — 重置（需用户确认）
1. **提醒用户**: 这将删除所有进化数据
2. 等待确认
3. 备份当前 `evolved_context.json`
4. 删除进化数据
5. 验证 `get_weights()` 回退到 YAML 基线
