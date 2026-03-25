"""10 Agents End-to-End VULCA Studio Test.

Each agent has a distinct persona, intent, and interaction pattern.
Runs through the full SDK pipeline (no stdin, no interactive UI).
Records observations for each phase and produces a summary report.
"""
from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

# Add vulca to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vulca" / "src"))

from vulca.studio.brief import Brief
from vulca.studio.session import StudioSession, SessionState
from vulca.studio.phases.intent import IntentPhase
from vulca.studio.phases.scout import ScoutPhase
from vulca.studio.phases.concept import ConceptPhase
from vulca.studio.phases.generate import GeneratePhase
from vulca.studio.phases.evaluate import EvaluatePhase
from vulca.studio.nl_update import parse_nl_update, parse_nl_update_llm, apply_update


@dataclass
class AgentPersona:
    name: str
    role: str
    language: str  # primary language of intent
    intent: str
    sketch_path: str = ""
    expected_traditions: list[str] = field(default_factory=list)
    expected_elements: list[str] = field(default_factory=list)
    expected_mood: str = ""
    expected_palette_keywords: list[str] = field(default_factory=list)
    update_instructions: list[str] = field(default_factory=list)
    concept_selection: int = 0  # 0-indexed
    concept_notes: str = ""


@dataclass
class PhaseObservation:
    phase: str
    fields_populated: list[str]
    fields_missing: list[str]
    issues: list[str]
    data: dict = field(default_factory=dict)


@dataclass
class AgentReport:
    agent: str
    role: str
    intent: str
    observations: list[PhaseObservation] = field(default_factory=list)
    brief_snapshot: dict = field(default_factory=dict)
    final_scores: dict = field(default_factory=dict)
    total_rounds: int = 0
    verdict: str = ""  # "success" | "partial" | "failure"
    pain_points: list[str] = field(default_factory=list)


# ── 10 Agent Personas ──

