"""Test that pptk.set() gives a helpful error (issue #64)."""
import pytest


def test_module_set_raises_attribute_error():
    import pptk
    with pytest.raises(AttributeError, match="pptk.set\\(\\) is not a module-level function"):
        pptk.set(point_size=0.01)


def test_viewer_set_still_works():
    """Ensure viewer.set() is not broken by the module-level guard."""
    import pptk
    # Just test the method exists on the class
    assert hasattr(pptk.viewer, 'set')
