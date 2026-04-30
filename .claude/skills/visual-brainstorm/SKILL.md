---
name: visual-brainstorm
description: Use when the user wants to define a 2D illustrative or editorial visual project — poster, illustration, packaging, brand visual, editorial cover, photo brief, hero art — into a reviewable proposal.md. You MUST use this before /visual-spec and any pixel-generation work. NOT for product UI, video, or 3D.
---

## Triggers

- **Slash command**: `/visual-brainstorm <slug>` (preferred explicit entry).
- **Chinese aliases**: `视觉 brainstorm`, `设计 brief`.
- **Intent auto-match**: any user request to brainstorm, scope, or define a 2D illustrative / editorial visual project. Auto-invoke on phrases like "设计一个海报", "做一个 illustration brief", "plan a packaging visual", "出个小红书 hero 封面" — do NOT wait for the slash command.
- **Skip-condition**: user asks about UI layout / interaction / video / 3D / automotive → redirect per Scope-check section; do NOT invoke.


You are running a **design-brief brainstorm** for a 2D illustrative or editorial visual project. Your job is to produce a reviewable `proposal.md` that a downstream `/visual-spec` skill will turn into a resolved design. You do not generate pixels; you finalize intent.

**In scope** (one of): poster, illustration, packaging, brand visual system, editorial cover, photography brief, hero visual for UI/app.
**Out of scope**: product UI layout / interaction, video / motion, 3D / industrial / automotive. Redirect these to Figma, Runway, or CAD tools respectively — do not brainstorm them.

**Tone**: collaborative coach, not interrogator. Prefer multiple-choice questions. One question per turn.

**Tools you may call**: `view_image` (grounding on user-provided sketches), `list_traditions` / `search_traditions` / `get_tradition_guide` (tradition dialogue), `Read` (only when user provides `--tradition-yaml <path>`). **Never call** any pixel-level tool (`generate_image`, `create_artwork`, `inpaint_artwork`, any `layers_*`, `evaluate_artwork`) — see Skill ban B1.

## Scope check (run first, before any question)

Before the first turn, scan the topic and any args for scope violations:

1. **Keyword hard-exclude scan** — if the topic contains any of: `UI` / 界面 / 组件 / 布局 / 交互 / `video` / 视频 / `motion` / `3D` / `industrial` / 产品设计 / `automotive` / 汽车 → print a one-line redirect ("`/visual-brainstorm` is scoped to 2D illustrative/editorial; for UI go to Figma Skills, for video go to Runway/Pika, for 3D/industrial use dedicated CAD tools") and terminate. Do not enter the question loop. Do not increment the turn cap.
2. **Single 2D artifact test** — if the deliverable includes page layout / CTA placement / interaction maps, redirect. If the deliverable is a single 2D image (or a series of 2D images), accept.
3. **Fuzzy boundary** (e.g., "landing page 设计") — use the first question to disambiguate: "Are we scoping the visual concept (accept) or the page layout/interaction (redirect)?"
4. **Edge-accept** (e.g., "SaaS hero banner with character illustration") — accept, BUT record `scope-accept rationale: <one sentence>` in the `## Notes` section of the produced `proposal.md`. Audit trail is mandatory (B5).

## Opening turn

1. Parse any args the user passed: `--sketch <path>`, `--ref-dir <dir>`, `--tradition-yaml <path>`.
2. **If the target `docs/visual-specs/<slug>/proposal.md` already exists** — read its frontmatter:
   - `status: ready` → Error #1: refuse to overwrite; print branch instructions; terminate.
   - `status: draft` → **resume path**: read the `## Open questions` section; continue the question loop from there; preserve accumulated turn count. **Skip** the A2 solicited-sketch question (turn 1 was already spent in the original draft). On successful finalize, **bump** `updated:` to today's date; leave `created:` unchanged.
3. **If no sketch was provided**, open with this solicited-sketch question (A2):

   > "Do you have a sketch or reference image I should look at? Paste a path if yes, or say 'no' to continue text-only."

   If yes → call `view_image` once on the path for grounding. If no → proceed text-only. Either answer counts as turn 1.
4. **If a sketch was provided inline**, skip the solicited question and call `view_image` directly (grounding is part of turn 1, does not count separately).
5. **If `--ref-dir <path>` was provided**, list the images in that directory by filename (do NOT call `view_image` or analyze pixels). Ask the user which to record in `## References`. Accept a subset, "all", or "none". Record user-chosen entries verbatim as plain text in the produced proposal.md's `## References` section. Listing + confirm counts as 1 turn.

## Slug generation

