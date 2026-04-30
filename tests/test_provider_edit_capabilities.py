from vulca.providers.base import ImageEditCapabilities
from vulca.providers.openai_provider import OpenAIImageProvider


def test_image_edit_capabilities_defaults_are_conservative():
    caps = ImageEditCapabilities()
    assert caps.supports_edits is False
    assert caps.requires_mask_for_edits is True
    assert caps.supports_unmasked_edits is False
    assert caps.supports_masked_edits is False
    assert caps.supports_input_fidelity is False


def test_openai_gpt_image_2_requires_mask_for_edits():
    provider = OpenAIImageProvider(api_key="sk-test", model="gpt-image-2")
    caps = provider.edit_capabilities()
    assert caps.supports_edits is True
    assert caps.supports_masked_edits is True
    assert caps.requires_mask_for_edits is True
    assert caps.supports_unmasked_edits is False
    assert caps.supports_input_fidelity is False


def test_openai_gpt_image_1_preserves_existing_unmasked_behavior():
    provider = OpenAIImageProvider(api_key="sk-test", model="gpt-image-1")
    caps = provider.edit_capabilities()
    assert caps.supports_edits is True
    assert caps.supports_masked_edits is True
    assert caps.requires_mask_for_edits is False
    assert caps.supports_unmasked_edits is True
