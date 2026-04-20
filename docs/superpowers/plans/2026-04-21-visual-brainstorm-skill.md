# `/visual-brainstorm` Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `/visual-brainstorm` skill — a zero-pixel meta-skill that turns fuzzy visual intent into a reviewable `proposal.md` — on a feature branch, mirrored byte-identical to the vulca-plugin repo, passing both parallel reviewers and the T1-T3 + N1-N6 ship-gate.

**Architecture:** Single-file skill (`SKILL.md`, ~140 lines, Hybrid shape: narrative head + structured middle + rigor tail). No new Python code. Main-repo primary source; plugin-repo mirror is byte-identical. Version-bumped via existing PyPI release flow. All content derives from the frozen design spec at `docs/superpowers/specs/2026-04-21-visual-brainstorm-skill-design.md` (commit `809e339`).

**Tech Stack:** Markdown (YAML frontmatter + prose + tables), git (feature branch + worktree), Claude Code skill loader (`.claude/skills/<name>/SKILL.md`), PyPI (hatch or existing release script).

**Companion docs** (do NOT re-read their content into this plan — already captured in spec):
- `docs/superpowers/specs/2026-04-21-visual-brainstorm-skill-design.md` — frozen design (all sections, all tables, all content). **This plan references spec sections by number; the engineer must open the spec.**
- `docs/superpowers/specs/2026-04-20-competitive-landscape.md` — moat + positioning (for context only; no implementation reference)
- `.claude/skills/decompose/SKILL.md` — rigor baseline (141 lines; weight class precedent)
- `docs/tools-readiness-matrix.md` — **not a dependency** of this plan (zero-pixel skill)

**Ship-gate (from spec §8, enumerated there, not here):** T1 (song_gongbi series poster), T2 (plain book cover no tradition), T3 (ukiyoe brand visual) + N1 (UI hard reject), N2 (SaaS hero banner edge-accept), N3 (pixel-tool pushback), N4 (unknown tradition), N5 (cap reached without finalize), N6 (second scope pushback → terminate).

---

## File Structure

### Files created

- `.claude/skills/visual-brainstorm/SKILL.md` — the shipped skill; ~140 lines
- `<plugin-repo>/skills/visual-brainstorm/SKILL.md` — byte-identical mirror
- `CHANGELOG.md` entry (if missing, create; if present, prepend)

### Files modified

- `README.md` — add `/visual-brainstorm` to the Skills section (mirror `/decompose` formatting)
- `<plugin-repo>/README.md` — same
- `pyproject.toml` — bump main-repo version (`0.17.2` → `0.17.3`)
- Plugin-repo version file (`plugin.json` or equivalent; discover during Task 14) — bump `0.16.1` → `0.16.2`

### Responsibility boundary

The only file carrying skill behavior is `SKILL.md`. README, version file, and changelog are distribution metadata. Mirror is literal copy.

---

## Task 1: Create feature worktree on fresh branch

**Files:**
- Create: git branch `feature/visual-brainstorm-skill`
- Create: worktree at `../vulca-visual-brainstorm` (sibling of the main checkout)

- [ ] **Step 1: Verify clean working state (uncommitted spec is already shipped)**

```bash
cd /Users/yhryzy/dev/vulca
git status --short | head -5
```

Expected: output shows only untracked asset directories / gen_*.png and unrelated files — no unstaged tracked changes. (Recent commits `809e339` spec + `46bc32e` audit are already on master.)

- [ ] **Step 2: Create feature branch + worktree**

```bash
git worktree add -b feature/visual-brainstorm-skill ../vulca-visual-brainstorm
cd ../vulca-visual-brainstorm
git branch --show-current
```

Expected: `feature/visual-brainstorm-skill` printed.

- [ ] **Step 3: Verify spec is visible in the worktree**

```bash
test -f docs/superpowers/specs/2026-04-21-visual-brainstorm-skill-design.md && echo OK
```

Expected: `OK`.

No commit at this stage.

---

## Task 2: Create skill directory + frontmatter stub

**Files:**
- Create: `.claude/skills/visual-brainstorm/SKILL.md`

- [ ] **Step 1: Create skill dir and a scaffolded SKILL.md**

```bash
mkdir -p .claude/skills/visual-brainstorm
cat > .claude/skills/visual-brainstorm/SKILL.md <<'EOF'
---
name: visual-brainstorm
description: Brainstorm a 2D illustrative or editorial visual project (poster, illustration, packaging, brand visual, hero/cover art) into a reviewable proposal.md. Invoke for /visual-brainstorm or when user says '视觉 brainstorm', '视觉需求', '设计 brief'. NOT for product UI/app layout, video, 3D modeling.
---

<!-- body to be filled in Tasks 3-11 per spec §§0-9 -->
EOF
```

- [ ] **Step 2: Verify frontmatter parseable as YAML**

```bash
python3 -c "import yaml,sys; doc = open('.claude/skills/visual-brainstorm/SKILL.md').read().split('---')[1]; yaml.safe_load(doc); print('OK')"
```

Expected: `OK`.

- [ ] **Step 3: Verify `description` length**

```bash
python3 -c "import yaml; doc=yaml.safe_load(open('.claude/skills/visual-brainstorm/SKILL.md').read().split('---')[1]); d=doc['description']; print(len(d), 'chars:', d)"
```

Expected: length ≤ 250 chars (routing tokenizer is generous; spec §3 targets ≤ 150 chars measured by tokenizer — the raw char count may exceed 150 because Chinese chars count as 1 token each). If raw chars > 220, shorten per spec §3 "Rules for description".

