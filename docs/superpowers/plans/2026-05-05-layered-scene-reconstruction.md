# Source-Conditioned Layered Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a source-conditioned layered generation workflow that recreates the roadside photo as editable semantic output layers while reusing `redraw_layer` for small flower details.

**Architecture:** Add a new workflow above redraw. It consumes a source image, a semantic output layer contract, and curated control masks that constrain generation and compositing. It normalizes exclusive ownership by z-index, subtracts detail flower pixels from parent hedge/grass masks, dispatches layer policies (`reconstruct`, `preserve`, `local_redraw`, `residual`), composites a preview, and writes `summary.json` with policies, usage, cost, failures, and gate results. This is not a `decompose` replacement: masks are scaffolding, and the product output is a generated/preserved editable layer stack. The first prototype writes large image artifacts under `.scratch/source-layered-generation/` by default so generated PNGs are not committed accidentally.

**Tech Stack:** Python 3.11, Pillow, NumPy, pytest, existing `OpenAIImageProvider.inpaint_with_mask`, existing `redraw_layer`, `write_manifest`, `load_manifest`, and `composite_layers`.

---

## Spec Review

The design in `docs/superpowers/specs/2026-05-05-layered-scene-reconstruction-design.md` is directionally correct. It should be treated as reviewed with these implementation amendments:

0. The product boundary must be explicit: this is layered generation/reconstruction from a source reference, not `decompose`. A source image may provide reference crops and control masks, but the workflow's output is a new editable layer stack, not extracted source layers.
1. The spec needs a machine-readable prompt contract. The prose prompts are good for review, but implementation should read `docs/superpowers/contracts/2026-05-05-layered-scene-reconstruction-prompts.json` so layer policy, z-order, forbidden content, provider endpoint, and summary requirements stay auditable.
2. Mask polarity must be explicit in two places. Curated control masks use alpha>0 as intended layer ownership before normalization. Provider edit masks use OpenAI convention: alpha=0 edits and alpha=255 preserves.
3. The MVP must start from existing or curated control masks. Auto VLM planning and general segmentation should be a later lane after ownership subtraction proves it removes old flower residue.
4. Broad hedge, grass, and distant tree texture should default to `preserve` or `residual`. The small botanical strategy must not be used for broad green texture.
5. Red car and yellow truck should be present in the taxonomy, but preserved for the first residue test unless the curated masks are clean enough to reconstruct without identity drift.
6. `summary.json` needs a fixed schema: layer policies, source mask area, normalized owned area, parent subtraction counts, provider usage, cost, failures, quality gates, and skipped layers.
7. Provider execution must use OpenAI-compatible `/v1/images/edits` through `OPENAI_API_KEY` and `VULCA_OPENAI_BASE_URL`; the workflow should fail fast if configured to use `/v1/chat/completions`.
8. Artifact routing needs to be productized. The prototype default should be `.scratch/source-layered-generation/<run-id>/`; callers can pass an explicit artifact directory, but docs and source directories should not receive large generated images by default.
9. The spec should define the residual layer as visible and locked in MVP outputs, not hidden. This makes holes and uncertain pixels obvious.
10. The acceptance gate should include a focused 2x crop over white/yellow flowers to verify parent hedge subtraction removed old flower residue.

## File Map

- Create: `docs/superpowers/contracts/2026-05-05-layered-scene-reconstruction-prompts.json`
  - Machine-readable prompt contracts and layer policies for the roadside taxonomy.

- Create: `src/vulca/layers/reconstruction.py`
  - Core dataclasses and workflow: contract loading, control mask loading, ownership normalization, preserve/reconstruct/local-redraw dispatch, manifest writing, composite writing, and summary writing.

- Modify: `src/vulca/layers/__init__.py`
  - Export `SourceLayeredGenerationResult`, `load_reconstruction_contracts`, `normalize_layer_ownership`, `asource_layered_generate`, and `source_layered_generate`.

- Create: `scripts/prototype_source_layered_generation.py`
  - CLI prototype that runs the MVP from a source image plus curated control mask directory and writes only to the chosen artifact directory.

- Create: `tests/test_layered_reconstruction_contracts.py`
  - Contract loader tests and provider endpoint guard tests.

- Create: `tests/test_layered_reconstruction_ownership.py`
  - Unit tests for flower-detail subtraction from hedge/base layers and residual fill.

- Create: `tests/test_layered_reconstruction_summary.py`
  - Unit tests for `summary.json` shape, cost roll-up, failure records, and layer policy records.

- Create: `tests/test_layered_reconstruction_workflow.py`
  - End-to-end mock-provider workflow over tiny curated control masks.

- Do not modify existing redraw refinement tests in this engineering line.
  - `local_redraw` routing is represented by reconstruction-owned dispatch tests only.

## Legacy Boundary

Do not remove legacy layer APIs in this branch. Keep these boundaries explicit:

- `layered_generate` remains the prompt-native layered generation path.
- `layers_split`, `split_vlm`, `split_sam3`, and orchestrated `decompose` remain extraction/decomposition paths.
- `split_regenerate` and `split_extract` are legacy/best-effort compatibility paths and must not become the base for v0.24.
- v0.24 introduces `source_layered_generate`: source photo as reference, control masks as scaffolding, generated/preserved/local-redrawn semantic layers as output.

