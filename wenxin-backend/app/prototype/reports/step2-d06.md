# Step 2 D06: 阈值调优 + Go/No-Go

**日期**: 2026-02-09
**状态**: PASS — 全部 DoD 达标，Decision = **GO**

## 执行命令

```bash
cd <project-root>/wenxin-backend

# Baseline (20t, together_flux)
TOGETHER_API_KEY=*** python3 app/prototype/tools/run_benchmark.py \
  --tasks app/prototype/data/benchmarks/tasks-20.json \
  --provider together_flux --width 512 --height 512 --steps 4 --n-candidates 2 \
  --output app/prototype/reports/step2-d06-baseline.json

# Threshold sweep (10t, together_flux, 15 configs)
TOGETHER_API_KEY=*** python3 app/prototype/tools/run_threshold_sweep.py \
  --tasks app/prototype/data/benchmarks/tasks-10.json \
  --provider together_flux --width 512 --height 512 --steps 4 --n-candidates 2 \
  --output app/prototype/reports/step2-d06-sweep-together.json

# 质量门
python3 app/prototype/tools/validate_regression.py       # 13/13
python3 app/prototype/tools/validate_pipeline_e2e.py     # 35/35
python3 app/prototype/tools/validate_fallback.py         # 19/19
bash .claude/hooks/post-plan-validate.sh                 # exit 0
```

## Baseline 指标 (20 tasks, together_flux)

| 指标 | 值 | 门槛 | 状态 |
|------|-----|------|------|
| Pass Rate | 90.0% | >= 85% | **PASS** |
| Avg Latency | 3154ms | — | — |
| P95 Latency | 7480ms | < 30s | **PASS** |
| Avg Cost | $0.0132 | <= $0.08 | **PASS** |
| Taboo 漏判 | 0 | = 0 | **PASS** |

## Sweep 结果 (15 configs × 10 tasks, together_flux)

| Config | Pass Rate | Avg Cost | Avg Latency |
|--------|-----------|----------|-------------|
| baseline | 90.0% | $0.0132 | 3289ms |
| pass_threshold=0.3 | 90.0% | $0.0132 | 3923ms |
| pass_threshold=0.4 | 90.0% | $0.0132 | 2630ms |
| pass_threshold=0.5 | 90.0% | $0.0132 | 4122ms |
| pass_threshold=0.6 | 90.0% | $0.0132 | 2972ms |
| min_dim_score=0.1 | 90.0% | $0.0132 | 3516ms |
| min_dim_score=0.15 | 90.0% | $0.0132 | 3223ms |
| min_dim_score=0.2 | 90.0% | $0.0132 | 3445ms |
| min_dim_score=0.25 | 90.0% | $0.0132 | 2681ms |
| accept_threshold=0.5 | 90.0% | $0.0132 | 3381ms |
| accept_threshold=0.6 | 90.0% | $0.0132 | 2950ms |
| accept_threshold=0.7 | 90.0% | $0.0132 | 2946ms |
| early_stop=0.7 | 90.0% | $0.0132 | 3047ms |
| early_stop=0.8 | 90.0% | $0.0132 | 2464ms |
| early_stop=0.9 | 90.0% | $0.0132 | 2847ms |

**推荐配置**: baseline（所有配置结果一致，默认即最优）

## 质量门

| 验证脚本 | 通过/总数 | 状态 |
|----------|----------|------|
| validate_regression.py | 13/13 | PASS |
| validate_pipeline_e2e.py | 35/35 | PASS |
| validate_fallback.py | 19/19 | PASS |
| post-plan-validate.sh | exit 0 | PASS |
| **总计** | **67/67** | **ALL PASS** |

## DoD 检查

| # | 条件 | 结果 | 状态 |
|---|------|------|------|
| 1 | baseline + sweep 全部跑完 | 20t + 15×10t = 170 runs | **PASS** |
| 2 | 20 样例 pass_rate >= 85% | 90.0% | **PASS** |
| 3 | taboo 漏判 = 0 | bench-010 + bench-020 均 stop | **PASS** |
| 4 | avg_cost <= $0.08 | $0.0132 | **PASS** |
| 5 | P95 < 30s | 7480ms | **PASS** |
| 6 | regression + e2e + fallback + hook 全通过 | 67/67 + exit 0 | **PASS** |
| 7 | 三份验收文档齐全并给出明确 Go/No-Go | GO | **PASS** |

## 产出文档

| 文档 | 路径 |
|------|------|
| 回归测试报告 | `reports/step2-regression-report.md` |
| 成本与延迟报告 | `reports/step2-cost-latency-report.md` |
| Go/No-Go 决策 | `reports/step2-go-no-go.md` |

## 成本跟踪

| 日期 | 消耗 | 累计 |
|------|------|------|
| D2 | $0.14 | $0.14 |
| D3 | $0.26 | $0.40 |
| D4 | $0.79 | $1.19 |
| D5 | $0.40 | $1.59 |
| D6 | ~$1.25 | ~$2.84 |
| **剩余** | | **~$2.16 / $5.00** |
