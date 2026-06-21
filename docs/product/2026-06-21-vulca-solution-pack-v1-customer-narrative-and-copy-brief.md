# VULCA Solution Pack v1 Customer Narrative And Copy Brief

**Date:** 2026-06-21
**Status:** customer narrative draft for review only
**Branch scope:** customer-facing story, short email draft, PDF opening copy,
CTA language, and terminology

This document is not an outreach execution packet. It must not be used to
contact anyone until the main review thread and the user approve the final
customer PDF and copy.

Related internal research:

- `docs/product/2026-06-21-vulca-reference-company-deep-research-brief.md`

Mainline proof inputs integrated after thread
`019ee5a2-15dc-72b2-a900-6e8cb1ab6cfa` completed:

- commit `7aab0468`: clarified three-lane purpose map
- commit `519e26a6`: Creatify workflow deep proof
- commit `c9b292fc`: Seedream / BytePlus deep proof
- commit `ef9cd2b3`: PROYA source-safe distilled card
- commit `e3454235`: PROYA deep proof artifacts

## Source Context Reviewed

Reviewed in this branch:

- `assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/README.md`
- `assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/manifest.json`
- `docs/product/workspace-current-state-audit.md`
- `docs/agent-native-workflow.md`
- Lane A PROYA production brief from commit `6030f437`
- Lane B Seedream / BytePlus production brief from commit `cb2b7eea`
- Lane C Creatify production brief from commit `49ebf1e4`
- Mainline internal preview README from commit `7aab0468`
- Mainline PROYA, Seedream / BytePlus, and Creatify source-safe card logic from
  commits `ef9cd2b3`, `c9b292fc`, and `519e26a6`

Not present in this worktree at review time:

- `docs/product/2026-06-20-vulca-solution-pack-v1-pdf-storyboard.md`
- `docs/product/2026-06-20-vulca-solution-pack-v1-master-pdf-production-plan.md`
- checked-in `docs/product/lane-work/*production-brief.md` files

Those missing files should be treated as main-thread inputs only if the main
review branch imports them later.

## Core Customer Narrative

### One-Sentence Version

VULCA helps teams turn AI-assisted and high-frequency visual assets into
source-backed evidence packs before those assets move into public launch,
campaign, marketplace, or client-review workflows.

### Short Version

Modern visual teams are shipping more generated, edited, and cross-channel
assets than their release process can easily explain. A product display, a
generated image, a URL-to-video ad, or a campaign page can move quickly across
retail, marketplace, social, and internal review surfaces. The missing layer is
not another image generator. It is a compact record of source context, visible
claim or output context, review questions, owner routing, and the human decision
gate before reuse.

VULCA Solution Pack v1 is a sample of that release-evidence layer. It uses
public examples and source-safe visual treatment to show how a team could move
from raw multimodal material to reviewable evidence cards and a bounded pilot
discussion.

### Customer Should Understand Immediately

- VULCA exists because public-facing visual assets now move faster than their
  source trail, review notes, and release ownership.
- The deliverable is an evidence pack, not a legal opinion, platform clearance,
  or automated approval system.
- The first customer PDF should demonstrate a serious workflow: source intake,
  visual annotation, evidence card, owner route, and a bounded pilot.
- Named companies are public examples only. They are not VULCA customers,
  partners, endorsers, authorization sources, or negative findings.

### Recommended Default Buyer

For the first formal customer PDF, lead with **brand / ecommerce / AI ad
workflow owners**. They have the clearest pain because their product visuals,
generated ad candidates, marketplace assets, and campaign handoffs can all move
quickly before source context and release ownership catch up.

Secondary readers can still be AI creative platforms, creative-ops teams, and
founder/operators, but the first version should not read as a generic creative
tool pitch.

### Plain Problem Statement

Teams can now generate, edit, and reuse product visuals much faster than they
can explain them. Before an asset moves into a campaign, marketplace listing,
client review, or public page, someone still needs to answer: what did this
asset come from, what product or claim does it represent, what generation or
edit context shaped it, what is unresolved, and who owns the release decision?

That is the gap VULCA should own.

### Three-Lane Narrative Map