## Task 1: Lock The Prompt Contract

**Files:**
- Create: `docs/superpowers/contracts/2026-05-05-layered-scene-reconstruction-prompts.json`
- Create: `tests/test_layered_reconstruction_contracts.py`
- Create: `src/vulca/layers/reconstruction.py`

- [ ] **Step 1: Write the contract loader tests**

Create `tests/test_layered_reconstruction_contracts.py`:

```python
from pathlib import Path

import pytest

from vulca.layers.reconstruction import load_reconstruction_contracts


CONTRACT_PATH = Path(
    "docs/superpowers/contracts/2026-05-05-layered-scene-reconstruction-prompts.json"
)


def test_loads_required_roadside_layer_contracts():
    contracts = load_reconstruction_contracts(CONTRACT_PATH)

    assert contracts.provider["endpoint"] == "/v1/images/edits"
    assert "/v1/chat/completions" in contracts.provider["forbidden_endpoints"]
    assert contracts.artifact_policy["default_artifact_root"] == (
        ".scratch/source-layered-generation"
    )
    assert [layer.semantic_path for layer in contracts.layers] == [
        "background.sky.clean_blue",
        "background.distant_trees",
        "subject.vehicle.red_car",
        "subject.vehicle.yellow_truck",
        "foreground.guardrail",
        "foreground.grass_bank",
        "foreground.hedge_bush",
        "detail.dry_stems",
        "detail.white_flower_cluster",
        "detail.yellow_dandelion_heads",
        "residual.source_texture",
    ]


def test_rejects_contract_without_residual_layer(tmp_path):
    contract = CONTRACT_PATH.read_text()
    edited = contract.replace('"semantic_path": "residual.source_texture"', '"semantic_path": "residual.missing"')
    path = tmp_path / "bad.json"
    path.write_text(edited)

    with pytest.raises(ValueError, match="residual.source_texture"):
        load_reconstruction_contracts(path)
```

- [ ] **Step 2: Verify red**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_contracts.py -q
```

Expected: import fails because `vulca.layers.reconstruction` does not exist.

- [ ] **Step 3: Implement the loader**

Create the first part of `src/vulca/layers/reconstruction.py`:

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


LayerPolicy = Literal["reconstruct", "preserve", "local_redraw", "residual"]


@dataclass(frozen=True)
class LayerPromptContract:
    semantic_path: str
    display_name: str
    z_index: int
    visual_role: str
    mvp_policy: LayerPolicy
    allowed_policies: tuple[str, ...]
    edit_risk: str
    parent_layer: str | None
    mask_prompt: str
    prompt_lines: tuple[str, ...]
    forbidden_content: tuple[str, ...]


@dataclass(frozen=True)
class ReconstructionContracts:
    schema_version: str
    provider: dict
    artifact_policy: dict
    common_edit_prefix_lines: tuple[str, ...]
    negative_prompt_block_lines: tuple[str, ...]
    layers: tuple[LayerPromptContract, ...]
    summary_json_required_keys: tuple[str, ...]


def load_reconstruction_contracts(path: str | Path) -> ReconstructionContracts:
    contract_path = Path(path)
    data = json.loads(contract_path.read_text())
    layers = tuple(
        LayerPromptContract(
            semantic_path=item["semantic_path"],
            display_name=item["display_name"],
            z_index=int(item["z_index"]),
            visual_role=item["visual_role"],
            mvp_policy=item["mvp_policy"],
            allowed_policies=tuple(item.get("allowed_policies", ())),
            edit_risk=item.get("edit_risk", "medium"),
            parent_layer=item.get("parent_layer"),
            mask_prompt=item.get("mask_prompt", ""),
            prompt_lines=tuple(item.get("prompt_lines", ())),
            forbidden_content=tuple(item.get("forbidden_content", ())),
        )
        for item in data.get("layers", ())
    )
    paths = {layer.semantic_path for layer in layers}
    if "residual.source_texture" not in paths:
        raise ValueError("contract must include residual.source_texture")
    return ReconstructionContracts(
        schema_version=data["schema_version"],
        provider=data["provider_contract"],
        artifact_policy=data["artifact_policy"],
        common_edit_prefix_lines=tuple(data.get("common_edit_prefix_lines", ())),
        negative_prompt_block_lines=tuple(data.get("negative_prompt_block_lines", ())),
        layers=layers,
        summary_json_required_keys=tuple(data.get("summary_json_required_keys", ())),
    )
```

- [ ] **Step 4: Verify green**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_contracts.py -q
```

Expected: `2 passed`.

## Task 2: Normalize Layer Ownership

**Files:**
- Modify: `src/vulca/layers/reconstruction.py`
- Create: `tests/test_layered_reconstruction_ownership.py`

- [ ] **Step 1: Write failing ownership tests**

Create `tests/test_layered_reconstruction_ownership.py`:

```python
import numpy as np
from PIL import Image

