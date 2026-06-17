# Vulca Product Strategy Research Brief

Status: draft-public-blocked

## Research Question

What should Vulca's main product become next if it is positioned as an agent-native visual production control layer rather than a one-shot image generator or template deck tool?

## Source Table

| Source Id | URL Or Local Path | Source Type | Allowed Use | Do Not Use |
| --- | --- | --- | --- | --- |
| src_vulca_readme | README.md | local product README | Product framing, current workflow stages, MCP/tool capability summary, non-model positioning, provider and layer-editing facts. | Do not copy showcase images, logos, code examples, long prose, provider ids into audience-facing claims, or imply every roadmap item is polished. |
| src_vulca_roadmap | docs/product/roadmap.md | local product roadmap | Current/next/later capability status, non-goals, PPT status boundaries, marketplace and remote MCP direction. | Do not claim future roadmap items are shipped or public-ready. |
| src_vulca_commercial_case | docs/product/ppt-run2-data-skill-quality/commercial_case.md | local product case brief | PPT wedge rationale, audience, decision, editable-output requirement, release constraints, and visual-quality bar. | Do not claim the existing PPT work is a finished public demo. |
| src_vulca_generation_protocol | docs/product/ppt-run2-data-skill-quality/generation_protocol.md | local generation and review protocol | Source-boundary rules, editable object requirements, layout checks, isolation requirements, and gate language for generated decks. | Do not expose internal review vocabulary in audience-facing slides. |
| src_vulca_run2_93_eval | docs/product/ppt-run2-data-skill-quality/results/run2_93_visual_quality_evaluation.md | local visual-quality evaluation | Cautionary evidence that text-object binding improved but visual polish, legibility, and surface realism still need repair before public use. | Do not use as proof that current PPT outputs are public-ready. |
| src_vulca_mcp_server | src/vulca/mcp_server.py | local MCP server source | Concrete MCP surface: discovery, prompt composition, image generation, evaluation, layer editing, inpaint, archive, and session tools. | Do not claim a web-research-to-usecase pack tool exists in the MCP server. |

## Derived Observations

| Observation Id | Source Ids | Observation | Deck Use |
| --- | --- | --- | --- |
| obs_01 | src_vulca_readme, src_vulca_roadmap | Vulca is explicitly framed as an agent-native visual control layer that turns fuzzy intent into controlled creative production through artifacts, provider-routed generation, editing, and evaluation. | Supports the deck thesis and position slide. |
| obs_02 | src_vulca_readme | Vulca says it does not try to beat image models at raw generation; it sits around them to clarify intent, choose and constrain providers, preserve non-target pixels, and record fit against a brief. | Supports contrast between prompt-only generation and workflow control. |
| obs_03 | src_vulca_readme, src_vulca_mcp_server | The repo exposes a workflow from discovery and brief parsing through prompt composition, generation, visual inspection, evaluation, layer splitting, targeted edit, compositing/export, and archive. | Supports the product loop slide. |
| obs_04 | src_vulca_roadmap, src_vulca_mcp_server | Current capabilities include visual discovery, visual brainstorm/spec/plan, image generation/viewing, evaluation, inpainting, layers, redraw, compositing, paste-back, and Tool Protocol analysis. | Supports the capability map without presenting all items as a finished app. |
| obs_05 | src_vulca_readme, src_vulca_roadmap | Vulca lists non-goals around hosting foundation models, competing with one-click models on raw quality, and building a general-purpose design app before artifact contracts stabilize. | Supports category focus and scope discipline. |
| obs_06 | src_vulca_commercial_case | The PPT wedge is framed as a code-generated presentation system that applies curated design knowledge while keeping evidence, assets, and release gates inspectable. | Supports editable presentation generation as the first wedge. |
| obs_07 | src_vulca_generation_protocol, src_vulca_commercial_case | Generated presentation work must keep core text editable, avoid copied source visuals, avoid invented metrics, and pass structural, layout, render, provenance, and human review gates before public use. | Supports source-boundary and QA language. |
| obs_08 | src_vulca_run2_93_eval, src_vulca_roadmap | Existing PPT output work has internal progress, but public use remains gated by visual polish, legibility, surface realism, render inspection, and human approval. | Supports softening any claim about current PPT quality. |
| obs_09 | src_vulca_mcp_server, src_vulca_roadmap | The MCP server does not expose a productized web-research-to-usecase deck-pack tool; related PPT case-pack and data/skill-quality work appears as planned or package-building work. | Supports the honest "next bet" slide. |
| obs_10 | src_vulca_readme, src_vulca_mcp_server | Cultural evaluation, provider routing, semantic layers, masks, paste-back, and archive/session records are separate capabilities that can compound when tied into one product loop. | Supports the moat slide. |
| obs_11 | src_vulca_readme | Visual-discovery and visual-brainstorm skills are text/artifact-first and allow mock sketch records by default, with real provider sketch generation requiring explicit opt-in. | Supports a workflow-first product story rather than an automatic image-output story. |
| obs_12 | src_vulca_roadmap | Later work includes a lightweight Studio review UI for direction cards, sketch grids, layers, and evaluation reports. | Supports a future product surface, not a current claim. |