| Lane | Unit of review | Core question | Evidence-card output |
| --- | --- | --- | --- |
| A / Product-truth | Existing commercial material and product claim | Does the campaign, product representation, source, channel reuse, and owner route connect? | Product-truth evidence card |
| B / AI publishability | One generated asset or generated asset set | Can this AI output be published or reused with source, prompt/reference, model context, label posture, and owner route attached? | AI publishability evidence card |
| C / AI ad workflow | Product-to-ad workflow and campaign handoff | How does product URL/listing/brief become candidate creative, review state, export state, and campaign owner handoff? | AI ad workflow handoff card |

Short rule: Lane A is claim/material level, Lane B is generated-asset level,
and Lane C is workflow/handoff level. Lane C can contain many Lane B-style
generated assets, but its main proof is the workflow and handoff path.

## Narrative Variants By Customer Type

### Variant A: Consumer / Beauty / Ecommerce Company

**Use when talking to:** beauty brands, product teams, ecommerce teams,
marketplace operators, retail/channel owners.

**Customer problem:**

Product visuals and campaign claims travel across retail displays, product
pages, event materials, paid social, marketplace listings, and internal decks.
Teams often need to answer simple but expensive questions: what source supports
this visual claim, what product representation is being reused, and who owns
the decision before it goes public?

**VULCA story:**

VULCA creates a source-backed product-truth evidence card. The card does not
accuse a public example of being wrong. It records what is visible, where the
source trail lives, what representation is being reused, and which role should
review unresolved questions.

**Customer-facing copy:**

For product and campaign teams, VULCA turns public-facing visual material into a
reviewable source trail. A campaign display, product image, event cue, or
marketplace page becomes a compact evidence card: visible claim, source
context, product representation, channel role, and release owner.

**Internal note:** PROYA can be named only as a public market example. Do not
say the campaign has an issue, do not state VULCA has verified claim accuracy,
and do not use raw source crops externally without treatment.

### Variant B: AI Creative / Generated Media Platform

**Use when talking to:** AI image/video platforms, creative tooling companies,
brand studios using generative workflows.

**Customer problem:**

Generated assets are often treated as output files, but publishability depends
on the prompt/reference context, model or workflow context, output state,
label/disclosure posture, and the human owner who decides how the asset may be
reused.

**VULCA story:**

VULCA does not rank or certify models. It creates a review packet around
generated media: input/source, model or workflow context, output status, label
posture, unresolved questions, and release owner.

**Customer-facing copy:**

For AI creative teams, VULCA makes generated assets inspectable before reuse. A
generated image or video candidate is paired with its prompt/reference context,
source pages, output state, label posture, and owner route so teams can review
what may move forward and what still needs human decision.

**Internal note:** Seedream / BytePlus should stay version-neutral unless the
main review branch explicitly chooses a version. Kling remains internal reserve
unless the customer PDF intentionally covers video-reference workflows.

### Variant C: AI Ad Workflow / Creative Automation Company

**Use when talking to:** URL-to-video platforms, AI ad builders, creative
automation tools, growth and creative-ops teams.

**Customer problem:**

Product-link-to-ad workflows can turn a listing, URL, image, or brief into
multiple campaign candidates. The operational problem is not only generation;
it is reviewability: what source input shaped the ad, which candidate was
produced, what was reviewed, what was exported, and who owns the campaign handoff?

**VULCA story:**

VULCA records the workflow evidence around generated campaign assets. It can
show source input, workflow step, creative-structure review, export/reuse state,
and accountable handoff owner without turning vendor marketing claims into
VULCA claims.

**Customer-facing copy:**

For AI ad workflow teams, VULCA turns generated campaign candidates into
handoff packets. Product URL, generated candidate, review context, export state,
and campaign owner are captured in one evidence card before assets move into a
launch or client-review workflow.

**Internal note:** Creatify can be a public workflow example. Alibaba case-study
material remains internal reference by default unless the main review branch
approves exact citation and attribution.

## Concrete Before / After Example

Use this as the customer-readable example spine for the first PDF and founder
note.

### Before VULCA

A team or workflow starts from a product URL, listing, image, or brief and
quickly produces multiple campaign candidates. Those candidates may be edited,
exported, sent to a client, moved into a seller portal, or prepared for paid
social. The output exists, but the review context is scattered:

- source input may be separate from the generated candidate;
- hook, body, CTA, product fit, claim fit, and brand fit may not be recorded as
  review fields;
- draft/edit/export/channel state may be unclear;
- the campaign owner may not know which questions remain unresolved;
- third-party case-study or vendor screenshots may be unsafe to reuse directly.

### After VULCA

VULCA turns the same workflow into a release-evidence packet:

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

