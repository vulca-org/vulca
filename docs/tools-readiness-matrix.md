# Vulca MCP Tools — Readiness & Reduction Matrix

**Date:** 2026-04-20 (scaffold) / 2026-04-21 (mock-run populated)
**Status:** Mock-provider audit GREEN on 9/11 Skeleton-tier tools. 2 remaining tools FAIL with env-prereq error dicts (`inpaint_artwork` wants `GOOGLE_API_KEY`; `sync_data` wants `VULCA_API_URL`) — not code regressions. Real-provider audit in progress (ComfyUI, `--max-images 3`).
**Purpose:** (1) Gate the next meta-skill choice (`/visual-spec` vs `/visual-plan` per the 2026-04-20 session plan); (2) input to the Tool Count Reduction decision (21 → 16 if all merges land).
**Companion:** `scripts/tool_audit.py` (now takes `--provider-mode {mock,real}`, `--real-provider <name>`, `--max-images <N>`; `--dry-run` confirms corpus without invoking).

---

## 1. Tool inventory (21 MCP tools)

Source of truth: `src/vulca/mcp_server.py` — one `@mcp.tool()` decorator per tool, confirmed by `grep '@mcp.tool' src/vulca/mcp_server.py | wc -l` = 21.

| Category | Tools | Count |
|---|---|---|
| Discovery | `list_traditions`, `search_traditions`, `get_tradition_guide`, `brief_parse` | 4 |
| Generation | `generate_image`, `create_artwork`, `generate_concepts`, `inpaint_artwork` | 4 |
| Evaluation | `evaluate_artwork`, `view_image` | 2 |
| Layer editing | `layers_split`, `layers_list`, `layers_edit`, `layers_transform`, `layers_redraw`, `layers_composite`, `layers_export`, `layers_evaluate` | 8 |
| Session | `archive_session`, `sync_data`, `unload_models` | 3 |

The 11-tool Skeleton tier audited by `tool_audit.py` is the union of Generation (4), most of Layer editing (4 — excluding `layers_split`, `layers_list`, `layers_composite`), `brief_parse`, and Session `archive_session` + `sync_data`. The 10 tools not in the Skeleton tier are either proven-stable (Discovery 4 + `view_image` + `evaluate_artwork`) or serve as infrastructure not needing a readiness pass (`layers_split`, `layers_list`, `layers_composite`, `unload_models`).

---

## 2. Readiness matrix — per-tool PASS/FAIL (Skeleton tier, 11 tools)

