# Website And PPT Claim Spine

Vault status: protected public-story standard.

## Purpose

This file defines the shared claim spine for VULCA's website, README-facing
copy, public one-pagers, investor or partner decks, and internal PPT proof
materials.

The goal is one coherent external story:

```text
VULCA is moving toward a Workspace / Creative Repo product model.
The SDK/MCP layer produces artifacts and evidence.
Workspace organizes review, checks, decisions, and release gates.
The website explains the product and routes pilots or partners.
PPT is an internal proof and packaging lab until its gates clear.
```

This file does not replace `09-claim-boundaries.md`. It applies those boundaries
to the public website and presentation surfaces.

## Shared Public Thesis

Use this as the common top-level claim:

> VULCA is a Creative Repo for AI-native visual work: briefs, motif branches,
> visual variants, evidence packs, and release gates in one reviewable system.

Supporting explanation:

- Agents and MCP tools execute work inside the system.
- SDK/MCP outputs become artifacts, evidence, and review records.
- Human reviewers own release decisions.
- Unsupported public claims remain blocked.

Avoid making agents the product identity. Agents are collaborators and
operators inside VULCA; the durable product is the repo, evidence, review, and
release-control model.

## Audience-Specific Framing

| Surface | Primary audience | Primary job | Boundary |
| --- | --- | --- | --- |
| Website | pilots, partners, researchers, investors | explain product direction and request paths | no raw proof logs as first story |
| README | developers and technical evaluators | explain SDK/MCP and Workspace relationship | no production Workspace claim |
| Product deck | partners, investors, internal strategy | explain market, system, and demo path | qualify preview and internal proof |
| PPT proof lab | internal product/design review | test story, QA, visual proof, and deck workflows | public blocked until fresh gate clears |
| Workspace demo | product reviewers | show review workflow and evidence surfaces | preview-gated without persistence |

## Claim Levels

### Level A: Public Stable

Allowed when the source remains current:

- VULCA has SDK, CLI, MCP, and skill surfaces.
- VULCA supports visual discovery, prompt control, generation, decomposition,
  layer editing, redraw, inpaint, evaluation, archive, and case records.
- VULCA is moving toward a Workspace / Creative Repo product model.
- VULCA can structure creative work through briefs, motif branches, variants,
  evidence packs, review requests, and release gates.

### Level B: Public With Qualification

Allowed only with status language:

- Workspace: preview product direction.
- Website: public positioning surface.
- PPT and deck work: internal proof or gated deck workflow.
- Provider-backed image quality: example-specific and evidence-bound.
- Cultural evaluation: review support, not final cultural authority.
- Redraw or target refinement: implemented contracts with quality evidence.

Required qualifiers:

- preview;
- internal proof;
- public blocked;
- requires human review;
- source-backed;
- gate pending.

### Level C: Internal Only

Use inside planning, vault, review, or product strategy:

- raw run IDs;
- branch names;
- quality-gate failure details;
- private proof logs;
- visual QA critique;
- model/provider troubleshooting;
- blocked deck outputs;
- unreviewed generated artifacts.

### Level D: Blocked

Do not use on the website, in public decks, or in customer-facing copy:

- claims of production Workspace readiness;
- claims that automated review can approve public release;
- claims that internal PPT outputs are production quality;
- claims that public release is cleared when a gate says blocked;
- claims that AI-assisted labels are human-confirmed.

## Website Spine

The website should follow this order:

```text
1. What VULCA is
2. Why AI-native visual work needs evidence and release control
3. How Creative Repo objects work
4. What SDK/MCP executes under the surface
5. What the preview demo path shows
6. Who should contact VULCA
```

### Website First Screen

First-viewport signal:

- VULCA name;
- Creative Repo / Workspace direction;
- review, evidence, and release-control language;
- one strong product visual or demo scene;
- pilot/partner/research routes.

Do not lead with:

- branch names;
- raw proof logs;
- dense tool lists;
- PPT run numbers;
- unsupported production claims.

### Website Proof Section

Allowed proof blocks:

- SDK/MCP capability overview;
- artifact bridge concept;
- complete demo path;
- one RR4-cleared public example when it remains example-specific;
- internal proof pipeline with boundary language;
- release-gate discipline.

Required boundary copy:

```text
Preview workflow; public release remains gated by human review and stronger
implementation evidence.
```

## PPT Spine

PPT work should use the same product spine as the website, but it can go deeper
into market, proof, and implementation details.

Recommended deck order:

```text
1. Problem: AI-native visual work loses context, evidence, and release control
2. Product: VULCA Creative Repo
3. System: Workspace + SDK/MCP + Artifact Bridge
4. Demo: brief -> variant -> evidence -> human decision -> gate
5. Proof: implemented SDK/MCP capabilities and internal proof lab
6. Boundary: preview-gated, public blocked where relevant
7. Ask: pilot, partner, research, or investment route
```

## PPT Proof Lab Rules

The PPT proof lab is useful for:

- claim-spine testing;
- story structure;
- deck visual QA;
- renderer and layout experiments;
- comparison prompts;
- proof that VULCA keeps blocked outputs blocked.

The PPT proof lab is not public evidence for polished deck generation until a
fresh visual quality gate clears the specific artifact.

Use this label:

```text
Internal proof lab: valuable for story and gate discipline; public release
blocked until a fresh visual quality gate passes.
```

## Shared Demo Language

Use `12-complete-demo-path.md` as the shared example across website and decks.

Allowed short version:

```text
A brief enters VULCA, becomes a motif branch and visual variant, gathers SDK/MCP
evidence, enters Workspace review, and stays behind a human release gate.
```

Allowed longer version:

```text
Brief -> MotifBranch -> VisualVariant -> AgentRun -> EvidencePack ->
ReviewRequest -> human decision -> ReleaseGate.
```

Required release boundary:

```text
public_ready=false until a human-owned release workflow clears the blockers.
```

## Copy Blocks

### Homepage Hero

Use:

```text
VULCA is a Creative Repo for AI-native visual work.
```

Support:

```text
Briefs, motif branches, visual variants, evidence packs, and release gates in
one reviewable system.
```

### Technical Proof

Use:

```text
The SDK/MCP layer executes discovery, generation, decomposition, redraw,
evaluation, and archive workflows. Workspace organizes the outputs for review.
```

### Release Control

Use:

```text
Agent and system checks can flag, recommend, and block. Human reviewers own
release decisions.
```

### PPT Boundary

Use:

```text
The deck workflow is an internal proof lab until visual quality gates clear a
specific public artifact.
```

## Translation Rule

English and Chinese website/PPT copy may differ in phrasing, but the claim
level must remain identical. A Chinese phrase cannot upgrade a preview claim
into a production claim. An English deck cannot downgrade a blocked gate into an
implicit approval.

Every bilingual surface should preserve:

- Creative Repo / Workspace as the product center;
- SDK/MCP as execution layer;
- evidence packs and release gates;
- human-owned release decisions;
- preview/internal/public-blocked status where required.

## Review Checklist

Before publishing website copy or PPT slides:

- Does the story start from Workspace / Creative Repo rather than agents alone?
- Does SDK/MCP appear as execution and evidence, not the whole product?
- Are PPT proof-lab outputs clearly internal or gated?
- Does any public example trace to the complete demo path or source-backed
  evidence?
- Are provider-backed visual quality claims qualified?
- Are cultural evaluation claims framed as review support?
- Does every release claim preserve human review?
- Are blocked artifacts still described as blocked?

## M4 Acceptance Criteria

M4 is satisfied when:

- the website, README, PPT, and Workspace demo all use the same product spine;
- public copy uses Level A or Level B claims only;
- PPT proof-lab material is labeled internal or gated;
- `12-complete-demo-path.md` is the shared demo reference;
- every public scenario keeps release boundary language;
- future website/PPT sessions read this file before writing copy.

## Next Milestone

M5 release readiness is specified in
`14-release-readiness-evidence-gate.md`. It should not begin from copy polish.
It should begin from implementation evidence:

- real artifact ingestion into Workspace;
- persistent Creative Repo and review state;
- stable evidence-pack rendering;
- human release workflow;
- fresh visual quality gates for public examples;
- copy reviewed against this claim spine.

## Sources

- `docs/review-context/08-website-and-ppt-boundaries.md`
- `docs/review-context/09-claim-boundaries.md`
- `docs/review-context/10-integration-spine.md`
- `docs/review-context/11-artifact-bridge-spec.md`
- `docs/review-context/12-complete-demo-path.md`
- `origin/master:docs/product/workspace-current-state-audit.md`
- Website branch `codex/vulcaart-film-led-homepage` at platform commit
  `5dc32cd`
- Platform website content:
  `/Users/yhryzy/dev/vulca-platform/wenxin-moyun/src/content/homeCommercial.ts`
- Platform homepage plans:
  `/Users/yhryzy/dev/vulca-platform/docs/superpowers/plans/2026-06-13-vulcaart-film-led-homepage.md`
  `/Users/yhryzy/dev/vulca-platform/docs/superpowers/plans/2026-06-14-vulcaart-flora-method-homepage-redesign.md`
- PPT proof lab source index entry and Run 2.93 public-blocked gate
