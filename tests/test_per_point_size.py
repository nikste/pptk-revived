"""Tests for per-point size support (issue #33)."""
import pytest


def test_point_sizes_property_registered():
    """point_sizes should be a recognized property."""
    from pptk.viewer.viewer import _properties
    assert 'point_sizes' in _properties


def test_point_sizes_encoder():
    """point_sizes should use float array encoding."""
    import numpy as np
    from pptk.viewer.viewer import _properties
    sizes = np.array([0.01, 0.02, 0.03], dtype=np.float32)
    encoded = _properties['point_sizes'](sizes)
    assert len(encoded) == 12  # 3 * 4 bytes