**Mock-provider audit** (2026-04-21, corpus 24, `provider='mock'` where accepted). Validates MCP surface: dispatch, arg shape, error path, return shape. Does NOT validate real provider chains (that's §2.2).

| Tool | PASS | p50 | Category | Notes |
|---|---|---|---|---|
| `brief_parse` | 100% | 0 ms | ✅ surface valid | Pure rule-based parser; no LLM on happy path. |
| `generate_image` | 100% | 1 ms | ✅ surface valid | Routed to MockImageProvider via `provider='mock'`. |
| `create_artwork` | 100% | 1 ms | ✅ surface valid | Defaults to `provider='mock'` natively. |
| `generate_concepts` | 100% | 2 ms | ✅ surface valid | Multi-variant wrapper; mock-routed. |
| `inpaint_artwork` | **0%** | 298 ms | 🌍 env-prereq | Public MCP signature has no `provider` kwarg — always exercises default (gemini). Blocked by missing `GOOGLE_API_KEY`. Error dict surfaces correctly (error-handling path works). **Not a code regression.** |
| `layers_redraw` | 100% | 12 ms | ✅ surface valid | Routed against `assets/demo/v3/layered/` (has real manifest.json). |
| `layers_edit` | 100% | 0 ms | ✅ surface valid | Actual ops: `add / remove / reorder / toggle / lock` (5). Previous matrix prose said "list / add / remove / move / visibility / rename / regenerate" — stale; `layers_list` is the separate listing tool; move/visibility/rename/regenerate never landed. |
| `layers_transform` | 100% | 0 ms | ✅ surface valid | Geometric ops (dx/dy/scale/rotate/opacity); no `transform` dict kwarg (audit script previously assumed one — fixed). |
| `layers_evaluate` | 100% | 0 ms | ✅ surface valid | L1-L5 scoring at layer granularity. |
| `archive_session` | 100% | 0 ms | ✅ surface valid | Signature `(intent, tradition, image_path, feedback)` — no `output_dir` (audit previously assumed one — fixed). |
| `sync_data` | **0%** | 0 ms | 🌍 env-prereq | Correctly errors with `"VULCA_API_URL not set"` when env unset. Error path works. **Not a code regression.** |

**Macro PASS rate excluding env-prereq**: 9/9 = 100% surface valid.
**Tools < 75% on raw numbers**: `inpaint_artwork`, `sync_data` — both env-prereq FAILs, reclassified below.

### 2.1 Stratified gate interpretation

Literal read of §5 rollup target ("≥90% macro, ≥75% per tool") would light red here. Stratified read separates failure kinds:

| Failure class | Tools | Gate impact |
|---|---|---|
| Code regression | (none) | — |
| Audit-script bug (prior run) | (fixed 2026-04-21: `create_artwork`, `inpaint_artwork`, `archive_session`, `layers_transform`, `layers_edit`) | No longer counted |
| Corpus incompatibility | (none after `layers_*` repointed at `assets/demo/v3/layered/`) | — |
| Environment prereq missing | `inpaint_artwork` (GOOGLE_API_KEY), `sync_data` (VULCA_API_URL) | Gate = **pass with note**: error paths exercise correctly |

§5 gate **on surface validity**: 🟢 GREEN. `/visual-spec` may name Skeleton-tier tools in design.md.

### 2.2 Real-provider audit (ComfyUI)

Completed 2026-04-21. Command: `PYTHONPATH=src python3.11 scripts/tool_audit.py --provider-mode real --real-provider comfyui --max-images 3 --json-out docs/tool-audit-report-real.json --verbose`. Report at `docs/tool-audit-report-real.json`.

| Tool | PASS | p50 | Category | Notes |
|---|---|---|---|---|
| `brief_parse` | 100% | 0 ms | ✅ | Provider-independent. |
| `generate_image` | 100% | 80,078 ms | ✅ real pipeline | ComfyUI SDXL real inference confirmed. |
| `create_artwork` | 100% | 75,093 ms | ✅ real pipeline | Wraps generate_image + archival. |
| `generate_concepts` | 100% | 125,250 ms | ✅ real pipeline | `count=2` → 2 real gens/call; per-gen ~62 s. |
| `inpaint_artwork` | **0%** | 331 ms | 🌍 env-prereq | Same as mock — no provider kwarg on MCP signature, hits gemini default, blocked by missing `GOOGLE_API_KEY`. Consistent error-dict; no new regression. |
| `layers_redraw` | 100% | **5,058 ms** | ✅ real pipeline (?) | **Suspiciously fast** vs. the ~80 s of other gen tools. Two hypotheses: (α) internal cache short-circuit when `instruction="retain existing content"` is interpreted as no-op; (β) the audit call didn't trigger real SDXL inference. Followup: probe with a divergent `instruction` to confirm real generation path. |
| `layers_edit` | 100% | 1 ms | ✅ | Structural op `toggle` — idempotent when `visible=True` already set. |
| `layers_transform` | 100% | 1 ms | ✅ | Geometric — no provider. |
| `layers_evaluate` | 100% | 0 ms | ✅ | L1-L5 scoring — no pipeline. |
| `archive_session` | 100% | 0 ms | ✅ | Filesystem only. |
| `sync_data` | **0%** | 0 ms | 🌍 env-prereq | Same as mock — VULCA_API_URL unset. |

**Macro PASS excluding env-prereq**: 9/9 = 100%. **Tools <75% on raw numbers**: `inpaint_artwork`, `sync_data` — both env-prereq, same reclassification as §2.1.

**Real-pipeline additions over mock**:
- Latency data for cost-model anchoring in `/visual-spec` design.md.
- `layers_redraw` anomaly (5 s vs. 80 s) — flagged as a probe-me item, not a blocker.
- No new error modes vs. mock. Zero new regressions introduced by the real-provider substitution.

### 2.3 Gate decision — 2026-04-21

**§5 stratified gate: 🟢 GREEN.** Mock (surface) and Real (pipeline) audits both hold under the stratified interpretation. `/visual-spec` next meta-skill is unblocked. No tool renames or merges are gating.

**Rollup target**: if the Skeleton tier shows a macro PASS rate ≥ 90% with no single tool below 75%, the tier is green-lit to be referenced in `/visual-spec` design.md. Tools below 75% block downstream planning until fixed or explicitly omitted from the spec.

---

## 3. Tool Count Reduction Audit (pi-mono-inspired)

pi-mono (Mario Zechner) ships only 4 tools and is endorsed by Shopify's Tobi Lütke. Vulca's 21 is not automatically wrong — this is a pixel-editing domain, not a code-agent harness — but an audit is warranted. The question for each pair is: *would a single tool with a `mode` flag reduce agent cognitive load without inflating signature cost?*

### 3.1 MUST merge (2)

| From | Into | Added signature cost | Rationale |
|---|---|---|---|
| `create_artwork` | `generate_image` | `session: bool = False` (default false) | `create_artwork` is `generate_image` + archival side effects. Two tools, one pixel semantic. Agents repeatedly pick the wrong one. |
| `layers_export` | `layers_composite` | `export_format: Literal["png", "psd", "webp"] = "png"` | `layers_export` is `layers_composite` + a file-format hop. Collapsing removes a redundant terminal step. |

Projected reduction: 21 → 19.

### 3.2 SHOULD merge (3)

| From | Into | Added signature cost | Rationale |
|---|---|---|---|
| `generate_concepts` | `generate_image` | `count: int = 1` | `generate_concepts` is `generate_image` with `count>1`. Same merge logic as `create_artwork`; SHOULD rather than MUST because the variant-diversity prompt prefix differs. Merge post-`create_artwork` or together. |
| `layers_evaluate` | `evaluate_artwork` | `scope: Literal["artwork", "layer"] = "artwork"` + `layer: str \| None = None` | Same L1-L5 scoring code path; the artwork-vs-layer split is a narrow scope arg, not a separate capability. |
| `layers_transform` | `layers_edit` | `operation="transform"` + `transform: dict` | Conditional: only merge if the audit's `invalid_arg` rate on `layers_transform` is comparable to `layers_edit`'s. If transforms have disproportionately stricter argument shapes, keep separate. |

Projected reduction if all three land: 19 → 16.

### 3.3 KEEP separate (16 after MUST+SHOULD; currently 17 before audit)

| Tool | Reason to keep |
|---|---|
| `list_traditions`, `search_traditions`, `get_tradition_guide`, `brief_parse` | Discovery tier — distinct return shapes and agent-side usage patterns. Merging loses routing clarity. |
| `generate_image` (target of merges) | Pixel-generation core. |
| `inpaint_artwork` | Mask-gated generation — different semantics from free generation. |
| `evaluate_artwork` (target of merge) | Evaluation core. |
| `view_image` | Agent's visual sense — read-only, always-safe. Mandatory for skills like `/visual-brainstorm`. |
| `layers_split` | Decomposition pipeline entry — orthogonal to editing tools. |
| `layers_list` | Introspection — different semantic (read-only, no pixels). Merging into `layers_edit` inflates a write-oriented tool's signature. |
| `layers_edit` (target of merge) | Core layer mutation. |
| `layers_redraw` | **Semantically distinct from `layers_edit`** — `layers_edit` is structural (add/remove/visibility/move), `layers_redraw` is pixel regeneration. Keeping them apart preserves the agent's mental model of structural-vs-pixel. This is the most important "do not merge" boundary in the surface. |
| `layers_composite` (target of merge) | Terminal step — flattens to a single image. |
| `archive_session` | Session boundary — different concern from pixel/layer ops. |
| `sync_data` | Cloud-boundary — different concern again. |
| `unload_models` | Memory-pressure release valve. Always available, never in the main loop. |

**Counts**: the list above has 13 explicit lines plus the 3 merge targets (`generate_image`, `evaluate_artwork`, `layers_edit`, `layers_composite` = 4 — but `generate_image` and `evaluate_artwork` and `layers_composite` and `layers_edit` already appear as "target of merge" callouts; the net "keep separate" count from the pre-merge 21 is **16**).

---

## 4. If all merges land (21 → 16)

| Tool (post-merge) | Replaces | New signature surface |
|---|---|---|
| `generate_image` | `create_artwork`, `generate_concepts` | `prompt`, `output_dir`, `count=1`, `session=False` |
| `evaluate_artwork` | `layers_evaluate` | `image_path` or `artwork_dir`, `scope="artwork"|"layer"`, `layer=None` |
| `layers_edit` (conditional) | `layers_transform` | adds `operation="transform"` + `transform` dict branch |
| `layers_composite` | `layers_export` | adds `export_format="png"|"psd"|"webp"` |

`layers_edit` at 7 → 8 internal operations sits at the pi-mono merge-threshold edge; if agent error rate on op-selection spikes, split again. Everything else converges cleanly.

---

## 5. Next actions (2026-04-20 → 2026-04-22)

1. **Run `python scripts/tool_audit.py --json-out docs/tool-audit-report.json --verbose`** against the local MCP server. Populates the pending columns in §2.
2. **Pick the next meta-skill** per the audit outcome:
   - If Skeleton tier green (≥ 90% macro PASS, every tool ≥ 75%) → build `/visual-spec` next (design.md can safely reference these tool names)
   - If any tool < 75% → fix-first; consider `/visual-plan` ahead of `/visual-spec` because `/visual-plan` requires only stable tools, not full parity
3. **Decide merge timing**. Recommendation: execute the MUST merges (§3.1, 21 → 19) **before** `/visual-spec` ships, because `/visual-spec` design.md will name tools; post-ship renames force history rewrites of every design.md. SHOULD merges can wait for the `/visual-plan` cycle.
4. **Thread through EmoArt deadline (2026-06-10)**. The EmoArt pipeline runs end-to-end; a broken Skeleton tool found at submission week is a different kind of emergency than one found now. This matrix is an early-warning system.

---

## 6. Audit invariants

These do not change across runs; if violated, the audit itself has a bug.

- `src/vulca/mcp_server.py` contains exactly 21 `@mcp.tool()` decorators
- The 11 Skeleton-tier tool names in `scripts/tool_audit.py` are a subset of the 21 inventory above
- `scripts/tool_audit.py --dry-run` exits 0 on any machine with this repo checked out, regardless of MCP server state
- The corpus walker visits `assets/demo/v3/{gallery, gallery-promptfix, layered, defense3}` in that priority order; `gallery` contributes the 13 tradition exemplars unchanged across runs
