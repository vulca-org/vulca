# VULCA Solution Pack v1 客户叙事与文案简报（中文审核版）

**日期：** 2026-06-21
**状态：** 中文审核稿，仅供主会话和用户 review
**范围：** 客户第一眼叙事、三类客户文案、短邮件草稿、PDF 开场文案、
CTA、术语口径和安全边界

这不是外联执行文件，也不是可直接发送的邮件。只有在主会话和用户审核
正式客户 PDF 与最终文案后，才可以进入外发准备。

相关内部研究：

- `docs/product/2026-06-21-vulca-reference-company-deep-research-brief.md`

主线会话 `019ee5a2-15dc-72b2-a900-6e8cb1ab6cfa` 完成后，已纳入的输入：

- commit `7aab0468`：clarify three-lane purpose map
- commit `519e26a6`：Creatify workflow deep proof
- commit `c9b292fc`：Seedream / BytePlus deep proof
- commit `ef9cd2b3`：PROYA source-safe distilled card
- commit `e3454235`：PROYA deep proof artifacts

## 本分支参考的上下文

本分支已阅读或参考：

- `assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/README.md`
- `assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/manifest.json`
- `docs/product/workspace-current-state-audit.md`
- `docs/agent-native-workflow.md`
- Lane A / PROYA production brief：commit `6030f437`
- Lane B / Seedream-BytePlus production brief：commit `cb2b7eea`
- Lane C / Creatify production brief：commit `49ebf1e4`
- 主线 internal preview README：commit `7aab0468`
- 主线 PROYA、Seedream / BytePlus、Creatify 三张 source-safe card 的逻辑：
  commits `ef9cd2b3`、`c9b292fc`、`519e26a6`

当前 review branch 仍未包含：

- `docs/product/2026-06-20-vulca-solution-pack-v1-pdf-storyboard.md`
- `docs/product/2026-06-20-vulca-solution-pack-v1-master-pdf-production-plan.md`
- 已 checkout 的 `docs/product/lane-work/*production-brief.md`

所以上述缺失文件不能被当作当前分支的 canonical input；只有后续真正导入
当前 review branch 后，才能按导入版本更新中文稿。

## 客户第一眼需要理解什么

### 一句话版本

VULCA 帮助团队在 AI 辅助视觉素材进入公开发布、campaign、电商渠道或
客户审核流程之前，把这些素材整理成有来源、有审核问题、有负责人路径的
证据包。

### 短版本

现在的视觉团队正在更快地生产和复用图片、视频、产品页、广告素材和
AI 生成内容。问题不只是“能不能生成一张图”，而是：这张图来自哪里，
它表达了什么，哪些信息还需要人工确认，谁拥有最终发布决定。

VULCA Solution Pack v1 要展示的是这中间缺失的一层：release-evidence
layer。它把公开素材、截图、产品图、生成内容、工作流页面和审核问题
整理成一组可读的 evidence cards，让团队在公开使用之前能看到：
source context、visual annotation、review question、owner route 和
human review gate。

### 客户应该马上明白的边界

- VULCA 不是另一个图片生成器。
- VULCA 不是法律意见、合规认证、平台审核保证或自动批准系统。
- VULCA 做的是 evidence-assisted、human-reviewed、source-backed 的
  发布前证据整理。
- 文档里出现的命名公司只能是 public example，不能被写成 VULCA 客户、
  合作方、背书方、授权来源或负面审计对象。

### 第一版正式客户 PDF 的默认读者

建议第一版正式客户 PDF 默认打 **brand / ecommerce / AI ad workflow owner**。
他们的痛点最清楚：产品图、AI 生成广告候选、marketplace 素材、campaign
handoff 都可能跑得很快，但 source context、review question 和 release owner
没有同步跟上。

AI creative 平台、creative ops 和 founder/operator 仍然是次级读者，但第一版
不要写成泛泛的 creative tool pitch。

### 更直白的痛点句

现在团队生成、修改、复用视觉素材的速度已经超过了他们解释这些素材的能力。
在一张图、一条广告候选或一个产品视觉进入 campaign、marketplace listing、
client review 或 public page 之前，仍然需要有人回答：它来自哪里，它代表了
哪个产品或 claim，生成或编辑上下文是什么，还有哪些问题没解决，谁拥有最终
发布决定。

这就是 VULCA 要解决的缺口。

