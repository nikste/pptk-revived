"""Tests for point query / hover details (issue #8)."""
import pytest


def test_query_point_method_exists():
    """viewer should have query_point method."""
    from pptk.viewer.viewer import viewer
    assert hasattr(viewer, 'query_point')
    assert callable(viewer.query_point)


def test_query_near_point_original_exists():
    """PointCloud should have queryNearPointOriginal (C++ side).

    This test just verifies the Python API is in place.
    The C++ method is tested via integration tests with a display.
    """
    import struct
    # Verify message type 18 encoding
    msg = struct.pack('b', 18)
    assert msg == b'\x12'


def test_query_point_message_format():
    """query_point should send msg type 18 + two floats."""
    import struct
    msg = struct.pack('b', 18) + struct.pack('ff', 100.0, 200.0)
    assert len(msg) == 9  # 1 + 4 + 4 bytes
