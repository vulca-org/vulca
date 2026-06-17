# Vulca Product Strategy Deck Brief

Status: draft-public-blocked

## Audience

Product advisors, design partners, early platform reviewers, and technical investors evaluating what Vulca should become next.

## Decision

Decide whether Vulca's next main product should be an agent-native visual production control layer, with usecase-first editable presentation generation as the first wedge.

## Thesis

Vulca should become the agent-native control layer around visual generation: it should help agents structure intent, choose providers, edit pixels, evaluate results, and package inspectable visual artifacts.

## Product Or Workflow Concept

A usecase-first visual workflow system where an agent starts from a real business or creative problem, converts it into a sourced claim spine and visual plan, routes generation or editing through appropriate providers, evaluates the result, and packages an editable artifact for review.

The research-to-deck surface is a next product bet, not a shipped Vulca MCP capability today. Current capability claims should stay grounded in the existing visual workflow, provider routing, editing, evaluation, and artifact packaging surface.

## Six-Slide Arc

| Slide | Role | Audience-Facing Claim | Proof Object | Source Or Basis |
| --- | --- | --- | --- | --- |
| 1 | cover | Vulca's next product should be the control layer for visual work done by agents. | Full-bleed product-loop surface with one clear handoff path from intent to packaged artifact. | src_vulca_readme, src_vulca_roadmap, internal_strategy_thesis |
| 2 | problem | Image models can make outputs; teams still need a controlled workflow for intent, sources, edits, and review. | Split-stage diagram contrasting prompt-only output with a governed visual workflow. | src_vulca_readme, src_vulca_commercial_case, internal_strategy_thesis |
| 3 | position | Vulca sits around providers so agents can structure intent, route generation, edit pixels, evaluate fit, and preserve artifacts. | Capability map organized by agent job: discover, specify, route, edit, evaluate, package. | src_vulca_readme, src_vulca_roadmap, src_vulca_mcp_server |
| 4 | loop | The product loop should start with a usecase and end with an inspectable package, not a loose prompt result. | Circular workflow from usecase to brief, claim spine, visual plan, editable generation, evaluation, and handoff. | src_vulca_readme, src_vulca_commercial_case, src_vulca_generation_protocol, internal_strategy_thesis |
| 5 | wedge | Editable presentation generation is the clearest wedge because it turns visual control into a business artifact people can inspect. | Before/after board: generic prompt result versus editable strategy deck package. | src_vulca_commercial_case, src_vulca_generation_protocol, src_vulca_roadmap, internal_strategy_thesis |
| 6 | next bet | Productize research-to-usecase deck packs next, while being clear that web research is not yet a Vulca MCP product surface. | Roadmap decision board with current capabilities, missing product surface, and launch gates. | src_vulca_mcp_server, src_vulca_roadmap, src_vulca_generation_protocol, internal_strategy_thesis |

## Failure Modes

- The deck reads as an internal roadmap instead of a product decision story.
- The deck implies current PPT outputs are public-ready.
- The deck hides the missing research-to-usecase product surface instead of naming it as the next bet.
- The deck drifts into one-shot image generation, template deck automation, or generic AI workflow claims.
- The deck exposes local run labels, implementation ids, low-level rendering vocabulary, or review artifact wording in slide copy.
- The deck uses screenshots, copied source layouts, logos, or invented metrics as proof.
- The deck becomes a dense engineering report with no visible product climax or decision handoff.
- The deck forgets to show editability, review, and source boundaries as the wedge's concrete control mechanisms.

## Copy Ban Applied

Confirmed audience-facing copy avoids the banned internal terms from `output-templates.md` and avoids local run labels, implementation ids, and review-only vocabulary.
