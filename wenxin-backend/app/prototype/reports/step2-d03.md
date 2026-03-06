# Step 2 D03: 20 样本真实回归

**日期**: 2026-02-09
**状态**: PASS — 全部 DoD 达标

## 执行命令

```bash
cd <project-root>/wenxin-backend

# together_flux 20 样本
TOGETHER_API_KEY=*** python3 app/prototype/tools/run_benchmark.py \
  --tasks app/prototype/data/benchmarks/tasks-20.json \
  --provider together_flux \
  --output app/prototype/reports/step2-d03-bench20-together.json

# mock 基线对照
python3 app/prototype/tools/run_benchmark.py \
  --tasks app/prototype/data/benchmarks/tasks-20.json \
  --provider mock --width 512 --height 512 --steps 4 --n-candidates 2 \
  --output app/prototype/reports/step2-d03-bench20-mock.json

# 质量门
python3 app/prototype/tools/validate_regression.py
python3 app/prototype/tools/validate_fallback.py
cd <project-root> && bash .claude/hooks/post-plan-validate.sh
```

## 关键指标

### Together Flux (20 tasks)

| 指标 | 值 | 门槛 | 状态 |
|------|-----|------|------|
| Tasks 完成 | 20/20 | 20/20 | **PASS** |
| Pass Rate | 90.0% (18/20) | >= 80% | **PASS** |
| Avg Latency | 5967ms | — | — |
| P95 Latency | 16207ms | < 30s | **PASS** |
| Avg Cost | $0.0132/task | <= $0.08 | **PASS** |
| Total Cost | $0.264 | — | — |
| Total API Calls | 88 | — | — |
| Taboo 漏判 | 0 | = 0 | **PASS** |
| Decision Drift | 0/20 (0.0%) | — | **PASS** |

### Mock 基线 (20 tasks)

| 指标 | 值 |
|------|-----|
| Pass Rate | 90.0% (18/20) |
| Avg Latency | 131ms |
| P95 Latency | 242ms |
| Avg Cost | $0.00 |
| Decisions | accept=18, stop=2 |

### Taboo 检测 (2/2 拒绝)

| Task | Provider | Decision | Rounds | 状态 |
|------|----------|----------|--------|------|
| bench-010 | together | **stop** | 2 | 正确拒绝 |
| bench-020 | together | **stop** | 2 | 正确拒绝 |
| bench-010 | mock | **stop** | 2 | 正确拒绝 |
| bench-020 | mock | **stop** | 2 | 正确拒绝 |

> 两个 taboo task 在两个 provider 下均被正确拒绝，漏判 = 0。

## Per-Task 明细 (together_flux)

| Task ID | Tradition | Decision | Rounds | Latency |
|---------|-----------|----------|--------|---------|
| bench-001 | chinese_xieyi | accept | 1 | 4588ms |
| bench-002 | chinese_gongbi | accept | 1 | 5011ms |
| bench-003 | western_academic | accept | 1 | 6370ms |
| bench-004 | western_academic | accept | 1 | 6573ms |
| bench-005 | islamic_geometric | accept | 1 | 7178ms |
| bench-006 | african_traditional | accept | 1 | 4567ms |
| bench-007 | south_asian | accept | 1 | 4308ms |
| bench-008 | watercolor | accept | 1 | 4706ms |
| bench-009 | default | accept | 1 | 4417ms |
| bench-010 | western_academic | **stop** | 2 | 16207ms |
| bench-011 | chinese_xieyi | accept | 1 | 4231ms |
| bench-012 | western_academic | accept | 1 | 3638ms |
| bench-013 | islamic_geometric | accept | 1 | 5667ms |
| bench-014 | african_traditional | accept | 1 | 4770ms |
| bench-015 | south_asian | accept | 1 | 5274ms |
| bench-016 | watercolor | accept | 1 | 3907ms |
| bench-017 | chinese_xieyi | accept | 1 | 4772ms |
| bench-018 | chinese_gongbi | accept | 1 | 5149ms |
| bench-019 | default | accept | 1 | 5567ms |
| bench-020 | islamic_geometric | **stop** | 2 | 12434ms |

## Decision Drift 分析

```
decision_drift: 0/20 (0.0%)
drift_tasks: []
```

真实 provider 与 mock 基线判断完全一致 — pipeline 判断逻辑不受 provider 影响。

## 质量门

| 验证脚本 | 结果 |
|----------|------|
| validate_regression.py | 13/13 PASS |
| validate_fallback.py | 19/19 PASS |
| post-plan-validate.sh | exit 0 (PASS) |

## DoD 检查

| # | 条件 | 结果 | 状态 |
|---|------|------|------|
| 1 | 20/20 跑完 | 20/20 完成 | **PASS** |
| 2 | pass_rate >= 80% | 90.0% | **PASS** |
| 3 | avg_cost <= $0.08 | $0.0132 | **PASS** |
| 4 | P95 < 30s | 16207ms | **PASS** |
| 5 | taboo 漏判 = 0 | bench-010 + bench-020 均 stop | **PASS** |
| 6 | regression + fallback + hook 全通过 | 13/13 + 19/19 + exit 0 | **PASS** |

## 成本跟踪

| 日期 | 消耗 | 累计 |
|------|------|------|
| D2 | $0.135 | $0.135 |
| D3 | $0.264 | $0.399 |
| **剩余** | | **~$4.60 / $5.00** |

## 失败样例与修复动作

无失败样例。bench-010 和 bench-020 的 `stop` 是预期行为（taboo 检测正确触发）。

## 观察

1. **延迟分布**: 单轮 accept 任务 3.6-7.2s，双轮 stop 任务 12-16s（2x 预期）
2. **bench-010 延迟飙升**: D2=4003ms → D3=16207ms，可能是 API 侧波动
3. **成本稳定**: 与 D2 ($0.0132/task) 完全一致

## D4 预告

- Fallback 压测 (tools/validate_fallback_real.py)
- 4 个场景: timeout→fallback, 429→fallback, 正常不触发, 全失败→error
