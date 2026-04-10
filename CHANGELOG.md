# Changelog

## [0.14.0] - 2026-04-09

### Defense 3 — A-path Reference Image Fidelity
- **Serial-first orchestration:** First layer generates serially (with optional user reference image), its raw RGB output becomes `style_ref` for remaining parallel layers. Cross-layer style consistency without requiring a user-provided reference.
- **Style anchoring:** Remaining layers receive the first layer's output as `reference_image_b64` via `asyncio.gather`, ensuring visual coherence across the composition.
- **Graceful degradation:** If first layer fails, remaining layers proceed without reference (same as v0.13 behavior). Corrupt cached files logged and skipped.
- **Cache-hit fallback:** When first layer is a cache hit (`raw_rgb_bytes=None`), reads cached RGBA, converts to RGB, and uses that as `style_ref`.
- **Pipeline integration:** `_generate_layers_native` resolves reference from context with priority chain (top-level `reference_image_b64` > `composite_b64` > `image_b64` > `node_params`). Legacy B-path unified with same resolution chain.
- **`LayerOutcome.raw_rgb_bytes`:** New field preserves pre-keyed RGB bytes on fresh generation for accurate style reference derivation.
- **SCHEMA_VERSION "0.14":** Layer cache from v0.13 is invalidated on first run.

### Infra
- **mypy advisory config:** 96/135 modules checked, 39 overridden. `pyproject.toml` `[tool.mypy]`.
- **Test baseline cleanup:** 18 pre-existing failures repaired (importorskip guards, flaky event-loop fix, stale release test removed).
- **Retry exception map:** `docs/retry-exception-map.md` documents the two-layer retry architecture and worst-case 12-call amplification.

### Code quality
- `_apply_alpha` accepts numpy array directly (eliminates redundant PIL decode cycle).
- Empty plan guard before resource allocation.
- Pillow 13 deprecation fix (`mode=` parameter removed from `Image.fromarray`).

### Tests
- 18 new tests in `test_layered_style_ref.py` covering serial ordering, style_ref passthrough, user reference chaining, graceful degradation, single-layer plans, cache-hit fallback, empty plans, RGB normalization.

## [0.13.3] - 2026-04-09

### Cleanup Sweep
- **`_call_provider_with_retry`:** Extracted from `generate_one_layer` as standalone function with retry budget, jitter backoff, and exception classification.
- **`_obtain_validation_report`:** Extracted validation/sidecar logic into standalone function with three-branch flow (sidecar hit, sidecar miss, fresh validation).
- **`provider_capabilities()` lookup:** New function in `vulca.providers` for coarse capability inspection without instantiating providers.
- **`ImageProvider.capabilities`** defaults to `frozenset()` on the Protocol.
- **Mock literal elimination:** All `"mock"` string comparisons in pipeline replaced with `"raw_rgba" in capabilities` checks.
- **ValidationReport sidecar round-trip test:** Contract test for serialize/deserialize cycle.

## [0.13.2] - 2026-04-08

### A-path Hardening (P2 Cleanup)

#### Correctness
- `_apply_alpha` asserts shape match between RGB and alpha (no silent resize).
- `LayerCache.put` atomic via `tempfile + os.replace` (no partial writes on crash).
- Tier-2 keying loader wraps `ModuleNotFoundError`/`AttributeError` → `ValueError`.
- `AssertionError`/`TypeError` propagate out of `layered_generate` orchestration (not silently converted to `generation_failed`).

#### Performance
- **Validation sidecar cache:** `<key>.report.json` stored alongside keyed PNGs. Cache hits skip `validate_layer_alpha` entirely.
- **Cache write reuse:** `cache.put` reads disk bytes from `rgba_img.save(out_path)` instead of re-encoding through PIL.

#### Retry
- In-process retry budget=2 (3 total attempts) with full-jitter backoff `random.uniform(0, 0.5 * 2**attempt)`.
- `AssertionError`/`TypeError`/`asyncio.CancelledError` propagate immediately (not retried).
- `LayerFailure.reason` is now `Literal["generation_failed", "validation_failed"]`.

#### Provider capabilities
- `ImageProvider.capabilities: frozenset[str]` — real providers declare `{'raw_rgba'}`, mock declares `frozenset()`.
- `_provider_supports_native` queries capabilities (no `"mock"` string match).

