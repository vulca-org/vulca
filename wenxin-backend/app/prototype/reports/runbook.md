# VULCA Prototype V1 — Runbook

**Date**: 2026-02-08

---

## Quick Start

```bash
cd wenxin-backend

# Verify environment
python3 --version  # 3.10+

# Run single evaluation
python -m app.prototype.ui.cli_demo \
    --subject "Dong Yuan landscape with hemp-fiber texture strokes" \
    --tradition chinese_xieyi \
    --output-dir ./output
```

## Secrets Safety

```bash
cd <project-root>

# 1) Secret scan before commit (recommended if gitleaks is installed)
gitleaks detect --source . --redact
```

```bash
cd <project-root>/wenxin-backend

# 2) Avoid inline secrets in command history
# Bad: TOGETHER_API_KEY=xxx python3 ...

# Option A: load from local env file (must stay untracked)
set -a
source .env.local
set +a

# Option B: read key silently (not echoed)
read -s TOGETHER_API_KEY && export TOGETHER_API_KEY

# 3) Verify local env files are ignored by git
git check-ignore -v .env.local
git check-ignore -v .env.*.local
```

## Full Validation Suite

```bash
cd wenxin-backend

# Run all validation scripts in order
python3 app/prototype/validate_schema.py          # D2: Schema
python3 app/prototype/tools/validate_resources.py  # D3: Data resources
python3 app/prototype/tools/validate_scout.py      # D4: Scout (31 checks)
python3 app/prototype/tools/validate_draft.py      # D5: Draft (81 checks)
python3 app/prototype/tools/validate_critic.py     # D6: Critic (66 checks)
python3 app/prototype/tools/validate_queen.py      # D7: Queen (34 checks)
python3 app/prototype/tools/validate_pipeline_e2e.py  # D8: Pipeline (35 checks)
python3 app/prototype/tools/validate_archivist.py  # D9: Archivist (28 checks)
python3 app/prototype/tools/validate_fallback.py   # D10: Fallback (19 checks)
python3 app/prototype/tools/validate_demo_api.py   # D11: Demo (18 checks)
python3 app/prototype/tools/validate_regression.py # D12: 10-sample (11 checks)

# Post-plan hook
cd <project-root> && bash .claude/hooks/post-plan-validate.sh
```

## Benchmark Runs

```bash
cd wenxin-backend

# 10-sample benchmark
python3 app/prototype/tools/run_benchmark.py \
    --tasks app/prototype/data/benchmarks/tasks-10.json

# 20-sample benchmark
python3 app/prototype/tools/run_benchmark.py \
    --tasks app/prototype/data/benchmarks/tasks-20.json

# Threshold sweep
python3 app/prototype/tools/run_threshold_sweep.py \
    --tasks app/prototype/data/benchmarks/tasks-20.json
```

## Troubleshooting

### Import errors
```bash
# Ensure you're in wenxin-backend/
cd <project-root>/wenxin-backend
python3 -c "from app.prototype.pipeline.run_pipeline import run_pipeline; print('OK')"
```

### Checkpoint cleanup
```bash
# Clear all checkpoints (non-destructive to code)
rm -rf app/prototype/checkpoints/draft/d*
rm -rf app/prototype/checkpoints/critique/d*
rm -rf app/prototype/checkpoints/pipeline/
rm -rf app/prototype/checkpoints/archive/
```

### Gradio not installed
```bash
# Gradio is optional — CLI works without it
pip install gradio  # Only if you need the web UI
```

## Key File Locations

| Purpose | Path |
|---------|------|
| Pipeline runner | `app/prototype/pipeline/run_pipeline.py` |
| CLI demo | `app/prototype/ui/cli_demo.py` |
| Gradio demo | `app/prototype/ui/gradio_demo.py` |
| Benchmark runner | `app/prototype/tools/run_benchmark.py` |
| Threshold sweep | `app/prototype/tools/run_threshold_sweep.py` |
| 10-task data | `app/prototype/data/benchmarks/tasks-10.json` |
| 20-task data | `app/prototype/data/benchmarks/tasks-20.json` |
| Sample index | `app/prototype/data/samples/index.v1.json` |
| Terminology | `app/prototype/data/terminology/terms.v1.json` |
| Taboo rules | `app/prototype/data/terminology/taboo_rules.v1.json` |
| Reports | `app/prototype/reports/` |

## Configuration Reference

### CriticConfig
| Parameter | Default | Description |
|-----------|---------|-------------|
| pass_threshold | 0.4 | Minimum weighted total to pass gate |
| min_dimension_score | 0.2 | Minimum per-dimension score |
| critical_risk_blocks | True | Critical risk tag auto-rejects |
| top_k | 1 | Number of candidates in output |
| weights | L3=0.25 highest | L1-L5 dimension weights |

### QueenConfig
| Parameter | Default | Description |
|-----------|---------|-------------|
| max_rounds | 2 | Maximum iteration rounds |
| max_cost_usd | 0.10 | Per-task cost ceiling |
| accept_threshold | 0.6 | Score threshold to accept |
| early_stop_threshold | 0.8 | Score for immediate accept |
| min_improvement | 0.05 | Minimum inter-round improvement |
| downgrade_at_cost_pct | 0.8 | Cost threshold for downgrade |