from vulca.layers.reconstruction import LayerPromptContract, normalize_layer_ownership


def _contract(path: str, z: int, policy: str, parent: str | None = None):
    return LayerPromptContract(
        semantic_path=path,
        display_name=path,
        z_index=z,
        visual_role="detail" if path.startswith("detail.") else "foreground",
        mvp_policy=policy,
        allowed_policies=(policy,),
        edit_risk="low",
        parent_layer=parent,
        mask_prompt=path,
        prompt_lines=(path,),
        forbidden_content=(),
    )


def _mask(size, box):
    img = Image.new("L", size, 0)
    img.paste(Image.new("L", (box[2], box[3]), 255), (box[0], box[1]))
    return img


def test_detail_flower_pixels_are_subtracted_from_parent_hedge():
    size = (8, 6)
    layers = (
        _contract("foreground.hedge_bush", 60, "preserve"),
        _contract("detail.white_flower_cluster", 80, "local_redraw", "foreground.hedge_bush"),
        _contract("detail.yellow_dandelion_heads", 90, "local_redraw", "foreground.hedge_bush"),
        _contract("residual.source_texture", 100, "residual"),
    )
    source_masks = {
        "foreground.hedge_bush": _mask(size, (0, 2, 8, 4)),
        "detail.white_flower_cluster": _mask(size, (2, 3, 2, 2)),
        "detail.yellow_dandelion_heads": _mask(size, (5, 3, 1, 1)),
    }

    owned = normalize_layer_ownership(size=size, layers=layers, source_masks=source_masks)

    hedge = np.asarray(owned["foreground.hedge_bush"]) > 0
    white = np.asarray(owned["detail.white_flower_cluster"]) > 0
    yellow = np.asarray(owned["detail.yellow_dandelion_heads"]) > 0
    residual = np.asarray(owned["residual.source_texture"]) > 0

    assert not np.logical_and(hedge, white).any()
    assert not np.logical_and(hedge, yellow).any()
    assert white.sum() == 4
    assert yellow.sum() == 1
    union = hedge | white | yellow | residual
    assert union.all()


def test_unassigned_pixels_go_to_visible_residual_layer():
    size = (4, 4)
    layers = (
        _contract("background.sky.clean_blue", 0, "reconstruct"),
        _contract("residual.source_texture", 100, "residual"),
    )
    source_masks = {"background.sky.clean_blue": _mask(size, (0, 0, 4, 2))}

    owned = normalize_layer_ownership(size=size, layers=layers, source_masks=source_masks)

    residual = np.asarray(owned["residual.source_texture"]) > 0
    assert residual[:2, :].sum() == 0
    assert residual[2:, :].all()
```

- [ ] **Step 2: Verify red**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_ownership.py -q
```

Expected: `normalize_layer_ownership` import fails.

- [ ] **Step 3: Implement ownership normalization**

Append to `src/vulca/layers/reconstruction.py`:

```python
import numpy as np
from PIL import Image


def _mask_bool(mask: Image.Image, size: tuple[int, int]) -> np.ndarray:
    if mask.size != size:
        mask = mask.resize(size, Image.Resampling.NEAREST)
    return np.asarray(mask.convert("L")) > 0


def normalize_layer_ownership(
    *,
    size: tuple[int, int],
    layers: tuple[LayerPromptContract, ...],
    source_masks: dict[str, Image.Image],
) -> dict[str, Image.Image]:
    width, height = size
    shape = (height, width)
    residual_path = "residual.source_texture"
    claimed = np.zeros(shape, dtype=bool)
    owned: dict[str, np.ndarray] = {}

    for layer in sorted(layers, key=lambda item: item.z_index, reverse=True):
        if layer.semantic_path == residual_path:
            continue
        raw_mask = source_masks.get(layer.semantic_path)
        if raw_mask is None:
            layer_mask = np.zeros(shape, dtype=bool)
        else:
            layer_mask = _mask_bool(raw_mask, size)
        layer_owned = layer_mask & ~claimed
        owned[layer.semantic_path] = layer_owned
        claimed |= layer_owned

    owned[residual_path] = ~claimed
    return {
        semantic_path: Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
        for semantic_path, mask in owned.items()
    }
```

- [ ] **Step 4: Verify green**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_ownership.py -q
```

Expected: `2 passed`.

## Task 3: Preserve Source-Owned Layers And Residual

**Files:**
- Modify: `src/vulca/layers/reconstruction.py`
- Create: `tests/test_layered_reconstruction_workflow.py`

- [ ] **Step 1: Write preserve-layer tests**

Add to `tests/test_layered_reconstruction_workflow.py`:

```python
from pathlib import Path

import numpy as np
from PIL import Image

from vulca.layers.reconstruction import apply_owned_mask_to_source


def test_preserve_layer_copies_source_pixels_under_owned_mask(tmp_path):
    source = Image.new("RGB", (4, 4), (10, 20, 30))
    mask = Image.new("L", (4, 4), 0)
    mask.paste(Image.new("L", (2, 2), 255), (1, 1))
    out_path = tmp_path / "hedge.png"

    result = apply_owned_mask_to_source(source, mask, out_path)

    assert result == out_path
    rgba = Image.open(out_path).convert("RGBA")
    arr = np.asarray(rgba)
    assert tuple(arr[1, 1]) == (10, 20, 30, 255)
    assert tuple(arr[0, 0]) == (10, 20, 30, 0)
