# PPT Run 2.51 Editorial Copy And Shape Text Sockets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Run 2.51 data/workflow repair pass that prepares editorial copy memory, shape text socket memory, and renderer archetype gates for the next generated PPT rerun.

**Architecture:** Follow the existing Run 2.49 data-only builder pattern. Add one Python builder that reads Run 2.49/2.50 source context, writes three Run 2.51 JSON artifacts plus result JSON/Markdown, extends `skill_workflow.json`, and updates the HTML viewer Data / Skill tab. Do not add Run 2.51 to `RUN_SPECS`, do not create PPTX files, and do not claim visual repair is validated before a generated rerun consumes these artifacts.

**Tech Stack:** Python 3.11+, pytest, existing JSON case-pack artifacts under `docs/product/ppt-run2-data-skill-quality`, existing viewer builder `scripts/build_ppt_run_html_viewer.py`, ruff.

---

## File Structure

- Create `scripts/build_ppt_run2_51_editorial_copy_shape_sockets.py`
  - Responsibility: validate Run 2.49/2.50 inputs, build three Run 2.51 data/workflow artifacts, write result JSON/Markdown, and enforce no PPT artifacts.
- Create `docs/product/ppt-run2-data-skill-quality/run2_51_editorial_copy_memory.json`
  - Responsibility: six public-facing display copy records, one per slide role.
- Create `docs/product/ppt-run2-data-skill-quality/run2_51_shape_text_socket_memory.json`
  - Responsibility: six shape/text socket records, one per slide role.
- Create `docs/product/ppt-run2-data-skill-quality/run2_51_renderer_archetype_workflow_gates.json`
  - Responsibility: six renderer gates that the next generated full arm must consume.
- Create `docs/product/ppt-run2-data-skill-quality/results/run2_51_editorial_shape_text_repair_result.json`
  - Responsibility: machine-readable result summary for Run 2.51.
- Create `docs/product/ppt-run2-data-skill-quality/results/run2_51_editorial_shape_text_repair_result.md`
  - Responsibility: human-readable boundary and next-action report.
- Modify `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
  - Responsibility: add three Run 2.51 workflow stages after Run 2.50 consumption proof.
- Modify `scripts/build_ppt_run_html_viewer.py`
  - Responsibility: read Run 2.51 artifacts, expose them in Data / Skill, keep latest generated run at 2.50.
- Modify `tests/test_ppt_run2_data_skill_quality.py`
  - Responsibility: add focused tests for builder outputs, existing artifacts, workflow stages, viewer embedding, and no generated deck.

## Constants

Use these exact shared values across builder and tests:

```python
RUN_ID = "2.51"
SELECTED_USECASE_ID = "usecase_design_to_production_platform_launch"
TARGET_LAYER = "editorial_copy_and_shape_text_socket_repair"
STATUS = "run2_51_editorial_shape_text_repair_ready_public_blocked"
COPY_STATUS = "run2_51_editorial_copy_memory_ready_public_blocked"
SOCKET_STATUS = "run2_51_shape_text_socket_memory_ready_public_blocked"
GATE_STATUS = "run2_51_renderer_archetype_workflow_gates_ready_public_blocked"
NEXT_ACTION = "consume_run2_51_before_run2_52_four_arm_rerun"
NEXT_RERUN_CONTRACT = "must_be_consumed_before_run2_52_four_arm_rerun"
ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]
FORBIDDEN_PUBLIC_TERMS = [
    "run2",
    "memory",
    "workflow gate",
    "trace",
    "audit",
    "negative control",
    "public blocked",
]
```

Use these role archetypes:

```python
ROLE_ARCHETYPES = {
    "cover": {
        "primary_archetype": "poster_stage",
        "required_sockets": ["headline_plane", "hero_object_caption", "proof_badge", "source_boundary_whisper"],
        "shape_primitives": ["stage", "spotlight", "stamp_badge", "ribbon"],
    },
    "setup": {
        "primary_archetype": "route_map",
        "required_sockets": ["failure_path_title", "route_node_labels", "break_risk_marker", "selected_route_claim"],
        "shape_primitives": ["route_path", "bracket_callout", "stamp_badge", "depth_stack"],
    },
    "contrast": {
        "primary_archetype": "before_after_lens",
        "required_sockets": ["before_caption", "after_claim", "delta_marker", "implication_line"],
        "shape_primitives": ["lens", "route_path", "bracket_callout", "spotlight"],
    },
    "proof": {
        "primary_archetype": "workspace_surface",
        "required_sockets": ["workspace_title", "lane_labels", "proof_nuggets", "inspectable_object_captions"],
        "shape_primitives": ["stage", "depth_stack", "bracket_callout", "stamp_badge"],
    },
    "climax": {
        "primary_archetype": "exploded_hero_object",
        "required_sockets": ["result_headline", "exploded_proof_tags", "release_boundary_tag", "memory_route_label"],
        "shape_primitives": ["exploded_layers", "spotlight", "ribbon", "bracket_callout"],
    },
    "close": {
        "primary_archetype": "decision_room",
        "required_sockets": ["decision_headline", "gate_labels", "next_action_strip", "residual_blocker_caption"],
        "shape_primitives": ["decision_wall", "route_path", "ribbon", "stamp_badge"],
    },
}
```

Use these copy budgets:

```python
COPY_BUDGETS = {
    "headline": {"max_words": 7, "max_chars": 48, "max_lines": 2},
    "subline": {"max_words": 18, "max_chars": 120, "max_lines": 3},
    "proof_nugget": {"max_words": 8, "max_chars": 54, "max_lines": 2},
    "annotation": {"max_words": 6, "max_chars": 42, "max_lines": 2},
    "state_label": {"max_words": 4, "max_chars": 28, "max_lines": 1},
}
```

---

### Task 1: Add Failing Tests For The Run 2.51 Builder

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create in Task 2: `scripts/build_ppt_run2_51_editorial_copy_shape_sockets.py`

- [ ] **Step 1: Add test constants near the other Run 2 constants**

Add this near the existing expected Run 2 constants:

```python
EXPECTED_RUN2_51_ROLES = {"cover", "setup", "contrast", "proof", "climax", "close"}
EXPECTED_RUN2_51_COPY_BUNDLE_KEYS = {
    "headline",
    "subline",
    "proof_nuggets",
    "annotations",
    "state_labels",
}
EXPECTED_RUN2_51_TRACE_FIELDS = {
    "run2_51_editorial_copy_memory_id",
    "run2_51_shape_text_socket_memory_id",
    "run2_51_renderer_archetype_gate_id",
    "run2_51_primary_archetype",
    "run2_51_public_surface_copy_status",
    "run2_51_text_socket_placement_status",
    "run2_51_shape_vocabulary_status",
    "run2_51_character_fit_status",
    "run2_51_forbidden_surface_terms_count",
    "run2_51_equal_card_cluster_count",
    "run2_51_semantic_primitive_count",
}
EXPECTED_RUN2_51_FORBIDDEN_PUBLIC_TERMS = {
    "run2",
    "memory",
    "workflow gate",
    "trace",
    "audit",
    "negative control",
    "public blocked",
}
```

- [ ] **Step 2: Add local assertion helpers for copy budgets**

Add these helpers near existing helper functions in `tests/test_ppt_run2_data_skill_quality.py`:

```python
def word_count(value: str) -> int:
    return len([part for part in re.split(r"\s+", value.strip()) if part])


