# MCP `decompose` skill + hardening

**Date**: 2026-04-19
**Scope**: one focused session (~2.5h implementation after spec + plan approval — revised up from initial 30-60 min estimate after review surfaced that `test_decompose_smoke.py` mocking alone takes ~60 min; ~2.5h matches the per-step budget totals in the Implementation sequencing section with modest slack for context-switching/rework)
**Status**: design approved; implementation plan pending

## Context

Vulca's thesis is agent-native: Claude Code is the brain, the SDK is hands+eyes, no LLM inside the library. After shipping four Xiaohongshu + X carousels and publishing `docs/agent-native-workflow.md`, the workflow is documented but not reachable as a tool. Users reading the repo cannot invoke the pipeline via a slash command or natural-language instruction.

The existing `layers_split(mode="orchestrated", ...)` MCP tool in `src/vulca/mcp_server.py:607-652` already provides in-process access to the typed `vulca.pipeline.segment.run` entry point. The work here is to make that tool discoverable and safe as a Claude Code skill, plus fix three pipeline-level hazards surfaced during the review.

## Non-goals

- Do not refactor `scripts/claude_orchestrated_pipeline.py` into `src/vulca/pipeline/segment/*` stages (2-3 day job, separate session).
- Do not add a new `decompose` MCP tool as an alias; the skill will call `layers_split(mode="orchestrated")` directly. (Avoids tool-surface creep beyond the v0.16 20-tool surface.)
- Do not run the 47-image showcase regression in the test suite.
- Do not attempt to enforce `decomp_validator` coverage/overlap invariants in the orchestrated path (known gap; documented, out of scope).
- Do not fix `cop.ORIG_DIR` module-global race condition (requires orchestrator refactor; document in skill as "never dispatch two calls in parallel").

## Architecture

```
User input
  │
  ▼  (Claude Code skill system)
.claude/skills/decompose/SKILL.md             [NEW]
  │
  ▼  (Claude reads image, authors plan)
layers_split(mode="orchestrated", plan=...)   [EXISTS, mcp_server.py:607]
  │
  ▼  (typed Plan validation)
vulca.pipeline.segment.run(plan, image, out)  [EXISTS, orchestrator.py:94]
  │
  ▼  (via _import_cop helper)
scripts/claude_orchestrated_pipeline.py       [EXISTS]
  ├── load_grounding_dino  ─┐
  ├── load_yolo             │  @lru_cache + threading.Lock  [NEW]
  ├── load_face_parser      │
  └── _load_sam_model       ─┘
```

Changes:

- **New**: `.claude/skills/decompose/SKILL.md` — discoverable skill with frontmatter (`name: decompose`, `description: ...`) + agent instructions + minimal plan template + decision tree + failure-mode table + explicit rules preserving Phase 1.11 invariants.
- **New**: `_import_cop()` helper in `src/vulca/pipeline/segment/orchestrator.py` — factors the `sys.path` manipulation + `import claude_orchestrated_pipeline as cop` into a reusable function. Used by the orchestrator and by the new `unload_models` tool.
- **New**: `unload_models` MCP tool in `src/vulca/mcp_server.py` — calls `_import_cop().load_*.cache_clear()` on the four loaders, then `gc.collect()` and `torch.mps.empty_cache()` in a try/except. Returns `{"status":"ok","cleared":<count>}`. Exposed via MCP schema (agents can call it) but not promoted in README or user-facing docs; docstring marks it as diagnostic. Tool surface grows from 20 to 21; acceptable because the previous 20-tool promise applied to content-facing tools, not admin tools.
- **Modify**: `scripts/claude_orchestrated_pipeline.py` — add module-level `_MODEL_LOCK = threading.Lock()`, wrap the bodies of the four `@lru_cache`d loaders at decorator lines **85 (`load_grounding_dino`), 95 (`load_yolo`), 119 (`load_face_parser`), 401 (`_load_sam_model`)** in `with _MODEL_LOCK:`. One lock shared across all four. Note: line 408 hosts `def load_sam(...)` which is an *uncached wrapper* around `_load_sam_model` — do not attempt to wrap or clear it; it delegates to the cached 401 function.

## Data flow + decision tree

