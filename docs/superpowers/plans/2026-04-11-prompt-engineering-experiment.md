# Prompt Engineering Experiment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the `scripts/generate-e2e-demo.py` changes described in `docs/superpowers/specs/2026-04-11-prompt-engineering-experiment-design.md`, then execute Stage 1 (5 images: gongbi × 3 seeds + xieyi + japanese), hand-score against the rubric, apply the Decision Tree, and report a go/no-go signal for the GuoFeng checkpoint experiment.

**Architecture:** Single-file edit to `scripts/generate-e2e-demo.py`. Add three CLI flags (`--traditions`, `--gallery-subdir`, `--seeds-per-tradition`), evolve `TRADITION_PROMPTS` schema from `list[tuple]` to `list[dict]`, wire `negative_prompt` through to the provider, add an `EXPERIMENTAL_PROMPT_OVERRIDES` map with startup validation, wire override resolution into the generation loop (including `suppress_tradition_suffix` handling). No provider changes. No automated tests (disposable scaffolding per spec).

**Tech Stack:** Python 3.11, argparse, asyncio, pathlib. ComfyUI + SDXL base 1.0 as the image backend. No new dependencies.

**Spec reference:** `docs/superpowers/specs/2026-04-11-prompt-engineering-experiment-design.md` (422 lines).

**Worktree note:** Not using a worktree. Scope is a single script file with no library impact. Brainstorming did not create a worktree for this spike.

**Pre-flight state at plan write time:**
- Commit SHA: `cc3bb63bd86aefee5ad3b0bc911cd6f22ac395b4` (approximate — check `git rev-parse HEAD` before starting)
- `sd_xl_base_1.0.safetensors` SHA-256: `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b` (pinned)
- ComfyUI: not running — start before Task 8
- `assets/demo/v3/gallery/` baseline: 13 PNGs present, to be preserved

---

## File Structure

**Files touched in this plan (one):**
- **Modify**: `scripts/generate-e2e-demo.py` — all code changes in Tasks 1-7
- **Create (artifacts, Task 8)**:
  - `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed1.png`
  - `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed2.png`
  - `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed3.png`
  - `assets/demo/v3/gallery-promptfix/chinese_xieyi.png`
  - `assets/demo/v3/gallery-promptfix/japanese_traditional.png`
  - `assets/demo/v3/e2e-report-gallery-promptfix.json`

**Files NOT touched (for reference, out of scope):**
- `src/vulca/providers/comfyui.py` — already supports `negative_prompt`
- Any test file — spec forbids new tests
- Any other asset or config

---

## Task Ordering Rationale

Tasks 1-7 are sequential because each depends on earlier changes (schema, then consumers, then flags that compose together). Each task ends with a committed, working script so a task-level rollback is always `git reset --hard HEAD~1`. Task 8 is the real-ComfyUI run, Task 9 is the rubric scoring, Task 10 is the optional Stage 2.

---

## Task 1: Evolve `TRADITION_PROMPTS` schema

**Files:**
- Modify: `scripts/generate-e2e-demo.py` (lines 51–65 for the constant; line 88 for the loop; line 293 for Phase 3 consumer)

**Goal:** Change `TRADITION_PROMPTS` from `list[tuple[str, str]]` to `list[dict]` with `{tradition, prompt, negative}` shape. Update all consumers. Default behavior stays identical.

- [ ] **Step 1: Read current state of the three touch points**

Run:
```bash
sed -n '51,65p;88,88p;293,293p' scripts/generate-e2e-demo.py
```

Expected output (verify before editing):
- Lines 51–65: the tuple list
- Line 88: `for idx, (tradition, prompt) in enumerate(TRADITION_PROMPTS, start=1):`
- Line 293: `prompt_by_tradition = dict(TRADITION_PROMPTS)`

- [ ] **Step 2: Replace the TRADITION_PROMPTS constant**

Replace lines 51–65 with:

```python
# Tradition → prompt mapping. Uses the 13 actual tradition YAML definitions
# present in src/vulca/cultural/data/traditions/. Prompts match the E2E spec
# where they overlap and are invented for the traditions the spec did not
# cover (contemporary_art, ui_ux_design).
#
# Each entry carries a positive ``prompt`` and an optional ``negative`` prompt
# (default empty). The experimental-override path (see
# EXPERIMENTAL_PROMPT_OVERRIDES below) can substitute either per tradition
# without mutating this list.
TRADITION_PROMPTS: list[dict] = [
    {"tradition": "chinese_xieyi",        "prompt": "水墨山水，雨后春山，松间茅屋",                                                "negative": ""},
    {"tradition": "chinese_gongbi",       "prompt": "工笔牡丹，细腻勾线，三矾九染",                                                "negative": ""},
    {"tradition": "japanese_traditional", "prompt": "京都金閣寺の雪景色、墨絵風",                                                  "negative": ""},
    {"tradition": "western_academic",     "prompt": "Impressionist garden at golden hour, oil on canvas",                        "negative": ""},
    {"tradition": "watercolor",           "prompt": "English countryside cottage, loose wet-on-wet watercolor",                  "negative": ""},
    {"tradition": "islamic_geometric",    "prompt": "Alhambra-inspired geometric pattern, turquoise and gold",                   "negative": ""},
    {"tradition": "african_traditional",  "prompt": "Ndebele mural pattern, bold primary colors",                                "negative": ""},
    {"tradition": "south_asian",          "prompt": "Mughal miniature, garden scene with lotus pond",                            "negative": ""},
    {"tradition": "brand_design",         "prompt": "Premium tea packaging, mountain watermark, Eastern aesthetics",             "negative": ""},
    {"tradition": "photography",          "prompt": "Misty mountain landscape at dawn, cinematic",                               "negative": ""},
    {"tradition": "contemporary_art",     "prompt": "Abstract expressionist canvas with bold gestural strokes",                  "negative": ""},
    {"tradition": "ui_ux_design",         "prompt": "Clean dashboard UI mockup with card layout and soft shadows",               "negative": ""},
    {"tradition": "default",              "prompt": "Serene landscape with mountains and water",                                 "negative": ""},
]
```

- [ ] **Step 3: Update the Phase 1 loop unpacking**

Find the line:
```python
for idx, (tradition, prompt) in enumerate(TRADITION_PROMPTS, start=1):
```

Replace with:
```python
for idx, entry in enumerate(TRADITION_PROMPTS, start=1):
    tradition = entry["tradition"]
    prompt = entry["prompt"]
```

- [ ] **Step 4: Update the Phase 3 consumer**

Find the line:
```python
prompt_by_tradition = dict(TRADITION_PROMPTS)
```

Replace with:
```python
prompt_by_tradition = {e["tradition"]: e["prompt"] for e in TRADITION_PROMPTS}
```

- [ ] **Step 5: Syntax check**

Run:
```bash
python -c "import ast; ast.parse(open('scripts/generate-e2e-demo.py').read()); print('ok')"
```

Expected: `ok`

- [ ] **Step 6: argparse smoke**

Run:
```bash
python scripts/generate-e2e-demo.py --help 2>&1 | head -20
```

Expected: standard `usage:` output, no traceback.

- [ ] **Step 7: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "refactor(e2e): evolve TRADITION_PROMPTS to dict shape

Prep for prompt engineering experiment — each tradition entry now
carries an optional 'negative' prompt (defaults to '' for the 13
existing entries). Phase 1 loop and Phase 3 consumer updated to the
new shape. No behavioral change: every entry has an empty negative,
which is the same as the prior behavior of passing no negative at all.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Plumb `negative_prompt` through `run_phase1_gallery`

**Files:**
- Modify: `scripts/generate-e2e-demo.py` (the `provider.generate` call inside `run_phase1_gallery`, ~line 101-106 post-Task-1)

**Goal:** Pass `entry["negative"]` to `provider.generate(..., negative_prompt=...)`. Since all existing entries have `negative=""`, default behavior is unchanged.

- [ ] **Step 1: Locate the generate call**

Run:
```bash
grep -n 'provider.generate' scripts/generate-e2e-demo.py
```

Expected: one match around line 101 in `run_phase1_gallery`.

- [ ] **Step 2: Add `negative_prompt` kwarg**

Find:
```python
            result = await provider.generate(
                prompt,
                tradition=tradition,
                width=width,
                height=height,
            )
```