def public_text_values(bundle: dict[str, object]) -> list[str]:
    values: list[str] = []
    for key in ("headline", "subline"):
        value = bundle.get(key)
        if isinstance(value, str):
            values.append(value)
    for key in ("proof_nuggets", "annotations", "state_labels"):
        items = bundle.get(key)
        if isinstance(items, list):
            values.extend(str(item) for item in items)
    return values
```

- [ ] **Step 3: Add the failing builder test**

Append this after the Run 2.50 tests:

```python
def test_run2_51_builder_creates_editorial_copy_shape_socket_repair_pack(tmp_path: Path) -> None:
    script_path = ROOT / "scripts" / "build_ppt_run2_51_editorial_copy_shape_sockets.py"
    result_json = tmp_path / "run2_51_editorial_shape_text_repair_result.json"
    result_md = tmp_path / "run2_51_editorial_shape_text_repair_result.md"
    presentations = ROOT / "outputs" / "019e7d9c-532a-70b3-8892-fa3ae42baef2" / "presentations"
    pptx_before = sorted(path.name for path in presentations.glob("*2-51*.pptx"))

    assert script_path.exists(), "missing Run 2.51 editorial copy/shape socket builder"
    body = script_path.read_text(encoding="utf-8")
    assert "presentation_artifact_tool" not in body
    assert "pptxgen" not in body.lower()
    assert "slide.shapes" not in body
    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--out-dir",
            str(tmp_path),
            "--result-json",
            str(result_json),
            "--result-md",
            str(result_md),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    pptx_after = sorted(path.name for path in presentations.glob("*2-51*.pptx"))
    result = load_json(result_json)
    copy_memory = load_json(tmp_path / "run2_51_editorial_copy_memory.json")
    socket_memory = load_json(tmp_path / "run2_51_shape_text_socket_memory.json")
    gates = load_json(tmp_path / "run2_51_renderer_archetype_workflow_gates.json")
    report = result_md.read_text(encoding="utf-8")

    assert "run2_51_editorial_shape_text_repair_ready_public_blocked" in completed.stdout
    assert pptx_before == pptx_after == []
    assert result["run_id"] == "2.51"
    assert result["status"] == "run2_51_editorial_shape_text_repair_ready_public_blocked"
    assert result["source_data_workflow_run"] == "2.49"
    assert result["source_generated_run"] == "2.50"
    assert result["target_layer"] == "editorial_copy_and_shape_text_socket_repair"
    assert result["creates_new_ppt_deck"] is False
    assert result["visual_validation_deferred_to_generated_rerun"] is True
    assert result["public_ready"] is False
    assert result["next_required_action"] == "consume_run2_51_before_run2_52_four_arm_rerun"
    assert result["delivery_artifacts"]["pptx_paths"] == []
    assert result["artifact_counts"] == {
        "editorial_copy_records": 6,
        "shape_text_socket_records": 6,
        "renderer_archetype_workflow_gates": 6,
    }

    assert copy_memory["status"] == "run2_51_editorial_copy_memory_ready_public_blocked"
    assert socket_memory["status"] == "run2_51_shape_text_socket_memory_ready_public_blocked"
    assert gates["status"] == "run2_51_renderer_archetype_workflow_gates_ready_public_blocked"
    assert {record["role"] for record in copy_memory["editorial_copy_records"]} == EXPECTED_RUN2_51_ROLES
    assert {record["role"] for record in socket_memory["shape_text_socket_records"]} == EXPECTED_RUN2_51_ROLES
    assert {record["role"] for record in gates["renderer_archetype_workflow_gates"]} == EXPECTED_RUN2_51_ROLES

    assert_contains(
        report,
        [
            "Run 2.51",
            "data/workflow-only",
            "editorial copy",
            "shape text sockets",
            "visual validation is deferred",
            "Run 2.52",
        ],
    )
```

- [ ] **Step 4: Run the failing test**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_51_builder_creates_editorial_copy_shape_socket_repair_pack -q
```

Expected: FAIL with `missing Run 2.51 editorial copy/shape socket builder`.

---

### Task 2: Implement The Run 2.51 Data-Only Builder

**Files:**
- Create: `scripts/build_ppt_run2_51_editorial_copy_shape_sockets.py`
- Test: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Create the builder header, constants, and IO helpers**

Create `scripts/build_ppt_run2_51_editorial_copy_shape_sockets.py` with this opening:

```python
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
PRESENTATIONS_DIR = ROOT / "outputs" / "019e7d9c-532a-70b3-8892-fa3ae42baef2" / "presentations"
DEFAULT_OUT_DIR = PACK
DEFAULT_RESULT_JSON = PACK / "results" / "run2_51_editorial_shape_text_repair_result.json"
DEFAULT_RESULT_MD = PACK / "results" / "run2_51_editorial_shape_text_repair_result.md"

RUN_ID = "2.51"
SELECTED_USECASE_ID = "usecase_design_to_production_platform_launch"
TARGET_LAYER = "editorial_copy_and_shape_text_socket_repair"
NEXT_ACTION = "consume_run2_51_before_run2_52_four_arm_rerun"
NEXT_RERUN_CONTRACT = "must_be_consumed_before_run2_52_four_arm_rerun"
ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"]
FORBIDDEN_PUBLIC_TERMS = [
    "run2",
    "memory",
    "workflow gate",
    "trace",
    "audit",
    "negative control",
    "public blocked",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def count_words(value: str) -> int:
    return len([part for part in re.split(r"\s+", value.strip()) if part])


def role_record(records: list[dict[str, Any]], role: str, key: str) -> dict[str, Any]:
    for record in records:
        if record.get("role") == role:
            return record
    raise ValueError(f"missing {key} for role {role}")
```

- [ ] **Step 2: Add role copy and archetype source data**

Add these dictionaries after the helpers:

```python
ROLE_COPY: dict[str, dict[str, Any]] = {
    "cover": {
        "headline": "Design decks people can judge",
        "subline": "Turn messy design evidence into a launch-ready presentation path.",
        "proof_nuggets": ["Real brief selected", "Evidence becomes design", "Deck stays editable"],
        "annotations": ["Usecase locked", "Public copy only", "No raw process"],
        "state_labels": ["Brief", "Learn", "Build"],
        "business_claim": "The product can convert design evidence into an editable launch presentation.",
    },
    "setup": {
        "headline": "The old path stays boxy",
        "subline": "Prompt-only decks miss the route from evidence to visual decision.",
        "proof_nuggets": ["Failure is visible", "Route is selected", "Risk is named"],
        "annotations": ["Before state", "Decision path", "Break point"],
        "state_labels": ["Fail", "Route", "Select"],
        "business_claim": "The setup slide explains the commercial failure and the selected correction route.",
    },
    "contrast": {
        "headline": "Evidence changes the surface",
        "subline": "The after state must show a business consequence, not another equal card set.",
        "proof_nuggets": ["Before is smaller", "After owns focus", "Delta is explicit"],
        "annotations": ["Before", "After", "Why it matters"],
        "state_labels": ["Before", "After", "Delta"],
        "business_claim": "The contrast slide must make the improvement legible as a business outcome.",
    },
    "proof": {
        "headline": "Proof lives inside the workspace",
        "subline": "Each proof point is attached to an inspectable object, lane, or surface.",
        "proof_nuggets": ["Decision lane", "Preview object", "Review state"],
        "annotations": ["Active lane", "Proof object", "Review state"],
        "state_labels": ["Lane", "Proof", "Review"],
        "business_claim": "The proof slide shows how evidence becomes a working presentation surface.",
    },
    "climax": {
        "headline": "One result owns the frame",
        "subline": "The peak slide needs one dominant generated result with attached proof tags.",
        "proof_nuggets": ["Result object", "Layered proof", "Release boundary"],
        "annotations": ["Large result", "Proof tag", "Boundary"],
        "state_labels": ["Result", "Proof", "Gate"],
        "business_claim": "The climax slide must focus attention on the generated result and its evidence.",
    },
    "close": {
        "headline": "Ship only after the gate",
        "subline": "The handoff makes next action clear while release remains blocked.",
        "proof_nuggets": ["Decision wall", "Next action", "Residual blocker"],
        "annotations": ["Decision", "Next step", "Blocked item"],
        "state_labels": ["Gate", "Next", "Hold"],
        "business_claim": "The close slide turns evaluation into a clear release decision.",
    },
}

COPY_BUDGETS = {
    "headline": {"max_words": 7, "max_chars": 48, "max_lines": 2},
    "subline": {"max_words": 18, "max_chars": 120, "max_lines": 3},
    "proof_nugget": {"max_words": 8, "max_chars": 54, "max_lines": 2},
    "annotation": {"max_words": 6, "max_chars": 42, "max_lines": 2},
    "state_label": {"max_words": 4, "max_chars": 28, "max_lines": 1},
}
```

Add the `ROLE_ARCHETYPES` dictionary from the Constants section above.

- [ ] **Step 3: Add input validation and no-deck guard**

Add:

```python
def assert_no_run251_deck_artifacts() -> None:
    if not PRESENTATIONS_DIR.exists():
        return
    deck_paths = sorted(
        path
        for pattern in ("*2-51*.ppt", "*2-51*.pptx")
        for path in PRESENTATIONS_DIR.glob(pattern)
    )
    if deck_paths:
        names = ", ".join(path.name for path in deck_paths)
        raise ValueError(f"Run 2.51 is data/workflow-only and must not create PPT artifacts: {names}")


def validate_inputs(
    run249_result: dict[str, Any],
    run249_readability: dict[str, Any],
    run249_density: dict[str, Any],
    run249_gates: dict[str, Any],
    run250_result: dict[str, Any],
) -> None:
    if run249_result.get("status") != "run2_49_readability_content_density_renderer_repair_ready_public_blocked":
        raise ValueError("Run 2.51 requires Run 2.49 repair result")
    if run249_readability.get("status") != "run2_49_readability_memory_ready_public_blocked":
        raise ValueError("Run 2.51 requires Run 2.49 readability memory")
    if run249_density.get("status") != "run2_49_content_evidence_density_memory_ready_public_blocked":
        raise ValueError("Run 2.51 requires Run 2.49 content evidence density memory")
    if run249_gates.get("status") != "run2_49_editorial_renderer_workflow_gates_ready_public_blocked":
        raise ValueError("Run 2.51 requires Run 2.49 renderer gates")
    if run250_result.get("status") != "run2_50_readability_density_renderer_rerun_public_blocked":
        raise ValueError("Run 2.51 requires Run 2.50 generated proof result")
    if (run250_result.get("quality_delta") or {}).get("source_data_status") != (
        "run2_49_repair_pack_consumed_before_native_ppt_drawing"
    ):
        raise ValueError("Run 2.50 must consume Run 2.49 before Run 2.51 can repair copy/socket workflow")
    if len(run249_readability.get("readability_records") or []) != 6:
        raise ValueError("Run 2.51 expected six readability records")
    if len(run249_density.get("content_evidence_density_records") or []) != 6:
        raise ValueError("Run 2.51 expected six content density records")
    if len(run249_gates.get("editorial_renderer_workflow_gates") or []) != 6:
        raise ValueError("Run 2.51 expected six renderer gates")
```

- [ ] **Step 4: Add budget validation**

Add:

```python
def assert_copy_fits_budget(role: str, bundle: dict[str, Any]) -> None:
    headline = bundle["headline"]
    subline = bundle["subline"]
    if count_words(headline) > COPY_BUDGETS["headline"]["max_words"]:
        raise ValueError(f"{role} headline exceeds word budget")
    if len(headline) > COPY_BUDGETS["headline"]["max_chars"]:
        raise ValueError(f"{role} headline exceeds character budget")
    if count_words(subline) > COPY_BUDGETS["subline"]["max_words"]:
        raise ValueError(f"{role} subline exceeds word budget")
    if len(subline) > COPY_BUDGETS["subline"]["max_chars"]:
        raise ValueError(f"{role} subline exceeds character budget")
    for key, budget_key in (
        ("proof_nuggets", "proof_nugget"),
        ("annotations", "annotation"),
        ("state_labels", "state_label"),
    ):
        for value in bundle[key]:
            if count_words(value) > COPY_BUDGETS[budget_key]["max_words"]:
                raise ValueError(f"{role} {key} exceeds word budget: {value}")
            if len(value) > COPY_BUDGETS[budget_key]["max_chars"]:
                raise ValueError(f"{role} {key} exceeds character budget: {value}")
    lowered = " ".join(
        [headline, subline, *bundle["proof_nuggets"], *bundle["annotations"], *bundle["state_labels"]]
    ).lower()
    for term in FORBIDDEN_PUBLIC_TERMS:
        if term in lowered:
            raise ValueError(f"{role} public copy contains forbidden term: {term}")
```