After `layers_split(mode="orchestrated", plan=...)` returns, the skill tells Claude to walk the branches below in order and take the first match:

### Per-entity signals (highest priority; entity-level beats aggregate)

| Branch | Condition | Fix |
|---|---|---|
| A | any `detection_report[entity].status == "missed"` | rewrite label or switch detector |
| B | any `detection_report[entity].status == "suspect"` (driven by `empty_mask`, `low_bbox_fill`, `mask_outside_bbox` — sam_bbox only) | adjust `bbox_hint_pct` or tighten label |
| C | any layer has `quality_flag == "area_ballooned"` (pre 0.01%-0.5% AND post > pre×3) | tighten bbox or raise threshold |
| D | any layer has `quality_flag == "over_eroded"` (pre > 0.1% AND post/pre < 0.5) | promote `order: 10` or move semantic_path to `foreground.*` |
| E | any person has `quality_flag == "face_parse_skipped"` AND that person's `pct > 3%` | head+body split (*exactly two* entities per occluded person, one head-bbox + one body-bbox, post-composited with PIL `alpha_composite`) OR crop face region + 2× upscale + brightness rescue. **Note**: two-entity head+body split is allowed because face-parsing never ran; the E3 ban below (never split a person into head/torso/limbs) applies when face-parsing DID run and `body_remainder` was auto-generated. |

### Delta-residual guard (prevents over-decomposition)

| Branch | Condition | Fix |
|---|---|---|
| F | residual layer exists AND `residual.pct > prev_residual.pct + 1pp` | revert to prior entity set; do not continue decomposing that region |

### Residual-driven additions (only if per-entity + delta checks pass)

| Branch | Condition | Action |
|---|---|---|
| G | residual layer exists AND `pct > 20%` | inspect residual PNG, add missing entity |
| H | residual layer exists AND `pct` in 5-20% | judgment: add if payoff clear |
| I | residual layer absent OR `pct < 5%` | STOP adding entities |

### Honesty signal

| Branch | Condition | Action |
|---|---|---|
| J | `detection_report["warning"]` present (requested > 2 AND hint ratio > 0.5) | surface to user; plan is hint-heavy and fragile |

### Face-parse rescue ladder (triggered when per-person sub-part count < 6)

The pipeline does not return `face_parts_count`; the skill instructs Claude to **count layers** in the returned `layers` array whose `semantic_path` starts with `subject.person[N].` followed by one of {eyes, nose, lips, eyebrows, ears, hair, neck, skin, cloth, hat}. If any person's count < 6 AND Claude judges the face crop small or dark (Read tool on the original image), try in order, accepting only when the count increases after re-decomposition of the cropped slug:

1. Crop the face region to a new slug + re-decompose.
2. Add 2× upscale to that crop.
3. Add ~20% brightness/contrast boost.

The `face_parse_skipped` flag is a separate signal — it fires only when SegFormer returns zero parts, not when results are sparse.

### Hard iteration cap

- 5 `layers_split` calls per source image.
- OR early stop if previous iteration improved residual by less than 2 percentage points.

## Error matrix

### MCP input errors (exact strings from `mcp_server.py`:620/627/629)

| Code | Error string | Skill guidance |
|---|---|---|
| A1 | `"pass either plan (inline JSON) or plan_path, not both"` | fix call, pass one |
| A2 | `"orchestrated mode requires 'plan' (inline JSON) or 'plan_path'"` | author plan, retry |
| A3 | `"plan validation failed: <any exception>"` — catches all Pydantic + JSON errors | read message, fix specific field |

### Runtime exceptions (returned as `{"error":"pipeline error: <Type>: <msg>"}`)

| Code | Trigger | Retry policy |
|---|---|---|
| B1 | `MemoryError` | combine: call `unload_models()`, reduce image to ≤2 MP (resize or crop), reduce to 2-3 entities — retry once |
| B2 | `ConnectionError`, `HTTPError` (HuggingFace weights) | report to user, no auto-retry |
| B3 | `RuntimeError` from Torch/MPS | one soft retry after `unload_models()`; escalate to session restart if recurs |
| B4 | `PermissionError` (output_dir read-only) | tell user to change output_dir, no retry |
| B5 | `FileNotFoundError` on image_path | verify path, no auto-retry |
| B6 | PIL/format decode error (WebP, HEIC) | suggest conversion to PNG/JPG |
| B7 | Any other Exception | report full type + message, no auto-retry |

