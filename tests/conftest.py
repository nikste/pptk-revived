"""Shared pytest fixtures for pptk tests."""

import pytest
import numpy as np


@pytest.fixture
def xyz():
    """100 random 3D points as float32."""
    rng = np.random.default_rng(42)
    return rng.random((100, 3)).astype(np.float32)


@pytest.fixture
def viewer(xyz):
    """An open pptk viewer that is automatically closed after the test."""
    import pptk
    v = pptk.viewer(xyz)
    yield v
    v.close()
