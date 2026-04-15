"""Phase 0 Task 9: parse_prompt_entry — 2/3-tuple tolerant."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts"))
from evfsam_showcase import parse_prompt_entry  # noqa: E402


def test_parse_two_element_tuple_defaults_semantic_path_to_name():
    name, prompt, path = parse_prompt_entry(["bg", "the sky"])
    assert name == "bg"
    assert prompt == "the sky"
    assert path == "bg"


def test_parse_three_element_tuple_uses_explicit_path():
    name, prompt, path = parse_prompt_entry(["bg", "the sky", "background.sky"])
    assert name == "bg"
    assert prompt == "the sky"
    assert path == "background.sky"


def test_parse_rejects_short_tuple():
    with pytest.raises(ValueError):
        parse_prompt_entry(["bg"])


def test_parse_tolerates_tuple_input():
    """Input can be list or tuple (JSON loader yields lists; in-memory code uses tuples)."""
    name, prompt, path = parse_prompt_entry(("bg", "sky"))
    assert (name, prompt, path) == ("bg", "sky", "bg")


def test_site_b_passes_3tuple_through_without_crash():
    """Regression: Site B's `for n, p in prompts_cfg[stem]` crashes with
    'too many values to unpack' on 3-tuple JSON entries. Fix: route through
    parse_prompt_entry so 3-tuple entries produce 3-tuple output.

    We can't exec main() (it loads EVF-SAM), so we replicate Site B's
    logic and verify it survives a 3-tuple."""
    # Simulate Site B logic: after the fix, it must NOT use 2-tuple destructure
    cfg_3tuple = [["bg", "sky", "background.sky"]]

    # Old broken form: `[(n, p) for n, p in cfg]` raises ValueError.
    # New form must survive and either pass the 3-tuple through OR at least
    # not crash.
    import evfsam_showcase
    # Use the module's own helper — parse_prompt_entry is the canonical
    # normalization, Site B after the fix must use it.
    normalized = [tuple(evfsam_showcase.parse_prompt_entry(e)) for e in cfg_3tuple]
    assert len(normalized[0]) == 3
    assert normalized[0] == ("bg", "sky", "background.sky")

    # Source-inspection contract: Site B must not use the 2-tuple destructure
    # pattern that caused the bug.
    src = Path(evfsam_showcase.__file__).read_text()
    assert "for n, p in prompts_cfg[stem]" not in src, (
        "Site B still uses `for n, p in prompts_cfg[stem]` which crashes on "
        "3-tuple entries. Route through parse_prompt_entry instead."
    )


def test_cli_flag_name_disambiguated_from_core_cli():
    """`src/vulca/cli.py` defines `--semantic-path <value>` (Task 4b).
    evfsam_showcase.py's log-only boolean must rename to `--show-semantic-path`
    to avoid same-name / different-semantics collision."""
    import evfsam_showcase
    src = Path(evfsam_showcase.__file__).read_text()
    assert '"--show-semantic-path"' in src, (
        "evfsam_showcase.py must rename its boolean --semantic-path flag to "
        "--show-semantic-path to disambiguate from src/vulca/cli.py's value flag"
    )
    # And the old name must be gone to prevent silent double-definition
    assert '"--semantic-path"' not in src