#### Manifest & retry polish
- `layer_extras` whitelist (8 keys, raises on unknown).
- `retry_layers` preserves non-validation manifest warnings and drops stale validation warnings for retried layers.

## [0.13.1] - 2026-04-08

### Fixes (codex review nice-to-haves from v0.13.0)
- **ChromaKeying linear RGB**: distance is now computed in linear RGB (sRGB gamma-decoded) instead of on raw sRGB bytes. Subject separation on colored canvases is now perceptually consistent with the docstring.
- **`_box_blur` vectorization**: replaced the Python per-pixel integral-image loop with full-frame numpy slicing. 512×512 box blur now runs in single-digit ms instead of seconds.
- **`_despill` gating**: no longer erodes alpha on solid interior. Only pixels in the soft-edge band (0.02 < alpha < 0.98) that are close to the background color get attenuated (up to 50% by default).

### Test coverage
- `test_chroma_operates_in_linear_rgb_not_srgb` pins the gamma-decode behavior.
- `test_box_blur_matches_reference_and_is_fast` checks output against a naive per-pixel reference AND enforces a 0.5s budget on 512×512.
- `test_despill_preserves_solid_interior` asserts solid opaque interior stays at alpha >= 0.999 and the edge band still attenuates.

## [0.13.0] - 2026-04-08

### Layered Generation — A-path (generation-time alpha)
- **New keying subsystem** (`vulca.layers.keying`): hand-rolled sRGB→LAB, `CanvasSpec` + `KeyingStrategy` protocol, tier-0 luminance keying (the WOW unlock for ink wash), tier-1 chroma + Delta-E keying, strategy registry.
- **Validation** (`vulca.layers.validate`): coverage / position-IoU / emptiness checks with structured warnings.
- **Tradition config +5 fields**: `layerability`, `canvas_color`, `canvas_description`, `style_keywords`, `key_strategy` rolled out to all 13 traditions. `chinese_xieyi` is the hero case.
- **Anchored layered prompt builder** with canvas / content-exclusivity / spatial / style anchors.
- **Layered generation library** (`vulca.layers.layered_generate`): `generate_one_layer` + concurrent `layered_generate` with semaphore-bounded orchestration and partial-failure non-blocking semantics.
- **Per-artifact sidecar cache** (`.layered_cache/`) keyed on provider + model + prompt + canvas + schema version.
- **Pipeline dispatch**: `LayerGenerateNode` routes native traditions through the new library (A-path). Split / discouraged traditions keep the v0.12 VLM-mask path.
- **Spatial metadata passthrough**: `plan_layers` forwards VLM `position`/`coverage` onto `LayerInfo` for the anchored prompt.

### B-path matting
- `soften_mask` with feather + optional `cv2.ximgproc.guidedFilter` + despill (pure-numpy fallback).
- `apply_vlm_mask` now softens the alpha channel on save for B-path edge quality.

### Manifest v3
- New top-level fields: `generation_path` (a / b), `layerability`, `partial`, `warnings`, plus per-layer extras (`source`, `cache_hit`, `attempts`, `validation`).
- `CompositeNode` writes `manifest.json` alongside `artifact.json` for every LAYERED run.

### CLI
- `vulca create --layered` gains `--no-cache`, `--strict`, `--max-layers` and a proper output directory.
- `vulca layers retry <dir> [--layer NAME | --all-failed]` — re-run failed layers through `layered_generate` with cache reuse.
- `vulca layers cache clear <dir>` — drop the sidecar cache.
- `discouraged` tradition warning on `--layered` (stderr or interactive y/N prompt).

### MCP
- New tools: `vulca_layered_create`, `vulca_layers_retry`.

### Tests
- Unit tests for every keying tier, validation, anchored prompt, cache, `generate_one_layer`, orchestration, manifest v3.
- E2E tests: A-path on chinese_xieyi (mock) and partial-failure on a flaky provider.
- Gated golden test (`--run-real-provider`) comparing 16-bin alpha histograms against a baseline JSON.

### Notes
- Defense 3 (reference image conditioning) is interface-only in v0.13; full implementation deferred to v0.14 per spec.
- No separate in-process counter module — telemetry lives in the manifest via `cache_hit` / `attempts` / `validation` per-layer extras.

## [0.12.0] - 2026-04-07