- [ ] **Step 5: Build the three artifact functions**

Add three functions with these interfaces:

```python
def build_editorial_copy_memory(
    run249_readability: dict[str, Any],
    run249_density: dict[str, Any],
    run250_result: dict[str, Any],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    readability_records = run249_readability["readability_records"]
    density_records = run249_density["content_evidence_density_records"]
    for role in ROLES:
        readability = role_record(readability_records, role, "Run 2.49 readability")
        density = role_record(density_records, role, "Run 2.49 density")
        copy = ROLE_COPY[role]
        bundle = {
            "headline": copy["headline"],
            "subline": copy["subline"],
            "proof_nuggets": copy["proof_nuggets"],
            "annotations": copy["annotations"],
            "state_labels": copy["state_labels"],
        }
        assert_copy_fits_budget(role, bundle)
        records.append(
            {
                "copy_memory_id": f"editorial_copy_2_51_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "source_run_ids": ["2.49", "2.50"],
                "required_run2_49_readability_memory_id": readability["readability_memory_id"],
                "required_run2_49_content_evidence_density_memory_id": density[
                    "content_evidence_density_memory_id"
                ],
                "raw_evidence_inputs": {
                    "readability_goal": readability["readability_goal"],
                    "business_proof_points": density.get("business_proof_points", []),
                    "run2_50_quality_delta": (run250_result.get("quality_delta") or {}).get("target_layer"),
                },
                "public_surface_copy_bundle": bundle,
                "trace_only_copy_bundle": {
                    "source_status": run250_result.get("status"),
                    "source_data_status": (run250_result.get("quality_delta") or {}).get("source_data_status"),
                },
                "copy_fit_budget": COPY_BUDGETS,
                "forbidden_surface_terms": FORBIDDEN_PUBLIC_TERMS,
                "business_claim_preservation_check": copy["business_claim"],
                "visual_validation_deferred_to_generated_rerun": True,
                "bad_control_probe": "Bad control fails if public copy is raw Run 2.49/2.50 workflow language.",
                "next_rerun_obligation": NEXT_RERUN_CONTRACT,
            }
        )
    return {
        "schema_version": "ppt_run2_editorial_copy_memory.v1",
        "status": "run2_51_editorial_copy_memory_ready_public_blocked",
        "run_id": RUN_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_data_workflow_run": "2.49",
        "source_generated_run": "2.50",
        "target_layer": TARGET_LAYER,
        "editorial_copy_records": records,
    }
```

Add these helper and builder functions:

```python
TRACE_FIELDS = [
    "run2_51_editorial_copy_memory_id",
    "run2_51_shape_text_socket_memory_id",
    "run2_51_renderer_archetype_gate_id",
    "run2_51_primary_archetype",
    "run2_51_public_surface_copy_status",
    "run2_51_text_socket_placement_status",
    "run2_51_shape_vocabulary_status",
    "run2_51_character_fit_status",
    "run2_51_forbidden_surface_terms_count",
    "run2_51_equal_card_cluster_count",
    "run2_51_semantic_primitive_count",
]

GEOMETRY_CONSTRAINTS = {
    "stage": "poster-scale field; not an equal card; owns the headline plane",
    "route_path": "connected path with at least three node sockets and visible connectors",
    "lens": "oval, circle, or cropped-window comparison surface; not a plain rectangle",
    "exploded_layers": "at least three offset layers with scale separation and connector lines",
    "bracket_callout": "brace, bracket, or leader line that anchors annotation copy",
    "ribbon": "narrow strip or diagonal strip for state labels; smaller than the main surface",
    "stamp_badge": "compact proof marker with status or proof socket",
    "spotlight": "clipped focus field that creates contrast around the main object",
    "depth_stack": "unequal overlapping layers with visible offset",
    "decision_wall": "handoff surface with gate/action sockets and grouped decisions",
}


def copy_role_for_socket(socket_name: str) -> str:
    if "headline" in socket_name or "title" in socket_name or "claim" in socket_name:
        return "headline"
    if "caption" in socket_name or "implication" in socket_name or "whisper" in socket_name:
        return "subline"
    if "label" in socket_name or "tag" in socket_name or "marker" in socket_name:
        return "state_label"
    if "proof" in socket_name:
        return "proof_nugget"
    return "annotation"


def socket_contracts_for(role: str, archetype: dict[str, Any]) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for index, socket_name in enumerate(archetype["required_sockets"], start=1):
        copy_role = copy_role_for_socket(socket_name)
        budget = COPY_BUDGETS[copy_role]
        primitive = archetype["shape_primitives"][(index - 1) % len(archetype["shape_primitives"])]
        contracts.append(
            {
                "socket_id": f"socket_2_51_{role}_{socket_name}",
                "copy_role": copy_role,
                "owning_shape_id": f"shape_2_51_{role}_{primitive}_{index}",
                "placement_rule": f"bind {socket_name} to {primitive} with visible padding and no float-away label",
                "max_lines": budget["max_lines"],
                "font_size_range": [11, 34] if copy_role == "headline" else [8, 18],
                "character_budget": budget["max_chars"],
                "minimum_padding": 8,
                "alignment": "center" if copy_role == "headline" else "left",
                "overflow_policy": "reject_and_recompile",
            }
        )
    return contracts


def build_shape_text_socket_memory(
    copy_memory: dict[str, Any],
    run249_gates: dict[str, Any],
) -> dict[str, Any]:
    copy_records = copy_memory["editorial_copy_records"]
    prior_gates = run249_gates["editorial_renderer_workflow_gates"]
    records: list[dict[str, Any]] = []
    for role in ROLES:
        copy_record = role_record(copy_records, role, "Run 2.51 copy")
        prior_gate = role_record(prior_gates, role, "Run 2.49 renderer gate")
        archetype = ROLE_ARCHETYPES[role]
        constraints = [GEOMETRY_CONSTRAINTS[primitive] for primitive in archetype["shape_primitives"]]
        records.append(
            {
                "socket_memory_id": f"shape_text_socket_2_51_{role}",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "source_run_ids": ["2.49", "2.50"],
                "required_editorial_copy_memory_id": copy_record["copy_memory_id"],
                "required_run2_49_editorial_renderer_gate_id": prior_gate["gate_id"],
                "primary_archetype": archetype["primary_archetype"],
                "shape_primitives": archetype["shape_primitives"],
                "socket_contracts": socket_contracts_for(role, archetype),
                "geometry_constraints": constraints,
                "copy_role_bindings": {
                    "headline": "dominant archetype title socket",
                    "subline": "secondary semantic surface socket",
                    "proof_nugget": "proof object, path node, badge, callout, or layer tag",
                    "annotation": "bracket, leader, or caption socket",
                    "state_label": "ribbon, badge, or node label socket",
                },
                "fit_checks": [
                    "character budget passes before drawing",
                    "max-line budget passes before drawing",
                    "public copy is bound to a socket, not a free-floating label",
                ],
                "forbidden_layout_patterns": [
                    "equal card cluster as primary surface",
                    "plain rectangle renamed as lens",
                    "proof text detached from proof object",
                    "workflow terms rendered as public labels",
                ],
                "bad_control_probe": "Bad control fails if it draws text without Run 2.51 socket ids.",
                "next_rerun_obligation": NEXT_RERUN_CONTRACT,
            }
        )
    return {
        "schema_version": "ppt_run2_shape_text_socket_memory.v1",
        "status": "run2_51_shape_text_socket_memory_ready_public_blocked",
        "run_id": RUN_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_data_workflow_run": "2.49",
        "source_generated_run": "2.50",
        "target_layer": TARGET_LAYER,
        "shape_text_socket_records": records,
    }


def build_renderer_archetype_workflow_gates(
    copy_memory: dict[str, Any],
    socket_memory: dict[str, Any],
) -> dict[str, Any]:
    copy_records = copy_memory["editorial_copy_records"]
    socket_records = socket_memory["shape_text_socket_records"]
    gates: list[dict[str, Any]] = []
    for role in ROLES:
        copy_record = role_record(copy_records, role, "Run 2.51 copy")
        socket_record = role_record(socket_records, role, "Run 2.51 socket")
        gates.append(
            {
                "gate_id": f"gate_2_51_{role}_renderer_archetype",
                "role": role,
                "selected_usecase_id": SELECTED_USECASE_ID,
                "required_editorial_copy_memory_id": copy_record["copy_memory_id"],
                "required_shape_text_socket_memory_id": socket_record["socket_memory_id"],
                "primary_archetype": socket_record["primary_archetype"],
                "forbid_square_block_grid_as_primary_surface": True,
                "max_equal_card_clusters": 1,
                "min_semantic_primitives": 3,
                "min_socket_bound_public_text_elements": 4,
                "max_socket_bound_public_text_elements": 7,
                "require_character_fit_status": True,
                "require_forbidden_surface_terms_count_zero": True,
                "visual_validation_deferred_to_generated_rerun": True,
                "consumer_contract": {
                    "next_generated_run": "2.52",
                    "must_bind_before_public_text": True,
                    "required_trace_fields": TRACE_FIELDS,
                },
                "next_rerun_contract": NEXT_RERUN_CONTRACT,
                "required_trace_fields": TRACE_FIELDS,
                "pass_fail_checks": [
                    "Run 2.52 binds one Run 2.51 editorial copy memory id before drawing public text.",
                    "Run 2.52 binds one Run 2.51 shape text socket memory id before drawing semantic surfaces.",
                    "Slide has one primary archetype and at least three semantic primitives.",
                    "Every public proof nugget is socket-bound to a proof object, path node, badge, callout, or layer tag.",
                    "Forbidden workflow terms have count zero on the public surface.",
                    "Bad control fails without Run 2.51 copy/socket/archetype ids.",
                ],
                "bad_control_probe": "A negative control may reuse Run 2.49/2.50 context, but fails if it lacks Run 2.51 copy, socket, and archetype gate ids.",
                "public_release_gate": "blocked",
            }
        )
    return {
        "schema_version": "ppt_run2_renderer_archetype_workflow_gates.v1",
        "status": "run2_51_renderer_archetype_workflow_gates_ready_public_blocked",
        "run_id": RUN_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_data_workflow_run": "2.49",
        "source_generated_run": "2.50",
        "target_layer": TARGET_LAYER,
        "next_rerun_contract": NEXT_RERUN_CONTRACT,
        "renderer_archetype_workflow_gates": gates,
    }
```

- [ ] **Step 6: Add result writer and CLI main**

Add:

```python
def build_result(
    out_dir: Path,
    copy_memory: dict[str, Any],
    socket_memory: dict[str, Any],
    gates: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_editorial_shape_text_repair_result.v1",
        "run_id": RUN_ID,
        "status": "run2_51_editorial_shape_text_repair_ready_public_blocked",
        "source_data_workflow_run": "2.49",
        "source_generated_run": "2.50",
        "selected_usecase_id": SELECTED_USECASE_ID,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "public_ready": False,
        "creates_new_ppt_deck": False,
        "visual_validation_deferred_to_generated_rerun": True,
        "target_layer": TARGET_LAYER,
        "input_chain": {
            "run2_49_result": rel(PACK / "results" / "run2_49_readability_content_density_renderer_repair_result.json"),
            "run2_49_readability_memory": rel(PACK / "run2_49_readability_memory.json"),
            "run2_49_content_evidence_density_memory": rel(PACK / "run2_49_content_evidence_density_memory.json"),
            "run2_49_editorial_renderer_workflow_gates": rel(PACK / "run2_49_editorial_renderer_workflow_gates.json"),
            "run2_50_result": rel(PACK / "results" / "run2_50_readability_density_renderer_rerun_result.json"),
        },
        "output_chain": {
            "editorial_copy_memory": rel(out_dir / "run2_51_editorial_copy_memory.json"),
            "shape_text_socket_memory": rel(out_dir / "run2_51_shape_text_socket_memory.json"),
            "renderer_archetype_workflow_gates": rel(out_dir / "run2_51_renderer_archetype_workflow_gates.json"),
        },
        "artifact_counts": {
            "editorial_copy_records": len(copy_memory["editorial_copy_records"]),
            "shape_text_socket_records": len(socket_memory["shape_text_socket_records"]),
            "renderer_archetype_workflow_gates": len(gates["renderer_archetype_workflow_gates"]),
        },
        "delivery_artifacts": {"pptx_paths": [], "rendered_slide_paths": [], "contact_sheet_paths": []},
        "repair_contract": {
            "editorial copy": "raw evidence becomes short public-facing display copy",
            "shape text sockets": "text is bound to semantic shape sockets before drawing",
            "renderer archetypes": "each slide role has one dominant visual archetype and explicit geometry gates",
            "data/workflow-only": True,
        },
        "public_release_gate": "blocked",
        "release_boundary": (
            "public_blocked_until_run2_52_consumes_run2_51_artifacts_then_visual_review_render_review_and_human_approval_pass"
        ),
        "next_required_action": NEXT_ACTION,
    }
```

