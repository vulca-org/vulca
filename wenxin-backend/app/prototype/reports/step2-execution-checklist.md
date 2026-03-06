# Step 2 执行清单（真实模型接入）

> 基线：D14 已完成（Mock 闭环通过）  
> 目标：在不破坏现有稳定性的前提下，将 Draft/Critic 逐步切到真实模型，并完成小流量验证。

## S0：发布冻结（Day 0）
- [ ] 冻结 D14 基线：记录当前 commit/tag（建议 `v1.0-prototype`）。
- [ ] 固化配置快照：`critic_config`、`queen_config`、fallback 策略。
- [ ] 归档交付文档：`d14-final.md`、`runbook.md`、`risk-register-final.md`。

DoD:
- [ ] 基线可一键复跑，结果与 D14 对齐（20 样例 90%）。

## S1：真实 Provider 接入（Day 1-3）
- [ ] 在 `Draft Provider` 增加真实模型实现（保留 `mock` 与 fallback）。
- [ ] 增加 provider 配置分层：`dev/mock`、`staging/real`、`prod/real+fallback`。
- [ ] 加入失败分类与重试：429、timeout、5xx、鉴权错误。
- [ ] 记录每次调用：模型、耗时、token/成本、失败原因、fallback 路径。

DoD:
- [ ] `validate_fallback.py` 通过。
- [ ] 单任务可在真实 provider 成功产图并可追溯。

## S2：质量门升级（Day 4-6）
- [ ] 新增真实质量评测维度：视觉一致性、文化术语覆盖、taboo 误触发率。
- [ ] 扩展 `validate_regression.py` 输出：
- [ ] 首轮通过率、平均轮次、fallback 触发率、单位成本、P95 延迟。
- [ ] 建立人工抽检模板（至少 20 样例中抽 5 条双人复核）。

DoD:
- [ ] 自动指标 + 人工抽检均有结果。
- [ ] 指标达到上线阈值（建议：通过率 >= 75%，fallback 失败率 <= 5%）。

## S3：小流量试运行（Day 7-10）
- [ ] 建立 `canary` 入口（仅白名单任务）。
- [ ] 每日固定复盘：失败样例、失败类型、成本漂移、回退频率。
- [ ] 对高频失败项做“定向修复 -> 回归重跑”闭环。

DoD:
- [ ] 连续 3 天无 P0 故障。
- [ ] 关键指标稳定且未明显劣化（与 D14 基线可解释偏差）。

## S4：放量前验收（Day 11-14）
- [ ] 跑满 20 样例真实模型回归。
- [ ] 执行阈值扫参（保留 baseline 对照）。
- [ ] 输出 Step 2 验收包：
- [ ] `step2-regression-report.md`
- [ ] `step2-cost-latency-report.md`
- [ ] `step2-go-no-go.md`

DoD:
- [ ] Go/No-Go 结论明确。
- [ ] 可直接进入放量或明确回退方案。

## 每日必跑质量门（不可跳过）
```bash
cd wenxin-backend
venv/bin/python app/prototype/tools/validate_critic.py
venv/bin/python app/prototype/tools/validate_queen.py
venv/bin/python app/prototype/tools/validate_pipeline_e2e.py
venv/bin/python app/prototype/tools/validate_archivist.py
venv/bin/python app/prototype/tools/validate_fallback.py
venv/bin/python app/prototype/tools/validate_regression.py

cd <project-root>
bash .claude/hooks/post-plan-validate.sh
```

## 风险优先级（先盯这 4 个）
1. 真实模型成本飙升（超预算）
2. 429/超时导致 fallback 连锁触发
3. taboo 误判/漏判影响门禁可信度
4. 人工体验分与自动分数背离
