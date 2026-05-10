# Vulca JEPA 视觉审计实验样本清单

**日期：** 2026-05-10

**目标：** 在 Vulca 仓库内，用 Vulca 已有生成图、编辑图、分层图和 visual-spec 产物测试 JEPA / DINO / SigLIP 类视觉表征是否能给 Vulca 的图像审计增加有效信号。

**范围修正：** 本实验只做 Vulca 项目的视觉审计实验，不做 EmoArt challenge Track2。Track2 的 guard、标签、提交包和 challenge 复现实验都应放在 `/Users/yhryzy/dev/emoart-130k` 另开路径处理。

---

## 1. 实验边界

本实验要回答的是：

- JEPA / DINO 这类 image-only 表征，能不能发现 Vulca 生成图里的主体漂移、结构漂移、风格簇偏移。
- SigLIP / CLIP 这类 text-image 表征，能不能补充判断 prompt 和图像主体是否对齐。
- Vulca 现有 L1-L5 文化评估，和这些 embedding 指标之间是否互补。

本实验不做的是：

- 不训练 challenge 模型。
- 不读取 Track2 标签。
- 不改 challenge 提交包。
- 不把 JEPA / DINO 分数当成 Vulca L1-L5 的替代品。
- 不把静态图实验强行写成 V-JEPA 视频实验。

---

## 2. 模型定位

| 模型族 | 在本实验中的角色 | 适合检查 | 不适合检查 |
|---|---|---|---|
| DINO / DINOv2 | 图像结构和视觉语义 embedding | 主体是否同类、构图是否漂移、promptfix 前后是否更稳定 | 中文文化术语是否正确 |
| I-JEPA | image-only 表征候选 | 静态图的高层结构相似度、异常样本检出 | 文本 prompt 对齐 |
| V-JEPA | 视频或时序视觉表征候选 | 未来有视频、逐帧生成、分层动画时再用 | 当前 Vulca 静态图首轮实验 |
| SigLIP / CLIP | text-image 对齐候选 | prompt 文字和图片主体是否一致 | 细粒度文化审美是否成立 |
| Vulca `evaluate` | 文化和意图审计主线 | L1-L5、tradition、intent、subject、rubric | 低成本批量 embedding 聚类 |

首轮推荐顺序：

1. 先跑不依赖大模型下载的样本 inventory 和 contact sheet。
2. 再跑 DINO / DINOv2 或 SigLIP 的 embedding smoke run。
3. 最后把 embedding 结果和 Vulca 现有 eval JSON / Gemini VLM rescore 做对照。

---

## 3. 第 0 阶段样本包

这些文件已在当前 Vulca 仓库确认存在。

### 3.0 样本分流：core 与 artifact_qa

inventory 不把 30 张图都直接送进 embedding。先做轻量质量预检，再分成两类：

| audit_set | 数量 | 用途 | 是否进入 JEPA/DINO/SigLIP 主实验 |
|---|---:|---|---|
| `core` | 21 | 有真实视觉信息的 gallery、promptfix、inpaint、fusion 样本 | 是 |
| `artifact_qa` | 9 | 黑图、低信息图、layered/defense 中间产物和坏 composite | 否 |

质量预检字段：

- `luma_mean`：亮度均值。
- `luma_stddev`：亮度标准差，用来识别纯色/低信息图。
- `alpha_coverage`：非透明像素占比。
- `near_black_opaque`：近黑且几乎完全不透明。
- `low_information`：亮度变化极低。
- `usable_for_embedding`：是否允许进入主 embedding 实验。
- `reject_reasons`：例如 `near_black_opaque`、`low_information`、`intermediate_artifact`。

这里的黑图和灰图不是好图样本，也不是要展示的视觉结果。它们保留在 `artifact_qa` 里，是为了测试 Vulca 能不能自动挡住坏产物：空层、全黑 composite、坏 edit 输出、低信息中间层。主实验只用 `usable_for_embedding=true` 的样本。

### 3.1 Gallery baseline 与 promptfix 对照

