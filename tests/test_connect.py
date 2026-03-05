"""Tests for connecting to an existing viewer (issue #19)."""
import pytest
import numpy as np


def test_connect_creates_viewer_without_process():
    """viewer.connect() should create a viewer with _process=None."""
    from pptk.viewer.viewer import viewer
    v = viewer.connect(12345)
    assert v._portNumber == 12345
    assert v._process is None
    assert v.port == 12345
    np.testing.assert_array_equal(v._offset, np.zeros(3))
    # close should not raise even without a process
    v.close()


def test_connect_available_at_module_level():
    """pptk.connect should be available."""
    import pptk
    assert callable(pptk.connect)


def test_port_property():
    """viewer.port should return the port number."""
    from pptk.viewer.viewer import viewer
    v = viewer.connect(54321)
    assert v.port == 54321
    v.close()