- [ ] **Step 4: Commit scaffold**

```bash
git add .claude/skills/visual-brainstorm/SKILL.md
git commit -m "feat(skill): scaffold /visual-brainstorm skill with frontmatter

Empty body; Tasks 3-11 fill sections per design spec §§0-9."
```

---

## Task 3: Write §0 Purpose & tone + §0-a Scope check

**Files:**
- Modify: `.claude/skills/visual-brainstorm/SKILL.md` — replace the `<!-- body to be filled -->` stub with §0 + §0-a content

Source of truth: spec §4 (skill body structure) defines §0 ≤ 12 lines, §0-a ≤ 8 lines. Spec §1.2 has the exact scope wording. Spec §5 (B5) has the hard-reject keyword list.

- [ ] **Step 1: Write §0 Purpose & tone section**

Open `.claude/skills/visual-brainstorm/SKILL.md`. After the closing `---` of the frontmatter, append:

```markdown

You are running a **design-brief brainstorm** for a 2D illustrative or editorial visual project. Your job is to produce a reviewable `proposal.md` that a downstream `/visual-spec` skill will turn into a resolved design. You do not generate pixels; you finalize intent.

**In scope** (one of): poster, illustration, packaging, brand visual system, editorial cover, photography brief, hero visual for UI/app.
**Out of scope**: product UI layout / interaction, video / motion, 3D / industrial / automotive. Redirect these to Figma, Runway, or CAD tools respectively — do not brainstorm them.

**Tone**: collaborative coach, not interrogator. Prefer multiple-choice questions. One question per turn.

**Tools you may call**: `view_image` (grounding on user-provided sketches), `list_traditions` / `search_traditions` / `get_tradition_guide` (tradition dialogue), `Read` (only when user provides `--tradition-yaml <path>`). **Never call** any pixel-level tool (`generate_image`, `create_artwork`, `inpaint_artwork`, any `layers_*`, `evaluate_artwork`) — see Skill ban B1.
```

- [ ] **Step 2: Write §0-a Scope check section**

Immediately after §0, append:

```markdown

## Scope check (run first, before any question)

Before the first turn, scan the topic and any args for scope violations:

1. **Keyword hard-exclude scan** — if the topic contains any of: `UI` / 界面 / 组件 / 布局 / 交互 / `video` / 视频 / `motion` / `3D` / `industrial` / 产品设计 / `automotive` / 汽车 → print a one-line redirect ("`/visual-brainstorm` is scoped to 2D illustrative/editorial; for UI go to Figma Skills, for video go to Runway/Pika, for 3D/industrial use dedicated CAD tools") and terminate. Do not enter the question loop. Do not increment the turn cap.
2. **Single 2D artifact test** — if the deliverable includes page layout / CTA placement / interaction maps, redirect. If the deliverable is a single 2D image (or a series of 2D images), accept.
3. **Fuzzy boundary** (e.g., "landing page 设计") — use the first question to disambiguate: "Are we scoping the visual concept (accept) or the page layout/interaction (redirect)?"
4. **Edge-accept** (e.g., "SaaS hero banner with character illustration") — accept, BUT record `scope-accept rationale: <one sentence>` in the `## Notes` section of the produced `proposal.md`. Audit trail is mandatory (B5).
```

- [ ] **Step 3: Line-count check**

```bash
awk '/^## Scope check/,/^## Opening/' .claude/skills/visual-brainstorm/SKILL.md | wc -l
awk '/^You are running/,/^## Scope check/' .claude/skills/visual-brainstorm/SKILL.md | wc -l
```

Expected: §0-a ≤ 20 lines (spec ≤ 8 lines of actual rules, plus heading + blanks); §0 ≤ 15 lines. If over, tighten prose; do not drop rules.

- [ ] **Step 4: Zero-Y grep**

```bash
grep -iE 'future|later|subskills|扩展到|domain packs' .claude/skills/visual-brainstorm/SKILL.md || echo "CLEAN"
```

Expected: `CLEAN` (no matches). If matched, rewrite offending line; Y-future phrasing is banned in the shipped SKILL.md (spec §10 skill-author checklist, superpowers reviewer hard condition).

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/visual-brainstorm/SKILL.md
git commit -m "feat(skill): §0 purpose + §0-a scope check

Covers zero-pixel promise, tool whitelist, scope declaration,
single-2D-artifact test, edge-accept audit trail (B5)."
```

---

## Task 4: Write §1 Opening turn template + §2 Slug generation

**Files:**
- Modify: `.claude/skills/visual-brainstorm/SKILL.md`

Source: spec §4 skill body §1 (≤ 12 lines) + §2 (≤ 6 lines); A2 solicited-sketch behavior; A6 resume-from-draft behavior.

- [ ] **Step 1: Append §1 Opening turn template**

After §0-a, append:

```markdown

## Opening turn

1. Parse any args the user passed: `--sketch <path>`, `--ref-dir <dir>`, `--tradition-yaml <path>`.
2. **If the target `docs/visual-specs/<slug>/proposal.md` already exists** — read its frontmatter:
   - `status: ready` → Error #1: refuse to overwrite; print branch instructions; terminate.
   - `status: draft` → **resume path**: read the `## Open questions` section; continue the question loop from there; preserve accumulated turn count.