### Layer Primitives — Spatial + Opacity + Blend Modes
- **LayerInfo spatial fields**: `x`, `y`, `width`, `height`, `rotation` (percentage-based, resolution-independent), `content_bbox` (auto-computed pixel coords)
- **`opacity` field now affects compositing**: 0.0–1.0 alpha multiplier applied during blend
- **Spatial transform engine** (`transform.py`): apply rotation + spatial coords to layer images, with content_bbox tracking
- **`transform_layer` operation**: programmatic layer transform via SDK
- **MCP `layers_transform` tool**: agent-driven spatial manipulation
- **CLI `vulca layers transform`** subcommand
- **6 new blend modes**: `overlay`, `soft_light`, `darken`, `lighten`, `color_dodge`, `color_burn` (joined existing `normal`, `screen`, `multiply`)

### New Split Modes — Two Pixel-Precise Methods
- **`split_vlm`** (Gemini-based semantic split):
  - Per-layer BW mask generation via Gemini image model
  - Custom `prompt` parameter on `generate_vlm_mask`
  - Foreground-first exclusive pixel assignment + background fallback (`~assigned`)
  - Degenerate mask detection (std<10) → fallback to color mask
  - **Validated end-to-end**: composite roundtrip diff = 0.00 on hero-shanshui.jpg
  - Best for: stylized art (ink wash, post-impressionist), recognizable objects with details (trees, characters)
- **`split_sam3`** (SAM3 text-prompted segmentation):
  - Uses `transformers.Sam3Processor` + `Sam3Model` (`facebook/sam3`)
  - Direct text prompts from `info.description` — no point-prompt heuristics
  - Pixel-precise multi-instance OR combination for full concept coverage
  - Resize handling (model resolution → original image size)
  - **Validated end-to-end**: composite roundtrip diff = 0.00 on synthetic + shanshui
  - Best for: large structural elements with clear boundaries (mountains, terrain, well-defined subjects)
  - Requires `pip install vulca[sam3]` (transformers ≥ 4.50, torch ≥ 2.0) + CUDA GPU

### CLI / MCP / SDK Wiring
- **CLI**: `vulca layers split --mode {regenerate,extract,sam,vlm,sam3}` (5 modes)
- **MCP**: `layers_split(image_path, mode="vlm"|"sam3", ...)` routes to new modes
- **SDK**: `from vulca.layers import split_vlm, sam3_split, SAM3_AVAILABLE`

### Fixes
- **`gemini.py` mime type detection**: Hardcoded `image/png` caused Gemini to hang on JPEG inputs (90s timeout). Now detects format from magic bytes (JPEG, PNG, GIF, WebP). **Affects all callers of `GeminiImageProvider` with reference images, not just split_vlm**.
- **SAM3 tensor handling**: Fixed `Boolean value of Tensor with no values is ambiguous` error. SAM3 PCS returns `Tensor[N, mask_h, mask_w]`; combine all instances above threshold via OR for full concept coverage.
- **SAM3 resolution handling**: Resize model output (e.g., 288×288) to original image size via PIL NEAREST.
- **`split_vlm` review fixes**: docstring update, dead `io as _io` import removal, `assigned` array passthrough to `build_color_mask` fallback for consistency.
- **Test fixtures**: Replace deprecated `asyncio.get_event_loop().run_until_complete()` with `asyncio.run()` to prevent `RuntimeError` in full test suite execution.

### Tests
- **+26 new tests**: `test_v012_split_vlm.py` (14 tests) + `test_v012_split_sam3.py` (12 tests)
- All tests are mock-based (no GPU/API key needed for CI)
- Real-provider validation completed on RTX 2070 + Gemini API: composite roundtrip diff = 0.00

### Optional Dependencies
```toml
sam3 = ["transformers>=4.50", "torch>=2.0", "numpy>=1.24", "Pillow>=10.0"]
```

### Coverage Strategy (3-mode complementarity)
| Concept type | Recommended mode | Reason |
|---|---|---|
| Mountains, terrain, large structures | `sam3` | Pixel-precise, recognizes structural shapes |
| Trees, characters, detailed objects | `vlm` | Semantic understanding, captures fine details |
| Geometric shapes, clear boundaries | `sam3` | Sharp edges |
| Stylized art, abstract brushstrokes | `vlm` | Contextual understanding |
| No GPU + no API key | `extract` | Zero-dep fallback |

These modes are **complementary, not replacements** — use them together via AI Agent orchestration through MCP/CLI.

---