### 三条 lane 的叙事地图

| Lane | 审核对象 | 核心问题 | evidence-card 输出 |
| --- | --- | --- | --- |
| A / Product-truth | 已有商业物料和产品 claim | campaign、产品表达、source、渠道复用和 owner route 能否串起来？ | Product-truth evidence card |
| B / AI publishability | 一个 AI 生成素材或一组生成素材 | 这个 AI output 能否发布或复用？source、prompt/reference、model context、label posture 和 owner route 是否附上？ | AI publishability evidence card |
| C / AI ad workflow | product-to-ad workflow 和 campaign handoff | product URL/listing/brief 如何变成 candidate creative、review state、export state 和 campaign owner handoff？ | AI ad workflow handoff card |

短规则：A 是 claim/material level，B 是 generated-asset level，C 是
workflow/handoff level。C 里面可以包含很多 B 类型的生成素材，但 C 的主证明是
工作流和交接路径，不是单张生成图或视频。

## 三类客户叙事变体

### 变体 A：消费品 / 美妆 / 电商公司

**适用对象：** 美妆品牌、产品团队、电商团队、marketplace 运营、
零售渠道负责人。

**客户问题：**

一张产品图、一句 campaign claim、一个活动展示或一个电商页面，很快会
被复用到 retail display、PDP、社媒、广告、内部材料和销售渠道里。
团队真正需要回答的是：

- 这个视觉 claim 的来源是什么？
- 这张图到底代表哪个产品、哪个场景、哪个渠道？
- 如果要跨渠道复用，谁需要确认？
- 哪些素材只是公开来源，哪些可以进入正式发布材料？

**VULCA 叙事：**

VULCA 可以把这些视觉素材整理成 product-truth evidence card。它不是在
说某个公开案例“有问题”，而是把 visible claim、source trail、
product representation 和 release owner 放在同一张卡里，让团队知道
发布前需要补什么证据、问谁、怎么留痕。

**客户可读文案：**

For product and campaign teams, VULCA turns public-facing visual material into
a reviewable source trail. A campaign display, product image, event cue, or
marketplace page becomes a compact evidence card: visible claim, source
context, product representation, channel role, and release owner.

**中文解释稿：**

对于产品和 campaign 团队，VULCA 把公开视觉素材变成可审核的 source
trail。一个 campaign 展示、产品图、活动线索或 marketplace 页面，
可以被整理成一张 evidence card：可见 claim、来源上下文、产品表达、
渠道角色和负责人路径。

**内部提醒：**

PROYA 只能作为 public market example。不能写成 VULCA 审计了 PROYA，
不能写成 PROYA 有问题，不能写成 VULCA 已确认 claim 准确性或权利状态。
外发前不能直接使用未经处理的 raw source crops。

### 变体 B：AI Creative / Generated Media 平台

**适用对象：** AI 图像/视频平台、创意工具公司、使用生成式内容的品牌
studio。

**客户问题：**

生成式视觉经常被当作“输出文件”处理，但真正决定它能否被复用的是：

- prompt / reference 来源是否保留？
- model 或 workflow context 是否清楚？
- 输出状态是 demo、draft、export 还是 campaign candidate？
- 是否需要 AI label / disclosure？
- 谁拥有 release decision？

**VULCA 叙事：**

VULCA 不评价某个模型好不好，也不认证某个模型是否安全。VULCA 做的是
围绕 generated media 建立 review packet：input/source、model or
workflow context、output status、label posture、unresolved questions 和
release owner。

**客户可读文案：**

For AI creative teams, VULCA makes generated assets inspectable before reuse.
A generated image or video candidate is paired with its prompt/reference
context, source pages, output state, label posture, and owner route so teams can
review what may move forward and what still needs human decision.

**中文解释稿：**

对于 AI creative 团队，VULCA 让生成式素材在复用前变得可检查。一张生成图
或视频候选，不只是一个文件，而是应该和 prompt/reference context、
source pages、output state、label posture 和 owner route 放在一起，
让团队判断哪些可以继续推进，哪些还需要人工确认。

**内部提醒：**

Seedream / BytePlus 保持 version-neutral，除非主会话明确选择某个版本。
Kling 保留为 internal reserve，除非正式 PDF 明确覆盖 video/reference
workflow。

### 变体 C：AI Ad Workflow / Creative Automation 公司