3. **If no sketch was provided**, open with this solicited-sketch question (A2):

   > "Do you have a sketch or reference image I should look at? Paste a path if yes, or say 'no' to continue text-only."

   If yes → call `view_image` once on the path for grounding. If no → proceed text-only. Either answer counts as turn 1.
4. **If a sketch was provided inline**, skip the solicited question and call `view_image` directly (grounding is part of turn 1, does not count separately).
```

- [ ] **Step 2: Append §2 Slug generation**

Immediately after §1, append:

```markdown

## Slug generation

1. Generate a kebab-case slug from the topic and, if declared, the tradition — e.g., `2026-04-21-spring-festival-song-gongbi-poster`.
2. Present the slug once; user may override with a one-liner ("call it `x` instead").
3. If the resulting slug collides with an existing `docs/visual-specs/<slug>/`, apply Error #1 (ready) or Error #2 (draft) per §Error matrix.
```

- [ ] **Step 3: Zero-Y grep + commit**

```bash
grep -iE 'future|later|subskills|扩展到|domain packs' .claude/skills/visual-brainstorm/SKILL.md || echo "CLEAN"
git add .claude/skills/visual-brainstorm/SKILL.md
git commit -m "feat(skill): §1 opening + §2 slug generation

Solicited-sketch flow (A2), resume-from-draft (A6), slug kebab-case + collision delegation."
```

Expected: `CLEAN`.

---

## Task 5: Write §3 Decision tree (5 nodes)

**Files:**
- Modify: `.claude/skills/visual-brainstorm/SKILL.md`

Source: spec §4 (5 nodes, ≤ 20 lines, table form).

- [ ] **Step 1: Append §3 Decision tree as a table**

After §2, append:

```markdown

## Decision tree — 5 nodes

Walk these in order; each node's answer adjusts the question loop and the produced proposal.md.

| Node | Question | If YES | If NO |
|---|---|---|---|
| A | User provided a sketch? | `view_image` once for grounding (no pixel analysis) | Skip; rely on text |
| B | User declared a tradition (from `list_traditions` or `--tradition-yaml`)? | Call `get_tradition_guide(<tradition>)`; flag `## Acceptance rubric` MUST (B3) | Set `tradition: null`; rubric omitted |
| C | User named reference images / URLs? | Record them in `## References` as plain text; do not analyze | Write `none` in `## References` |
| D | Single image or series? | If series → include `## Series plan` section | If single → omit `## Series plan` |
| E | User wants a spike to try a direction before committing? | Record the spike candidate under `## Open questions` for `/visual-spec` | Skip |
```

- [ ] **Step 2: Zero-Y grep + commit**

```bash
grep -iE 'future|later|subskills|扩展到|domain packs' .claude/skills/visual-brainstorm/SKILL.md || echo "CLEAN"
git add .claude/skills/visual-brainstorm/SKILL.md
git commit -m "feat(skill): §3 5-node decision tree (A-E)"
```

Expected: `CLEAN`.

---

## Task 6: Write §4 6-dimension question bank

**Files:**
- Modify: `.claude/skills/visual-brainstorm/SKILL.md`

Source: spec §4 dimension bank (≤ 25 lines, table).

- [ ] **Step 1: Append §4 as a table with prompt + skip + default columns**

After §3, append:

```markdown

## Question bank — 6 dimensions

Cover these dimensions across the turn budget (cap 8 hard / 12 soft; see §Turn cap). Order by what the user has not yet clarified; do not force all 6 if the answer is obvious from prior context.

| Dimension | Sample prompt | Skip allowed? | Inferred default if skipped |
|---|---|---|---|
| Tradition | "Which cultural tradition should anchor this? (I can list options via `list_traditions`, or accept a custom YAML path.)" | Yes | `tradition: null`; omit rubric |
| Audience | "Who is the viewer? Demographic, familiarity with the tradition, consumption context." | Yes | "unspecified audience" recorded |
| Physical form | "What's the final deliverable format? Print size, digital viewport, packaging die-line, etc." | No — must have answer | — |
| Market | "Is this for a 国内 / 海外 / 多语言 audience? Any region-specific constraints?" | Yes | "domestic, no multilingual" recorded |
| Budget & deadline | "How many deliverables, by when, with what time budget for iteration?" | No — must have answer | — |
| Color constraints | "Any required palette, brand color, or forbidden color?" | Yes | "none specified" recorded |
```

- [ ] **Step 2: Zero-Y grep + commit**

```bash
grep -iE 'future|later|subskills|扩展到|domain packs' .claude/skills/visual-brainstorm/SKILL.md || echo "CLEAN"
git add .claude/skills/visual-brainstorm/SKILL.md
git commit -m "feat(skill): §4 6-dimension question bank

tradition / audience / physical-form / market / budget-deadline / color."
```

Expected: `CLEAN`.

---

## Task 7: Write §5 proposal.md schema with `## Template` block

**Files:**
- Modify: `.claude/skills/visual-brainstorm/SKILL.md`

Source: spec §5.1 frontmatter, §5.2 domain enum priority, §5.3 section layout, §5.4 RFC 2119 rules. This is the longest subsection; spec §4 budgets ≤ 25 lines. **Budget strictness is a guideline — if the `## Template` block needs to be verbatim, it takes the space it takes.**

- [ ] **Step 1: Append §5 intro prose**

After §4, append:

```markdown

## Produced artifact — `proposal.md` schema

Write the final artifact to `docs/visual-specs/<slug>/proposal.md`. The artifact has a 6-field YAML frontmatter and 12 markdown sections (2 conditional). Copy the `## Template` block below verbatim and fill the bracketed placeholders.