AGENTS: list[AgentPersona] = [
    AgentPersona(
        name="墨客 (Ink Master)",
        role="Professional Chinese ink wash painter, 20 years experience",
        language="zh",
        intent="一幅传统水墨山水画，远山含烟，近水有桥，留白三成，散点透视",
        expected_traditions=["chinese_xieyi"],
        expected_elements=["远山", "烟", "桥", "水"],
        expected_mood="serene",
        expected_palette_keywords=["ink", "black", "gray"],
        update_instructions=["墨色层次要更丰富，远山需要淡墨渲染"],
        concept_selection=2,
        concept_notes="留白再多一些",
    ),
    AgentPersona(
        name="Luna (Digital Beginner)",
        role="College student, first time using AI art tools",
        language="en",
        intent="a beautiful sunset over the ocean with warm colors",
        expected_traditions=[],
        expected_elements=["sunset", "ocean"],
        expected_mood="warm",
        expected_palette_keywords=["warm", "orange", "gold"],
        update_instructions=[],
        concept_selection=0,
    ),
    AgentPersona(
        name="赛博道人 (Cyber Taoist)",
        role="Cross-cultural digital artist specializing in east-west fusion",
        language="zh",
        intent="赛博朋克水墨山水，霓虹灯光与传统笔触的融合，暗色调底，亮色点缀",
        expected_traditions=["chinese_xieyi"],
        expected_elements=["霓虹灯", "山水", "笔触"],
        expected_mood="cyberpunk-mystical",
        expected_palette_keywords=["dark", "neon", "contrast"],
        update_instructions=["山的轮廓用传统皴法，但加入电路纹理", "背景的雾气改成数据流粒子效果"],
        concept_selection=2,
        concept_notes="赛博元素再多一些",
    ),
    AgentPersona(
        name="素描姐 (Sketch Sister)",
        role="Illustrator who always starts with pencil sketches",
        language="zh",
        intent="根据我的铅笔草图，转化为水彩风格的完成品，保持原始构图",
        sketch_path="experiments/test_sketch.png",  # Will create a placeholder
        expected_traditions=["watercolor"],
        expected_elements=["sketch composition"],
        expected_mood="",
        update_instructions=["水彩的晕染效果再自然一些"],
        concept_selection=1,
        concept_notes="保持我草图的构图",
    ),
    AgentPersona(
        name="Palette Queen",
        role="Color-obsessed digital painter",
        language="en",
        intent="abstract ocean painting in cold tones, deep navy blue and emerald green, high contrast",
        expected_traditions=[],
        expected_elements=["ocean"],
        expected_mood="cold",
        expected_palette_keywords=["navy", "emerald", "cold", "contrast"],
        update_instructions=["add more teal transitions between the blue and green"],
        concept_selection=3,
    ),
    AgentPersona(
        name="茶商 (Tea Merchant)",
        role="Commercial designer for tea brand packaging",
        language="zh",
        intent="中国风茶叶包装插画，需要竹子和茶壶元素，配色要典雅，竖版3:4比例",
        expected_traditions=["chinese_gongbi"],
        expected_elements=["竹子", "茶壶"],
        expected_mood="elegant",
        expected_palette_keywords=["elegant", "traditional"],
        update_instructions=["茶壶要放在画面中央偏下的位置"],
        concept_selection=0,
        concept_notes="竹子要更突出",
    ),
    AgentPersona(
        name="Dr. VULCA (Researcher)",
        role="Academic researcher testing VULCA evaluation",
        language="en",
        intent="evaluate a chinese xieyi landscape painting for cultural fidelity",
        expected_traditions=["chinese_xieyi"],
        expected_elements=[],
        expected_mood="",
        update_instructions=[],
        concept_selection=0,
    ),
    AgentPersona(
        name="浮世绘子 (Ukiyo-e Ko)",
        role="Japanese art enthusiast creating modern ukiyo-e",
        language="zh",
        intent="浮世绘风格的现代东京夜景，要有东京塔和樱花，名所绘构图",
        expected_traditions=["japanese_traditional"],
        expected_elements=["东京塔", "樱花"],
        expected_mood="nostalgic-modern",
        expected_palette_keywords=["traditional japanese"],
        update_instructions=["前景加入一个穿和服的人物剪影"],
        concept_selection=1,
        concept_notes="东京塔要更突出",
    ),
    AgentPersona(
        name="Geo (Geometric Artist)",
        role="Islamic geometric pattern specialist",
        language="en",
        intent="Islamic geometric pattern with 8-fold rotational symmetry, blue and gold color scheme, high precision",
        expected_traditions=["islamic_geometric"],
        expected_elements=["8-fold symmetry"],
        expected_mood="",
        expected_palette_keywords=["blue", "gold"],
        update_instructions=["make the central star more prominent"],
        concept_selection=0,
    ),
    AgentPersona(
        name="江南客 (Jiangnan Guest)",
        role="Chinese-speaking amateur painter",
        language="zh",
        intent="画一幅春天桃花盛开的江南水乡，小桥流水人家，要有诗意",
        expected_traditions=["chinese_xieyi"],
        expected_elements=["桃花", "小桥", "流水", "人家"],
        expected_mood="poetic-spring",
        expected_palette_keywords=["pink", "green", "spring"],
        update_instructions=["远处加一座宝塔", "整体色调再暖一点"],
        concept_selection=2,
        concept_notes="桃花再多一些",
    ),
]


def check_brief_fields(brief: Brief, expected: AgentPersona) -> PhaseObservation:
    """Check which Brief fields are populated vs expected."""
    populated = []
    missing = []
    issues = []

    # Check tradition detection
    detected_traditions = [s.tradition for s in brief.style_mix if s.tradition]
    detected_tags = [s.tag for s in brief.style_mix if s.tag]

    if detected_traditions or detected_tags:
        populated.append(f"style_mix: {detected_traditions + detected_tags}")
    else:
        missing.append("style_mix (no tradition or tag detected)")

    for exp_t in expected.expected_traditions:
        if exp_t not in detected_traditions:
            issues.append(f"Expected tradition '{exp_t}' not detected")

    # Check other fields
    field_checks = [
        ("mood", brief.mood),
        ("composition.layout", brief.composition.layout),
        ("composition.focal_point", brief.composition.focal_point),
        ("palette.primary", brief.palette.primary),
        ("palette.mood", brief.palette.mood),
        ("elements", brief.elements),
        ("must_have", brief.must_have),
        ("must_avoid", brief.must_avoid),
        ("user_sketch", brief.user_sketch),
    ]

    for name, value in field_checks:
        if value:
            populated.append(f"{name}: {value}")
        else:
            missing.append(name)

    # Check if expected elements were captured
    element_names = [e.name for e in brief.elements]
    for exp_e in expected.expected_elements:
        if not any(exp_e.lower() in en.lower() for en in element_names):
            issues.append(f"Expected element '{exp_e}' not in Brief.elements")

    return PhaseObservation(
        phase="intent",
        fields_populated=populated,
        fields_missing=missing,
        issues=issues,
        data={
            "detected_traditions": detected_traditions,
            "detected_tags": detected_tags,
            "mood": brief.mood,
            "elements_count": len(brief.elements),
        },
    )


