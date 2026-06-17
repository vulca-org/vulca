# PPT Run 2.6R Visual Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Run 2.6R as a same-stage visual repair pass where the full-skill PPT output is visibly different from Run 2.5/2.6 while preserving Run 2.6 data/workflow trace boundaries.

**Architecture:** Implement in two verified commits. The first commit adds a visual repair policy, workflow/trace contract fields, and tests. The second commit adds a Run 2.6R generator with new full-arm drawing functions, reruns the four arms, refreshes QA, regenerates the two required comparison images, and records public-blocked results.

**Tech Stack:** Python stdlib JSON tests, pytest, ruff, Node.js artifact-tool generator, Pillow comparison sheet builder, existing PPT layout/delivery/trace QA scripts, Gemini-agent artifact review, local untracked `outputs/` artifacts.

---

## File Map

First commit, repair policy contract:

- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create: `docs/product/ppt-run2-data-skill-quality/visual_repair_policy.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json`

Second commit, generator/rerun/results:

- Create: `scripts/generate_ppt_run2_6r_visual_repair_arms.mjs`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_6r_visual_repair_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_6r_visual_repair_result.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`

Generated artifacts remain untracked:

- `outputs/<thread-id>/presentations/ppt-run2-6r-prompt-only/`
- `outputs/<thread-id>/presentations/ppt-run2-6r-run1-5-skill/`
- `outputs/<thread-id>/presentations/ppt-run2-6r-full-vulca/`
- `outputs/<thread-id>/presentations/ppt-run2-6r-bad-aesthetic-memory/`
- `outputs/<thread-id>/presentations/run2-6r-four-arm-contact-sheet.png`
- `outputs/<thread-id>/presentations/run2-full-skill-series-horizontal.png`

---

### Task 1: Add Failing Visual Repair Policy Tests

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add expected Run 2.6R constants**

Add these constants near the existing Run 2.6 constants:

```python
EXPECTED_RUN2_6R_REPAIR_IDS = {
    "repair_editorial_typography_system",
    "repair_spacing_token_visibility",
    "repair_climax_editorial_spread",
    "repair_theme_differentiation_from_run2_5",
    "repair_mini_preview_fidelity",
}
EXPECTED_RUN2_6R_REPAIR_FIELDS = {
    "id",
    "target_slide_roles",
    "source_policy_ids",
    "typography_delta",
    "spacing_delta",
    "composition_delta",
    "theme_delta",
    "must_differ_from",
    "native_ppt_requirements",
    "qa_probe",
    "release_boundary",
}
EXPECTED_RUN2_6R_TRACE_FIELDS = {
    "visual_repair_policy_ids",
    "visual_delta_from_run2_5",
    "visual_repair_validation_probe",
}
```

- [ ] **Step 2: Add failing policy test**

Append this test after `test_run2_6_has_workflow_decision_policy_and_trace_contract`:

```python
def test_run2_6r_has_visual_repair_policy() -> None:
    policy = load_json(PACK / "visual_repair_policy.json")
    workflow_policy = load_json(PACK / "workflow_decision_policy.json")
    workflow_policy_ids = {
        mapping["theme_policy_id"] for mapping in workflow_policy["usecase_benchmark_map"]
    } | {
        mapping["typography_system_id"] for mapping in workflow_policy["usecase_benchmark_map"]
    } | {
        mapping["spacing_token_set_id"] for mapping in workflow_policy["usecase_benchmark_map"]
    }

    assert policy["status"] == "run2_6r_visual_repair_policy_public_blocked"
    assert policy["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert policy["default_visual_direction"] == "light_first_editorial_graphite_with_vivid_proof_color"
    assert EXPECTED_RUN2_6R_REPAIR_IDS <= {repair["id"] for repair in policy["repairs"]}

    for repair in policy["repairs"]:
        assert EXPECTED_RUN2_6R_REPAIR_FIELDS <= set(repair), repair["id"]
        assert repair["target_slide_roles"]
        assert set(repair["target_slide_roles"]) <= {"cover", "setup", "contrast", "proof", "climax", "close"}
        assert set(repair["source_policy_ids"]) <= workflow_policy_ids | {"workflow_decision_policy.json"}
        assert_contains(repair["typography_delta"], ["Run 2.5"])
        assert_contains(repair["spacing_delta"], ["Run 2.5"])
        assert_contains(repair["composition_delta"], ["native"])
        assert_contains(repair["theme_delta"], ["forest-green", "source-brand"])
        assert "ppt-run2-5-full-vulca" in repair["must_differ_from"]
        assert "ppt-run2-6-full-vulca" in repair["must_differ_from"]
        assert_contains(" ".join(repair["native_ppt_requirements"]), ["native", "editable"])
        assert_contains(repair["qa_probe"], ["contact sheet"])
        assert_contains(repair["release_boundary"], ["public_blocked"])
```

- [ ] **Step 3: Run test and verify failure**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_6r_has_visual_repair_policy -q
```

Expected: fail because `visual_repair_policy.json` does not exist.

---

### Task 2: Add Visual Repair Policy, Workflow Stage, And Trace Contract

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/visual_repair_policy.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Create `visual_repair_policy.json`**

Create:

```json
{
  "schema_version": 1,
  "status": "run2_6r_visual_repair_policy_public_blocked",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "default_visual_direction": "light_first_editorial_graphite_with_vivid_proof_color",
  "repairs": [
    {
      "id": "repair_editorial_typography_system",
      "target_slide_roles": ["cover", "setup", "contrast", "proof", "climax", "close"],
      "source_policy_ids": ["type_system_editorial_product_sans", "workflow_decision_policy.json"],
      "typography_delta": "Replace the inherited Run 2.5 title/body scale with stronger editorial contrast, shorter subtitles, and marginal trace notes.",
      "spacing_delta": "Use Run 2.5 as the negative baseline: remove repeated same-position headings and give each slide role a distinct focal/support/provenance zone.",
      "composition_delta": "Keep all major text and proof objects native editable PPT shapes while reducing report-like label density.",
      "theme_delta": "Pair graphite text with light editorial canvas and one vivid proof color; avoid forest-green and source-brand color mimicry.",
      "must_differ_from": ["ppt-run2-5-full-vulca", "ppt-run2-6-full-vulca"],
      "native_ppt_requirements": ["native editable text hierarchy", "native shape labels", "no full-slide rasterized text"],
      "qa_probe": "In the contact sheet, headline hierarchy must be visibly different from Run 2.5 before zooming.",
      "release_boundary": "public_blocked_until_native_render_human_approval_and_visual_delta_review"
    },
    {
      "id": "repair_spacing_token_visibility",
      "target_slide_roles": ["setup", "contrast", "proof", "climax"],
      "source_policy_ids": ["spacing_tokens_precision_grid_12", "workflow_decision_policy.json"],
      "typography_delta": "Use smaller support labels than Run 2.5 and move implementation detail into side rails or trace strips.",
      "spacing_delta": "Make spacing tokens visible: large outer editorial margins, wider gutters around focal proof objects, and tighter internal mini-preview spacing.",
      "composition_delta": "Use native focal/support/provenance zones instead of repeated Run 2.5 panel placement.",
      "theme_delta": "Let whitespace carry the premium feel; do not use dark forest-green panels or source-brand color mimicry as the primary visual rhythm.",
      "must_differ_from": ["ppt-run2-5-full-vulca", "ppt-run2-6-full-vulca"],
      "native_ppt_requirements": ["native grouped zones", "editable gutters and proof rails", "layout geometry checks remain zero"],
      "qa_probe": "The contact sheet should show distinct slide-role spacing rhythms rather than repeated templates.",
      "release_boundary": "public_blocked_until_native_render_human_approval_and_visual_delta_review"
    },
    {
      "id": "repair_climax_editorial_spread",
      "target_slide_roles": ["climax"],
      "source_policy_ids": ["theme_original_high_contrast_product_system", "spacing_tokens_precision_grid_12", "workflow_decision_policy.json"],
      "typography_delta": "Give the climax the largest and shortest headline, with secondary detail pushed into a small proof strip.",
      "spacing_delta": "Allocate the largest visual field to one native editorial proof spread, not to repeated Run 2.5 hero-object blocks.",
      "composition_delta": "Rebuild slide 05 as a before/after or workflow-to-output editorial spread using native PPT shapes; do not reuse the Run 2.5/2.6 dark hero-object layout.",
      "theme_delta": "Use light canvas plus graphite and vivid proof color; avoid the inherited forest-green climax and source-brand mimicry.",
      "must_differ_from": ["ppt-run2-5-full-vulca", "ppt-run2-6-full-vulca"],
      "native_ppt_requirements": ["native before/after spread", "editable proof object", "secondary details in native side rail"],
      "qa_probe": "Slide 05 must be the most visibly changed full-arm slide in the full-skill-series image.",
      "release_boundary": "public_blocked_until_native_render_human_approval_and_visual_delta_review"
    },
    {
      "id": "repair_theme_differentiation_from_run2_5",
      "target_slide_roles": ["cover", "setup", "contrast", "proof", "climax", "close"],
      "source_policy_ids": ["theme_original_high_contrast_product_system", "workflow_decision_policy.json"],
      "typography_delta": "Use editorial type contrast to carry theme change instead of relying on dark slide backgrounds.",
      "spacing_delta": "Use whitespace and graphite rails as the main system, not Run 2.5 dark/light alternation.",
      "composition_delta": "Build a light-first product editorial surface with native material panels for mini-previews and proof objects.",
      "theme_delta": "Replace Run 2.5 forest-green/off-white dominance with light editorial canvas, graphite structure, cool material surfaces, and one vivid proof color; forbid source-brand mimicry.",
      "must_differ_from": ["ppt-run2-5-full-vulca", "ppt-run2-6-full-vulca"],
      "native_ppt_requirements": ["native theme-color shapes", "native editable material panels", "no copied source visual identity"],
      "qa_probe": "The full-skill-series image must show Run 2.6R as a different visual system after Run 2.6.",
      "release_boundary": "public_blocked_until_native_render_human_approval_and_visual_delta_review"
    },
    {
      "id": "repair_mini_preview_fidelity",
      "target_slide_roles": ["setup", "proof", "close"],
      "source_policy_ids": ["benchmark_visual_fidelity_interactive_slide_surface", "workflow_decision_policy.json"],
      "typography_delta": "Use preview labels as small native captions, not explanatory paragraphs.",
      "spacing_delta": "Use tight internal preview spacing and generous external whitespace to make previews feel intentional.",
      "composition_delta": "Replace placeholder screens with editable native slide-surface modules that show selected states, proof routes, and handoff gates.",
      "theme_delta": "Use cool material preview surfaces without reverting to forest-green rhythm or copying Figma, Apple, Google, Stripe, Duarte, SlideModel, or other source-brand identity.",
      "must_differ_from": ["ppt-run2-5-full-vulca", "ppt-run2-6-full-vulca"],
      "native_ppt_requirements": ["native mini-preview frames", "editable selected-state indicators", "no screenshots"],
      "qa_probe": "Mini-previews should read as product surfaces in the contact sheet, not placeholder rectangles.",
      "release_boundary": "public_blocked_until_native_render_human_approval_and_visual_delta_review"
    }
  ]
}
```

- [ ] **Step 2: Add workflow/trace failing test**

Append:

```python
def test_run2_6r_workflow_and_trace_contract_include_visual_repair() -> None:
    workflow = load_json(PACK / "skill_workflow.json")
    trace_contract = load_json(PACK / "results" / "trace_manifest_contract.json")

    workflow_stage_ids = {stage["id"] for stage in workflow["stages"]}
    assert "select_visual_repair_policy" in workflow_stage_ids
    workflow_text = json.dumps(workflow)
    assert_contains(workflow_text, ["visual_repair_policy.json", "visual repair", "not Run 3.0"])
    assert EXPECTED_RUN2_6R_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])
```

- [ ] **Step 3: Update `skill_workflow.json`**

Insert this stage after `select_theme_typography_spacing_policy` and before `select_visual_production_modules`:

```json
{
  "id": "select_visual_repair_policy",
  "order": 11,
  "layer": "skill_workflow",
  "inputs": [
    "visual_repair_policy.json",
    "commercial_usecase_id",
    "aesthetic_benchmark_ids",
    "theme_policy_id",
    "typography_system_id",
    "spacing_token_set_id"
  ],
  "outputs": ["visual_repair_policy_ids", "visual_delta_from_run2_5", "visual_repair_validation_probe"],
  "gates": [
    "Run 2.6R visual repair remains public blocked until review",
    "visual repair remains same-stage and not Run 3.0",
    "selected repair ids must differ from Run 2.5 and Run 2.6",
    "repair policy must preserve native editable PPT output"
  ]
}
```

Increment all later stage `order` values by 1 so the orders remain strictly increasing. Update `generate_code_first_ppt` inputs to include:

```json
"selected visual repair policy ids",
"visual delta from Run 2.5",
"visual repair validation probe"
```

Update `run_structural_and_aesthetic_qa` gates to include:

```json
"visual repair validation checks whether Run 2.6R differs visibly from Run 2.5 and Run 2.6"
```

- [ ] **Step 4: Update trace contract**

Append to `per_slide_required_fields`:

```json
"visual_repair_policy_ids",
"visual_delta_from_run2_5",
"visual_repair_validation_probe"
```

- [ ] **Step 5: Update workflow order test**

In `test_run2_skill_workflow_is_declarative_and_gated`, insert `"select_visual_repair_policy"` after `"select_theme_typography_spacing_policy"` and change the expected orders to:

```python
assert [stage["order"] for stage in workflow["stages"]] == list(range(1, 18))
```

Add:

```python
assert "visual_repair_policy.json" in workflow_text
assert_contains(workflow_text, ["visual repair", "Run 2.6R"])
```

- [ ] **Step 6: Run data/workflow tests**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_6r_has_visual_repair_policy tests/test_ppt_run2_data_skill_quality.py::test_run2_6r_workflow_and_trace_contract_include_visual_repair tests/test_ppt_run2_data_skill_quality.py::test_run2_skill_workflow_is_declarative_and_gated -q
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
ruff check tests/test_ppt_run2_data_skill_quality.py
```

Expected: tests pass, case pack ok, ruff ok.

- [ ] **Step 7: Commit repair policy contract**

Run:

```bash
git add tests/test_ppt_run2_data_skill_quality.py docs/product/ppt-run2-data-skill-quality/visual_repair_policy.json docs/product/ppt-run2-data-skill-quality/skill_workflow.json docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json
git commit -m "docs: add PPT run 2.6R visual repair policy"
```

---

### Task 3: Add Run 2.6R Generator Contract Tests

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create later: `scripts/generate_ppt_run2_6r_visual_repair_arms.mjs`

- [ ] **Step 1: Add failing generator boundary test**

Append after the Run 2.6 generator test:

```python
def test_run2_6r_generator_consumes_visual_repair_policy_and_preserves_boundaries() -> None:
    body = (ROOT / "scripts" / "generate_ppt_run2_6r_visual_repair_arms.mjs").read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_6r_visual_repair_full_skill", "bad_aesthetic_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else body.index("function sequenceStepsForSlide", start)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    assert_contains(
        body,
        [
            "run2_6r_visual_repair_full_skill",
            "visual_repair_policy.json",
            "visual_repair_policy_ids",
            "visual_delta_from_run2_5",
            "visual_repair_validation_probe",
            "renderFullRepair",
            "drawEditorialClimaxSpread",
            "no_cross_arm_reuse",
        ],
    )
    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_6r_visual_repair_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_6r_visual_repair_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_aesthetic_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_aesthetic_memory"), "forbidden:", "palette:")

    assert "visual_repair_policy.json" not in prompt_allowed
    assert "visual_repair_policy.json" in prompt_forbidden
    assert "visual_repair_policy.json" not in run1_allowed
    assert "visual_repair_policy.json" in run1_forbidden
    assert "visual_repair_policy.json" in full_allowed
    assert "visual_repair_policy.json" not in full_forbidden
    assert "commercial_usecase_bank.json" in bad_allowed
    assert "visual_repair_policy.json" not in bad_allowed
    assert "visual_repair_policy.json" in bad_forbidden
    assert 'const repairEligible = arm.armId === "run2_6r_visual_repair_full_skill";' in body
    assert re.search(r"visual_repair_policy_ids:\s*repairEligible\s*\\?", body)
    assert re.search(r"visual_delta_from_run2_5:\s*repairEligible\s*\\?", body)
    assert re.search(r"visual_repair_validation_probe:\s*repairEligible\s*\\?", body)
```

- [ ] **Step 2: Run test and verify failure**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_6r_generator_consumes_visual_repair_policy_and_preserves_boundaries -q
```

Expected: fail because the Run 2.6R generator does not exist.

---

### Task 4: Implement Run 2.6R Generator With New Full-Arm Visual System

**Files:**
- Create: `scripts/generate_ppt_run2_6r_visual_repair_arms.mjs`

- [ ] **Step 1: Create generator from Run 2.6**

Copy:

```bash
cp scripts/generate_ppt_run2_6_arms.mjs scripts/generate_ppt_run2_6r_visual_repair_arms.mjs
```

Apply these required replacements:

```bash
perl -0pi -e 's/run2_6_full_skill/run2_6r_visual_repair_full_skill/g; s/ppt-run2-6-/ppt-run2-6r-/g; s/RUN 2\\.6/RUN 2.6R/g; s/Run 2\\.6/Run 2.6R/g; s/generate_ppt_run2_6_arms\\.mjs/generate_ppt_run2_6r_visual_repair_arms.mjs/g' scripts/generate_ppt_run2_6r_visual_repair_arms.mjs
```

- [ ] **Step 2: Add repair policy role maps**

Add near the existing workflow maps:

```js
const repairPolicyByRole = {
  cover: ["repair_editorial_typography_system", "repair_theme_differentiation_from_run2_5"],
  setup: ["repair_spacing_token_visibility", "repair_mini_preview_fidelity"],
  contrast: ["repair_spacing_token_visibility", "repair_mini_preview_fidelity"],
  proof: ["repair_spacing_token_visibility", "repair_mini_preview_fidelity"],
  climax: ["repair_climax_editorial_spread", "repair_theme_differentiation_from_run2_5"],
  close: ["repair_editorial_typography_system", "repair_mini_preview_fidelity"],
};
const visualDeltaByRole = {
  cover: "light-first editorial opening replaces Run 2.5 dark cover",
  setup: "workflow selection becomes compact selected-state decision surface",
  contrast: "before-after spread receives larger editorial proof field",
  proof: "data-to-benchmark-to-policy route replaces equal cards",
  climax: "rebuilt editorial climax spread replaces Run 2.5 dark hero object",
  close: "product handoff surface replaces dark report-like close",
};
```

- [ ] **Step 3: Add repair policy input boundaries**

In `prompt_only.forbidden` and `run1_5_skill.forbidden`, add:

```js
"visual_repair_policy.json",
```

In full arm `allowed`, add:

```js
`${pack}/visual_repair_policy.json`,
```

In bad-memory `forbidden`, add:

```js
`${pack}/visual_repair_policy.json`,
```

Keep `bad_aesthetic_memory.allowed` with `commercial_usecase_bank.json`, and keep it forbidden from `aesthetic_benchmark_bank.json`, `workflow_decision_policy.json`, and `visual_repair_policy.json`.

- [ ] **Step 4: Replace full-arm render entrypoint**

Change `renderSlide` so the full arm uses `renderFullRepair`:

```js
function renderSlide(presentation, spec, arm, n) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  if (arm.armId === "run2_6r_visual_repair_full_skill") {
    renderFullRepair(slide, spec, arm, n);
  } else {
    renderControl(slide, spec, arm);
  }
  proofFooter(slide, spec, arm);
  return slide;
}
```

- [ ] **Step 5: Add repaired full-arm drawing functions**

Add these functions above `renderSlide`. They must use native shapes/text only:

```js
function editorialRule(slide, x, y, w, arm) {
  rect(slide, x, y, w, 2, arm.palette.accent);
  rect(slide, x, y + 8, Math.max(54, w * 0.22), 5, arm.palette.proof);
}

function selectedState(slide, label, value, x, y, w, arm) {
  rect(slide, x, y, w, 58, C.white, colorLine("#cfd6dd", 1));
  rect(slide, x, y, 8, 58, arm.palette.proof);
  text(slide, label, x + 18, y + 10, w - 32, 15, { fontSize: 8, bold: true, mono: true, color: arm.palette.accent });
  text(slide, value, x + 18, y + 28, w - 32, 22, { fontSize: 13, bold: true, title: true, color: arm.palette.title });
}

function materialPreview(slide, x, y, w, h, arm, label) {
  rect(slide, x, y, w, h, "#edf4f6", colorLine("#b9cbd1", 1));
  rect(slide, x + 22, y + 22, w - 44, 9, arm.palette.proof);
  rect(slide, x + 28, y + 68, w * 0.42, h * 0.42, C.white, colorLine("#cfd6dd", 1));
  rect(slide, x + 48, y + 92, w * 0.20, h * 0.18, arm.palette.proof);
  rect(slide, x + w * 0.56, y + 82, w * 0.28, 12, arm.palette.accent);
  rect(slide, x + w * 0.56, y + 118, w * 0.32, 8, "#b9c4c8");
  rect(slide, x + w * 0.56, y + 148, w * 0.22, 8, "#b9c4c8");
  text(slide, label, x + 28, y + h - 42, w - 56, 24, { fontSize: 14, bold: true, title: true, color: arm.palette.title });
}

function drawEditorialClimaxSpread(slide, arm) {
  rect(slide, 54, 88, 1170, 542, arm.palette.bg, colorLine("#d8dde1", 1));
  text(slide, "The workflow becomes visible.", 84, 118, 620, 68, {
    fontSize: 46,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  text(slide, "Run 2.6R turns usecase, benchmark, typography, spacing, and repair policy into one native proof spread.", 88, 198, 540, 58, {
    fontSize: 15,
    color: arm.palette.muted,
  });
  rect(slide, 82, 308, 330, 190, "#eef1f4", colorLine("#cfd6dd", 1));
  text(slide, "before / inherited", 108, 332, 190, 18, { fontSize: 9, bold: true, mono: true, color: arm.palette.muted });
  for (let i = 0; i < 4; i += 1) rect(slide, 110 + i * 68, 378, 46, 36, "#dfe4e8", colorLine("#cfd6dd", 1));
  rect(slide, 456, 278, 540, 256, C.white, colorLine(arm.palette.proof, 3));
  text(slide, "after / repaired native PPT", 492, 306, 260, 18, { fontSize: 9, bold: true, mono: true, color: arm.palette.proof });
  rect(slide, 502, 354, 230, 128, arm.palette.proof);
  rect(slide, 760, 354, 156, 16, arm.palette.accent);
  rect(slide, 760, 400, 190, 9, "#c6d0d5");
  rect(slide, 760, 434, 132, 9, "#c6d0d5");
  rect(slide, 1032, 300, 122, 210, "#172026", colorLine("#172026", 1));
  text(slide, "repair ids", 1050, 324, 88, 16, { fontSize: 8, bold: true, mono: true, color: "#d7eff2" });
  text(slide, "type / spacing / climax / theme", 1050, 356, 82, 92, { fontSize: 12, color: C.white });
  editorialRule(slide, 88, 548, 858, arm);
}

function renderFullRepair(slide, spec, arm, n) {
  if (spec.role === "cover") {
    rect(slide, 0, 0, W, H, arm.palette.bg);
    text(slide, "Vulca", 72, 94, 300, 56, { fontSize: 30, bold: true, title: true, color: arm.palette.accent });
    text(slide, "The data now changes the picture.", 72, 164, 720, 140, { fontSize: 58, bold: true, title: true, color: arm.palette.title });
    text(slide, "Run 2.6R repairs typography, spacing, climax composition, and theme so workflow policy becomes visible.", 76, 326, 570, 62, { fontSize: 17, color: arm.palette.muted });
    materialPreview(slide, 760, 126, 360, 330, arm, "native repaired proof surface");
    selectedState(slide, "usecase", "design-to-production launch", 76, 470, 250, arm);
    selectedState(slide, "benchmark", "visual fidelity + grid precision", 350, 470, 294, arm);
    editorialRule(slide, 76, 576, 606, arm);
    return;
  }
  simpleTitle(slide, spec, arm, true);
  if (spec.role === "setup") {
    selectedState(slide, "selected usecase", "design-to-production platform launch", 82, 292, 300, arm);
    selectedState(slide, "selected benchmark", "grid precision + visual fidelity", 82, 372, 300, arm);
    selectedState(slide, "selected policy", "light editorial graphite system", 82, 452, 300, arm);
    materialPreview(slide, 520, 278, 440, 260, arm, "policy-selected native slide surface");
  } else if (spec.role === "contrast") {
    rect(slide, 82, 292, 430, 244, "#eef1f4", colorLine("#cfd6dd", 1));
    rect(slide, 588, 260, 500, 310, C.white, colorLine(arm.palette.proof, 3));
    text(slide, "before: inherited full arm", 110, 320, 230, 18, { fontSize: 9, bold: true, mono: true, color: arm.palette.muted });
    text(slide, "after: repaired composition", 626, 294, 260, 18, { fontSize: 9, bold: true, mono: true, color: arm.palette.proof });
    materialPreview(slide, 636, 340, 310, 160, arm, "native after-state preview");
    rect(slide, 520, 398, 48, 10, arm.palette.proof);
    rect(slide, 558, 378, 20, 50, arm.palette.proof);
  } else if (spec.role === "proof") {
    const route = [
      ["usecase", "commercial job"],
      ["benchmark", "visual rules"],
      ["policy", "type + spacing"],
      ["module", "native output"],
    ];
    route.forEach((item, index) => {
      const x = 90 + index * 260;
      selectedState(slide, item[0], item[1], x, 316 + (index % 2) * 82, 214, arm);
      if (index < route.length - 1) rect(slide, x + 226, 346 + (index % 2) * 82, 36, 4, arm.palette.proof);
    });
    editorialRule(slide, 92, 566, 830, arm);
  } else if (spec.role === "climax") {
    drawEditorialClimaxSpread(slide, arm);
  } else {
    materialPreview(slide, 90, 292, 360, 250, arm, "editable handoff surface");
    selectedState(slide, "gate", "native render pending", 520, 318, 260, arm);
    selectedState(slide, "approval", "human review pending", 520, 398, 260, arm);
    selectedState(slide, "release", "public blocked", 520, 478, 260, arm);
    rect(slide, 850, 314, 240, 162, "#172026", colorLine("#172026", 1));
    text(slide, "not public-ready", 878, 346, 184, 34, { fontSize: 23, bold: true, title: true, color: C.white });
    text(slide, "visual repair proof only", 878, 404, 170, 38, { fontSize: 13, color: "#d7eff2" });
  }
}
```

- [ ] **Step 6: Change full arm palette**

Set the full arm palette to a light-first editorial system:

```js
palette: {
  bg: "#f7f4ee",
  rail: "#1a2228",
  rule: "#d8dde1",
  accent: "#27343c",
  accent2: "#93a7ad",
  proof: "#e24b2f",
  panel: "#ffffff",
  title: "#11171c",
  muted: "#5f6d75",
},
```

Keep control palettes unchanged.

- [ ] **Step 7: Add trace repair fields**

Inside `traceFor`, add:

```js
const repairEligible = arm.armId === "run2_6r_visual_repair_full_skill";
```

Each slide trace must include:

```js
visual_repair_policy_ids: repairEligible ? repairPolicyByRole[slide.role] ?? [] : [],
visual_delta_from_run2_5: repairEligible ? visualDeltaByRole[slide.role] ?? "Run 2.6R visual repair delta recorded" : "not applicable; repair policy forbidden for this arm",
visual_repair_validation_probe: repairEligible
  ? "contact sheet and full-skill-series must show visible difference from Run 2.5 and Run 2.6"
  : "control arm must not claim Run 2.6R visual repair",
```

Update `runtime_isolation.prompt_context` to say:

```js
fresh Run 2.6R visual-repair arm-specific generation from scripts/generate_ppt_run2_6r_visual_repair_arms.mjs
```

- [ ] **Step 8: Verify syntax and generator contract**

Run:

```bash
/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --check scripts/generate_ppt_run2_6r_visual_repair_arms.mjs
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_6r_generator_consumes_visual_repair_policy_and_preserves_boundaries -q
```

Expected: both pass.

---

### Task 5: Run 2.6R Four Arms And QA

**Files:**
- Generated only under `outputs/`

- [ ] **Step 1: Run generator**

Run:

```bash
/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/generate_ppt_run2_6r_visual_repair_arms.mjs
```

Expected: creates four directories under `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/`:

- `ppt-run2-6r-prompt-only`
- `ppt-run2-6r-run1-5-skill`
- `ppt-run2-6r-full-vulca`
- `ppt-run2-6r-bad-aesthetic-memory`

- [ ] **Step 2: Build per-arm contact sheets**

Run:

```bash
for slug_title in \
  "ppt-run2-6r-prompt-only|Run 2.6R prompt-only control" \
  "ppt-run2-6r-run1-5-skill|Run 2.6R run1.5 baseline" \
  "ppt-run2-6r-full-vulca|Run 2.6R visual repair full skill" \
  "ppt-run2-6r-bad-aesthetic-memory|Run 2.6R bad aesthetic memory"; do
  slug=${slug_title%%|*}
  title=${slug_title#*|}
  python3 scripts/build_ppt_contact_sheet.py \
    --out "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/preview/contact-sheet.png" \
    --title "$title" \
    outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/preview/slide-01.png \
    outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/preview/slide-02.png \
    outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/preview/slide-03.png \
    outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/preview/slide-04.png \
    outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/preview/slide-05.png \
    outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/preview/slide-06.png
done
```

Expected: four `preview/contact-sheet.png` files are created.

- [ ] **Step 3: Run layout QA**

Run:

```bash
for slug in ppt-run2-6r-prompt-only ppt-run2-6r-run1-5-skill ppt-run2-6r-full-vulca ppt-run2-6r-bad-aesthetic-memory; do
  python3 scripts/check_ppt_layout_quality.py \
    --layout-dir "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/layout/final" \
    --out "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/qa/layout_quality_report.txt"
done
```

Expected: each arm reports:

```json
{
  "layout_files": 6,
  "layout_errors": 0,
  "layout_warnings": 0
}
```

- [ ] **Step 4: Run delivery QA**

Run:

```bash
for slug in ppt-run2-6r-prompt-only ppt-run2-6r-run1-5-skill ppt-run2-6r-full-vulca ppt-run2-6r-bad-aesthetic-memory; do
  python3 scripts/validate_pptx_delivery.py \
    --pptx "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/output/${slug}.pptx" \
    --layout-dir "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/layout/final" \
    --contact-sheet "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/preview/contact-sheet.png" \
    --label "${slug}" \
    --out "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/qa/delivery_report.md"
done
```

Expected: each arm prints `internal-demo-ok-public-blocked`.

- [ ] **Step 5: Refresh trace QA**

Run:

```bash
for slug in ppt-run2-6r-prompt-only ppt-run2-6r-run1-5-skill ppt-run2-6r-full-vulca ppt-run2-6r-bad-aesthetic-memory; do
  python3 scripts/refresh_ppt_trace_qa.py \
    --trace "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/trace_manifest.json" \
    --delivery-report "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/qa/delivery_report.md" \
    --layout-report "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/qa/layout_quality_report.txt" \
    --aesthetic-status "run2_6r_visual_delta_review_pending_gemini_and_human"
done
```

Expected: each summary reports `delivery_gate` as `internal-demo-ok-public-blocked`.

- [ ] **Step 6: Run native editability and arm isolation guards**

Run:

```bash
python3 - <<'PY'
import json
import zipfile
from pathlib import Path

root = Path("outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations")
expected_arms = {
    "ppt-run2-6r-prompt-only": "prompt_only",
    "ppt-run2-6r-run1-5-skill": "run1_5_skill",
    "ppt-run2-6r-full-vulca": "run2_6r_visual_repair_full_skill",
    "ppt-run2-6r-bad-aesthetic-memory": "bad_aesthetic_memory",
}
for slug, arm_id in expected_arms.items():
    trace = json.loads((root / slug / "trace_manifest.json").read_text(encoding="utf-8"))
    assert trace["arm_id"] == arm_id, (slug, trace["arm_id"])
    for slide in trace["slides"]:
        repairs = slide.get("visual_repair_policy_ids") or []
        if arm_id == "run2_6r_visual_repair_full_skill":
            assert repairs, (slug, slide.get("slide"))
        else:
            assert repairs == [], (slug, slide.get("slide"), repairs)

full_pptx = root / "ppt-run2-6r-full-vulca/output/ppt-run2-6r-full-vulca.pptx"
with zipfile.ZipFile(full_pptx) as archive:
    names = archive.namelist()
    media = [name for name in names if name.startswith("ppt/media/")]
    slide_xml = [
        archive.read(name).decode("utf-8", errors="ignore")
        for name in names
        if name.startswith("ppt/slides/slide") and name.endswith(".xml")
    ]
shape_count = sum(xml.count("<p:sp>") for xml in slide_xml)
picture_count = sum(xml.count("<p:pic>") for xml in slide_xml)
assert media == [], media
assert picture_count == 0, picture_count
assert shape_count >= 60, shape_count
print({"arm_isolation_guard": "passed", "run2_6r_full_media_entries": 0, "run2_6r_full_picture_shapes": 0, "shape_count": shape_count})
PY
```

Expected: prints a passed guard with zero media entries and zero picture shapes. This blocks flat-image fallbacks and arm-boundary leakage.

- [ ] **Step 7: Build two mandatory comparison images**

Run:

```bash
python3 scripts/build_ppt_full_skill_series_sheet.py \
  --title "Run 2.6R four-arm visual repair comparison" \
  --item-width 560 \
  --out outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-6r-four-arm-contact-sheet.png \
  --item "prompt-only=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-6r-prompt-only/preview/contact-sheet.png" \
  --item "run1.5=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-6r-run1-5-skill/preview/contact-sheet.png" \
  --item "run2.6R full=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-6r-full-vulca/preview/contact-sheet.png" \
  --item "bad memory=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-6r-bad-aesthetic-memory/preview/contact-sheet.png"

python3 scripts/build_ppt_full_skill_series_sheet.py \
  --title "Run 2.0-2.6R full-skill progression" \
  --item-width 470 \
  --out outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png \
  --item "Run 2.0=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.1=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-1-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.2=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-2-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.3=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-3-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.4=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-4-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.5=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-5-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.6=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-6-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.6R=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-6r-full-vulca/preview/contact-sheet.png"
```

Expected:

- `run2-6r-four-arm-contact-sheet.png` exists.
- `run2-full-skill-series-horizontal.png` includes Run 2.6R after Run 2.6.

- [ ] **Step 8: Run Gemini artifact review**

Call `mcp__gemini_agent.gemini_artifact_review` on:

```text
outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png
```

Expected: review artifact written under `.gemini-agent/artifacts/`; verdict may remain caution/public-blocked.

---

### Task 6: Record Run 2.6R Results

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_6r_visual_repair_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_6r_visual_repair_result.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`

- [ ] **Step 1: Add failing result test**

Append after `test_run2_6_records_data_workflow_rerun_result`:

```python
def test_run2_6r_records_visual_repair_rerun_result() -> None:
    result = (PACK / "results" / "run2_6r_visual_repair_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_6r_visual_repair_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_6r_visual_repair_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert result_json["rerun"]["best_internal_arm_verdict"] in {
        "visual_repair_visible_but_not_public_release_ready",
        "visual_repair_insufficient_same_stage_repeat_required",
    }
    assert result_json["next_required_action"] in {
        "native_render_and_human_review_then_continue_same_five_layers_if_needed",
        "repeat_same_stage_visual_repair_before_native_review",
    }
    assert_contains(
        json.dumps(result_json["visual_repair_learning"]),
        [
            "visual_repair_policy_ids",
            "visual_delta_from_run2_5",
            "visual_repair_validation_probe",
            "typography",
            "spacing",
            "climax",
            "theme",
        ],
    )
    assert result_json["qa_summary"]["arm_isolation_guard"] == "passed"
    assert result_json["qa_summary"]["run2_6r_full_media_entries"] == 0
    assert result_json["qa_summary"]["run2_6r_full_picture_shapes"] == 0
    assert result_json["qa_summary"]["run2_6r_full_native_shape_minimum_passed"] is True
    assert_contains(
        result,
        [
            "Run 2.6R",
            "visual_repair_policy.json",
            "run2_6r_visual_repair_full_skill",
            "full-skill-series",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )
```

- [ ] **Step 2: Create result JSON**

Create `run2_6r_visual_repair_result.json` with this shape. Fill the exact Gemini artifact path after review:

```json
{
  "schema_version": 1,
  "status": "rerun_completed_public_blocked",
  "public_ready": false,
  "stage_policy": "repeat_same_five_layers_not_run3",
  "rerun": {
    "status": "completed",
    "generated_outputs_committed": false,
    "combined_contact_sheet": "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-6r-four-arm-contact-sheet.png",
    "full_skill_series_sheet": "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png",
    "delivery_gate": "internal-demo-ok-public-blocked",
    "best_internal_arm": "run2_6r_visual_repair_full_skill",
    "best_internal_arm_verdict": "visual_repair_visible_but_not_public_release_ready"
  },
  "visual_repair_learning": {
    "visual_repair_policy_ids": "present_for_run2_6r_visual_repair_full_skill_only",
    "visual_delta_from_run2_5": "recorded_per_slide_for_full_arm",
    "visual_repair_validation_probe": "recorded_per_slide_for_full_arm",
    "typography": "editorial_type_scale_changed_from_run2_5",
    "spacing": "focal_support_trace_zones_changed_from_run2_5",
    "climax": "slide_05_recomposed_as_editorial_proof_spread",
    "theme": "light_first_graphite_proof_color_replaces_forest_green_dominance",
    "control_boundary": "prompt_only_run1_5_and_bad_memory_forbid_visual_repair_policy",
    "visual_quality_boundary": "still_internal_demo_grade_until_native_render_and_human_review"
  },
  "qa_summary": {
    "prompt_only_layout_errors": 0,
    "prompt_only_layout_warnings": 0,
    "run1_5_layout_errors": 0,
    "run1_5_layout_warnings": 0,
    "run2_6r_full_layout_errors": 0,
    "run2_6r_full_layout_warnings": 0,
    "bad_aesthetic_memory_layout_errors": 0,
    "bad_aesthetic_memory_layout_warnings": 0,
    "arm_isolation_guard": "passed",
    "run2_6r_full_media_entries": 0,
    "run2_6r_full_picture_shapes": 0,
    "run2_6r_full_native_shape_minimum_passed": true,
    "generated_outputs_committed": false,
    "gemini_contact_sheet_reviews": [
      ".gemini-agent/artifacts/<timestamp>-artifacts.json"
    ]
  },
  "next_required_action": "native_render_and_human_review_then_continue_same_five_layers_if_needed",
  "release_gate": "public_blocked_until_native_render_human_approval_source_brand_sanitization_and_public_demo_visual_pass"
}
```

- [ ] **Step 3: Create result Markdown**

Create `run2_6r_visual_repair_result.md` with:

```markdown
# Run 2.6R Visual Repair Result

Status: rerun_completed_public_blocked.

Run 2.6R reran the same four arms as a same-stage visual repair pass, not as Run 3.0:

- `prompt_only`
- `run1_5_skill`
- `run2_6r_visual_repair_full_skill`
- `bad_aesthetic_memory`

The purpose was to make Run 2.6 workflow data visible in the picture. Run 2.6 proved that `commercial_usecase_bank.json`, `aesthetic_benchmark_bank.json`, and `workflow_decision_policy.json` entered the trace. Run 2.6R adds `visual_repair_policy.json` so typography, spacing, climax composition, theme differentiation, and mini-preview fidelity are selected before code generation.

The full arm records `visual_repair_policy_ids`, `visual_delta_from_run2_5`, and `visual_repair_validation_probe` in trace. The controls preserve their boundaries: prompt-only and Run 1.5 forbid Run 2.6R policy, while bad aesthetic memory receives the commercial usecase but not the good visual repair policy.

Two mandatory images were generated locally:

- Four-arm sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-6r-four-arm-contact-sheet.png`
- Full-skill series sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Public publishing remains blocked. Native render inspection, source-brand sanitization review, and human approval have not passed.

## Decision

Run 2.6R is an internal visual repair result only. Do not advance to Run 3.0.
```

- [ ] **Step 4: Update result indexes**

Update `results/README.md`, `comparison_report.md`, and `delivery_gate.md` so Run 2.6R is the latest internal result.

Required phrases:

- `Run 2.6R`
- `visual_repair_policy.json`
- `run2_6r_visual_repair_full_skill`
- `run2-6r-four-arm-contact-sheet`
- `run2-full-skill-series-horizontal`
- `public blocked`
- `same-stage visual repair`

- [ ] **Step 5: Final verification**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py tests/test_ppt_case_pack_validator.py tests/test_refresh_ppt_trace_qa.py tests/test_pptx_delivery_validator.py -q
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
ruff check tests/test_ppt_run2_data_skill_quality.py scripts/check_ppt_layout_quality.py scripts/refresh_ppt_trace_qa.py scripts/validate_pptx_delivery.py scripts/build_ppt_full_skill_series_sheet.py
/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --check scripts/generate_ppt_run2_6r_visual_repair_arms.mjs
git ls-files outputs | wc -l
```

Expected:

- pytest passes with only the existing config warning if present;
- case pack ok;
- ruff ok;
- node check ok;
- tracked `outputs` count is `0`.

- [ ] **Step 6: Gemini diff review**

Call `mcp__gemini_agent.gemini_diff_review` on the staged diff. Focus on:

- whether the generator really changes full-arm visual functions;
- whether control arms still forbid repair policy;
- whether source-brand sanitization and public-blocked language remain correct;
- whether result docs overclaim visual quality.

- [ ] **Step 7: Commit visual repair rerun**

Run:

```bash
git add scripts/generate_ppt_run2_6r_visual_repair_arms.mjs tests/test_ppt_run2_data_skill_quality.py docs/product/ppt-run2-data-skill-quality/results/run2_6r_visual_repair_result.json docs/product/ppt-run2-data-skill-quality/results/run2_6r_visual_repair_result.md docs/product/ppt-run2-data-skill-quality/results/README.md docs/product/ppt-run2-data-skill-quality/results/comparison_report.md docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md
git commit -m "docs: record PPT run 2.6R visual repair"
```

---

## Self-Review Checklist

- Run 2.6R stays inside the same five-layer loop and does not advance to Run 3.0.
- `visual_repair_policy.json` is tested before generator changes.
- Prompt-only and Run 1.5 forbid `visual_repair_policy.json`.
- Bad aesthetic memory forbids `visual_repair_policy.json`.
- Full arm receives and traces repair policy.
- Full arm drawing functions are changed, not only renamed.
- Two images are generated every time: four-arm and full-skill-series.
- Results remain public blocked.
- Generated outputs remain untracked.