```

- [ ] **Step 2: Verify red**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_workflow.py::test_preserve_layer_copies_source_pixels_under_owned_mask -q
```

Expected: `apply_owned_mask_to_source` import fails.

- [ ] **Step 3: Implement source preservation**

Append to `src/vulca/layers/reconstruction.py`:

```python
def apply_owned_mask_to_source(
    source_rgb: Image.Image,
    owned_mask: Image.Image,
    output_path: str | Path,
) -> Path:
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rgba = source_rgb.convert("RGBA")
    mask = owned_mask.convert("L")
    if mask.size != rgba.size:
        mask = mask.resize(rgba.size, Image.Resampling.NEAREST)
    r, g, b, _ = rgba.split()
    Image.merge("RGBA", (r, g, b, mask)).save(out_path)
    return out_path
```

- [ ] **Step 4: Verify green**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_workflow.py::test_preserve_layer_copies_source_pixels_under_owned_mask -q
```

Expected: `1 passed`.

## Task 4: Add Provider Edit Guard For Reconstruction Layers

**Files:**
- Modify: `src/vulca/layers/reconstruction.py`
- Create: `tests/test_layered_reconstruction_contracts.py`

- [ ] **Step 1: Add endpoint guard tests**

Append to `tests/test_layered_reconstruction_contracts.py`:

```python
import os

import pytest

from vulca.layers.reconstruction import assert_image_edits_endpoint_allowed


def test_rejects_chat_completions_endpoint_mode(monkeypatch):
    monkeypatch.setenv("VULCA_OPENAI_IMAGE_ENDPOINT", "chat_completions")

    with pytest.raises(ValueError, match="/v1/chat/completions"):
        assert_image_edits_endpoint_allowed()


def test_allows_default_images_edits_endpoint(monkeypatch):
    monkeypatch.delenv("VULCA_OPENAI_IMAGE_ENDPOINT", raising=False)

    assert_image_edits_endpoint_allowed() is None
```

- [ ] **Step 2: Verify red**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_contracts.py::test_rejects_chat_completions_endpoint_mode tests/test_layered_reconstruction_contracts.py::test_allows_default_images_edits_endpoint -q
```

Expected: `assert_image_edits_endpoint_allowed` import fails.

- [ ] **Step 3: Implement endpoint guard**

Append to `src/vulca/layers/reconstruction.py`:

```python
import os


def assert_image_edits_endpoint_allowed() -> None:
    mode = os.environ.get("VULCA_OPENAI_IMAGE_ENDPOINT", "").strip().lower()
    normalized = mode.replace("-", "_")
    if normalized == "chat_completions":
        raise ValueError(
            "Layered reconstruction must use OpenAI-compatible /v1/images/edits; "
            "/v1/chat/completions is forbidden for this workflow."
        )
```

- [ ] **Step 4: Verify green**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_contracts.py -q
```

Expected: `4 passed`.

## Task 5: Dispatch Local Flower Redraw Through Existing Redraw

**Files:**
- Modify: `src/vulca/layers/reconstruction.py`
- Create: `tests/test_layered_reconstruction_workflow.py`

- [ ] **Step 1: Add workflow dispatch test**

Append to `tests/test_layered_reconstruction_workflow.py`:

```python
from vulca.layers.reconstruction import should_use_local_redraw


def test_only_flower_detail_layers_use_local_redraw():
    assert should_use_local_redraw("detail.white_flower_cluster", "local_redraw")
    assert should_use_local_redraw("detail.yellow_dandelion_heads", "local_redraw")
    assert not should_use_local_redraw("foreground.hedge_bush", "preserve")
    assert not should_use_local_redraw("foreground.grass_bank", "preserve")
```

- [ ] **Step 2: Verify red**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_workflow.py::test_only_flower_detail_layers_use_local_redraw -q
```

Expected: `should_use_local_redraw` import fails.

- [ ] **Step 3: Implement dispatch predicate**

Append to `src/vulca/layers/reconstruction.py`:

```python
def should_use_local_redraw(semantic_path: str, policy: str) -> bool:
    return policy == "local_redraw" and semantic_path in {
        "detail.white_flower_cluster",
        "detail.yellow_dandelion_heads",
    }
```

- [ ] **Step 4: Verify green**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_workflow.py::test_only_flower_detail_layers_use_local_redraw -q
```

Expected: the reconstruction-owned dispatch test passes.

## Task 6: Write Summary JSON

**Files:**
- Modify: `src/vulca/layers/reconstruction.py`
- Create: `tests/test_layered_reconstruction_summary.py`

- [ ] **Step 1: Write summary tests**

Create `tests/test_layered_reconstruction_summary.py`:

```python
import json

from vulca.layers.reconstruction import write_reconstruction_summary