## Allowed Claims

| Claim Id | Source Ids | Claim | Confidence |
| --- | --- | --- | --- |
| claim_01 | src_vulca_readme, src_vulca_roadmap | Vulca already has a clear control-layer framing around agent-led visual production. | high |
| claim_02 | src_vulca_readme, src_vulca_roadmap | Vulca's product scope is around workflow control, not hosting a foundation model or competing on raw one-click generation. | high |
| claim_03 | src_vulca_readme, src_vulca_mcp_server | Vulca's current surface spans discovery, prompt composition, generation, visual inspection, evaluation, layer editing, compositing/export, and archive/session operations. | high |
| claim_04 | src_vulca_commercial_case, src_vulca_generation_protocol | Editable presentation generation is a credible wedge only if core text remains editable and source, asset, layout, and review boundaries are enforced. | high |
| claim_05 | src_vulca_run2_93_eval, src_vulca_generation_protocol, src_vulca_roadmap | Current PPT outputs should not be described as public-ready; they need further render, polish, and human review gates. | high |
| claim_06 | src_vulca_mcp_server, src_vulca_roadmap | A web-research-to-usecase deck-pack workflow should be positioned as a next product bet, not as an already productized Vulca MCP tool. | high |
| claim_07 | src_vulca_readme, src_vulca_mcp_server | Vulca can be described as provider-agnostic at the workflow level because it routes across multiple image backends and includes local/mock paths. | medium |
| claim_08 | src_vulca_readme, src_vulca_mcp_server | Semantic layer editing, targeted inpainting, paste-back, evaluation, and archive records give Vulca a control loop that a one-shot prompt flow does not provide. | high |
| claim_09 | src_vulca_commercial_case, internal_strategy_thesis | The strongest near-term commercial wedge is usecase-first editable presentation generation because it makes the control layer visible in a business artifact. | medium |
| claim_10 | internal_strategy_thesis | Vulca's next product should package source boundaries, claim spine, visual plan, generation, evaluation, and handoff as one agent-facing workflow. | medium |
| claim_11 | src_vulca_roadmap, src_vulca_mcp_server, internal_strategy_thesis | Workflow memory, provider routing, cultural evaluation, and layer-level editing can become a moat when they compound across repeated visual-production jobs. | medium |
| claim_12 | internal_strategy_thesis | The product category should be described as visual production control, not image generation or template deck creation. | medium |

## Forbidden Or Unproven Claims

| Claim | Reason |
| --- | --- |
| Vulca already ships a public-ready research-to-deck MCP product. | The MCP server exposes visual workflow tools, but no productized web-research-to-usecase deck-pack tool is present. |
| Current PPT outputs are public-ready or suitable as public proof. | Local evaluation and roadmap sources keep current PPT work gated on polish, render inspection, and human approval. |
| Vulca outperforms hosted image models on raw image generation quality. | The README and roadmap position Vulca around control, not raw model competition. |
| Vulca hosts its own foundation image or video model. | The roadmap lists hosting a foundation model as a non-goal. |
| The presentation wedge is fully validated commercially. | The commercial case defines an intended wedge and demo candidate, not market validation. |
| Existing evaluation scores prove production quality. | Evaluation sources are internal quality signals and cannot be used as public proof without the required gates. |
| Vulca is a general-purpose design app today. | The roadmap says building a general-purpose design app before artifact contracts stabilize is a non-goal. |
| Web research is already safe to automate without source boundaries. | The generation protocol requires derived observations, source limits, and review gates for external source usage. |

## Open Questions

- Which first user segment should anchor the product surface: product strategists, creative operations teams, AI platform teams, or design partners?
- Should the first public surface be an agent skill pack, a remote MCP workflow, a Studio review UI, or a narrow editable deck generator?
- What minimal source-boundary contract is needed before web research can become a productized Vulca tool?
- Which evaluation signals should be product-visible, and which should remain implementation-only?
- What proof is enough to promote the PPT wedge from internal evidence to public demo?