**Domain enum** (`frontmatter.domain`, required):

| Deliverable signature | domain value |
|---|---|
| Activity / exhibition / event signage | `poster` |
| Standalone illustrative artwork, no host | `illustration` |
| Product packaging / bottle / label | `packaging` |
| Brand visual system / marketing series / peripherals | `brand_visual` |
| Book / magazine / report cover | `editorial_cover` |
| Brief for an upcoming photo shoot | `photography_brief` |
| Hero illustration / splash art for app or web (not layout) | `hero_visual_for_ui` |

**Disambiguation**: art-exhibition poster → `poster` (activity-signage wins over editorial); book-with-illustrated-cover → `editorial_cover` (host-artifact wins over illustration).
```

- [ ] **Step 2: Append the `## Template` block (verbatim copyable)**

Immediately after §5 intro, append:

````markdown

### Template (copy and fill)

```markdown
---
slug: YYYY-MM-DD-<topic>
status: draft
domain: <one of poster | illustration | packaging | brand_visual | editorial_cover | photography_brief | hero_visual_for_ui>
tradition: <enum id from list_traditions OR YAML literal null>  # NEVER "N/A", "none", "", "unknown" — see B7
generated_by: visual-brainstorm@0.1.0
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# <human-readable title>

> Partial OpenSpec alignment: status enum + RFC 2119 keywords. Does not use ADDED/MODIFIED/REMOVED delta markers. Full alignment deferred until /visual-spec consumption validates need.

## Intent
<2-5 sentences of user intent; no compositional detail>

## Audience
<viewer / consumer description; or the literal "none specified">

## Physical form
<print size / digital viewport / packaging die-line / etc.>

## Market
<国内 / 海外 / 多语言; or "domestic, no multilingual">

## Budget & deadline
<time budget, deliverables count, hard deadlines>

## Color constraints
<palette or "none specified">

## References
<external URLs / local paths, OR the literal "none">

## Series plan
<ONLY if series; count / variation axis / rhythm / deliverables list>

## Acceptance rubric
<ONLY if tradition is non-null>
- [L1 <dimension>] ... **MUST** ...
- [L2 <dimension>] ... **MUST** ...
- [L3 <dimension>] ... **SHOULD** ...
- [L4 <dimension>] ... **SHOULD** ...
- [L5 <dimension>] ... **MAY** ...

## Questions resolved
- Q: ...
  A: ...
- ...

## Open questions
<bullet list; non-empty if turn cap forced show>

## Notes
<free-form; edge-accept cases MUST log "scope-accept rationale: <reason>" here>
```

**RFC 2119 usage**: tag each `## Acceptance rubric` bullet with MUST / SHOULD / MAY per L-level defaults (L1-L2 MUST, L3-L4 SHOULD, L5 MAY). Tradition guide MAY override (e.g., religious iconography taboos → L3 MUST). `## Open questions` bullets MAY use MUST to flag "downstream must resolve". Other sections: prose only.

**Empty-section rule**: when a non-conditional section has no content, write the literal `none` (not `TBD`, `N/A`, or blank).
````

- [ ] **Step 3: Zero-Y grep + commit**

```bash
grep -iE 'future|later|subskills|扩展到|domain packs' .claude/skills/visual-brainstorm/SKILL.md || echo "CLEAN"
git add .claude/skills/visual-brainstorm/SKILL.md
git commit -m "feat(skill): §5 proposal.md schema + Template block

6-field frontmatter, domain enum (7 values) priority table, 12 sections
(2 conditional), RFC 2119 usage, empty-section 'none' rule."
```

Expected: `CLEAN`.

---

## Task 8: Write §6 Turn cap + finalize

**Files:**
- Modify: `.claude/skills/visual-brainstorm/SKILL.md`

Source: spec A7 (8/12 cap), B4 (no auto-advance), spec §4 §6 (≤ 8 lines).

- [ ] **Step 1: Append §6 after §5**

```markdown

## Turn cap and finalize

- **Hard cap: 8 questions per session.** Clarifying Qs + dimension-bank Qs + decision-tree follow-ups all count. Out-of-scope redirect turns and "I don't generate images" responses do NOT count.
- **Soft extension: +4 (hard 12)** if the user explicitly says "deep dive" or equivalent.
- When the cap is reached without the user having said "finalize" → Error #7: force-show the full current draft proposal.md and ask "finalize to lock `status: ready`, or 'deep dive' to extend +4?". **Do not auto-advance** (B4).
- **Finalize trigger**: the user says "finalize" / "done" / "ready" / "lock it". Then and only then, flip `status: draft → status: ready` in frontmatter. Print the §Handoff line and stop.
```

- [ ] **Step 2: Zero-Y grep + commit**

```bash
grep -iE 'future|later|subskills|扩展到|domain packs' .claude/skills/visual-brainstorm/SKILL.md || echo "CLEAN"
git add .claude/skills/visual-brainstorm/SKILL.md
git commit -m "feat(skill): §6 turn cap 8/12 + finalize gate (B4)"
```

Expected: `CLEAN`.

---

## Task 9: Write §7 Skill bans B1-B7

**Files:**
- Modify: `.claude/skills/visual-brainstorm/SKILL.md`

Source: spec §6 (the complete B1-B7 table with rule · consequence · remedy columns).

- [ ] **Step 1: Append §7 table verbatim from spec §6**

After §6, append the following (this is a compressed form of spec §6 — the one-line-per-ban constraint holds):

