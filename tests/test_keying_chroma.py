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

def test_chroma_operates_in_linear_rgb_not_srgb():
    """v0.13.1 NTH #1: ChromaKeying must linearize before computing distance.

    Gamma amplifies mid-gray differences in sRGB bytes. If we used raw
    sRGB bytes, (128,128,128) vs (160,160,160) would look closer than
    (10,10,10) vs (42,42,42) relative to a black canvas because byte
    distances are identical (32) but linear-RGB distances differ by ~3x
    because of the gamma curve.
    """
    canvas = CanvasSpec(color=(0, 0, 0))
    dark_pair = ChromaKeying().extract_alpha(_img((42, 42, 42)), canvas)
    mid_pair = ChromaKeying().extract_alpha(_img((160, 160, 160)), canvas)
    # Both should be > 0, but mid gray is MUCH further from black in
    # linear RGB than dark gray — strictly so, not just marginally.
    assert mid_pair.mean() > dark_pair.mean() + 0.2, (
        f"expected linear gap mid - dark > 0.2, got "
        f"mid={mid_pair.mean():.3f} dark={dark_pair.mean():.3f}"
    )


def test_delta_e_uses_perceptual_distance():
    canvas = CanvasSpec(color=(128, 128, 128))
    a_chroma = ChromaKeying().extract_alpha(_img((128, 200, 128)), canvas)
    a_delta_e = DeltaEKeying().extract_alpha(_img((128, 200, 128)), canvas)
    assert a_chroma.mean() > 0.1
    assert a_delta_e.mean() > 0.1
