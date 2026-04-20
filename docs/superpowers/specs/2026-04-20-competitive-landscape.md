# Vulca Competitive Landscape & Architectural Context

**Date:** 2026-04-20 (end of day)
**Status:** Research artifact — feeds into the `/visual-brainstorm` meta-skill design and subsequent top-layer skills
**Purpose:** Give future brainstorming sessions a dense, citable context so we never rebuild this map

This is not a plan. It is the **context input** for the plan we will write next session. Every future Vulca meta-skill brainstorm should `@`-reference this file.

---

## TL;DR (read this if you only have 60 seconds)

1. **Vulca target quadrant** = full meta-skill coverage × cultural/fine-art specialization. **This quadrant is currently empty.** Figma's Skills framework (shipped 2026-04) is the closest architectural analog but scoped to UI/UX.
2. **Timeline pressure: 3–6 month window.** Figma Skills could extend to generative/fine-art; Adobe Firefly AI Assistant (2026-04-15) already owns creator distribution. Speed matters.
3. **Our defensible moats**: (a) cultural evaluation backed by EMNLP 2025 Findings + VULCA-Bench + 13 traditions — **no commercial competitor scores cultural quality**; (b) born-agent-native delivery (MCP skills), not a GUI with agents bolted on.
4. **Four architectural takeaways** to port into Vulca:
   - Frontmatter description routes skill activation; **never compress workflow body into description** (superpowers + windsurf convention).
   - Reviewable intent as first-class artifacts — **proposal → design → tasks** chain (OpenSpec).
   - Layered autonomy — human approves design, autonomous subagents execute with 2-reviewer quality gate (superpowers).
   - Skill activation must be **scoped / on-demand, not always-on** (Cursor + Windsurf both retrofitted this after pain).
5. **One counter-philosophy to hold in mind**: pi-mono ships only 4 tools (read/write/edit/bash). Vulca has 21. Worth a Tool Count Reduction Audit before building more.

---

## Section 1 — Four reference ecosystems

### 1.1 Superpowers (obra/superpowers, by Jesse Vincent)

**Scale & traction:** 93k GitHub stars; **~2 000 stars/day in March 2026**. Fastest-growing OSS project in the Claude Code ecosystem.

**Storage model:**
- `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description` only)
- Loadable from repo, `~/.claude/skills/`, or `~/.agents/skills/` (deterministic precedence)
- Cross-harness compatible: works in Claude Code, Codex CLI, Cursor, OpenCode — **one skill file, four hosts**

**Dispatch discipline:**
- Frontmatter `description` is **used exclusively for routing** — the agent matches user intent to description, then loads the full body
- Explicit anti-pattern: description must NOT summarize the procedure. Agents will pattern-match partial summary and skip the body. Superpowers repo has checklist + automated skill audits enforcing this

**Autonomy / execution model:**
- Human approves the *design* during brainstorming
- Fresh subagent dispatched per plan task
- Two independent reviewers run after each subagent: (1) spec-compliance (did subagent build what spec said?), (2) code-quality (is the build itself good?)
- We are using exactly this pattern today (`/decompose` + README refresh were built this way)

**Takeaway:** **this is our base platform.** Vulca's meta-skills are domain-specialized extensions, not replacements.

### 1.2 OpenSpec (Fission-AI/OpenSpec)

**Positioning:** Spec-driven development framework for AI coding assistants. "Agree on what to build before any code is written."

**Artifact chain (each is its own markdown file in the repo):**
- `proposal.md` — the brief, the intent
- `design.md` — the resolved shape
- `tasks.md` — executable steps

**State machine (strict):**
- `proposal → apply → archive`
- Proposals can't skip to apply without review; applied changes auto-archive

**Delta markers (brownfield-friendly):**
- `ADDED` / `MODIFIED` / `REMOVED` annotations on each change
- Critical for iterative work where existing code/design evolves rather than starts from zero

