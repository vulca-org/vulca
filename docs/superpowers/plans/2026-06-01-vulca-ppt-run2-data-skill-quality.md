# Vulca PPT Run 2.0 Data Skill Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Run 2.0 as a data-first and skill-first PPT case package that thickens the five fixed product layers before rerunning generation.

**Architecture:** Add a `run2` validation profile and a self-contained `docs/product/ppt-run2-data-skill-quality/` package. Run 2.0 reuses Run 1.5 infrastructure where useful, but splits the knowledge layer into evidence, aesthetic, and asset memory with explicit source-card traceability and aesthetic quality gates.

**Tech Stack:** Python stdlib validator, pytest, ruff, Markdown/JSON case-pack files, Academic Writing Toolkit for written-logic/source discipline checks, Gemini-agent for plan and artifact review, existing PPT generation and delivery QA infrastructure in later execution tasks.

---

## Decisions Locked By This Plan

- Start by upgrading the existing Run 1.5 source set and adding curated presentation-design tutorial/video references.
- Require at least 8 source cards before generation is allowed.
- Require at least 2 video cards before generation is allowed.
- Author video cards manually in Run 2.0 v1; do not build automated video ingestion yet.
- First generated Run 2.0 public-demo main deck should be 6 slides.
- Do not generate PPTs until validator, package contract tests, source cards, memories, skill workflow, and generation briefs pass.

## File Map

- Modify `scripts/validate_ppt_case_pack.py`: add `run2` profile, required files, source-card/video-card checks, memory schema checks, and cross-reference validation.
- Modify `tests/test_ppt_case_pack_validator.py`: add unit tests for the `run2` validation profile.
- Create `tests/test_ppt_run2_data_skill_quality.py`: repository contract tests for the committed Run 2.0 package.
- Create `docs/product/ppt-run2-data-skill-quality/README.md`: entry point, five-layer status, artifact map, and release status.
- Create `docs/product/ppt-run2-data-skill-quality/commercial_case.md`: concrete commercial case and failure definition.
- Create `docs/product/ppt-run2-data-skill-quality/sources.json`: source registry with public URLs and reference-analysis-only policy.
- Create `docs/product/ppt-run2-data-skill-quality/source_cards/README.md`: source-card contract.
- Create `docs/product/ppt-run2-data-skill-quality/source_cards/*.json`: at least 8 manually curated source cards.
- Create `docs/product/ppt-run2-data-skill-quality/video_cards/README.md`: video-card contract.
- Create `docs/product/ppt-run2-data-skill-quality/video_cards/*.json`: at least 2 manually curated video cards.
- Create `docs/product/ppt-run2-data-skill-quality/evidence_memory.json`: claim/provenance memory.
- Create `docs/product/ppt-run2-data-skill-quality/aesthetic_memory.json`: composition, rhythm, typography, density, and negative-rule memory.
- Create `docs/product/ppt-run2-data-skill-quality/asset_memory.json`: generated image, SVG, video-derived reference, provenance, and editability rules.
- Create `docs/product/ppt-run2-data-skill-quality/narrative_spine.json`: 6-slide public-demo narrative.
- Create `docs/product/ppt-run2-data-skill-quality/slide_archetypes.json`: archetype definitions linked to aesthetic memory.
- Create `docs/product/ppt-run2-data-skill-quality/aesthetic_rubric.md`: measurable aesthetic and evidence QA rubric.
- Create `docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md`: staged deck-director skill workflow.
- Create `docs/product/ppt-run2-data-skill-quality/generation_briefs/README.md`: arm contract.
- Create `docs/product/ppt-run2-data-skill-quality/generation_briefs/prompt_only.md`: baseline arm.
- Create `docs/product/ppt-run2-data-skill-quality/generation_briefs/run1_5_skill.md`: old-skill comparison arm.
- Create `docs/product/ppt-run2-data-skill-quality/generation_briefs/run2_skill.md`: new Run 2.0 arm.
- Create `docs/product/ppt-run2-data-skill-quality/generation_briefs/bad_aesthetic_memory.md`: negative-control arm.
- Create `docs/product/ppt-run2-data-skill-quality/results/README.md`: result contract and public-blocked status.
- Create `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`: not-run comparison scaffold.
- Create `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`: not-run delivery gate scaffold.
- Modify `docs/product/roadmap.md`: add Run 2.0 status and preserve public-release blockers.

Generated local-only artifacts for later tasks:

- `outputs/$THREAD_ID/presentations/ppt-run2-prompt-only/`
- `outputs/$THREAD_ID/presentations/ppt-run2-run1-5-skill/`
- `outputs/$THREAD_ID/presentations/ppt-run2-full-vulca/`
- `outputs/$THREAD_ID/presentations/ppt-run2-bad-aesthetic-memory/`

Do not commit generated `.pptx`, preview images, layout JSON, local slide modules, contact sheets, copied screenshots, full video transcripts, or downloaded copyrighted media unless the user explicitly approves release packaging.

---

### Task 1: Add Run 2.0 Validator Profile

**Files:**
- Modify: `tests/test_ppt_case_pack_validator.py`
- Modify: `scripts/validate_ppt_case_pack.py`

- [ ] **Step 1: Add failing tests for the `run2` profile**

Append this code to `tests/test_ppt_case_pack_validator.py`:

```python
def write_run2_required_files(pack: Path) -> None:
    for directory in ["source_cards", "video_cards", "generation_briefs"]:
        (pack / directory).mkdir()
        (pack / directory / "README.md").write_text(f"# {directory}\n\nContract for {directory}.\n", encoding="utf-8")
    (pack / "commercial_case.md").write_text(
        "# Commercial Case\n\nAudience: AI product teams.\n\nFailed deck: generic dashboard report.\n",
        encoding="utf-8",
    )
    (pack / "aesthetic_rubric.md").write_text(
        "# Aesthetic Rubric\n\n- rhythm variance\n- density control\n- public-demo quality\n",
        encoding="utf-8",
    )
    (pack / "vulca_ppt_skill.md").write_text(
        "# Vulca PPT Skill\n\nStages: case, evidence, aesthetic, assets, code, QA, repair, release.\n",
        encoding="utf-8",
    )
    (pack / "generation_briefs" / "prompt_only.md").write_text("# Prompt Only\n\nCommercial brief only.\n", encoding="utf-8")
    (pack / "generation_briefs" / "run1_5_skill.md").write_text("# Run 1.5 Skill\n\nUse old evidence-heavy skill.\n", encoding="utf-8")
    (pack / "generation_briefs" / "run2_skill.md").write_text("# Run 2.0 Skill\n\nUse evidence, aesthetic, and asset memory.\n", encoding="utf-8")
    (pack / "generation_briefs" / "bad_aesthetic_memory.md").write_text(
        "# Bad Aesthetic Memory\n\nUse valid evidence with weak aesthetic rules.\n",
        encoding="utf-8",
    )
    (pack / "results" / "delivery_gate.md").write_text(
        "# Delivery Gate\n\nStatus: not-run-public-blocked\n",
        encoding="utf-8",
    )


def write_run2_source_card(pack: Path, card_id: str = "card_cinematic_cover") -> None:
    (pack / "source_cards" / f"{card_id}.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "card_id": card_id,
                "source_id": "supervity_ai_keynote",
                "source_type": "commercial_case",
                "allowed_use": "derived_rules_only",
                "do_not_copy": "Do not copy screenshots, logos, layouts, full prose, or brand marks.",
                "observed_move": "Open with a high-confidence product promise before technical detail.",
                "why_it_works": "It gives executives a decision frame before process proof appears.",
                "ppt_translation": "Use a low-density cinematic cover with one claim and one focal object.",
                "quality_risk": "Can become generic if the cover has no concrete commercial decision.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def write_run2_video_card(pack: Path, card_id: str = "video_keynote_rhythm") -> None:
    (pack / "video_cards" / f"{card_id}.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "card_id": card_id,
                "source_id": "schema_2025_keynote_video",
                "source_type": "video",
                "allowed_use": "timestamped_observation_only",
                "do_not_copy": "Do not store full transcripts, screenshots, audio, or video frames.",
                "timestamp_map": ["00:00-00:45 opening frame", "00:45-02:00 setup sequence"],
                "keyframe_descriptions": ["Large title with sparse support text.", "Presenter advances from promise to system proof."],
                "pacing_notes": "Start low-density, then reveal structure in stages.",
                "transition_observations": "Use contrast between promise and proof rather than repeated panels.",
                "derived_aesthetic_cards": ["aesthetic_cinematic_cover", "aesthetic_proof_reveal"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def valid_run2_aesthetic_memory() -> dict:
    return {
        "schema_version": 1,
        "moves": [
            {
                "id": "aesthetic_cinematic_cover",
                "source_card_ids": ["card_cinematic_cover", "video_keynote_rhythm"],
                "aesthetic_move": "cinematic_cover",
                "trigger": "Use when the deck needs to create public-demo confidence before proof.",
                "composition_rule": "One focal object must occupy at least 35 percent of the slide area.",
                "typography_rule": "Title may use one or two lines; supporting text stays under 22 words.",
                "density_budget": {"max_claims": 1, "max_panels": 0, "max_words": 32},
                "rhythm_role": "cover",
                "ppt_primitive": "editable_text_plus_svg_or_generated_background",
                "negative_rules": ["no dashboard grid", "no dense status strip", "no four-column table"],
                "qa_signal": "Contact sheet must read as a launch moment, not a report title page.",
            }
        ],
    }


def valid_run2_evidence_memory() -> dict:
    return {
        "schema_version": 1,
        "claims": [
            {
                "id": "claim_data_changes_deck_quality",
                "source_card_ids": ["card_cinematic_cover"],
                "claim": "Structured design data should change visible deck quality.",
                "business_relevance": "The product must prove data-driven generation, not prompt decoration.",
                "allowed_use": "derived_rules_only",
                "qa_checks": ["evidence_alignment", "baseline_comparison"],
            }
        ],
    }


def valid_run2_asset_memory() -> dict:
    return {
        "schema_version": 1,
        "assets": [
            {
                "id": "asset_launch_atmosphere_background",
                "asset_type": "generated_background",
                "source_card_ids": ["card_cinematic_cover"],
                "allowed_slide_roles": ["cover", "close"],
                "provenance_state": "prompt_required_before_generation",
                "text_editability": "all_text_must_remain_editable",
                "license_state": "not-generated",
                "render_risks": ["bitmap_scaling", "contrast"],
                "accessibility_risks": ["low_contrast_if_used_under_text"],
            }
        ],
    }


def write_run2_memory_files(pack: Path) -> None:
    (pack / "aesthetic_memory.json").write_text(json.dumps(valid_run2_aesthetic_memory(), indent=2), encoding="utf-8")
    (pack / "evidence_memory.json").write_text(json.dumps(valid_run2_evidence_memory(), indent=2), encoding="utf-8")
    (pack / "asset_memory.json").write_text(json.dumps(valid_run2_asset_memory(), indent=2), encoding="utf-8")
    (pack / "narrative_spine.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "deck_length": 6,
                "slides": [
                    {"id": "slide_01", "rhythm_role": "cover", "aesthetic_move_ids": ["aesthetic_cinematic_cover"]}
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (pack / "slide_archetypes.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "archetypes": [
                    {
                        "id": "cinematic_cover",
                        "rhythm_role": "cover",
                        "aesthetic_move_ids": ["aesthetic_cinematic_cover"],
                        "density_budget": {"max_claims": 1, "max_panels": 0, "max_words": 32},
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_run2_profile_requires_data_skill_quality_files(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "missing required file: commercial_case.md" in result.errors
    assert "missing required file: source_cards/README.md" in result.errors
    assert "missing required file: video_cards/README.md" in result.errors
    assert "missing required file: aesthetic_memory.json" in result.errors
    assert "missing required file: asset_memory.json" in result.errors
    assert "missing required file: generation_briefs/run2_skill.md" in result.errors


def test_run2_profile_validates_memory_contracts(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is True, result.errors


def test_run2_profile_rejects_untraced_aesthetic_move(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    memory = valid_run2_aesthetic_memory()
    memory["moves"][0]["source_card_ids"] = ["missing_card"]
    (pack / "aesthetic_memory.json").write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "aesthetic_memory.moves[0].source_card_ids[0] missing_card is not defined by source_cards or video_cards" in result.errors


def test_run2_profile_rejects_asset_without_provenance_state(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    write_run2_source_card(pack)
    write_run2_video_card(pack)
    write_run2_memory_files(pack)
    memory = valid_run2_asset_memory()
    del memory["assets"][0]["provenance_state"]
    (pack / "asset_memory.json").write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert "asset_memory.assets[0] missing key: provenance_state" in result.errors
```

- [ ] **Step 2: Run tests and verify RED**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py -q
```

Expected: FAIL because `run2` is not an accepted profile.

- [ ] **Step 3: Add Run 2.0 constants and profile routing**

Modify `scripts/validate_ppt_case_pack.py`:

```python
RUN2_REQUIRED_FILES = [
    "README.md",
    "commercial_case.md",
    "sources.json",
    "source_cards/README.md",
    "video_cards/README.md",
    "evidence_memory.json",
    "aesthetic_memory.json",
    "asset_memory.json",
    "narrative_spine.json",
    "slide_archetypes.json",
    "aesthetic_rubric.md",
    "vulca_ppt_skill.md",
    "generation_briefs/README.md",
    "generation_briefs/prompt_only.md",
    "generation_briefs/run1_5_skill.md",
    "generation_briefs/run2_skill.md",
    "generation_briefs/bad_aesthetic_memory.md",
    "results/README.md",
    "results/comparison_report.md",
    "results/delivery_gate.md",
]

RUN2_SOURCE_TYPES = {"commercial_case", "tutorial", "video", "design_article", "reference_deck"}
RUN2_ALLOWED_USES = {"short_analysis", "derived_rules_only", "visual_inspiration", "timestamped_observation_only"}
RUN2_RHYTHM_ROLES = {"cover", "setup", "contrast", "proof", "climax", "relief", "close"}
RUN2_ASSET_TYPES = {"generated_background", "editable_svg", "native_shapes", "chart", "diagram", "video_derived_reference"}
```

Update `required_files_for_profile`:

```python
def required_files_for_profile(profile: str) -> list[str]:
    if profile == "default":
        return REQUIRED_FILES
    if profile == "run1":
        return [*REQUIRED_FILES, *RUN1_REQUIRED_FILES]
    if profile == "run1_5":
        return [*REQUIRED_FILES, *RUN1_5_REQUIRED_FILES]
    if profile == "run2":
        return RUN2_REQUIRED_FILES
    raise ValueError(f"unknown case-pack profile: {profile}")
```

- [ ] **Step 4: Add Run 2.0 card loaders and validators**

Add these helpers:

```python
def load_json_files(directory: Path, label: str, errors: list[str]) -> list[tuple[Path, dict[str, Any]]]:
    if not directory.exists():
        errors.append(f"{label} directory does not exist")
        return []
    if not directory.is_dir():
        errors.append(f"{label} must be a directory")
        return []
    files = sorted(path for path in directory.glob("*.json") if path.is_file())
    if not files:
        errors.append(f"{label} must contain at least one JSON card")
        return []
    return [(path, load_json(path, errors)) for path in files]


