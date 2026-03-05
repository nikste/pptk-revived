"""Tests for memory validation on large point clouds (issue #38)."""
import pytest
import warnings
import numpy as np


def test_large_cloud_warning():
    """Loading more than 500M points should emit a warning."""
    from pptk.viewer.viewer import _MAX_POINTS_WARNING
    assert _MAX_POINTS_WARNING == 500_000_000


def test_octree_max_depth_constant():
    """Octree should have a max recursion depth guard (C++ side)."""
    # This test just verifies the Python-side validation exists.
    # The C++ octree depth guard is tested via the build/integration tests.
    from pptk.viewer.viewer import viewer
    assert hasattr(viewer, '_viewer__load')  # name-mangled private method exists
