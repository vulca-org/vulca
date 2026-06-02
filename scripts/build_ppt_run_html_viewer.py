from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK_REL = Path("docs") / "product" / "ppt-run2-data-skill-quality"


@dataclass(frozen=True)
class ArmSpec:
    arm_id: str
    label: str
    slug: str
    role: str


@dataclass(frozen=True)
class RunSpec:
    run_id: str
    label: str
    four_arm_sheet: str
    arms: tuple[ArmSpec, ...]


RUN_SPECS: tuple[RunSpec, ...] = (
    RunSpec(
        "2.0",
        "Run 2.0",
        "run2-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-run1-5-skill", "baseline"),
            ArmSpec("run2_skill", "Run 2.0 full", "ppt-run2-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.1",
        "Run 2.1",
        "run2-1-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-1-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-1-run1-5-skill", "baseline"),
            ArmSpec("run2_1_full_skill", "Run 2.1 full", "ppt-run2-1-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-1-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.2",
        "Run 2.2",
        "run2-2-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-2-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-2-run1-5-skill", "baseline"),
            ArmSpec("run2_2_full_skill", "Run 2.2 full", "ppt-run2-2-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-2-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.3",
        "Run 2.3",
        "run2-3-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-3-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-3-run1-5-skill", "baseline"),
            ArmSpec("run2_3_full_skill", "Run 2.3 full", "ppt-run2-3-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-3-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.4",
        "Run 2.4",
        "run2-4-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-4-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-4-run1-5-skill", "baseline"),
            ArmSpec("run2_4_full_skill", "Run 2.4 full", "ppt-run2-4-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-4-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.5",
        "Run 2.5",
        "run2-5-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-5-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-5-run1-5-skill", "baseline"),
            ArmSpec("run2_5_full_skill", "Run 2.5 full", "ppt-run2-5-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-5-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.6",
        "Run 2.6",
        "run2-6-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-6-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-6-run1-5-skill", "baseline"),
            ArmSpec("run2_6_full_skill", "Run 2.6 full", "ppt-run2-6-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-6-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.6r",
        "Run 2.6R",
        "run2-6r-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-6r-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-6r-run1-5-skill", "baseline"),
            ArmSpec("run2_6r_visual_repair_full_skill", "Run 2.6R full", "ppt-run2-6r-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-6r-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.7",
        "Run 2.7",
        "run2-7-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-7-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-7-run1-5-skill", "baseline"),
            ArmSpec("run2_7_full_skill", "Run 2.7 full", "ppt-run2-7-full-vulca", "full"),
            ArmSpec("bad_workflow_memory", "Bad workflow memory", "ppt-run2-7-bad-workflow-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.8",
        "Run 2.8",
        "run2-8-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-8-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-8-run1-5-skill", "baseline"),
            ArmSpec("run2_8_full_skill", "Run 2.8 full", "ppt-run2-8-full-vulca", "full"),
            ArmSpec("bad_memory_schema", "Bad memory schema", "ppt-run2-8-bad-memory-schema", "negative"),
        ),
    ),
)


