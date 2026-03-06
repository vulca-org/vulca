# D4 TodoList: Scout 最小闭环

> 基线：D1 + D2 + D3 已完成  
> 更新日期：2026-02-08

## D4 目标
- 实现 3 个 Scout 锚定工具：`SampleMatcher`、`TerminologyLoader`、`TabooRuleEngine`。
- 统一输出结构，直接对齐 Intent Card `evidence` 字段：
  - `sample_matches`
  - `terminology_hits`
  - `taboo_violations`

## 输入依赖（必须先通过）
- [x] `app/prototype/data/samples/index.v1.json`
- [x] `app/prototype/data/terminology/terms.v1.json`
- [x] `app/prototype/data/terminology/taboo_rules.v1.json`
- [x] `app/prototype/tools/validate_resources.py`

## 开发清单（按顺序）

### 1. 定义接口与输出协议
- [ ] 新建 `app/prototype/tools/scout_types.py`
- [ ] 定义 `SampleMatchResult` / `TerminologyHitResult` / `TabooViolationResult`
- [ ] 约束字段命名与 D2 schema 一致（`sample_id/similarity/source` 等）

### 2. 实现 `SampleMatcher`
- [ ] 新建 `app/prototype/tools/sample_matcher.py`
- [ ] 基于 `index.v1.json` 做关键词/标签 Top-K 召回
- [ ] 输出 `{sample_id, similarity, source}`（含可解释命中理由）

### 3. 实现 `TerminologyLoader`
- [ ] 新建 `app/prototype/tools/terminology_loader.py`
- [ ] 基于 `term_zh / term_en / aliases` 匹配主题文本
- [ ] 输出 `{term, matched, confidence, dictionary_ref}`

### 4. 实现 `TabooRuleEngine`
- [ ] 新建 `app/prototype/tools/taboo_rule_engine.py`
- [ ] 按 tradition + wildcard 规则做触发检测
- [ ] 输出 `{rule_id, description, severity}`

### 5. 实现 Scout 聚合入口
- [ ] 新建 `app/prototype/tools/scout_service.py`
- [ ] 统一接口：输入 `subject + cultural_tradition`，返回三类 evidence
- [ ] 返回结构可直接写入 Intent Card `evidence`

### 6. 验证脚本与演示
- [ ] 新建 `app/prototype/tools/validate_scout.py`
- [ ] 固定 3 条主题做回归（覆盖至少 3 个 tradition）
- [ ] 打印结构化输出与字段完整性结果

### 7. D4 报告
- [ ] 生成 `app/prototype/reports/d4-scout.md`
- [ ] 记录命令、通过率、示例输出、剩余风险

## D4 DoD（完成判定）
- [ ] 3 个工具均可单独调用并返回非空结果
- [ ] 聚合接口返回字段与 D2 evidence schema 对齐
- [ ] `validate_scout.py` 输出 `ALL CHECKS PASSED`
- [ ] D2/D3 回归仍通过：
  - `venv/bin/python app/prototype/validate_schema.py`
  - `venv/bin/python app/prototype/tools/validate_resources.py`
  - `bash .claude/hooks/post-plan-validate.sh`

## 执行命令模板
```bash
cd wenxin-backend
venv/bin/python app/prototype/tools/validate_scout.py
venv/bin/python app/prototype/validate_schema.py
venv/bin/python app/prototype/tools/validate_resources.py

cd <project-root>
bash .claude/hooks/post-plan-validate.sh
```