| sample_id | 文件 | 尺寸 | 用途 |
|---|---|---:|---|
| `gongbi_baseline_failed_subject` | `assets/demo/v3/gallery/chinese_gongbi.png` | 1024x1024 | 关键失败样本：原 prompt 是工笔牡丹，但 VLM rescore 记录为山水图，适合测试主体漂移检出 |
| `gongbi_promptfix_seed1` | `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed1.png` | 1024x1024 | promptfix 后的工笔牡丹样本，用于和 baseline 拉开距离 |
| `gongbi_promptfix_seed2` | `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed2.png` | 1024x1024 | promptfix 多 seed 稳定性 |
| `gongbi_promptfix_seed3` | `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed3.png` | 1024x1024 | promptfix 多 seed 稳定性 |
| `xieyi_baseline` | `assets/demo/v3/gallery/chinese_xieyi.png` | 1024x1024 | 与失败 gongbi baseline 可能同属山水簇，用于检查错误样本是否靠近 xieyi |
| `xieyi_promptfix` | `assets/demo/v3/gallery-promptfix/chinese_xieyi.png` | 1024x1024 | promptfix 后的写意山水样本 |
| `japanese_baseline_failed_style` | `assets/demo/v3/gallery/japanese_traditional.png` | 1024x1024 | VLM rescore 记录主体和风格不完全对齐，适合做中等失败样本 |
| `japanese_promptfix` | `assets/demo/v3/gallery-promptfix/japanese_traditional.png` | 1024x1024 | promptfix 后的日本传统样本 |

已知外部审计信号：

- `assets/demo/v3/gemini-vlm-rescore.json` 中 `chinese_gongbi` baseline 总分为 0，`passed=false`。
- 同一文件中 `chinese_xieyi` baseline 总分为 4，`passed=true`。
- `chinese_gongbi_seed1` promptfix 总分为 4，`passed=true`。
- `chinese_gongbi_seed2` promptfix 总分为 3，`passed=true`，但备注指出不是单朵主导花。

### 3.2 Gallery breadth 样本

| sample_id | 文件 | 尺寸 | 用途 |
|---|---|---:|---|
| `western_academic` | `assets/demo/v3/gallery/western_academic.png` | 1024x1024 | 非东亚传统对照 |
| `watercolor` | `assets/demo/v3/gallery/watercolor.png` | 1024x1024 | 媒介风格对照 |
| `islamic_geometric` | `assets/demo/v3/gallery/islamic_geometric.png` | 1024x1024 | 几何纹样对照 |
| `african_traditional` | `assets/demo/v3/gallery/african_traditional.png` | 1024x1024 | 高色彩平面图案对照 |
| `south_asian` | `assets/demo/v3/gallery/south_asian.png` | 1024x1024 | 细密画传统对照 |
| `brand_design` | `assets/demo/v3/gallery/brand_design.png` | 1024x1024 | 产品/品牌视觉对照 |
| `photography` | `assets/demo/v3/gallery/photography.png` | 1024x1024 | 摄影风格对照 |
| `contemporary_art` | `assets/demo/v3/gallery/contemporary_art.png` | 1024x1024 | 抽象艺术对照 |
| `ui_ux_design` | `assets/demo/v3/gallery/ui_ux_design.png` | 1024x1024 | UI 画面类型对照 |

对应评估结果目录：

- `assets/demo/v3/eval/*.json`
- `assets/demo/v3/eval-v2merged/*.json`

这一组用来检查 embedding 是否主要按主体/构图聚类，而 Vulca L1-L5 是否能提供更细的文化和意图判断。

### 3.3 Layered 分层样本

| sample_id | 文件 | 尺寸 | 用途 |
|---|---|---:|---|
| `layered_composite` | `assets/demo/v3/layered/composite.png` | 1024x1024 | 分层重组后的整体图 |
| `layer_base_xuan_paper` | `assets/demo/v3/layered/base_xuan_paper.png` | 1024x1024 | 底纸层 |
| `layer_distant_mountains` | `assets/demo/v3/layered/distant_haze_mountains.png` | 1024x1024 | 远山层 |
| `layer_midground_river_forest` | `assets/demo/v3/layered/midground_river_forest.png` | 1024x1024 | 中景层 |
| `layer_foreground_details_hut` | `assets/demo/v3/layered/foreground_details_hut.png` | 1024x1024 | 前景细节层 |

元数据入口：

- `assets/demo/v3/layered/manifest.json`

这一组归入 `artifact_qa`，不进入首轮 JEPA/DINO 主 embedding。它主要检查：

- layer alpha 覆盖率是否合理。
- 分层输出是否出现空层、重复层或主体层丢失。

### 3.4 Defense no_ref 与 with_ref 对照

| sample_id | 文件 | 尺寸 | 用途 |
|---|---|---:|---|
| `defense_no_ref_composite` | `assets/demo/v3/defense3/no_ref/composite.png` | 1024x1024 | 无参考图分层结果 |
| `defense_with_ref_composite` | `assets/demo/v3/defense3/with_ref/composite.png` | 1024x1024 | 有参考图分层结果 |

