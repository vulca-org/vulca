# Prototype TodoList (After D2)

> 基线：D1（环境就绪）+ D2（Schema 固化）已完成
> 更新时间：2026-02-08

## 已完成（复盘）
- [x] D1 环境可运行：前后端启动、关键依赖与导入链修复
- [x] D1 prototype 目录骨架就绪（agents/pipeline/checkpoints/tools/router/ui/data/reports）
- [x] D2 `intent_card.schema.json` 完成（14 root 字段，9 个 `$defs`）
- [x] D2 样例与校验脚本完成：2 valid + 2 invalid
- [x] D2 严格格式校验与一致性约束补强（format + locked/rerun 规则）
- [x] `post-plan-validate.sh` 已接入 schema gate

## 待办（按优先级）

### P0 - D3 素材库骨架（先做）
- [ ] 建立术语词典：`app/prototype/data/terminology/terms.v1.json`
- [ ] 建立禁区规则：`app/prototype/data/terminology/taboo_rules.v1.json`
- [ ] 建立样本索引：`app/prototype/data/samples/index.v1.json`
- [ ] 覆盖 8 个文化传统，每个至少 1 条核心条目
- [ ] 新增校验脚本：`app/prototype/tools/validate_resources.py`

验收：
- [ ] `validate_resources.py` 输出 ALL CHECKS PASSED
- [ ] 任意 tradition 查询可返回 `source + snippet + id`

### P0 - D4 Scout 最小闭环
- [ ] 实现 `SampleMatcher`（Top-K 样本召回）
- [ ] 实现 `TerminologyLoader`（术语命中率）
- [ ] 实现 `TabooRuleEngine`（规则命中）
- [ ] 统一返回结构：`sample_matches / terminology_hits / taboo_violations`

验收：
- [ ] 输入 3 个主题，均返回结构化结果且字段完整

### P1 - D5 Draft 接口准备
- [ ] 定义 `DraftInput`/`DraftOutput` 数据结构（先 mock）
- [ ] 接口级联点与预算字段预留（不接真实模型也可跑）

## 固定质量门（每次 plan 完成后都执行）
```bash
cd wenxin-backend
venv/bin/python app/prototype/validate_schema.py

cd <project-root>
bash .claude/hooks/post-plan-validate.sh
```

## 备注
- 本阶段先不做生产部署；建议至少完成 D3 + D4 gate 后再合并发版。