Replace with:
```python
            result = await provider.generate(
                prompt,
                tradition=tradition,
                width=width,
                height=height,
                negative_prompt=entry.get("negative", ""),
            )
```

- [ ] **Step 3: Syntax check**

Run:
```bash
python -c "import ast; ast.parse(open('scripts/generate-e2e-demo.py').read()); print('ok')"
```

Expected: `ok`

- [ ] **Step 4: Verify provider accepts the kwarg**

Run:
```bash
grep -n 'negative_prompt' src/vulca/providers/comfyui.py
```

Expected: two matches — one on the `generate()` signature (`negative_prompt: str = "",`), one in the `CLIPTextEncode` node input.

- [ ] **Step 5: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "feat(e2e): pass negative_prompt through Phase 1 gallery loop

Runner now forwards each entry's 'negative' field to
provider.generate(). All 13 default entries have negative='', so
behavior is identical to pre-change; the wiring is prep for the
experimental override path introduced in a later commit.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Add `EXPERIMENTAL_PROMPT_OVERRIDES` constant + startup validation

**Files:**
- Modify: `scripts/generate-e2e-demo.py` (add constant after `TRADITION_PROMPTS`; add `_validate_overrides` function; call from `main()`)

**Goal:** Add the override map with the exact prompts from the spec. Fail fast at startup if any override key is not a valid `TRADITION_PROMPTS` tradition name (spec's superpowers-m5 fix).

- [ ] **Step 1: Add the override constant**

Insert immediately after the closing `]` of `TRADITION_PROMPTS` (before the `def _validate_png_bytes` function):

```python


# ---------------------------------------------------------------------------
# Experimental prompt overrides — see
# docs/superpowers/specs/2026-04-11-prompt-engineering-experiment-design.md
#
# Applied only when --traditions is passed AND the listed tradition is a
# key in this map. Each override replaces the positive prompt, sets a
# negative, and may suppress the provider's auto-appended
# `, {tradition} style` suffix by causing the runner to pass tradition=""
# to provider.generate(). The baseline TRADITION_PROMPTS list is not
# mutated; invocations without --traditions behave exactly as today.
# ---------------------------------------------------------------------------
EXPERIMENTAL_PROMPT_OVERRIDES: dict[str, dict] = {
    "chinese_gongbi": {
        "prompt": (
            "(single large peony flower:1.4), close-up centered botanical "
            "portrait, Chinese gongbi meticulous brush painting, fine ink "
            "outlines, mineral pigments, peony blossom with green leaves, "
            "blank silk background, Chinese court flower-and-bird painting, "
            "museum quality botanical study"
        ),
        "negative": (
            "landscape, scenery, mountain, mountains, distant mountains, "
            "temple, pagoda, building, architecture, pine tree, river, lake, "
            "clouds, misty background, cottage, loose brushstrokes, xieyi, "
            "abstract, photography, impressionist"
        ),
        "suppress_tradition_suffix": True,
    },
    "chinese_xieyi": {
        "prompt": (
            "traditional Chinese xieyi freehand ink painting, misty mountains "
            "after spring rain, pine trees by a thatched cottage, sumi-e style, "
            "monochrome ink on rice paper, expressive loose brushwork, "
            "abundant reserved white space"
        ),
        "negative": (
            "photorealistic, saturated colors, western oil painting, gongbi, "
            "tight line work, peony, botanical portrait"
        ),
        "suppress_tradition_suffix": True,
    },
    "japanese_traditional": {
        "prompt": (
            "(Kinkaku-ji Golden Pavilion:1.3), Kyoto, winter snow, "
            "sumi-e monochrome ink painting, traditional Japanese ink wash "
            "suiboku-ga, minimal brushwork, atmospheric, gold temple "
            "reflecting on pond"
        ),
        "negative": (
            "saturated color, ukiyo-e print, anime, photography, western "
            "painting, cherry blossoms, red bridge, generic pagoda, "
            "snow on trees"
        ),
        "suppress_tradition_suffix": True,
    },
}


def _validate_experimental_overrides() -> None:
    """Fail fast if any EXPERIMENTAL_PROMPT_OVERRIDES key is unknown.

    Guards against silent drift between the override map and
    TRADITION_PROMPTS (e.g., a tradition renamed or removed without the
    override being updated).
    """
    valid = {e["tradition"] for e in TRADITION_PROMPTS}
    invalid = [k for k in EXPERIMENTAL_PROMPT_OVERRIDES if k not in valid]
    if invalid:
        raise SystemExit(
            f"EXPERIMENTAL_PROMPT_OVERRIDES contains unknown traditions: "
            f"{invalid}. Valid names: {sorted(valid)}"
        )
```

- [ ] **Step 2: Call the validator from `main()`**

Find in `main()`:
```python
    args = parser.parse_args()
    return asyncio.run(main_async(args))
```

Replace with:
```python
    args = parser.parse_args()
    _validate_experimental_overrides()
    return asyncio.run(main_async(args))
```

- [ ] **Step 3: Syntax check**

Run:
```bash
python -c "import ast; ast.parse(open('scripts/generate-e2e-demo.py').read()); print('ok')"
```

Expected: `ok`

- [ ] **Step 4: Verify `--help` still runs (i.e., validator does not block argparse)**

Run:
```bash
python scripts/generate-e2e-demo.py --help 2>&1 | head -5
```

Expected: standard `usage:` output.

Note: `--help` exits inside `parser.parse_args()`, before the validator is called. That is intentional — unknown-override errors should not block discoverability.

- [ ] **Step 5: Verify the validator actually fires on bad input**

Run (this temporarily corrupts the dict to test the error path):
```bash
python -c "
import sys; sys.path.insert(0, 'scripts')
# Load the module
spec_text = open('scripts/generate-e2e-demo.py').read()
ns = {}
exec(spec_text.replace('if __name__ == \"__main__\":', 'if False:'), ns)
ns['EXPERIMENTAL_PROMPT_OVERRIDES']['not_a_tradition'] = {'prompt': '', 'negative': '', 'suppress_tradition_suffix': False}
try:
    ns['_validate_experimental_overrides']()
    print('FAIL: validator did not raise')
except SystemExit as e:
    print(f'ok: {e}')
"
```

Expected: `ok: EXPERIMENTAL_PROMPT_OVERRIDES contains unknown traditions: ['not_a_tradition']. Valid names: [...]`

- [ ] **Step 6: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "feat(e2e): add EXPERIMENTAL_PROMPT_OVERRIDES + startup validation

Adds the three experimental prompts (chinese_gongbi, chinese_xieyi,
japanese_traditional) from the prompt engineering experiment spec.
Each entry carries a positive, a negative, and a
suppress_tradition_suffix flag (applied in a later commit wiring
override resolution into the loop).

Startup validator fails fast at main() if any override key is not in
TRADITION_PROMPTS — guards against silent drift if a tradition is
renamed or removed without the override being updated.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Add `--traditions` CLI flag + filter + fail-fast

**Files:**
- Modify: `scripts/generate-e2e-demo.py` (argparse section in `main()`; `run_phase1_gallery` signature; `main_async` call site)

**Goal:** New optional CLI flag that accepts a comma-separated list of tradition names. When set, Phase 1 only runs the listed subset. Unknown names fail fast with a clear error before any generation begins.

- [ ] **Step 1: Add the argparse argument**

Find in `main()`:
```python
    parser.add_argument(
        "--eval-mode",
        default="strict",
        choices=("strict", "reference", "fusion"),
        help="VLM evaluation mode for Phase 3. Default: strict",
    )
```

Insert immediately after it:
```python
    parser.add_argument(
        "--traditions",
        default=None,
        help="Comma-separated list of tradition names to regenerate in "
             "Phase 1 (e.g. 'chinese_gongbi,chinese_xieyi'). When unset, "
             "all 13 traditions run. Unknown names fail fast at startup.",
    )
```

- [ ] **Step 2: Parse + validate at startup**

Find in `main()`:
```python
    args = parser.parse_args()
    _validate_experimental_overrides()
    return asyncio.run(main_async(args))
```

Replace with:
```python
    args = parser.parse_args()
    _validate_experimental_overrides()

    # Parse and validate --traditions into a set (or None for "all 13")
    if args.traditions:
        requested = [t.strip() for t in args.traditions.split(",") if t.strip()]
        valid = {e["tradition"] for e in TRADITION_PROMPTS}
        unknown = [t for t in requested if t not in valid]
        if unknown:
            raise SystemExit(
                f"--traditions contains unknown names: {unknown}. "
                f"Valid: {sorted(valid)}"
            )
        args.traditions_set = set(requested)
    else:
        args.traditions_set = None

    return asyncio.run(main_async(args))
```

- [ ] **Step 3: Thread the filter into `run_phase1_gallery`**

Find the signature:
```python
async def run_phase1_gallery(provider_name: str, *, width: int, height: int) -> dict:
```

Replace with:
```python
async def run_phase1_gallery(
    provider_name: str,
    *,
    width: int,
    height: int,
    traditions: set[str] | None = None,
) -> dict:
```

Then find the loop line inside the function:
```python
    for idx, entry in enumerate(TRADITION_PROMPTS, start=1):
```

Replace with:
```python
    selected_entries = (
        [e for e in TRADITION_PROMPTS if e["tradition"] in traditions]
        if traditions is not None
        else list(TRADITION_PROMPTS)
    )
    for idx, entry in enumerate(selected_entries, start=1):
```

Then find the two references to `len(TRADITION_PROMPTS)` inside this function (one in the print at ~line 97, one in the return dict at ~line 142 and ~line 144, one in the status line ~147) and replace each with `len(selected_entries)`.

Specifically, the return dict block:

```python
    return {
        "phase": 1,
        "name": "gallery",
        "provider": provider_name,
        "traditions_total": len(TRADITION_PROMPTS),
        "traditions_ok": ok_count,
        "traditions_failed": len(TRADITION_PROMPTS) - ok_count,
        "elapsed_s": round(total_elapsed, 2),
        "entries": entries,
        "status": "ok" if ok_count == len(TRADITION_PROMPTS) else "partial",
    }
```

becomes:

```python
    return {
        "phase": 1,
        "name": "gallery",
        "provider": provider_name,
        "traditions_total": len(selected_entries),
        "traditions_ok": ok_count,
        "traditions_failed": len(selected_entries) - ok_count,
        "elapsed_s": round(total_elapsed, 2),
        "entries": entries,
        "status": "ok" if ok_count == len(selected_entries) else "partial",
    }
```

And the print inside the loop:
```python
            print(
                f"[{idx:>2}/{len(TRADITION_PROMPTS)}] {tradition} "
                f"via {provider_name}: {prompt}",
                flush=True,
            )
```

becomes:
```python
            print(
                f"[{idx:>2}/{len(selected_entries)}] {tradition} "
                f"via {provider_name}: {prompt}",
                flush=True,
            )
```

- [ ] **Step 4: Pass `traditions` from `main_async` to `run_phase1_gallery`**

Find in `main_async`:
```python
                rep = await run_phase1_gallery(
                    args.provider,
                    width=args.width,
                    height=args.height,
                )
```

Replace with:
```python
                rep = await run_phase1_gallery(
                    args.provider,
                    width=args.width,
                    height=args.height,
                    traditions=args.traditions_set,
                )
```

- [ ] **Step 5: Syntax check**

Run:
```bash
python -c "import ast; ast.parse(open('scripts/generate-e2e-demo.py').read()); print('ok')"
```

Expected: `ok`

- [ ] **Step 6: Verify fail-fast on unknown name**

Run:
```bash
python scripts/generate-e2e-demo.py --phases 1 --traditions foo,bar 2>&1 | tail -3
```

Expected: `SystemExit: --traditions contains unknown names: ['foo', 'bar']. Valid: ['african_traditional', 'brand_design', ...]`

- [ ] **Step 7: Verify `--help` still lists the new flag**

Run:
```bash
python scripts/generate-e2e-demo.py --help 2>&1 | grep -A2 'traditions'
```

Expected: help text for `--traditions` shown.

- [ ] **Step 8: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "feat(e2e): add --traditions filter flag to Phase 1 runner

Comma-separated list of tradition names to regenerate in Phase 1.
Unknown names fail fast at startup before any generation begins.
When unset, all 13 traditions run (existing behavior).

Phase 1 report's traditions_total/ok/failed counts are scoped to the
filtered subset, so a --traditions chinese_gongbi run reports
1/1 ok rather than 1/13.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Add `--gallery-subdir` CLI flag + scoped gallery path + scoped report path

**Files:**
- Modify: `scripts/generate-e2e-demo.py` (argparse; `run_phase1_gallery` signature; `main_async` gallery-dir and report-path computation)

**Goal:** New optional CLI flag that redirects Phase 1 output to a named subdirectory under `assets/demo/v3/`. When set, the Phase 1 report is written to `e2e-report-<subdir>.json` instead of merging into the default `e2e-report.json`. Phase 3 and Phase 8 continue reading from the default `gallery/`.

- [ ] **Step 1: Add the argparse argument**

Find in `main()` (right after the `--traditions` arg you added in Task 4):
```python
    parser.add_argument(
        "--traditions",
        default=None,
        help="Comma-separated list of tradition names to regenerate in "
             "Phase 1 (e.g. 'chinese_gongbi,chinese_xieyi'). When unset, "
             "all 13 traditions run. Unknown names fail fast at startup.",
    )
```

Insert immediately after it:
```python
    parser.add_argument(
        "--gallery-subdir",
        default=None,
        help="Subdirectory under assets/demo/v3/ to write Phase 1 gallery "
             "images into (e.g. 'gallery-promptfix'). When set, the Phase "
             "1 report is scoped to e2e-report-<subdir>.json instead of "
             "merging into the default e2e-report.json. Phase 3 and Phase "
             "8 continue reading from the default gallery/ — this flag "
             "only affects Phase 1 output isolation.",
    )
```

- [ ] **Step 2: Thread `gallery_dir` into `run_phase1_gallery`**

Find the signature (updated in Task 4):
```python
async def run_phase1_gallery(
    provider_name: str,
    *,
    width: int,
    height: int,
    traditions: set[str] | None = None,
) -> dict:
```

Replace with:
```python
async def run_phase1_gallery(
    provider_name: str,
    *,
    width: int,
    height: int,
    traditions: set[str] | None = None,
    gallery_dir: Path | None = None,
) -> dict:
```

Then find:
```python
    GALLERY_DIR.mkdir(parents=True, exist_ok=True)
    provider = get_image_provider(provider_name)
```

Replace with:
```python
    target_dir = gallery_dir if gallery_dir is not None else GALLERY_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    provider = get_image_provider(provider_name)
```

Then find:
```python
        out_path = GALLERY_DIR / f"{tradition}.png"
```

Replace with:
```python
        out_path = target_dir / f"{tradition}.png"
```

- [ ] **Step 3: Compute scoped gallery_dir + report_path in `main_async`**

Find the start of `main_async`:
```python
async def main_async(args: argparse.Namespace) -> int:
    phases = sorted({int(p) for p in args.phases.split(",") if p.strip()})
    DEMO_ROOT.mkdir(parents=True, exist_ok=True)
    phase_reports: list[dict] = []
    overall_status = "ok"
```

Replace with:
```python
async def main_async(args: argparse.Namespace) -> int:
    phases = sorted({int(p) for p in args.phases.split(",") if p.strip()})
    DEMO_ROOT.mkdir(parents=True, exist_ok=True)
    phase_reports: list[dict] = []
    overall_status = "ok"

    # Scope Phase 1 output and report path to --gallery-subdir when set.
    # Phase 3 and Phase 8 still use the default GALLERY_DIR / REPORT_PATH.
    if args.gallery_subdir:
        scoped_gallery_dir = DEMO_ROOT / args.gallery_subdir
        scoped_report_path = DEMO_ROOT / f"e2e-report-{args.gallery_subdir}.json"
    else:
        scoped_gallery_dir = None  # run_phase1_gallery falls back to GALLERY_DIR
        scoped_report_path = REPORT_PATH
```

- [ ] **Step 4: Pass `gallery_dir` to `run_phase1_gallery`**

Find (updated in Task 4):
```python
                rep = await run_phase1_gallery(
                    args.provider,
                    width=args.width,
                    height=args.height,
                    traditions=args.traditions_set,
                )
```

Replace with:
```python
                rep = await run_phase1_gallery(
                    args.provider,
                    width=args.width,
                    height=args.height,
                    traditions=args.traditions_set,
                    gallery_dir=scoped_gallery_dir,
                )
```

- [ ] **Step 5: Use `scoped_report_path` in the report merge + write block**

Find the final report block in `main_async`:

```python
    # Merge with any existing report so re-running one phase preserves the
    # others' results.  Newer entries replace older ones for the same phase.
    merged: dict[int, dict] = {}
    if REPORT_PATH.exists():
        try:
            prior = json.loads(REPORT_PATH.read_text())
            for entry in prior.get("phases", []):
                if isinstance(entry, dict) and "phase" in entry:
                    merged[int(entry["phase"])] = entry
        except Exception:
            pass
    for entry in phase_reports:
        if isinstance(entry, dict) and "phase" in entry:
            merged[int(entry["phase"])] = entry
    final_phases = [merged[k] for k in sorted(merged.keys())]
    aggregate_status = (
        "ok" if all(p.get("status") == "ok" for p in final_phases) else "partial"
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": aggregate_status,
        "phases": final_phases,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print()
    print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")
    print(f"Overall: {overall_status}")
    return 0 if overall_status == "ok" else 1
```

Replace the three `REPORT_PATH` references with `scoped_report_path`:

```python
    # Merge with any existing report so re-running one phase preserves the
    # others' results.  Newer entries replace older ones for the same phase.
    # When --gallery-subdir is set, merges are scoped to that subdir's own
    # report file — the default e2e-report.json is never touched.
    merged: dict[int, dict] = {}
    if scoped_report_path.exists():
        try:
            prior = json.loads(scoped_report_path.read_text())
            for entry in prior.get("phases", []):
                if isinstance(entry, dict) and "phase" in entry:
                    merged[int(entry["phase"])] = entry
        except Exception:
            pass
    for entry in phase_reports:
        if isinstance(entry, dict) and "phase" in entry:
            merged[int(entry["phase"])] = entry
    final_phases = [merged[k] for k in sorted(merged.keys())]
    aggregate_status = (
        "ok" if all(p.get("status") == "ok" for p in final_phases) else "partial"
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": aggregate_status,
        "phases": final_phases,
    }
    scoped_report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print()
    print(f"Report: {scoped_report_path.relative_to(REPO_ROOT)}")
    print(f"Overall: {overall_status}")
    return 0 if overall_status == "ok" else 1
```

- [ ] **Step 6: Syntax check**

Run:
```bash
python -c "import ast; ast.parse(open('scripts/generate-e2e-demo.py').read()); print('ok')"
```

Expected: `ok`

- [ ] **Step 7: Verify `--help` lists the new flag**

Run:
```bash
python scripts/generate-e2e-demo.py --help 2>&1 | grep -A4 'gallery-subdir'
```

Expected: help text for `--gallery-subdir` shown.

- [ ] **Step 8: Verify default path computation (no ComfyUI needed)**

Run:
```bash
python -c "
import sys, types
sys.path.insert(0, 'scripts')
spec = open('scripts/generate-e2e-demo.py').read()
ns = {}
exec(spec.replace('if __name__ == \"__main__\":', 'if False:'), ns)
# Fake args
args = types.SimpleNamespace(gallery_subdir=None)
if args.gallery_subdir:
    sgd = ns['DEMO_ROOT'] / args.gallery_subdir
    srp = ns['DEMO_ROOT'] / f'e2e-report-{args.gallery_subdir}.json'
else:
    sgd = None
    srp = ns['REPORT_PATH']
print(f'default: gallery_dir={sgd}, report={srp}')

args2 = types.SimpleNamespace(gallery_subdir='gallery-promptfix')
sgd2 = ns['DEMO_ROOT'] / args2.gallery_subdir
srp2 = ns['DEMO_ROOT'] / f'e2e-report-{args2.gallery_subdir}.json'
print(f'scoped:  gallery_dir={sgd2}, report={srp2}')
"
```

Expected:
```
default: gallery_dir=None, report=/Users/yhryzy/dev/vulca/assets/demo/v3/e2e-report.json
scoped:  gallery_dir=/Users/yhryzy/dev/vulca/assets/demo/v3/gallery-promptfix, report=/Users/yhryzy/dev/vulca/assets/demo/v3/e2e-report-gallery-promptfix.json
```

- [ ] **Step 9: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "feat(e2e): add --gallery-subdir flag for isolated Phase 1 output

When set, Phase 1 writes images to assets/demo/v3/<subdir>/ and the
report to assets/demo/v3/e2e-report-<subdir>.json. The default
e2e-report.json and gallery/ are untouched, so the canonical v3
baseline is preserved for before/after comparison during the prompt
engineering experiment.

Phase 3 and Phase 8 continue reading from the default gallery/ —
this flag only scopes Phase 1.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Add `--seeds-per-tradition` CLI flag + multi-seed loop + filename suffix

**Files:**
- Modify: `scripts/generate-e2e-demo.py` (argparse; parse helper; `run_phase1_gallery` signature + inner loop; `main_async` pass-through)

**Goal:** New optional CLI flag that accepts `tradition:count` pairs. For each matched tradition, the generator runs `count` times (producing `count` independent random seeds per commit `fb8d47b`). Output filenames gain a `_seedN` suffix when count > 1. Report entries gain a `seed_index` field.

- [ ] **Step 1: Add the argparse argument**

Find in `main()` (right after the `--gallery-subdir` arg from Task 5):
```python
    parser.add_argument(
        "--gallery-subdir",
        default=None,
        help="Subdirectory under assets/demo/v3/ to write Phase 1 gallery "
             "images into (e.g. 'gallery-promptfix'). When set, the Phase "
             "1 report is scoped to e2e-report-<subdir>.json instead of "
             "merging into the default e2e-report.json. Phase 3 and Phase "
             "8 continue reading from the default gallery/ — this flag "
             "only affects Phase 1 output isolation.",
    )
```

Insert immediately after it:
```python
    parser.add_argument(
        "--seeds-per-tradition",
        default=None,
        help="Comma-separated 'tradition:count' pairs (e.g. "
             "'chinese_gongbi:3,japanese_traditional:2'). For each listed "
             "tradition, generate 'count' images with independent random "
             "seeds. Traditions not listed default to 1 image. When "
             "unset, all traditions produce 1 image (existing behavior). "
             "Files with count>1 are named {tradition}_seed{N}.png; "
             "count==1 uses the flat {tradition}.png name.",
    )
```

- [ ] **Step 2: Parse + validate the flag in `main()`**

Find the block you added in Task 4 (right before `return asyncio.run(main_async(args))`):

```python
    # Parse and validate --traditions into a set (or None for "all 13")
    if args.traditions:
        ...
    else:
        args.traditions_set = None

    return asyncio.run(main_async(args))
```

Replace with:
```python
    # Parse and validate --traditions into a set (or None for "all 13")
    if args.traditions:
        requested = [t.strip() for t in args.traditions.split(",") if t.strip()]
        valid = {e["tradition"] for e in TRADITION_PROMPTS}
        unknown = [t for t in requested if t not in valid]
        if unknown:
            raise SystemExit(
                f"--traditions contains unknown names: {unknown}. "
                f"Valid: {sorted(valid)}"
            )
        args.traditions_set = set(requested)
    else:
        args.traditions_set = None

    # Parse --seeds-per-tradition into {tradition: int}. Missing traditions
    # default to 1 seed at lookup time.
    args.seeds_map = {}
    if args.seeds_per_tradition:
        valid = {e["tradition"] for e in TRADITION_PROMPTS}
        for pair in args.seeds_per_tradition.split(","):
            pair = pair.strip()
            if not pair:
                continue
            if ":" not in pair:
                raise SystemExit(
                    f"--seeds-per-tradition entry {pair!r} must be "
                    f"'tradition:count' (e.g. 'chinese_gongbi:3')"
                )
            name, _, count_s = pair.partition(":")
            name = name.strip()
            if name not in valid:
                raise SystemExit(
                    f"--seeds-per-tradition unknown tradition {name!r}. "
                    f"Valid: {sorted(valid)}"
                )
            try:
                count = int(count_s.strip())
            except ValueError:
                raise SystemExit(
                    f"--seeds-per-tradition count for {name!r} "
                    f"must be an integer, got {count_s!r}"
                )
            if count < 1:
                raise SystemExit(
                    f"--seeds-per-tradition count for {name!r} "
                    f"must be >= 1, got {count}"
                )
            args.seeds_map[name] = count

    return asyncio.run(main_async(args))
```

- [ ] **Step 3: Thread `seeds_map` into `run_phase1_gallery` and add the inner seed loop**

Find the signature (updated in Tasks 4-5):
```python
async def run_phase1_gallery(
    provider_name: str,
    *,
    width: int,
    height: int,
    traditions: set[str] | None = None,
    gallery_dir: Path | None = None,
) -> dict:
```

Replace with:
```python
async def run_phase1_gallery(
    provider_name: str,
    *,
    width: int,
    height: int,
    traditions: set[str] | None = None,
    gallery_dir: Path | None = None,
    seeds_map: dict[str, int] | None = None,
) -> dict:
```

Then find the entire body block starting from `selected_entries = ...` through the `entries.append(...)` block and replace it. The new version wraps per-seed work in an inner loop:

Find:
```python
    selected_entries = (
        [e for e in TRADITION_PROMPTS if e["tradition"] in traditions]
        if traditions is not None
        else list(TRADITION_PROMPTS)
    )
    for idx, entry in enumerate(selected_entries, start=1):
        out_path = target_dir / f"{tradition}.png"
        ...
```

(the block through `entries.append({...})` including the error-handling try/except and the trailing print).

Replace the whole loop body with:

```python
    selected_entries = (
        [e for e in TRADITION_PROMPTS if e["tradition"] in traditions]
        if traditions is not None
        else list(TRADITION_PROMPTS)
    )
    seeds_map = seeds_map or {}

    # Flatten (entry, seed_idx, seed_count) so the progress counter and
    # entry list are per-image, not per-tradition.
    work: list[tuple[dict, int, int]] = []
    for entry in selected_entries:
        count = seeds_map.get(entry["tradition"], 1)
        for seed_idx in range(1, count + 1):
            work.append((entry, seed_idx, count))

    for idx, (entry, seed_idx, seed_count) in enumerate(work, start=1):
        tradition = entry["tradition"]
        prompt = entry["prompt"]
        if seed_count == 1:
            filename = f"{tradition}.png"
        else:
            filename = f"{tradition}_seed{seed_idx}.png"
        out_path = target_dir / filename
        t0 = time.time()
        status = "ok"
        error: str | None = None
        dims: tuple[int, int] | None = None
        size_bytes = 0
        try:
            label = f"{tradition}" if seed_count == 1 else f"{tradition}#seed{seed_idx}"
            print(
                f"[{idx:>2}/{len(work)}] {label} "
                f"via {provider_name}: {prompt}",
                flush=True,
            )
            result = await provider.generate(
                prompt,
                tradition=tradition,
                width=width,
                height=height,
                negative_prompt=entry.get("negative", ""),
            )
            assert result.image_b64, "provider returned empty image_b64"
            raw = base64.b64decode(result.image_b64)
            size_bytes = len(raw)
            dims = _validate_png_bytes(raw)
            out_path.write_bytes(raw)
        except Exception as exc:
            status = "failed"
            error = f"{type(exc).__name__}: {exc}"
            traceback.print_exc()
        elapsed = time.time() - t0
        entry_report = {
            "tradition": tradition,
            "prompt": prompt,
            "status": status,
            "path": str(out_path.relative_to(REPO_ROOT)) if status == "ok" else None,
            "width": dims[0] if dims else None,
            "height": dims[1] if dims else None,
            "size_bytes": size_bytes if status == "ok" else None,
            "elapsed_s": round(elapsed, 2),
            "error": error,
        }
        if seed_count > 1:
            entry_report["seed_index"] = seed_idx
            entry_report["seed_count"] = seed_count
        entries.append(entry_report)
        print(
            f"      → {status} in {elapsed:.1f}s"
            + (f" ({dims[0]}x{dims[1]}, {size_bytes // 1024} KB)" if dims else "")
            + (f" [{error}]" if error else "")
        )
```

Then update the return dict's totals. Find:
```python
    return {
        "phase": 1,
        "name": "gallery",
        "provider": provider_name,
        "traditions_total": len(selected_entries),
        "traditions_ok": ok_count,
        "traditions_failed": len(selected_entries) - ok_count,
        "elapsed_s": round(total_elapsed, 2),
        "entries": entries,
        "status": "ok" if ok_count == len(selected_entries) else "partial",
    }
```

Replace with:
```python
    return {
        "phase": 1,
        "name": "gallery",
        "provider": provider_name,
        "traditions_total": len(selected_entries),
        "images_total": len(work),
        "images_ok": ok_count,
        "images_failed": len(work) - ok_count,
        "elapsed_s": round(total_elapsed, 2),
        "entries": entries,
        "status": "ok" if ok_count == len(work) else "partial",
    }
```

(Note: `ok_count` was previously per-tradition; with multi-seed it becomes per-image, which is what we want. The counting logic `sum(1 for e in entries if e["status"] == "ok")` still works and produces the per-image count.)

- [ ] **Step 4: Pass `seeds_map` from `main_async` to `run_phase1_gallery`**

Find (updated in Task 5):
```python
                rep = await run_phase1_gallery(
                    args.provider,
                    width=args.width,
                    height=args.height,
                    traditions=args.traditions_set,
                    gallery_dir=scoped_gallery_dir,
                )
```

Replace with:
```python
                rep = await run_phase1_gallery(
                    args.provider,
                    width=args.width,
                    height=args.height,
                    traditions=args.traditions_set,
                    gallery_dir=scoped_gallery_dir,
                    seeds_map=args.seeds_map,
                )
```

- [ ] **Step 5: Syntax check**

Run:
```bash
python -c "import ast; ast.parse(open('scripts/generate-e2e-demo.py').read()); print('ok')"
```

Expected: `ok`

- [ ] **Step 6: Verify invalid `--seeds-per-tradition` inputs fail fast**

Run:
```bash
python scripts/generate-e2e-demo.py --phases 1 --seeds-per-tradition 'chinese_gongbi' 2>&1 | tail -3
```

Expected: `SystemExit: --seeds-per-tradition entry 'chinese_gongbi' must be 'tradition:count' (e.g. 'chinese_gongbi:3')`

Run:
```bash
python scripts/generate-e2e-demo.py --phases 1 --seeds-per-tradition 'chinese_gongbi:zero' 2>&1 | tail -3
```

Expected: `SystemExit: --seeds-per-tradition count for 'chinese_gongbi' must be an integer, got 'zero'`

Run:
```bash
python scripts/generate-e2e-demo.py --phases 1 --seeds-per-tradition 'foo:3' 2>&1 | tail -3
```

Expected: `SystemExit: --seeds-per-tradition unknown tradition 'foo'. Valid: [...]`

Run:
```bash
python scripts/generate-e2e-demo.py --phases 1 --seeds-per-tradition 'chinese_gongbi:0' 2>&1 | tail -3
```

Expected: `SystemExit: --seeds-per-tradition count for 'chinese_gongbi' must be >= 1, got 0`

- [ ] **Step 7: Verify `--help` shows the flag**

Run:
```bash
python scripts/generate-e2e-demo.py --help 2>&1 | grep -A8 'seeds-per-tradition'
```

Expected: help text for `--seeds-per-tradition` shown.

- [ ] **Step 8: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "feat(e2e): add --seeds-per-tradition for multi-seed Phase 1 runs

New flag accepts 'tradition:count' pairs. Matched traditions
regenerate 'count' times with independent random seeds (each call
draws its own seed via secrets.randbelow in the ComfyUI provider,
see commit fb8d47b). Filenames gain a _seedN suffix when count>1;
count==1 keeps the flat {tradition}.png name for backwards compat.

Report entries under multi-seed runs carry seed_index and seed_count
fields; the gallery loop's progress counter is per-image not
per-tradition, and the return totals become images_total / images_ok
/ images_failed.

Prep for the prompt engineering experiment which runs gongbi x 3
seeds to guard against SDXL's high seed variance on culturally
niche subjects.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Wire override resolution into the generation loop

**Files:**
- Modify: `scripts/generate-e2e-demo.py` (the work-building block and the `provider.generate` call inside `run_phase1_gallery`)

**Goal:** When a selected tradition has an entry in `EXPERIMENTAL_PROMPT_OVERRIDES`, substitute the override's `prompt` + `negative`, and if `suppress_tradition_suffix=True` pass `tradition=""` to `provider.generate` so the provider's auto-appended `, {tradition} style` suffix doesn't dilute the experimental prompt.

- [ ] **Step 1: Update the loop to resolve per-tradition overrides**

Find the multi-seed loop body you wrote in Task 6:

```python
    for idx, (entry, seed_idx, seed_count) in enumerate(work, start=1):
        tradition = entry["tradition"]
        prompt = entry["prompt"]
        if seed_count == 1:
            filename = f"{tradition}.png"
        else:
            filename = f"{tradition}_seed{seed_idx}.png"
        out_path = target_dir / filename
        t0 = time.time()
        status = "ok"
        error: str | None = None
        dims: tuple[int, int] | None = None
        size_bytes = 0
        try:
            label = f"{tradition}" if seed_count == 1 else f"{tradition}#seed{seed_idx}"
            print(
                f"[{idx:>2}/{len(work)}] {label} "
                f"via {provider_name}: {prompt}",
                flush=True,
            )
            result = await provider.generate(
                prompt,
                tradition=tradition,
                width=width,
                height=height,
                negative_prompt=entry.get("negative", ""),
            )
```

Replace with:

```python
    for idx, (entry, seed_idx, seed_count) in enumerate(work, start=1):
        tradition = entry["tradition"]
        # Resolve override per-tradition. Mixed invocations (some with
        # override, some without) work correctly: each tradition is looked
        # up independently.
        override = EXPERIMENTAL_PROMPT_OVERRIDES.get(tradition)
        if override is not None:
            resolved_prompt = override["prompt"]
            resolved_negative = override["negative"]
            suppress_suffix = bool(override.get("suppress_tradition_suffix", False))
        else:
            resolved_prompt = entry["prompt"]
            resolved_negative = entry.get("negative", "")
            suppress_suffix = False
        # When suppressing the auto-suffix, pass tradition="" to the provider.
        # The file name still uses the real tradition key from the loop.
        tradition_arg = "" if suppress_suffix else tradition

        if seed_count == 1:
            filename = f"{tradition}.png"
        else:
            filename = f"{tradition}_seed{seed_idx}.png"
        out_path = target_dir / filename
        t0 = time.time()
        status = "ok"
        error: str | None = None
        dims: tuple[int, int] | None = None
        size_bytes = 0
        try:
            label = f"{tradition}" if seed_count == 1 else f"{tradition}#seed{seed_idx}"
            override_tag = " [override]" if override is not None else ""
            print(
                f"[{idx:>2}/{len(work)}] {label}{override_tag} "
                f"via {provider_name}: {resolved_prompt[:80]}"
                f"{'...' if len(resolved_prompt) > 80 else ''}",
                flush=True,
            )
            result = await provider.generate(
                resolved_prompt,
                tradition=tradition_arg,
                width=width,
                height=height,
                negative_prompt=resolved_negative,
            )
```

- [ ] **Step 2: Record the resolved prompt + override flag in the entry report**

Find (still inside the same loop body):

```python
        entry_report = {
            "tradition": tradition,
            "prompt": prompt,
            "status": status,
            "path": str(out_path.relative_to(REPO_ROOT)) if status == "ok" else None,
            "width": dims[0] if dims else None,
            "height": dims[1] if dims else None,
            "size_bytes": size_bytes if status == "ok" else None,
            "elapsed_s": round(elapsed, 2),
            "error": error,
        }
```

Replace with:

```python
        entry_report = {
            "tradition": tradition,
            "prompt": resolved_prompt,
            "negative": resolved_negative,
            "override_applied": override is not None,
            "tradition_suffix_suppressed": suppress_suffix,
            "status": status,
            "path": str(out_path.relative_to(REPO_ROOT)) if status == "ok" else None,
            "width": dims[0] if dims else None,
            "height": dims[1] if dims else None,
            "size_bytes": size_bytes if status == "ok" else None,
            "elapsed_s": round(elapsed, 2),
            "error": error,
        }
```

- [ ] **Step 3: Syntax check**

Run:
```bash
python -c "import ast; ast.parse(open('scripts/generate-e2e-demo.py').read()); print('ok')"
```

Expected: `ok`

- [ ] **Step 4: Dry-run verification of resolution logic (no ComfyUI needed)**

Run:
```bash
python -c "
spec = open('scripts/generate-e2e-demo.py').read()
ns = {}
exec(spec.replace('if __name__ == \"__main__\":', 'if False:'), ns)
overrides = ns['EXPERIMENTAL_PROMPT_OVERRIDES']
traditions = ns['TRADITION_PROMPTS']

for entry in traditions:
    tr = entry['tradition']
    override = overrides.get(tr)
    if override is not None:
        print(f'{tr}: override applied, suppress_suffix={override[\"suppress_tradition_suffix\"]}')
        print(f'  positive: {override[\"prompt\"][:70]}...')
        print(f'  negative: {override[\"negative\"][:70]}...')
    # else: unchanged — skip printout
"
```

Expected output (three lines with `override applied, suppress_suffix=True` for `chinese_gongbi`, `chinese_xieyi`, `japanese_traditional`, each followed by truncated positive/negative lines).

- [ ] **Step 5: Verify the full experimental CLI passes argparse validation**

Run:
```bash
python scripts/generate-e2e-demo.py \
    --phases 1 \
    --provider comfyui \
    --traditions chinese_gongbi,chinese_xieyi,japanese_traditional \
    --gallery-subdir gallery-promptfix \
    --seeds-per-tradition chinese_gongbi:3 \
    --help 2>&1 | tail -3
```

Expected: help text displayed. This confirms the full flag combination parses without error. (`--help` short-circuits before any generation runs.)

- [ ] **Step 6: Commit**

```bash
git add scripts/generate-e2e-demo.py
git commit -m "feat(e2e): wire EXPERIMENTAL_PROMPT_OVERRIDES into gallery loop

Per-tradition override resolution: for each scheduled work item, the
loop looks up the tradition in EXPERIMENTAL_PROMPT_OVERRIDES. On hit,
the override's positive prompt + negative replace the defaults; when
suppress_tradition_suffix=True, the loop also passes tradition='' to
provider.generate() so the provider's auto-appended ', <tradition>
style' suffix does not dilute the experimental prompt.

Mixed invocations (some traditions with override, some without) are
handled correctly because lookup is per-tradition, not per-invocation.

Report entries now carry the resolved prompt + negative plus the
override_applied and tradition_suffix_suppressed flags, so the
comparison summary can show exactly what was sent to the model.

All plumbing for the prompt engineering experiment is now complete;
the next commit will be the Stage 1 artifacts from running this
against ComfyUI.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Execute Stage 1 — 5 images against real ComfyUI

**Files:**
- Create: `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed1.png` (and seed2/seed3)
- Create: `assets/demo/v3/gallery-promptfix/chinese_xieyi.png`
- Create: `assets/demo/v3/gallery-promptfix/japanese_traditional.png`
- Create: `assets/demo/v3/e2e-report-gallery-promptfix.json`

**Goal:** Run the experimental CLI against a live ComfyUI, produce 5 PNGs + 1 report. This is the only task that requires ComfyUI running.

- [ ] **Step 1: Confirm ComfyUI is running**

Run:
```bash
curl -sS --connect-timeout 2 http://localhost:8188/system_stats 2>&1 | head -20
```

Expected: JSON response with `system` and `devices` fields.

If connection refused: **pause and ask the user to start ComfyUI**. Do not start it yourself — the user manages the ComfyUI lifecycle manually per prior spec convention.

- [ ] **Step 2: Record run metadata for the comparison summary**

Run:
```bash
echo "--- run metadata ---"
date -u +"%Y-%m-%dT%H:%M:%SZ"
echo "vulca commit: $(git rev-parse HEAD)"
echo "comfyui commit: $(cd ~/dev/ComfyUI && git rev-parse HEAD)"
shasum -a 256 ~/dev/ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors
```

Expected:
- UTC timestamp
- vulca commit SHA (your Task 7 commit)
- ComfyUI repo HEAD SHA
- `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b  /Users/yhryzy/dev/ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors` (SHA must match the pinned value in the spec; if it diverges, abort and investigate)

Save this output for use in the comparison summary in Task 9.

- [ ] **Step 3: Run Stage 1**

Run:
```bash
VULCA_IMAGE_BASE_URL=http://localhost:8188 \
    python scripts/generate-e2e-demo.py \
    --phases 1 \
    --provider comfyui \
    --traditions chinese_gongbi,chinese_xieyi,japanese_traditional \
    --gallery-subdir gallery-promptfix \
    --seeds-per-tradition chinese_gongbi:3
```

Expected timeline (approximate):
- Startup + validators: <1s
- 5 images × ~110s each ≈ **9 minutes wall time**
- Progress lines per image: `[N/5] {tradition}#seedK [override] via comfyui: <first 80 chars of prompt>...`
- Final lines: `Report: assets/demo/v3/e2e-report-gallery-promptfix.json` + `Overall: ok`

If any image fails (`→ failed`), capture the traceback and ask the user before proceeding. The common failure modes are: ComfyUI stalled (kill & restart), token weighting `(peony:1.4)` not parsed (fall back to `PEONY PEONY peony` per the Risk section of the spec), or out-of-VRAM (reduce batch via the provider — out of scope for this spike).

- [ ] **Step 4: Verify all 5 files exist and are valid PNGs**

Run:
```bash
ls -lh assets/demo/v3/gallery-promptfix/
```

Expected: exactly these 5 files, each 1-3 MB:
```
chinese_gongbi_seed1.png
chinese_gongbi_seed2.png
chinese_gongbi_seed3.png
chinese_xieyi.png
japanese_traditional.png
```

Run:
```bash
python -c "
from PIL import Image
from pathlib import Path
for p in sorted(Path('assets/demo/v3/gallery-promptfix').glob('*.png')):
    img = Image.open(p)
    print(f'{p.name}: {img.size}  {p.stat().st_size // 1024} KB')
"
```

Expected: each entry reports `(1024, 1024)` and a KB size between ~1500 and ~3000.

- [ ] **Step 5: Verify the report was written to the scoped path**

Run:
```bash
test -f assets/demo/v3/e2e-report-gallery-promptfix.json && echo "report ok"
ls -la assets/demo/v3/e2e-report.json
```

Expected: `report ok`, and the mtime of `e2e-report.json` **unchanged from before the run** (the baseline report must not be touched).

Run:
```bash
python -c "
import json
r = json.load(open('assets/demo/v3/e2e-report-gallery-promptfix.json'))
assert r['overall_status'] == 'ok', r
for phase in r['phases']:
    assert phase['status'] == 'ok', phase
    if phase['phase'] == 1:
        entries = phase['entries']
        assert len(entries) == 5, f'expected 5 entries, got {len(entries)}'
        gongbi_entries = [e for e in entries if e['tradition'] == 'chinese_gongbi']
        assert len(gongbi_entries) == 3, f'expected 3 gongbi seeds, got {len(gongbi_entries)}'
        for e in gongbi_entries:
            assert e['override_applied'] is True
            assert e['tradition_suffix_suppressed'] is True
            assert 'seed_index' in e and 'seed_count' in e
        print('report sanity ok')
"
```

Expected: `report sanity ok`

- [ ] **Step 6: (No commit yet.)** Task 9 scores the images and Task 9's commit bundles all 5 PNGs + report + comparison summary together.

---

## Task 9: Score against rubric, apply Decision Tree, commit artifacts

**Files:**
- Commit: the 5 PNGs + `e2e-report-gallery-promptfix.json` from Task 8
- Post (not committed): the filled-in Comparison Summary template to the user

**Goal:** Hand-score each of the 5 images against the 4-criterion rubric from the spec, determine which Decision Tree branch applies, post the comparison summary to the user, commit the artifacts with the summary embedded in the commit message.

- [ ] **Step 1: Re-read the rubric before viewing any images**

Open `docs/superpowers/specs/2026-04-11-prompt-engineering-experiment-design.md` and re-read the `## Evaluation Rubric` section (~line 266). The four binary criteria per image are:

1. **Subject present** — requested subject visible at all
2. **Subject dominant** — requested subject occupies visual center of gravity
3. **No wrong-genre dominance** — image not dominated by a genre other than requested
4. **Style roughly matches** — brushwork/palette/composition broadly fits the tradition

Pass threshold per image: score ≥ 3 **AND** criterion 1 = 1.

- [ ] **Step 2: View each image and score**

For each of the 5 files, use the `Read` tool on the PNG path (this shows the image to the model). Score each of the 4 criteria 0 or 1 with a one-sentence rationale. Write scores to a scratch scoring block in memory (not committed anywhere).

Files to read (in order):
1. `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed1.png`
2. `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed2.png`
3. `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed3.png`
4. `assets/demo/v3/gallery-promptfix/chinese_xieyi.png`
5. `assets/demo/v3/gallery-promptfix/japanese_traditional.png`

For comparison, also read the baselines to visually confirm the deltas (these already exist on disk):
- `assets/demo/v3/gallery/chinese_gongbi.png` (the broken mountain landscape)
- `assets/demo/v3/gallery/chinese_xieyi.png` (the acceptable ink landscape)
- `assets/demo/v3/gallery/japanese_traditional.png` (the generic colored pagoda)

- [ ] **Step 3: Compute aggregate outcomes**

- **Primary**: gongbi passes in ≥2 of 3 seeds? (0/3, 1/3, 2/3, or 3/3)
- **Secondary**: xieyi passes?
- **Tertiary**: japanese passes?

- [ ] **Step 4: Apply the Decision Tree**

Cross-reference the outcomes against the `## Decision Tree After Results` table in the spec. The five branches are:

| Primary (gongbi ≥2/3) | Secondary (xieyi) | Next action |
|---|---|---|
| Pass | Pass | **Close GuoFeng experiment as not-needed.** Open follow-up for backport decision. |
| Pass | Fail | Rebalance xieyi prompt and re-run xieyi only (1 seed, ~2 min). Primary win still stands. |
| Fail (0/3) | any | **Stage 2 bounded reformulation**: exactly one reformulation iteration for gongbi (stronger token weight, different phrasing, 3 seeds). |
| Ambiguous (1/3) | any | **Stage 2 factorial**: 3 English-no-neg + 3 CJK-with-neg for gongbi to disentangle causes. |

If the outcome triggers Stage 2, **pause** and ask the user for approval before spending another ~5-11 minutes. Do not silently continue.

- [ ] **Step 5: Fill in the Comparison Summary template**

Populate the template from the spec verbatim (section `### Comparison summary template`):

```
## Prompt Engineering Experiment Results

**Run commit**: <from Task 8 Step 2>
**ComfyUI commit**: <from Task 8 Step 2>
**Model SHA-256**: 31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b
**Total wall time**: <from the e2e-report elapsed_s field>
**Stage 2 triggered**: <yes-reformulation / yes-factorial / no>

### Per-image rubric scores

| Image | Subject present | Subject dominant | No wrong-genre | Style match | Total | Pass? |
|---|---|---|---|---|---|---|
| chinese_gongbi_seed1 | <0/1> | <0/1> | <0/1> | <0/1> | <N>/4 | <yes/no> |
| chinese_gongbi_seed2 | <0/1> | <0/1> | <0/1> | <0/1> | <N>/4 | <yes/no> |
| chinese_gongbi_seed3 | <0/1> | <0/1> | <0/1> | <0/1> | <N>/4 | <yes/no> |
| chinese_xieyi        | <0/1> | <0/1> | <0/1> | <0/1> | <N>/4 | <yes/no> |
| japanese_traditional | <0/1> | <0/1> | <0/1> | <0/1> | <N>/4 | <yes/no> |

### Aggregate
- Primary (gongbi ≥2/3 pass): **<PASS/FAIL>** (<N>/3)
- Secondary (xieyi pass): **<PASS/FAIL>**
- Tertiary (japanese pass): **<PASS/FAIL>**

### Decision
**<branch name from the Decision Tree>** → **<next action>**

### One-sentence rationale per image
- gongbi seed1: <rationale>
- gongbi seed2: <rationale>
- gongbi seed3: <rationale>
- xieyi: <rationale>
- japanese: <rationale>
```

Post this summary back to the user as part of your reply (not committed).

- [ ] **Step 6: Commit the Stage 1 artifacts**

Only commit after the user has seen the summary. Use a commit message that embeds the summary's `Aggregate` and `Decision` sections so future `git log -p` readers can find the verdict.

```bash
git add assets/demo/v3/gallery-promptfix/ assets/demo/v3/e2e-report-gallery-promptfix.json
git commit -m "$(cat <<'EOF'
chore(demo): Stage 1 artifacts for prompt engineering experiment

Generated 2026-04-11 against ComfyUI + SDXL base 1.0
(SHA-256 31e35c80...b893f7e5b) with the override prompts from
docs/superpowers/specs/2026-04-11-prompt-engineering-experiment-design.md.

Images:
- chinese_gongbi_seed{1,2,3}.png (multi-seed, test peony-vs-landscape)
- chinese_xieyi.png (regression sentinel)
- japanese_traditional.png (secondary CJK fidelity test)

Aggregate:
- Primary (gongbi ≥2/3): <PASS/FAIL> (<N>/3)
- Secondary (xieyi): <PASS/FAIL>
- Tertiary (japanese): <PASS/FAIL>

Decision: <branch> → <next action>

Full rubric scores and per-image rationale in the session summary
posted alongside this commit.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

(Fill in the angle-bracketed placeholders from the actual scoring before running the commit command.)

- [ ] **Step 7: Push**

Only push if the user explicitly approves.

```bash
git push origin master
```

Expected: fast-forward update of `origin/master`.

---

## Task 10 (conditional): Stage 2 — reformulation or factorial

**Trigger:** Only execute if the Task 9 Decision Tree lands on `Fail (0/3)` or `Ambiguous (1/3)` AND the user approves a Stage 2 budget.

**Files:** same as Task 8 — one more round of generation into `gallery-promptfix/`, report merges into the existing scoped report file.

**Goal:** Single bounded reformulation (≤3 more gongbi images) or Stage 2 factorial (≤6 more gongbi images), then re-score and re-apply the decision tree.

- [ ] **Step 1 (Reformulation branch): rewrite the gongbi override with stronger weighting**

If the trigger is `Primary = 0/3 fail`, edit `EXPERIMENTAL_PROMPT_OVERRIDES["chinese_gongbi"]["prompt"]` to use a stronger token weight and alternate subject phrasing. Example:

```python
        "prompt": (
            "(peony blossom botanical illustration:1.6), close-up centered, "
            "single pink peony flower, fine ink outlines, mineral pigments, "
            "Chinese gongbi meticulous brush painting, flower-and-bird "
            "painting, blank silk background"
        ),
```

No other changes. Commit the edit as a separate commit before running.

- [ ] **Step 2 (Reformulation branch): re-run gongbi × 3**

Run:
```bash
VULCA_IMAGE_BASE_URL=http://localhost:8188 \
    python scripts/generate-e2e-demo.py \
    --phases 1 \
    --provider comfyui \
    --traditions chinese_gongbi \
    --gallery-subdir gallery-promptfix \
    --seeds-per-tradition chinese_gongbi:3
```

Expected: the 3 gongbi PNGs are **overwritten** in place (`seed1.png`, `seed2.png`, `seed3.png`), the scoped report is **merged** (phase 1 replaced, any prior phases preserved). Wall time ~5-6 minutes.

**⚠️ Warning:** This overwrites the original Stage 1 gongbi images. Back them up first if the user wants to preserve both runs for comparison:
```bash
cp assets/demo/v3/gallery-promptfix/chinese_gongbi_seed{1,2,3}.png /tmp/stage1-gongbi-backup/
```

- [ ] **Step 3 (Reformulation branch): re-score and re-apply decision tree**

Repeat Task 9 Steps 2-6 with the new gongbi images only (xieyi and japanese are unchanged).

- [ ] **Step 4 (Factorial branch): wire a second override variant for English-no-negative**

If the trigger is `Primary = 1/3 ambiguous`, the factorial requires two conditions that the current single-override map cannot express. The cleanest minimal patch is to temporarily add two more overrides keyed by synthetic tradition names:

```python
    # Stage 2 factorial siblings — only used for the ambiguous-branch re-run.
    "chinese_gongbi": {  # condition B: English positive, no negative
        "prompt": (
            "(single large peony flower:1.4), close-up centered botanical "
            "portrait, Chinese gongbi meticulous brush painting, fine ink "
            "outlines, mineral pigments, peony blossom with green leaves, "
            "blank silk background, Chinese court flower-and-bird painting, "
            "museum quality botanical study"
        ),
        "negative": "",
        "suppress_tradition_suffix": True,
    },
```

And run with gongbi × 3 seeds. Then restore the original override, add another variant with the original CJK prompt and the Stage 1 negative, and run gongbi × 3 again.

Because this requires restructuring the override map, **prefer to discuss with the user before choosing this branch**. The factorial is the most expensive path (~11 extra minutes), and the scientific payoff is "we know whether English or negative is carrying the signal" — which may or may not be worth it depending on whether the signal is strong enough that you already know what to do next.

- [ ] **Step 5 (either branch): commit + summary**

Commit the new artifacts + a concise summary referencing Task 9's commit. Apply the decision tree with the new scores. If Stage 2 still fails, the spec sends the work to the GuoFeng checkpoint experiment (separate future spec).

- [ ] **Step 6: Close the loop**

Update `memory/project_vulca_current_state.md` (or open a new memory file) with the experiment outcome, the final decision, and any tech debt items:

- If primary passed → the experiment scaffolding (CLI flags, override map) stays in the repo; open a follow-up ticket to decide whether to backport the override prompts into `TRADITION_PROMPTS` as the canonical prompts or design a prompt library
- If primary failed → the experiment scaffolding stays (still useful for the GuoFeng experiment), open a follow-up for the GuoFeng spec
- Either way, mention the disposable-scaffolding tech debt from Goal 3 (no regression tests for the 3 CLI flags) as an open item

---

## Self-review (plan author's own pass before handing off)

- **Spec coverage**: every section of the spec maps to a task:
  - Background / Hypothesis → no task (context only)
  - Goals / Non-Goals → enforced by Tasks 1-7 scope
  - Experimental Scope → Task 8 Step 3 CLI
  - Architecture changes 1-6 → Tasks 1, 2, 3, 4, 5, 6, 7 (six changes, seven tasks because negative_prompt and schema were split)
  - Data Flow → Task 7 + Task 8
  - Evaluation Rubric → Task 9 Step 2
  - Decision Tree → Task 9 Step 4, Task 10 trigger logic
  - Reproducibility → Task 8 Step 2 metadata capture
  - Risk & Rollback → implicit in the per-task commit cadence + Task 8 Step 1 pre-flight
  - Pre-requisites → Task 8 Step 1
  - Test Plan manual verification → Tasks 6 Step 6 + 7 Steps 4-5 (cover the 4-step manual sequence spread across the code-change tasks)
  - Wall time → Task 8 Step 3 expected timeline
  - Deliverables 1-7 → Tasks 1-7 (code), Task 8 (artifacts), Task 9 (comparison summary + go/no-go)
- **Placeholder scan**: no "TODO", "TBD", "implement later" in any code step. The `<>` placeholders in Task 9 Step 5 and Step 6 are intentional — they are template fields that the executor fills in with the actual scoring output.
- **Type consistency**: `run_phase1_gallery` signature accumulates kwargs across Tasks 4, 5, 6 — `traditions: set[str] | None`, `gallery_dir: Path | None`, `seeds_map: dict[str, int] | None`. Each task shows the full signature so the executor sees the cumulative state.
- **Scope**: single file, single spec. No hidden cross-module work.

No fixes needed inline. Handing off.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-11-prompt-engineering-experiment.md`.

Two execution options:

**1. Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks. Fast iteration, clean context between tasks.

**2. Inline Execution** — execute all code-change tasks (1-7) in this session in sequence, with Task 8/9 as a natural checkpoint before the ComfyUI run.

Given:
- All 7 code-change tasks touch one file in sequence (subagent isolation has limited value here since each task depends on the last).
- Task 8 is an external ComfyUI run the user must start.
- Task 9 needs visual image inspection which is most useful in-session.

**My recommendation: Inline Execution.** Subagents for this shape of work add coordination overhead without proportional benefit.

Which approach?
