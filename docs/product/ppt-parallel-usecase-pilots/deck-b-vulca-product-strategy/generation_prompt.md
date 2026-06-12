# Vulca Product Strategy Generation Prompt

Status: draft-public-blocked

## Prompt

Create a six-slide editable PowerPoint deck for product advisors, design partners, early platform reviewers, and technical investors.

The deck decision is: decide whether Vulca's next main product should be an agent-native visual production control layer, with usecase-first editable presentation generation as the first wedge.

Use this thesis: Vulca should become the agent-native control layer around visual generation: it should help agents structure intent, choose providers, edit pixels, evaluate results, and package inspectable visual artifacts.

Use this six-slide arc:
1. Vulca's next product should be the control layer for visual work done by agents. Proof object: full-bleed product-loop surface from intent to packaged artifact. Basis: src_vulca_readme, src_vulca_roadmap, internal_strategy_thesis.
2. Image models can make outputs; teams still need a controlled workflow for intent, sources, edits, and review. Proof object: prompt-only versus governed workflow comparison. Basis: src_vulca_readme, src_vulca_commercial_case, internal_strategy_thesis.
3. Vulca sits around providers so agents can structure intent, route generation, edit pixels, evaluate fit, and preserve artifacts. Proof object: capability map grouped by agent job. Basis: src_vulca_readme, src_vulca_roadmap, src_vulca_mcp_server.
4. The product loop should start with a usecase and end with an inspectable package, not a loose prompt result. Proof object: usecase-to-package loop diagram. Basis: src_vulca_readme, src_vulca_commercial_case, src_vulca_generation_protocol, internal_strategy_thesis.
5. Editable presentation generation is the clearest wedge because it turns visual control into a business artifact people can inspect. Proof object: editable strategy deck package mockup with source boundary, claim spine, visual plan, and review handoff. Basis: src_vulca_commercial_case, src_vulca_generation_protocol, src_vulca_roadmap, internal_strategy_thesis.
6. Productize research-to-usecase deck packs next, while being clear that web research is not yet a Vulca MCP product surface. Proof object: roadmap decision board showing current base, missing product surface, launch gates, and next bet. Basis: src_vulca_mcp_server, src_vulca_roadmap, src_vulca_generation_protocol, internal_strategy_thesis.

Constraints:
- Keep all core text editable.
- Use one dominant proof object per slide.
- Do not copy source visuals, logos, screenshots, layouts, or long prose.
- Do not invent metrics.
- Do not use internal implementation terms in slide copy.
- Do not put source ids on audience-facing slides.
- Keep the output draft-only until render inspection and human review pass.

## Source Boundary

Use local sources only as paraphrased input for product facts, workflow status, source boundaries, and review gates. The README, roadmap, commercial case, generation protocol, visual-quality evaluation, and MCP server source may inform the deck, but the slides must not copy their prose, screenshots, code, local labels, or implementation details.

The visual-quality evaluation may only support a caution: current PPT work has internal progress but must not be described as public-ready. The MCP server source may support the current visual workflow surface, but it must also prevent overclaiming: web research to usecase pack is not yet a productized Vulca MCP tool.
