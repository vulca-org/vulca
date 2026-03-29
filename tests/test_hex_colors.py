import sys
sys.path.insert(0, 'vulca/src')

from vulca.studio.brief import Brief
from vulca.studio.phases.concept import ConceptPhase
from vulca.studio.nl_update import parse_nl_update, apply_update


class TestHexColorInput:
    def test_palette_accepts_hex_values(self):
        b = Brief.new("test")
        b.palette.primary = ["#C87F4A", "#5F8A50"]
        assert b.palette.primary == ["#C87F4A", "#5F8A50"]

    def test_prompt_includes_hex_colors(self):
        b = Brief.new("test poster")
        b.palette.primary = ["#C87F4A", "#5F8A50"]
        b.palette.accent = ["#B8923D"]
        phase = ConceptPhase()
        prompt = phase.build_concept_prompt(b)
        assert "#C87F4A" in prompt
        assert "#5F8A50" in prompt
        assert "#B8923D" in prompt

    def test_prompt_has_strict_color_instruction(self):
        b = Brief.new("test poster")
        b.palette.primary = ["#FF0000"]
        phase = ConceptPhase()
        prompt = phase.build_concept_prompt(b)
        assert "must use" in prompt.lower() or "strictly" in prompt.lower() or "exact" in prompt.lower()

    def test_nl_update_parses_hex_colors(self):
        b = Brief.new("test")
        result = parse_nl_update("use colors #C87F4A and #5F8A50 as primary palette", b)
        apply_update(b, result)
        # Should have extracted hex colors into palette
        all_text = str(result.field_updates)
        assert "#C87F4A" in all_text or "#C87F4A".lower() in str(b.palette.primary).lower()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