### Normal return with bad status

Status enum per `context.py`: `{ok, partial, error, skipped, unknown}`.

| Code | Condition | Skill guidance |
|---|---|---|
| C1 | `status == "partial"` | iterate per decision tree; per-entity fixes first |
| C2 | `status == "error"` — read `reason` field (`image_load: ...` or `pipeline produced no manifest`) | route to B5/B6 or stop |
| C3 | `status == "skipped"` | cached manifest returned; ensure `force=True` when retrying |
| C4 | `status == "unknown"` | manifest missing status; treat as error |
| C5 | all `entity.status == "missed"` | retry once with swapped `domain` first, then with rewritten labels |

### Skill-enforced bans (pipeline does not reject these; skill must)

- **E1**: do not author separate face-part entities per person. Phase 1.11 sibling-mask only fires inside `face_person_N` parent. Declare `subject.person[N]`; face parts auto-generate.
- **E2**: do not place a foreground object that overlaps a person under `background.*`. The person-overlap leak-fix skips entries starting with `background`.
- **E3**: do not manually split a person into 3+ entities (head/torso/limbs). `body_remainder` is only auto-generated when `subparts_kept` is populated by face-parsing. The Branch E two-entity head+body rescue is the *only* manual split allowed — it applies when face-parsing itself failed (`face_parse_skipped`), so no `body_remainder` exists to preserve.
- **E4**: when `detection_report["warning"]` fires (hint-heavy plan), surface to user — do not silently iterate.

### Static hazards worth documenting

- **F3 output-dir clobber** (orchestrator.py:214-219): existing output_dir files are deleted before copy-from-staging. If the copy fails midway, previous good output is destroyed. Skill warns users to back up important outputs before re-decomposing the same slug.
- **F4 `cop.ORIG_DIR` globals**: parallel `layers_split` calls race on module-level state. Skill forbids parallel dispatch.
- **F2 coverage/overlap unchecked**: `decomp_validator` is dead in the orchestrated path. The skill instructs Claude to sanity-check residual and hidden regions manually.

## Testing

All tests offline-safe, ~6 seconds total.

### New test files

| File | Purpose | Approx runtime |
|---|---|---|
| `tests/test_decompose_smoke.py` | mocked pipeline round-trip (cold → clear caches → reload). Asserts `status=="ok"`, non-empty layers, manifest mtime advances, 2nd-run time bounded. Pattern mirrors `tests/vulca/scripts/test_claude_orchestrated_pipeline.py:149-153`. Also: exact MCP error-string contracts | ~2s |
| `tests/test_import_cop_helper.py` | `_import_cop()` returns `sys.modules["claude_orchestrated_pipeline"]` identity. Thread-safety: 4 concurrent `_import_cop()` calls return the same module id. | ~0.5s |
| `tests/test_skill_discovery.py` | SKILL.md exists; frontmatter parses; `name: decompose`; `description` non-empty | ~0.1s |
| `tests/test_import_cop_subprocess.py` | fresh Python subprocess invokes `_import_cop()` correctly — catches `sys.path` drift between pytest harness and runtime | ~3s |
| `tests/test_unload_models.py` | mocks `cache_clear` on four loaders, asserts all invoked + structured response | ~0.5s |

### Existing regression

- `tests/vulca/scripts/test_claude_orchestrated_pipeline.py` must stay green. The `threading.Lock` addition does not serialize any existing test (no test calls loaders concurrently; all monkeypatch the loaders before `cop.process()`).
- The `_MODEL_LOCK` itself is not under automated test this session (would require a synthetic fake loader with `time.sleep` to prove serialization). It is covered by static review only. Follow-up test could be added via `@pytest.mark.slow` once that marker exists.

### Deliberately out of scope

- Full 47-image regression.
- Real model loads (HuggingFace download dependency).
- Real OOM or MPS error triggering.
- Parallel dispatch on `cop.ORIG_DIR` (skill forbids; no runtime fix this session).

### Acceptance

All 5 new test files green + existing `test_claude_orchestrated_pipeline.py` green. All pytest targets offline-safe (total ~6s).

