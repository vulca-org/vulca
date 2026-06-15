# Project Overview

Vault status: synthesis with source-backed boundaries.

## Current Integrated Thesis

VULCA should be understood as:

> Workspace-first, protocol-backed, agent-enabled creative control for
> AI-native visual teams.

The product center is the Workspace / Creative Repo model. The SDK and MCP
tools are the execution engine. The website is the public trust and acquisition
surface. The PPT work is an internal proof and packaging lab until its quality
gates pass.

## Product Layers

### 1. Workspace Product Layer

Primary object:

- `CreativeRepo`
- `Brief`
- `MotifBranch`
- `VisualVariant`
- `ReviewRequest`
- `EvidencePack`
- `ReleaseGate`
- `AgentRun`

This layer is implemented in the `vulca-platform` Workspace branch and should
be the center of future product explanations.

### 2. Protocol And Execution Layer

This is the `vulca` Python SDK / MCP project:

- visual discovery, brainstorm, spec, plan
- decompose
- evaluate
- generate
- inpaint
- layer split, edit, redraw, composite, export, pasteback
- provider routing
- L1-L5 cultural and visual evaluation
- artifact and case logging

### 3. Website Layer

`vulcaart.art` should explain the product, establish trust, route visitors to
pilots/partners/research, and point to the Workspace demo. It should not expose
raw run IDs or internal proof logs as the main story.

### 4. PPT Proof Lab

The PPT branch is a usecase-to-deck proof lab. It contains valuable design
memory, QA gates, and usecase briefs, but current outputs are public blocked.
It must be mined selectively, not merged wholesale.

## Important Boundary

Agents are collaborators and operators inside VULCA. Agents are not VULCA.

The durable VULCA asset is the artifact, review, evidence, and release model
that agents and external tools operate through.

## Sources

- `README.md`
- `docs/product/2026-04-30-product-positioning-brief.md`
- `docs/product/roadmap.md`
- `docs/product/provider-capabilities.md`
- `source-index.md` Workspace section
- `source-index.md` Website section
- `source-index.md` PPT Proof Lab section
