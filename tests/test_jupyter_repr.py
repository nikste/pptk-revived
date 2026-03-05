"""Tests for Jupyter _repr_html_ support (issue #1)."""
import pytest
import numpy as np


def test_repr_html_method_exists():
    """viewer should have _repr_html_ method for Jupyter display."""
    from pptk.viewer.viewer import viewer
    assert hasattr(viewer, '_repr_html_')
    assert callable(viewer._repr_html_)


def test_repr_html_returns_threejs_html():
    """_repr_html_ should return interactive Three.js HTML."""
    from pptk.viewer.viewer import viewer
    v = viewer.__new__(viewer)
    v._portNumber = 1
    v._process = None
    v._offset = np.zeros(3)
    v._positions = np.random.rand(50, 3)
    v._attr = ()
    result = v._repr_html_()
    assert isinstance(result, str)
    assert 'three' in result.lower() or 'THREE' in result
    assert 'OrbitControls' in result
    assert 'pptk_' in result
    v.close()


def test_repr_html_with_rgb_colors():
    """_repr_html_ should embed vertex colors from RGB attributes."""
    from pptk.viewer.viewer import viewer
    v = viewer.__new__(viewer)
    v._portNumber = 1
    v._process = None
    v._offset = np.zeros(3)
    v._positions = np.random.rand(20, 3)
    v._attr = (np.random.rand(20, 3).astype(np.float32),)
    result = v._repr_html_()
    assert 'vertexColors' in result
    v.close()


def test_repr_html_with_scalar_attr():
    """_repr_html_ should colormap scalar attributes."""
    from pptk.viewer.viewer import viewer
    v = viewer.__new__(viewer)
    v._portNumber = 1
    v._process = None
    v._offset = np.zeros(3)
    v._positions = np.random.rand(30, 3)
    v._attr = (np.arange(30, dtype=np.float32),)
    result = v._repr_html_()
    assert 'vertexColors' in result
    v.close()


def test_repr_html_no_positions():
    """_repr_html_ should handle missing positions gracefully."""
    from pptk.viewer.viewer import viewer
    v = viewer.__new__(viewer)
    v._portNumber = 1
    v._process = None
    v._offset = np.zeros(3)
    result = v._repr_html_()
    assert '<pre>' in result
    v.close()


def test_repr_html_subsamples_large_clouds():
    """_repr_html_ should subsample when points > 200k."""
    from pptk.viewer.viewer import viewer
    v = viewer.__new__(viewer)
    v._portNumber = 1
    v._process = None
    v._offset = np.zeros(3)
    v._positions = np.random.rand(300_000, 3)
    v._attr = ()
    result = v._repr_html_()
    assert 'subsampled' in result
    assert 'showing 200000' in result
    v.close()
