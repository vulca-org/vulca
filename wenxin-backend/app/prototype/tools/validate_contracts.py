"""Cross-module contract validation — prevents implicit contract drift.

Checks that cross-file data contracts remain consistent after code changes.
Run after any modification to catch the class of bugs that caused R14/R15
audit regressions (sentinel mismatches, mask_hints drift, action set drift).

Usage:
    python -m app.prototype.tools.validate_contracts
"""

from __future__ import annotations

import ast
import inspect
import re
import sys
from pathlib import Path

passed = 0
failed = 0


def check(label: str, condition: bool) -> None:
    global passed, failed
    if condition:
        print(f"  [PASS] {label}")
        passed += 1
    else:
        print(f"  [FAIL] {label}")
        failed += 1


# ─────────────────────────────────────────────────────────────
# Contract 1: mask_hints values ⊆ MaskGenerator._STRATEGIES values
# ─────────────────────────────────────────────────────────────

def test_mask_hints_subset_of_strategies() -> None:
    """critic_llm mask_hints values must be valid MaskGenerator strategies."""
    print("\n=== Contract 1: mask_hints ⊆ _STRATEGIES ===")

    from app.prototype.agents.critic_llm import CriticLLM
    from app.prototype.agents.inpaint_provider import MaskGenerator

    # Extract mask_hints from critic_llm source
    src = inspect.getsource(CriticLLM)
    match = re.search(r'mask_hints\s*=\s*\{([^}]+)\}', src)
    assert match, "Could not find mask_hints dict in CriticLLM"
    hint_values = set(re.findall(r'"(\w+)"', match.group(1)))
    # Filter to only values (not keys like L1-L5)
    keys_in_hints = {"L1", "L2", "L3", "L4", "L5"}
    hint_values -= keys_in_hints

    strategies = set(MaskGenerator._STRATEGIES.values())

    check("mask_hints values are subset of _STRATEGIES",
          hint_values.issubset(strategies))
    if not hint_values.issubset(strategies):
        print(f"    Missing: {hint_values - strategies}")


# ─────────────────────────────────────────────────────────────
# Contract 2: AgentResult.score is Optional[float], consumers use `is None`
# ─────────────────────────────────────────────────────────────

def test_score_sentinel_consumers() -> None:
    """All AgentResult.score consumers must use `is None`/`is not None`."""
    print("\n=== Contract 2: score sentinel (Optional[float]) ===")

    from app.prototype.agents.agent_runtime import AgentResult

    # Verify type
    import dataclasses
    fields = {f.name: f for f in dataclasses.fields(AgentResult)}
    score_field = fields["score"]
    check("AgentResult.score default is None", score_field.default is None)

    # Grep for old-style sentinel checks
    proto_root = Path(__file__).resolve().parent.parent
    bad_patterns = [
        re.compile(r'\.score\s*[<>]=?\s*0'),       # score < 0, score <= 0, score > 0, score >= 0
        re.compile(r'\.score\s*==\s*-1'),            # score == -1
        re.compile(r'\.score\s*!=\s*-1'),            # score != -1
    ]

    violations = []
    for py_file in proto_root.rglob("*.py"):
        if "validate_contracts" in py_file.name:
            continue
        content = py_file.read_text(encoding="utf-8")
        for i, line in enumerate(content.splitlines(), 1):
            if "agent_result.score" in line or "result.score" in line:
                for pat in bad_patterns:
                    if pat.search(line):
                        violations.append(f"    {py_file.name}:{i}: {line.strip()}")

    check("No old-style sentinel checks (< 0 / > 0 / == -1)", len(violations) == 0)
    for v in violations:
        print(v)


# ─────────────────────────────────────────────────────────────
# Contract 3: Queen action set consistency
# ─────────────────────────────────────────────────────────────

def test_queen_action_set() -> None:
    """QueenDecision action annotation matches actual produced actions."""
    print("\n=== Contract 3: Queen action set ===")

    from app.prototype.agents.queen_agent import QueenAgent
    src = inspect.getsource(QueenAgent)

    # Find all action= assignments
    produced = set(re.findall(r'action="(\w+)"', src))
    expected = {"accept", "rerun", "stop"}

    check("Queen produces only accept/rerun/stop", produced == expected)
    if produced != expected:
        print(f"    Produced: {produced}, Expected: {expected}")

    # Check no downgrade references
    check("No 'downgrade' in queen_agent.py", "downgrade" not in src.lower())


# ─────────────────────────────────────────────────────────────
# Contract 4: taboo protection threshold consistency
# ─────────────────────────────────────────────────────────────

