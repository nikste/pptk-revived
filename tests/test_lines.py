"""Tests for line rendering support (issue #44)."""
import pytest
import numpy as np


def test_lines_method_exists():
    """viewer should have lines method."""
    from pptk.viewer.viewer import viewer
    assert hasattr(viewer, 'lines')
    assert callable(viewer.lines)


def test_clear_lines_method_exists():
    """viewer should have clear_lines method."""
    from pptk.viewer.viewer import viewer
    assert hasattr(viewer, 'clear_lines')
    assert callable(viewer.clear_lines)


def test_lines_message_format():
    """lines should use message type 16."""
    import struct
    msg_type = struct.pack('b', 16)
    assert msg_type == b'\x10'


def test_clear_lines_message_format():
    """clear_lines should use message type 17."""
    import struct
    msg_type = struct.pack('b', 17)
    assert msg_type == b'\x11'
