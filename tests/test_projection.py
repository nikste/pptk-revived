"""Tests for 2D projection (issue #6)."""
import numpy as np
from pptk.projection import project


def test_project_shape():

    class MockViewer:
        def get(self, key):
            return np.eye(4, dtype=np.float64)

    v = MockViewer()
    pts = np.random.rand(10, 3).astype(np.float32)
    result = project(v, pts)
    assert result.shape == (10, 2)
    assert result.dtype == np.float32


def test_project_identity():
    """With identity MVP, projection should give x/w, y/w of homogeneous pts."""

    class MockViewer:
        def get(self, key):
            return np.eye(4, dtype=np.float64)

    v = MockViewer()
    pts = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
    result = project(v, pts)
    # With identity MVP: clip = [x, y, z, 1], ndc = [x/1, y/1] = [x, y]
    np.testing.assert_allclose(result[0], [1.0, 2.0], atol=1e-5)