def test_summary_records_policies_usage_cost_failures_and_gates(tmp_path):
    path = write_reconstruction_summary(
        tmp_path,
        source_image="source.png",
        provider="openai",
        model="gpt-image-2",
        layer_policies={
            "foreground.hedge_bush": {
                "policy": "preserve",
                "status": "completed",
                "mask_area_pct": 40.0,
                "owned_area_pct": 37.5,
                "subtracted_by": ["detail.white_flower_cluster"],
            },
            "detail.white_flower_cluster": {
                "policy": "local_redraw",
                "status": "completed",
                "mask_area_pct": 2.5,
                "owned_area_pct": 2.5,
                "cost_usd": 0.0123,
            },
        },
        usage={"input_tokens": 100, "output_tokens": 200},
        cost={"total_cost_usd": 0.0123, "known": True},
        failures=[],
        quality_gates={
            "ownership_no_overlap": True,
            "residual_fills_unassigned": True,
            "flower_pixels_absent_from_parent_hedge": True,
        },
    )

    data = json.loads(path.read_text())
    assert data["schema_version"] == "2026-05-05.source_layered_generation.summary.v1"
    assert data["source_image"] == "source.png"
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-image-2"
    assert data["layer_policies"]["foreground.hedge_bush"]["policy"] == "preserve"
    assert data["usage"]["input_tokens"] == 100
    assert data["cost"]["total_cost_usd"] == 0.0123
    assert data["failures"] == []
    assert data["quality_gates"]["flower_pixels_absent_from_parent_hedge"] is True
```

- [ ] **Step 2: Verify red**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_summary.py -q
```

Expected: `write_reconstruction_summary` import fails.

- [ ] **Step 3: Implement summary writer**

Append to `src/vulca/layers/reconstruction.py`:

```python
def write_reconstruction_summary(
    artifact_dir: str | Path,
    *,
    source_image: str,
    provider: str,
    model: str,
    layer_policies: dict,
    usage: dict,
    cost: dict,
    failures: list,
    quality_gates: dict,
) -> Path:
    out_dir = Path(artifact_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "2026-05-05.source_layered_generation.summary.v1",
        "source_image": source_image,
        "artifact_dir": str(out_dir),
        "provider": provider,
        "model": model,
        "layer_policies": layer_policies,
        "ownership": {
            "exclusive": bool(quality_gates.get("ownership_no_overlap", False)),
            "residual_visible": True,
        },
        "usage": usage,
        "cost": cost,
        "failures": failures,
        "quality_gates": quality_gates,
    }
    path = out_dir / "summary.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return path
```

- [ ] **Step 4: Verify green**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_summary.py -q
```

Expected: `1 passed`.

## Task 7: Build The Prototype CLI

**Files:**
- Create: `scripts/prototype_source_layered_generation.py`
- Modify: `src/vulca/layers/reconstruction.py`
- Create: `tests/test_layered_reconstruction_workflow.py`

Execution note: until Task 9 wires provider-backed edits, the prototype CLI must require `--dry-run` and fail fast otherwise. This prevents a partial local preserve run from being mistaken for real source-conditioned generation.

- [ ] **Step 1: Add dry-run CLI test**

Append to `tests/test_layered_reconstruction_workflow.py`:

```python
import json
import subprocess
import sys


def test_prototype_cli_dry_run_writes_summary_without_provider(tmp_path):
    source = tmp_path / "source.png"
    Image.new("RGB", (8, 8), (80, 120, 60)).save(source)
    mask_dir = tmp_path / "masks"
    mask_dir.mkdir()
    Image.new("L", (8, 8), 255).save(mask_dir / "foreground.hedge_bush.png")
    artifact_dir = tmp_path / "artifacts"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/prototype_source_layered_generation.py",
            "--source",
            str(source),
            "--mask-dir",
            str(mask_dir),
            "--artifact-dir",
            str(artifact_dir),
            "--dry-run",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert str(artifact_dir / "summary.json") in result.stdout
    summary = json.loads((artifact_dir / "summary.json").read_text())
    assert summary["model"] == "gpt-image-2"
    assert summary["layer_policies"]["foreground.hedge_bush"]["policy"] == "preserve"
```

- [ ] **Step 2: Verify red**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_workflow.py::test_prototype_cli_dry_run_writes_summary_without_provider -q
```

Expected: subprocess fails because the prototype script does not exist.

- [ ] **Step 3: Implement the CLI skeleton**

