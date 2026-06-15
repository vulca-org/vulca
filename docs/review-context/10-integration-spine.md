# Integration Spine

Vault status: protected integration memory.

## Purpose

This file is the routing layer for VULCA's scattered workstreams. It defines
how the SDK/MCP, Workspace, website, PPT proof lab, and protected context vault
fit together without turning every branch into a competing product story.

The integration spine is:

```text
VULCA Workspace
  -> owns review workflow and product objects
VULCA SDK / MCP
  -> owns execution, artifacts, and evidence production
VULCA website
  -> owns public explanation, trust, and intake
PPT proof lab
  -> owns internal storytelling experiments and deck-quality gates
Review Context Vault
  -> owns long-lived project memory and claim boundaries
```

## One Product Model

The product center is VULCA Workspace. Everything else should connect to it as
an input, execution layer, proof surface, or memory source.

Core object spine:

```text
Brief
  -> MotifBranch
  -> VisualVariant
  -> AgentRun
  -> EvidencePack
  -> ReviewRequest
  -> ReleaseGate
```

This object spine should be used when planning future work. If a feature cannot
map into this chain, it is probably one of:

- an internal tool improvement;
- a provider capability improvement;
- a website or deck communication asset;
- a vault/context update;
- a blocked or exploratory experiment.

It should not be promoted as a new product category until the mapping is clear.

## Layer Responsibilities

| Layer | Owns | Should not own |
| --- | --- | --- |
| Workspace | Creative Repo, review inbox, asset review, checks, decisions, release gates | provider behavior, raw generation quality, public marketing truth |
| SDK / MCP | discovery, prompt control, provider routing, generate, decompose, redraw, inpaint, evaluate, archive | final public release approval |
| Website | public story, pilot intake, trust, product framing | raw internal run logs, unsupported claims |
| PPT proof lab | internal case packaging, deck experiments, visual QA memory | public proof that VULCA has solved decks |
| Context vault | durable memory, boundaries, source index, request workflow | day-to-day feature code or marketing copy |

## Artifact Bridge

Future integration work should use this bridge instead of inventing a second
ontology:

| SDK / MCP output | Workspace object | Review meaning |
| --- | --- | --- |
| visual discovery record | `Brief`, `MotifBranch` | initial direction evidence |
| brainstorm proposal | `Brief`, `MotifBranch` | direction options and constraints |
| visual spec | `MotifBranch`, `EvidencePack` | source-backed intended form |
| visual plan | `AgentRun`, `EvidencePack` | executable plan and gates |
| generated image | `VisualVariant`, `AgentRun` | candidate asset |
| decomposed layers | `VisualVariant`, `EvidencePack` | inspectable structure |
| redraw / inpaint result | `VisualVariant`, `AgentRun` | proposed edit with non-target preservation claims |
| evaluation result | `EvidencePack`, `ReleaseGate` | review signal, not final approval |
| case record | `AgentRun`, future training record | evidence substrate |
| human decision | `ReviewRequest`, `ReleaseGate` | release or blocker state |

The bridge should preserve source IDs, artifact paths, provider metadata,
prompts, masks, quality warnings, human notes, and claim status. It should not
turn advisory agent output into human confirmation.

## Current State

### Protected context

The vault is branch-only on `codex/vulca-context-vault`. Other sessions may
read it and submit request packets, but direct vault edits belong to a dedicated
context-curator session and must pass the review-context gate.

### Mainline README

`master` now exposes the Workspace direction in the public README through
merge commit `cb6d52fe docs: surface VULCA Workspace product direction`.
That README positions the SDK/MCP tools as the execution layer and Workspace as
the Creative Repo review surface.

### Workspace preview

The user-cited Workspace context baseline is
`6efef07 fix: align workspace context review controls`. The latest observed
local Workspace preview is
`5f4a666 feat: add manual upload intake workflow`.

The preview includes review triage, single asset review, context drawer, typed
checks, decision controls, manual upload intake, and a visible
`public_ready=false` boundary. It is still preview-gated because persistence,
real SDK/MCP artifact ingestion, and production release workflow are not yet
implemented.

### Website

The website should make VULCA legible to users, partners, researchers, and
investors. It should lead with Workspace / Creative Repo framing and explain
why AI-native visual work needs review, evidence, and release control.

It should not lead with internal proof logs, raw branch names, or claims that
PPT/deck generation is production-ready.

### PPT proof lab

