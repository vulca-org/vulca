# Run 2.1 Readiness

Status: ready_to_rerun_public_blocked.

Run 2.1 is not a new stage. It thickens the same Run 2 product layers before the next generation pass:

- source and video cards now include executable `extraction_units`;
- `skill_workflow.json` records the declarative stage contract, gates, and human-gated repair triggers;
- `scripts/refresh_ppt_trace_qa.py` can refresh local trace QA outcomes with dry-run, backup, and atomic replacement.

The trace refresh utility is a prerequisite helper, not release evidence. Release evidence requires regenerated arms, refreshed traces for those regenerated arms, native or manual render inspection, and human approval.

## Decision

The case pack is ready to rerun four arms: prompt-only, Run 1.5 skill, Run 2.1 full skill, and bad aesthetic memory. Public status remains public blocked. The current local outputs were refreshed for trace QA inspection, but they are not the final Run 2.1 experiment because the deck arms have not been regenerated from the thickened data and workflow contract.

## Next Required Action

Rerun four arms from the updated case pack, then repeat structural QA, trace refresh, Gemini contact-sheet review, native or manual render inspection, and human approval.