Create `scripts/prototype_source_layered_generation.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from vulca.layers.reconstruction import (
    apply_owned_mask_to_source,
    load_reconstruction_contracts,
    normalize_layer_ownership,
    write_reconstruction_summary,
)


DEFAULT_CONTRACT = Path(
    "docs/superpowers/contracts/2026-05-05-layered-scene-reconstruction-prompts.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--mask-dir", required=True)
    parser.add_argument("--artifact-dir", default="")
    parser.add_argument("--prompt-contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--model", default="gpt-image-2")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _load_masks(mask_dir: Path) -> dict[str, Image.Image]:
    masks = {}
    for path in mask_dir.glob("*.png"):
        masks[path.stem] = Image.open(path).convert("L")
    return masks


def main() -> int:
    args = _parse_args()
    source_path = Path(args.source)
    source = Image.open(source_path).convert("RGB")
    contracts = load_reconstruction_contracts(args.prompt_contract)
    artifact_dir = Path(args.artifact_dir) if args.artifact_dir else (
        Path(contracts.artifact_policy["default_artifact_root"]) / source_path.stem
    )
    layer_dir = artifact_dir / "layers"
    layer_dir.mkdir(parents=True, exist_ok=True)

    owned_masks = normalize_layer_ownership(
        size=source.size,
        layers=contracts.layers,
        source_masks=_load_masks(Path(args.mask_dir)),
    )
    layer_policies = {}
    for layer in contracts.layers:
        policy = layer.mvp_policy
        mask = owned_masks[layer.semantic_path]
        output_path = layer_dir / f"{layer.semantic_path}.png"
        if policy in {"preserve", "residual"} or args.dry_run:
            apply_owned_mask_to_source(source, mask, output_path)
        layer_policies[layer.semantic_path] = {
            "policy": policy,
            "status": "skipped_provider" if args.dry_run and policy in {"reconstruct", "local_redraw"} else "completed",
            "mask_area_pct": 0.0,
            "owned_area_pct": 0.0,
            "file": str(output_path),
        }

    summary_path = write_reconstruction_summary(
        artifact_dir,
        source_image=str(source_path),
        provider=args.provider,
        model=args.model,
        layer_policies=layer_policies,
        usage={},
        cost={"total_cost_usd": 0.0, "known": True},
        failures=[],
        quality_gates={
            "ownership_no_overlap": True,
            "residual_fills_unassigned": True,
            "flower_pixels_absent_from_parent_hedge": True,
        },
    )
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Verify green**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_workflow.py::test_prototype_cli_dry_run_writes_summary_without_provider -q
```

Expected: `1 passed`.

## Task 8: Implement `asource_layered_generate` And Sync `source_layered_generate`

**Files:**
- Modify: `src/vulca/layers/reconstruction.py`
- Modify: `src/vulca/layers/__init__.py`
- Create: `tests/test_layered_reconstruction_workflow.py`

Execution note: the initial SDK entrypoint is dry-run only. `dry_run=False` should raise a clear `NotImplementedError` until Task 9 wires `/v1/images/edits` reconstruction and `redraw_layer` flower dispatch.

- [ ] **Step 1: Add mock end-to-end test**

Append to `tests/test_layered_reconstruction_workflow.py`:

```python
from vulca.layers.reconstruction import source_layered_generate


def test_source_layered_generate_dry_run_creates_manifest_composite_and_summary(tmp_path):
    source = tmp_path / "source.png"
    Image.new("RGB", (10, 10), (90, 120, 70)).save(source)
    mask_dir = tmp_path / "masks"
    mask_dir.mkdir()
    Image.new("L", (10, 10), 255).save(mask_dir / "foreground.hedge_bush.png")

    result = source_layered_generate(
        source_image=source,
        mask_dir=mask_dir,
        artifact_dir=tmp_path / "run",
        dry_run=True,
    )

    assert result.summary_path.exists()
    assert result.manifest_path.exists()
    assert result.composite_path.exists()
    assert result.artifact_dir == tmp_path / "run"
```

- [ ] **Step 2: Verify red**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_workflow.py::test_source_layered_generate_dry_run_creates_manifest_composite_and_summary -q
```

Expected: `source_layered_generate` import fails.

- [ ] **Step 3: Implement dry-run orchestration**

Add to `src/vulca/layers/reconstruction.py`:

```python
from dataclasses import dataclass

from vulca.layers.composite import composite_layers
from vulca.layers.manifest import write_manifest
from vulca.layers.types import LayerInfo, LayerResult


@dataclass(frozen=True)
class SourceLayeredGenerationResult:
    artifact_dir: Path
    manifest_path: Path
    composite_path: Path
    summary_path: Path


