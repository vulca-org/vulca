# D6 TodoList: Critic 评分与门禁（L1-L5）

> 基线：D1-D5 已通过（环境、Schema、资源库、Scout、Draft）  
> 更新日期：2026-02-08

## D6 目标
- 接通 `Critic` 角色，对 `DraftOutput` 候选进行结构化评分与排序。
- 输出 L1-L5 分数、总分、风险标签、通过/不通过结论与理由。
- 为 D7 Queen 提供可执行门禁信号（`pass/fail + reason + rerun_hint`）。

## 范围与非目标
- 范围：后端规则化评估链路（先不依赖重模型），确保可复现、可回归。
- 非目标：真实视觉审美最优判别、复杂多模态评审、线上实时优化。

## 输入依赖（必须通过）
- [x] `app/prototype/tools/validate_draft.py`（D5）
- [x] `app/prototype/tools/validate_scout.py`（D4）
- [x] `app/prototype/tools/validate_resources.py`（D3）
- [x] `app/prototype/validate_schema.py`（D2）

## 执行清单（按顺序）

### 1) 数据契约
- [ ] 新建 `app/prototype/agents/critic_types.py`
- [ ] 定义 `CritiqueInput / CandidateScore / CritiqueOutput`
- [ ] 字段最少包含：`candidate_id, l1_l5_scores, weighted_total, risk_tags, gate_passed, rationale`

### 2) 评分配置与门禁阈值
- [ ] 新建 `app/prototype/agents/critic_config.py`
- [ ] 固化维度权重（L1-L5）与通过阈值（总分阈值 + 硬门禁规则）
- [ ] 增加可调参数：`min_l5`, `critical_risk_block`, `top_k_for_selection`

### 3) 规则化评分器
- [ ] 新建 `app/prototype/agents/critic_rules.py`
- [ ] 输入：`DraftCandidate + Scout evidence + cultural_tradition`
- [ ] 输出：各维度分数（0-1）与维度级理由（便于 rerun 定位）

### 4) 风险标签引擎
- [ ] 新建 `app/prototype/agents/critic_risk.py`
- [ ] 统一风险标签（如 `taboo_critical`, `low_evidence_coverage`, `style_mismatch`）
- [ ] 风险等级映射：`low/medium/high/critical`

### 5) Critic Agent 主逻辑
- [ ] 新建 `app/prototype/agents/critic_agent.py`
- [ ] 对所有候选评分、排序、选优
- [ ] 输出 `gate_passed` 与 `rejected_reasons`，并给出 `rerun_hint`（指向需重跑维度）

### 6) Checkpoint 与可追溯
- [ ] 新建 `app/prototype/checkpoints/critic_checkpoint.py`
- [ ] 落盘 `checkpoints/critique/{task_id}/run.json`
- [ ] 保存：输入快照、各候选评分、最终决策、门禁原因

### 7) 校验脚本
- [ ] 新建 `app/prototype/tools/validate_critic.py`
- [ ] 至少覆盖 4 个用例：3 个正常 + 1 个故意失败（触发门禁拒绝）
- [ ] 断言：评分字段完整、排序稳定、拒绝原因可解释、checkpoint 可读

### 8) D6 报告
- [ ] 生成 `app/prototype/reports/d6-critic.md`
- [ ] 记录：命令、通过率、拒绝样例、阈值设置、残余风险

## D6 DoD（完成判定）
- [ ] 每个候选都能产出 L1-L5 + 总分 + 风险标签。
- [ ] 至少 1 条样例触发 `gate_passed=False` 且理由明确。
- [ ] `validate_critic.py` 输出 `ALL CHECKS PASSED`。
- [ ] D2/D3/D4/D5 回归仍通过，且 `post-plan-validate.sh` exit 0。

## 验证命令模板
```bash
cd wenxin-backend
venv/bin/python app/prototype/tools/validate_critic.py
venv/bin/python app/prototype/tools/validate_draft.py
venv/bin/python app/prototype/tools/validate_scout.py
venv/bin/python app/prototype/tools/validate_resources.py
venv/bin/python app/prototype/validate_schema.py

cd <project-root>
bash .claude/hooks/post-plan-validate.sh
```

## 风险与缓解（先写入清单）
- Mock 图像无法代表真实美学质量：D6 先验证流程可信，D7/D8 再接入更强评估器。
- 规则评分可能偏硬：保留阈值参数化，使用固定样例回归做迭代。
- 解释不足会影响重跑：强制输出维度级 rationale 与 `rerun_hint`。
