# D5 TodoList: Draft 低成本产图链路

> 基线：D1-D4 已通过（环境、Schema、资源库、Scout）  
> 更新日期：2026-02-08

## D5 目标
- 接通 `Draft` 角色，完成低分辨率草图生成链路。
- 单请求稳定产出 `4-6` 张候选草图。
- 产物可追溯：每张图都能回查提示词、参数、seed、模型信息。

## 范围与非目标
- 范围：后端最小可运行链路（输入 Intent Card + Scout evidence，输出草图结果）。
- 非目标：高分辨率渲染、复杂图控（ControlNet/IP-Adapter）、前端交互优化。

## 输入依赖（必须通过）
- [x] `app/prototype/tools/validate_scout.py`（D4）
- [x] `app/prototype/validate_schema.py`（D2）
- [x] `app/prototype/tools/validate_resources.py`（D3）

## 执行清单（按顺序）

### 1) 数据契约
- [ ] 新建 `app/prototype/agents/draft_types.py`
- [ ] 定义 `DraftInput` / `DraftCandidate` / `DraftOutput`
- [ ] 字段包含：`prompt, negative_prompt, seed, width, height, steps, sampler, model_ref, image_path`

### 2) 配置与预算护栏
- [ ] 新建 `app/prototype/agents/draft_config.py`
- [ ] 固化 D5 默认参数（建议：`512x512`, `steps<=20`, `n_candidates=4~6`）
- [ ] 增加预算字段（单请求最大候选数、超时上限、失败重试上限）

### 3) Provider 抽象层
- [ ] 新建 `app/prototype/agents/draft_provider.py`
- [ ] 定义统一接口：`generate_candidates(input) -> DraftOutput`
- [ ] 预留 `local_sd15` 与 `fallback_mock` 两种实现入口

### 4) Draft Agent 主逻辑
- [ ] 新建 `app/prototype/agents/draft_agent.py`
- [ ] 输入：Intent Card + Scout evidence
- [ ] 逻辑：提示词组装 -> 生成候选 -> 结构化返回 -> checkpoint 落盘

### 5) 结果落盘与可追溯
- [ ] 新建 `app/prototype/checkpoints/draft/` 目录规则
- [ ] 每次运行产出 `run.json`（含参数、seed、耗时、失败重试记录）
- [ ] 图片文件与元数据一一对应（可回放）

### 6) 校验脚本
- [ ] 新建 `app/prototype/tools/validate_draft.py`
- [ ] 至少覆盖 3 条样例输入（不同 tradition）
- [ ] 断言：每条输入产出 4-6 张、字段完整、路径存在、无未捕获异常

### 7) D5 报告
- [ ] 生成 `app/prototype/reports/d5-draft.md`
- [ ] 记录：命令、通过率、平均耗时、失败样例、残余风险

## D5 DoD（完成判定）
- [ ] 任意 1 条输入可稳定输出 4-6 张草图（低分辨率）。
- [ ] 每张草图均有可追溯元数据（prompt/seed/model_ref/path）。
- [ ] `validate_draft.py` 输出 `ALL CHECKS PASSED`。
- [ ] D2/D3/D4 回归仍通过，且 `post-plan-validate.sh` exit 0。

## 验证命令模板
```bash
cd wenxin-backend
venv/bin/python app/prototype/tools/validate_draft.py
venv/bin/python app/prototype/tools/validate_scout.py
venv/bin/python app/prototype/validate_schema.py
venv/bin/python app/prototype/tools/validate_resources.py

cd <project-root>
bash .claude/hooks/post-plan-validate.sh
```

## 风险与缓解（先写死到清单）
- 本地显存/依赖不足：先保证 `fallback_mock` 可跑通，标注为降级路径，不计入“真实产图通过率”。
- 生成波动大：固定 `seed` 集合做回归样例，避免每次结果不可比较。
- 超时：设置每条请求超时与重试上限，超限即早停并产出失败原因。