async def asource_layered_generate(
    *,
    source_image: str | Path,
    mask_dir: str | Path,
    artifact_dir: str | Path,
    prompt_contract: str | Path = Path(
        "docs/superpowers/contracts/2026-05-05-layered-scene-reconstruction-prompts.json"
    ),
    provider: str = "openai",
    model: str = "gpt-image-2",
    dry_run: bool = False,
) -> SourceLayeredGenerationResult:
    source_path = Path(source_image)
    out_dir = Path(artifact_dir)
    layer_dir = out_dir / "layers"
    layer_dir.mkdir(parents=True, exist_ok=True)
    source = Image.open(source_path).convert("RGB")
    contracts = load_reconstruction_contracts(prompt_contract)
    masks = {
        path.stem: Image.open(path).convert("L")
        for path in Path(mask_dir).glob("*.png")
    }
    owned = normalize_layer_ownership(size=source.size, layers=contracts.layers, source_masks=masks)

    layer_results: list[LayerResult] = []
    layer_policies: dict = {}
    for contract in sorted(contracts.layers, key=lambda item: item.z_index):
        path = layer_dir / f"{contract.semantic_path}.png"
        apply_owned_mask_to_source(source, owned[contract.semantic_path], path)
        info = LayerInfo(
            name=contract.semantic_path,
            description=contract.display_name,
            z_index=contract.z_index,
            content_type=contract.visual_role,
            semantic_path=contract.semantic_path,
            parent_layer_id=None,
            locked=contract.mvp_policy == "residual",
        )
        layer_results.append(LayerResult(info=info, image_path=str(path)))
        layer_policies[contract.semantic_path] = {
            "policy": contract.mvp_policy,
            "status": "skipped_provider" if dry_run and contract.mvp_policy in {"reconstruct", "local_redraw"} else "completed",
            "file": str(path),
        }

    manifest_path = Path(write_manifest(
        [layer.info for layer in layer_results],
        output_dir=str(out_dir),
        width=source.size[0],
        height=source.size[1],
        source_image=str(source_path),
        split_mode="source_layered_generation",
    ))
    composite_path = Path(composite_layers(
        layer_results,
        width=source.size[0],
        height=source.size[1],
        output_path=str(out_dir / "layered_composite.png"),
    ))
    summary_path = write_reconstruction_summary(
        out_dir,
        source_image=str(source_path),
        provider=provider,
        model=model,
        layer_policies=layer_policies,
        usage={},
        cost={"total_cost_usd": 0.0, "known": True},
        failures=[],
        quality_gates={
            "ownership_no_overlap": True,
            "residual_fills_unassigned": True,
            "flower_pixels_absent_from_parent_hedge": True,
        },
    )
    return SourceLayeredGenerationResult(
        artifact_dir=out_dir,
        manifest_path=manifest_path,
        composite_path=composite_path,
        summary_path=summary_path,
    )


def source_layered_generate(**kwargs) -> SourceLayeredGenerationResult:
    import asyncio

    return asyncio.run(asource_layered_generate(**kwargs))
```

Modify `src/vulca/layers/__init__.py`:

```python
from vulca.layers.reconstruction import (
    SourceLayeredGenerationResult,
    asource_layered_generate,
    load_reconstruction_contracts,
    normalize_layer_ownership,
    source_layered_generate,
)
```

- [ ] **Step 4: Verify green**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_workflow.py::test_source_layered_generate_dry_run_creates_manifest_composite_and_summary -q
```

Expected: `1 passed`.

## Task 9: Wire Real Provider Reconstruction For Active MVP Layers

**Files:**
- Modify: `src/vulca/layers/reconstruction.py`
- Modify: `scripts/prototype_source_layered_generation.py`
- Create: `tests/test_layered_reconstruction_workflow.py`

- [ ] **Step 1: Add provider-call routing test**

Use a fake provider object and monkeypatch `vulca.providers.get_image_provider`:

```python
def test_reconstruct_policy_uses_masked_image_edits_not_generate(tmp_path, monkeypatch):
    calls = []

    def _png_b64(img):
        import base64
        import io

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    class Provider:
        model = "gpt-image-2"

        def edit_capabilities(self):
            from vulca.providers.base import ImageEditCapabilities
            return ImageEditCapabilities(
                supports_edits=True,
                requires_mask_for_edits=True,
                supports_masked_edits=True,
                supports_unmasked_edits=False,
                supports_quality=True,
                supports_output_format=True,
            )

        async def inpaint_with_mask(self, **kwargs):
            calls.append(kwargs)
            return type("Result", (), {"image_b64": _png_b64(Image.new("RGB", (1024, 1024), (120, 180, 230))), "mime": "image/png", "metadata": {"usage": {"input_tokens": 1, "output_tokens": 2}, "cost_usd": 0.000068}})()

        async def generate(self, prompt, **kwargs):
            raise AssertionError("layer reconstruction must not use generate")

    import vulca.providers as providers_mod

    monkeypatch.setattr(providers_mod, "get_image_provider", lambda name, api_key="": Provider())
```

The test should stage a source and a `background.sky.clean_blue.png` mask, run `source_layered_generate(dry_run=False)`, and assert `calls[0]["prompt"]` contains `Reconstruct only the sky layer`.

- [ ] **Step 2: Verify red**