def rel(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def build_arm(base: Path, out: Path, spec: ArmSpec) -> dict[str, Any] | None:
    arm_dir = base / spec.slug
    preview = arm_dir / "preview"
    if not preview.exists():
        return None
    slides = [preview / f"slide-{index:02d}.png" for index in range(1, 7)]
    slides = [path for path in slides if path.exists()]
    if not slides:
        return None
    trace = read_json(arm_dir / "trace_manifest.json")
    return {
        "id": spec.arm_id,
        "label": spec.label,
        "role": spec.role,
        "slug": spec.slug,
        "contactSheet": rel(preview / "contact-sheet.png", out.parent) if (preview / "contact-sheet.png").exists() else "",
        "traceManifest": rel(arm_dir / "trace_manifest.json", out.parent) if (arm_dir / "trace_manifest.json").exists() else "",
        "deliveryGate": trace.get("release_decision") or trace.get("delivery_gate") or "internal-demo-ok-public-blocked",
        "slides": [rel(path, out.parent) for path in slides],
    }


def build_reference_data(repo_root: Path) -> dict[str, Any]:
    pack = repo_root / PACK_REL
    sources = read_json(pack / "sources.json")
    decomposition = read_json(pack / "run2_8_tutorial_decomposition.json")
    memory = read_json(pack / "run2_8_executable_design_memory.json")
    gate_matrix = read_json(pack / "run2_8_workflow_gate_matrix.json")
    run29_repair = read_json(pack / "run2_9_visual_primitive_repair.json")
    run29_modules = read_json(pack / "run2_9_executable_visual_modules.json")
    run29_gate_matrix = read_json(pack / "run2_9_visual_gate_matrix.json")
    workflow = read_json(pack / "skill_workflow.json")
    source_records = read_json(pack / "run2_7_multimodal_source_records.json")
    skill_markdown = read_text(pack / "vulca_ppt_skill.md")

    return {
        "packPath": PACK_REL.as_posix(),
        "diagnosis": [
            {
                "label": "2.8 visual verdict",
                "body": "The data and workflow are executable, but the code bindings still render mostly type ladders, spacing zones, before/after panels, gates, and one hero object.",
            },
            {
                "label": "Why it still feels boxy",
                "body": "Tutorial learning has been translated into native PPT rectangles and text modules, so it proves traceable execution more than high-end editorial composition.",
            },
            {
                "label": "Next design problem",
                "body": "The next rerun must upgrade visual primitives: product-surface composition, asymmetry, depth, editorial spread, motion beats, and a non-dashboard climax.",
            },
        ],
        "sources": sources.get("sources", []),
        "sourceRecords": source_records.get("records", []),
        "decompositionStatus": decomposition.get("status", ""),
        "decompositionUnits": decomposition.get("units", []),
        "memoryStatus": memory.get("status", ""),
        "memoryBindings": memory.get("bindings", []),
        "gateStatus": gate_matrix.get("status", ""),
        "workflowGates": gate_matrix.get("gates", []),
        "run29RepairStatus": run29_repair.get("status", ""),
        "run29PrimitiveRepairs": run29_repair.get("primitive_repairs", []),
        "run29ModuleStatus": run29_modules.get("status", ""),
        "run29VisualModules": run29_modules.get("modules", []),
        "run29GateStatus": run29_gate_matrix.get("status", ""),
        "run29VisualGates": run29_gate_matrix.get("gates", []),
        "workflowStatus": workflow.get("status", ""),
        "workflowStages": workflow.get("stages", []),
        "skillMarkdown": skill_markdown,
    }


def build_data(presentations_dir: Path, out: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[1]
    runs: list[dict[str, Any]] = []
    for run in RUN_SPECS:
        arms = [arm for arm_spec in run.arms if (arm := build_arm(presentations_dir, out, arm_spec))]
        if not arms:
            continue
        full_arm = next((arm for arm in arms if arm["role"] == "full"), arms[0])
        four_arm_sheet = presentations_dir / run.four_arm_sheet
        runs.append(
            {
                "id": run.run_id,
                "label": run.label,
                "fourArmSheet": rel(four_arm_sheet, out.parent) if four_arm_sheet.exists() else "",
                "arms": arms,
                "fullArm": full_arm,
            }
        )
    return {
        "title": "PPT run viewer",
        "status": "internal-demo-ok-public-blocked",
        "runs": runs,
        "latestRunId": runs[-1]["id"] if runs else "",
        "generatedFrom": "scripts/build_ppt_run_html_viewer.py",
        "references": build_reference_data(repo_root),
    }


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def build_html(data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=True, indent=2)
    latest = esc(str(data.get("latestRunId") or ""))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>PPT Run Viewer</title>
  <style>
    :root {{
      --bg: #f5f3ee;
      --panel: #ffffff;
      --ink: #17181c;
      --muted: #5d6670;
      --line: #d0cbc1;
      --dark: #15171c;
      --accent: #e24d30;
      --blue: #2a63da;
      --green: #0d8d68;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; min-height: 100%; background: var(--bg); color: var(--ink); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ overflow: hidden; }}
    button, input {{ font: inherit; }}
    .app {{ display: grid; grid-template-rows: auto auto 1fr; height: 100vh; }}
    .topbar {{ display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 18px 22px 14px; border-bottom: 1px solid var(--line); background: rgba(245, 243, 238, 0.96); }}
    .brand {{ display: flex; flex-direction: column; gap: 3px; min-width: 220px; }}
    .brand h1 {{ margin: 0; font-size: 22px; line-height: 1.1; }}
    .brand .meta {{ color: var(--muted); font-size: 12px; }}
    .statusbar {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    .pill {{ display: inline-flex; align-items: center; height: 28px; padding: 0 10px; border-radius: 999px; background: var(--panel); border: 1px solid var(--line); font-size: 12px; color: var(--muted); white-space: nowrap; }}
    .pill.strong {{ background: var(--dark); border-color: var(--dark); color: #fff; }}
    .toolbar {{ display: flex; align-items: center; gap: 18px; padding: 12px 22px; border-bottom: 1px solid var(--line); background: #fbfaf7; overflow-x: auto; }}
    .versionRail, .viewRail {{ display: flex; gap: 8px; align-items: center; }}
    .railLabel {{ font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; }}
    .seg {{ height: 34px; border: 1px solid var(--line); background: #fff; color: var(--ink); border-radius: 6px; padding: 0 12px; cursor: pointer; white-space: nowrap; }}
    .seg.active {{ background: var(--dark); color: #fff; border-color: var(--dark); }}
    .seg[data-role="full"].active {{ background: var(--accent); border-color: var(--accent); }}
    .content {{ min-height: 0; overflow: auto; padding: 18px 22px 26px; }}
    .sectionHeader {{ display: flex; align-items: end; justify-content: space-between; gap: 18px; margin-bottom: 14px; }}
    .sectionHeader h2 {{ margin: 0; font-size: 20px; }}
    .sectionHeader .summary {{ color: var(--muted); font-size: 13px; }}
    .fourGrid {{ display: grid; grid-template-columns: repeat(4, minmax(340px, 1fr)); gap: 16px; min-width: 1400px; }}
    .seriesGrid {{ display: flex; gap: 16px; align-items: flex-start; min-width: max-content; }}
    .armCard, .seriesCard {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; box-shadow: 0 1px 0 rgba(0,0,0,0.04); }}
    .armHead, .seriesHead {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; background: var(--dark); color: #fff; padding: 11px 12px; }}
    .armHead h3, .seriesHead h3 {{ margin: 0; font-size: 14px; }}
    .armHead .tag, .seriesHead .tag {{ font-size: 10px; color: #d9dde2; text-transform: uppercase; }}
    .slidesGrid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; padding: 10px; }}
    .seriesCard {{ width: 360px; }}
    .seriesCard .slidesGrid {{ grid-template-columns: repeat(2, 1fr); }}
    .slideTile {{ position: relative; border: 1px solid #d8dce0; background: #fff; cursor: zoom-in; overflow: hidden; }}
    .slideTile img {{ display: block; width: 100%; height: auto; aspect-ratio: 16 / 9; object-fit: contain; background: #fff; }}
    .slideNo {{ position: absolute; left: 6px; bottom: 5px; height: 18px; min-width: 34px; padding: 2px 6px; background: rgba(21,23,28,0.82); color: #fff; font-size: 10px; border-radius: 3px; }}
    .contactRow {{ display: flex; gap: 8px; padding: 0 10px 10px; }}
    .contactRow button {{ height: 30px; border: 1px solid var(--line); background: #f8f8f5; border-radius: 6px; padding: 0 10px; cursor: zoom-in; color: var(--muted); }}
    .sheetPanel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 12px; min-width: 1120px; }}
    .sheetPanel img {{ display: block; width: 100%; height: auto; border: 1px solid #c8c4b8; background: #fff; cursor: zoom-in; }}
    .dataStack {{ display: grid; gap: 16px; max-width: 1480px; }}
    .dataBand {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
    .dataBandHead {{ display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; padding: 14px 16px; border-bottom: 1px solid var(--line); background: #fbfaf7; }}
    .dataBandHead h3 {{ margin: 0; font-size: 16px; }}
    .dataBandHead p {{ margin: 4px 0 0; color: var(--muted); font-size: 12px; line-height: 1.45; }}
    .dataGrid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; padding: 14px; }}
    .dataCard {{ border: 1px solid #d8d5ce; border-radius: 8px; background: #fff; padding: 12px; display: grid; gap: 9px; align-content: start; min-width: 0; }}
    .dataCard h4 {{ margin: 0; font-size: 14px; line-height: 1.25; overflow-wrap: anywhere; }}
    .dataCard p {{ margin: 0; color: var(--muted); font-size: 12px; line-height: 1.45; overflow-wrap: anywhere; }}
    .dataCard a {{ color: var(--blue); text-decoration: none; overflow-wrap: anywhere; }}
    .dataCard a:hover {{ text-decoration: underline; }}
    .dataLabel {{ color: var(--muted); font-size: 10px; font-weight: 800; letter-spacing: 0; text-transform: uppercase; }}
    .chipRow {{ display: flex; flex-wrap: wrap; gap: 5px; }}
    .chip {{ display: inline-flex; align-items: center; min-height: 22px; padding: 2px 7px; border: 1px solid #d8d5ce; border-radius: 999px; background: #f7f6f1; color: #343841; font-size: 11px; overflow-wrap: anywhere; }}
    .dataList {{ margin: 0; padding-left: 18px; color: var(--muted); font-size: 12px; line-height: 1.45; }}
    .dataPre {{ margin: 0; max-height: 420px; overflow: auto; white-space: pre-wrap; color: #2a2e35; font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; padding: 14px; }}
    .empty {{ padding: 40px; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; color: var(--muted); }}
    .modal {{ position: fixed; inset: 0; z-index: 20; display: none; align-items: center; justify-content: center; background: rgba(12, 14, 17, 0.86); padding: 22px; }}
    .modal.open {{ display: flex; }}
    .modalFrame {{ max-width: min(96vw, 1560px); max-height: 94vh; background: #111; border: 1px solid #3a3e46; border-radius: 10px; overflow: hidden; box-shadow: 0 18px 48px rgba(0,0,0,0.34); }}
    .modalBar {{ display: flex; justify-content: space-between; gap: 12px; align-items: center; color: #fff; padding: 10px 12px; background: #15171c; }}
    .modalBar button {{ height: 30px; border: 1px solid #4b515a; background: #242832; color: #fff; border-radius: 6px; cursor: pointer; }}
    .modal img {{ display: block; max-width: 96vw; max-height: calc(94vh - 52px); width: auto; height: auto; background: #fff; }}
    @media (max-width: 900px) {{
      body {{ overflow: auto; }}
      .app {{ height: auto; min-height: 100vh; }}
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      .statusbar {{ justify-content: flex-start; }}
      .fourGrid {{ grid-template-columns: minmax(340px, 1fr); min-width: 0; }}
      .seriesGrid {{ min-width: 0; flex-direction: column; }}
      .seriesCard {{ width: 100%; }}
      .sheetPanel {{ min-width: 0; }}
    }}
  </style>
</head>
<body>
  <div class="app">
    <header class="topbar">
      <div class="brand">
        <h1>PPT Run Viewer</h1>
        <div class="meta">latest {latest} / generated native PPT outputs</div>
      </div>
      <div class="statusbar">
        <span class="pill strong">internal demo</span>
        <span class="pill">public blocked</span>
        <span class="pill" id="runCount"></span>
      </div>
    </header>
    <nav class="toolbar">
      <div class="versionRail" id="versionRail"><span class="railLabel">Version</span></div>
      <div class="viewRail" id="viewRail">
        <span class="railLabel">View</span>
        <button class="seg active" data-view="four">Four arms</button>
        <button class="seg" data-view="series">Full series</button>
        <button class="seg" data-view="sheet">Sheets</button>
        <button class="seg" data-view="data">Data / Skill</button>
      </div>
    </nav>
    <main class="content" id="content"></main>
  </div>
  <div class="modal" id="modal" aria-hidden="true">
    <div class="modalFrame">
      <div class="modalBar">
        <div id="modalTitle"></div>
        <button id="modalClose">Close</button>
      </div>
      <img id="modalImage" alt="">
    </div>
  </div>
  <script>
    const DATA = {payload};
    let selectedRunId = DATA.latestRunId;
    let selectedView = "four";

    const byId = (id) => document.getElementById(id);
    const content = byId("content");
    const versionRail = byId("versionRail");
    const modal = byId("modal");
    const modalImage = byId("modalImage");
    const modalTitle = byId("modalTitle");

    byId("runCount").textContent = `${{DATA.runs.length}} versions`;

    function activeRun() {{
      return DATA.runs.find((run) => run.id === selectedRunId) || DATA.runs[DATA.runs.length - 1];
    }}

    function button(label, className, attrs = "") {{
      return `<button class="${{className}}" ${{attrs}}>${{label}}</button>`;
    }}

    function safe(value) {{
      return value === undefined || value === null ? "" : String(value);
    }}

    function escapeHtml(value) {{
      const map = {{
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      }};
      return safe(value).replace(/[&<>"']/g, (char) => map[char]);
    }}

    function safeHref(value) {{
      const url = safe(value).trim();
      return /^https?:\\/\\//i.test(url) ? url : "";
    }}

    function chipList(items) {{
      const values = Array.isArray(items) ? items : [];
      if (!values.length) return "";
      return `<div class="chipRow">${{values.map((item) => `<span class="chip">${{escapeHtml(item)}}</span>`).join("")}}</div>`;
    }}

    function listBlock(items) {{
      const values = Array.isArray(items) ? items : [];
      if (!values.length) return "";
      return `<ul class="dataList">${{values.map((item) => `<li>${{escapeHtml(item)}}</li>`).join("")}}</ul>`;
    }}

    function detailBlock(label, value) {{
      if (value === undefined || value === null || value === "") return "";
      if (Array.isArray(value) && !value.length) return "";
      if (typeof value === "object" && !Array.isArray(value)) {{
        return `<div><div class="dataLabel">${{escapeHtml(label)}}</div><pre class="dataPre">${{escapeHtml(JSON.stringify(value, null, 2))}}</pre></div>`;
      }}
      if (Array.isArray(value)) {{
        return `<div><div class="dataLabel">${{escapeHtml(label)}}</div>${{listBlock(value)}}</div>`;
      }}
      return `<div><div class="dataLabel">${{escapeHtml(label)}}</div><p>${{escapeHtml(value)}}</p></div>`;
    }}

    function slideTile(src, title, index) {{
      return `<button class="slideTile" data-src="${{src}}" data-title="${{title}} / slide ${{index + 1}}">
        <img src="${{src}}" loading="lazy" alt="${{title}} slide ${{index + 1}}">
        <span class="slideNo">S${{String(index + 1).padStart(2, "0")}}</span>
      </button>`;
    }}

    function renderVersionRail() {{
      const buttons = DATA.runs.map((run) => {{
        const active = run.id === selectedRunId ? " active" : "";
        return `<button class="seg${{active}}" data-run="${{run.id}}">${{run.label}}</button>`;
      }}).join("");
      versionRail.innerHTML = `<span class="railLabel">Version</span>${{buttons}}`;
    }}

    function renderFour() {{
      const run = activeRun();
      if (!run) {{
        content.innerHTML = `<div class="empty">No generated runs found.</div>`;
        return;
      }}
      const arms = run.arms.map((arm) => {{
        const slides = arm.slides.map((src, index) => slideTile(src, `${{run.label}} / ${{arm.label}}`, index)).join("");
        const contact = arm.contactSheet
          ? `<button data-src="${{arm.contactSheet}}" data-title="${{run.label}} / ${{arm.label}} contact sheet">Contact sheet</button>`
          : "";
        return `<section class="armCard">
          <div class="armHead"><h3>${{arm.label}}</h3><span class="tag">${{arm.role}}</span></div>
          <div class="slidesGrid">${{slides}}</div>
          <div class="contactRow">${{contact}}</div>
        </section>`;
      }}).join("");
      content.innerHTML = `<div class="sectionHeader">
        <div><h2>${{run.label}} four-arm comparison</h2><div class="summary">${{run.arms.length}} arms / six editable native-PPT slide previews per arm</div></div>
        <span class="pill">${{DATA.status}}</span>
      </div><div class="fourGrid">${{arms}}</div>`;
    }}

    function renderSeries() {{
      const cards = DATA.runs.map((run) => {{
        const arm = run.fullArm;
        const slides = arm.slides.map((src, index) => slideTile(src, `${{run.label}} / ${{arm.label}}`, index)).join("");
        return `<section class="seriesCard">
          <div class="seriesHead"><h3>${{run.label}}</h3><span class="tag">${{arm.id}}</span></div>
          <div class="slidesGrid">${{slides}}</div>
        </section>`;
      }}).join("");
      content.innerHTML = `<div class="sectionHeader">
        <div><h2>Full skill series</h2><div class="summary">Run 2.0 through latest full arm, kept as individual slide previews</div></div>
        <span class="pill">${{DATA.runs.length}} versions</span>
      </div><div class="seriesGrid">${{cards}}</div>`;
    }}

    function renderSheets() {{
      const run = activeRun();
      const four = run?.fourArmSheet
        ? `<section class="sheetPanel"><img src="${{run.fourArmSheet}}" data-src="${{run.fourArmSheet}}" data-title="${{run.label}} four-arm sheet" alt="${{run.label}} four-arm sheet"></section>`
        : `<div class="empty">No four-arm sheet for ${{run?.label || "selected run"}}.</div>`;
      const seriesSheet = "run2-full-skill-series-horizontal.png";
      content.innerHTML = `<div class="sectionHeader">
        <div><h2>Comparison sheets</h2><div class="summary">${{run.label}} four-arm sheet plus the current full-series sheet</div></div>
      </div>
      <div style="display:grid; gap:16px;">
        ${{four}}
        <section class="sheetPanel"><img src="${{seriesSheet}}" data-src="${{seriesSheet}}" data-title="Full skill series sheet" alt="Full skill series sheet"></section>
      </div>`;
    }}

    function sourceCard(source) {{
      const href = safeHref(source.url);
      const url = href
        ? `<a href="${{escapeHtml(href)}}" target="_blank" rel="noreferrer">${{escapeHtml(source.url)}}</a>`
        : detailBlock("URL", source.url);
      return `<article class="dataCard">
        <h4>${{escapeHtml(source.title || source.id)}}</h4>
        ${{chipList([source.role, source.allowed_use].filter(Boolean))}}
        <p><strong>${{escapeHtml(source.id)}}</strong></p>
        ${{url}}
        ${{detailBlock("Accessed", source.accessed_on)}}
      </article>`;
    }}

    function sourceRecordCard(record) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(record.id)}}</h4>
        ${{chipList(record.modalities)}}
        ${{detailBlock("Source", record.source_id)}}
        ${{detailBlock("Observation", record.visual_observation)}}
        ${{detailBlock("Derived rule", record.extracted_design_rule)}}
        ${{detailBlock("Native implication", record.native_ppt_implication)}}
      </article>`;
    }}

    function decompositionCard(unit) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(unit.id)}}</h4>
        ${{chipList(unit.modality_mix)}}
        ${{detailBlock("Source ids", unit.source_ids)}}
        ${{detailBlock("Tutorial method", unit.tutorial_anchor)}}
        ${{detailBlock("Observed move", unit.observed_design_move)}}
        ${{detailBlock("Derived rule", unit.derived_rule)}}
        ${{detailBlock("Code binding", unit.code_generation_binding)}}
        ${{detailBlock("Native obligation", unit.native_ppt_obligation)}}
        ${{detailBlock("Failure probe", unit.failure_probe)}}
      </article>`;
    }}

    function bindingCard(binding) {{
      const code = binding.code_binding || {{}};
      return `<article class="dataCard">
        <h4>${{escapeHtml(binding.id)}}</h4>
        ${{chipList(binding.applies_to_slide_roles)}}
        ${{detailBlock("Function", code.function_name)}}
        ${{detailBlock("Params", code.params)}}
        ${{detailBlock("Composition constraints", binding.composition_constraints)}}
        ${{detailBlock("Typography constraints", binding.typography_constraints)}}
        ${{detailBlock("Spacing constraints", binding.spacing_constraints)}}
        ${{detailBlock("Negative-control failure", binding.negative_control_failure)}}
      </article>`;
    }}

    function gateCard(gate) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(gate.id)}}</h4>
        ${{chipList([gate.slide_role])}}
        ${{detailBlock("Required code bindings", gate.required_code_bindings)}}
        ${{detailBlock("Layout budget", gate.layout_budget)}}
        ${{detailBlock("Pass/fail checks", gate.pass_fail_checks)}}
        ${{detailBlock("Trace fields", gate.trace_fields)}}
      </article>`;
    }}

    function run29PrimitiveCard(primitive) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(primitive.id)}}</h4>
        ${{chipList(primitive.target_slide_roles)}}
        ${{detailBlock("Source ids", primitive.source_ids)}}
        ${{detailBlock("Visual problem", primitive.visual_problem)}}
        ${{detailBlock("Reference method", primitive.reference_method)}}
        ${{detailBlock("Visual primitive", primitive.extracted_visual_primitive)}}
        ${{detailBlock("Native PPT translation", primitive.native_ppt_translation)}}
        ${{detailBlock("Code obligation", primitive.code_module_obligation)}}
        ${{detailBlock("Forbidden box patterns", primitive.forbidden_box_patterns)}}
        ${{detailBlock("Boxiness probe", primitive.boxiness_failure_probe)}}
      </article>`;
    }}

    function run29ModuleCard(module) {{
      const code = module.code_binding || {{}};
      return `<article class="dataCard">
        <h4>${{escapeHtml(module.id)}}</h4>
        ${{chipList(module.applies_to_slide_roles)}}
        ${{detailBlock("Function", code.function_name)}}
        ${{detailBlock("Params", code.params)}}
        ${{detailBlock("Composition contract", module.composition_contract)}}
        ${{detailBlock("Native primitives", module.native_ppt_primitives)}}
        ${{detailBlock("Negative control", module.negative_control_failure)}}
        ${{detailBlock("QA probe", module.qa_probe)}}
      </article>`;
    }}

    function run29VisualGateCard(gate) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(gate.id)}}</h4>
        ${{chipList([gate.slide_role])}}
        ${{detailBlock("Visual primitive ids", gate.visual_primitive_ids)}}
        ${{detailBlock("Visual module ids", gate.visual_module_ids)}}
        ${{detailBlock("Required code modules", gate.required_code_modules)}}
        ${{detailBlock("Boxiness probe", gate.boxiness_failure_probe)}}
        ${{detailBlock("Pass/fail checks", gate.pass_fail_checks)}}
        ${{detailBlock("Trace fields", gate.trace_fields)}}
      </article>`;
    }}

    function stageCard(stage) {{
      return `<article class="dataCard">
        <h4>${{String(stage.order || "").padStart(2, "0")}} / ${{escapeHtml(stage.id)}}</h4>
        ${{detailBlock("Inputs", stage.inputs || stage.input_files || stage.input_ids)}}
        ${{detailBlock("Outputs", stage.outputs || stage.output_files || stage.output_ids)}}
        ${{detailBlock("Gate", stage.pass_fail_gate || stage.gate || stage.qa_gate)}}
        ${{detailBlock("Repair", stage.repair_recommendation)}}
      </article>`;
    }}

    function renderData() {{
      const refs = DATA.references || {{}};
      const diagnosis = (refs.diagnosis || []).map((item) => `<article class="dataCard"><h4>${{escapeHtml(item.label)}}</h4><p>${{escapeHtml(item.body)}}</p></article>`).join("");
      const sources = (refs.sources || []).map(sourceCard).join("");
      const records = (refs.sourceRecords || []).map(sourceRecordCard).join("");
      const units = (refs.decompositionUnits || []).map(decompositionCard).join("");
      const bindings = (refs.memoryBindings || []).map(bindingCard).join("");
      const gates = (refs.workflowGates || []).map(gateCard).join("");
      const run29Primitives = (refs.run29PrimitiveRepairs || []).map(run29PrimitiveCard).join("");
      const run29Modules = (refs.run29VisualModules || []).map(run29ModuleCard).join("");
      const run29Gates = (refs.run29VisualGates || []).map(run29VisualGateCard).join("");
      const stages = (refs.workflowStages || []).map(stageCard).join("");
      const skill = escapeHtml(refs.skillMarkdown || "Missing vulca_ppt_skill.md");

      content.innerHTML = `<div class="sectionHeader">
        <div><h2>Reference data and skill workflow</h2><div class="summary">Shows the allowed derived evidence behind Run 2.8, not copied tutorial media or source layouts.</div></div>
        <span class="pill">${{escapeHtml(refs.packPath || "case pack")}}</span>
      </div>
      <div class="dataStack">
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Why 2.8 still looks close to 2.7</h3><p>The current bottleneck is visual primitive quality, not trace plumbing.</p></div></div>
          <div class="dataGrid">${{diagnosis}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Source URLs</h3><p>Reference identities stored in sources.json. These links are for inspection; copied media, layouts, transcripts, and brand marks remain forbidden.</p></div><span class="pill">${{(refs.sources || []).length}} sources</span></div>
          <div class="dataGrid">${{sources}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.7 multimodal records</h3><p>Derived source observations feeding the later Run 2.8 decomposition.</p></div><span class="pill">${{(refs.sourceRecords || []).length}} records</span></div>
          <div class="dataGrid">${{records}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.8 tutorial decomposition</h3><p>${{escapeHtml(refs.decompositionStatus)}}. This is where tutorial/video methods become generator rules.</p></div><span class="pill">${{(refs.decompositionUnits || []).length}} units</span></div>
          <div class="dataGrid">${{units}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Executable design memory</h3><p>${{escapeHtml(refs.memoryStatus)}}. These bindings explain why the output still depends on a small set of native PPT modules.</p></div><span class="pill">${{(refs.memoryBindings || []).length}} bindings</span></div>
          <div class="dataGrid">${{bindings}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Workflow gate matrix</h3><p>${{escapeHtml(refs.gateStatus)}}. Per-slide role gates connect data selection to required code calls and trace fields.</p></div><span class="pill">${{(refs.workflowGates || []).length}} gates</span></div>
          <div class="dataGrid">${{gates}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.9 visual primitive repair</h3><p>${{escapeHtml(refs.run29RepairStatus)}}. Converts the Run 2.8 boxiness diagnosis into native editable visual primitives.</p></div><span class="pill">${{(refs.run29PrimitiveRepairs || []).length}} primitives</span></div>
          <div class="dataGrid">${{run29Primitives}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.9 executable visual modules</h3><p>${{escapeHtml(refs.run29ModuleStatus)}}. Function-level contracts for editorial spread, product depth, storyboard, climax stage, and typographic field modules.</p></div><span class="pill">${{(refs.run29VisualModules || []).length}} modules</span></div>
          <div class="dataGrid">${{run29Modules}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.9 visual gate matrix</h3><p>${{escapeHtml(refs.run29GateStatus)}}. Per-role gates require visual delta from Run 2.8 and explicit boxiness failure probes.</p></div><span class="pill">${{(refs.run29VisualGates || []).length}} gates</span></div>
          <div class="dataGrid">${{run29Gates}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Skill workflow stages</h3><p>${{escapeHtml(refs.workflowStatus)}}. This is the ordered product loop, not a one-off prompt.</p></div><span class="pill">${{(refs.workflowStages || []).length}} stages</span></div>
          <div class="dataGrid">${{stages}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Vulca PPT Skill</h3><p>The persistent skill contract used to decide what data, memory, code, QA, and release gates mean.</p></div></div>
          <pre class="dataPre">${{skill}}</pre>
        </section>
      </div>`;
    }}

    function render() {{
      renderVersionRail();
      document.querySelectorAll("#viewRail .seg").forEach((item) => {{
        item.classList.toggle("active", item.dataset.view === selectedView);
      }});
      if (selectedView === "series") renderSeries();
      else if (selectedView === "sheet") renderSheets();
      else if (selectedView === "data") renderData();
      else renderFour();
    }}

    function openModal(src, title) {{
      modalImage.src = src;
      modalImage.alt = title;
      modalTitle.textContent = title;
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
    }}

    versionRail.addEventListener("click", (event) => {{
      const target = event.target.closest("[data-run]");
      if (!target) return;
      selectedRunId = target.dataset.run;
      selectedView = selectedView || "four";
      render();
    }});

    byId("viewRail").addEventListener("click", (event) => {{
      const target = event.target.closest("[data-view]");
      if (!target) return;
      selectedView = target.dataset.view;
      render();
    }});

    content.addEventListener("click", (event) => {{
      const target = event.target.closest("[data-src]");
      if (!target) return;
      openModal(target.dataset.src, target.dataset.title || target.getAttribute("alt") || "preview");
    }});

    byId("modalClose").addEventListener("click", () => {{
      modal.classList.remove("open");
      modal.setAttribute("aria-hidden", "true");
      modalImage.removeAttribute("src");
    }});
    modal.addEventListener("click", (event) => {{
      if (event.target === modal) byId("modalClose").click();
    }});
    document.addEventListener("keydown", (event) => {{
      if (event.key === "Escape") byId("modalClose").click();
    }});

    render();
  </script>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an HTML viewer for PPT run outputs.")
    parser.add_argument(
        "--presentations-dir",
        type=Path,
        default=Path("outputs") / DEFAULT_THREAD_ID / "presentations",
    )
    parser.add_argument("--out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    presentations_dir = args.presentations_dir.resolve()
    out = args.out.resolve() if args.out else presentations_dir / "ppt-run-viewer.html"
    data = build_data(presentations_dir, out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(data), encoding="utf-8")
    print(json.dumps({"html": str(out), "runs": len(data["runs"]), "latest": data["latestRunId"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