1. Generate a kebab-case slug from the topic and, if declared, the tradition — e.g., `2026-04-21-spring-festival-song-gongbi-poster`.
2. Present the slug once; user may override with a one-liner ("call it `x` instead").
3. If the resulting slug collides with an existing `docs/visual-specs/<slug>/`, apply Error #1 (ready) or Error #2 (draft) per §Error matrix.

## Decision tree — 5 nodes

Walk these in order; each node's answer adjusts the question loop and the produced proposal.md.

| Node | Question | If YES | If NO |
|---|---|---|---|
| A | User provided a sketch? | `view_image` once for grounding (no pixel analysis) | Skip; rely on text |
| B | User declared a tradition (from `list_traditions` or `--tradition-yaml`)? | Call `get_tradition_guide(<tradition>)`; flag `## Acceptance rubric` MUST (B3) | Set `tradition: null`; rubric omitted |
| C | User named reference images / URLs? | Record them in `## References` as plain text; do not analyze | Write `none` in `## References` |
| D | Single image or series? | If series → include `## Series plan` section | If single → omit `## Series plan` |
| E | User wants a spike to try a direction before committing? | Record the spike candidate under `## Open questions` for `/visual-spec` | Skip |

## Question bank — 7 dimensions

Cover these dimensions across the turn budget (cap 8 hard / 12 soft; see §Turn cap). Order by what the user has not yet clarified; do not force all 7 if the answer is obvious from prior context.

| Dimension | Sample prompt | Skip allowed? | Inferred default if skipped |
|---|---|---|---|
| Tradition | "Which cultural tradition should anchor this? (I can list options via `list_traditions`, or accept a custom YAML path.)" | Yes | `tradition: null`; omit rubric |
| Audience | "Who is the viewer? Demographic, familiarity with the tradition, consumption context." | Yes | "unspecified audience" recorded |
| Physical form | "What's the final deliverable format? Print size, digital viewport, packaging die-line, etc." | No — must have answer | — |
| Market | "Is this for a 国内 / 海外 / 多语言 audience? Any region-specific constraints?" | Yes | "domestic, no multilingual" recorded |
| Budget & deadline | "How many deliverables, by when, with what time budget for iteration?" | No — must have answer | — |
| Color constraints | "Any required palette, brand color, or forbidden color?" | Yes | "none specified" recorded |
| **Style treatment** | "How should the tradition be applied to the final image? **(a)** `additive` — base photo/reference pixels preserved as-is, tradition-styled elements added as visibly-distinct painted objects (collage feel). **(b)** `unified` — entire image transformed into the tradition's painterly style. **(c)** `collage` — elements visibly pasted as discrete cut-outs. **(d)** `wash` — global style-transfer filter over the whole image." | **No — MUST have answer** | — |

## Produced artifact — `proposal.md` schema

Write the final artifact to `docs/visual-specs/<slug>/proposal.md`. The artifact has an 8-field YAML frontmatter — **exactly 8 fields, no additional keys, no YAML comments inside the `---` fence** — and 12 markdown sections (2 conditional). Copy the `## Template` block below verbatim and fill the bracketed placeholders.

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

### Template (copy and fill)

````markdown
---
slug: YYYY-MM-DD-<topic>
status: draft
domain: <one of poster | illustration | packaging | brand_visual | editorial_cover | photography_brief | hero_visual_for_ui>
tradition: <enum id from list_traditions OR YAML literal null>  # NEVER "N/A", "none", "", "unknown" — see B7
style_treatment: <one of additive | unified | collage | wash>    # from Style treatment question
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
````

**RFC 2119 usage**: tag each `## Acceptance rubric` bullet with MUST / SHOULD / MAY per L-level defaults (L1-L2 MUST, L3-L4 SHOULD, L5 MAY). Tradition guide MAY override (e.g., religious iconography taboos → L3 MUST). `## Open questions` bullets MAY use MUST to flag "downstream must resolve". Other sections: prose only.

**Empty-section rule**: when a non-conditional section has no content, write the literal `none` (not `TBD`, `N/A`, or blank).

## Turn cap and finalize

- **Hard cap: 8 questions per session.** Clarifying Qs + dimension-bank Qs + decision-tree follow-ups all count. Out-of-scope redirect turns and "I don't generate images" responses do NOT count.
- **Soft extension: +4 (hard 12)** if the user explicitly says "deep dive" or equivalent.
- When the cap is reached without the user having said any finalize trigger → Error #7: force-show the full current draft proposal.md and ask "finalize to lock `status: ready`, or 'deep dive' to extend +4?". **Do not auto-advance** (B4).
- **Finalize trigger**: the user says any of `finalize` / `done` / `ready` / `lock it` / `approve` (case-insensitive substring match — 5-word normalized set shared with /visual-spec). Then and only then, flip `status: draft → status: ready` in frontmatter. Print the §Handoff line and stop.

