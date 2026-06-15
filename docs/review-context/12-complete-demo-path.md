# Complete Demo Path

Vault status: protected demo-path standard.

## Purpose

This file defines the first complete VULCA preview scenario. It is the M3
standard that future Workspace, SDK/MCP, website, and PPT work should reference
when they need one coherent example instead of scattered proof fragments.

The path is:

```text
Brief
  -> MotifBranch
  -> visual plan
  -> generated or imported VisualVariant
  -> SDK/MCP AgentRun evidence
  -> Artifact Bridge record
  -> EvidencePack
  -> ReviewRequest
  -> human decision
  -> ReleaseGate remains blocked or internally approved
```

This is a preview scenario. It proves linkage, evidence discipline, and review
flow. It does not prove production Workspace persistence, hosted ingestion, or
public release readiness.

## Scenario

Use one standard demo project:

```text
Creative Repo:
  VULCA Cultural Key Visual Review

Business task:
  Prepare a campaign key visual for an internal pilot review.

Visual task:
  Generate or import one candidate image, decompose or redraw a target region,
  evaluate cultural and visual fit, and route the result through Workspace
  review checks.

Release state:
  public_ready=false
```

The demo should keep the asset type simple: one static key visual. A static
visual exercises the important VULCA primitives without adding deck, video, or
multi-page complexity too early.

## Object Spine

Use these object names unless implementation constraints require stable IDs:

| Product object | Demo value | Purpose |
| --- | --- | --- |
| `CreativeRepo` | `repo-cultural-key-visual-review` | one review workspace |
| `Brief` | `brief-cultural-key-visual` | task, audience, constraints, success criteria |
| `MotifBranch` | `motif-proof-spine` | selected creative direction |
| `VisualVariant` | `variant-key-visual-v1` | generated or imported candidate |
| `AgentRun` | `agentrun-generate-decompose-evaluate-v1` | SDK/MCP execution trace |
| `EvidencePack` | `evidencepack-key-visual-v1` | reviewer proof bundle |
| `ReviewRequest` | `review-key-visual-v1` | human review workflow |
| `ReleaseGate` | `releasegate-key-visual-v1` | release blockers and decision state |

The implementation may create more granular `AgentRun` records, but it should
still present one readable chain in Workspace.

Reference fixture:

- `artifact-bridge/m3-demo-bridge-fixture.json` records the RR2 canonical
  bridge-to-Workspace projection for this object spine.

## Step 1: Brief

The demo brief should include:

- objective: create an internally reviewed campaign key visual;
- audience: internal creative, evidence, and release reviewers;
- constraints: one static visual, source-backed prompt, no unsupported public
  claims, human release review required;
- claims: draft claim candidates only;
- success criteria: visual clarity, source boundary preserved, L1-L5 review
  available, release blockers visible.

Bridge source:

- visual discovery record;
- brainstorm proposal;
- visual spec;
- manual intake brief text if the asset starts from upload.

Workspace projection:

- `Brief.objective`;
- `Brief.audience`;
- `Brief.constraints`;
- `Brief.claims`;
- `Brief.successCriteria`.

## Step 2: Motif Branch

The selected motif branch should capture the creative direction under review:

- motif contract;
- prompt policy;
- visual language;
- changed-from-main rationale;
- cultural or visual tradition context.

Bridge source:

- `/visual-brainstorm`;
- `/visual-spec`;
- `/visual-plan`;
- `compose_prompt_from_design`;
- tradition guide and L1-L5 rubric.

Workspace projection:

- `MotifBranch.status = in_review`;
- prompt policy is visible in evidence context;
- branch is not treated as release approval.

## Step 3: Candidate Visual

The candidate visual can enter through either path:

### Generated path

```text
generate_image
  -> image_path
  -> provider metadata
  -> prompt refs
  -> bridge record
  -> VisualVariant
```

Required evidence:

- prompt text or prompt reference;
- provider;
- model when available;
- generation parameters that affect output;
- `image_path`;
- cost and latency when available;
- warnings or provider metadata.

### Manual upload path

```text
manual upload intake
  -> file metadata
  -> intake brief
  -> bridge record
  -> VisualVariant
```

Required evidence:

- file name;
- MIME type;
- size label;
- source tool set to upload/import;
- intake brief;
- visible note that browser-session upload metadata is not durable storage in
  the observed preview.

## Step 4: Structure Or Edit Evidence

The demo should include at least one SDK/MCP evidence operation beyond raw
generation or upload.

Preferred minimal path:

```text
layers_split
  -> manifest_path
  -> semantic layer list
  -> detection report when available
  -> decompose bridge record
```

Optional edit path:

```text
layers_redraw
  -> redrawn layer path
  -> source pasteback preview
  -> advisory fields
  -> redraw bridge record
```

Use `layers_redraw` only when the demo needs a targeted edit. Do not make the
first scenario depend on advanced redraw quality unless it has fresh evidence.

Workspace projection:

- `VisualVariant` version context;
- `AgentRun` output paths;
- `EvidencePack` artifact refs;
- `ReviewCheck` warnings or blockers.

## Step 5: Evaluation Evidence

The demo should run or represent `evaluate_artwork` evidence when available:

```text
evaluate_artwork
  -> score
  -> dimensions
  -> rationales
  -> recommendations
  -> risk flags
  -> EvidencePack
```

Evaluation output is review support. It is not final cultural authority or
release approval.

Workspace projection:

- `ReviewCheck.modeId = cultural-review`;
- `ReviewCheck.source = agent` or `system`;
- `ReviewCheck.canSetPublicReady = false`;
- risk flags become blockers or warnings.