```markdown

## Skill bans

Rules the agent running this skill MUST follow. Each: rule / consequence if violated / remedy.

| # | Rule | Consequence | Remedy |
|---|---|---|---|
| **B1** | No pixel-level tool calls. Forbidden: `generate_image`, `create_artwork`, `inpaint_artwork`, any `layers_*`, `evaluate_artwork`. | Breaks zero-pixel promise; Week-1 shippability lost | Whitelist: `view_image`, `list_traditions`, `search_traditions`, `get_tradition_guide`, `Read` (only for `--tradition-yaml`). |
| **B2** | No hidden brief. Even if user says "just go", finalize MUST show full draft + wait for explicit confirm. | Vibe-spec anti-pattern; downstream burns tokens on misaligned intent | User may shorten `## Intent`; `## Acceptance rubric`, `## Open questions`, frontmatter MUST display in full. |
| **B3** | Tradition declared ⇒ `## Acceptance rubric` MUST appear (L1-L5 template; tradition-guide MAY override strength). | Vulca moat artifact missing | If user insists "no rubric", set `tradition: null` first — consistent declaration, not bypass. |
| **B4** | No auto-advance status. `draft → ready` ONLY on explicit user trigger ("done" / "finalize" / "ready"). | Unverified draft consumed downstream; resume broken | At cap, present draft and ask; never flip status automatically. |
| **B5** | Scope-check first; no out-of-scope brainstorm. Hard-exclude hit → redirect + terminate (no turn cap increment). | Skill props up a domain it cannot win | Fuzzy → first-Q disambiguate. Edge-accept → log `scope-accept rationale` in `## Notes`. |
| **B6** | No parallel invocation on same slug. | File race; state corruption; resume broken | Detect via `updated` timestamp vs now; reject second call; user renames slug. |
| **B7** | `frontmatter.tradition` MUST be enum-id or YAML literal `null`. Forbidden strings: `"N/A"`, `"none"`, `"null"`, `""`, `"unknown"`. | `if tradition:` truthy fails → rubric silently omitted → moat artifact missing | Self-assert before write: "tradition is enum-id or YAML null?" |
```

- [ ] **Step 2: Zero-Y grep + commit**

```bash
grep -iE 'future|later|subskills|扩展到|domain packs' .claude/skills/visual-brainstorm/SKILL.md || echo "CLEAN"
git add .claude/skills/visual-brainstorm/SKILL.md
git commit -m "feat(skill): §7 skill bans B1-B7

Runtime rules the agent must follow. Mirrors /decompose E1-E5 shape but
covers scope drift + vibe-spec + state integrity, not pipeline data."
```

Expected: `CLEAN`.

---

## Task 10: Write §8 Error matrix

**Files:**
- Modify: `.claude/skills/visual-brainstorm/SKILL.md`

Source: spec §7 (the complete 8-row error matrix).

- [ ] **Step 1: Append §8 table verbatim from spec §7**

After §7, append (compressed one-line-per-row):

```markdown

## Error matrix

| # | Signal | Response |
|---|---|---|
| 1 | Slug collision; existing `proposal.md` has `status: ready` | Print "already finalized at `<path>`; branch with `-v2` or pick new slug". Terminate. Do not overwrite. |
| 2 | Slug collision; existing has `status: draft` | Resume path (A6): read `## Open questions`; continue loop; turn cap accumulates. |
| 3 | Unknown tradition (not in `list_traditions` + no `--tradition-yaml` match) | Prompt: (a) ask for `--tradition-yaml <path>`; (b) set `tradition: null` + freeform in `## Notes`; (c) if user insists on undefined id, treat as `null` + warn "rubric omitted, tradition unvalidated". Never fabricate enum id. |
| 4 | `--tradition-yaml` unreadable (FileNotFoundError / YAML parse / schema) | Print `tradition-yaml at <path> invalid: <err>`. Fall through to Error #3. Do not auto-retry. |
| 5 | `--sketch` unreadable / `view_image` fails | Print `sketch at <path> unreadable: <err>. Proceeding text-only.` Degrade; do not charge turn cap. |
| 6 | User requests pixel action mid-dialogue | Print "I don't generate images; I finalize the brief. After finalize, run /visual-spec then downstream pixel tools." Do not call B1 tools. Does not count toward cap. |
| 7 | Turn cap reached without user finalize | Force-show draft + prompt "finalize or deep dive". Do not auto-finalize (B4). |
| 8 | Scope hard-reject + user pushback | Explain once. Second pushback → terminate silently. |

**Do-not-auto-retry**: Errors #3, #4, #8. **Do-not-overwrite**: Error #1, Error #6.
```

- [ ] **Step 2: Zero-Y grep + commit**

```bash
grep -iE 'future|later|subskills|扩展到|domain packs' .claude/skills/visual-brainstorm/SKILL.md || echo "CLEAN"
git add .claude/skills/visual-brainstorm/SKILL.md
git commit -m "feat(skill): §8 error matrix (8 rows)"
```

Expected: `CLEAN`.

---

## Task 11: Write §9 Handoff + References

**Files:**
- Modify: `.claude/skills/visual-brainstorm/SKILL.md`

- [ ] **Step 1: Append §9 and References**

After §8, append:

```markdown

## Handoff

On finalize (status: draft → ready), print exactly:

> `Ready for /visual-spec. Run it with \`/visual-spec <slug>\`.`

Do NOT auto-invoke `/visual-spec`. Human-in-the-loop gate is preserved here.

## References