async def run_agent(persona: AgentPersona, output_dir: Path) -> AgentReport:
    """Run a single agent through the full Studio pipeline."""
    report = AgentReport(
        agent=persona.name,
        role=persona.role,
        intent=persona.intent,
    )

    project_dir = output_dir / persona.name.split("(")[0].strip().replace(" ", "_")
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create session
    session = StudioSession.new(persona.intent, project_dir=str(project_dir))

    # ── Phase 1: INTENT ──
    intent_phase = IntentPhase()
    await intent_phase.parse_intent_llm(session.brief)

    # Set sketch if provided
    if persona.sketch_path:
        sketch_file = Path(persona.sketch_path)
        if not sketch_file.exists():
            sketch_file.parent.mkdir(parents=True, exist_ok=True)
            sketch_file.write_bytes(b"placeholder_sketch")
        intent_phase.set_sketch(session.brief, persona.sketch_path)

    # Generate and apply questions (simulate answering first option for mood/brush)
    questions = intent_phase.generate_questions(session.brief)
    for q in questions:
        if q["options"]:
            intent_phase.apply_answer(session.brief, q, q["options"][0])

    # Check intent phase results
    intent_obs = check_brief_fields(session.brief, persona)
    report.observations.append(intent_obs)

    # ── Scout ──
    scout_phase = ScoutPhase()
    scout_obs = PhaseObservation(phase="scout", fields_populated=[], fields_missing=[], issues=[])
    try:
        refs = await scout_phase.generate_references(
            session.brief, provider="mock", project_dir=str(project_dir)
        )
        scout_obs.fields_populated.append(f"references: {len(refs)} generated")
        scout_obs.data["reference_count"] = len(refs)
    except Exception as e:
        scout_obs.issues.append(f"Scout failed: {e}")
        scout_obs.data["reference_count"] = 0
    report.observations.append(scout_obs)

    session.advance_to(SessionState.CONCEPT)

    # ── Phase 2: CONCEPT ──
    concept_phase = ConceptPhase()
    concept_obs = PhaseObservation(phase="concept", fields_populated=[], fields_missing=[], issues=[])

    # Check concept prompt
    concept_prompt = concept_phase.build_concept_prompt(session.brief)
    concept_obs.data["prompt_length"] = len(concept_prompt)
    concept_obs.data["prompt_preview"] = concept_prompt[:200]

    # Check what's in the prompt vs what should be
    for exp_e in persona.expected_elements:
        if exp_e.lower() not in concept_prompt.lower():
            concept_obs.issues.append(f"Expected element '{exp_e}' missing from concept prompt")

    # Check palette: Brief should have palette info populated (not checking exact keywords
    # since LLM may return Chinese or different English terms)
    if persona.expected_palette_keywords:
        has_palette = bool(session.brief.palette.mood or session.brief.palette.primary)
        if not has_palette:
            concept_obs.issues.append(
                f"Expected palette info but Brief.palette is empty "
                f"(expected keywords: {persona.expected_palette_keywords})"
            )

    # Generate concepts
    paths = await concept_phase.generate_concepts(
        session.brief, count=4, provider="mock", project_dir=str(project_dir)
    )
    concept_obs.fields_populated.append(f"concepts: {len(paths)} generated")

    # Select concept
    idx = min(persona.concept_selection, len(paths) - 1)
    concept_phase.select(session.brief, index=idx, notes=persona.concept_notes)
    concept_obs.fields_populated.append(f"selected: #{idx + 1}, notes: '{persona.concept_notes}'")

    report.observations.append(concept_obs)
    session.advance_to(SessionState.GENERATE)

    # ── Phase 3+4: GENERATE + EVALUATE (with updates) ──
    gen_phase = GeneratePhase()
    eval_phase = EvaluatePhase()

    total_rounds = 0
    all_scores = []

    # First generation
    result_path = await gen_phase.generate(
        session.brief, provider="mock", project_dir=str(project_dir)
    )
    session.advance_to(SessionState.EVALUATE)
    scores = await eval_phase.evaluate(session.brief, image_path=result_path, mock=True)
    total_rounds += 1
    all_scores.append({"round": total_rounds, "scores": dict(scores)})

    # Record generation prompt
    gen_prompt = gen_phase.build_prompt(session.brief)
    gen_obs = PhaseObservation(
        phase="generate_r1",
        fields_populated=[f"prompt_length: {len(gen_prompt)}"],
        fields_missing=[],
        issues=[],
        data={
            "prompt_preview": gen_prompt[:300],
            "scores": dict(scores),
        },
    )

    # Check generate prompt completeness
    for exp_e in persona.expected_elements:
        if exp_e.lower() not in gen_prompt.lower():
            gen_obs.issues.append(f"Expected element '{exp_e}' missing from generate prompt")

    report.observations.append(gen_obs)

    # Apply NL updates
    for instruction in persona.update_instructions:
        nl_result = await parse_nl_update_llm(instruction, session.brief)
        apply_update(session.brief, nl_result)

        update_obs = PhaseObservation(
            phase=f"update_{total_rounds}",
            fields_populated=[f"instruction: '{instruction}'"],
            fields_missing=[],
            issues=[],
            data={
                "parsed_fields": list(nl_result.field_updates.keys()),
                "rollback_to": nl_result.rollback_to.value,
                "confidence": nl_result.confidence,
                "explanation": nl_result.explanation,
            },
        )

        # Check if update was meaningful
        if nl_result.confidence < 0.5:
            update_obs.issues.append(f"Low confidence: {nl_result.confidence}")
        if "composition" in nl_result.field_updates and nl_result.field_updates["composition"] == instruction:
            update_obs.issues.append("Fallback: entire instruction stored as composition (no real parsing)")

        report.observations.append(update_obs)

        # Regenerate after update
        session.rollback_to(SessionState.GENERATE)
        result_path = await gen_phase.generate(
            session.brief, provider="mock", project_dir=str(project_dir)
        )
        session.rollback_to(SessionState.EVALUATE)
        scores = await eval_phase.evaluate(session.brief, image_path=result_path, mock=True)
        total_rounds += 1
        all_scores.append({"round": total_rounds, "scores": dict(scores)})

    # Final evaluation observation
    eval_obs = PhaseObservation(
        phase="evaluate_final",
        fields_populated=[],
        fields_missing=[],
        issues=[],
        data={
            "final_scores": dict(scores),
            "all_rounds": all_scores,
            "total_rounds": total_rounds,
            "scores_changed": len(set(json.dumps(s["scores"]) for s in all_scores)) > 1,
        },
    )

    # Check if scores changed across rounds
    if not eval_obs.data["scores_changed"]:
        eval_obs.issues.append("CRITICAL: Scores identical across all rounds — no feedback variation")

    # Check if eval criteria were generated
    if session.brief.eval_criteria:
        eval_obs.fields_populated.append(f"eval_criteria: {list(session.brief.eval_criteria.keys())}")
    else:
        eval_obs.issues.append("eval_criteria never generated")

    report.observations.append(eval_obs)

    # ── Finalize ──
    report.total_rounds = total_rounds
    report.final_scores = dict(scores)
    report.brief_snapshot = {
        "intent": session.brief.intent,
        "mood": session.brief.mood,
        "style_mix": [{"t": s.tradition, "tag": s.tag, "w": s.weight} for s in session.brief.style_mix],
        "composition": {"layout": session.brief.composition.layout, "focal": session.brief.composition.focal_point},
        "palette": {"primary": session.brief.palette.primary, "mood": session.brief.palette.mood},
        "elements": [e.name for e in session.brief.elements],
        "must_have": session.brief.must_have,
        "must_avoid": session.brief.must_avoid,
        "user_sketch": session.brief.user_sketch,
        "eval_criteria": session.brief.eval_criteria,
        "concept_notes": session.brief.concept_notes,
        "updates": [u.instruction for u in session.brief.updates],
        "total_generations": len(session.brief.generations),
    }

    # Calculate verdict
    all_issues = []
    for obs in report.observations:
        all_issues.extend(obs.issues)

    critical_issues = [i for i in all_issues if "CRITICAL" in i or "Expected" in i]
    if len(critical_issues) >= 3:
        report.verdict = "failure"
    elif len(critical_issues) >= 1:
        report.verdict = "partial"
    else:
        report.verdict = "success"

    # Compile pain points
    for obs in report.observations:
        for issue in obs.issues:
            if issue not in report.pain_points:
                report.pain_points.append(issue)

    session.save()
    return report


