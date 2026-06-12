# Vulca Workflow Demo QA Prompt

Status: draft-public-blocked

## Gemini Or Human Review Prompt

Review this six-file Markdown input pack and, if generated later, the six-slide deck as a public-facing product workflow presentation.

Check:
- Does every slide have an audience-facing claim rather than a topic label?
- Does every claim map to source ids or internal_strategy_thesis?
- Does audience-facing copy avoid the ban list from output-templates.md: primitive, Run 2.92, Run 2.93, public blocked, bound proof, trace manifest, renderer id, arm id, debug, QA artifact?
- Does the deck show concrete product/workflow objects: usecase intake, source ledger, planning board, editable slide canvas, review board, and handoff packet?
- Does the deck avoid copied source visuals, logos, screenshots, layouts, long prose, and unsupported metrics such as invented percentages, scores, time savings, cost savings, tool counts, or quality deltas?
- Does the deck clearly separate current Vulca MCP capabilities from agent-side or aspirational deck workflow capabilities?
- Are conceptual workflow-demo surfaces labeled as conceptual, rather than implied to be shipped product UI?
- Does the deck avoid claiming public readiness before render, provenance, QA, and human review pass?
- Does the workflow read as a product experience rather than an implementation record?
- Does slide 5 acknowledge the prior visual-quality blocker as a repair loop rather than a finished result?
- Does slide 6 create a clear decision handoff: proceed, revise, or block?

Use this rubric when naming strongest and weakest slide: claim clarity, source mapping, dominance of one proof object, visible capability boundary, copy-ban compliance, and likely generation risk.

Return:
- verdict: proceed_to_generation, revise_brief, or block;
- strongest slide;
- weakest slide;
- unsupported claim risk;
- visual risk;
- capability-boundary risk;
- next action.
