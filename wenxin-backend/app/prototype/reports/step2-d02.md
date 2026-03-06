# Step 2 D02: 真实 API 冒烟测试

**日期**: 2026-02-09
**状态**: PASS — 全部 DoD 达标

## 执行命令

```bash
cd <project-root>/wenxin-backend

# 1. 真实 Provider 验证
TOGETHER_API_KEY=*** python3 app/prototype/tools/validate_provider_real.py

# 2. Canary 冒烟测试 (10 tasks, together_flux, 512x512, steps=4, n_candidates=2)
TOGETHER_API_KEY=*** python3 app/prototype/tools/run_benchmark.py \
  --tasks app/prototype/data/benchmarks/tasks-10.json \
  --provider together_flux \
  --width 512 --height 512 --steps 4 --n-candidates 2 \
  --output app/prototype/reports/step2-d02-canary.json

# 3. 质量门回归
python3 app/prototype/tools/validate_regression.py
cd <project-root> && bash .claude/hooks/post-plan-validate.sh
```

## 关键指标

### Provider 验证

| 项目 | 结果 |
|------|------|
| 检查项 | 35/35 PASS |
| 真实调用 | 成功 (非 SKIP) |
| 延迟 | 1338ms |
| 文件大小 | 5702 bytes |
| 图像格式 | JPEG (valid header) |

### Canary Benchmark (together_flux)

| 指标 | 值 | 门槛 | 状态 |
|------|-----|------|------|
| Tasks | 10/10 完成 | 无异常 | PASS |
| Pass Rate | 90.0% (9/10) | >= 75% | PASS |
| Avg Latency | 3129ms | — | — |
| P95 Latency | 4654ms | < 30s | PASS |
| Avg Cost | $0.0132/task | <= $0.08 | PASS |
| Total Cost | $0.132 | — | — |
| Total API Calls | 44 (11 rounds × 2 candidates × 2) | — | — |
| Taboo 漏判 | 0 (bench-010 正确 stop) | = 0 | PASS |

### Per-Task 明细

| Task ID | Tradition | Decision | Rounds | Latency |
|---------|-----------|----------|--------|---------|
| bench-001 | chinese_xieyi | accept | 1 | 4654ms |
| bench-002 | chinese_gongbi | accept | 1 | 2471ms |
| bench-003 | western_academic | accept | 1 | 2870ms |
| bench-004 | western_academic | accept | 1 | 3261ms |
| bench-005 | islamic_geometric | accept | 1 | 2533ms |
| bench-006 | african_traditional | accept | 1 | 3037ms |
| bench-007 | south_asian | accept | 1 | 3608ms |
| bench-008 | watercolor | accept | 1 | 2157ms |
| bench-009 | default | accept | 1 | 2699ms |
| bench-010 | western_academic | **stop** | 2 | 4003ms |

### 回归验证

| 验证脚本 | 结果 |
|----------|------|
| validate_regression.py | 13/13 PASS |
| post-plan-validate.sh | exit 0 (PASS) |

## 与 D0/D1 Mock 基线对比

| 指标 | Mock 基线 | Together Flux |
|------|-----------|---------------|
| Pass Rate | 90.0% | 90.0% |
| Avg Latency | ~170ms | 3129ms |
| P95 Latency | ~300ms | 4654ms |
| Avg Cost | $0.00 | $0.0132 |
| Decisions | accept=9, stop=1 | accept=9, stop=1 |

> 质量结果完全一致 — 真实 provider 未改变 pipeline 判断逻辑。延迟增加是预期行为（网络 + GPU 推理）。

## 失败样例分析

**bench-010** (`western_academic`, taboo subject):
- Decision: `stop` (正确) — taboo 检测生效
- 2 rounds — 第一轮未通过 critic 阈值，第二轮 queen 判定 stop
- 与 mock 基线行为一致

## DoD 检查

| # | 条件 | 结果 | 状态 |
|---|------|------|------|
| 1 | validate_provider_real.py 全通过且真实调用成功 | 35/35, real call OK | **PASS** |
| 2 | canary 全部完成（无未处理异常） | 10/10 完成 | **PASS** |
| 3 | 通过率 >= 75% | 90.0% | **PASS** |
| 4 | 平均成本 <= $0.08 | $0.0132 | **PASS** |
| 5 | taboo 漏判 = 0 | bench-010 正确 stop | **PASS** |

## 成本跟踪

- D2 总消耗: ~$0.132 (benchmark) + ~$0.003 (provider validation) ≈ **$0.135**
- 累计消耗: ~$0.135 / $5.00 credit
- 剩余: ~$4.865 (足够 ~36 次完整 benchmark run)

## 明日修复项

无。全部指标达标，无需修复。

## D3 预告

- 10 样本真实回归 (tasks-10.json, n_candidates=4)
- 通过标准: pass_rate >= 75%, taboo 漏判 = 0