The output is not an ad-performance prediction, legal review, platform
clearance, or automatic approval. It is a compact packet a human owner can
inspect before assets move into launch, client review, marketplace, or campaign
handoff.

### Customer Copy

For ecommerce and AI ad workflow teams, VULCA turns generated campaign
candidates into reviewable handoff packets. Product URL, source input,
generated candidate, creative anatomy, export state, missing fields, and
campaign owner are captured before assets move into launch or client-review
workflows.

## Technical Base Translated For Customers

Do not lead with the internal toolchain. Translate the VULCA base into customer
outcomes:

- **Source read:** public or provided source material is preserved as review
  context, not treated as decorative evidence.
- **Visual field read:** visible claim, product representation, generated
  output, label posture, and workflow state become named fields.
- **Source-safe treatment:** raw screenshots, untreated crops, local paths, and
  third-party case-study material stay internal unless redrawn, masked,
  cropped, or cleared.
- **Evidence card:** the customer sees a compact review object, not a folder of
  screenshots.
- **Owner route:** unresolved fields are routed to the human role that can make
  a release decision.

## Short Email Draft

**Status:** review draft only. Do not use as an outbound message until the main
thread approves the final customer PDF and copy.

**Subject options:**

- A source-backed review packet for AI-assisted visual assets
- Thoughtful sample: release evidence for generated and product visuals
- Can I share a short VULCA visual evidence pack?

**Draft:**

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

### Revised Draft After Mainline Proof

**Status:** review draft only. Not ready to send.

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

## PDF Opening Copy

### Page 1 Opening

**Title:** VULCA Solution Pack v1

**Subtitle:** Source-backed evidence packets for AI-assisted visual release.

AI-assisted visuals are becoming part of everyday launch, ecommerce, campaign,
and client-review workflows. The bottleneck is no longer only creating an image
or video candidate. The bottleneck is explaining what it came from, what it
represents, what still needs review, and who owns the release decision.

VULCA Solution Pack v1 shows a compact release-evidence workflow using public
examples. Each example is treated as a market pattern, not as a customer,
endorsement, authorization source, or negative finding.

### Page 2 Opening

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

### Recommended Formal PDF Sequence

1. **Why now:** AI-assisted visual production is scaling across ecommerce,
   campaigns, generated media, and ad workflows.
2. **Problem:** release context is not scaling with it. Source, claim,
   generated-output state, product fidelity, label posture, and owner route are
   often scattered.
3. **VULCA packet:** VULCA turns the asset or workflow into a source-backed
   evidence packet for human review.
4. **Three lanes:** product-truth evidence, AI publishability context, and AI
   ad workflow handoff.
5. **Concrete example:** product URL / listing -> generated campaign candidate
   -> review fields -> export state -> missing-field list -> campaign owner.
6. **Pilot ask:** public examples or sanitized assets only, one review lane,
   small asset count, short readout.

## Customer-Facing Compressed Copy Pack

**Status:** review draft only. This is the compressed copy source for a future
formal customer PDF and outreach note. It still requires final review, visual
export safety checks, and recipient-specific framing before external use.

### PDF Opening Draft

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

### What The Pack Shows

- **Product-truth evidence:** visible commercial material becomes a
  source-backed evidence card.
- **AI publishability context:** generated assets are paired with source,
  prompt/reference, model/workflow context, output state, label posture, and
  owner route.
- **AI ad workflow handoff:** product URL or listing workflows become campaign
  handoff packets with source input, generated candidate, review anatomy,
  export state, missing fields, and owner route.

### One-Page Before / After Draft

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

### Short Outreach Draft V3

**Status:** review draft only; not for external use until the customer PDF and
recipient framing are approved.

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

### Customer Version Inclusion Rule

Include in the formal customer PDF:

- the `Why now -> Problem -> VULCA packet -> Example -> Pilot` sequence;
- the three-lane map in concise form;
- the before/after example built around product URL / listing to campaign
  handoff;
- source-safe card visuals or redrawn workflow strips;
- a narrow review / feedback / bounded-pilot CTA.

Keep internal:

- funding, ARR, valuation, org-structure research, and competitor critique;
- raw source screenshots, local capture paths, debug overlays, and untreated
  crops;
- Alibaba case-study metrics unless separately approved with attribution and
  metric controls;
- any legal, rights, platform, model-safety, release-readiness, or performance
  conclusion.

## CTA Copy