Add `write_markdown`, `parse_args`, and `main` following the Run 2.49 builder pattern. `main` must read the five input files, validate them, build/write all artifacts, call `assert_no_run251_deck_artifacts()` before and after writing, print the status JSON, and return `0`.

- [ ] **Step 7: Run the builder test again**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_51_builder_creates_editorial_copy_shape_socket_repair_pack -q
```

Expected: PASS.

- [ ] **Step 8: Commit builder and first test**

Run:

```bash
git add scripts/build_ppt_run2_51_editorial_copy_shape_sockets.py tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: add run2.51 editorial socket builder"
```

---

### Task 3: Generate And Validate The Run 2.51 Artifacts In The Case Pack

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/run2_51_editorial_copy_memory.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_51_shape_text_socket_memory.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_51_renderer_archetype_workflow_gates.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_51_editorial_shape_text_repair_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_51_editorial_shape_text_repair_result.md`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Run the builder against the real case pack**

Run:

```bash
python3 scripts/build_ppt_run2_51_editorial_copy_shape_sockets.py
```

Expected stdout contains:

```json
{
  "status": "run2_51_editorial_shape_text_repair_ready_public_blocked"
}
```

- [ ] **Step 2: Add artifact validation test**

Append:

```python
def test_run2_51_records_editorial_copy_shape_socket_repair_pack() -> None:
    result = load_json(PACK / "results" / "run2_51_editorial_shape_text_repair_result.json")
    copy_memory = load_json(PACK / "run2_51_editorial_copy_memory.json")
    socket_memory = load_json(PACK / "run2_51_shape_text_socket_memory.json")
    gates = load_json(PACK / "run2_51_renderer_archetype_workflow_gates.json")

    assert result["status"] == "run2_51_editorial_shape_text_repair_ready_public_blocked"
    assert result["visual_validation_deferred_to_generated_rerun"] is True
    assert result["output_chain"]["editorial_copy_memory"].endswith("run2_51_editorial_copy_memory.json")
    assert result["output_chain"]["shape_text_socket_memory"].endswith("run2_51_shape_text_socket_memory.json")
    assert result["output_chain"]["renderer_archetype_workflow_gates"].endswith(
        "run2_51_renderer_archetype_workflow_gates.json"
    )
    assert copy_memory["schema_version"] == "ppt_run2_editorial_copy_memory.v1"
    assert socket_memory["schema_version"] == "ppt_run2_shape_text_socket_memory.v1"
    assert gates["schema_version"] == "ppt_run2_renderer_archetype_workflow_gates.v1"
    assert copy_memory["source_generated_run"] == "2.50"
    assert socket_memory["source_generated_run"] == "2.50"
    assert gates["source_generated_run"] == "2.50"
    assert len(copy_memory["editorial_copy_records"]) == 6
    assert len(socket_memory["shape_text_socket_records"]) == 6
    assert len(gates["renderer_archetype_workflow_gates"]) == 6

    for record in copy_memory["editorial_copy_records"]:
        bundle = record["public_surface_copy_bundle"]
        assert EXPECTED_RUN2_51_COPY_BUNDLE_KEYS <= set(bundle)
        assert word_count(bundle["headline"]) <= 7
        assert len(bundle["headline"]) <= 48
        assert word_count(bundle["subline"]) <= 18
        assert len(bundle["subline"]) <= 120
        for text in public_text_values(bundle):
            lowered = text.lower()
            assert not any(term in lowered for term in EXPECTED_RUN2_51_FORBIDDEN_PUBLIC_TERMS)
        assert record["visual_validation_deferred_to_generated_rerun"] is True
        assert record["next_rerun_obligation"] == "must_be_consumed_before_run2_52_four_arm_rerun"

    for record in socket_memory["shape_text_socket_records"]:
        assert len(record["socket_contracts"]) >= 4
        assert len(record["shape_primitives"]) >= 3
        assert len(record["geometry_constraints"]) >= 3
        assert record["primary_archetype"]
        assert record["forbidden_layout_patterns"]
        for socket in record["socket_contracts"]:
            assert socket["owning_shape_id"]
            assert socket["placement_rule"]
            assert socket["character_budget"] > 0
            assert socket["max_lines"] >= 1
            assert socket["overflow_policy"] in {"shrink_to_fit", "wrap_within_socket", "reject_and_recompile"}

    for gate in gates["renderer_archetype_workflow_gates"]:
        assert EXPECTED_RUN2_51_TRACE_FIELDS <= set(gate["required_trace_fields"])
        assert gate["consumer_contract"]["next_generated_run"] == "2.52"
        assert gate["consumer_contract"]["must_bind_before_public_text"] is True
        assert EXPECTED_RUN2_51_TRACE_FIELDS <= set(gate["consumer_contract"]["required_trace_fields"])
        assert gate["next_rerun_contract"] == "must_be_consumed_before_run2_52_four_arm_rerun"
        assert gate["forbid_square_block_grid_as_primary_surface"] is True
        assert gate["max_equal_card_clusters"] <= 1
        assert gate["min_semantic_primitives"] >= 3
        assert gate["visual_validation_deferred_to_generated_rerun"] is True
```

- [ ] **Step 3: Run focused artifact validation**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_51_records_editorial_copy_shape_socket_repair_pack -q
```

Expected: PASS.

- [ ] **Step 4: Commit generated artifacts and validation test**

Run:

```bash
git add docs/product/ppt-run2-data-skill-quality/run2_51_editorial_copy_memory.json \
  docs/product/ppt-run2-data-skill-quality/run2_51_shape_text_socket_memory.json \
  docs/product/ppt-run2-data-skill-quality/run2_51_renderer_archetype_workflow_gates.json \
  docs/product/ppt-run2-data-skill-quality/results/run2_51_editorial_shape_text_repair_result.json \
  docs/product/ppt-run2-data-skill-quality/results/run2_51_editorial_shape_text_repair_result.md \
  tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: record run2.51 editorial socket artifacts"
