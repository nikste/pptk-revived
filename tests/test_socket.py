"""Tests for socket reliability (issue #60)."""
import pytest
import numpy as np
import pptk


@pytest.fixture
def xyz():
    rng = np.random.default_rng(1)
    return rng.random((50, 3)).astype(np.float32)


@pytest.mark.requires_display
def test_repeated_load_clear(xyz):
    """30 load/clear cycles must not raise ConnectionRefusedError (issue #60)."""
    v = pptk.viewer(xyz)
    try:
        for _ in range(30):
            v.load(xyz)
            v.clear()
    finally:
        v.close()


@pytest.mark.requires_display
def test_socket_cleanup(xyz):
    """Create and close viewer 5 times without socket leaks."""
    for _ in range(5):
        v = pptk.viewer(xyz)
        v.close()
