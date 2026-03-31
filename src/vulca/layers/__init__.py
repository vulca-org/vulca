"""VULCA Layers — native layered artwork generation and editing (V2)."""
from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork
from vulca.layers.analyze import analyze_layers, parse_layer_response
from vulca.layers.split import split_extract, split_regenerate, crop_layer, chromakey_white, chromakey_black
from vulca.layers.composite import composite_layers
from vulca.layers.blend import blend_normal, blend_screen, blend_multiply, blend_layers
from vulca.layers.export import export_psd
from vulca.layers.manifest import write_manifest as write_manifest_v2, load_manifest, MANIFEST_VERSION
from vulca.layers.mask import build_color_mask, apply_mask_to_image
from vulca.layers.prompt import build_analyze_prompt, build_regeneration_prompt, parse_v2_response
from vulca.layers.redraw import redraw_layer, redraw_merged
from vulca.layers.regenerate import build_regenerate_prompt, regenerate_from_composite

# V1 compat re-exports
from vulca.layers.manifest import load_manifest as load_artwork

__all__ = [
    "LayerInfo", "LayerResult", "LayeredArtwork",
    "analyze_layers", "parse_layer_response",
    "split_extract", "split_regenerate",
    "crop_layer", "chromakey_white", "chromakey_black",
    "composite_layers",
    "blend_normal", "blend_screen", "blend_multiply", "blend_layers",
    "export_psd",
    "write_manifest_v2", "load_manifest", "MANIFEST_VERSION",
    "build_color_mask", "apply_mask_to_image",
    "build_analyze_prompt", "build_regeneration_prompt", "parse_v2_response",
    "redraw_layer", "redraw_merged",
    "build_regenerate_prompt", "regenerate_from_composite",
    "load_artwork",
]