### Conservative CTA

If this matches a real workflow you see, we would value your feedback on the
sample pack: which fields are useful, which are missing, and where a bounded
pilot would need to fit into an existing review process.

### Pilot Discussion CTA

If the workflow is relevant, the next step could be a bounded pilot discussion:
public examples or sanitized assets only, a small number of visual materials,
one review lane, and a short readout focused on source context, evidence cards,
owner routing, and what should or should not move forward.

### Feedback CTA

The most useful feedback would be practical: whether your team already tracks
source context, prompt/reference records, generated-output state, and release
ownership; and whether these fields would help before assets enter public,
client, marketplace, or campaign workflows.

## Terminology

| Term | Customer-facing definition |
| --- | --- |
| Source-backed evidence pack | A compact packet that links visual assets to source context, review questions, evidence cards, and owner routing before reuse. |
| Public example | A publicly available market example used to explain a workflow pattern. It is not a customer, partner, endorsement, authorization source, or finding. |
| Release owner | The human role responsible for deciding whether unresolved questions are resolved, escalated, blocked, or allowed to move forward. |
| Evidence card | A structured card that records the visible asset context, source context, review question, current state, suggested action, and owner route. |
| Human review gate | The point where a qualified human owner reviews the evidence and decides the next action. VULCA can prepare the packet; the human owner decides. |
| Source-safe visual treatment | Cropping, masking, redrawing, anonymizing, or replacing raw source visuals so customer-facing material avoids local paths, raw screenshots, unclear rights, and misleading source presentation. |

## Safety Copy Bank

Use these lines when customer-facing material needs a boundary statement:

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

## Mainline Deep Proof Status

The main thread has now produced internal deep-proof inputs for all three lanes:

1. **Lane A / PROYA:** public source-backed visual -> visual annotation ->
   field extraction -> evidence-card draft -> owner route -> source-safe visual
   treatment decision.
2. **Lane B / Seedream / BytePlus:** public model/tool source pages -> field
   annotation -> source, input, model, output, label, and owner fields ->
   source-safe publishability card.
3. **Lane C / Creatify:** public product-to-video workflow source ->
   workflow-field annotation -> source input, candidate creative, review
   anatomy, export state, owner route -> source-safe campaign handoff card.

This resolves the earlier "must wait for proof" gap for narrative drafting.
It does not make the customer PDF ready to send. Formal customer export still
requires the master PDF safety gate, source-safe visual treatment, final copy
review, and recipient-specific framing.

Still keep internal-only:

- raw source crops, local paths, debug labels, and untreated screenshots;
- Alibaba case-study material unless later explicitly approved with attribution
  and metric controls;
- any legal, rights, platform, policy, model-safety, ad-performance, ROI, CPA,
  CTR, ROAS, or release-readiness conclusion;
- any claim that a named public company is a VULCA customer, partner, endorser,
  authorization source, or audit target.

## Mainline Review Decisions

These points reflect the current main-thread default after the internal proof
work and user review:

1. **Default reader:** lead with brand, ecommerce, and AI ad workflow owners.
   AI creative platforms remain a secondary reader, not the only framing.
2. **Named examples:** named companies may appear only as public examples.
   The first customer PDF can use names when they are treated with source-safe
   visuals and explicit public-example language.
3. **Email posture:** first contact should ask for practical feedback on the
   sample pack. Bounded pilot discussion can be the next step if the workflow
   maps to their real bottleneck.
4. **Lane weighting:** use Lane C as the clearest before/after workflow example
   for the customer story, with Lane A and Lane B as supporting evidence that
   the same source-backed method works across claims and generated assets.
5. **Field language:** keep the PDF body concise. Put only the fields needed for
   reader comprehension in the formal PDF; keep full source matrix, crop logic,
   raw proof notes, and treatment ledger in the internal master.

Still ask the user before generating a new customer-facing PDF file. The
current internal PDF remains the master review source, and any customer variant
must be regenerated from that corrected basis rather than patched separately.

## Copy Rules

- Prefer operational language over marketing language.
- Say "evidence-assisted" and "human-reviewed" instead of automated approval.
- Say "public example" instead of customer, partner, endorsement, or audit.
- Say "source-backed review packet" instead of compliance report.
- Keep CTAs narrow: feedback, review, or bounded pilot discussion.
- Do not request private assets in the first customer note.
- Do not mark any draft as final, externally approved, or immediately usable.
