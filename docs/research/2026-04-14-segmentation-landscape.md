# Text-Prompted Image Segmentation Landscape

*Research snapshot: April 2026*

## Context

Vulca added text-prompted layer decomposition (Cap 4) as part of the 8×8 showcase
pipeline. This document records the competitive landscape and technical choices
at the time of the decision.

## The Problem

Decompose an artwork into N semantic layers (e.g., sky / subject / foreground)
where each layer contains ONLY the pixels belonging to that concept, with
pixel-precise edges and no gaps or leakage between layers.

Constraints for Vulca:
- Must run on Apple Silicon MPS (no CUDA dependency)
- Text-prompted (user describes what each layer contains)
- Single-pass preferred (no post-hoc filtering which causes holes)
- Works on diverse artworks: photos, oils, frescoes, ink paintings, scrolls

## Decision: EVF-SAM

**Chosen backbone**: [EVF-SAM](https://github.com/hustvl/EVF-SAM) (Zhang et al.,
TMLR 2024-2025, HUST + vivo). Early Vision-Language Fusion: BEIT-3 shared
Transformer fuses text and image features before the SAM decoder, producing a
single coherent mask per prompt in one forward pass.

Measured on Earthrise (2400×2400) at MPS fp32:
- 1.2% dark-pixel leak (vs 19.3% CLIPSeg, 11.1% CLIPSeg+GrabCut, 0.8% FastSAM+CLIP)
- Single-mask output (vs FastSAM's 12-segment merge pattern with holes)
- ~5 seconds per prompt on M-series unified memory
- 1.32B params, Apache 2.0

Full 8-image showcase runs in 94s total on MPS.

## Approaches Evaluated

### Rejected

| Method | Why rejected |
|---|---|
| Color-range masking (our `extract` mode) | Fails on low-contrast images — gray moon and gray Earth clouds both match the same dominant colors |
| Connected-component filter on color masks | Solves foreground leakage (0% for Earthrise) but removes the Earth when subject also matches by color |
| Spatial priors (hard bbox / weight decay) | Works for specific compositions (bottom = foreground) but brittle across art forms |
| CLIPSeg | Native 352×352 output → blocky edges when upsampled to 2400px |
| CLIPSeg + GrabCut edge refinement | Improves edges but still inherits CLIPSeg's coarse seed masks |
| FastSAM + CLIP text filtering | Pixel-perfect edges but post-hoc CLIP scoring creates holes when objects are split across segments |
| Florence-2 referring expression segmentation | Returns polygons that cut corners of circular objects; version-conflict prone with transformers library |
| SAM 3 (Meta, Nov 2025) | CUDA + Triton only; MPS broken |
| Grounded-SAM-2 | Grounding DINO uses custom CUDA deformable attention |
| LISA, GLaMM | 7B+ parameters, too heavy |

### The Winner

**EVF-SAM** solved the fundamental problem of post-hoc approaches: because text
conditioning happens at the feature level, not as a selection over candidates,
a semantic object that happens to be split across multiple visual segments
still produces one coherent mask. For Earthrise's lunar surface this means
no "missing block" artifact.

## Industry Competitive Landscape

### Professional creative tools (commercial)

| Product | Tech | Limitation |
|---|---|---|
| Adobe Photoshop Select Subject + Generative Fill | Private SAM fork + Firefly | Cloud only, preset categories only (sky / subject / hair), no free-text prompts |
| After Effects Roto Brush 3.0 | SAM-derivative temporal | Click-based, not text |
| PhotoRoom, Remove.bg, Clipdrop | BiRefNet + U²-Net | Two-class only (fg/bg) |
| Canva, Figma bg removers | Remove.bg API | Two-class only |

### AI generation platforms

| Product | Tech | Limitation |
|---|---|---|
| ComfyUI + SAM2 / GroundingDINO nodes | GroundingDINO → SAM2 → manual composite | DAG builder, not a product; user wires everything |
| Krita AI Diffusion (Acly) | ComfyUI backend + GroundingDINO-SAM | Closest open-source analog for the decomposition step alone. No art evaluation, no cultural context |
| InvokeAI Canvas | SAM-based Segment Anything tool | Click-based, not text |
| RunwayML Magic Mask | Trajectory-based + Gen-3 | Cloud only, $15-95/month |

### Open-source dev tools (technical peers)

| Project | Relation |
|---|---|
| Meta SAM 2.1 / SAM 3 | Point / box prompted, not text natively |
| lang-sam (luca-medeiros) | GroundingDINO + SAM wrapper library |
| Grounded-SAM-2 (IDEA-Research) | Research-grade reference impl, same family as EVF-SAM |
| APE (BAAI, 2024) | Open-vocab detection + segmentation in one model, direct EVF-SAM alternative |

### Academic / art-specific

| Project | Status |
|---|---|
| ArtSeg (Oxford VGG, 2023) | Trained on WikiArt, not maintained |
| PaintScene / ArtBench-Decompose (CVPR 2025) | Paper only, no public weights |
| Qwen-Image-Layered | Generates layered images; doesn't decompose existing artwork |
| Evo-Ukiyoe | Ukiyo-e generation; no evaluation or decomposition |

## Niche Assessment

No competitor combines all four of:

1. Art-specific VLM evaluation (L1–L5 rubric)
2. Cultural tradition awareness (xieyi, ukiyo-e, gongbi, etc.)
3. Text-prompted multi-layer decomposition (not fg/bg only)
4. Local inference, open source

Closest single-feature matches:
- Krita AI plugin ≈ local + text-decomposition, no critique
- Photoshop Generative Fill ≈ polished edit UX, no critique, cloud
- ComfyUI workflows ≈ fully local but no curation, rubric, or cultural framing

Vulca's differentiation is workflow and domain vocabulary, not backbone tech.
EVF-SAM is a commodity backbone choice; value accrues in prompt design, rubric
curation, and cultural tradition YAML extensions.

## Future Watch

| Candidate | ETA | What to watch for |
|---|---|---|
| EVF-SAM v2 | Announced Jan 2025, unreleased | Salient matting + small-object segmentation → solves Pearl Earring (1% coverage) and Great Wave boats (1.9%) |
| SAMA (arXiv 2601.12147) | Code pending | Unified SAM + matting; stack behind EVF-SAM for alpha refinement |
| SSP-SAM (Mar 2026) | Just released | MPS unverified; potential EVF-SAM competitor |

Monitor hustvl/EVF-SAM for v2 release. Do not switch backbones until measured
improvement on Vulca's showcase set.

## References

- EVF-SAM: [paper](https://arxiv.org/abs/2406.20076) · [code](https://github.com/hustvl/EVF-SAM)
- Grounded-SAM-2: [code](https://github.com/IDEA-Research/Grounded-SAM-2)
- Krita AI Diffusion: [code](https://github.com/Acly/krita-ai-diffusion)
- SAM 3: [discussion on MPS incompatibility](https://huggingface.co/facebook/sam3/discussions/11)
- Experimental scripts: `scripts/experiment_layer_fixes.py`, `scripts/evfsam_showcase.py`
- Measurement results: `assets/showcase/experiments/evfsam_all/stats.json`