**适用对象：** URL-to-video 平台、AI ad builder、creative automation
公司、growth / creative ops 团队。

**客户问题：**

产品链接、listing、图片或 brief 可以快速生成多条广告候选。商业问题
不只是“生成了多少条广告”，而是：

- 哪个 source input 影响了这条广告？
- 哪个 workflow step 生成了候选？
- hook / body / CTA 是否被 review？
- 输出是否进入 export、campaign 或客户审核？
- 谁负责最终 campaign handoff？

**VULCA 叙事：**

VULCA 把 AI ad workflow 里的 source input、generated candidate、
review context、export state 和 campaign owner 整理成 handoff packet。
它不把 vendor case-study 或营销数字变成 VULCA 的 performance claim。

**客户可读文案：**

For AI ad workflow teams, VULCA turns generated campaign candidates into
handoff packets. Product URL, generated candidate, review context, export state,
and campaign owner are captured in one evidence card before assets move into a
launch or client-review workflow.

**中文解释稿：**

对于 AI ad workflow 团队，VULCA 把生成式 campaign candidates 变成可交接的
证据包。Product URL、generated candidate、review context、export state
和 campaign owner 会被放进同一张 evidence card，帮助团队在进入 launch
或客户审核流程前完成发布前整理。

**内部提醒：**

Creatify 可以作为 public workflow example。Alibaba case-study material 默认只
作为 internal reference，除非主会话明确批准具体引用方式和 attribution。

## 具体 Before / After Example

这个例子可以作为第一版客户 PDF 和 founder note 的主线。

### Before VULCA

团队或 AI 广告工作流从 product URL、listing、图片或 brief 开始，很快生成多条
campaign candidates。这些候选可能继续被编辑、导出、发给客户、进入 seller
portal，或者准备投放 paid social。问题是：输出已经存在，但 review context
是散的：

- source input 和 generated candidate 可能分离；
- hook、body、CTA、product fit、claim fit、brand fit 没有变成 review fields；
- draft / edit / export / channel state 不清楚；
- campaign owner 不知道哪些问题还没有解决；
- vendor screenshot 或第三方案例材料不能直接安全复用。

### After VULCA

VULCA 把同一条链路整理成 release-evidence packet：

```text
product URL / listing / source input
-> generated campaign candidate
-> review anatomy: hook, body, CTA, scene, product fit, claim fit, brand fit
-> edit and export state
-> source-safe visual treatment
-> missing-field list
-> campaign owner route
-> bounded human review gate
```

这个输出不是广告效果预测、法律审核、平台许可或自动批准；它是一份 compact
packet，让人工负责人在素材进入 launch、client review、marketplace 或 campaign
handoff 前可以检查。

### 客户可读英文

For ecommerce and AI ad workflow teams, VULCA turns generated campaign
candidates into reviewable handoff packets. Product URL, source input,
generated candidate, creative anatomy, export state, missing fields, and
campaign owner are captured before assets move into launch or client-review
workflows.

## VULCA 技术基座的客户语言

不要在客户第一页堆内部技术名词。应该把技术基座翻译成客户能理解的结果：

- **Source read:** public 或 provided source material 被保留为 review
  context，而不是装饰性截图。
- **Visual field read:** visible claim、product representation、generated
  output、label posture、workflow state 被变成字段。
- **Source-safe treatment:** raw screenshots、untreated crops、local paths、
  third-party case-study material 默认留在内部，除非 redraw、mask、crop 或
  clearance。
- **Evidence card:** 客户看到的是 compact review object，不是一堆截图文件夹。
- **Owner route:** unresolved fields 被路由到能做 release decision 的人工角色。

## 短邮件草稿

**状态：** review draft only。不是 ready to send，不得直接外发。

**标题选项：**

- A source-backed review packet for AI-assisted visual assets
- Thoughtful sample: release evidence for generated and product visuals
- Can I share a short VULCA visual evidence pack?

**英文草稿：**

Hi {{name}},

I am working on VULCA, a visual review workflow for teams shipping AI-assisted
campaign, ecommerce, and generated-media assets.

The problem we are exploring is narrow: before a visual asset is reused in a
public channel, teams often need a compact record of the source context, visible
claim or generated-output context, review questions, owner route, and human
release gate.