对应报告：

- `assets/demo/v3/defense3/no_ref/.layered_cache/*.report.json`
- `assets/demo/v3/defense3/with_ref/.layered_cache/*.report.json`

这一组归入 `artifact_qa`，用于检查 reference 是否改善结构稳定性和 layerability。当前样本如果是全黑 composite，结论不是“reference 无效”，而是“这一路产物需要先被质量闸门挡住”。

### 3.5 Edit / Inpaint 对照

| sample_id | 文件 | 尺寸 | 用途 |
|---|---|---:|---|
| `edit_before` | `assets/demo/v3/edit/before.png` | 1024x1024 | 编辑前图 |
| `edit_after` | `assets/demo/v3/edit/after.png` | 1024x1024 | 编辑后图 |
| `inpaint_before` | `assets/demo/v3/inpaint/before.png` | 1024x1024 | inpaint 前图 |
| `inpaint_after` | `assets/demo/v3/inpaint/after.png` | 1024x1024 | inpaint 后图 |

这一组用于检查局部编辑是否导致全局结构漂移。当前 `edit_before` / `edit_after` 被质量预检识别为全黑不透明图，归入 `artifact_qa`；`inpaint_before` / `inpaint_after` 有真实视觉内容，归入 `core`。后续如果有 mask，再把审计从全图升级到局部区域。

### 3.6 Scottish-Chinese fusion visual-spec 样本

| sample_id | 文件 | 尺寸 | 用途 |
|---|---|---:|---|
| `fusion_source` | `docs/visual-specs/2026-04-23-scottish-chinese-fusion/source.png` | 1280x1707 | 原始街景参考图 |
| `fusion_iter0` | `docs/visual-specs/2026-04-23-scottish-chinese-fusion/iters/7/gen_bfbbacd2.png` | 1024x1024 | additive gongbi overlay 结果图 |

上下文文件：

- `docs/visual-specs/2026-04-23-scottish-chinese-fusion/design.md`
- `docs/visual-specs/2026-04-23-scottish-chinese-fusion/plan.md`

已知审计结果：

- `plan.md` 记录 iter0 的 L2 为 0.65，低于 hard threshold 0.70。
- strict verdict 是 `reject`，但用户选择 `user-override-accept`。

这一组最适合测试“保留原图锚点”和“只增加中式工笔元素”之间的平衡：DINO/JEPA 看结构保留，Vulca L1-L5 看文化与风格完成度。

---

## 4. 第一轮实验问题

### 问题 A：失败的工笔牡丹 baseline 能否被自动挑出来？

输入：

- `gongbi_baseline_failed_subject`
- `gongbi_promptfix_seed1`
- `gongbi_promptfix_seed2`
- `gongbi_promptfix_seed3`
- `xieyi_baseline`

预期：

- DINO/JEPA image embedding 应该显示 `gongbi_baseline_failed_subject` 更接近山水/写意样本，而不是 promptfix 牡丹样本。
- SigLIP/CLIP text-image 分数应该显示 promptfix 牡丹比 baseline 更接近 “single large peony flower / Chinese gongbi”。
- Vulca/Gemini 已有 rescore 用作 ground truth 对照，不被 embedding 替代。

### 问题 B：promptfix 后多 seed 是否稳定？

输入：

- `gongbi_promptfix_seed1`
- `gongbi_promptfix_seed2`
- `gongbi_promptfix_seed3`

预期：

- 三张图在 image embedding 中距离较近。
- seed2 可以被标记为“通过但主体主导性较弱”，因为 VLM rescore 已记录它更像重复图案，而不是单朵主导花。

### 问题 C：Vulca gallery 的传统类别是否能形成可解释簇？

输入：

- `assets/demo/v3/gallery/*.png`
- `assets/demo/v3/eval-v2merged/*.json`

预期：

- embedding 可能按主体和媒介聚类，例如摄影、UI、几何图案、山水。
- L1-L5 分数可能不按 embedding 距离排序，因为文化正确性和视觉相似度不是同一个问题。
- 报告需要明确列出“embedding 有帮助”和“必须交给 Vulca evaluate”的边界。

### 问题 D：分层输出是否出现空层、重复层或语义混乱？

输入：

- `layered_composite`
- `layer_base_xuan_paper`
- `layer_distant_mountains`
- `layer_midground_river_forest`
- `layer_foreground_details_hut`
- `assets/demo/v3/layered/manifest.json`