## Step 6: Bridge Record

Each meaningful SDK/MCP step should normalize into a bridge record using
`11-artifact-bridge-spec.md`.

Minimum demo record requirements:

- `bridge_record_id`;
- `source_operation`;
- `source_refs.tool`;
- artifact paths as strings;
- provider/model where available;
- prompt refs when available;
- quality or evaluation fields when available;
- `claim_state.public_ready = false`;
- human review labels left empty until a human decision exists.

The demo may use one aggregate bridge record for the first preview if all
source refs remain visible. Later implementations should prefer one record per
operation plus a small rollup record.

## Step 7: Evidence Pack

The EvidencePack should answer reviewer questions without forcing them to open
raw logs first.

Minimum sections:

- brief and motif summary;
- primary visual artifact;
- generation or upload provenance;
- layer/decompose evidence;
- redraw evidence if present;
- L1-L5 or visual evaluation snapshot;
- warnings, blockers, and boundary notes;
- source refs and artifact refs.

The pack should include enough evidence for a reviewer to decide:

- request changes;
- keep blocked;
- approve for internal use with boundary notes.

It should not include a public-release approval unless a future human-owned
release workflow creates one.

## Step 8: Review Request

Create one ReviewRequest:

```text
review-key-visual-v1
  required checks:
    - visual-qa
    - cultural-review
    - release-review
  required roles:
    - Creative reviewer
    - Evidence reviewer
    - Release owner
```

Default decision state:

```text
decision = blocked
humanOverride = ""
```

Allowed human decisions in the preview:

- request changes;
- block release;
- approve internal use with explicit boundary notes.

The preview should not expose a public approval action.

## Step 9: Review Checks

Use three checks:

| Check | Source | Blocks release? | Notes |
| --- | --- | --- | --- |
| Visual QA | agent or human | may block | layout, target fidelity, edit quality |
| Cultural Review | agent or human | may block | L1-L5 evidence, motif risk, source boundary |
| Release Review | human | yes | claim boundary, final owner, public copy status |

Agent or system checks can recommend and block. They cannot set final public
release state.

## Step 10: Release Gate

The demo ReleaseGate starts with:

```json
{
  "publicReady": false,
  "label": "public_ready=false",
  "blockers": [
    "Human release decision required",
    "Public claim copy not approved",
    "Preview artifact ingestion is not production persistence"
  ],
  "finalApprover": "Release owner",
  "boundaryNotes": "Internal pilot review only."
}
```

If a human reviewer approves internal use, the gate can record internal
approval with boundary notes. It should still preserve the public release
boundary unless a later production release workflow exists and is verified.

## Demo Acceptance Criteria

A complete demo path is acceptable when:

- one Brief links to one MotifBranch;
- one VisualVariant links to at least one AgentRun;
- one bridge record preserves source operation, artifact paths, and claim
  state;
- one EvidencePack links to the visible review item;
- visual, cultural, and release checks are visible;
- agent/system checks cannot set final public release state;
- a human decision is required before any release claim changes;
- the release gate visibly remains blocked or internally approved with notes.

## Website And PPT Use

Website copy may use this scenario as:

- a preview workflow example;
- a Creative Repo explanation;
- an evidence and release-control story.

PPT may use it as:

- a product narrative spine;
- an internal proof deck scenario;
- a release-gated example.

Required qualifier:

```text
Preview workflow; public release remains gated by human review and stronger
implementation evidence.
```

Do not use this scenario to claim production Workspace readiness, public
customer deployment, or final cultural/legal approval.

## Implementation Order

### DP1: Static Demo Packet

Create a checked-in JSON/Markdown packet that represents the full path without
running providers.

Acceptance:

- object IDs match this file;
- bridge record validates against the M2 spec;
- release gate starts blocked;
- evidence pack includes source refs.

### DP2: SDK/MCP Sample Export

Generate or import one candidate asset and export bridge records from actual
SDK/MCP outputs.

Acceptance:

- artifact paths exist;
- provider metadata is preserved when available;
- evaluation and warnings are carried into evidence.

### DP3: Workspace Preview Import

Load the demo packet into the Workspace preview.

Acceptance:

- Review Inbox shows one item;
- Single Asset Review shows version/provenance;
- Context Drawer shows evidence on demand;
- Decision Panel preserves advisory-agent boundary;
- release gate label remains visible.

### DP4: Website/PPT Alignment

Use `13-website-ppt-claim-spine.md` and this scenario for public story and
internal deck work with explicit preview-gated language.

Acceptance:

- no unsupported public-readiness claim;
- no raw proof log as first story;
- same object spine appears across README/website/PPT where needed.

## Non-Goals

- Do not add backend persistence in this vault file.
- Do not require live provider calls for the first static demo packet.
- Do not treat automated evaluation as human approval.
- Do not present internal pilot approval as public release.
- Do not mix deck-generation proof output into the first key-visual demo unless
  the deck gate has fresh evidence.

## Sources

- `docs/review-context/10-integration-spine.md`
- `docs/review-context/11-artifact-bridge-spec.md`
- `docs/review-context/07-workspace-product-model.md`
- `docs/review-context/09-claim-boundaries.md`
- `origin/master:docs/product/workspace-current-state-audit.md`
- `src/vulca/mcp_server.py`
- Platform Workspace file:
  `/Users/yhryzy/.config/superpowers/worktrees/vulca-platform/workspace-interactive-demo/wenxin-moyun/src/content/workspaceDemo.ts`