def collect_run2_card_ids(pack_dir: Path, errors: list[str]) -> set[str]:
    card_ids: set[str] = set()
    for label in ["source_cards", "video_cards"]:
        for path, data in load_json_files(pack_dir / label, label, errors):
            require_keys(path.name, data, ["schema_version", "card_id", "source_id", "source_type", "allowed_use", "do_not_copy"], errors)
            if "schema_version" in data:
                require_integer(f"{path.name}.schema_version", data["schema_version"], errors)
            if "card_id" in data and require_non_empty_string(f"{path.name}.card_id", data["card_id"], errors):
                if data["card_id"] in card_ids:
                    errors.append(f"{path.name}.card_id duplicates {data['card_id']}")
                card_ids.add(data["card_id"])
            if "source_type" in data:
                validate_choice(f"{path.name}.source_type", data["source_type"], RUN2_SOURCE_TYPES, errors)
            if "allowed_use" in data:
                validate_choice(f"{path.name}.allowed_use", data["allowed_use"], RUN2_ALLOWED_USES, errors)
            for key in ["source_id", "do_not_copy"]:
                if key in data:
                    require_non_empty_string(f"{path.name}.{key}", data[key], errors)
            if label == "source_cards":
                require_keys(path.name, data, ["observed_move", "why_it_works", "ppt_translation", "quality_risk"], errors)
                for key in ["observed_move", "why_it_works", "ppt_translation", "quality_risk"]:
                    if key in data:
                        require_non_empty_string(f"{path.name}.{key}", data[key], errors)
            if label == "video_cards":
                require_keys(
                    path.name,
                    data,
                    ["timestamp_map", "keyframe_descriptions", "pacing_notes", "transition_observations", "derived_aesthetic_cards"],
                    errors,
                )
                for key in ["timestamp_map", "keyframe_descriptions", "derived_aesthetic_cards"]:
                    if key in data:
                        validate_string_list(f"{path.name}.{key}", data[key], errors)
                for key in ["pacing_notes", "transition_observations"]:
                    if key in data:
                        require_non_empty_string(f"{path.name}.{key}", data[key], errors)
    return card_ids
```

- [ ] **Step 5: Add Run 2.0 memory validators**

Add:

```python
def validate_run2_source_references(label: str, source_card_ids: Any, card_ids: set[str], errors: list[str]) -> None:
    if not validate_string_list(label, source_card_ids, errors):
        return
    for index, source_card_id in enumerate(source_card_ids):
        if source_card_id not in card_ids:
            errors.append(f"{label}[{index}] {source_card_id} is not defined by source_cards or video_cards")


def validate_run2_evidence_memory(pack_dir: Path, card_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "evidence_memory.json", errors)
    require_keys("evidence_memory.json", data, ["schema_version", "claims"], errors)
    if "schema_version" in data:
        require_integer("evidence_memory.schema_version", data["schema_version"], errors)
    claims = data.get("claims", [])
    if not isinstance(claims, list) or not claims:
        errors.append("evidence_memory.claims must be a non-empty list")
        return
    required = ["id", "source_card_ids", "claim", "business_relevance", "allowed_use", "qa_checks"]
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"evidence_memory.claims[{index}] must be an object")
            continue
        require_keys(f"evidence_memory.claims[{index}]", claim, required, errors)
        for key in ["id", "claim", "business_relevance", "allowed_use"]:
            if key in claim:
                require_non_empty_string(f"evidence_memory.claims[{index}].{key}", claim[key], errors)
        if "source_card_ids" in claim:
            validate_run2_source_references(f"evidence_memory.claims[{index}].source_card_ids", claim["source_card_ids"], card_ids, errors)
        if "qa_checks" in claim:
            validate_string_list(f"evidence_memory.claims[{index}].qa_checks", claim["qa_checks"], errors)


def validate_run2_aesthetic_memory(pack_dir: Path, card_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "aesthetic_memory.json", errors)
    require_keys("aesthetic_memory.json", data, ["schema_version", "moves"], errors)
    if "schema_version" in data:
        require_integer("aesthetic_memory.schema_version", data["schema_version"], errors)
    moves = data.get("moves", [])
    if not isinstance(moves, list) or not moves:
        errors.append("aesthetic_memory.moves must be a non-empty list")
        return
    required = [
        "id",
        "source_card_ids",
        "aesthetic_move",
        "trigger",
        "composition_rule",
        "typography_rule",
        "density_budget",
        "rhythm_role",
        "ppt_primitive",
        "negative_rules",
        "qa_signal",
    ]
    for index, move in enumerate(moves):
        if not isinstance(move, dict):
            errors.append(f"aesthetic_memory.moves[{index}] must be an object")
            continue
        require_keys(f"aesthetic_memory.moves[{index}]", move, required, errors)
        for key in ["id", "aesthetic_move", "trigger", "composition_rule", "typography_rule", "ppt_primitive", "qa_signal"]:
            if key in move:
                require_non_empty_string(f"aesthetic_memory.moves[{index}].{key}", move[key], errors)
        if "source_card_ids" in move:
            validate_run2_source_references(f"aesthetic_memory.moves[{index}].source_card_ids", move["source_card_ids"], card_ids, errors)
        if "density_budget" in move:
            validate_number_mapping(f"aesthetic_memory.moves[{index}].density_budget", move["density_budget"], errors)
        if "rhythm_role" in move:
            validate_choice(f"aesthetic_memory.moves[{index}].rhythm_role", move["rhythm_role"], RUN2_RHYTHM_ROLES, errors)
        if "negative_rules" in move:
            validate_string_list(f"aesthetic_memory.moves[{index}].negative_rules", move["negative_rules"], errors)


def validate_run2_asset_memory(pack_dir: Path, card_ids: set[str], errors: list[str]) -> None:
    data = load_json(pack_dir / "asset_memory.json", errors)
    require_keys("asset_memory.json", data, ["schema_version", "assets"], errors)
    if "schema_version" in data:
        require_integer("asset_memory.schema_version", data["schema_version"], errors)
    assets = data.get("assets", [])
    if not isinstance(assets, list) or not assets:
        errors.append("asset_memory.assets must be a non-empty list")
        return
    required = [
        "id",
        "asset_type",
        "source_card_ids",
        "allowed_slide_roles",
        "provenance_state",
        "text_editability",
        "license_state",
        "render_risks",
        "accessibility_risks",
    ]
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            errors.append(f"asset_memory.assets[{index}] must be an object")
            continue
        require_keys(f"asset_memory.assets[{index}]", asset, required, errors)
        for key in ["id", "provenance_state", "text_editability", "license_state"]:
            if key in asset:
                require_non_empty_string(f"asset_memory.assets[{index}].{key}", asset[key], errors)
        if "asset_type" in asset:
            validate_choice(f"asset_memory.assets[{index}].asset_type", asset["asset_type"], RUN2_ASSET_TYPES, errors)
        if "source_card_ids" in asset:
            validate_run2_source_references(f"asset_memory.assets[{index}].source_card_ids", asset["source_card_ids"], card_ids, errors)
        for key in ["allowed_slide_roles", "render_risks", "accessibility_risks"]:
            if key in asset:
                validate_string_list(f"asset_memory.assets[{index}].{key}", asset[key], errors)
```

- [ ] **Step 6: Wire Run 2.0 validation into `validate_case_pack` and CLI**

Modify `validate_case_pack` after `validate_markdown_not_empty`:

```python
    if profile == "run2":
        card_ids = collect_run2_card_ids(root, errors)
        validate_run2_evidence_memory(root, card_ids, errors)
        validate_run2_aesthetic_memory(root, card_ids, errors)
        validate_run2_asset_memory(root, card_ids, errors)
        return ValidationResult(not errors, errors)
```

Keep existing Run 1 and Run 1.5 behavior:

```python
    if profile in {"run1", "run1_5"}:
        validate_design_memory(root, errors, profile=profile)
```

Update CLI choices:

```python
parser.add_argument("--profile", choices=["default", "run1", "run1_5", "run2"], default="default")
```

- [ ] **Step 7: Run validator tests**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py -q
```

Expected: PASS.

- [ ] **Step 8: Lint and commit**