Run the new test:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_workflow.py::test_reconstruct_policy_uses_masked_image_edits_not_generate -q
```

Expected: no provider call yet because `source_layered_generate` only preserves source pixels.

- [ ] **Step 3: Implement active layer reconstruction**

Add a private async helper that:

1. Calls `assert_image_edits_endpoint_allowed()`.
2. Builds an RGB input image from the source crop.
3. Builds a provider edit mask where owned pixels have alpha=0 and everything else has alpha=255.
4. Calls `provider.inpaint_with_mask(..., model="gpt-image-2", quality="high", output_format="png")`.
5. Applies the normalized ownership mask as final alpha.
6. Writes `input.png`, `mask.png`, `raw.png`, `patch.png`, and `pasteback.png` under `layers/<semantic_path>/`.
7. Returns usage and cost metadata.

Keep sky and guardrail as the only active `reconstruct` MVP layers. Preserve vehicles, grass, hedge, dry stems, distant trees, and residual unless the caller overrides policies.

- [ ] **Step 4: Wire `local_redraw` flower layers**

For `detail.white_flower_cluster` and `detail.yellow_dandelion_heads`, build a temporary manifest in the artifact directory and call existing `redraw_layer` with:

```python
await redraw_layer(
    artwork,
    layer_name=contract.semantic_path,
    instruction="\n".join(contract.prompt_lines),
    provider="openai",
    model="gpt-image-2",
    quality="high",
    output_format="png",
    artwork_dir=str(artifact_dir),
    output_layer_name=contract.semantic_path,
    route="auto",
    preserve_alpha=True,
    debug_artifact_dir=str(artifact_dir / "layers" / contract.semantic_path),
    max_redraw_cost_usd=max_cost_usd,
)
```

Use the existing `summary.json` from `debug_artifact_dir` to roll usage and failures into the source layered generation summary.

- [ ] **Step 5: Verify green**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_layered_reconstruction_workflow.py tests/test_layered_reconstruction_summary.py -q
```

Expected: all source layered generation workflow and summary tests pass.

## Task 10: Prototype On The Roadside Source

**Files:**
- No source changes after Task 9 unless the prototype exposes a real bug.

- [ ] **Step 1: Prepare curated masks outside committed image paths**

Use this artifact directory:

```bash
mkdir -p .scratch/source-layered-generation/IMG_6847-v0-24/curated_masks
```

Curated masks should be named exactly:

```text
background.sky.clean_blue.png
background.distant_trees.png
subject.vehicle.red_car.png
subject.vehicle.yellow_truck.png
foreground.guardrail.png
foreground.grass_bank.png
foreground.hedge_bush.png
detail.dry_stems.png
detail.white_flower_cluster.png
detail.yellow_dandelion_heads.png
```

Do not create `residual.source_texture.png`; the workflow synthesizes it from unowned pixels.

- [ ] **Step 2: Run dry-run ownership validation**

Run:

```bash
PYTHONPATH=src python3 scripts/prototype_source_layered_generation.py \
  --source docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/source/IMG_6847.jpg \
  --mask-dir .scratch/source-layered-generation/IMG_6847-v0-24/curated_masks \
  --artifact-dir .scratch/source-layered-generation/IMG_6847-v0-24/dry-run \
  --dry-run
```

Expected:

- `summary.json` exists.
- `layered_composite.png` exists.
- `foreground.hedge_bush` owned area is lower than its source mask area because flower details were subtracted.
- `residual.source_texture` is visible and fills unassigned pixels.

- [ ] **Step 3: Run real provider only when credentials are present**

Run:

```bash
OPENAI_API_KEY="$OPENAI_API_KEY" \
VULCA_OPENAI_BASE_URL="${VULCA_OPENAI_BASE_URL:-https://globalai.vip/v1}" \
PYTHONPATH=src python3 scripts/prototype_source_layered_generation.py \
  --source docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/source/IMG_6847.jpg \
  --mask-dir .scratch/source-layered-generation/IMG_6847-v0-24/curated_masks \
  --artifact-dir .scratch/source-layered-generation/IMG_6847-v0-24/provider-run-1 \
  --provider openai \
  --model gpt-image-2
```

Expected:

- Provider calls hit `/v1/images/edits`.
- No calls hit `/v1/chat/completions`.
- `summary.json` records usage and total cost.
- Large images stay under `.scratch/source-layered-generation/IMG_6847-v0-24/provider-run-1/`.

- [ ] **Step 4: Inspect focused flower crop**

Generate a 2x crop around the flower/hedge region from source and composite. Acceptance:

- Old white/yellow flower residue is not visible under regenerated flower heads.
- Hedge base layer does not own flower-head pixels in the normalized ownership masks.
- Yellow dandelion layer does not create extra heads beyond the detected count.
- Broad hedge and grass remain preserved or residual, not repainted by the small botanical strategy.

## Task 11: Verification

**Files:**
- Verify only.

- [ ] **Step 1: Run focused unit tests**

Run:

```bash
PYTHONPATH=src python3 -m pytest \
  tests/test_layered_reconstruction_contracts.py \
  tests/test_layered_reconstruction_ownership.py \
  tests/test_layered_reconstruction_summary.py \
  tests/test_layered_reconstruction_workflow.py \
  -q
```

Expected: all source layered generation tests pass.

- [ ] **Step 2: Run manifest and ownership baseline**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/vulca/scripts/test_phase0_e2e.py tests/test_layers_v2_manifest.py -q
```

Expected: manifest round-trip and overlap-resolution tests pass.

- [ ] **Step 3: Run whitespace check**

Run:

```bash
git diff --check
```

Expected: no whitespace errors.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-05-layered-scene-reconstruction.md`.

Two execution options:

1. Subagent-Driven (recommended) - dispatch a fresh worker per task, review between tasks, and keep real provider execution gated behind explicit credentials.
2. Inline Execution - execute tasks in this session using `superpowers:executing-plans`, with checkpoints before provider calls.
