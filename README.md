# VULCA

[![PyPI version](https://img.shields.io/pypi/v/vulca.svg)](https://pypi.org/project/vulca/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://pypi.org/project/vulca/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://github.com/vulca-org/vulca/blob/main/LICENSE)
[![Tests](https://img.shields.io/badge/tests-1104%20passing-brightgreen.svg)]()
[![MCP Tools](https://img.shields.io/badge/MCP_tools-21-blueviolet.svg)]()

**AI-native cultural art creation organism.** Create, evaluate, and evolve artwork across 13 cultural traditions — L1-L5 scoring, self-evolving weights, full layer editing, and 5 algorithmic analysis tools. 21 MCP tools, all from one `pip install`.

<p align="center">
  <img src="assets/demo/v2/hero-xieyi.png" alt="Chinese Xieyi ink wash landscape — scored 92%" width="280">
  <img src="assets/demo/v2/hero-japanese.png" alt="Japanese traditional autumn temple" width="280">
  <img src="assets/demo/v2/hero-brand.png" alt="Brand design tea packaging" width="280">
</p>

```bash
pip install vulca
export GOOGLE_API_KEY=your-key
vulca create "Misty mountains after rain, pine pavilion in clouds" -t chinese_xieyi -o artwork.png
# → Score: 0.915 | Tradition: chinese_xieyi | 1 round | 43s
# → Image: artwork.png
```

<details>
<summary><strong>See it in action</strong> (GIF)</summary>
<p align="center">
  <img src="assets/demo/v2/vhs-full.gif" alt="VULCA full demo — create, evaluate, layers, tools, studio, evolution" width="800">
</p>
</details>

> Based on peer-reviewed research: [VULCA Framework](https://aclanthology.org/2025.findings-emnlp/) (EMNLP 2025 Findings) and [VULCA-Bench](https://arxiv.org/abs/2601.07986) (7,410 samples, 9 traditions).

---

## Architecture

```mermaid
graph LR
    subgraph Pipeline["Creation Pipeline"]
        S[Scout] --> G[Generate]
        G --> E[Evaluate<br/>L1-L5]
        E --> D{Decide}
        D -->|rerun| G
        D -->|accept| OUT[Output]
    end

    subgraph Evolution["Self-Evolution Loop"]
        OUT --> SE[Session Store<br/>1100+ sessions]
        SE --> LE[LocalEvolver]
        LE --> EW[Evolved Weights]
        EW --> G
        EW --> E
        EW --> D
    end

    subgraph Tools["Algorithmic Tools (no API)"]
        T1[brushstroke] --> E
        T2[whitespace] --> E
        T3[composition] --> E
        T4[color_gamut] --> E
        T5[color_correct] --> E
    end

    subgraph LayersV2["Layers V2"]
        AN[Analyze] --> SP{Split}
        SP -->|regenerate| IG[img2img per layer]
        SP -->|extract| CM[Color mask]
        SP -->|sam| SAM[SAM2 pixel mask]
        IG --> FC[Full-canvas RGBA]
        CM --> FC
        SAM --> FC
        FC --> ED[Edit: add/remove/reorder<br/>merge/lock/toggle/duplicate]
        ED --> RD[Redraw via img2img]
        RD --> CO[Composite<br/>normal/screen/multiply]
    end
```

**4 entry points, 1 engine**: CLI, Python SDK, MCP (21 tools), ComfyUI (11 nodes) — all share `vulca.pipeline.execute()`.

---

## Create — One Command, Multiple Styles

<details>
<summary>See create workflow (GIF)</summary>
<p align="center">
  <img src="assets/demo/v2/vhs-create.gif" alt="Create workflow demo" width="800">
</p>
</details>

```bash
vulca create "Misty mountains after rain" -t chinese_xieyi -o landscape.png
vulca create "Tea packaging, Eastern aesthetics" -t brand_design --colors "#C87F4A,#5F8A50"
```

**Layer-Driven Design Transfer** — extract elements from art, transform into products:

```bash
# 1. Extract mountain layer from ink wash painting
vulca layers split landscape.png -o ./layers/ --mode extract
# → [1] distant_mountains (subject, 48% opaque)

# 2. Use the mountain layer as reference → create brand packaging
vulca create "Premium tea packaging, mountain silhouette as watermark" \
  -t brand_design --reference ./layers/distant_mountains.png
# → Score: 0.92 | Brand consistency maintained
```

<p align="center">
  <img src="assets/demo/v2/hero-xieyi.png" alt="Original ink wash landscape" width="220">
  →
  <img src="assets/demo/v2/workflow-test/distant_mountains.png" alt="Extracted mountain layer" width="220">
  →
  <img src="assets/demo/v2/workflow-brand-output.png" alt="Brand design using mountain reference" width="220">
</p>
<p align="center"><em>Ink wash landscape → extract mountain layer → tea packaging design (92%)</em></p>

---

## Evaluate — Three Modes

### Strict Mode (Judge)

<details>
<summary>See all 3 modes in action (GIF)</summary>
<p align="center">
  <img src="assets/demo/v2/vhs-create.gif" alt="Evaluate 3 modes demo" width="800">
</p>
</details>

Scores reflect tradition conformance with pass/fail indicators:

```
$ vulca evaluate artwork.png -t chinese_xieyi

  Score:     90%    Tradition: chinese_xieyi    Risk: low

    L1 Visual Perception         ██████████████████░░ 90%  ✓
    L2 Technical Execution       █████████████████░░░ 85%  ✓
    L3 Cultural Context          ██████████████████░░ 90%  ✓
    L4 Critical Interpretation   ████████████████████ 100%  ✓
    L5 Philosophical Aesthetics  ██████████████████░░ 90%  ✓
```

### Reference Mode (Advisor)

Cultural guidance with professional terminology — not a judge, a mentor:

```
$ vulca evaluate artwork.png -t chinese_xieyi --mode reference

  L2 Technical Execution  85%  (traditional)
     To push further: exploring a wider variety of texture strokes
     (e.g., axe-cut strokes 斧劈皴 for sharper rocks, or rain-drop
     strokes 雨点皴 for more rounded forms) could add further
     textural richness.

  L3 Cultural Context  95%  (traditional)
     To push further: adding a short poem (题画诗) that directly
     relates to the scene, further integrating the 'poetry-calligraphy-
     painting-seal' (诗书画印) harmony.
```

### Fusion Mode (Cross-Cultural Comparison)

Evaluate one artwork against multiple traditions simultaneously:

```
$ vulca evaluate artwork.png -t chinese_xieyi,japanese_traditional,western_academic --mode fusion

  Dimension                   Chinese Xieyi Japanese Tradit Western Academi
  ------------------------- --------------- --------------- ---------------
  Visual Perception                   90%             90%             10%
  Technical Execution                 90%             90%             10%
  Cultural Context                    95%             80%              0%
  Critical Interpretation            100%            100%             10%
  Philosophical Aesthetics            90%             90%             10%

  Overall Alignment                    93%             90%              8%

  Closest tradition: chinese_xieyi (93%)
```

| Dimension | What it measures |
|-----------|-----------------|
| **L1** Visual Perception | Composition, color harmony, spatial arrangement |
| **L2** Technical Execution | Rendering quality, technique fidelity, craftsmanship |
| **L3** Cultural Context | Tradition-specific motifs, canonical conventions |
| **L4** Critical Interpretation | Cultural sensitivity, contextual framing |
| **L5** Philosophical Aesthetics | Artistic depth, emotional resonance, spiritual qualities |

Each dimension returns: score (0-1), observations, rationale, actionable suggestion, reference technique, deviation type (traditional / intentional_departure / experimental).

---

## Layers V2 — Full Editing System

Every layer is **full-canvas RGBA** (not bbox crops). Proper blend modes (normal/screen/multiply). 3 split modes. 7 editing operations. 14 CLI subcommands.

<details>
<summary>See layer decomposition in action (GIF)</summary>
<p align="center">
  <img src="assets/demo/v2/vhs-layers.gif" alt="Layers V2 decomposition demo" width="800">
</p>
</details>

<p align="center">
  <img src="assets/demo/v2/hero-xieyi.png" alt="Original artwork" width="180">
  →
  <img src="assets/demo/v2/layers-extract/background_paper.png" alt="Layer: background (32% opaque)" width="120">
  <img src="assets/demo/v2/layers-extract/distant_mountains.png" alt="Layer: mountains (48% opaque)" width="120">
  <img src="assets/demo/v2/layers-extract/central_pavilion_and_pine_trees.png" alt="Layer: pavilion (34% opaque)" width="120">
  <img src="assets/demo/v2/layers-extract/calligraphy_and_seals.png" alt="Layer: calligraphy (6% opaque)" width="120">
  →
  <img src="assets/demo/v2/layers-extract/composite.png" alt="Composite" width="180">
</p>

### Scenario 1: Non-Destructive Editing (Artists)

*"The sky doesn't feel right, but the mountains are perfect"* — edit one layer without touching the rest.

<p align="center">
  <img src="assets/demo/v2/scenario1-comparison.png" alt="Original → preview without mist → final with sunset mist" width="800">
</p>

```bash
# Decompose into semantic layers
vulca layers split artwork.png -o ./layers/ --mode extract

# Preview: toggle mist off to see the difference
vulca layers toggle ./layers/ --layer mist_and_clouds --visible false
vulca layers composite ./layers/ -o preview-no-mist.png

# Redraw only the mist layer — mountains, pavilion, calligraphy untouched
vulca layers toggle ./layers/ --layer mist_and_clouds --visible true
vulca layers redraw ./layers/ --layer mist_and_clouds \
  -i "replace with dramatic sunset gradient, warm orange to purple"

# Composite back with blend modes
vulca layers composite ./layers/ -o final-with-sunset.png
```

Lock layers you want to protect, toggle visibility to preview changes:

```bash
vulca layers lock ./layers/ --layer calligraphy_and_seals   # prevent accidental edits
vulca layers toggle ./layers/ --layer mist --visible false   # preview without mist
vulca layers composite ./layers/ -o preview-no-mist.png      # see the difference
```

### Scenario 2: Element Extraction for Design (Designers)

*Like Figma's component extraction, but for cultural art* — pull out elements, transform into design assets, maintain cultural consistency.

<p align="center">
  <img src="assets/demo/v2/scenario2-design-flow.png" alt="Source artwork → extract mountain layer → brand packaging design" width="800">
</p>

```bash
# 1. Extract the mountain element from an ink wash painting
vulca layers split artwork.png -o ./layers/ --mode extract

# 2. Use it as reference for brand packaging design
vulca create "Premium tea packaging, mountain silhouette as watermark" \
  -t brand_design --reference ./layers/distant_mountains.png
# → Score: 0.92 | Cultural motif preserved in commercial context

# 3. Or merge elements into a reusable design asset
vulca layers merge ./layers/ --layers pavilion_and_pine_trees,calligraphy_and_seals \
  --name "hero_element"

# 4. Add design layers (glow, overlay, etc.)
vulca layers add ./layers/ --name "golden_glow" --z-index 6 --content-type effect

# 5. Export as Photoshop-compatible structure
vulca layers export ./layers/ -o ./design-assets.psd
# → 00_background.png, 01_mountains.png, ... + manifest.json
```

**Design workflow parallel**: Split → Extract element → Reference for new creation → Evaluate cultural consistency — like using Figma's "Detach Instance" to pull out a component, then placing it in a new frame with different styling.

### Scenario 3: Per-Layer Cultural Evaluation (Researchers)

*Which element carries the most cultural weight?* Evaluate each layer independently:

<p align="center">
  <img src="assets/demo/v2/scenario3-eval-chart.png" alt="Per-layer evaluation scores" width="700">
</p>

```
$ vulca layers evaluate ./layers/ -t chinese_xieyi

  [0] background_canvas:       92%  L3=95%
  [1] distant_mountains:       88%  L3=90%
  [2] mist_and_clouds:         88%  L3=90%
  [3] foreground_landscape:    92%  L3=95%  ← highest cultural alignment
  [4] pavilion_and_pines:      92%  L3=95%  ← canonical xieyi motif
  [5] calligraphy_and_seals:   89%  L3=90%
```

`pavilion_and_pines` scores highest on L2 Technical (90%) — the ink wash rendering of pine trees is the most technically accomplished layer. `distant_mountains` at L2=80% suggests the mountain strokes could benefit from more texture variation (axe-cut 斧劈皴 or rain-drop 雨点皴 strokes).

### Technical Reference

**3 split modes:**

| Mode | Command | How it works | API cost |
|------|---------|-------------|:--------:|
| **extract** | `--mode extract` | Color-range masking, no API | Free |
| **regenerate** | `--mode regenerate` | img2img per layer via Gemini | ~$0.05/layer |
| **sam** | `--mode sam` | SAM2 pixel-precise masks (`pip install vulca[sam]`) | Free (local) |

**7 editing operations:**

| Operation | Command | What it does |
|-----------|---------|-------------|
| **add** | `vulca layers add` | Create new transparent layer at z-index |
| **remove** | `vulca layers remove` | Delete layer (blocked if locked) |
| **reorder** | `vulca layers reorder` | Move layer to new z-index |
| **toggle** | `vulca layers toggle` | Show/hide layer in composite |
| **lock** | `vulca layers lock` | Prevent accidental deletion/merge |
| **merge** | `vulca layers merge` | Combine selected layers into one |
| **duplicate** | `vulca layers duplicate` | Copy layer for experimentation |

**Composite + export:**

```bash
vulca layers composite ./layers/ -o final.png        # blend-mode-aware composite
vulca layers export ./layers/ -o ./assets.psd         # PNG directory per layer
vulca layers redraw ./layers/ --layer sky -i "..."    # single-layer img2img
vulca layers redraw ./layers/ --layers a,b --merge    # merge + redraw
```

---

## Tools — Algorithmic Analysis (No API Required)

5 tools that run locally with zero API cost, using OpenCV and NumPy:

<details>
<summary>See all 5 tools in action (GIF)</summary>
<p align="center">
  <img src="assets/demo/v2/vhs-tools.gif" alt="Tools demo" width="800">
</p>
</details>

<p align="center">
  <img src="assets/demo/v2/tools-viz.png" alt="Tool analysis evidence: brushstroke energy, whitespace ratio, composition alignment" width="800">
</p>

```
$ vulca tools run brushstroke_analyze --image artwork.png -t chinese_xieyi
  Brushstroke energy (0.87) aligns with chinese_xieyi's expressive style.
  Visible, dynamic strokes are consistent with tradition expectations.
  Confidence: 0.90

$ vulca tools run whitespace_analyze --image artwork.png -t chinese_xieyi
  Whitespace (32.8%) is within the chinese_xieyi ideal range (30%-55%).
  The top_heavy distribution aligns well with tradition expectations.
  Confidence: 0.75

$ vulca tools run composition_analyze --image artwork.png -t chinese_xieyi
  Rule-of-thirds alignment (0.75), left_heavy asymmetry aligns with
  chinese_xieyi's preference for asymmetric, dynamic arrangements.
  Confidence: 0.90
```

| Tool | What it detects | Zero API |
|------|----------------|:--------:|
| `brushstroke_analyze` | Stroke energy, edge density, direction | ✓ |
| `whitespace_analyze` | Negative space ratio, distribution | ✓ |
| `composition_analyze` | Rule of thirds, center weight, balance | ✓ |
| `color_gamut_check` | Saturation profiling + auto-fix mode | ✓ |
| `color_correct` | Color correction with check/fix/suggest | ✓ |

Hybrid pipeline: algorithmic tools run first, VLM evaluation covers remaining dimensions.

---

## Inpainting — Region-Based Repaint

Repaint specific regions while **guaranteeing pixel-level preservation** outside the bounding box. Not full-image regeneration — PIL local blend.

<p align="center">
  <img src="assets/demo/v2/hero-xieyi.png" alt="Before inpainting" width="350">
  →
  <img src="assets/demo/v2/inpaint-after.png" alt="After inpainting — sky replaced with sunset" width="350">
</p>
<p align="center"><em>Left: original | Right: sky region replaced with golden sunset (mountains untouched)</em></p>

```bash
# Natural language region description
vulca inpaint artwork.png --region "the sky in the upper portion" \
  --instruction "replace with dramatic stormy clouds" -t chinese_xieyi

# Or precise coordinates (x, y, w, h as percentages)
vulca inpaint artwork.png --region "0,0,100,40" \
  --instruction "add golden sunset gradient" --count 4 --select 1
```

How it works:
1. **Region detection**: NL description → VLM identifies bounding box, or use explicit coordinates
2. **Variant generation**: Generate N repaint variants for the region (default 4)
3. **Pixel-level blend**: Only pixels inside the bbox are replaced — everything outside is the original, untouched
4. **Selection**: Auto-select best variant or manually pick with `--select N`

```python
from vulca import ainpaint

result = await ainpaint(
    "artwork.png",
    region="the mountains in the background",
    instruction="make them more misty and ethereal",
    tradition="chinese_xieyi",
    count=4,
)
print(result.bbox)       # {"x": 0, "y": 10, "w": 100, "h": 45}
print(result.variants)   # [path1, path2, path3, path4]
print(result.blended)    # final blended output path
```

---

## Studio — Brief-Driven Creative Session

Multi-round creative collaboration with natural language control:

<details>
<summary>See studio workflow (GIF)</summary>
<p align="center">
  <img src="assets/demo/v2/vhs-studio.gif" alt="Studio workflow demo" width="800">
</p>
</details>

<p align="center">
  <img src="assets/demo/v2/studio-c1.jpg" alt="Concept 1" width="180">
  <img src="assets/demo/v2/studio-c2.jpg" alt="Concept 2" width="180">
  <img src="assets/demo/v2/studio-c3.jpg" alt="Concept 3" width="180">
  <img src="assets/demo/v2/studio-c4.jpg" alt="Concept 4" width="180">
</p>
<p align="center"><em>4 concept variations from brief: "Cyberpunk ink wash, neon pavilions" → select best → generate → evaluate</em></p>

```
$ vulca studio "Cyberpunk ink wash neon pavilions in misty mountains" --provider gemini --auto

  Suggested styles: chinese_xieyi
  Style detected: chinese_xieyi (50%), cyberpunk (50%)

  [Concept] 4 concepts generated (831-921KB each)
  [Generate] Creating artwork via gemini...
  [Evaluate] L1-L5:
    L1 ███████████████████░ 95%
    L2 ██████████████████░░ 90%
    L3 █████████████████░░░ 85%
    L4 ████████████████████ 100%
    L5 ███████████████████░ 95%

  Score target reached (93%). Accepted.
```

```bash
# Interactive mode (with prompts at each step)
vulca studio "Zen garden at dawn" --provider gemini

# Non-interactive (scriptable, CI/CD friendly)
vulca studio "Zen garden at dawn" --provider gemini --auto --max-rounds 3

# Step by step
vulca brief ./project -i "Cyberpunk shanshui" -m "epic-futuristic"
vulca brief-update ./project "Add more negative space, reduce neon intensity"
vulca concept ./project -n 4 --provider gemini
vulca concept ./project --select 1
```

---

## Self-Evolution

The system learns from every session. After 1100+ sessions, weights evolve per tradition:

```
$ vulca evolution chinese_xieyi

  Dim     Original    Evolved     Change
  ----- ---------- ---------- ----------
  L1        10.0%     10.0% +    0.0%
  L2        15.0%     20.0% +    5.0%    ← Technical Execution strengthened
  L3        25.0%     35.0% +   10.0%    ← Cultural Context most evolved
  L4        20.0%     15.0%    -5.0%
  L5        30.0%     20.0%   -10.0%
  Sessions: 71
```

```mermaid
graph LR
    C[Create/Evaluate] -->|scores| S[Session Store]
    S -->|every 5 min| LE[LocalEvolver]
    LE -->|per tradition| EW[Evolved Weights]
    EW -->|read| G[GenerateNode<br/>strengthen weak dims]
    EW -->|read| E[EvaluateNode<br/>calibrated scoring]
    EW -->|read| D[DecideNode<br/>adaptive threshold]
    G --> C
    E --> C
```

**How users interact with evolution:**

```bash
# View current evolved state for any tradition
vulca evolution chinese_xieyi

# Compare multiple traditions
vulca evolution default
vulca evolution japanese_traditional

# Evolution happens automatically — every create/evaluate session
# contributes to weight refinement. No manual intervention needed.

# Session data:
vulca sessions stats    # 1100+ sessions, per-tradition breakdown
vulca sessions list -t chinese_xieyi --sort score  # browse by tradition
```

**Key design choices:**
- `strict` mode sessions strengthen tradition conformance weights
- `reference` mode sessions track exploration trends without penalizing
- `deviation_type=intentional_departure` is not treated as a weakness
- Weights converge after ~50 sessions per tradition

---

## Where to Use

### Claude Code / Cursor (MCP Plugin)

```bash
pip install vulca[mcp]
claude plugin install vulca-org/vulca-plugin
```

Then ask: *"Evaluate this painting for Chinese xieyi style"* — Claude calls VULCA automatically.

21 MCP tools: `evaluate_artwork`, `create_artwork`, `analyze_layers`, `layers_split`, `layers_redraw`, `layers_edit` (7 operations), `studio_create_brief`, `inpaint_artwork`, 5 Tool Protocol tools, and more.

### ComfyUI

```bash
# In ComfyUI/custom_nodes/
git clone https://github.com/vulca-org/comfyui-vulca
pip install vulca>=0.9.2
```

11 nodes: Brief, Concept, Generate, Evaluate, Update, Inpaint, Layers Analyze/Composite/Export, Evolution, Traditions.

### Python SDK

```python
import vulca

# Evaluate
result = vulca.evaluate("artwork.png", tradition="chinese_xieyi")
print(result.score)        # 0.90
print(result.suggestions)  # {"L2": "explore axe-cut strokes...", ...}
print(result.L3)           # 0.95

# Create
result = vulca.create("Tea packaging with mountain landscape",
                       provider="gemini", tradition="brand_design")
print(result.weighted_total)  # 0.88
print(result.best_image_b64[:20])  # base64 image data

# Sparse evaluation (only relevant dimensions)
result = vulca.evaluate("artwork.png", tradition="chinese_xieyi",
                         sparse=True, intent="文化传统符号")
print(result.sparse_activation)  # {"active": {"L3": 0.9, ...}, "skipped": {...}}

# Layers
from vulca.layers import analyze_layers, split_extract, composite_layers
import asyncio
layers = asyncio.run(analyze_layers("artwork.png"))
results = split_extract("artwork.png", layers, output_dir="./layers")
composite_layers(results, width=1024, height=1024, output_path="composite.png")
```

### CLI Reference

```bash
vulca evaluate painting.jpg -t chinese_xieyi                    # strict mode
vulca evaluate painting.jpg -t chinese_xieyi --mode reference   # advisor mode
vulca evaluate painting.jpg -t xieyi,japanese --mode fusion     # cross-cultural
vulca evaluate painting.jpg --sparse-eval                       # only relevant dims

vulca create "Misty mountains" -t chinese_xieyi --provider gemini -o art.png
vulca create "Tea packaging" --provider gemini --residuals       # agent attention weights

vulca studio "Zen garden" --provider gemini                      # interactive
vulca studio "Zen garden" --provider gemini --auto               # non-interactive

vulca layers analyze artwork.png                                 # VLM semantic analysis
vulca layers split artwork.png -o ./layers --mode regenerate     # 3 modes
vulca layers redraw ./layers --layer sky -i "add sunset"         # img2img
vulca layers add ./layers --name glow --content-type effect      # 7 editing ops
vulca layers composite ./layers -o final.png                     # blend modes

vulca inpaint artwork.png --region "sky" --instruction "add dramatic clouds"
vulca tools run brushstroke_analyze --image art.png -t chinese_xieyi
vulca evolution chinese_xieyi                                    # evolved weights
vulca sessions stats                                             # 1100+ sessions
vulca resume <session-id>                                        # resume checkpoint
```

---

## 13 Cultural Traditions

`chinese_xieyi` `chinese_gongbi` `japanese_traditional` `western_academic` `islamic_geometric` `watercolor` `african_traditional` `south_asian` `contemporary_art` `photography` `brand_design` `ui_ux_design` + `default`

Custom traditions via YAML:

```bash
vulca evaluate painting.jpg --tradition ./my_style.yaml
```

---

## Install

```bash
pip install vulca           # core SDK + CLI
pip install vulca[mcp]      # + MCP server for Claude Code / Cursor
pip install vulca[sam]      # + SAM2 pixel-precise layer extraction
```

No API key required for mock mode. For real VLM scoring + image generation:

```bash
export GOOGLE_API_KEY=your-key
```

Gemini image generation supports **512 / 1K / 2K / 4K** output with automatic size and aspect ratio mapping.

---

## Citation

```bibtex
@inproceedings{yu2025vulca,
  title={VULCA: A Framework for Culturally-Aware Visual Understanding},
  author={Yu, Haorui},
  booktitle={Findings of EMNLP 2025},
  year={2025}
}
```

## License

Apache 2.0

---

> Issues and PRs welcome. Development happens in a private monorepo and is synced here via `git subtree`.