**RFC 2119 built-in:**
- `MUST` / `SHALL` / `SHOULD` / `MAY` keywords in specs, standard meaning
- Requirement strength is machine-detectable — agents can surface "you said MUST but didn't implement it"

**2026 workflow commands** (via `/opsx:*`):
- `/opsx:propose "idea"` — create proposal
- `/opsx:continue` — advance a proposal through the state machine
- `/opsx:ff` — fast-forward ("accept and apply")
- `/opsx:verify` — check spec vs code alignment
- `/opsx:sync` / `/opsx:bulk-archive` / `/opsx:onboard`

**Takeaway:** **Vulca's `/visual-spec` skill should produce OpenSpec-format artifacts** (or at minimum align the artifact schema). Reusing this schema buys interoperability — our visual specs will be reviewable by generic OpenSpec tooling without Vulca-specific knowledge.

### 1.3 pi-mono / pi-agent (badlogic/pi-mono, by Mario Zechner)

**Not** Physical Intelligence (pi.inc). This is Mario Zechner's (libGDX creator) minimalist terminal coding harness.

**Philosophy — radical minimalism:**
- **Only 4 core tools**: `read`, `write`, `edit`, `bash`
- Extensions via TypeScript SDK — Extensions / Skills / Prompt Templates / Themes
- Ships as "pi packages" via npm or git

**Four run modes:**
- Interactive (TUI)
- Print/JSON (batch)
- RPC (process integration)
- SDK (embed in your own app — this is what OpenClaw uses)

