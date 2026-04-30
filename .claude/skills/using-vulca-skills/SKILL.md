---
name: using-vulca-skills
description: Use when starting any conversation about Vulca visual workflows - establishes auto-invoke discipline for the discovery -> brainstorm -> spec -> plan -> evaluate chain. Preload via SessionStart hook so the agent matches user intent without requiring slash commands.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If there is even a 1% chance a Vulca visual-skill applies to the user's intent, you MUST invoke it before responding. Do NOT wait for a `/visual-*` slash command — match on intent.

This is the rule that stops the agent from slipping into "free-form" image-generation detours that bypass Vulca's structured decision artifacts.
</EXTREMELY-IMPORTANT>

## Instruction priority

1. **User's explicit instructions** (CLAUDE.md, AGENTS.md, direct requests) — highest.
2. **Vulca skills** (this meta-skill + the visual-* skills) — override default "just generate an image" behavior where they conflict.
3. **Default system prompt** — lowest.

If the user says "skip the brainstorm, just generate" — that's an explicit instruction; honor it. Otherwise the discovery-to-plan chain is the default.

## Intent routing — pick the right skill

| If user's intent is … | Invoke |
|---|---|
| explore fuzzy visual direction, taste, culture tendency, "抽卡", "方向探索", "审美分析", "文化倾向分析"; no discovery artifacts yet | `visual-discovery` |
| define / scope / brainstorm a 2D visual project (poster / illustration / packaging / brand / editorial / photo brief / hero art); no proposal.md yet | `visual-brainstorm` |
| derive technical decisions (provider, prompt, L1-L5 weights, thresholds, cost) from an existing `proposal.md` with `status: ready` | `visual-spec` |
| evaluate an existing image against a tradition/brief, ask for L1-L5 scoring, cultural critique, "评价这张图", "文化评分"; image already exists | `evaluate` |
| review the derived plan.md AND execute the real generate+evaluate loop for an existing `design.md` with `status: resolved` | `visual-plan` |
| decompose a given image into semantic layers | `decompose` |

**Chain rule**: never skip ahead. Pre-conditions gate each step — `/visual-brainstorm` follows selected discovery direction when discovery was needed; `/visual-spec` refuses without a ready proposal.md; `/visual-plan` refuses without a resolved design.md. If the user's intent lands on a stage whose precondition is missing, say so and invoke the earliest unmet stage.

**Tie-breaker**: if multiple skills could apply, pick the earliest unmet stage in the chain.

## Finalize vocabulary (normalized across Vulca visual skills)

- **Brainstorm → Spec handoff**: `finalize` / `done` / `ready` / `lock it` / `approve` (5 words; case-insensitive substring match)
- **Spec → Plan handoff**: same 5-word set
- **Plan review → execution gate**: `accept all` (exact phrase, case-insensitive — stricter because it triggers real cost-incurring pixel calls)

If the user uses any of the above tokens in the brainstorm/spec review, treat as finalize trigger.

## Red flags — STOP if you're thinking this

- "The user didn't type `/visual-brainstorm`, so I should just answer directly." → NO. Match on intent; invoke anyway.
- "This is just a quick question about a poster." → NO. Questions about visual projects ARE the brainstorm's entry point.
- "Let me just call `generate_image` first and see what happens." → NO. `generate_image` outside `/visual-plan` Phase 3 is a S1 violation.
- "The user wants a fast draft; skip the brainstorm." → Only if user gave an explicit instruction to skip. Otherwise NO.

## Announcement

When you invoke a Vulca skill, print one line first:

```
Using /visual-<skill> to <one-line purpose>.
```

Then follow the skill's body exactly.

## What this skill does NOT do

- Does NOT execute any visual skill's logic itself. It only routes.
- Does NOT override CLAUDE.md, AGENTS.md, or user instructions.
- Does NOT apply to non-visual Vulca work (e.g. layer editing via `layers_*` MCP tools, which are tool-level not skill-level).

## References

- `.claude/skills/visual-discovery/SKILL.md`
- `.claude/skills/visual-brainstorm/SKILL.md`
- `.claude/skills/visual-spec/SKILL.md`
- `.claude/skills/visual-plan/SKILL.md`
- `.claude/skills/evaluate/SKILL.md`
- Sibling pattern: `superpowers:using-superpowers` (Superpowers' meta-skill this one is modeled on).