```bash
ruff check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py
ruff format --check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py
git add scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py
git commit -m "test: add PPT Run 2.0 case-pack profile"
```

---

### Task 2: Add Run 2.0 Repository Contract Tests

**Files:**
- Create: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Write failing repository tests**

Create `tests/test_ppt_run2_data_skill_quality.py`:

```python
from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.validate_ppt_case_pack import validate_case_pack


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
EXPECTED_ARMS = {"prompt_only", "run1_5_skill", "run2_skill", "bad_aesthetic_memory"}
EXPECTED_MOVES = {
    "cinematic_cover",
    "low_density_claim",
    "big_object_layout",
    "editorial_comparison",
    "proof_reveal",
    "visual_climax",
    "premium_closing",
    "appendix_absorption",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def assert_contains(body: str, terms: list[str]) -> None:
    normalized = normalize(body)
    for term in terms:
        assert normalize(term) in normalized


def json_files(directory: str) -> list[Path]:
    return sorted((PACK / directory).glob("*.json"))


def test_run2_case_pack_is_valid() -> None:
    result = validate_case_pack(PACK, profile="run2")

    assert result.ok is True, result.errors


def test_run2_commercial_case_is_concrete_and_public_demo_oriented() -> None:
    body = (PACK / "commercial_case.md").read_text(encoding="utf-8")

    assert_contains(body, ["audience", "decision", "failed deck", "public-demo", "six slides"])
    assert "generic beautiful PPT" not in body


def test_run2_has_thick_source_and_video_cards() -> None:
    source_cards = json_files("source_cards")
    video_cards = json_files("video_cards")

    assert len(source_cards) >= 8
    assert len(video_cards) >= 2
    for path in [*source_cards, *video_cards]:
        card = load_json(path)
        assert_contains(card["do_not_copy"], ["do not copy"])
        assert card["allowed_use"] in {
            "short_analysis",
            "derived_rules_only",
            "visual_inspiration",
            "timestamped_observation_only",
        }


def test_run2_aesthetic_memory_has_required_public_demo_moves() -> None:
    memory = load_json(PACK / "aesthetic_memory.json")
    moves = {move["aesthetic_move"] for move in memory["moves"]}

    assert EXPECTED_MOVES <= moves
    assert len(memory["moves"]) >= 8
    for move in memory["moves"]:
        assert move["source_card_ids"]
        assert move["negative_rules"]
        assert move["density_budget"]["max_words"] <= 80
        assert move["rhythm_role"] in {"cover", "setup", "contrast", "proof", "climax", "relief", "close"}


def test_run2_narrative_spine_is_six_slide_public_demo() -> None:
    spine = load_json(PACK / "narrative_spine.json")

    assert spine["deck_length"] == 6
    assert [slide["rhythm_role"] for slide in spine["slides"]] == [
        "cover",
        "setup",
        "contrast",
        "proof",
        "climax",
        "close",
    ]


def test_run2_skill_is_a_staged_deck_director() -> None:
    body = (PACK / "vulca_ppt_skill.md").read_text(encoding="utf-8")

    assert_contains(
        body,
        [
            "select the narrative spine",
            "compile evidence memory",
            "compile aesthetic memory",
            "select assets",
            "generate code-first PPT modules",
            "run structural QA",
            "run aesthetic QA",
            "repair",
            "release decision",
        ],
    )
    assert_contains(body, ["move detail to appendix", "not compress the same content into smaller text"])


def test_run2_generation_briefs_define_four_arms() -> None:
    briefs = {path.stem for path in (PACK / "generation_briefs").glob("*.md") if path.name != "README.md"}

    assert briefs == EXPECTED_ARMS
    assert_contains((PACK / "generation_briefs" / "prompt_only.md").read_text(encoding="utf-8"), ["commercial brief only"])
    assert_contains((PACK / "generation_briefs" / "run1_5_skill.md").read_text(encoding="utf-8"), ["evidence-heavy"])
    assert_contains((PACK / "generation_briefs" / "run2_skill.md").read_text(encoding="utf-8"), ["aesthetic memory"])
    assert_contains((PACK / "generation_briefs" / "bad_aesthetic_memory.md").read_text(encoding="utf-8"), ["negative control"])


def test_run2_results_start_public_blocked() -> None:
    comparison = (PACK / "results" / "comparison_report.md").read_text(encoding="utf-8")
    delivery = (PACK / "results" / "delivery_gate.md").read_text(encoding="utf-8")

    assert_contains(comparison, ["Status", "not-run-public-blocked"])
    assert_contains(delivery, ["public publishing", "blocked", "native render", "human approval"])


def test_run2_pack_does_not_commit_generated_artifacts() -> None:
    blocked_suffixes = {".jpeg", ".jpg", ".mp4", ".pdf", ".png", ".pptx"}
    blocked = [
        str(path.relative_to(PACK))
        for path in PACK.rglob("*")
        if path.is_file() and path.suffix.lower() in blocked_suffixes
    ]

    assert blocked == []
```

- [ ] **Step 2: Run tests and verify RED**

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q
```

Expected: FAIL because the Run 2.0 package does not exist.

- [ ] **Step 3: Keep RED tests uncommitted until Task 3**

Do not commit failing tests alone. This repository commits coherent verified changes after the package exists.

---

### Task 3: Build The Run 2.0 Data Package

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/**`
- Modify: `docs/product/roadmap.md`
- Test: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Create package directories**

```bash
mkdir -p docs/product/ppt-run2-data-skill-quality/source_cards
mkdir -p docs/product/ppt-run2-data-skill-quality/video_cards
mkdir -p docs/product/ppt-run2-data-skill-quality/generation_briefs
mkdir -p docs/product/ppt-run2-data-skill-quality/results
```

- [ ] **Step 2: Create `sources.json` with curated public references**

Create `docs/product/ppt-run2-data-skill-quality/sources.json`:

```json
{
  "schema_version": 1,
  "sources": [
    {
      "id": "geo_figma_slides",
      "title": "GEO - Figma Slides",
      "url": "https://geo-nyc.com/projects/figma-slides/",
      "role": "presentation_product_reference",
      "accessed_on": "2026-06-01",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis only; do not copy visuals, layouts, screenshots, brand marks, template files, or full prose."
    },
    {
      "id": "figma_config_2025_identity",
      "title": "How Figma Shaped the Visual Identity for Config 2025",
      "url": "https://www.figma.com/blog/how-we-shaped-the-visual-identity-for-config-2025/",
      "role": "identity_system_reference",
      "accessed_on": "2026-06-01",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis only; do not copy visuals, layouts, screenshots, brand marks, template files, or full prose."
    },
    {
      "id": "supervity_ai_keynote",
      "title": "MUSE Creatives - Supervity AI Thought Leadership Presentation",
      "url": "https://musecreatives.org/case-studies/visual-presentation-for-ai-thought-leadership/",
      "role": "commercial_ai_keynote_reference",
      "accessed_on": "2026-06-01",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis only; do not copy visuals, layouts, screenshots, brand marks, template files, or full prose."
    },
    {
      "id": "launch_lab_sales_deck",
      "title": "Whitepage Studio - Launch Lab Sales Deck",
      "url": "https://www.whitepage.studio/portfolio/launch-lab",
      "role": "sales_deck_reference",
      "accessed_on": "2026-06-01",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis only; do not copy visuals, layouts, screenshots, brand marks, template files, or full prose."
    },
    {
      "id": "google_cloud_next_keynote",
      "title": "Sparks - Google Cloud Next",
      "url": "https://www.wearesparks.com/our-work/google-cloud-next/",
      "role": "large_scale_keynote_reference",
      "accessed_on": "2026-06-01",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis only; do not copy visuals, layouts, screenshots, brand marks, template files, or full prose."
    },
    {
      "id": "slidemodel_visual_hierarchy",
      "title": "SlideModel - Visual Hierarchy for Presentations",
      "url": "https://slidemodel.com/visual-hierarchy-for-presentations/",
      "role": "tutorial_reference",
      "accessed_on": "2026-06-01",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis only; do not copy visuals, layouts, screenshots, brand marks, template files, or full prose."
    },
    {
      "id": "present_partners_whitespace",
      "title": "Present Partners - White Space and Visual Hierarchy Slides",
      "url": "https://present.partners/resources/white-space-visual-hierarchy-slides",
      "role": "tutorial_reference",
      "accessed_on": "2026-06-01",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use for original analysis only; do not copy visuals, layouts, screenshots, brand marks, template files, or full prose."
    },
    {
      "id": "schema_2025_keynote_video",
      "title": "Schema 2025 Keynote Video Page",
      "url": "https://www.tldwyoutube.com/video/QFjIaN_wlWg",
      "role": "video_reference",
      "accessed_on": "2026-06-01",
      "allowed_use": "reference_analysis_only",
      "copyright_note": "Use timestamped observations only; do not store full transcripts, screenshots, audio, or video frames."
    }
  ]
}
```

