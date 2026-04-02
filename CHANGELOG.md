# Changelog

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