I have a short sample Solution Pack built from public examples. It is not a
legal or compliance opinion, and it does not treat any named company as a
customer or finding. The goal is to show what a source-backed evidence packet
could look like for product visuals, generated media, and AI ad workflows.

Would you be open to reviewing the sample and telling me whether this kind of
release-evidence workflow maps to problems your team or customers actually see?

No private assets needed for this first review.

Best,
{{sender}}

### 主线 proof 后的修订版

**状态：** review draft only。不是 ready to send。

Hi {{name}},

I am working on VULCA, a release-evidence workflow for teams shipping
AI-assisted product visuals, campaign assets, and generated ad candidates.

The specific problem is not generation. It is what happens right before reuse:
teams often need to know what source input shaped an asset, what product or
claim it represents, what review fields are still missing, and who owns the
release decision.

I have a short sample pack built from public examples. It shows three review
lanes: product-truth evidence, AI publishability context, and AI ad workflow
handoff. The pack is not legal advice, a compliance certification, or a finding
about any named company.

Could I send it over and ask whether this maps to a real review bottleneck you
see in ecommerce, campaign, or AI creative workflows?

No private assets needed for this first review.

Best,
{{sender}}

**中文审核解释：**

这封邮件的姿态应该是 founder/operator 的 thoughtful note，而不是销售邮件。
它只问对方是否愿意 review 一个 sample，不索取 private assets，不承诺 demo，
不说我们已经做完某个客户的审计，也不把 PDF 标成正式报告。

## PDF 开场文案

### Page 1 开场

**Title:** VULCA Solution Pack v1

**Subtitle:** Source-backed evidence packets for AI-assisted visual release.

AI-assisted visuals are becoming part of everyday launch, ecommerce, campaign,
and client-review workflows. The bottleneck is no longer only creating an image
or video candidate. The bottleneck is explaining what it came from, what it
represents, what still needs review, and who owns the release decision.

VULCA Solution Pack v1 shows a compact release-evidence workflow using public
examples. Each example is treated as a market pattern, not as a customer,
endorsement, authorization source, or negative finding.

**中文审核解释：**

第一页要让客户马上明白：我们不是来展示“AI 能生成图片”，而是展示“AI 视觉
资产公开使用前，需要一层可追踪、可审核、有人负责的 evidence workflow”。

### Page 2 开场

The pack is built around three operating lanes:

1. **Product-truth and claim evidence:** visible campaign or product material
   becomes a source-backed evidence card.
2. **AI publishability context:** generated assets are paired with input/source,
   workflow context, output state, label posture, and owner route.
3. **AI ad workflow evidence:** product-link or brief-to-ad workflows become
   handoff packets for growth, creative-ops, or campaign owners.

The output is not a final approval. It is a structured packet for qualified
human review: source context, visual annotation, evidence card, owner route,
and bounded next action.

**中文审核解释：**

第二页要把三条线说清楚：产品真实性 / AI 生成内容可发布性 / AI 广告工作流。
但要避免写得像三个“审计报告”。它们都是 public example 和 evidence-card
pattern。

### 推荐正式 PDF 顺序

1. **Why now:** AI-assisted visual production 正在 ecommerce、campaign、
   generated media、ad workflow 里规模化。
2. **Problem:** release context 没有同步规模化。Source、claim、
   generated-output state、product fidelity、label posture、owner route 分散。
3. **VULCA packet:** VULCA 把 asset 或 workflow 变成 source-backed evidence
   packet，用于 human review。
4. **Three lanes:** product-truth evidence、AI publishability context、AI ad
   workflow handoff。
5. **Concrete example:** product URL / listing -> generated campaign candidate
   -> review fields -> export state -> missing-field list -> campaign owner。
6. **Pilot ask:** public examples 或 sanitized assets，小范围、一个 review
   lane、短 readout。

## 客户正式版压缩文案包

**状态：** review draft only。这一节是未来正式客户 PDF 和外联 note 的压缩文案
源，但仍然需要 final review、visual export safety checks 和 recipient-specific
framing 后才能外部使用。

### PDF 开场 Draft

**Title:** VULCA Solution Pack v1

**Subtitle:** Release-evidence packets for AI-assisted visual assets.

AI-assisted visual production is scaling across ecommerce, campaign, generated
media, and ad workflows. Teams can now turn product URLs, listings, prompts,
and briefs into many visual candidates quickly. The bottleneck is no longer
only making the asset. The bottleneck is explaining what it came from, what it
represents, what is still missing, and who owns the release decision.