def print_report(report: AgentReport) -> None:
    """Pretty-print a single agent report."""
    verdict_icon = {"success": "✅", "partial": "⚠️", "failure": "❌"}[report.verdict]
    print(f"\n{'='*70}")
    print(f"{verdict_icon}  {report.agent} ({report.role})")
    print(f"   Intent: {report.intent[:60]}...")
    print(f"   Rounds: {report.total_rounds} | Verdict: {report.verdict}")
    print(f"   Final scores: {report.final_scores}")

    # Brief completeness
    snap = report.brief_snapshot
    filled = sum(1 for v in [
        snap["mood"], snap["style_mix"], snap["composition"]["layout"],
        snap["palette"]["primary"], snap["palette"]["mood"],
        snap["elements"], snap["must_have"], snap["must_avoid"],
        snap["user_sketch"], snap["eval_criteria"],
    ] if v)
    print(f"   Brief fields filled: {filled}/10")

    # Issues
    if report.pain_points:
        print(f"   Issues ({len(report.pain_points)}):")
        for i, p in enumerate(report.pain_points[:5], 1):
            print(f"     {i}. {p}")
        if len(report.pain_points) > 5:
            print(f"     ... and {len(report.pain_points) - 5} more")


def print_summary(reports: list[AgentReport]) -> None:
    """Print aggregate summary across all agents."""
    print(f"\n{'='*70}")
    print("AGGREGATE SUMMARY")
    print(f"{'='*70}")

    # Verdicts
    verdicts = [r.verdict for r in reports]
    print(f"\nVerdicts: ✅ {verdicts.count('success')} | ⚠️ {verdicts.count('partial')} | ❌ {verdicts.count('failure')}")

    # Brief completeness
    completeness = []
    for r in reports:
        snap = r.brief_snapshot
        filled = sum(1 for v in [
            snap["mood"], snap["style_mix"], snap["composition"]["layout"],
            snap["palette"]["primary"], snap["palette"]["mood"],
            snap["elements"], snap["must_have"], snap["must_avoid"],
            snap["user_sketch"], snap["eval_criteria"],
        ] if v)
        completeness.append(filled)
    avg_comp = sum(completeness) / len(completeness)
    print(f"Brief completeness: avg {avg_comp:.1f}/10 (range {min(completeness)}-{max(completeness)})")

    # Tradition detection
    tradition_detected = sum(1 for r in reports if r.brief_snapshot["style_mix"])
    print(f"Tradition detected: {tradition_detected}/{len(reports)}")

    # Score variation
    scores_varied = sum(
        1 for r in reports
        for obs in r.observations
        if obs.phase == "evaluate_final" and obs.data.get("scores_changed")
    )
    print(f"Scores varied across rounds: {scores_varied}/{len(reports)}")

    # Common issues
    all_issues: dict[str, int] = {}
    for r in reports:
        for p in r.pain_points:
            # Normalize similar issues
            key = p.split("'")[0] if "'" in p else p[:50]
            all_issues[key] = all_issues.get(key, 0) + 1

    print(f"\nTop issues (across {len(reports)} agents):")
    sorted_issues = sorted(all_issues.items(), key=lambda x: -x[1])
    for issue, count in sorted_issues[:10]:
        print(f"  [{count}/{len(reports)}] {issue}")

    # Element capture rate
    total_expected = sum(len(a.expected_elements) for a in AGENTS)
    total_captured = 0
    for r, a in zip(reports, AGENTS):
        elements_in_brief = r.brief_snapshot.get("elements", [])
        for exp in a.expected_elements:
            if any(exp.lower() in e.lower() for e in elements_in_brief):
                total_captured += 1
    print(f"\nExpected elements captured in Brief: {total_captured}/{total_expected}")

    # NL update parsing quality
    total_updates = sum(len(a.update_instructions) for a in AGENTS)
    fallback_updates = sum(
        1 for r in reports
        for obs in r.observations
        if obs.phase.startswith("update_") and any("Fallback" in i for i in obs.issues)
    )
    print(f"NL updates: {total_updates} total, {fallback_updates} fell back to raw composition storage")


async def main():
    output_dir = Path("experiments/ten_agents_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("VULCA Studio — 10 Agent End-to-End Test")
    print(f"Output: {output_dir}/\n")

    reports: list[AgentReport] = []
    for i, persona in enumerate(AGENTS, 1):
        print(f"[{i}/10] Running {persona.name}...", end=" ", flush=True)
        try:
            report = await run_agent(persona, output_dir)
            reports.append(report)
            print(f"{report.verdict} ({len(report.pain_points)} issues)")
        except Exception as e:
            print(f"CRASH: {e}")
            reports.append(AgentReport(
                agent=persona.name, role=persona.role, intent=persona.intent,
                verdict="failure", pain_points=[f"CRASH: {e}"],
            ))

    # Print individual reports
    for report in reports:
        print_report(report)

    # Print aggregate summary
    print_summary(reports)

    # Save full report as JSON
    report_path = output_dir / "report.json"
    report_path.write_text(
        json.dumps([asdict(r) for r in reports], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nFull report saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
