# Vulca JEPA 视觉审计实验报告

## 结论摘要

- 样本分流有效：core=21，artifact_qa=9。黑图和低信息中间产物没有进入主 embedding 实验。
- DINOv2 跑通：模型 `facebook/dinov2-base`，样本 21，pairwise=210。
- SigLIP 跑通：模型 `google/siglip2-base-patch16-224`，样本 21，text_image_scores=21。
- 已对齐 Vulca eval 文件 matched_eval_files=13，Gemini rescore matched_gemini_items=8。
- 这些信号能增强 Vulca 的图片理解，但不能替代 Vulca L1-L5；L1-L5 仍负责文化、风格、意图和人工 override 的判断。

## 工笔牡丹 Baseline 失败案例

工笔牡丹 baseline 是当前最重要的正反例：prompt 要求工笔牡丹，但图像实际更像山水。

| 信号 | 结果 |
| --- | --- |
| Gemini baseline total | 0 |
| Gemini baseline passed | False |
| DINOv2 baseline nearest | xieyi_promptfix |
| DINOv2 nearest distance | 0.623181 |
| SigLIP baseline probability | 8.6e-05 |
| SigLIP best promptfix | gongbi_promptfix_seed3 |
| SigLIP best promptfix probability | 0.034367 |

解释：DINOv2 把工笔牡丹 baseline 拉到山水/写意邻近区域；SigLIP 给 baseline 的 prompt-image 分数低于 promptfix 牡丹；Gemini rescore 也记录 baseline 未通过。三者方向一致，说明这类主体跑偏可以形成自动 guard。

## Guard 原型结果

第一版 guard 只在 `gallery_promptfix` 组内运行，且只报警不拒绝；samples=8，warnings=1。

| 字段 | 值 |
| --- | --- |
| guard_scope | gallery_promptfix |
| samples_evaluated | 8 |
| warnings | 1 |
| warning_type | subject_drift_warning |
| rule.action | warn_only |
| siglip_probability_max | 0.001 |
| requires_nearest_family_mismatch | True |
| sample_id | gongbi_baseline_failed_subject |
| action | warn_only |
| nearest_sample_id | xieyi_promptfix |
| siglip_probability | 8.6e-05 |

解释：`subject_drift_warning` 只说明样本需要进入 Vulca 人工/规则复核队列；当前动作为 `warn_only`，不会影响生成结果，也不会覆盖用户 override。

## DINOv2 图像相似度观察

| sample_id | mean_distance | nearest_sample_id | nearest_distance |
| --- | --- | --- | --- |
| african_traditional | 1.39219 | islamic_geometric | 1.26168 |
| islamic_geometric | 1.38851 | african_traditional | 1.26168 |
| ui_ux_design | 1.38639 | brand_design | 1.22569 |
| western_academic | 1.38449 | south_asian | 1.234 |
| fusion_source | 1.3689 | fusion_iter0 | 0.621036 |
| contemporary_art | 1.36676 | inpaint_after | 1.31623 |
| photography | 1.35825 | xieyi_baseline | 1.23215 |
| fusion_iter0 | 1.35203 | fusion_source | 0.621036 |

DINOv2 适合回答图像之间的结构/主体距离。它不理解中文文化术语，也不应该直接判断 L1-L5。

## Vulca L1-L5 文化评估观察

| tradition | L1 | L2 | L3 | L4 | L5 | mean |
| --- | --- | --- | --- | --- | --- | --- |
| chinese_gongbi | 0.85 | 0.65 | 0.8 | 0.9 | 0.9 | 0.82 |
| chinese_xieyi | 0.9 | 0.85 | 0.95 | 1 | 0.9 | 0.92 |
| japanese_traditional | 0.9 | 0.7 | 0.8 | 0.9 | 0.95 | 0.85 |
| brand_design | 0.95 | 0.95 | 0.98 | 0.95 | 0.98 | 0.962 |
| ui_ux_design | 0.9 | 0.9 | 0.95 | 0.9 | 0.85 | 0.9 |

Vulca L1-L5 提供的是文化/风格解释层。例如 `chinese_gongbi` 的 L2 低于其他维度，能指出工笔技法深度不足；DINOv2/SigLIP 只能提示主体或文本对齐问题，不能解释技法层面的失败。

## SigLIP Text-Image 对齐观察

| sample_id | probability | logit | text_source |
| --- | --- | --- | --- |
| inpaint_before | 2.9e-05 | -10.456 | purpose |
| inpaint_after | 3.5e-05 | -10.2679 | purpose |
| gongbi_baseline_failed_subject | 8.6e-05 | -9.36316 | prompt |
| fusion_iter0 | 0.000125 | -8.98671 | purpose |
| gongbi_promptfix_seed2 | 0.002054 | -6.18613 | prompt |
| fusion_source | 0.007242 | -4.92056 | purpose |
| gongbi_promptfix_seed1 | 0.007428 | -4.89504 | prompt |
| japanese_promptfix | 0.009665 | -4.62951 | prompt |

SigLIP/SigLIP2 适合回答图像和文本是否大方向对齐。对 `text_source=purpose` 的样本只能弱参考，因为那不是原始生成 prompt。

## Fusion Source/Edit 保留关系

| 字段 | 值 |
| --- | --- |
| fusion_source nearest | fusion_iter0 |
| fusion_source distance | 0.621036 |
| fusion_iter0 nearest | fusion_source |
| fusion_iter0 distance | 0.621036 |
| fusion_source SigLIP text_source | purpose |
| fusion_iter0 SigLIP text_source | purpose |

DINOv2 能看到 source 与 edit 之间的结构保留关系；但 fusion 的 SigLIP 文本来自 purpose，不足以判断设计 brief 是否完成。

## Artifact QA 样本用途

| sample_id | reject_reasons |
| --- | --- |
| layered_composite | intermediate_artifact,near_black_opaque,low_information |
| layer_base_xuan_paper | intermediate_artifact |
| layer_distant_mountains | intermediate_artifact,near_black_opaque,low_information |
| layer_midground_river_forest | intermediate_artifact,near_black_opaque,low_information |
| layer_foreground_details_hut | intermediate_artifact,near_black_opaque,low_information |
| defense_no_ref_composite | intermediate_artifact,near_black_opaque,low_information |
| defense_with_ref_composite | intermediate_artifact,near_black_opaque,low_information |
| edit_before | near_black_opaque,low_information |
| edit_after | near_black_opaque,low_information |

这些样本不是低质量展示图，而是质量闸门样本。它们应继续用于检测黑图、低信息图、坏 composite 和中间层异常。

## 下一步

- Vulca evaluate/create 已可通过 `--eval-metadata` 读取 guard metadata；下一步把 warning 与当前 image/sample_id 绑定，只在命中当前输入时提示。
- 对 `text_source=purpose` 的样本补真实 prompt/brief 字段，否则 SigLIP 分数只能弱参考。
- 用 Vulca L1-L5 解释 DINO/SigLIP 不能覆盖的文化问题，例如工笔技法深度、风格完成度、用户 override。
- 后续再考虑 I-JEPA/V-JEPA；当前静态图实验里 DINOv2 与 SigLIP 已经覆盖了主要验证问题。