**Endorsements:**
- **Shopify CEO Tobi Lütke: "the most interesting agent harness"**
- Powers OpenClaw (Shopify's coding agent)

**Implied counter-lesson for Vulca:**
- Vulca ships 21 MCP tools. pi-mono argues 4 is enough for 80% of work.
- **Before we build more meta-skills, question whether leaf tool count is pulling weight.** Some of Vulca's 21 tools could collapse (e.g. `layers_edit` + `layers_list` + `layers_transform` + `layers_composite` might be one capability with flags). This is part of the Tool Readiness + Reduction Audit.

### 1.4 Claude Code official plugin ecosystem (April 2026 snapshot)

**Scale:**
- 72+ official plugins across 24 categories
- 150+ community skills by March 2026
- Discovery is now the bottleneck, not creation

**Key roles:**
- **`skill-creator`** is the meta-meta-skill — it creates other skills. This is analogous to how we used `superpowers:brainstorming` + `superpowers:writing-plans` today to create `/decompose`
- **Plugin vs skill distinction:** plugin = bundle of (skills + MCP servers + commands). Vulca's `vulca-org/vulca-plugin` is already this shape
- **LiteLLM AI Gateway** acts as enterprise-governed registry — organizations can whitelist which plugins are allowed

**Implication for Vulca:**
- Publishing to the official Anthropic marketplace adds discovery. `vulca-plugin` is already installable via `claude plugin install` but not (as of 2026-04-20) listed in the official directory. **Post-merge follow-up**: submit vulca-plugin to the Anthropic directory once `/visual-brainstorm` ships, so Vulca rides the directory-discovery wave.

---

## Section 2 — Competitive landscape (visual design + creative AI)

### 2.1 Direct architectural threats (two, both shipped April 2026)

#### Figma AI + Skills framework (2026-04)
- Figma opened the canvas to MCP agents and shipped a **markdown-based "Skills" framework**
- Explicit framing: "vagueness masquerading as brevity" — exactly the problem Vulca wants to solve
- Currently UI/UX-scoped. **If they extend to fine-art/generative, the Vulca moat shrinks fast.**
- **Opportunity flip side:** if the SKILL.md format is compatible, Vulca skills could theoretically be callable from Figma's canvas agents. Worth investigating format alignment.

#### Adobe Firefly AI Assistant (2026-04-15)
- Multi-step workflow orchestrator across Creative Cloud
- Adobe owns: distribution (Creative Cloud installed base), license-safe training data, creator relationships
- If Firefly adds critique + iteration scaffolding, the generic creator segment stops being reachable by a CLI plugin

### 2.2 Adjacent but not directly competing

| Product | Layer | Domain | Relation to Vulca |
|---|---|---|---|
| Midjourney v7 (Vary Region, Remix) | Leaf tool | Generative art | Complement — we don't compete on base-model quality |
| Ideogram / Recraft / Leonardo AI | Leaf tool | Generative art | Complement — same reason |
| **Galileo AI → Google Stitch** | Leaf-to-mid | UI/UX | Acquired by Google mid-2025; not in Vulca's domain |
| Uizard, Relume | Mid meta | UI/UX | Out of Vulca's domain |
| **v0 / Bolt / Lovable** | Mid meta | Code | Adjacent domain; "vibe design" is prompt-first |
| **Canva Magic Studio 2.0** | Mid meta | Consumer design | Downstream of Vulca — if Vulca succeeds, Canva might bundle a Vulca-style eval |
| Notion AI, ChatGPT Canvas | Assistant | Generic text | Complementary — Vulca could be called from inside these |

### 2.3 The positioning map (2 axes)

```
                      Domain-specialized
                             │
    Midjourney ●             │              ● FIGMA SKILLS (threat)
    Ideogram ●               │              ● VULCA TARGET ← empty
                             │                quadrant
  Leaf tools ────────────────┼──────────────── Full meta-skill
                             │
              ● Aider         │              ● Superpowers
              ● Cursor        │              ● OpenSpec
                             │
                      Generic / cross-domain
```

Vulca's current position is bottom-right (leaf tools, specialized). Target is top-right. **Figma Skills is the ONLY other occupant of the top-right quadrant** and it's UI-scoped, not fine-art.

---

## Section 3 — Three user-journey patterns (for the "vague user with fuzzy sketch" scenario)

| Pattern | Representatives | Stickiness | Vulca choice |
|---|---|---|---|
| **Prompt-and-pray** — 1-shot text → 4 variants → Vary Region | Midjourney, Firefly, Canva Magic Design | High dopamine, frustrating for specific intent | ❌ not this |
| **Vibe-spec** — intent → AI infers spec → generate | v0, Bolt, Lovable, Canva AI 2.0 | Addictive for novices, frustrating for experts (spec invisible) | ⚠️ middle option |
| **Skill-scaffolded agent** — markdown skills → ask → spike → spec → execute | **Figma Skills, Superpowers, Vulca target** | Most durable (users build personal skill libraries); highest onboarding cost | ✅ **Vulca's bet** |

---

## Section 4 — Moats and risks

### 4.1 Defensible moats (Vulca's edge)

1. **Cultural / tradition-aware evaluation is academically validated and commercially uncontested.**
   - Research backbone: EMNLP 2025 Findings (`aclanthology.org/2025.findings-emnlp.103/`, Yu / Ruiz-Dolz / Yi), VULCA-Bench (arXiv 2601.07986)
   - Corroborating external research: CHI 2024 "Partiality and Misconception" (dl.acm.org/10.1145/3613904.3642877), arXiv 2504.04865 (East Asian women bias taxonomy), arXiv 2503.19075 ("Thick Evaluations"), DIS 2025 Chinese traditional subcultures
   - **No commercial product ships scored cultural evaluation.** Vulca's L1-L5 + 13 traditions is uniquely defensible.
   - Publishable — each new evaluation mode can seed another paper

2. **Born-agent-native delivery**
   - Figma/Canva/Adobe are all GUI-first products retrofitting agents on top
   - Vulca grew inside MCP — zero context switch for Claude Code users
   - As MCP/Claude Code install base grows, our distribution grows with it (vs. having to fight for canvas adoption)

### 4.2 Positioning risks (things that could close the window)

1. **Figma Skills extending from UI to fine-art/generative.**
   - Same architectural pattern; lower adoption friction (already on designers' desks)
   - Mitigation: ship `/visual-brainstorm` + `/visual-plan` inside the 3-6 month window; double down on cultural angle where Figma won't follow

2. **Adobe Firefly owning the creator funnel.**
   - Even if Vulca is technically better, installed base beats better
   - Mitigation: partner-friendly positioning — Vulca MCP tools could be callable from Firefly or Figma if their agent platforms support external MCP. Keep format alignment open.

---

## Section 5 — Architectural takeaways (the four to steal)

### 5.1 Frontmatter routes, body executes
**Source:** superpowers + windsurf converge on this
- Skill's YAML `description` field is for routing only (agent matches user intent to description)
- Body (the actual decision tree / procedure) must NOT be mirrored in description
- Otherwise agents pattern-match the summary and skip the body — defeats the point of the skill

**Vulca application:** every meta-skill's `description` ≤ 150 chars, covers routing intent only. Body lives in the SKILL.md and is ONLY read after Claude Code decides to load the skill.

### 5.2 Reviewable intent as first-class artifacts
**Source:** OpenSpec's proposal/design/tasks chain
- Before any pixel work, the intent is a reviewable markdown artifact
- Brownfield scenarios use ADDED/MODIFIED/REMOVED delta markers
- RFC 2119 requirement strength (MUST/SHOULD/MAY) makes specs machine-checkable

**Vulca application:**
- `/visual-brainstorm` → outputs `proposal.md` (intent, loose)
- `/visual-spec` → outputs `design.md` (resolved constraints, RFC 2119 keywords for evaluate-able criteria)
- `/visual-plan` → outputs `tasks.md` (ordered tool invocations)
- All three land in `docs/visual-specs/YYYY-MM-DD-<project>/*.md`
- Match OpenSpec format where possible so specs are portable

### 5.3 Autonomy in tiers, reviewed at gates
**Source:** superpowers subagent-driven-development
- Human approves DESIGN (top gate)
- Subagents execute PLAN steps autonomously
- Two independent reviewers per subagent output (spec compliance, code quality)

**Vulca application:**
- Top gate: user confirms `/visual-spec` output (design.md)
- Autonomous execution: subagents run each `tasks.md` step
- Two reviewers per visual step: (1) does the output match the spec's RFC 2119 criteria? (2) does the output pass L1-L5 evaluation against the declared tradition?

### 5.4 Scoped skill activation, not always-on
**Source:** Cursor + Windsurf retrofit pain
- Always-on skill context causes agent to pattern-match partial content
- Scoped activation (on-demand, manual, or model-requested) prevents this

**Vulca application:** every SKILL.md declares `activation: on-demand`. Skill list is `Skill`-tool-discoverable but not preloaded into every conversation.

---

## Section 6 — One anti-pattern to avoid

**Always-on context bloat.** Cursor and Windsurf both shipped this way initially and had to change. The symptom: agent has "read" the skill in its context but pattern-matches on partial summary instead of executing the decision tree. The fix: scoped activation.

Vulca's `/decompose` skill already does this right (it's loaded only when user says `/decompose`, not preloaded). Keep this discipline for every new skill.

---

## Section 7 — Timeline implications for Vulca

| Window | Event | Vulca must do |
|---|---|---|
| **Now — 2026-06-10** | EmoArt Challenge submission deadline | Batch run 24 artworks through Vulca pipeline; use as showcase + paper material |
| **Now — ~2026-07** | Figma Skills still UI-scoped (likely window) | Ship `/visual-brainstorm` + `/visual-plan` + at least one composition skill (`/redraw` or `/improve`) |
| **~2026-07 onward** | Figma Skills may extend to generative; Firefly Assistant matures | Vulca cultural moat should be visible in README + paper + dev.to — positioning must be clear |
| **Always-on** | Claude Code plugin marketplace discovery is the bottleneck | Submit `vulca-plugin` to Anthropic directory after `/visual-brainstorm` ships |

---

## Section 8 — Concrete action items (feed into next session's plan)

1. **Next skill: `/visual-brainstorm`** — zero tool dependencies, pure dialogue. Use superpowers:brainstorming as spec-writing reference. Ship in 1 session (brainstorm → spec → plan → subagent-execute).
2. **Parallel: Tool Readiness + Reduction Audit.** Leverage 24-artwork showcase corpus. For each of the 11 Skeleton-tier tools, run PASS/FAIL matrix. Also audit: can any 2–3 tools collapse into one (pi-mono-inspired reduction)? Output `docs/tools-readiness-matrix.md`.
3. **OpenSpec schema alignment.** Before writing `/visual-spec` brainstorm, read OpenSpec's proposal.md / design.md / tasks.md schemas and decide what to reuse. If there's a way to make Vulca specs portable (OpenSpec can read/validate them), do that.
4. **README competitive positioning block.** After `/visual-brainstorm` ships, add a small "How Vulca compares" section in the main README referencing superpowers / OpenSpec / pi-mono / Figma Skills. Honest positioning > silence.
5. **Submit vulca-plugin to Anthropic plugin directory.** After `/visual-brainstorm` lands. Discovery wave.
6. **Gemini billing unblock** — user-side action, tracked in `memory/project_gemini_api_billing.md`. Required for EmoArt VLM benchmark by 2026-06-10.

---

## References

### Superpowers
- [obra/superpowers](https://github.com/obra/superpowers)
- [Anthropic — Superpowers plugin](https://claude.com/plugins/superpowers)
- [Jesse Vincent blog](https://blog.fsck.com/2025/10/09/superpowers/)
- [Builder.io writeup](https://www.builder.io/blog/claude-code-superpowers-plugin)

### OpenSpec
- [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec/)
- [openspec.dev](https://openspec.dev/)
- [Redreamality deep dive](https://redreamality.com/garden/notes/openspec-guide/)

### pi-mono
- [badlogic/pi-mono](https://github.com/badlogic/pi-mono)
- [Mario Zechner post](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)
- [Tobi Lütke endorsement (YT short)](https://www.youtube.com/shorts/fRtODeCfL_E)

### Claude Code plugin ecosystem
- [Create and distribute plugin marketplace (Anthropic docs)](https://code.claude.com/docs/en/plugin-marketplaces)
- [LiteLLM plugin marketplace tutorial](https://docs.litellm.ai/docs/tutorials/claude_code_plugin_marketplace)
- [Best Claude Code skills & plugins 2026 (dev.to)](https://dev.to/raxxostudios/best-claude-code-skills-plugins-2026-guide-4ak4)

### Figma + Adobe (direct threats)
- [Figma — Agents, meet the canvas](https://www.figma.com/blog/the-figma-canvas-is-now-open-to-agents/)
- [Figma — Designer framework for better AI prompts](https://www.figma.com/blog/designer-framework-for-better-ai-prompts/)
- [Adobe Firefly AI Assistant launch](https://blog.adobe.com/en/publish/2026/04/15/introducing-firefly-ai-assistant-new-way-create-with-our-creative-agent)
- [Canva AI 2.0 newsroom](https://www.canva.com/newsroom/news/canva-create-2026-ai/)

### Academic / cultural evaluation moat
- [EMNLP 2025 Findings — VULCA Framework (Yu / Ruiz-Dolz / Yi)](https://aclanthology.org/2025.findings-emnlp.103/)
- [VULCA-Bench arXiv](https://arxiv.org/abs/2601.07986)
- [CHI 2024 Partiality & Misconception](https://dl.acm.org/doi/10.1145/3613904.3642877)
- [arXiv 2504.04865 East Asian bias taxonomy](https://arxiv.org/html/2504.04865v1)
- [arXiv 2503.19075 Thick Evaluations](https://arxiv.org/html/2503.19075v1)
- [DIS 2025 Chinese traditional subcultures](https://dl.acm.org/doi/10.1145/3715336.3735808)