预期：

- alpha 覆盖率能识别空层或过满层。
- embedding 距离能辅助发现重复层。
- composite 与关键主体层之间应存在可解释关系，但这不是文化打分。

### 问题 E：编辑和 inpaint 是否只改变局部？

输入：

- `edit_before` / `edit_after`
- `inpaint_before` / `inpaint_after`

预期：

- 全图 embedding 距离不应过大。
- 如果全图距离过大，需要人工检查是否出现全局风格漂移。
- 后续有 mask 时，再把审计从全图升级到局部区域。

### 问题 F：Scottish-Chinese fusion 是否保留原图锚点？

输入：

- `fusion_source`
- `fusion_iter0`
- `design.md`
- `plan.md`

预期：

- DINO/JEPA 用于检查源图街景锚点是否仍然明显。
- Vulca L1-L5 用于解释为什么 L2 低于阈值。
- 报告应同时保留 strict reject 和 user override 两条判断，不能用 embedding 分数覆盖人工决策。

---

## 5. 拟新增文件

第一轮只新增实验脚本和报告，不改 Vulca 核心 API。

| 文件 | 责任 |
|---|---|
| `scripts/experiments/vulca_jepa_inventory.py` | 生成样本 manifest，检查路径、尺寸、模式、质量指标和 `core`/`artifact_qa` 分流 |
| `scripts/experiments/vulca_jepa_contact_sheet.py` | 根据 manifest 生成 full/core/artifact_qa contact sheet，便于人工快速查看样本 |
| `scripts/experiments/vulca_jepa_audit.py` | 跑 image embedding / text-image embedding / mock backend，输出 pairwise distance 和异常排序 |
| `scripts/experiments/vulca_jepa_compare_eval.py` | 把 embedding 结果与 `eval-v2merged`、`gemini-vlm-rescore.json` 对齐 |
| `docs/product/experiments/2026-05-10-vulca-jepa-inventory.json` | 样本 manifest 输出 |
| `docs/product/experiments/2026-05-10-vulca-jepa-contact-sheet.png` | 人工审计用 contact sheet |
| `docs/product/experiments/2026-05-10-vulca-jepa-contact-sheet.core.png` | 主 embedding 实验样本 contact sheet |
| `docs/product/experiments/2026-05-10-vulca-jepa-contact-sheet.artifact-qa.png` | 坏产物/中间产物 QA contact sheet |
| `docs/product/experiments/2026-05-10-vulca-jepa-audit.mock.json` | mock backend 审计原始结果 |
| `docs/product/experiments/2026-05-10-vulca-jepa-audit.dinov2.json` | DINOv2 backend 审计原始结果 |
| `docs/product/experiments/2026-05-10-vulca-jepa-audit.siglip.json` | SigLIP/SigLIP2 text-image 审计原始结果 |
| `docs/product/experiments/2026-05-10-vulca-jepa-audit-report.md` | 实验结论报告 |
| `tests/experiments/test_vulca_jepa_inventory.py` | inventory 脚本测试 |
| `tests/experiments/test_vulca_jepa_audit.py` | mock backend 和距离计算测试 |

---

## 6. 执行任务

### Task 1：生成 Vulca-only manifest

命令：

```bash
python3 scripts/experiments/vulca_jepa_inventory.py \
  --out docs/product/experiments/2026-05-10-vulca-jepa-inventory.json
```

预期输出：

```text
wrote docs/product/experiments/2026-05-10-vulca-jepa-inventory.json
samples: 30
missing: 0
groups: gallery_promptfix, gallery_breadth, layered, defense, edit_inpaint, fusion
audit_sets: core=21, artifact_qa=9
```

测试：

```bash
python3 -m pytest tests/experiments/test_vulca_jepa_inventory.py -q
```

预期输出：

```text
8 passed
```

提交建议：

```bash
git add scripts/experiments/vulca_jepa_inventory.py tests/experiments/test_vulca_jepa_inventory.py docs/product/experiments/2026-05-10-vulca-jepa-visual-audit.md
git commit -m "docs: define vulca jepa visual audit samples"
```

### Task 2：生成 contact sheet

命令：

