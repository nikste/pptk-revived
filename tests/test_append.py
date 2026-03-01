"""Tests for viewer.append() — native C++ point append (issue #52)."""
import pytest
import numpy as np
import pptk


@pytest.mark.requires_display
def test_append_increases_point_count():
    rng = np.random.default_rng(42)
    v = pptk.viewer(rng.random((50, 3)).astype(np.float32))
    v.append(rng.random((30, 3)).astype(np.float32))
    assert v.get('num_points') == 80
    v.close()


@pytest.mark.requires_display
def test_append_to_empty_viewer():
    rng = np.random.default_rng(42)
    v = pptk.viewer(rng.random((10, 3)).astype(np.float32))
    v.clear()
    v.append(rng.random((20, 3)).astype(np.float32))
    assert v.get('num_points') == 20
    v.close()


@pytest.mark.requires_display
def test_append_empty_array_is_noop():
    rng = np.random.default_rng(42)
    v = pptk.viewer(rng.random((25, 3)).astype(np.float32))
    v.append(np.empty((0, 3), dtype=np.float32))
    assert v.get('num_points') == 25
    v.close()


@pytest.mark.requires_display
def test_multiple_appends():
    rng = np.random.default_rng(42)
    v = pptk.viewer(rng.random((10, 3)).astype(np.float32))
    for _ in range(5):
        v.append(rng.random((10, 3)).astype(np.float32))
    assert v.get('num_points') == 60
    v.close()