def test_taboo_threshold_consistent() -> None:
    """All taboo protection guards use the same <= 0.3 threshold."""
    print("\n=== Contract 4: taboo protection threshold ===")

    proto_root = Path(__file__).resolve().parent.parent
    taboo_guards = []

    for py_file in proto_root.rglob("*.py"):
        if py_file.name.startswith("validate_"):
            continue
        content = py_file.read_text(encoding="utf-8")
        for i, line in enumerate(content.splitlines(), 1):
            # Match patterns like: rule_score <= 0.3, old <= 0.3 (in taboo context)
            if "critical_interpretation" in line or ("L4" in line and "taboo" in content[max(0, content.find(line)-200):content.find(line)+200]):
                if re.search(r'<=\s*0\.\d', line):
                    threshold = re.search(r'<=\s*(0\.\d+)', line)
                    if threshold:
                        taboo_guards.append((py_file.name, i, threshold.group(1)))

    thresholds = set(t[2] for t in taboo_guards)
    check(f"All taboo guards use same threshold (found {len(taboo_guards)} guards)",
          len(thresholds) <= 1)
    if len(thresholds) > 1:
        for name, line, thresh in taboo_guards:
            print(f"    {name}:{line} uses {thresh}")


# ─────────────────────────────────────────────────────────────
# Contract 5: FixItPlan.strength flows through to MaskGenerator
# ─────────────────────────────────────────────────────────────

def test_fix_it_plan_strength_chain() -> None:
    """FixItem.strength field exists and is consumed by draft_agent."""
    print("\n=== Contract 5: FixItPlan.strength chain ===")

    from app.prototype.agents.fix_it_plan import FixItem
    import dataclasses

    fields = {f.name: f for f in dataclasses.fields(FixItem)}
    check("FixItem has 'strength' field", "strength" in fields)
    check("FixItem.strength default is 1.0", fields["strength"].default == 1.0)

    # Verify draft_agent consumes it
    draft_src = (Path(__file__).resolve().parent.parent / "agents" / "draft_agent.py").read_text()
    check("draft_agent reads item.strength", "item.strength" in draft_src)


# ─────────────────────────────────────────────────────────────
# Contract 6: preserve_dimensions end-to-end chain
# ─────────────────────────────────────────────────────────────

def test_preserve_dimensions_chain() -> None:
    """preserve_dimensions flows: Queen → orchestrator → draft → MaskGenerator."""
    print("\n=== Contract 6: preserve_dimensions chain ===")

    from app.prototype.agents.queen_types import QueenDecision
    import dataclasses

    fields = {f.name: f for f in dataclasses.fields(QueenDecision)}
    check("QueenDecision has 'preserve_dimensions'", "preserve_dimensions" in fields)

    # Check orchestrator passes it
    orch_src = (Path(__file__).resolve().parent.parent / "orchestrator" / "orchestrator.py").read_text()
    check("orchestrator reads preserve_dimensions",
          "preserve_dimensions" in orch_src)

    # Check draft_agent accepts it
    draft_src = (Path(__file__).resolve().parent.parent / "agents" / "draft_agent.py").read_text()
    check("draft_agent.rerun_with_fix has preserve_layers param",
          "preserve_layers" in draft_src)
    check("draft_agent.refine_candidate passes preserve_layers",
          "preserve_layers" in draft_src and "local_rerun_request" in draft_src)

    # Check MaskGenerator accepts it
    from app.prototype.agents.inpaint_provider import MaskGenerator
    sig = inspect.signature(MaskGenerator.generate)
    check("MaskGenerator.generate has preserve_layers param",
          "preserve_layers" in sig.parameters)


# ─────────────────────────────────────────────────────────────
# Contract 7: _LAYER_LABELS uniqueness
# ─────────────────────────────────────────────────────────────

def test_layer_labels_unique() -> None:
    """Only one _LAYER_LABELS definition exists in critic_llm.py."""
    print("\n=== Contract 7: _LAYER_LABELS uniqueness ===")

    src = (Path(__file__).resolve().parent.parent / "agents" / "critic_llm.py").read_text()
    occurrences = [m.start() for m in re.finditer(r'^_LAYER_LABELS\s*[:=]', src, re.MULTILINE)]
    check("Exactly one _LAYER_LABELS definition", len(occurrences) == 1)


# ─────────────────────────────────────────────────────────────
# Contract 8: No zombie concepts
# ─────────────────────────────────────────────────────────────

def test_no_zombie_concepts() -> None:
    """Verify removed concepts don't reappear."""
    print("\n=== Contract 8: No zombie concepts ===")

    proto_root = Path(__file__).resolve().parent.parent
    zombies = {
        "downgrade_at_cost_pct": 0,
        "downgrade_params": 0,
        "rerun_global": 0,
    }

    for py_file in proto_root.rglob("*.py"):
        if py_file.name.startswith("validate_"):
            continue
        content = py_file.read_text(encoding="utf-8")
        for zombie in zombies:
            if zombie in content:
                zombies[zombie] += 1

    for zombie, count in zombies.items():
        check(f"No '{zombie}' in production code", count == 0)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Cross-Module Contract Validation")
    print("=" * 60)

    test_mask_hints_subset_of_strategies()
    test_score_sentinel_consumers()
    test_queen_action_set()
    test_taboo_threshold_consistent()
    test_fix_it_plan_strength_chain()
    test_preserve_dimensions_chain()
    test_layer_labels_unique()
    test_no_zombie_concepts()

    print(f"\n{'=' * 60}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")
    sys.exit(1 if failed else 0)