```

---

### Task 4: Extend Skill Workflow And Result Index

**Files:**
- Modify: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add three workflow stages**

Append these stages after existing Run 2.49 workflow stages:

```json
{
  "id": "compile_run2_51_editorial_copy_memory",
  "order": 51,
  "layer": "evidence_aesthetic_asset_memory",
  "inputs": [
    "run2_49_readability_memory.json",
    "run2_49_content_evidence_density_memory.json",
    "results/run2_50_readability_density_renderer_rerun_result.json"
  ],
  "outputs": [
    "run2_51_editorial_copy_memory.json"
  ],
  "gates": [
    "public copy respects word and character budgets",
    "raw workflow terms are absent from public copy",
    "raw evidence remains available in trace-only fields",
    "visual validation is deferred to generated rerun"
  ]
}
```

Add these two additional stages immediately after `compile_run2_51_editorial_copy_memory`:

```json
{
  "id": "compile_run2_51_shape_text_socket_memory",
  "order": 52,
  "layer": "evidence_aesthetic_asset_memory",
  "inputs": [
    "run2_51_editorial_copy_memory.json",
    "run2_49_editorial_renderer_workflow_gates.json"
  ],
  "outputs": [
    "run2_51_shape_text_socket_memory.json"
  ],
  "gates": [
    "each role has one primary archetype",
    "each role has at least four socket contracts",
    "each socket owns a shape id and character budget",
    "semantic primitives include explicit geometry constraints"
  ]
}
```

```json
{
  "id": "apply_run2_51_renderer_archetype_workflow_gates",
  "order": 53,
  "layer": "skill_workflow",
  "inputs": [
    "run2_51_editorial_copy_memory.json",
    "run2_51_shape_text_socket_memory.json"
  ],
  "outputs": [
    "run2_51_renderer_archetype_workflow_gates.json"
  ],
  "gates": [
    "next generated full arm must bind Run 2.51 copy ids",
    "next generated full arm must bind Run 2.51 socket ids",
    "bad control must fail without Run 2.51 ids",
    "visual validation remains deferred until generated rerun"
  ]
}
```

Use order values that are higher than the existing Run 2.49 stages and preserve ascending order across the full file.

- [ ] **Step 2: Add workflow test**

Append:

```python
def test_run2_51_extends_skill_workflow_without_claiming_generated_deck() -> None:
    workflow = load_json(PACK / "skill_workflow.json")
    result = load_json(PACK / "results" / "run2_51_editorial_shape_text_repair_result.json")
    workflow_stage_ids = [stage["id"] for stage in workflow["stages"]]

    assert result["creates_new_ppt_deck"] is False
    assert result["visual_validation_deferred_to_generated_rerun"] is True
    assert "compile_run2_51_editorial_copy_memory" in workflow_stage_ids
    assert "compile_run2_51_shape_text_socket_memory" in workflow_stage_ids
    assert "apply_run2_51_renderer_archetype_workflow_gates" in workflow_stage_ids
    assert workflow_stage_ids.index("compile_run2_51_editorial_copy_memory") < workflow_stage_ids.index(
        "compile_run2_51_shape_text_socket_memory"
    )
    assert workflow_stage_ids.index("compile_run2_51_shape_text_socket_memory") < workflow_stage_ids.index(
        "apply_run2_51_renderer_archetype_workflow_gates"
    )
```

- [ ] **Step 3: Update results README**

Add one sentence to the Run 2 list:

```markdown
`run2_51_editorial_shape_text_repair_result.md` records the Run 2.51 editorial-copy and shape-text-socket data/workflow repair layer. It creates no PPT deck; visual validation is deferred until a generated rerun consumes the 2.51 artifacts.
```

- [ ] **Step 4: Run workflow test**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_51_extends_skill_workflow_without_claiming_generated_deck -q
```

Expected: PASS.

- [ ] **Step 5: Commit workflow and index**

Run:

```bash
git add docs/product/ppt-run2-data-skill-quality/skill_workflow.json \
  docs/product/ppt-run2-data-skill-quality/results/README.md \
  tests/test_ppt_run2_data_skill_quality.py
git commit -m "docs: add run2.51 workflow repair layer"
```

---

### Task 5: Update HTML Viewer Data / Skill Surface

**Files:**
- Modify: `scripts/build_ppt_run_html_viewer.py`
- Generate local ignored output: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Read Run 2.51 artifacts in viewer builder**

In `build_reference_data`, after Run 2.50 reads, add:

```python
    run251_copy_memory = read_json(pack / "run2_51_editorial_copy_memory.json")
    run251_socket_memory = read_json(pack / "run2_51_shape_text_socket_memory.json")
    run251_gates = read_json(pack / "run2_51_renderer_archetype_workflow_gates.json")
    run251_result = read_json(pack / "results" / "run2_51_editorial_shape_text_repair_result.json")
```

Add return keys:

```python
        "run251CopyMemoryStatus": run251_copy_memory.get("status", ""),
        "run251CopyRecords": run251_copy_memory.get("editorial_copy_records", []),
        "run251SocketMemoryStatus": run251_socket_memory.get("status", ""),
        "run251SocketRecords": run251_socket_memory.get("shape_text_socket_records", []),
        "run251GateStatus": run251_gates.get("status", ""),
        "run251Gates": run251_gates.get("renderer_archetype_workflow_gates", []),
        "run251ResultStatus": run251_result.get("status", ""),
        "run251Result": run251_result,
        "run251ResultPath": "run2_51_editorial_shape_text_repair_result.json",
```

- [ ] **Step 2: Add JavaScript cards for 2.51 records**

Near the existing `run249ReadabilityCards` definitions, add:

```javascript
      const run251Result = refs.run251Result || {};
      const run251CopyCards = (refs.run251CopyRecords || []).map((record) => `
        <article class="dataCard">
          <h4>${escapeHtml(record.role)} editorial copy</h4>
          ${detailBlock("Headline", record.public_surface_copy_bundle?.headline)}
          ${detailBlock("Subline", record.public_surface_copy_bundle?.subline)}
          ${detailBlock("Proof nuggets", record.public_surface_copy_bundle?.proof_nuggets)}
          ${detailBlock("Business claim", record.business_claim_preservation_check)}
          ${detailBlock("Next rerun", record.next_rerun_obligation)}
        </article>`).join("");
      const run251SocketCards = (refs.run251SocketRecords || []).map((record) => `
        <article class="dataCard">
          <h4>${escapeHtml(record.role)} sockets</h4>
          ${detailBlock("Archetype", record.primary_archetype)}
          ${detailBlock("Shape primitives", record.shape_primitives)}
          ${detailBlock("Socket count", (record.socket_contracts || []).length)}
          ${detailBlock("Geometry constraints", record.geometry_constraints)}
        </article>`).join("");
      const run251GateCards = (refs.run251Gates || []).map((gate) => `
        <article class="dataCard">
          <h4>${escapeHtml(gate.role)} archetype gate</h4>
          ${detailBlock("Gate", gate.gate_id)}
          ${detailBlock("Primary archetype", gate.primary_archetype)}
          ${detailBlock("Trace fields", gate.required_trace_fields)}
          ${detailBlock("Bad control", gate.bad_control_probe)}
        </article>`).join("");
```

- [ ] **Step 3: Add a latest data/workflow repair section before Run 2.49**

In the Data / Skill `content.innerHTML`, insert a Run 2.51 band before the Run 2.49 band:

```javascript
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Latest data/workflow repair</h3><p>Run 2.51 is the current data/workflow repair layer: it prepares editorial public copy, semantic shape text sockets, and renderer archetype gates. It creates no PPT deck; visual validation waits for the next generated rerun.</p></div><span class="pill" title="${escapeHtml(refs.run251ResultStatus || "missing")}">${escapeHtml(refs.run251ResultStatus || "missing")}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run 2.51 repair pack</h4>
              ${detailBlock("Result", refs.run251ResultPath || "run2_51_editorial_shape_text_repair_result.json")}
              ${detailBlock("Boundary", "Data/workflow-only, no new PPT deck")}
              ${detailBlock("Target layer", run251Result.target_layer || "editorial_copy_and_shape_text_socket_repair")}
              ${detailBlock("Next required action", run251Result.next_required_action || "consume_run2_51_before_run2_52_four_arm_rerun")}
            </article>
            <article class="dataCard">
              <h4>What it fixes</h4>
              ${detailBlock("Editorial copy", run251Result.repair_contract?.["editorial copy"])}
              ${detailBlock("Shape text sockets", run251Result.repair_contract?.["shape text sockets"])}
              ${detailBlock("Renderer archetypes", run251Result.repair_contract?.["renderer archetypes"])}
              ${detailBlock("Visual validation", "Deferred to generated rerun")}
            </article>
          </div>
          <div class="dataBandSubhead"><h4>Editorial copy memory</h4><p>${escapeHtml(refs.run251CopyMemoryStatus)}. Raw evidence is rewritten into short public-facing display copy with word and character budgets.</p></div>
          <div class="dataGrid">${run251CopyCards}</div>
          <div class="dataBandSubhead"><h4>Shape text socket memory</h4><p>${escapeHtml(refs.run251SocketMemoryStatus)}. Each role has a dominant archetype, semantic primitives, and text sockets before generation.</p></div>
          <div class="dataGrid">${run251SocketCards}</div>
          <div class="dataBandSubhead"><h4>Renderer archetype workflow gates</h4><p>${escapeHtml(refs.run251GateStatus)}. The next generated full arm must bind these gates, while the bad control must fail without them.</p></div>
          <div class="dataGrid">${run251GateCards}</div>
        </section>
```

Revise the older Run 2.49 "Latest data/workflow repair" heading to avoid duplicate latest claims:

```html
<h3>Run 2.49 readability/content density repair</h3>
```

- [ ] **Step 4: Rebuild viewer**

Run:

```bash
python3 scripts/build_ppt_run_html_viewer.py
```

Expected stdout includes:

```json
{
  "latest": "2.50"
}
```

- [ ] **Step 5: Add viewer test**

Append:

```python
def test_ppt_run_html_viewer_embeds_run2_51_data_workflow_repair_pack() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    viewer = (
        ROOT
        / "outputs"
        / "019e7d9c-532a-70b3-8892-fa3ae42baef2"
        / "presentations"
        / "ppt-run-viewer.html"
    ).read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_51_editorial_copy_memory.json",
            "run2_51_shape_text_socket_memory.json",
            "run2_51_renderer_archetype_workflow_gates.json",
            "run251ResultStatus",
            "Run 2.51 is the current data/workflow repair layer",
            "visual validation waits for the next generated rerun",
        ],
    )
    assert_contains(
        viewer,
        [
            '"latestRunId": "2.50"',
            "Run 2.51 is the current data/workflow repair layer",
            "run2_51_editorial_shape_text_repair_result.json",
            "run2_51_editorial_copy_memory.json",
            "run2_51_shape_text_socket_memory.json",
            "run2_51_renderer_archetype_workflow_gates.json",
            "Data/workflow-only, no new PPT deck",
            "Visual validation",
            "Deferred to generated rerun",
        ],
    )
    assert "ppt-run2-51" not in viewer
```

- [ ] **Step 6: Run viewer test**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_ppt_run_html_viewer_embeds_run2_51_data_workflow_repair_pack -q
```

Expected: PASS.

- [ ] **Step 7: Commit viewer update**

Run:

```bash
git add scripts/build_ppt_run_html_viewer.py tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: surface run2.51 repair pack in viewer"
```

Do not stage the generated `ppt-run-viewer.html` under `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/` unless the repository already tracks that file. It is normally a local ignored generated artifact.

---

### Task 6: Final Verification And Handoff

**Files:**
- Check: all files changed by Tasks 1-5

- [ ] **Step 1: Run focused pytest suite**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q
```

Expected: all tests pass.

- [ ] **Step 2: Run linter and syntax checks**

Run:

```bash
ruff check scripts/build_ppt_run2_51_editorial_copy_shape_sockets.py scripts/build_ppt_run_html_viewer.py tests/test_ppt_run2_data_skill_quality.py
python3 -m py_compile scripts/build_ppt_run2_51_editorial_copy_shape_sockets.py scripts/build_ppt_run_html_viewer.py
git diff --check
```

Expected: all commands pass with no output except normal summary text.

- [ ] **Step 3: Inspect generated viewer in browser**

Open:

```text
http://127.0.0.1:8787/outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html?v=251
```

Expected:

- Latest generated run still shows `Run 2.50`.
- Data / Skill tab shows `Run 2.51 is the current data/workflow repair layer`.
- Viewer shows editorial copy memory, shape text socket memory, and renderer archetype workflow gates.
- No Run 2.51 PPTX/download is shown.

- [ ] **Step 4: Review git status and commit any verification-only doc updates**

Run:

```bash
git status --short --branch
```

Expected: clean except local ignored outputs.

If a tracked verification doc was updated, commit it:

```bash
git add <tracked-verification-file>
git commit -m "docs: record run2.51 verification"
```

- [ ] **Step 5: Push branch**

Run:

```bash
git push
```

Expected: push succeeds.

---

## Self-Review

Spec coverage:

- Editorial copy memory: Task 2 and Task 3.
- Shape text socket memory: Task 2 and Task 3.
- Renderer archetype workflow gates: Task 2 and Task 3.
- Viewer Data / Skill exposure: Task 5.
- Data/workflow-only boundary and no generated deck: Tasks 1, 2, 3, and 5.
- Deferred visual validation: Tasks 2, 3, 4, and 5.
- Bad control trace contract for future rerun: Tasks 2 and 3.

Placeholder scan:

- No empty implementation slots are present.
- Every code-changing task has concrete file paths, snippets, commands, and expected results.

Type consistency:

- Artifact keys match the spec: `editorial_copy_records`, `shape_text_socket_records`, `renderer_archetype_workflow_gates`.
- Status strings match the Run 2.51 design spec.
- Viewer keys use the established camelCase prefix `refs.run251`.