## [0.11.0] - 2026-04-04

### Layer Semantics — Phase 3 Integrity Fixes
- **VLM mask shared module**: Extracted `vlm_mask.py` for two-pass mask generation (used by regenerate mode + LAYERED pipeline)
- **VLM mask fallback**: Use generated image as input (not source) when initial mask fails
- **Public `hex_to_rgb` API**: Color utility now exported
- **Round-trip integrity tests**: `composite(split(img)) ≈ img` validation
- **Empty `dominant_colors` guard**: Preserve transparent layers when VLM cannot identify colors
- **`info.id` as layer_masks key**: Prevent name collision when multiple layers share names
- **SAM medoid point**: Closest pixel to color centroid (not centroid itself, which can fall outside non-convex shapes)
- **VLM mask degenerate rejection**: Reject masks with `std<10` (no useful segmentation signal)
- **SAM point prompts from color centroid**: Compute layer point from `dominant_colors` instead of using image center
- **Deduplication**: Cleaner separation between mask generation and application

### Cleanup
- **Dead code removal**: 76 orphaned files + v0.2.0 vulca copy
- **Broken imports**: Fixed all references to deleted modules
- **6 unreachable prototype subdirs deleted**

---

## [0.10.0] - 2026-04-01

### LAYERED Pipeline — Structured Creation
- **LAYERED template**: PlanLayers -> LayerGenerate (2-node). Agent orchestrates composition, evaluation, and iteration via MCP tools (layers_composite, evaluate_artwork, layers_redraw)
- **PlanLayersNode**: VLM plans layer structure from text intent with tradition layer order knowledge (xieyi, gongbi, japanese, photography)
- **LayerGenerateNode**: Per-layer "full-scene + focus" generation with style anchor + reference conditioning
- **CompositeNode**: Blend layers + write Artifact V3 structured creation document
- **DecideNode enhancement**: Per-layer accept/rerun decisions; only regenerate weak layers in subsequent rounds
- **Artifact V3 format**: V2 superset with cultural_context, per-layer scores, creation history, export_hints
- **Tradition layer orders**: Canonical layer sequences in 5 YAML files, loaded at runtime with Python fallback
- **Entry points**: CLI `--layered`, MCP `layered=True`, SDK `layered=True`

### Export-Time Alpha Processing
- **`alpha.py`**: Chroma key + content_type strategy selection (background=opaque, text=chroma, subject=rembg, effect=sam2)
- **`export_with_alpha()`**: Export layers with transparency based on content type
- **Optional deps**: `pip install vulca[rembg]` for ML background removal, `vulca[layers-full]` for rembg + SAM2

### Fixes
- **CompositeNode**: Use tempdir instead of hardcoded `/tmp/vulca_composite/`
- **LayerGenerateNode**: Fix provider integration (`get_image_provider` + `ImageResult` handling)
- **PlanLayersNode**: Use `gemini-2.5-flash` (not deprecated `gemini-2.0-flash`)
- **README Scenario 2b**: Replace "UI Component Extraction" with "Parallax Hero Sections"

### Architecture Simplification (post-0.10.0)
- **LAYERED template simplified**: 5 nodes → 2 nodes (PlanLayers → LayerGenerate). Agent orchestrates composition via MCP tools (layers_composite, evaluate_artwork, layers_redraw)
- **Alpha extraction separated from blend**: blend.py is pure math, alpha.py handles ML-based extraction via ensure_alpha()
- **Background layer safety**: _build_prompt overrides VLM-planned content for background layers, forcing texture-only generation
- **OpenAI gpt-image-1**: Native transparency support with background:"transparent"

## [0.9.2] - 2026-03-30

### Release Automation + Dead Code Cleanup
- **`scripts/release.sh`**: One-command release (version bump + subtree push x3 + PyPI + GitHub releases x4)
- **Dead code audit**: Removed unused imports, stale references across 12 files

## [0.9.1] - 2026-03-30