VULCA is a release-evidence workflow for that gap. It turns source input,
visual or generated-output context, review fields, source-safe visual
treatment, and owner routing into a compact packet for qualified human review.

This sample pack uses public examples only. Named companies are market examples
for workflow discussion, not VULCA customers, partners, endorsers,
authorization sources, or findings.

**中文审核解释：**

这版开场比之前更紧：先讲 AI 视觉生产已经规模化，再讲真正瓶颈是 release
context，然后才说 VULCA。客户第一眼应该理解：我们不是卖生成，而是卖发布前
可审核的证据包。

### Pack 展示什么

- **Product-truth evidence:** visible commercial material becomes a
  source-backed evidence card.
- **AI publishability context:** generated assets are paired with source,
  prompt/reference, model/workflow context, output state, label posture, and
  owner route.
- **AI ad workflow handoff:** product URL or listing workflows become campaign
  handoff packets with source input, generated candidate, review anatomy,
  export state, missing fields, and owner route.

**中文审核解释：**

这三条要短，不要展开成三份审计报告。A 是已有商业物料，B 是生成素材本身，C 是
从 product URL/listing 到 campaign handoff 的工作流。

### Before / After 单页 Draft

**Before:** A product URL, listing, image, or brief quickly becomes multiple ad
or product-visual candidates. The output can move into editing, export, client
review, seller portals, marketplace listings, or paid social. But source input,
product or claim context, creative anatomy, edit/export state, unresolved
questions, and release ownership often sit in different places.

**After:** VULCA turns that flow into a reviewable release-evidence packet:

```text
source input
-> generated or edited candidate
-> product / claim / creative-anatomy fields
-> output and export state
-> source-safe visual treatment
-> missing-field list
-> owner route
-> bounded human review gate
```

**Reader takeaway:** VULCA does not replace generation, legal review, platform
review, or campaign performance measurement. It gives the release owner a
compact source-backed packet before the asset moves forward.

**中文审核解释：**

这一页是目前最应该放进正式客户 PDF 的“落地例子”。它解释 VULCA 到底把一条
AI 广告/电商视觉链路变成什么，不再只讲概念。

### Short Outreach Draft V3

**状态：** review draft only。必须等客户 PDF 和收件人 framing 审核后才能外部
使用。

**Subject options:**

- A short release-evidence sample for AI-assisted visual assets
- Public-example pack: source context for generated product visuals
- Can I share a VULCA visual evidence sample?

**Draft:**

Hi {{name}},

I am working on VULCA, a release-evidence workflow for teams shipping
AI-assisted product visuals, campaign assets, and generated ad candidates.

The specific gap is not generation. It is the review moment before reuse: what
source input shaped the asset, what product or claim it represents, what fields
are still missing, and who owns the release decision.

I have a short sample pack built from public examples. It shows how a product
visual, generated asset, or product-to-ad workflow can become a compact
source-backed review packet.

The sample is not legal advice, a compliance certification, platform approval,
or a finding about any named company. No private assets are needed for a first
review.

Could I share it and ask whether this maps to a real review bottleneck you see
in ecommerce, campaign, or AI creative workflows?

Best,
{{sender}}

**中文审核解释：**

这版邮件比前一版更像 founder/operator 的短 note：先定义 VULCA，再讲具体 gap，
再说明 sample pack 是 public examples，不索取 private assets。

### 客户版内容取舍规则

正式客户 PDF 可以放：

- `Why now -> Problem -> VULCA packet -> Example -> Pilot` 顺序；
- concise three-lane map；
- 围绕 product URL / listing 到 campaign handoff 的 before/after example；
- source-safe card visuals 或 redrawn workflow strips；
- narrow review / feedback / bounded-pilot CTA。

保持 internal-only：

- funding、ARR、valuation、org structure research、competitor critique；
- raw source screenshots、local capture paths、debug overlays、untreated crops；
- Alibaba case-study metrics，除非之后明确批准 attribution 和 metric controls；
- 任何 legal、rights、platform、model-safety、release-readiness 或 performance
  conclusion。

## CTA 文案

### 保守版 CTA

If this matches a real workflow you see, we would value your feedback on the
sample pack: which fields are useful, which are missing, and where a bounded
pilot would need to fit into an existing review process.

**中文解释：**