```bash
python3 scripts/experiments/vulca_jepa_contact_sheet.py \
  --manifest docs/product/experiments/2026-05-10-vulca-jepa-inventory.json \
  --out docs/product/experiments/2026-05-10-vulca-jepa-contact-sheet.png

python3 scripts/experiments/vulca_jepa_contact_sheet.py \
  --manifest docs/product/experiments/2026-05-10-vulca-jepa-inventory.json \
  --audit-set core \
  --out docs/product/experiments/2026-05-10-vulca-jepa-contact-sheet.core.png

python3 scripts/experiments/vulca_jepa_contact_sheet.py \
  --manifest docs/product/experiments/2026-05-10-vulca-jepa-inventory.json \
  --audit-set artifact_qa \
  --out docs/product/experiments/2026-05-10-vulca-jepa-contact-sheet.artifact-qa.png
```

预期输出：

```text
wrote docs/product/experiments/2026-05-10-vulca-jepa-contact-sheet.png
tiles: 30
wrote docs/product/experiments/2026-05-10-vulca-jepa-contact-sheet.core.png
tiles: 21
wrote docs/product/experiments/2026-05-10-vulca-jepa-contact-sheet.artifact-qa.png
tiles: 9
```

测试：

```bash
python3 -m pytest tests/experiments/test_vulca_jepa_inventory.py tests/experiments/test_vulca_jepa_contact_sheet.py -q
```

预期输出：

```text
10 passed
```

提交建议：

```bash
git add scripts/experiments/vulca_jepa_contact_sheet.py docs/product/experiments/2026-05-10-vulca-jepa-contact-sheet.png
git commit -m "chore: add vulca jepa contact sheet"
```

### Task 3：实现 mock audit backend

mock backend 只用于验证数据结构、样本过滤和距离矩阵，不用于得出语义结论。它的 embedding 来自图像统计特征，例如 RGB 均值、RGB 标准差、亮度均值、亮度标准差、alpha 覆盖率和画面比例。真实“主体是否接近”“风格是否接近”的结论必须等 DINO/DINOv2、I-JEPA 或 SigLIP backend 接入后再判断。

命令：

```bash
python3 scripts/experiments/vulca_jepa_audit.py \
  --manifest docs/product/experiments/2026-05-10-vulca-jepa-inventory.json \
  --backend mock \
  --out docs/product/experiments/2026-05-10-vulca-jepa-audit.mock.json
```

预期输出：

```text
wrote docs/product/experiments/2026-05-10-vulca-jepa-audit.mock.json
backend: mock
samples: 21
pairwise_distances: 210
```

测试：

```bash
python3 -m pytest tests/experiments/test_vulca_jepa_audit.py -q
```

预期输出：

```text
4 passed
```

提交建议：

```bash
git add scripts/experiments/vulca_jepa_audit.py tests/experiments/test_vulca_jepa_audit.py docs/product/experiments/2026-05-10-vulca-jepa-audit.mock.json
git commit -m "test: add mock backend for vulca jepa audit"
```

### Task 4：跑 DINO / DINOv2 image embedding smoke run

命令：

```bash
python3 scripts/experiments/vulca_jepa_audit.py \
  --manifest docs/product/experiments/2026-05-10-vulca-jepa-inventory.json \
  --backend dinov2 \
  --model facebook/dinov2-base \
  --out docs/product/experiments/2026-05-10-vulca-jepa-audit.dinov2.json
```

预期输出：

```text
wrote docs/product/experiments/2026-05-10-vulca-jepa-audit.dinov2.json
backend: dinov2
model: facebook/dinov2-base
samples: 21
pairwise_distances: 210
```

失败时的可接受输出：

```text
backend unavailable: install torch/transformers or run with --backend mock
```

2026-05-10 实际 smoke run：

```text
wrote docs/product/experiments/2026-05-10-vulca-jepa-audit.dinov2.json
backend: dinov2
model: facebook/dinov2-base
samples: 21
pairwise_distances: 210
```

实际观察到的首轮信号：

- `gongbi_baseline_failed_subject` 的最近邻是 `xieyi_promptfix`，符合“失败工笔牡丹实际更像山水”的预期。
- `gongbi_promptfix_seed1` 和 `gongbi_promptfix_seed2` 互为最近邻，`gongbi_promptfix_seed3` 最近邻也是 seed1，说明 promptfix 牡丹形成了稳定小簇。
- `fusion_source` 与 `fusion_iter0` 互为最近邻，说明 DINOv2 能捕捉 source/edit 之间的结构保留关系。

提交建议：

```bash
git add docs/product/experiments/2026-05-10-vulca-jepa-audit.dinov2.json
git commit -m "data: record vulca dinov2 audit smoke run"
```

### Task 5：跑 SigLIP text-image smoke run

命令：