- Design spec: `docs/superpowers/specs/2026-04-21-visual-brainstorm-skill-design.md`
- L1-L5 cultural evaluation academic anchors: EMNLP 2025 Findings VULCA (`aclanthology.org/2025.findings-emnlp.103/`); VULCA-Bench (`arxiv.org/abs/2601.07986`)
- Sibling skill for tone/rigor baseline: `.claude/skills/decompose/SKILL.md`
```

- [ ] **Step 2: Zero-Y grep + commit**

```bash
grep -iE 'future|later|subskills|扩展到|domain packs' .claude/skills/visual-brainstorm/SKILL.md || echo "CLEAN"
git add .claude/skills/visual-brainstorm/SKILL.md
git commit -m "feat(skill): §9 handoff + references

Skill body complete; next tasks run quality checks and ship-gate."
```

Expected: `CLEAN`.

---

## Task 12: Quality pass — line count, zero-Y audit, schema self-check

**Files:**
- Read-only check on `.claude/skills/visual-brainstorm/SKILL.md`

- [ ] **Step 1: Line-count check**

```bash
wc -l .claude/skills/visual-brainstorm/SKILL.md
```

Expected: between 120 and 170 lines. Target 140 (matches `/decompose`'s 141). If over 170, tighten prose without removing rules. If under 120, a rule is likely missing.

- [ ] **Step 2: Full zero-Y audit**

```bash
grep -inE 'future|later|subskills|扩展到|domain packs|going to add|plan to support' .claude/skills/visual-brainstorm/SKILL.md
```

Expected: no matches (exit 1). If any match, rewrite offending line.

- [ ] **Step 3: Frontmatter fields check**

```bash
python3 - <<'PY'
import yaml
doc = open('.claude/skills/visual-brainstorm/SKILL.md').read().split('---')[1]
meta = yaml.safe_load(doc)
assert set(meta) == {'name', 'description'}, f"unexpected frontmatter keys: {set(meta)}"
assert meta['name'] == 'visual-brainstorm'
assert 'NOT for' in meta['description'], "scope exclusion missing from description"
print('OK')
PY
```

Expected: `OK`.

- [ ] **Step 4: Schema block presence**

```bash
grep -F "generated_by: visual-brainstorm@0.1.0" .claude/skills/visual-brainstorm/SKILL.md
grep -F "Partial OpenSpec alignment" .claude/skills/visual-brainstorm/SKILL.md
```

Expected: both match exactly once.

- [ ] **Step 5: All 7 bans present**

```bash
for b in B1 B2 B3 B4 B5 B6 B7; do
  grep -Fq "**${b}**" .claude/skills/visual-brainstorm/SKILL.md || echo "MISSING $b"
done
```

Expected: no `MISSING` output.

- [ ] **Step 6: No commit** (pass-only check; if any step failed, go back to the corresponding task and fix).

---

## Task 13: Run ship-gate (T1-T3 + N1-N6)

**Files:**
- No file changes — this task runs scripted Claude Code sessions and records outcomes.

Source: spec §8.1 (T1-T3 positive cases), §8.2 (N1-N6 negative cases). **All 9 cases enumerated there; this task references them rather than re-stating.**

- [ ] **Step 1: Per-case checklist from spec §8.1**

Open a fresh Claude Code session (to avoid contaminated context). For each of T1, T2, T3:

1. Start: `/visual-brainstorm <topic per spec>`
2. Run through the dialog until `status: ready`.
3. Verify each bullet in the spec §8.1 "Per-case checklist" (turn count, frontmatter fields, conditional sections, no banned tool calls, `generated_by` anchor, partial-alignment blockquote, zero Y-phrasing).

Record outcomes in the worktree: `docs/superpowers/plans/visual-brainstorm-ship-gate-log.md` (create during this task) — one section per case (T1 / T2 / T3), each with PASS/FAIL + notes.

- [ ] **Step 2: Negative cases N1-N6 from spec §8.2**

Same fresh-session discipline. For each N1-N6, verify the `Expected behavior` column in spec §8.2 fires. Record in the same ship-gate log.

- [ ] **Step 3: If any case FAILs**

Stop. Go back to the task (3-11) responsible for the failing behavior, fix the SKILL.md, re-run only the failing case. Do NOT proceed to Task 14 with a failing case.

- [ ] **Step 4: When all 9 pass, commit the log**

```bash
git add docs/superpowers/plans/visual-brainstorm-ship-gate-log.md
git commit -m "test(skill): ship-gate log — T1-T3 + N1-N6 all PASS

Superpowers reviewer condition 2 satisfied. Ready for mirror + release."
```

---

## Task 14: Mirror byte-identical to vulca-plugin

**Files:**
- Create: `<plugin-repo>/skills/visual-brainstorm/SKILL.md`

- [ ] **Step 1: Locate the plugin repo**

```bash
find ~ -name 'vulca-plugin*' -type d -maxdepth 5 2>/dev/null | head -5
```

Use whichever path the main maintainer's local checkout uses (likely `~/dev/vulca-plugin` or similar).

- [ ] **Step 2: Copy the skill dir**

```bash
PLUGIN_REPO="<path from Step 1>"
mkdir -p "$PLUGIN_REPO/skills/visual-brainstorm"
cp .claude/skills/visual-brainstorm/SKILL.md "$PLUGIN_REPO/skills/visual-brainstorm/SKILL.md"
```

- [ ] **Step 3: Byte-equality verification**

```bash
diff -q .claude/skills/visual-brainstorm/SKILL.md "$PLUGIN_REPO/skills/visual-brainstorm/SKILL.md"
```

Expected: empty output (files are identical).

```bash
md5sum .claude/skills/visual-brainstorm/SKILL.md "$PLUGIN_REPO/skills/visual-brainstorm/SKILL.md"
```

Expected: identical md5 sums.

- [ ] **Step 4: Commit in plugin repo on feature branch**

```bash
cd "$PLUGIN_REPO"
git checkout -b feature/visual-brainstorm-skill
git add skills/visual-brainstorm/SKILL.md
git commit -m "feat(skill): add /visual-brainstorm (byte-identical to vulca main)