如果这个工作流和你们实际看到的问题相似，我们希望你能 review 这份 sample
pack：哪些字段有用，哪些缺失，如果做一个 bounded pilot，它应该如何嵌入
你们已有的 review process。

### Pilot 讨论版 CTA

If the workflow is relevant, the next step could be a bounded pilot discussion:
public examples or sanitized assets only, a small number of visual materials,
one review lane, and a short readout focused on source context, evidence cards,
owner routing, and what should or should not move forward.

**中文解释：**

如果对方感兴趣，下一步也只是 bounded pilot discussion：public examples 或
sanitized assets，小批量视觉素材，一个 review lane，一份短 readout。不要在
第一封里索取 private assets。

### 反馈版 CTA

The most useful feedback would be practical: whether your team already tracks
source context, prompt/reference records, generated-output state, and release
ownership; and whether these fields would help before assets enter public,
client, marketplace, or campaign workflows.

**中文解释：**

我们最想要的反馈不是泛泛评价，而是实际工作流问题：他们是否已经记录
source context、prompt/reference、generated-output state 和 release owner；
这些字段在进入 public / client / marketplace / campaign workflow 前是否有用。

## 术语表

| 术语 | 中文解释 | 客户可读英文口径 |
| --- | --- | --- |
| Source-backed evidence pack | 有来源记录的证据包，把素材、来源、审核问题、证据卡和负责人路径连起来。 | A compact packet that links visual assets to source context, review questions, evidence cards, and owner routing before reuse. |
| Public example | 公开市场案例，只用于解释工作流模式。不是客户、合作方、背书方、授权来源或发现对象。 | A publicly available market example used to explain a workflow pattern. It is not a customer, partner, endorsement, authorization source, or finding. |
| Release owner | 拥有发布前最终判断的人工负责人或角色。 | The human role responsible for deciding whether unresolved questions are resolved, escalated, blocked, or allowed to move forward. |
| Evidence card | 一张结构化卡片，记录可见素材、来源上下文、审核问题、当前状态、建议动作和 owner route。 | A structured card that records the visible asset context, source context, review question, current state, suggested action, and owner route. |
| Human review gate | 人类负责人基于证据做决定的关口。VULCA 可以准备证据包，但不能替人批准发布。 | The point where a qualified human owner reviews the evidence and decides the next action. VULCA can prepare the packet; the human owner decides. |
| Source-safe visual treatment | 对 raw screenshot / crop 做 crop、mask、redraw、anonymize 或 replace，避免外发时暴露本地路径、未清理截图、权利不清或误导性展示。 | Cropping, masking, redrawing, anonymizing, or replacing raw source visuals so customer-facing material avoids local paths, raw screenshots, unclear rights, and misleading source presentation. |

## Safety Copy Bank

这些句子用于客户 PDF、短邮件或说明页里建立边界：

- This sample uses public examples to show workflow patterns; it does not imply
  a customer relationship, endorsement, authorization, or audit target.
- VULCA prepares source-backed review evidence for qualified human decision
  makers.
- This is not legal advice, a compliance certification, platform approval, or
  model-safety certification.
- VULCA does not guarantee campaign performance, marketplace approval, platform
  acceptance, rights clearance, or final release outcome.
- The pack should not describe a named public company as having a negative
  finding.
- Raw screenshots, local files, capture-batch labels, and untreated source crops
  are internal evidence basis only unless separately cleared and treated.
- The initial review can use public examples or sanitized materials; it should
  not request private assets in the first note.

**中文审核解释：**

这部分不能删。它保证客户不会把这份 PDF 理解成法律意见、合规报告、平台审核
保证、正式审计或对某个命名公司的负面结论。

## 主线 deep proof 状态

主线现在已经为三条 lane 产出内部 deep-proof 输入：

1. **Lane A / PROYA:** public source-backed visual -> visual annotation ->
   field extraction -> evidence-card draft -> owner route -> source-safe visual
   treatment decision。
2. **Lane B / Seedream / BytePlus:** public model/tool source pages -> field
   annotation -> source、input、model、output、label、owner fields ->
   source-safe publishability card。
3. **Lane C / Creatify:** public product-to-video workflow source ->
   workflow-field annotation -> source input、candidate creative、review
   anatomy、export state、owner route -> source-safe campaign handoff card。