```bash
python3 scripts/experiments/vulca_jepa_audit.py \
  --manifest docs/product/experiments/2026-05-10-vulca-jepa-inventory.json \
  --backend siglip \
  --model google/siglip2-base-patch16-224 \
  --out docs/product/experiments/2026-05-10-vulca-jepa-audit.siglip.json
```

预期输出：

```text
wrote docs/product/experiments/2026-05-10-vulca-jepa-audit.siglip.json
backend: siglip
model: google/siglip2-base-patch16-224
samples: 21
text_image_scores: 21
```

失败时的可接受输出：

```text
backend unavailable: install torch/transformers or run with --backend mock
```

2026-05-10 实际 smoke run：

```text
wrote docs/product/experiments/2026-05-10-vulca-jepa-audit.siglip.json
backend: siglip
model: google/siglip2-base-patch16-224
samples: 21
text_image_scores: 21
```

实际观察到的首轮信号：

- `gongbi_baseline_failed_subject` 概率为 `0.000086`，明显低于 promptfix 牡丹 seed1 的 `0.007428` 和 seed3 的 `0.034367`，符合“原图主体不对齐”的预期。
- `gongbi_promptfix_seed2` 概率为 `0.002054`，低于 seed1/seed3，和已有 VLM 备注“主体主导性较弱”一致。
- `inpaint_before`、`inpaint_after`、`fusion_source`、`fusion_iter0` 使用的是 `purpose` 文本，不是原始 prompt，所以这些 text-image 分数只作为弱参考，不用于判断文化或编辑质量。

提交建议：

```bash
git add docs/product/experiments/2026-05-10-vulca-jepa-audit.siglip.json
git commit -m "data: record vulca siglip audit smoke run"
```

### Task 6：对齐 Vulca eval 与 Gemini rescore

命令：

```bash
python3 scripts/experiments/vulca_jepa_compare_eval.py \
  --inventory docs/product/experiments/2026-05-10-vulca-jepa-inventory.json \
  --dinov2-audit docs/product/experiments/2026-05-10-vulca-jepa-audit.dinov2.json \
  --siglip-audit docs/product/experiments/2026-05-10-vulca-jepa-audit.siglip.json \
  --eval-dir assets/demo/v3/eval-v2merged \
  --gemini-rescore assets/demo/v3/gemini-vlm-rescore.json \
  --out docs/product/experiments/2026-05-10-vulca-jepa-audit-report.md
```

预期输出：

```text
wrote docs/product/experiments/2026-05-10-vulca-jepa-audit-report.md
matched_eval_files: 13
matched_gemini_items: 8
```

2026-05-10 实际输出已生成：

- `docs/product/experiments/2026-05-10-vulca-jepa-audit-report.md`
- `matched_eval_files=13`
- `matched_gemini_items=8`

报告必须包含：

- 工笔牡丹 baseline 失败样本是否被 embedding 标为异常。
- promptfix 三个 seed 是否比 baseline 更接近。
- 哪些结论只能由 Vulca L1-L5 或人工 override 判断。
- 哪些信号适合进入后续自动 guard。

提交建议：

```bash
git add scripts/experiments/vulca_jepa_compare_eval.py docs/product/experiments/2026-05-10-vulca-jepa-audit-report.md
git commit -m "docs: compare vulca jepa audit with existing evals"
```

---

## 7. 首轮通过标准

首轮实验算通过，需要同时满足：

- manifest 加载 30 个样本，`missing=0`。
- manifest 输出 `audit_sets: core=21, artifact_qa=9`。
- full/core/artifact_qa 三张 contact sheet 能生成，人工可以快速看到样本分流。
- mock backend 测试通过，只对 `usable_for_embedding=true` 的 21 张 core 样本输出 210 个 pair。
- DINOv2 和 SigLIP/SigLIP2 两个真实 backend 均跑通；如果本地环境缺依赖，报告要明确记录失败命令和缺失依赖。
- 报告能解释 `chinese_gongbi.png` 为什么是高价值失败样本。
- 报告明确 JEPA/DINO/SigLIP 不能替代 Vulca L1-L5。
- 没有任何输出写入 `/Users/yhryzy/dev/emoart-130k`。

---

## 8. 下一步建议

下一步实现轻量 guard 原型：只对 `gallery_promptfix` 组报警，不自动拒绝。第一条规则建议是“DINOv2 nearest-neighbor 指向错误类型 + SigLIP prompt-image 概率显著低于 promptfix 对照”时标记为 `subject_drift_warning`。
