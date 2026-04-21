# `/visual-brainstorm` Skill — Design Spec

**Date:** 2026-04-21
**Status:** Design locked after brainstorm session (7 clarifying Q's → 3 approaches → 8 design sections, all user-approved) + two parallel review rounds (codex + superpowers-reviewer, both CONDITIONAL APPROVE, all conditions folded in)
**Follow-up:** implementation plan at `docs/superpowers/plans/2026-04-21-visual-brainstorm-skill.md` (next, via `superpowers:writing-plans`)
**Context input:** [`2026-04-20-competitive-landscape.md`](./2026-04-20-competitive-landscape.md)

This is a **design spec for the shipped skill artifact**. The skill file itself (`.claude/skills/visual-brainstorm/SKILL.md`) deliberately contains **zero "future / later / expand" phrasing** (superpowers reviewer condition 1 — deployed artifact is not a roadmap). Any "Y-future" thinking lives only in this spec and related plan docs, never in the skill body.

---

## 1. Purpose, scope, and moat

### 1.1 Purpose

`/visual-brainstorm` is a **meta-skill** that turns fuzzy visual intent (topic description, optional sketch, optional references) into a reviewable `proposal.md` compatible with the OpenSpec artifact chain. It is the top gate in the `brainstorm → spec → plan → execute` pipeline for Vulca visual projects.

### 1.2 Scope (ZS — Z-Sharpened after review)

**In-scope** — 2D illustrative or editorial visual projects where the deliverable is a single 2D image or a series of 2D images:

- `poster` — activity / exhibition / event signage
- `illustration` — standalone illustrative work
- `packaging` — product packaging / bottle / label artwork
- `brand_visual` — brand visual system, marketing illustrations, peripheral series
- `editorial_cover` — book / magazine / report cover
- `photography_brief` — brief for an upcoming shoot
- `hero_visual_for_ui` — hero illustration / splash art for app or web, NOT the UI layout itself

**Out-of-scope (hard reject + redirect)**:

- UI layout / component / interaction design → Figma, Figma Skills
- Video / motion / animation → Runway, Pika, Kling
- 3D / industrial / product / automotive design → Rhino, Alias, Blender, SolidWorks

**Edge-accept rule**: if a request spans the boundary (e.g., "SaaS hero banner with character illustration"), the skill applies the **Single 2D artifact test** — *is the deliverable a single 2D image?* Yes → accept; includes page layout / CTA placement / interaction flow → redirect. Every edge-accept MUST record a `scope-accept rationale: <reason>` line in the proposal's `## Notes` section for audit.

### 1.3 Moat defense

Vulca's defensible advantage (see `2026-04-20-competitive-landscape.md` §4.1) is **cultural evaluation backed by EMNLP 2025 Findings + L1-L5 + 13 traditions** — no commercial competitor scores cultural quality. `/visual-brainstorm` enforces this moat by:

- Offering the 13 built-in traditions (via `list_traditions` MCP tool) plus custom YAML (via `--tradition-yaml <path>`)
- Applying a **Conditional MUST**: any non-null `tradition` value forces an `## Acceptance rubric` section in the produced `proposal.md` with L1-L5 dimensions tagged using RFC 2119 keywords

---

## 2. Architecture

```
USER invokes: /visual-brainstorm [topic] [--sketch <path>] [--ref-dir <dir>] [--tradition-yaml <path>]
       │
       ▼
Skill body loads on-demand (activation: on-demand; scoped per competitive-landscape §5.4)
Allowed tools: view_image + list_traditions + search_traditions + get_tradition_guide + Read (only when --tradition-yaml)
       │
       ├─ draft exists at docs/visual-specs/<slug>/proposal.md with status:draft? ─── YES ──▶ resume from Open questions section
       │                                                                          │
       │                                                                          NO
       ▼                                                                          ▼
§0-a Scope check (keyword scan + single-2D-artifact test)        Fresh 5-node decision tree start
  ├─ out-of-scope keywords → redirect + terminate (no turn cap)
  ├─ fuzzy → first Q asks "visual concept vs layout/interaction"
  └─ edge-accept → proceed, mandatory rationale in ## Notes
       │
       ▼
5-node decision tree:
  A: sketch present? → view_image for grounding
  B: tradition declared? → get_tradition_guide + flag rubric MUST
  C: reference images/links? → short-note, no image analysis
  D: single-image vs series? → gate on including ## Series plan section
  E: needs spike? → record to ## Open questions for /visual-spec
       │
       ▼
6-dimension question loop (turns ≤ 8 hard, ≤ 12 soft on explicit "deep dive")
Dimensions: tradition / audience / physical-form / market / budget-deadline / color-constraint
       │
       ▼
Render proposal.md draft, show to user, ask "finalize?"
       │
       ▼
User says "finalize"/"done"/"ready" → status:draft → status:ready (no auto-advance — B4)
       │
       ▼
OUTPUT artifact: docs/visual-specs/YYYY-MM-DD-<slug>/proposal.md
       │
       ▼
Handoff hint printed: "Ready for /visual-spec. Run it with `/visual-spec <slug>`"
(Does NOT auto-invoke downstream skill — human-in-the-loop gate preserved)
```

**Inputs**:
- Required: `topic` (free-form text)
- Optional: `--sketch <path>` — triggers up to 1 `view_image` call for intent grounding
- Optional: `--ref-dir <path>` — lists files, user confirms which to record in `## References` (no image analysis)
- Optional: `--tradition-yaml <path>` — triggers 1 `Read` call; schema failure degrades to Error #4

**Outputs**:
- Single artifact: `docs/visual-specs/YYYY-MM-DD-<slug>/proposal.md`
- Frontmatter carries `status: draft | ready`; only `ready` is visible to `/visual-spec`

**Isolation boundary**: the skill writes exactly one file (`proposal.md`) and reads at most a few user-supplied paths and MCP metadata tools. No SDK state, no pipeline trigger, no pixel work. Week-1 shippability rests on this.

---

## 3. Frontmatter

Per `.claude/skills/decompose/SKILL.md` convention — only `name` and `description`:

```yaml
---
name: visual-brainstorm
description: Brainstorm a 2D illustrative or editorial visual project (poster, illustration, packaging, brand visual, hero/cover art) into a reviewable proposal.md. Invoke for /visual-brainstorm or when user says '视觉 brainstorm', '视觉需求', '设计 brief'. NOT for product UI/app layout, video, 3D modeling.
---
```

**Rules for `description`** (superpowers §5.1 anti-pattern: description routes, body executes):

- Target ≤ 150 characters (measured by the routing tokenizer)
- Leads with **outcome** ("reviewable proposal.md"), not procedure
- Lists bilingual trigger phrases for natural routing
- **Explicitly names out-of-scope domains** (NOT for product UI, video, 3D) — scope is a routing concern, not a workflow concern
- Does NOT mention decision-tree node count, turn cap, tool list, dimension names, directory paths (these live in body)

**Activation**: on-demand (no always-on preloading). Defends against competitive-landscape §6 context-bloat anti-pattern.

**Allowed tools** — declared in body, not frontmatter (matches `/decompose` convention):

- `view_image` — 1-3 calls when sketch or refs supplied
- `list_traditions` / `search_traditions` / `get_tradition_guide` — tradition dialogue
- `Read` — only when user explicitly supplies `--tradition-yaml <path>`
- **Explicitly banned** (B1): all pixel-level tools (`generate_image`, `create_artwork`, `inpaint_artwork`, all `layers_*`, `evaluate_artwork`)

---

## 4. Skill body structure

Hybrid skeleton (narrative head + structured body + rigor tail), ~140 lines to match `/decompose` weight class.

```
─── Frontmatter ─────────────────────────────── 3 lines
─── NARRATIVE HEAD ────────────────────────── ~35 lines

§0   Purpose & tone (≤ 12 lines)
     - Skill role: "design-brief midwife"
     - Scope declaration: 2D illustrative/editorial; NOT UI layout/video/3D
     - Zero-pixel promise + tool whitelist inline
     - Tone: collaborative coach, not interrogator

§0-a Scope check (≤ 8 lines)
     - Keyword hard-exclude scan (UI layout / video / 3D / automotive)
     - Hard-exclude hit → print redirect + terminate (no turn cap)
     - Single 2D artifact test as second gate
     - Fuzzy boundary ("landing page 设计") → first Q disambiguates
     - Edge-accept requires ## Notes rationale audit trail

§1   Opening turn template (≤ 12 lines)
     - Parse args → detect sketch / tradition hint
     - If no sketch → fixed solicited-sketch prompt (A2)
     - If existing draft for same slug → resume from Open questions (A6)

§2   Slug generation (≤ 6 lines)
     - Agent proposes kebab-case slug from topic + tradition hint
     - User may override
     - Slug collision handling delegated to Error #1 / #2

─── STRUCTURED MIDDLE ─────────────────────── ~70 lines

§3   Decision tree (5 nodes, ≤ 20 lines table):
     A: sketch present?        → view_image for grounding
     B: tradition declared?    → get_tradition_guide; flag rubric MUST
     C: reference images?      → text note, no image analysis
     D: single vs series?      → gate ## Series plan section presence
     E: needs spike direction? → record to ## Open questions

§4   6-dimension question bank (≤ 25 lines table):
     tradition / audience / physical-form / market / budget-deadline / color-constraint
     Each row: prompt template · skip-allowed · inferred default

§5   proposal.md schema (≤ 25 lines):
     - Frontmatter field list (7 fields)
     - Domain enum priority table (7 values with disambiguation rules)
     - ## Template block (the canonical section layout agent copies from)
     - RFC 2119 usage rules (scope to ## Acceptance rubric + ## Open questions)

─── RIGOR TAIL ────────────────────────────── ~32 lines

§6   Turn cap + finalize (≤ 8 lines)
     - 8 hard / 12 soft with explicit "deep dive"
     - Cap reached → force-show draft + prompt "finalize or deep dive" (B4)
     - Finalize trigger: user explicit "done" / "finalize" / "ready"
     - status:draft → status:ready only on trigger

§7   Skill bans (B1–B7, ≤ 14 lines table)
     - One-line per ban; rule · consequence · remedy columns

§8   Error matrix (≤ 10 lines table)
     - 8 errors from §6 of this spec

§9   Handoff (≤ 4 lines)
     - Print: "Ready for /visual-spec. Run it with `/visual-spec <slug>`"
     - Skill does NOT auto-invoke downstream

─── References ────────────────────────────── ~4 lines
     - EMNLP 2025 Findings / VULCA-Bench URLs (L1-L5 academic anchor)
     - competitive-landscape.md path
```

**Budget**: ~140 lines (narrative 25% / structured 50% / rigor 25%). `/decompose` is 141 lines, so precedent holds.

---

## 5. `proposal.md` schema

### 5.1 Frontmatter (7 fields, all MUST)

```yaml
---
slug: 2026-04-21-spring-festival-poster-series
status: draft                          # enum: draft | ready. Only "ready" visible to /visual-spec
domain: poster                         # enum, 7 values (see 5.2)
tradition: song_gongbi                 # enum from list_traditions, OR YAML `null`. NEVER "N/A", "none", "" (B7)
generated_by: visual-brainstorm@0.1.0  # version anchor for forward compat
created: 2026-04-21                    # ISO date
updated: 2026-04-21                    # ISO date
---
```

**Deliberately removed fields** (from initial draft, per review):

- `turns_used` — removed: no downstream consumer; turn cap is a body-internal runtime guard, not spec contract
- `series: bool` — removed: redundant with the existence of `## Series plan` section; single source of truth avoids drift (codex Q1 finding)

### 5.2 `domain` enum (7 values) with disambiguation rules

| `domain` value | Deliverable signature | Disambiguation |
|---|---|---|
| `poster` | Activity / exhibition / event signage | Art-exhibition posters → poster (activity-signage semantic wins over editorial) |
| `illustration` | Standalone illustrative artwork | No host artifact (not a cover, not a package) |
| `packaging` | Product packaging / bottle / label | Die-line / material constraints present |
| `brand_visual` | Brand visual system / marketing series / peripherals | System-level, not single artifact |
| `editorial_cover` | Book / magazine / report cover | Book-with-illustrated-cover → editorial_cover (host-artifact wins over illustration) |
| `photography_brief` | Brief for an upcoming shoot | No pixel deliverable yet; output is instructions |
| `hero_visual_for_ui` | Hero illustration for app / web | NOT the UI layout. Artifact is the single hero image |

### 5.3 Markdown section layout

First line of every produced proposal.md:

```markdown
# <human-readable title>

> Partial OpenSpec alignment: status enum + RFC 2119 keywords. Does not use ADDED/MODIFIED/REMOVED delta markers. Full alignment deferred until /visual-spec consumption validates need.
```

Then sections in the following order (lives in skill body §5 as a copyable `## Template` block, which is the one canonical place to edit layout — reason: a layout change 6 months from now should be a one-line skill body edit, not a schema migration):

1. `## Intent` — 2-5 sentences of user intent; no compositional detail (thin proposal promise)
2. `## Audience` — target viewer / consumer description
3. `## Physical form` — print size, digital viewport, die-line, etc.
4. `## Market` — 国内 / 海外 / 多语言 requirements
5. `## Budget & deadline` — time budget, deliverables count, hard deadlines
6. `## Color constraints` — explicit palette requirements or the literal text `none specified`
7. `## References` — external URLs / local paths / the literal `none`
8. `## Series plan` — *conditional: only if series project.* Count, variation axis, rhythm, deliverables list
9. `## Acceptance rubric` — *conditional: only if `frontmatter.tradition` is non-null (B3).* L1-L2 default MUST, L3-L4 default SHOULD, L5 default MAY. Tradition-guide MAY override strength (e.g., religious iconography L3 taboo → MUST)
10. `## Questions resolved` — agent-logged Q/A pairs from brainstorm (traceability)
11. `## Open questions` — unresolved points punted to `/visual-spec`; non-empty when turn cap triggered force-show
12. `## Notes` — free-form; edge-accept cases MUST log `scope-accept rationale: <reason>` here

**Empty-section rule**: when a non-conditional section has no content, write the literal `none` (not `TBD`, `N/A`, or blank). This consistency enables downstream parsers.

### 5.4 RFC 2119 usage

- **In `## Acceptance rubric`**: every bullet tagged MUST / SHOULD / MAY per the L1-L5 defaults or the tradition-guide override
- **In `## Open questions`**: MAY use MUST to mark "downstream must resolve this"
- **Elsewhere**: prose, no RFC 2119 keywords

---

## 6. Skill bans (B1–B7)

Runtime rules the agent running the skill MUST follow. Style matches `/decompose` §"Skill bans" (E1-E5).

| # | Rule | Consequence if violated | Remedy |
|---|---|---|---|
| **B1** | **No pixel-level tool calls.** Forbidden: `generate_image`, `create_artwork`, `inpaint_artwork`, any `layers_*`, `evaluate_artwork`. | Breaks zero-pixel promise; Week-1 shippability lost; contradicts agent-native moat §4.1 | Tool whitelist: `view_image` + `list_traditions` + `search_traditions` + `get_tradition_guide` + `Read` (only for `--tradition-yaml`). Anything else = bug |
| **B2** | **No hidden brief.** Even if user says "just go" / "skip confirmation", the skill MUST show full draft proposal.md content and wait for explicit confirm/modify/override before finalize | Vibe-spec anti-pattern; downstream `/visual-spec` burns tokens on misaligned intent | User can shorten the `## Intent` section to 2 sentences, but frontmatter / `## Acceptance rubric` / `## Open questions` MUST display in full |
| **B3** | **Tradition declared ⇒ rubric MUST appear.** Non-null `frontmatter.tradition` forces the `## Acceptance rubric` section (L1-L5 template). Tradition-guide MAY override default strength (religious/taboo → MUST) | Vulca moat artifact missing; downstream cannot resolve L1-L5 | If user insists "no rubric", change `tradition` to YAML `null` first — a consistent declaration, not a bypass |
| **B4** | **No auto-advance status.** `status: draft → ready` happens ONLY on explicit user trigger: "done" / "finalize" / "ready". Agent reasoning "I asked enough" is NOT a trigger | Unverified draft consumed downstream; resume semantics broken | Agent presents draft and asks; at turn cap, present + prompt — still never auto-flip |
| **B5** | **Scope-check first; no out-of-scope brainstorm.** Single 2D artifact test + keyword hard-exclude scan. Hard-exclude hit → redirect + terminate (no turn cap increment; no dialogue flow) | Vulca props up a domain it cannot win; Figma/Runway comparison reveals weakness | Fuzzy cases → first-Q disambiguate. Edge-accept cases MUST log `scope-accept rationale` in `## Notes` |
| **B6** | **No parallel invocation on same slug.** Two `/visual-brainstorm` sessions MUST NOT write the same `<slug>/proposal.md` concurrently | File race; state corruption; resume breaks | Detect via `updated` timestamp vs now; reject second call; user renames slug to branch |
| **B7** | **Tradition field type hard.** `frontmatter.tradition` MUST be either an enum id from `list_traditions` / valid `--tradition-yaml` id, OR YAML literal `null`. Forbidden strings: `"N/A"`, `"none"`, `"null"`, `""`, `"unknown"` | `if tradition:` truthy-check fails → rubric section silently omitted → Vulca moat artifact missing | Skill MUST self-assert before writing: "tradition value is enum-id or YAML null?" |

### 6.1 Why bans differ from `/decompose`'s E1-E5

`/decompose` E-series primarily guards **pipeline data integrity** (face-part naming, person-overlap leak fix).
`/visual-brainstorm` B-series primarily guards **scope drift, vibe-spec, state integrity**.

The two skills' bans serve different failure modes. No attempt to homogenize.

---

## 7. Error matrix

Follows `/decompose` §"Error handling" shape. 8 rows — dialogue skill has a smaller error surface than pipeline skill.

| # | Error signal | Response |
|---|---|---|
| **1** | Slug collision, target `<slug>/proposal.md` exists with `status: ready` | Print: `proposal already finalized at <path>. To branch: use <slug>-v2 or pick new slug. To re-open: manually change status:ready→draft.` Terminate. Do NOT overwrite |
| **2** | Slug collision, target exists with `status: draft` | **Resume path (A6)**: read `## Open questions` as dialogue-restart seed; continue Q loop; turn cap accumulates, does NOT reset |
| **3** | Unknown tradition: user names tradition but `list_traditions` + `search_traditions` find no match AND no `--tradition-yaml` | 3-way prompt: (a) ask for `--tradition-yaml <path>`; (b) set `tradition: null` + record freeform in `## Notes`; (c) if user insists on undefined id, treat as `null` + warn `rubric section omitted because tradition could not be validated`. Never fabricate enum ids |
| **4** | `--tradition-yaml` unreadable (FileNotFoundError / YAML parse / schema mismatch) | Print: `tradition-yaml at <path> invalid: <err>. Falling through to Error #3 flow.` Do NOT auto-retry |
| **5** | `--sketch` unreadable or `view_image` fails | Print: `sketch at <path> unreadable: <err>. Proceeding text-only (A2 fallback).` Degrade to text-only; do NOT count as error; do NOT charge turn cap |
| **6** | User requests pixel action mid-dialogue ("now generate", "画给我看", "run create_artwork") | Print: `I don't generate images; I finalize the brief. After finalize, run /visual-spec <slug>, then pixel-generation tools downstream.` Do NOT call any B1 tool. Do NOT count as cap turn |
| **7** | Turn cap hit (8 hard, or 12 soft after deep dive) without user finalize | Force-show current draft in full + print: `turn budget exhausted. Review draft and reply 'finalize' to lock status:ready, or 'deep dive' to extend +4 (hard 12).` Do NOT auto-finalize (B4) |
| **8** | Scope hard-reject, user pushes back ("but I really want to use you for this UI") | Explain once: `scoped to 2D illustrative/editorial; pixel/layout for product UI is Figma Skills territory. If you want a single hero illustration for UI, rephrase as hero_visual_for_ui.` **Second pushback → terminate, no further explanation** |

**Do-not-auto-retry rules**: Errors #3, #4, #8. These require user clarification (#3), user fix (#4), or respect a hard boundary (#8).

**Do-not-overwrite rules**: Error #1 (ready proposals are immutable through this skill); Error #6 (never silently invoke banned tools).

---

## 8. Testing and validation

Markdown + agent-behavior skills have no unit-test runner. Validation is via **scripted real cases** run inside Claude Code sessions that verify the agent (under the skill) follows the decision tree, bans, and schema.

### 8.1 Ship-gate — RED-GREEN on ≥ 3 real cases

Superpowers reviewer's mandatory condition for shipping. If any of these needs a large custom branch, scope homogeneity is false → return to design, do NOT ship.

| Case | Topic | Sketch | Tradition | Series | Expected domain | Expected rubric |
|---|---|---|---|---|---|---|
| T1 | "春节海报系列 12 张，宋画工笔风" | no | `song_gongbi` | yes | `poster` | MUST (tradition non-null) |
| T2 | "自出版诗集封面，现代简约" | yes (thumbnail) | `null` | no | `editorial_cover` | absent (tradition null) |
| T3 | "独立品牌视觉系统（logo-adjacent 插画 5 张），日式浮世绘" | no | `ukiyoe` | yes | `brand_visual` | MUST |

**Per-case checklist**:

- [ ] Turns ≤ 8 (or ≤ 12 with explicit "deep dive")
- [ ] Frontmatter has all 6 required fields
- [ ] `tradition` is enum-id or YAML `null` (strict B7; no `"N/A"` / `"none"` strings)
- [ ] Conditional sections correct (`## Acceptance rubric` iff tradition non-null; `## Series plan` iff series)
- [ ] No B1-banned tool called (tool-log audit)
- [ ] `generated_by: visual-brainstorm@<version>` present
- [ ] Partial-alignment `>` blockquote at top of file
- [ ] No Y-future phrasing anywhere in skill body OR generated proposals (grep: `future|later|expand|扩展到`)

### 8.2 Negative tests

| Case | Input | Expected behavior |
|---|---|---|
| N1 | "做个 SaaS 产品的登录页 UI" | §0-a hard-reject; print redirect; no turn cap; terminate |
| N2 | "SaaS hero banner 带角色插画" | Edge-accept; `## Notes` contains `scope-accept rationale: single 2D artifact` |
| N3 | Mid-dialogue user says "直接调 generate_image 给我看" | B1 decline + polite explanation; turn does NOT charge cap |
| N4 | User declares tradition `"xxx"` not in enum / no YAML | Error #3 flow; `tradition: null`; freeform description in `## Notes` |
| N5 | Turn count 8, user has NOT said "finalize" | Force-show draft + prompt "finalize or deep dive"; B4 holds (no auto-flip) |
| N6 | User second-time pushes back on out-of-scope redirect | Terminate silently after second pushback; no further explanation |

### 8.3 Deliberately not tested

- Specific tone / phrasing of agent replies (subjective; not a gate)
- Skill body line-count / char-count hard limits (guideline only)
- `view_image` call count upper bound (bans already restrict tool whitelist; common sense suffices)

---

## 9. Distribution

### 9.1 Source of truth and sync

- **Primary**: `/Users/yhryzy/dev/vulca/.claude/skills/visual-brainstorm/SKILL.md`
- **Mirror (byte-identical)**: `<vulca-plugin repo>/skills/visual-brainstorm/SKILL.md` — same pipe used for `/decompose`

### 9.2 Version bumps

- Vulca main: **v0.17.2 → v0.17.3** (skill is a pure markdown addition; patch bump. If open backlog items — e.g., sam_split fixes in `project_vulca_0_17_2_backlog` — ship in the same release, re-evaluate as minor)
- vulca-plugin: **v0.16.1 → v0.16.2** (feature addition)
- No new pinned dependencies (zero-pixel skill)

### 9.3 README updates

- Main repo `README.md`: add `/visual-brainstorm` to the Skills section, mirroring `/decompose`'s presentation
- Plugin `README.md`: same
- No About / topic updates needed (kept from last refresh)

### 9.4 Changelog draft

```markdown
## v0.17.3 — 2026-04-2X

### Added
- `/visual-brainstorm` skill — guide fuzzy visual intent into reviewable
  proposal.md (OpenSpec-aligned partial). Zero-pixel, Discovery-metadata-only.
  Scoped to 2D illustrative/editorial domains (7 enum values). Conditional
  L1-L5 rubric for tradition-bearing projects.
  See `.claude/skills/visual-brainstorm/SKILL.md`.
```

### 9.5 PR strategy

- Branch: `feature/visual-brainstorm-skill` (NOT direct to master, per user instruction)
- PR review: codex:codex-rescue + superpowers:code-reviewer dispatched in parallel (per `feedback_parallel_review_discipline`)
- Merge conditions: ship-gate T1-T3 + N1-N6 all pass; both reviewers approve
- PyPI upload follows `feedback_release_checklist` (push tag → GitHub release → PyPI)

---

## 10. Skill-author checklist (NOT in shipped SKILL.md)

These rules constrain how the skill file is written, not how the agent runs it. Belongs only to this spec.

- [ ] **Zero Y-future phrasing** in `.claude/skills/visual-brainstorm/SKILL.md`. Grep before commit: `future|later|expand|扩展到|subskills|domain packs`. Any hit = revision
- [ ] **Section layout canonical place** is the `## Template` block inside skill body §5. If a schema field or section order needs to change in the future, edit that one block; the `generated_by: visual-brainstorm@<version>` anchor provides compat traceability
- [ ] **Tradition enum hardness** (B7) is enforced by the skill body's self-assert step. Test case N4 validates it
- [ ] **Partial-OpenSpec declaration** (`>` blockquote at top of every produced proposal.md) is pre-written in the `## Template` block

---

## 11. References

- [competitive-landscape.md](./2026-04-20-competitive-landscape.md) — §2.3 positioning map, §4.1 Vulca moat, §5.1-5.4 architectural takeaways, §6 anti-pattern
- [`/decompose` SKILL.md](/Users/yhryzy/dev/vulca/.claude/skills/decompose/SKILL.md) — rigor baseline; E1-E5 shape for §6 bans; §"Out of scope" shape for §0-a scope check
- Superpowers: [brainstorming](/Users/yhryzy/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/skills/brainstorming/SKILL.md) (L73-74 decomposition precedent); [writing-skills](/Users/yhryzy/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/skills/writing-skills/SKILL.md) (L150-172 frontmatter conventions, L538-552 RED phase)
- OpenSpec — [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec/) (proposal / design / tasks chain; partial alignment target)
- Academic anchors — [EMNLP 2025 Findings VULCA](https://aclanthology.org/2025.findings-emnlp.103/); [VULCA-Bench arXiv 2601.07986](https://arxiv.org/abs/2601.07986)

---

## 12. Review trail

This spec reflects two rounds of parallel review:

**Round 1** — architecture + scope (Z+Y-later plan):
- codex:codex-rescue — verdict **HIGH quality**; key input: preserve editorial-UI hook in `domain` enum
- superpowers:code-reviewer — verdict **CONDITIONAL APPROVE**; 3 conditions: zero Y refs; ≥3 RED-GREEN cases; tighten naming OR description. All met in this spec

**Round 2** — proposal.md schema + scope-check edge rules:
- codex:codex-rescue — verdict **HIGH quality**; key change: delete `series: bool` (redundant with section existence)
- superpowers:code-reviewer — verdict **CONDITIONAL APPROVE**; 5 conditions: delete `turns_used`; move section order to `## Template` block; enum+null for tradition; `single 2D artifact?` test; partial-alignment declaration. All met

Every reviewer-requested change is folded in. Spec is design-frozen; next step is `superpowers:writing-plans` → implementation plan at `docs/superpowers/plans/2026-04-21-visual-brainstorm-skill.md`.
