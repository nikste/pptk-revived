"""Tests for point shape support (issue #5)."""
import pytest


def test_point_shape_property_registered():
    """point_shape should be a recognized property."""
    from pptk.viewer.viewer import _properties
    assert 'point_shape' in _properties


def test_point_shape_codes():
    """Shape name to code mapping should exist."""
    from pptk.viewer.viewer import _point_shape_code
    assert _point_shape_code['circle'] == 0
    assert _point_shape_code['square'] == 1
    assert _point_shape_code['diamond'] == 2


def test_point_shape_encoder():
    """point_shape should use uint encoding."""
    import struct
    from pptk.viewer.viewer import _properties
    encoded = _properties['point_shape'](1)
    assert encoded == struct.pack('I', 1)