Mirrors vulca@<commit-sha> where the skill was authored. See vulca:
docs/superpowers/specs/2026-04-21-visual-brainstorm-skill-design.md"
cd -
```

Record the plugin-repo commit SHA for Task 16 changelog reference.

---

## Task 15: README updates (main + plugin)

**Files:**
- Modify: `README.md` (main)
- Modify: `<plugin-repo>/README.md`

- [ ] **Step 1: Find the Skills section in main README**

```bash
grep -n '^## .*Skills' README.md || grep -n '/decompose' README.md | head -3
```

Note the section heading and the existing `/decompose` presentation.

- [ ] **Step 2: Add `/visual-brainstorm` entry mirroring `/decompose` format**

Edit `README.md` to add, under the same heading where `/decompose` lives, an entry matching its prose style. Exact prose (adapt phrasing to match the local `/decompose` entry; this is the minimal content the entry MUST carry):

```markdown
- **`/visual-brainstorm`** — turn fuzzy visual intent (topic, optional sketch, optional references) into a reviewable `proposal.md`. Zero-pixel, Discovery-metadata only. Scoped to 2D illustrative/editorial imagery (poster, illustration, packaging, brand visual, cover art, photography brief, hero visuals for UI). See `.claude/skills/visual-brainstorm/SKILL.md`.
```

- [ ] **Step 3: Same edit in plugin README**

Repeat Step 2 in `<plugin-repo>/README.md`, using the plugin repo's relative path to the skill: `skills/visual-brainstorm/SKILL.md`.

- [ ] **Step 4: Commit each repo**

```bash
# main
git add README.md
git commit -m "docs(readme): advertise /visual-brainstorm skill"
# plugin
cd "$PLUGIN_REPO"
git add README.md
git commit -m "docs(readme): advertise /visual-brainstorm skill"
cd -
```

---

## Task 16: Version bumps + changelog entries

**Files:**
- Modify: `pyproject.toml` (main repo; version 0.17.2 → 0.17.3)
- Modify: plugin repo version file (discover during this task)
- Create or modify: `CHANGELOG.md` in each repo

- [ ] **Step 1: Main-repo version bump**

```bash
grep -n '^version\s*=' pyproject.toml
```

Replace `version = "0.17.2"` with `version = "0.17.3"`.

- [ ] **Step 2: Add main-repo changelog entry**

Prepend to `CHANGELOG.md` (create with just this entry if file doesn't exist):

```markdown
## v0.17.3 — 2026-04-2X

### Added
- `/visual-brainstorm` skill — guide fuzzy visual intent into reviewable
  proposal.md (OpenSpec-aligned partial). Zero-pixel, Discovery-metadata-only.
  Scoped to 2D illustrative/editorial domains (7 enum values). Conditional
  L1-L5 rubric for tradition-bearing projects.
  See `.claude/skills/visual-brainstorm/SKILL.md`.
```

Replace `2026-04-2X` with the actual release date.

- [ ] **Step 3: Commit main-repo version + changelog**

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "release: v0.17.3 — add /visual-brainstorm skill"
```

- [ ] **Step 4: Plugin-repo version bump**

```bash
cd "$PLUGIN_REPO"
ls -1 | grep -iE 'plugin|manifest|version'
```

Discover the version file (likely `plugin.json`, `package.json`, or similar). Bump `0.16.1` → `0.16.2`. Add a matching plugin CHANGELOG entry.

```bash
git add <version-file> CHANGELOG.md
git commit -m "release: v0.16.2 — add /visual-brainstorm skill"
cd -
```

---

## Task 17: Parallel review dispatch (codex + superpowers)

**Files:**
- Nothing edited; runs two agents.

Per memory `feedback_parallel_review_discipline`: non-trivial PRs go through both reviewers in parallel.

- [ ] **Step 1: Push both feature branches**

```bash
# main repo
git push -u origin feature/visual-brainstorm-skill
# plugin repo
cd "$PLUGIN_REPO"
git push -u origin feature/visual-brainstorm-skill
cd -
```

- [ ] **Step 2: Open PRs**