- [ ] **Step 3: Create README and commercial case**

Create `README.md` with sections:

```markdown
# PPT Run 2.0 Data Skill Quality

Status: not-run-public-blocked.

Run 2.0 thickens the five fixed PPT product layers before generation:

1. Real commercial case.
2. Tutorial, video, and case data.
3. Evidence, aesthetic, and asset memory.
4. Skill workflow.
5. Rerun and evaluation.

Run 2.0 does not claim post-training or fine-tuning. It tests runtime case-pack-controlled, code-generated PPT output.

## Public Publishing

Public publishing remains blocked until generated outputs exist, native or cross-platform render checks pass, asset provenance is complete, and human review approves release.
```

Create `commercial_case.md` with these exact required headings and original prose under each:

```markdown
# Commercial Case

## Audience
AI product builders, design leaders, and platform reviewers evaluating whether Vulca can produce high-quality editable presentations from structured design knowledge.

## Decision
The deck must convince viewers that Vulca is not a one-shot image or slide generator. It is a code-generated presentation system that can learn from curated design knowledge while keeping evidence, assets, and release gates inspectable.

## Business Objective
Create a public-demo candidate that makes the PPT wedge understandable, credible, and visually strong enough for a product video.

## Deck Length
Six slides in the main public-demo deck. Supporting evidence belongs in appendix, speaker notes, or result reports.

## Must-Win Impression
The viewer should feel that the system has design taste, not only engineering discipline.

## Failed Deck
A failed deck looks like a generic engineering report: repeated dashboards, small labels, dense tables, low visual tension, no cinematic opening, and no clear visual climax.

## Public-Demo Constraints
Core text must remain editable. Images and SVGs can support atmosphere or diagrams, but they must not replace editable slide structure. Source visuals, copied layouts, logos, screenshots, full transcripts, and long copied prose are not allowed.
```

- [ ] **Step 4: Create card README files**

Create `source_cards/README.md`:

```markdown
# Source Cards

Each JSON file is one original analysis card derived from a public reference. Store observations and derived design rules only. Do not store copied layouts, screenshots, logos, full article text, full transcripts, or proprietary assets.

Required fields: `schema_version`, `card_id`, `source_id`, `source_type`, `allowed_use`, `do_not_copy`, `observed_move`, `why_it_works`, `ppt_translation`, `quality_risk`.
```

Create `video_cards/README.md`:

```markdown
# Video Cards

Video cards record timestamped observations and pacing analysis only. They do not store full transcripts, screenshots, downloaded media, audio, or video frames.

Required fields: `schema_version`, `card_id`, `source_id`, `source_type`, `allowed_use`, `do_not_copy`, `timestamp_map`, `keyframe_descriptions`, `pacing_notes`, `transition_observations`, `derived_aesthetic_cards`.
```

- [ ] **Step 5: Create at least 8 source-card JSON files**

Create these files with the validator-required fields:

```text
source_cards/card_cinematic_cover.json
source_cards/card_low_density_claim.json
source_cards/card_big_object_layout.json
source_cards/card_editorial_comparison.json
source_cards/card_proof_reveal.json
source_cards/card_visual_climax.json
source_cards/card_premium_closing.json
source_cards/card_appendix_absorption.json
```

Use `source_type` values from the validator set and `allowed_use` values from the validator set. Each `ppt_translation` must name an editable PPT primitive and each `quality_risk` must describe how the move can degrade into a generic or engineering-report look.

- [ ] **Step 6: Create at least 2 video-card JSON files**

Create:

```text
video_cards/video_keynote_rhythm.json
video_cards/video_transition_pacing.json
```

Both cards must use `allowed_use: "timestamped_observation_only"` and must avoid full transcripts, screenshots, audio, and video frame storage.

- [ ] **Step 7: Run repository tests and verify they still fail only on missing memory/skill files**

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q
```

Expected: FAIL until Task 4 and Task 5 create memory and skill files.

Do not commit yet.

---

### Task 4: Build Evidence, Aesthetic, Asset Memory And Archetypes

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/evidence_memory.json`
- Create: `docs/product/ppt-run2-data-skill-quality/aesthetic_memory.json`
- Create: `docs/product/ppt-run2-data-skill-quality/asset_memory.json`
- Create: `docs/product/ppt-run2-data-skill-quality/narrative_spine.json`
- Create: `docs/product/ppt-run2-data-skill-quality/slide_archetypes.json`
- Test: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Create `aesthetic_memory.json` with 8 moves**

Create `aesthetic_memory.json` with `schema_version: 1` and `moves` for:

```text
cinematic_cover
low_density_claim
big_object_layout
editorial_comparison
proof_reveal
visual_climax
premium_closing
appendix_absorption
```

Each move must include:

```json
{
  "id": "aesthetic_cinematic_cover",
  "source_card_ids": ["card_cinematic_cover", "video_keynote_rhythm"],
  "aesthetic_move": "cinematic_cover",
  "trigger": "Use when the deck needs to create public-demo confidence before proof.",
  "composition_rule": "One focal object must occupy at least 35 percent of the slide area.",
  "typography_rule": "Title may use one or two lines; supporting text stays under 22 words.",
  "density_budget": {
    "max_claims": 1,
    "max_panels": 0,
    "max_words": 32
  },
  "rhythm_role": "cover",
  "ppt_primitive": "editable_text_plus_svg_or_generated_background",
  "negative_rules": ["no dashboard grid", "no dense status strip", "no four-column table"],
  "qa_signal": "Contact sheet must read as a launch moment, not a report title page."
}
```

Adapt the values for the other seven moves. Keep every `density_budget.max_words` at or below `80`.

- [ ] **Step 2: Create `evidence_memory.json`**

Create at least 6 claims:

```text
claim_data_changes_deck_quality
claim_aesthetic_memory_controls_rhythm
claim_asset_memory_preserves_editability
claim_bad_aesthetic_memory_is_negative_control
claim_appendix_absorbs_proof_detail
claim_public_release_requires_render_and_human_gate
```

Each claim must trace to one or more source-card ids and include `qa_checks`.

- [ ] **Step 3: Create `asset_memory.json`**

Create at least 4 assets:

```text
asset_launch_atmosphere_background
asset_system_svg_mark
asset_evidence_flow_diagram
asset_comparison_delta_chart
```

Each asset must include `provenance_state`, `license_state`, `text_editability`, `render_risks`, and `accessibility_risks`.

- [ ] **Step 4: Create `narrative_spine.json`**

Create a six-slide spine:

```json
{
  "schema_version": 1,
  "deck_length": 6,
  "slides": [
    {
      "id": "slide_01",
      "rhythm_role": "cover",
      "title": "Vulca",
      "job": "Create a public-demo opening that feels designed before explaining the system.",
      "aesthetic_move_ids": ["aesthetic_cinematic_cover"],
      "evidence_claim_ids": ["claim_data_changes_deck_quality"]
    },
    {
      "id": "slide_02",
      "rhythm_role": "setup",
      "title": "The problem is not making slides. It is making taste repeatable.",
      "job": "Frame the commercial problem and avoid generic slide-generator positioning.",
      "aesthetic_move_ids": ["aesthetic_low_density_claim"],
      "evidence_claim_ids": ["claim_aesthetic_memory_controls_rhythm"]
    },
    {
      "id": "slide_03",
      "rhythm_role": "contrast",
      "title": "Data changes the deck only when it becomes design memory.",
      "job": "Contrast loose references with structured evidence, aesthetic, and asset memory.",
      "aesthetic_move_ids": ["aesthetic_editorial_comparison"],
      "evidence_claim_ids": ["claim_data_changes_deck_quality"]
    },
    {
      "id": "slide_04",
      "rhythm_role": "proof",
      "title": "The skill chooses what to show, what to remove, and what to gate.",
      "job": "Show the staged deck-director workflow without turning it into a dashboard.",
      "aesthetic_move_ids": ["aesthetic_proof_reveal", "aesthetic_appendix_absorption"],
      "evidence_claim_ids": ["claim_appendix_absorbs_proof_detail"]
    },
    {
      "id": "slide_05",
      "rhythm_role": "climax",
      "title": "Run 2.0 should beat both prompt-only and Run 1.5.",
      "job": "Create the visual climax around the comparison and negative control.",
      "aesthetic_move_ids": ["aesthetic_visual_climax", "aesthetic_big_object_layout"],
      "evidence_claim_ids": ["claim_bad_aesthetic_memory_is_negative_control"]
    },
    {
      "id": "slide_06",
      "rhythm_role": "close",
      "title": "Public-ready is a gate, not a vibe.",
      "job": "End with release discipline: render, provenance, human approval.",
      "aesthetic_move_ids": ["aesthetic_premium_closing"],
      "evidence_claim_ids": ["claim_public_release_requires_render_and_human_gate"]
    }
  ]
}
```

- [ ] **Step 5: Create `slide_archetypes.json`**

Create archetypes matching the six narrative roles:

```text
cinematic_cover
low_density_problem
editorial_memory_comparison
staged_skill_reveal
comparison_climax
premium_gate_close
```

Each archetype must include `rhythm_role`, `aesthetic_move_ids`, and a density budget.

- [ ] **Step 6: Run validator and repository tests**

```bash
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q
```

Expected: FAIL only until Task 5 creates skill, rubric, generation briefs, and results files.

Do not commit yet.

---