## Skill bans

Rules the agent running this skill MUST follow. Each: rule / consequence if violated / remedy.

| # | Rule | Consequence | Remedy |
|---|---|---|---|
| **B1** | No pixel-level tool calls. Forbidden: `generate_image`, `create_artwork`, `inpaint_artwork`, any `layers_*`, `evaluate_artwork`. | Breaks zero-pixel promise; Week-1 shippability lost | Whitelist: `view_image`, `list_traditions`, `search_traditions`, `get_tradition_guide`, `Read` (only for `--tradition-yaml`). |
| **B2** | No hidden brief. Even if user says "just go", finalize MUST show full draft + wait for explicit confirm. | Vibe-spec anti-pattern; downstream burns tokens on misaligned intent | User may shorten `## Intent`; `## Acceptance rubric`, `## Open questions`, frontmatter MUST display in full. |
| **B3** | Tradition declared ⇒ `## Acceptance rubric` MUST appear (L1-L5 template; tradition-guide MAY override strength). | Vulca moat artifact missing | If user insists "no rubric", set `tradition: null` first — consistent declaration, not bypass. |
| **B4** | No auto-advance status. `draft → ready` ONLY on explicit user trigger (any of `finalize` / `done` / `ready` / `lock it` / `approve` — 5-word normalized set). | Unverified draft consumed downstream; resume broken | At cap, present draft and ask; never flip status automatically. |
| **B5** | Scope-check first; no out-of-scope brainstorm. Hard-exclude hit → redirect + terminate (no turn cap increment). | Skill props up a domain it cannot win | Fuzzy → first-Q disambiguate. Edge-accept → log `scope-accept rationale` in `## Notes`. |
| **B6** | No parallel invocation on same slug. | File race; state corruption; resume broken | Detect via `updated` timestamp vs now; reject second call; user renames slug. |
| **B7** | `frontmatter.tradition` MUST be enum-id or YAML literal `null`. Forbidden strings: `"N/A"`, `"none"`, `"null"`, `""`, `"unknown"`. | `if tradition:` truthy fails → rubric silently omitted → moat artifact missing | Self-assert before write: "tradition is enum-id or YAML null?" |

## Error matrix

| # | Signal | Response |
|---|---|---|
| 1 | Slug collision; existing `proposal.md` has `status: ready` | Print exactly: `already finalized at <path>; branch with -v2 or pick new slug`. Terminate. Do not overwrite. (Verbatim per §Handoff convention — downstream tooling may grep for this string.) |
| 2 | Slug collision; existing has `status: draft` | Resume path (A6): read `## Open questions`; continue loop; turn cap accumulates. |
| 3 | Unknown tradition (not in `list_traditions` + no `--tradition-yaml` match) | Prompt: (a) ask for `--tradition-yaml <path>`; (b) set `tradition: null` + freeform in `## Notes`; (c) if user insists on undefined id, treat as `null` + warn "rubric omitted, tradition unvalidated". Never fabricate enum id. |
| 4 | `--tradition-yaml` unreadable (FileNotFoundError / YAML parse / schema) | Print `tradition-yaml at <path> invalid: <err>`. Fall through to Error #3. Do not auto-retry. |
| 5 | `--sketch` unreadable / `view_image` fails | Print `sketch at <path> unreadable: <err>. Proceeding text-only.` Degrade; do not charge turn cap. |
| 6 | User requests pixel action mid-dialogue | Print "I don't generate images; I finalize the brief. After finalize, run /visual-spec then downstream pixel tools." Do not call B1 tools. Does not count toward cap. |
| 7 | Turn cap reached without user finalize | Force-show draft + prompt "finalize or deep dive". Do not auto-finalize (B4). |
| 8 | Scope hard-reject + user pushback | Explain once. Second pushback → terminate silently. |

**Do-not-auto-retry**: Errors #3, #4, #8. **Do-not-overwrite**: Error #1, Error #6.

## Handoff

On finalize (status: draft → ready), print exactly:

> `Ready for /visual-spec. Run it with \`/visual-spec <slug>\`.`

Do NOT auto-invoke `/visual-spec`. Human-in-the-loop gate is preserved here.

## References

- Design spec: `docs/superpowers/specs/2026-04-21-visual-brainstorm-skill-design.md`
- L1-L5 cultural evaluation academic anchors: EMNLP 2025 Findings VULCA (`aclanthology.org/2025.findings-emnlp.103/`); VULCA-Bench (`arxiv.org/abs/2601.07986`)
- Sibling skill for tone/rigor baseline: `decompose`
