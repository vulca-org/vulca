"""VULCA Layers — native layered artwork generation and editing."""
from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork
from vulca.layers.analyze import analyze_layers, parse_layer_response
from vulca.layers.split import crop_layer, chromakey_white, chromakey_black
from vulca.layers.composite import composite_layers
from vulca.layers.export import export_psd
from vulca.layers.generate import infer_bg_color, build_layer_prompt, generate_layer

__all__ = [
    "LayerInfo", "LayerResult", "LayeredArtwork",
    "analyze_layers", "parse_layer_response",
    "crop_layer", "chromakey_white", "chromakey_black",
    "composite_layers",
    "export_psd",
    "infer_bg_color", "build_layer_prompt", "generate_layer",
]
