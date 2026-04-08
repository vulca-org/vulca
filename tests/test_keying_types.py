from vulca.layers.keying import CanvasSpec

def test_canvasspec_from_hex():
    spec = CanvasSpec.from_hex("#ffffff")
    assert spec.color == (255, 255, 255)
    assert spec.tolerance == 0.05
    assert spec.invert is False

def test_canvasspec_from_hex_short():
    spec = CanvasSpec.from_hex("#000")
    assert spec.color == (0, 0, 0)

def test_canvasspec_explicit():
    spec = CanvasSpec(color=(245, 230, 200), tolerance=0.1, invert=False)
    assert spec.color == (245, 230, 200)
    assert spec.tolerance == 0.1