### Tool Protocol — Hybrid Pipeline with Algorithmic Nodes
- **VulcaTool protocol**: Unified tool contract with ImageData, VisualEvidence, ToolConfig, ToolRegistry auto-discovery
- **5 algorithmic tools**: WhitespaceAnalyzer (L1), CompositionAnalyzer (L1), ColorGamutChecker (L3), BrushstrokeAnalyzer (L2), ColorCorrect (filter)
- **3 platform adapters**: CLI (`vulca tools`), SDK (`from vulca.tools import`), MCP (`tool_*` auto-registered)
- **Pipeline hybrid execution**: `_resolve_nodes()` falls back to ToolRegistry; EvaluateNode auto-detects algo-covered dimensions
- **CULTURAL_XIEYI template**: generate → whitespace_analyze → color_gamut_check → composition_analyze → evaluate → decide
- **VisualEvidence**: Every tool produces annotated images + confidence scores + structured details
- **`replaces` mechanism**: Tools declare which VLM dimensions they can replace (e.g., `{"evaluate": ["L1"]}`)

## [0.9.0] - 2026-03-29

### Layered Generation
- **VLM layer analysis**: Decompose artwork into semantic layers (background, midground, foreground, detail)
- **Per-layer generation**: Chromakey isolation + independent regeneration per layer
- **Layer composite**: Reassemble layers with bbox offset paste
- **PSD/PNG export**: Export with layer manifest (manifest.json with bbox + bg_color metadata)
- **CLI**: `vulca layers analyze`, `vulca layers export`, `vulca layers composite`
- **MCP**: `analyze_layers`, `layers_composite`, `layers_export`, `layers_evaluate`, `layers_regenerate`

### Inpainting
- **Region-based inpainting**: PIL local blend replaces full regeneration — pixels outside bbox guaranteed unchanged
- **VLM-guided**: Tradition-aware repaint prompts with cultural terminology injection
- **CLI**: `vulca inpaint` command
- **MCP**: `inpaint_artwork` tool
- **SDK**: `vulca.inpaint()` public API

### Hex Color Input
- Palette accepts `#hex` values with strict prompt injection into generation

### ComfyUI Parity
- 11 nodes (up from 8): added Evolution, Traditions, LayersExport nodes
- 18 tests pass

### MCP Parity
- 18 tools (up from 13): added `sync_data`, `layers_*`, `layers_regenerate`

### Testing
- 813 tests (up from 603), strict TDD red-green discipline

## [0.8.0] - 2026-03-29

### Multi-round img2img Iteration (P0-A)
- **Round-to-round reference**: Selected concept from Round N becomes reference for Round N+1 variations
- **Variation strength inference**: Auto-detects strength from NL update keywords (refine=0.2, change=0.4, redo=0.7)
- **Auto-stop suggestion**: Triggers when score >= 85% or converges (< 3% delta for 2 rounds)
- **Round-separated storage**: Concept images saved to `r{N}/concepts/` instead of overwriting

### VLM Analysis Depth (P0-B)
- **Two-phase prompt**: OBSERVE (visual analysis) → EVALUATE (scoring), replacing single-pass scoring
- **Per-dimension observations**: 3-5 factual visual observations per L1-L5 dimension
- **Reference techniques**: Most relevant traditional technique name per dimension (bilingual)
- **Enhanced suggestions**: Now include technique name + how to apply + expected effect
- `max_tokens` increased from 4096 to 6144

### CLI Unification (P0-C)
- **9 unified commands**: evaluate, create, traditions, tradition, evolution, studio, brief, brief-update, concept
- **Click dependency removed**: All commands now use argparse (stdlib)
- `vulca sync` command for cloud data synchronization

### Data Flow (P1-A)
- **LocalEvolver**: Reads `~/.vulca/data/sessions.jsonl` for local evolution
- **Local evolved_context**: VLM reads `~/.vulca/evolved_context.json` before YAML defaults
- **vulca sync**: Push local sessions to cloud, pull aggregated evolved weights (asymmetric)

### Sketch & Reference Upload (P1-B)
- **All entry points**: CLI (`--sketch`, `--reference`, `--ref-type`), SDK, MCP
- **3 reference types**: `style` (color/brushwork only), `composition` (layout only), `full` (both)
- **Dual input mode**: File path or base64 string, auto-detected
- `resolve_image_input()` utility for path/base64 resolution

### Commercial Extra Dimensions (P1-C)
- **Tradition-specific E1-E3**: Up to 3 extra evaluation dimensions per tradition YAML
- **brand_design**: Brand Consistency, Target Audience Fit, Market Differentiation
- **ui_ux_design**: Usability Clarity, Platform Convention, Interaction Affordance
- **photography**: Technical Exposure, Narrative Moment, Print/Screen Readiness
- Extra scores independent from L1-L5 total (displayed separately)