这意味着“必须等 proof 才能写叙事”的缺口已经解决；但正式客户 PDF 仍然不能
直接外发。客户版还需要 master PDF safety gate、source-safe visual treatment、
final copy review 和 recipient-specific framing。

仍然必须保持 internal-only：

- raw source crops、local paths、debug labels、untreated screenshots；
- Alibaba case-study material，除非之后明确批准 attribution 和 metric controls；
- 任何 legal、rights、platform、policy、model-safety、ad-performance、ROI、
  CPA、CTR、ROAS 或 release-readiness conclusion；
- 任何把命名公开公司写成 VULCA 客户、合作方、背书方、授权来源或 audit target
  的说法。

## 主线已确认口径

这些点反映当前主线内部 proof 和用户 review 之后的默认口径：

1. **默认读者：** 第一版先打 brand、ecommerce 和 AI ad workflow owner。
   AI creative platform 仍然是次级读者，不作为唯一 framing。
2. **命名案例：** 公司名字可以出现，但只能写成 public example。第一版客户
   PDF 可以出现名字，前提是视觉已经 source-safe 处理，并且文字明确不是客户、
   合作方、背书方、授权来源或发现对象。
3. **邮件姿态：** 第一封先请求对 sample pack 的实际反馈；如果对方确认这个
   workflow 是真实 bottleneck，再进入 bounded pilot discussion。
4. **Lane 权重：** Lane C 最适合做客户叙事里的 before/after 主例子；Lane A
   和 Lane B 作为 supporting proof，证明同一套 source-backed 方法可以覆盖
   product claim、generated asset 和 workflow handoff。
5. **字段语言：** 正式客户 PDF 正文保持简洁，只放客户理解必需的字段。完整
   source matrix、crop 逻辑、raw proof notes 和 treatment ledger 留在内部主线。

仍然必须在生成新的客户正式 PDF 文件前询问用户。当前 internal PDF 是 master
review source；客户版如果发现问题，先回到 master 规则、资产和页面组件修正，
再从修正后的基础重新生成，不单独 patch 客户版。

## 正式客户 PDF 生产 Gate

在制作任何客户可见 PDF、deck 或邮件附件前，必须过这个 gate：

1. **先问用户是否明确批准生成：** 普通的“继续”不能自动理解成允许生成新的
   customer PDF。
2. **确认收件人 framing：** brand/ecommerce owner、AI ad workflow owner、
   AI creative platform，还是某个具体公司的定制收件人。
3. **确认案例处理方式：** 命名 public example 可以出现，但必须配 public
   example 口径和 source-safe visual；否则使用 neutral redrawn workflow
   examples，把 source notes 放成辅助信息。
4. **默认故事顺序：** Lane C before/after workflow 先讲，Lane A product-truth
   proof 第二，Lane B AI-publishability proof 第三，最后是 safety boundary
   和 feedback CTA。除非用户另行批准，否则按这个顺序。
5. **移除内部材料：** raw crops、untreated screenshots、debug overlays、local
   paths、crop boxes、source-log filenames、full source matrix、internal
   reserves、Alibaba case-study material 都不能进入默认客户版。
6. **限制 claim：** 不写 legal、rights、platform、policy、model-safety、
   release-readiness、performance、ROI、CPA、CTR、ROAS、customer relationship、
   endorsement、authorization 或 audit-target claim。
7. **跑视觉 gate：** 把 PDF 渲染成图片检查 layout、text fit、source-safe
   visuals、boundary copy，以及是否还残留 raw internal labels。
8. **跑 preflight scanner：** 对客户可见 PDF、markdown、HTML 或 text export
   执行 `python3 scripts/customer_pdf_preflight.py <artifact>`。
9. **保持 lineage：** 如果 review 发现 master-level 问题，先修正 internal
   master source，再重新生成客户版，不只 patch 客户文件。

## 中文文案规则

- 语气要像 founder/operator 的认真说明，不要像 marketing landing page。
- 少用形容词，多用工作流、字段、证据、负责人、下一步。
- 可以说 evidence-assisted、human-reviewed、source-backed。
- 不要说自动审批、合规认证、平台保证、法律结论。
- 可以说 public example，不要说客户、合作、背书、授权或负面审计。
- CTA 只要求 feedback、review 或 bounded pilot discussion。
- 第一封不要索取 private assets。
- 任何文案都不能标成 final、approved、可直接发送。
