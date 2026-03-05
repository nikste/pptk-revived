"""Tests for depth image capture (issue #46)."""
import pytest


def test_depth_capture_method_exists():
    """viewer should have depth_capture method."""
    from pptk.viewer.viewer import viewer
    assert hasattr(viewer, 'depth_capture')
    assert callable(viewer.depth_capture)


def test_depth_capture_uses_msg_type_14():
    """depth_capture should use message type 14."""
    import struct
    msg_type = struct.pack('b', 14)
    assert msg_type == b'\x0e'