The optional live sanity run `python3 scripts/claude_orchestrated_pipeline.py trump-shooting` is a *post-landing smoke step* run manually, NOT a gate. It lives outside the pytest boundary and is done after merge as part of human verification, not as part of the commit gate.

## Implementation sequencing

Landing order with per-step verification checkpoint. Each step must stay green before moving to the next.

1. **`_import_cop()` helper** in `orchestrator.py`. Refactor the existing `import claude_orchestrated_pipeline as cop` pattern (orchestrator.py around line 171) into a module-level helper. Existing `orchestrator.run(...)` migrated to use the helper.
   - **Check**: `pytest tests/vulca/scripts/test_claude_orchestrated_pipeline.py` still green.

2. **`tests/test_import_cop_helper.py`** (unit) + **`tests/test_import_cop_subprocess.py`** (subprocess). Both offline, no model touch.
   - **Check**: both pass in <5s total.

3. **Threading.Lock** on four `@lru_cache`d loaders in `scripts/claude_orchestrated_pipeline.py` (decorator lines 85, 95, 119, 401). Module-level `_MODEL_LOCK`, body-wrapped, one lock total.
   - **Check**: existing test_claude_orchestrated_pipeline.py still green (lock is invisible when loaders are monkeypatched).

4. **`unload_models` MCP tool** in `mcp_server.py`. Uses `_import_cop()`. Returns `{"status":"ok","cleared":<n>}`.
   - **Check**: `tests/test_unload_models.py` pass.

5. **`tests/test_decompose_smoke.py`** (mocked). The heaviest single item — ~60 min estimated because monkeypatching four loaders + Stage 1/2/3 fakes + error-string contract assertions is fiddly.
   - **Check**: `pytest tests/test_decompose_smoke.py` green (scoped to this one new file — does NOT include `tests/test_skill_discovery.py`, which needs step 6's SKILL.md file).

6. **`.claude/skills/decompose/SKILL.md`**. Create directory, write frontmatter + agent instructions + decision tree + failure-mode table + E1-E4 bans + minimal plan template.
   - **Check**: `tests/test_skill_discovery.py` pass.

7. **Commit**. All 5 new tests + existing suite green, skill file present.

8. **Post-landing manual smoke**: `python3 scripts/claude_orchestrated_pipeline.py trump-shooting` produces a valid manifest.

**Budget allocation** (total ~2.5h, including slack):
- Steps 1-2: 20 min (refactor + 2 offline tests)
- Step 3: 10 min (mechanical lock wrap)
- Step 4: 15 min (new MCP tool)
- Step 5: 60 min (smoke test mocking — heaviest item)
- Step 6: 30 min (SKILL.md drafting — the other content-heavy item)
- Commit + live smoke: 15 min
- **Slack / rework buffer**: 30 min
- Subtotal: 180 min = 3h hard ceiling before escape hatch kicks in

If step 5 exceeds 90 min (wall clock, not cumulative), defer it with `@pytest.mark.xfail` and ship the other 6 steps. Do not let smoke-test scope creep eat skill delivery.

## Open questions

None as of spec-write. Both reviewer rounds resolved all ambiguities. If the `_import_cop` subprocess test surfaces a real sys.path mismatch during implementation, revisit.

## Out-of-scope work to track elsewhere

1. **GitHub Actions CI** — the repo has no `.github/` directory. Every change risks silent regression. Minimum viable workflow (pytest on push to master) should follow this change in a separate PR.
2. **Add `@pytest.mark.slow` + `--run-slow`** marker — opt-in gate for future real-model integration tests. Pattern exists (`real_provider` in `tests/conftest.py:14-46`).
3. **Orchestrator refactor** — lift `scripts/claude_orchestrated_pipeline.py` contents into `src/vulca/pipeline/segment/stages.py` so `cop.ORIG_DIR` globals go away and parallel dispatch is safe. 2-3 day effort.
4. **`decomp_validator` wiring** — plug coverage/overlap invariant check into the orchestrated path. Prevents silent-bad-output failure F2.

## Credit

Review rounds: codex:codex-rescue + superpowers:code-reviewer, four rounds (data-flow → error-handling → tests → import strategy). All identified bugs and contract corrections folded into the spec above.