### Task 5: Build Run 2.0 Skill, Generation Briefs, Rubric, Results, And Roadmap

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/aesthetic_rubric.md`
- Create: `docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md`
- Create: `docs/product/ppt-run2-data-skill-quality/generation_briefs/*.md`
- Create: `docs/product/ppt-run2-data-skill-quality/results/*.md`
- Modify: `docs/product/roadmap.md`
- Test: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Create `aesthetic_rubric.md`**

Include these scored dimensions:

```markdown
# Aesthetic Rubric

Status: not-run-public-blocked.

Scores are 0-5. Higher is better.

| Dimension | Checks |
| --- | --- |
| `commercial_specificity` | The deck names a concrete audience, decision, and failure mode. |
| `evidence_alignment` | Claims trace to evidence memory and source cards. |
| `aesthetic_memory_usage` | Visible design moves trace to aesthetic memory ids. |
| `visual_hierarchy` | Each slide has one dominant claim and one dominant visual object. |
| `rhythm_variance` | The six-slide sequence includes cover, setup, contrast, proof, climax, and close. |
| `density_control` | Main slides avoid dense tables, repeated dashboard grids, and small-label overload. |
| `asset_discipline` | Assets support atmosphere or diagrams without replacing editable slide structure. |
| `editability` | Core text, claims, labels, and proof objects remain editable. |
| `render_risk` | Native or cross-platform render checks are recorded before public release. |

Run 2.0 must beat Run 1.5 on `aesthetic_memory_usage`, `rhythm_variance`, and `density_control`, or the rerun has not solved the right problem.
```

- [ ] **Step 2: Create `vulca_ppt_skill.md`**

Create a staged deck-director skill with these sections:

```markdown
# Vulca PPT Skill

Status: not-run.

Run 2.0 workflow:

1. Read `commercial_case.md` and select the narrative spine.
2. Compile evidence memory into claims and guardrails.
3. Compile aesthetic memory into slide archetypes, rhythm roles, density budgets, and negative rules.
4. Select assets only after the slide role is known.
5. Generate code-first PPT modules with editable text and native structures.
6. Run structural QA before aesthetic repair.
7. Run aesthetic QA against the rubric.
8. Repair the deck with explicit reasons.
9. Emit a release decision: internal only, demo candidate, or public blocked.

## Deletion Rule

If a slide has too many proof objects, move detail to appendix, speaker notes, or result reports. Do not compress the same content into smaller text.

## Public-Ready Rule

Public-ready is a gate, not a vibe. Do not claim public readiness until render, provenance, and human approval gates pass.
```

- [ ] **Step 3: Create generation briefs**

Create `generation_briefs/README.md`:

```markdown
# Generation Briefs

Status: not-run.

Run 2.0 compares four arms: `prompt_only`, `run1_5_skill`, `run2_skill`, and `bad_aesthetic_memory`.
```

Create four arm files:

```markdown
# Prompt Only

Arm id: `prompt_only`.

Use the commercial brief only. Do not use evidence memory, aesthetic memory, asset memory, source cards, video cards, Run 1.5 skill files, or Run 2.0 skill files.
```

```markdown
# Run 1.5 Skill

Arm id: `run1_5_skill`.

Use the previous evidence-heavy product-lab workflow as the current baseline. This arm is expected to be more traceable than prompt-only but more report-like than Run 2.0.
```

```markdown
# Run 2.0 Skill

Arm id: `run2_skill`.

Use commercial case, source cards, video cards, evidence memory, aesthetic memory, asset memory, narrative spine, slide archetypes, and the Run 2.0 staged deck-director skill.
```

```markdown
# Bad Aesthetic Memory

Arm id: `bad_aesthetic_memory`.

Use valid evidence memory but intentionally weak aesthetic memory: repeated dashboard grids, dense tables, small labels, low rhythm variance, no visual climax, and no low-density high-impact slides. This is the negative control for the aesthetic layer.
```

- [ ] **Step 4: Create result scaffolds**

Create `results/README.md`:

```markdown
# Results

Status: not-run-public-blocked.

Generated decks, contact sheets, previews, and layout JSON remain local under `outputs/` unless the user explicitly approves release packaging.
```

Create `results/comparison_report.md`:

```markdown
# Comparison Report

Status: not-run-public-blocked.

Run 2.0 has not generated comparison arms yet.

Required arms:

| Arm | Status |
| --- | --- |
| `prompt_only` | not-run |
| `run1_5_skill` | not-run |
| `run2_skill` | not-run |
| `bad_aesthetic_memory` | not-run |

The comparison must score commercial specificity, evidence alignment, aesthetic memory usage, visual hierarchy, rhythm variance, density control, asset discipline, editability, and render risk.
```

Create `results/delivery_gate.md`:

```markdown
# Delivery Gate

Status: not-run-public-blocked.

Public publishing is blocked until generated outputs exist, native render or cross-platform render inspection passes, asset provenance is complete, and human approval is recorded.
```

- [ ] **Step 5: Update roadmap**

Modify `docs/product/roadmap.md` with a concise Run 2.0 entry:

```markdown
## PPT Run 2.0 Data And Skill Quality

Status: planned / package-building.

Run 2.0 deepens the same five fixed PPT product layers: real commercial case, tutorial/video/case data, memory, skill workflow, and rerun/evaluation. The goal is not to add a sixth stage, but to make the data and skill layers materially higher quality before rerunning generation.
```

- [ ] **Step 6: Run tests and validators**

```bash
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py -q
```

Expected: PASS.

- [ ] **Step 7: Lint and commit**

```bash
ruff check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py
ruff format --check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py
git add docs/product/ppt-run2-data-skill-quality docs/product/roadmap.md tests/test_ppt_run2_data_skill_quality.py
git commit -m "docs: add PPT Run 2.0 data skill package"
```

---

### Task 6: Run External Review And Prepare Execution Handoff

**Files:**
- Modify if needed: `docs/product/ppt-run2-data-skill-quality/**`
- Modify if needed: `docs/superpowers/plans/2026-06-01-vulca-ppt-run2-data-skill-quality.md`

- [ ] **Step 1: Run AWT logic review on written rationale**

Use Academic Writing Toolkit paragraph-level logic review on:

```text
docs/product/ppt-run2-data-skill-quality/README.md
docs/product/ppt-run2-data-skill-quality/commercial_case.md
docs/product/ppt-run2-data-skill-quality/aesthetic_rubric.md
docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md
```

Expected: no paragraph-level contradictions. If AWT finds issues, patch the affected docs and rerun package tests.

- [ ] **Step 2: Run Gemini plan critique**

Ask Gemini-agent to critique whether the Run 2.0 package is likely to solve the engineering-report aesthetic:

```text
Review docs/product/ppt-run2-data-skill-quality/ plus the Run 2.0 spec. Focus on whether source cards, video cards, aesthetic memory, and skill workflow are strong enough to justify rerunning generation. Identify missing aesthetic rules, weak source-card translation, or risks that the result will still look like an engineering report.
```

Expected: actionable critique. Patch material findings before generation.

- [ ] **Step 3: Run full relevant verification**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py tests/test_ppt_run2_data_skill_quality.py -q
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
ruff check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py
ruff format --check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py
git status -sb
```

Expected:

- pytest passes;
- Run 2.0 validator prints `case pack ok`;
- ruff check and format check pass;
- only expected untracked local generated artifacts remain under `outputs/`.

- [ ] **Step 4: Commit review fixes**

If Task 6 changed docs or tests:

```bash
git add docs/product/ppt-run2-data-skill-quality docs/superpowers/plans/2026-06-01-vulca-ppt-run2-data-skill-quality.md scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py
git commit -m "docs: tighten PPT Run 2.0 data skill quality package"
```

If no changes were required, do not create an empty commit.

---

### Task 7: Generate Run 2.0 Pilot Deck Arms Locally

**Files:**
- Local only: `outputs/$THREAD_ID/presentations/ppt-run2-prompt-only/**`
- Local only: `outputs/$THREAD_ID/presentations/ppt-run2-run1-5-skill/**`
- Local only: `outputs/$THREAD_ID/presentations/ppt-run2-full-vulca/**`
- Local only: `outputs/$THREAD_ID/presentations/ppt-run2-bad-aesthetic-memory/**`
- Read: `docs/product/ppt-run2-data-skill-quality/**`
- Read: `docs/product/ppt-run1-5-product-lab/**`

Use the `presentations:Presentations` skill for this task. Do not begin Task 7 until Tasks 1-6 pass and the user approves the data and skill package.

- [ ] **Step 1: Prepare local generation workspaces**

Create local-only output directories:

```bash
mkdir -p outputs/$THREAD_ID/presentations/ppt-run2-prompt-only
mkdir -p outputs/$THREAD_ID/presentations/ppt-run2-run1-5-skill
mkdir -p outputs/$THREAD_ID/presentations/ppt-run2-full-vulca
mkdir -p outputs/$THREAD_ID/presentations/ppt-run2-bad-aesthetic-memory
```

Expected: directories exist under `outputs/`. They remain untracked.

- [ ] **Step 2: Apply arm isolation and generation protocol**

Before any arm generation:

- Follow `docs/product/ppt-run2-data-skill-quality/generation_protocol.md`.
- Run each arm from a fresh generation prompt/context and a separate output directory.
- Do not reuse cached memory summaries, slide code, layout JSON, SVG assets, screenshots, contact sheets, or repair notes across arms.
- Record allowed files, forbidden files, model/provider, tool versions, cache scope, native PPT object counts, raster-image checks, and layout geometry checks in each arm's local `trace_manifest.json`.

Expected: any arm missing protocol evidence remains `internal_only` and cannot support winner/public-readiness claims.

- [ ] **Step 3: Generate the `prompt_only` arm**

Input boundary:

```text
Use only docs/product/ppt-run2-data-skill-quality/commercial_case.md.
Do not use source cards, video cards, evidence memory, aesthetic memory, asset memory, narrative spine, slide archetypes, Run 1.5 package files, or Run 2.0 skill files.
Generate a six-slide editable PPTX and contact sheet.
```

Write local notes:

```text
outputs/$THREAD_ID/presentations/ppt-run2-prompt-only/generation-notes.md
```

Expected local artifacts:

```text
outputs/$THREAD_ID/presentations/ppt-run2-prompt-only/output/ppt-run2-prompt-only.pptx
outputs/$THREAD_ID/presentations/ppt-run2-prompt-only/preview/contact-sheet.png
outputs/$THREAD_ID/presentations/ppt-run2-prompt-only/layout/final/*.layout.json
outputs/$THREAD_ID/presentations/ppt-run2-prompt-only/trace_manifest.json
```

- [ ] **Step 4: Generate the `run1_5_skill` arm**

Input boundary:

```text
Use docs/product/ppt-run1-5-product-lab plus docs/product/ppt-run2-data-skill-quality/commercial_case.md.
Do not use Run 2.0 source cards, video cards, aesthetic memory, asset memory, narrative spine, or slide archetypes.
Generate a six-slide editable PPTX and contact sheet using the older evidence-heavy/product-lab style.
```

Expected local artifacts:

```text
outputs/$THREAD_ID/presentations/ppt-run2-run1-5-skill/output/ppt-run2-run1-5-skill.pptx
outputs/$THREAD_ID/presentations/ppt-run2-run1-5-skill/preview/contact-sheet.png
outputs/$THREAD_ID/presentations/ppt-run2-run1-5-skill/layout/final/*.layout.json
outputs/$THREAD_ID/presentations/ppt-run2-run1-5-skill/trace_manifest.json
```

- [ ] **Step 5: Generate the `run2_skill` arm**

Input boundary:

```text
Use docs/product/ppt-run2-data-skill-quality/commercial_case.md,
source_cards,
video_cards,
evidence_memory.json,
aesthetic_memory.json,
asset_memory.json,
narrative_spine.json,
slide_archetypes.json,
aesthetic_rubric.md,
and vulca_ppt_skill.md.
Generate a six-slide editable PPTX and contact sheet.
```

Expected local artifacts:

```text
outputs/$THREAD_ID/presentations/ppt-run2-full-vulca/output/ppt-run2-full-vulca.pptx
outputs/$THREAD_ID/presentations/ppt-run2-full-vulca/preview/contact-sheet.png
outputs/$THREAD_ID/presentations/ppt-run2-full-vulca/layout/final/*.layout.json
outputs/$THREAD_ID/presentations/ppt-run2-full-vulca/trace_manifest.json
```

- [ ] **Step 6: Generate the `bad_aesthetic_memory` arm**

Input boundary:

```text
Use valid commercial case, source cards, video cards, evidence memory, asset memory, narrative spine, and Run 2.0 skill.
Replace aesthetic_memory.json at runtime with docs/product/ppt-run2-data-skill-quality/generation_briefs/bad_aesthetic_memory_replacement.json.
Do not use the good aesthetic_memory.json or good slide_archetypes.json.
Do not corrupt JSON, do not break PPTX structure, and do not remove source boundaries.
Generate a six-slide editable PPTX and contact sheet.
```

Expected local artifacts:

```text
outputs/$THREAD_ID/presentations/ppt-run2-bad-aesthetic-memory/output/ppt-run2-bad-aesthetic-memory.pptx
outputs/$THREAD_ID/presentations/ppt-run2-bad-aesthetic-memory/preview/contact-sheet.png
outputs/$THREAD_ID/presentations/ppt-run2-bad-aesthetic-memory/layout/final/*.layout.json
outputs/$THREAD_ID/presentations/ppt-run2-bad-aesthetic-memory/trace_manifest.json
```

- [ ] **Step 7: Run structural delivery QA for all four arms**

Run:

```bash
python3 scripts/validate_pptx_delivery.py \
  --pptx outputs/$THREAD_ID/presentations/ppt-run2-prompt-only/output/ppt-run2-prompt-only.pptx \
  --layout-dir outputs/$THREAD_ID/presentations/ppt-run2-prompt-only/layout/final \
  --contact-sheet outputs/$THREAD_ID/presentations/ppt-run2-prompt-only/preview/contact-sheet.png \
  --label ppt-run2-prompt-only \
  --out outputs/$THREAD_ID/presentations/ppt-run2-prompt-only/qa/delivery_report.md

python3 scripts/validate_pptx_delivery.py \
  --pptx outputs/$THREAD_ID/presentations/ppt-run2-run1-5-skill/output/ppt-run2-run1-5-skill.pptx \
  --layout-dir outputs/$THREAD_ID/presentations/ppt-run2-run1-5-skill/layout/final \
  --contact-sheet outputs/$THREAD_ID/presentations/ppt-run2-run1-5-skill/preview/contact-sheet.png \
  --label ppt-run2-run1-5-skill \
  --out outputs/$THREAD_ID/presentations/ppt-run2-run1-5-skill/qa/delivery_report.md

python3 scripts/validate_pptx_delivery.py \
  --pptx outputs/$THREAD_ID/presentations/ppt-run2-full-vulca/output/ppt-run2-full-vulca.pptx \
  --layout-dir outputs/$THREAD_ID/presentations/ppt-run2-full-vulca/layout/final \
  --contact-sheet outputs/$THREAD_ID/presentations/ppt-run2-full-vulca/preview/contact-sheet.png \
  --label ppt-run2-full-vulca \
  --out outputs/$THREAD_ID/presentations/ppt-run2-full-vulca/qa/delivery_report.md

python3 scripts/validate_pptx_delivery.py \
  --pptx outputs/$THREAD_ID/presentations/ppt-run2-bad-aesthetic-memory/output/ppt-run2-bad-aesthetic-memory.pptx \
  --layout-dir outputs/$THREAD_ID/presentations/ppt-run2-bad-aesthetic-memory/layout/final \
  --contact-sheet outputs/$THREAD_ID/presentations/ppt-run2-bad-aesthetic-memory/preview/contact-sheet.png \
  --label ppt-run2-bad-aesthetic-memory \
  --out outputs/$THREAD_ID/presentations/ppt-run2-bad-aesthetic-memory/qa/delivery_report.md
```

Expected: each command exits 0 with delivery gate `internal-demo-ok-public-blocked`. Public release remains blocked.

- [ ] **Step 8: Commit nothing from `outputs/`**

Run:

```bash
git ls-files outputs | wc -l
git status -sb
```

Expected: tracked outputs count remains `0`; generated artifacts appear only as untracked `outputs/`.

---

### Task 8: Review, Score, Repair, And Record Run 2.0 Results

**Files:**
- Modify: `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Local only: `outputs/$THREAD_ID/presentations/ppt-run2-*/**`

- [ ] **Step 1: Run Gemini artifact review on all contact sheets**

Use `gemini-agent artifact-review` on:

```text
outputs/$THREAD_ID/presentations/ppt-run2-prompt-only/preview/contact-sheet.png
outputs/$THREAD_ID/presentations/ppt-run2-run1-5-skill/preview/contact-sheet.png
outputs/$THREAD_ID/presentations/ppt-run2-full-vulca/preview/contact-sheet.png
outputs/$THREAD_ID/presentations/ppt-run2-bad-aesthetic-memory/preview/contact-sheet.png
```

Review criteria:

```text
Score 0-5 for commercial_specificity, evidence_alignment, aesthetic_memory_usage, visual_hierarchy, rhythm_variance, density_control, asset_discipline, editability, and render_risk.
Identify whether the deck still feels like an engineering report.
Identify whether Run 2.0 is visibly better than Run 1.5 skill and prompt-only.
Identify whether bad_aesthetic_memory degrades visual quality without breaking structure.
```

Expected: compact review artifacts saved under `.gemini-agent/artifacts/`.

- [ ] **Step 2: Repair the `run2_skill` arm once if review finds focused issues**

Only perform one focused repair pass before recording results. Allowed repair types:

```text
reduce text density
increase focal-object scale
replace repeated dashboard grid with editorial comparison
move proof detail to appendix or speaker notes
strengthen cover or closing slide
```

Forbidden repair types:

```text
copy source screenshots
flatten editable text into images
remove evidence alignment
change result scores without review evidence
claim public-ready before human/native-render approval
```

After repair, rerun delivery QA for `ppt-run2-full-vulca`.

- [ ] **Step 3: Update result reports**

Update `results/comparison_report.md` with this structure. Fill every `Average` cell with the numeric average from the review table before committing:

```markdown
# Comparison Report

