"""Tests for UV/pip compatibility and package metadata."""


def test_import():
    import pptk
    assert pptk is not None


def test_version():
    import pptk
    assert hasattr(pptk, '__version__')
    assert isinstance(pptk.__version__, str)
    assert pptk.__version__


def test_all_submodules():
    import pptk.viewer.viewer
    import pptk.kdtree.kdtree
    import pptk.points.points
    import pptk.processing.estimate_normals.estimate_normals
