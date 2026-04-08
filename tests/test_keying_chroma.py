import numpy as np
from vulca.layers.keying import CanvasSpec
from vulca.layers.keying.chroma import ChromaKeying, DeltaEKeying

def _img(rgb):
    return np.full((4, 4, 3), rgb, dtype=np.uint8)

def test_chroma_pure_canvas_color_alpha_zero():
    canvas = CanvasSpec(color=(245, 230, 200))
    alpha = ChromaKeying().extract_alpha(_img((245, 230, 200)), canvas)
    assert (alpha < 0.05).all()

def test_chroma_distant_color_alpha_high():
    canvas = CanvasSpec(color=(245, 230, 200))
    alpha = ChromaKeying().extract_alpha(_img((20, 20, 200)), canvas)
    assert (alpha > 0.5).all()

def test_chroma_near_color_alpha_partial():
    canvas = CanvasSpec(color=(245, 230, 200))
    alpha = ChromaKeying().extract_alpha(_img((230, 215, 185)), canvas)
    assert 0.0 < alpha.mean() < 0.4

def test_delta_e_uses_perceptual_distance():
    canvas = CanvasSpec(color=(128, 128, 128))
    a_chroma = ChromaKeying().extract_alpha(_img((128, 200, 128)), canvas)
    a_delta_e = DeltaEKeying().extract_alpha(_img((128, 200, 128)), canvas)
    assert a_chroma.mean() > 0.1
    assert a_delta_e.mean() > 0.1