### Testing
- 603 tests (up from 538), strict TDD red-green discipline (15 RED→GREEN cycles)

## [0.7.0] - 2026-03-28

### Selective Pipeline
- **Agent Residuals**: Selective aggregation of agent outputs — only consume what downstream nodes actually need
- **Cultural Engram**: Hash-indexed cultural knowledge retrieval — terminology and taboos injected via REPLACE (not append)
- **Sparse Eval**: BriefIndexer activates only relevant L1-L5 dimensions per Brief, skipped dimensions get baseline scores
- **Quantized Retrieval**: Zero-training session search for few-shot example selection

### Integrity Fixes
- Reset collapsed evolution weights to YAML defaults
- Replace mock return values with proper errors in production paths
- Evolution guard requires 3+ real human feedback entries before evolving
- Full evolution reset: counter, cultures, few-shot, insights

### CLI
- `--residuals` flag for selective agent output aggregation
- `--sparse-eval` flag for Brief-driven dimension activation

### VLM Integration
- Engram fragments REPLACE terminology/taboos instead of appending (prevents prompt bloat)
- Sparse dimensions integrated into VLM scoring prompts

### Testing
- 538 tests (up from 455), strict TDD red-green discipline
- 8 evolution guard boundary cases

## [0.6.0] - 2026-03-25

### Studio Intelligence (Phase 2)
- **LLM Intent Parsing**: `parse_intent_llm()` uses Gemini 2.5 Flash for implicit element extraction (0% -> 84% capture rate)
- **LLM Dynamic Questions**: `generate_questions_llm()` domain-adaptive question generation
- **LLM NL Update**: `parse_nl_update_llm()` complex Chinese instruction parsing (6/10 -> 1/10 fallback)
- **Keyword Extraction**: element/palette/composition regex for Chinese + English
- **Tradition Keywords**: expanded from 8 to 45+ mappings (60% -> 90% detection)
- **Dynamic Questions**: conditional question generation based on Brief state + free-text option
- **Mock Scoring**: hash-based variation by session/round/completeness (0% -> 80% variation)
- **Sketch Upload**: integrated into interactive flow

### Digestion V2 (Phase 3)
- **JsonlStudioStorage**: unified JSONL storage for sessions, artifacts, and signals
- **ArtifactAnalysis**: L1-L5 structured analysis types (L1-L5 dataclasses with serialization)
- **SessionPreferences**: Layer 1 real-time preference accumulation with prompt hints
- **Trajectory Analysis**: Layer 2 mood drift, cultural fidelity, composition preservation
- **Preloader**: Layer 0 pre-session intelligence from history + keyword matching
- **Evolver**: Layer 3 cross-session pattern detection + weight evolution (mock-data-protected)
- **Archiver**: local cold storage for session archival
- **Alembic Migration**: 5-table schema (studio_sessions, artifacts, signals, evolved_patterns, brief_templates)

### Studio Polish (Phase 4)
- **Concept Preview**: shows filename + file size
- **Style Weight Adjustment**: interactive 70/30 input for multi-style
- **Preloader Wired**: Layer 0 suggestions shown at session start

### Testing
- 455 tests (up from 376)
- 10/10 E2E agent test pass rate (up from 0/10)
- Strict TDD red-green commit discipline (44 commits)

## [0.5.0] - 2026-03-24

### Studio Pipeline V2
- Brief-driven creative collaboration (Intent -> Concept -> Generate -> Evaluate -> Refine)
- Natural language Brief updates with deterministic rollback
- Interactive terminal UI (`vulca studio`)
- CLI commands: `vulca brief`, `vulca brief-update`, `vulca concept`
- MCP tools: `studio_create_brief`, `studio_update_brief`, `studio_generate_concepts`, `studio_select_concept`
- ComfyUI custom nodes (5 nodes)

## [0.4.0] - 2026-03-24

### Judge -> Advisor
- Evaluation mode: `strict` | `reference` | `fusion`
- `reference` mode: advisor, not judge
- HITL / custom weights across all 4 entry points (Canvas, CLI, SDK, MCP)

## [0.3.0] - 2026-03-22

### MCP v2 + Provider Refactor
- 6 MCP tools via FastMCP
- Pluggable ImageProvider + VLMProvider protocols
- CLI/SDK/MCP share ONE engine: `vulca.pipeline.execute()`
