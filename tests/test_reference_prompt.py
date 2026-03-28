from vulca.studio.phases.concept import ConceptPhase
from vulca.studio.brief import Brief


class TestReferencePromptInjection:
    def test_style_reference_prompt(self):
        b = Brief.new("test")
        b.reference_path = "/fake/ref.jpg"
        b.reference_type = "style"
        phase = ConceptPhase()
        prompt = phase.build_concept_prompt(b)
        assert "style" in prompt.lower()
        assert "color palette" in prompt.lower() or "brushwork" in prompt.lower()

    def test_composition_reference_prompt(self):
        b = Brief.new("test")
        b.reference_path = "/fake/ref.jpg"
        b.reference_type = "composition"
        phase = ConceptPhase()
        prompt = phase.build_concept_prompt(b)
        assert "composition" in prompt.lower() or "layout" in prompt.lower()

    def test_full_reference_prompt(self):
        b = Brief.new("test")
        b.reference_path = "/fake/ref.jpg"
        b.reference_type = "full"
        phase = ConceptPhase()
        prompt = phase.build_concept_prompt(b)
        assert "style" in prompt.lower() and ("composition" in prompt.lower() or "layout" in prompt.lower())

    def test_no_reference_no_injection(self):
        b = Brief.new("test")
        phase = ConceptPhase()
        prompt = phase.build_concept_prompt(b)
        assert "reference image" not in prompt.lower() or "reference sketch" not in prompt.lower()
