# Step 2 D04: 故障与稳定性日

**日期**: 2026-02-09
**状态**: PASS — 全部 DoD 达标

## 执行命令

```bash
cd <project-root>/wenxin-backend

# Fallback 故障注入基线
python3 app/prototype/tools/validate_fallback.py

# 3 轮稳定性重复 (together_flux, 512x512, steps=4, n_candidates=2)
for i in 1 2 3; do
  TOGETHER_API_KEY=*** python3 app/prototype/tools/run_benchmark.py \
    --tasks app/prototype/data/benchmarks/tasks-20.json \
    --provider together_flux \
    --width 512 --height 512 --steps 4 --n-candidates 2 \
    --output app/prototype/reports/step2-d04-bench20-run${i}.json
done

# 质量门
python3 app/prototype/tools/validate_regression.py
python3 app/prototype/tools/validate_pipeline_e2e.py
cd <project-root> && bash .claude/hooks/post-plan-validate.sh
```

## Fallback 故障注入

| Case | 场景 | 结果 |
|------|------|------|
| 1 | Rate limit (429) → fallback to mock | PASS |
| 2 | Timeout on primary + backup → fallback to mock | PASS |
| 3 | All providers fail → AllProvidersFailedError | PASS |
| 4 | Intermittent failure → retry succeeds | PASS |
| 5 | FaultInjectProvider standalone | PASS |
| 6 | build_fallback_provider factory | PASS |
| **总计** | **19/19 checks** | **ALL PASS** |

Fallback chain 在所有故障模式下均正常触发，无未恢复失败。

## 3 轮稳定性指标

| Run | Pass Rate | Avg Latency | P95 Latency | Avg Cost | Taboo |
|-----|-----------|-------------|-------------|----------|-------|
| Run 1 | 90.0% (18/20) | 3179ms | 7933ms | $0.0132 | 0 leaked |
| Run 2 | 90.0% (18/20) | 3125ms | 5807ms | $0.0132 | 0 leaked |
| Run 3 | 90.0% (18/20) | 2870ms | 6143ms | $0.0132 | 0 leaked |

## 波动分析

| 指标 | Mean | Std | CV |
|------|------|-----|-----|
| Pass Rate | 90.0% | **0.0000** | 0% |
| Avg Cost | $0.0132 | **$0.000000** | 0% |
| P95 Latency | 6628ms | **933ms** | 14.1% |
| Avg Latency | 3058ms | **135ms** | 4.4% |

**解读**:
- **Pass rate 零波动** — 判断逻辑完全确定性
- **成本零波动** — 固定 per-image 定价，无变量
- **P95 延迟 CV=14.1%** — 正常网络/GPU 波动范围，最大值 7933ms 远低于 30s hard gate
- **平均延迟 CV=4.4%** — 极其稳定

## Taboo 检测稳定性

| Run | bench-010 | bench-020 | 漏判 |
|-----|-----------|-----------|------|
| Run 1 | stop | stop | 0 |
| Run 2 | stop | stop | 0 |
| Run 3 | stop | stop | 0 |
| **3 轮合计** | **3/3 stop** | **3/3 stop** | **0/6** |

## 最大失败类型分析

无运行时故障或异常。仅有预期行为：
- bench-010/bench-020 在所有轮次中均被 critic 正确标记并由 queen 判 stop

## Fallback 触发率

- 真实 benchmark 中: **0%** — together_flux 全部成功，无需 fallback
- 故障注入测试中: **100%** fallback chain 正常触发

## 质量门

| 验证脚本 | 结果 |
|----------|------|
| validate_fallback.py | 19/19 PASS |
| validate_regression.py | 13/13 PASS |
| validate_pipeline_e2e.py | 35/35 PASS |
| post-plan-validate.sh | exit 0 (PASS) |

## DoD 检查

| # | 条件 | 结果 | 状态 |
|---|------|------|------|
| 1 | 3 轮都完成且无崩溃 | 3/3 完成，60/60 tasks | **PASS** |
| 2 | pass_rate 每轮 >= 80% | 90%/90%/90% | **PASS** |
| 3 | avg_cost 每轮 <= $0.08 | $0.0132/$0.0132/$0.0132 | **PASS** |
| 4 | P95 每轮 < 30s | 7933/5807/6143ms | **PASS** |
| 5 | taboo 漏判 = 0 | 0/6 across 3 runs | **PASS** |
| 6 | fallback + regression + e2e + hook 全通过 | 19+13+35 PASS + exit 0 | **PASS** |

## 成本跟踪

| 日期 | 消耗 | 累计 |
|------|------|------|
| D2 | $0.135 | $0.135 |
| D3 | $0.264 | $0.399 |
| D4 | $0.792 (3 runs × $0.264) | $1.191 |
| **剩余** | | **~$3.81 / $5.00** |

## D5 扩量建议

**建议: GO — 可以进入 D5 扩量**

理由:
1. 3 轮 pass_rate 零波动 (std=0)，判断逻辑完全确定
2. 成本零波动，可预测
3. 延迟波动在正常范围 (P95 CV=14.1%)，峰值 7.9s 远低于 30s 门槛
4. Fallback chain 在故障注入下 100% 正常工作
5. Taboo 检测 6/6 次正确拒绝
6. 所有质量门全通过 (67/67 checks)
7. 剩余 $3.81 credit 足够约 14 次完整 20-task run

## D5 预告

- 阈值初调: threshold sweep with together_flux
- 在真实 provider 下验证不同 critic/queen 阈值配置