```bash
gh pr create --title "feat(skill): /visual-brainstorm — 2D illustrative brief brainstorm" --body "$(cat <<'EOF'
## Summary
- Ships `.claude/skills/visual-brainstorm/SKILL.md`, a zero-pixel meta-skill
- Brainstorms fuzzy visual intent into `proposal.md` (OpenSpec partial alignment)
- Scoped to 2D illustrative/editorial imagery; UI layout / video / 3D redirected
- Conditional L1-L5 rubric enforces Vulca's cultural-evaluation moat

Design spec: `docs/superpowers/specs/2026-04-21-visual-brainstorm-skill-design.md` (commit 809e339)
Ship-gate log: `docs/superpowers/plans/visual-brainstorm-ship-gate-log.md`
Version: v0.17.2 → v0.17.3

## Test plan
- [x] Ship-gate T1-T3 (cultural series, plain cover, ukiyoe brand visual) — all PASS
- [x] Negative cases N1-N6 — all PASS
- [x] Zero Y-future phrasing audit — CLEAN
- [x] Frontmatter audit — only name + description keys
- [x] Line count 120-170 — actual <fill in from Task 12>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Same for the plugin-repo PR.

- [ ] **Step 3: Dispatch codex + superpowers reviewers in parallel**

Invoke two subagents in a single message, each reviewing both PRs (main + plugin). Prompts should reference the design spec and ask for verdict + conditions. Dispatch both as `run_in_background: true`.

- [ ] **Step 4: Wait for both verdicts**

Resolve any CONDITIONAL APPROVE conditions inline; push amendments. Re-dispatch only if a reviewer requested large-surface changes.

- [ ] **Step 5: Once both approve, proceed to Task 18.**

---

## Task 18: Merge + PyPI release

**Files:**
- Merges the feature branch; PyPI upload.

- [ ] **Step 1: Merge main-repo PR**

After both reviewers approve:

```bash
gh pr merge --squash --delete-branch
```

Verify master now contains the skill at `.claude/skills/visual-brainstorm/SKILL.md`.

- [ ] **Step 2: Tag and push tag**

```bash
git checkout master
git pull
git tag v0.17.3
git push origin v0.17.3
```

- [ ] **Step 3: Build + PyPI upload**

Use the existing release flow (per `memory/feedback_release_checklist` — push tag → GitHub release → PyPI):

```bash
# whichever build tool the repo uses (hatch / setuptools)
rm -rf dist/ && python3 -m build
python3 -m twine upload dist/*
```

Expected: `vulca-0.17.3.tar.gz` and wheel uploaded to PyPI.

- [ ] **Step 4: GitHub release**

```bash
gh release create v0.17.3 --title "v0.17.3 — /visual-brainstorm skill" --notes-file <(sed -n '/^## v0.17.3/,/^## v0.17.2/p' CHANGELOG.md | head -n -1)
```

- [ ] **Step 5: Plugin-repo merge + tag + release**

Repeat Steps 1-4 in the plugin repo for v0.16.2.

- [ ] **Step 6: README install pin bump**

On both repos (main + plugin), bump any install-pin examples in README from previous versions to the new ones. Per `memory/project_readme_refresh_shipped`, this follows the same pattern as commit `50f27af`. Commit and push directly to master:

```bash
# main
sed -i '' 's/vulca==0.17.2/vulca==0.17.3/g' README.md
git add README.md
git commit -m "docs(readme): bump install pins 0.17.2 -> 0.17.3"
git push
# plugin
cd "$PLUGIN_REPO"
# analogous sed edit, commit, push
cd -
```

- [ ] **Step 7: Worktree cleanup**

```bash
cd ~/dev/vulca
git worktree remove ../vulca-visual-brainstorm
```

---

## Self-Review

**Spec coverage**:
- §1.1 Purpose → Task 3 §0
- §1.2 Scope (7 domains, redirect list) → Task 3 §0 + §0-a
- §1.3 Moat defense (conditional rubric) → Task 7 §5 + Task 9 §7 B3
- §2 Architecture → whole plan
- §3 Frontmatter → Task 2 + Task 12 Step 3
- §4 Skill body structure → Tasks 3-11 match §§0-9 one-to-one
- §5.1 6-field frontmatter in proposal.md → Task 7
- §5.2 domain enum priority table → Task 7 Step 1
- §5.3 Section layout `## Template` block → Task 7 Step 2
- §5.4 RFC 2119 rules → Task 7 Step 2
- §6 Skill bans B1-B7 → Task 9
- §7 Error matrix 8 rows → Task 10
- §8.1 Ship-gate T1-T3 → Task 13 Step 1
- §8.2 Negative cases N1-N6 → Task 13 Step 2
- §8.3 Deliberately not tested → implicit (plan doesn't add those gates)
- §9 Distribution → Tasks 14-16
- §10 Skill-author checklist (zero-Y grep, schema hardness, Template canonical place, partial-OpenSpec notice) → Tasks 3-11 Step ≥ 4 in each + Task 12
- §11 References → Task 11
- §12 Review trail → Task 17 reviewer round

No gaps.

**Placeholder scan**: No `TBD`, `TODO`, `fill in`, or "similar to Task N" phrasings. The only variable content is (a) the actual release date (marked `2026-04-2X` with explicit instruction to replace) and (b) the plugin-repo absolute path (discovered in Task 14 Step 1 and captured into `$PLUGIN_REPO` shell variable thereafter). These are deliberate runtime discoveries, not placeholders.

**Type consistency**: `slug`, `status`, `domain`, `tradition`, `generated_by`, `created`, `updated` used identically across Tasks 2, 7, 12. `docs/visual-specs/<slug>/proposal.md` path used identically in Tasks 4, 7, 10. All skill ban IDs (B1-B7) reference the same definitions in Tasks 3, 7, 9 (and in the spec).

Plan is internally consistent and fully covers the spec.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-21-visual-brainstorm-skill.md`. Two execution options:

1. **Subagent-Driven (recommended)** — fresh subagent per task, 2-stage review between tasks (spec compliance + code quality), fast iteration. Uses `superpowers:subagent-driven-development`.
2. **Inline Execution** — execute in this session using `superpowers:executing-plans`, batch with checkpoints for review.

Which approach?