The PPT work is valuable because it contains usecase framing, design briefs,
claim spines, visual QA prompts, renderer experiments, and evidence gates. It
remains internal proof material unless a fresh visual quality gate explicitly
clears public release.

Run 2.93 remains public blocked in the current vault memory.

## Decision Rules For Future Sessions

### If working on SDK / MCP

Use the SDK/MCP repository for execution contracts, tests, provider routing,
artifact schemas, and case records. If the work changes product meaning, create
a vault request or update source-index through a curator branch.

Required framing:

- execution layer;
- artifact/evidence producer;
- review support;
- not final release authority.

### If working on Workspace

Use Workspace as the product surface. New UI or data model work should map to
the object spine: `Brief`, `MotifBranch`, `VisualVariant`, `AgentRun`,
`EvidencePack`, `ReviewRequest`, `ReleaseGate`.

Required framing:

- review-first Creative Repo;
- preview-gated until persistence and artifact ingestion are implemented;
- human release decisions remain required.

### If working on website

Read `09-claim-boundaries.md` and `08-website-and-ppt-boundaries.md` before
writing public copy. The website can describe the product direction and review
model, but unsupported internal proof should stay qualified.

Required framing:

- public trust and intake surface;
- Workspace / Creative Repo as the product center;
- SDK/MCP as the execution engine;
- PPT as internal proof unless cleared.

### If working on PPT or decks

Treat the PPT branch as an internal proof lab. Use it for story, usecase, and
QA memory. Do not convert blocked visual outputs into public claims.

Required framing:

- internal proof;
- release-gated;
- public blocked until a fresh gate clears it.

### If working on vault context

Do not edit `docs/review-context/` from ordinary feature sessions. Submit a
request packet under `docs/review-context/requests/` or work from a dedicated
context-curator branch targeting `codex/vulca-context-vault`.

Required framing:

- source-backed synthesis;
- claim boundary preservation;
- gate must pass before merge.

## Integration Milestones

### M0: Protect context

Status: done.

- Vault branch created and protected.
- GitHub rulesets protect `master` and `codex/vulca-context-vault`.
- Review-context gate exists.

### M1: Public README alignment

Status: done on `master` at `cb6d52fe`.

- README exposes Workspace direction.
- `docs/product/workspace-current-state-audit.md` records current Workspace
  state and boundaries on `master`.

### M2: Artifact bridge specification

Status: specified in `11-artifact-bridge-spec.md`.

The protected spec defines how SDK/MCP outputs become Workspace objects. It
covers schema fields, artifact paths, provider metadata, claim status, review
status, and human decision boundaries.

### M3: One complete demo path

Status: specified in `12-complete-demo-path.md`.

The protected demo-path standard defines a single preview scenario:

```text
brief
  -> generated or imported visual
  -> agent run
  -> evidence pack
  -> human review
  -> release remains blocked or internally approved
```

This should be preview-gated until real persistence and SDK/MCP ingestion land.

### M4: Website and deck alignment

Status: next after demo-path standardization.

The website and PPT should share one claim spine:

- what VULCA is;
- what Workspace does;
- what the SDK/MCP executes;
- what evidence exists;
- what remains preview-gated or public blocked.

### M5: Release readiness

Status: blocked until stronger implementation evidence.

Release readiness requires:

- real artifact ingestion into Workspace;
- persistence for Creative Repos and review state;
- stable evidence-pack rendering;
- human release workflow;
- public copy reviewed against claim boundaries;
- fresh visual quality gates for any public examples.

## Non-Negotiable Boundaries

- Agents can advise and operate; they do not own final release.
- Automated evaluation supports review; it does not replace human judgment.
- Provider-backed visual quality must be qualified unless freshly verified.
- PPT outputs are not public-ready while their gate remains blocked.
- Workspace is the product direction, but the observed implementation is still
  a preview.
- The vault is not a scratchpad; it is protected context memory.

## Sources

- `docs/review-context/00-project-overview.md`
- `docs/review-context/02-capability-map.md`
- `docs/review-context/07-workspace-product-model.md`
- `docs/review-context/08-website-and-ppt-boundaries.md`
- `docs/review-context/09-claim-boundaries.md`
- `docs/review-context/PROTECTION.md`
- `docs/review-context/source-index.md`
- `origin/master` commit `cb6d52fe docs: surface VULCA Workspace product direction`
- `origin/master:docs/product/workspace-current-state-audit.md`
- Platform Workspace baseline `6efef07 fix: align workspace context review controls`
- Latest observed local Workspace preview `5f4a666 feat: add manual upload intake workflow`