Status: reviewed-public-blocked.

| Arm | Generation status | Review status | Delivery gate | Average |
| --- | --- | --- | --- | ---: |
| `prompt_only` | generated | reviewed | `internal-demo-ok-public-blocked` | 0.00 |
| `run1_5_skill` | generated | reviewed | `internal-demo-ok-public-blocked` | 0.00 |
| `run2_skill` | generated or generated-repaired | reviewed | `internal-demo-ok-public-blocked` | 0.00 |
| `bad_aesthetic_memory` | generated | reviewed | `internal-demo-ok-public-blocked` | 0.00 |

Public publishing remains blocked until native or cross-platform render inspection and human approval pass.
```

Replace the `0.00` example values with actual averages from the Gemini/human review table. Do not commit the report while any average is still `0.00`.

Update `results/delivery_gate.md` with each arm's local artifact paths and structural QA status. Keep status `reviewed-public-blocked`.

- [ ] **Step 4: Update repository tests from not-run to reviewed-public-blocked**

Modify `test_run2_results_start_public_blocked` in `tests/test_ppt_run2_data_skill_quality.py` into:

```python
def test_run2_results_reviewed_and_public_blocked() -> None:
    comparison = (PACK / "results" / "comparison_report.md").read_text(encoding="utf-8")
    delivery = (PACK / "results" / "delivery_gate.md").read_text(encoding="utf-8")

    assert_contains(comparison, ["Status", "reviewed-public-blocked"])
    assert_contains(comparison, ["prompt_only", "run1_5_skill", "run2_skill", "bad_aesthetic_memory"])
    assert_contains(delivery, ["public publishing", "blocked", "native render", "human approval"])
```

- [ ] **Step 5: Run final verification**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py tests/test_ppt_run2_data_skill_quality.py -q
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
ruff check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py
ruff format --check scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py
git ls-files outputs | wc -l
git status -sb
```

Expected:

- pytest passes;
- Run 2.0 validator prints `case pack ok`;
- ruff check and format check pass;
- tracked outputs count remains `0`;
- public publishing remains blocked.

- [ ] **Step 6: Commit reviewed results**

```bash
git add docs/product/ppt-run2-data-skill-quality/results tests/test_ppt_run2_data_skill_quality.py
git commit -m "docs: record PPT Run 2.0 pilot results"
```

Do not commit local generated artifacts from `outputs/`.

## Execution Handoff

After this plan is approved, use `superpowers:subagent-driven-development` and execute one task at a time. Each implementation task should end with review, verification, and a small commit. Do not generate Run 2.0 PPT decks until Tasks 1-6 pass and the user approves starting the pilot rerun.
