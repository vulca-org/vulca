# Parallel Deck Briefs

Status: prompt-design-ready-public-blocked

These briefs are starting points for parallel subagents. They are not finished
deck outputs and should not be treated as public-ready copy.

## Shared Public Copy Ban List

Do not put these terms in audience-facing slide titles or body copy:

- `primitive`
- `Run 2.92`
- `Run 2.93`
- `public blocked`
- `bound proof`
- `trace manifest`
- `renderer id`
- `arm id`
- `native deck` unless the audience already understands editable PPT as the
  product category

Use internal terms only in QA notes, speaker notes, trace manifests, or
implementation documentation.

## Deck A: Brand-Safe AI Creative Production

**Audience:** AI product builders, brand operations leaders, creative workflow
owners, and design-led founders.

**Decision:** Should a brand team use a governed AI creative workflow instead
of uncontrolled one-shot generation?

**Thesis:** The next AI creative product category is not "generate an image".
It is a governed workflow that turns approved brand inputs into reviewable
variants across channels.

**Primary source starting points:**

- Coca-Cola Create Real Magic official announcement:
  `https://www.coca-colacompany.com/media-center/coca-cola-invites-digital-artists-to-create-real-magic-using-new-ai-platform`
- Adobe Firefly Creative Production:
  `https://business.adobe.com/products/firefly-business/firefly-creative-production.html`
- Adobe Firefly Creative Production workflows:
  `https://business.adobe.com/products/firefly-business/firefly-creative-production/production-workflows.html`
- Adobe Creative Production overview:
  `https://helpx.adobe.com/firefly/web/work-with-enterprise-features/creative-production/creative-production-overview.html`
- Adobe workflow run/test/publish docs:
  `https://helpx.adobe.com/firefly/web/work-with-enterprise-features/creative-production/run-workflows.html`

**Product concept:** A brand-safe campaign workflow builder that turns approved
briefs, approved assets, channel requirements, and review rules into editable
creative variants and a presentation-ready review packet.

**Six-slide arc:**

1. **Pressure:** Campaign production has shifted from single hero assets to
   variant systems.
2. **Market proof:** Public AI brand cases show that brand archives, approved
   inputs, and governed workflows matter.
3. **Product promise:** A campaign brief becomes a workflow, not a prompt.
4. **Control layer:** Brand rules, asset boundaries, review states, and
   downstream delivery are first-class objects.
5. **Payoff:** One approved campaign system can produce localized and
   channel-ready variants.
6. **Decision gate:** Production is ready only when workflow, brand, and review
   gates pass.

**Proof objects:**

- campaign workflow map;
- approved input stack;
- variant matrix with channel/localization rows;
- review gate board;
- before/after from one-shot generation to governed production.

**Visual direction:** Editorial product strategy deck, not SaaS dashboard. Use
one large workflow surface, sparse claims, and credible production objects.

**Risk:** Brand-source references can cause accidental imitation. The deck must
abstract product/workflow rules and avoid copying Coca-Cola or Adobe visuals.

## Deck B: Vulca Product Strategy

**Audience:** product advisors, design partners, early platform reviewers, and
technical investors.

**Decision:** What should Vulca's main product become next?

**Thesis:** Vulca should become the agent-native visual production control
layer. It should help agents structure visual intent, choose providers, edit
pixels, evaluate results, and package inspectable artifacts.

**Source starting points:**

- `README.md`
- `docs/product/roadmap.md`
- `docs/product/ppt-run2-data-skill-quality/commercial_case.md`
- `docs/product/ppt-run2-data-skill-quality/generation_protocol.md`
- `docs/product/ppt-run2-data-skill-quality/results/run2_93_visual_quality_evaluation.md`

**Product concept:** A usecase-first visual workflow system that sits around
image models and presentation generation. The user starts with a real workflow
problem, not a prompt-only generation request.

**Six-slide arc:**

1. **Problem:** The market has enough generation; it lacks controlled visual
   workflow.
2. **Position:** Vulca is the control layer around visual generation.
3. **Loop:** discover -> brief -> spec -> plan -> generate/edit -> evaluate ->
   package.
4. **Wedge:** usecase-first editable presentation generation.
5. **Moat:** workflow memory, cultural evaluation, provider routing, and layer
   editing compound together.
6. **Next bet:** build the research-to-deck pipeline as the first public
   product surface.

**Proof objects:**

- product loop diagram;
- before/after of prompt-only versus governed workflow;
- capability map with current and missing pieces;
- usecase-first roadmap.

**Visual direction:** Product strategy keynote. No internal renderer jargon.
Show Vulca as a system of controlled handoffs, not a pile of tools.

**Risk:** This deck can become an internal roadmap. Keep it framed as a product
decision deck with a clear external wedge.

## Deck C: Vulca Workflow Demo

**Audience:** users who need to understand how Vulca works without reading
source code or internal trace manifests.

**Decision:** Can Vulca turn a real researched usecase into an editable,
reviewable deck with visible product value?

**Thesis:** The value is the pipeline from real usecase to governed visual
artifact. The deck should show the workflow as a product experience.

**Source starting points:**

- Deck A's research brief after it exists;
- Deck B's product strategy brief after it exists;
- `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- `docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md`
- `docs/product/ppt-run2-data-skill-quality/generation_protocol.md`

**Product concept:** A transparent workflow that converts research into a deck:
source boundaries, claim spine, visual plan, editable generation, evaluation,
and handoff.

**Six-slide arc:**

1. **Usecase:** Start with a real business case, not a generic prompt.
2. **Research:** Convert sources into allowed observations and blocked claims.
3. **Planning:** Turn observations into claim spine, visual brief, and prompt.
4. **Generation:** Create editable native slide structures and supporting
   assets.
5. **Evaluation:** Check specificity, editability, visual quality, and
   provenance.
6. **Handoff:** Deliver deck, QA ledger, and next repair decision.

**Proof objects:**

- workflow pipeline;
- source boundary ledger;
- claim spine board;
- generated deck preview placeholder;
- QA handoff checklist.

**Visual direction:** Workflow product demo. The workflow should be visible as
a clean product surface, not an engineering trace dump.

**Risk:** This deck is most likely to regress into internal trace language. It
must hide trace details behind readable product concepts.
