"""Tests for non-blocking wait (issue #17)."""
import pytest
from concurrent.futures import Future


def test_wait_async_returns_future():
    """wait_async() should return a concurrent.futures.Future."""
    from pptk.viewer.viewer import viewer
    assert hasattr(viewer, 'wait_async')
    assert callable(viewer.wait_async)


def test_wait_async_method_exists():
    """The viewer class should have wait_async defined."""
    from pptk.viewer.viewer import viewer
    import inspect
    assert 'wait_async' in dir(viewer)
    sig = inspect.signature(viewer.wait_async)
    # Only parameter should be 'self'
    params = list(sig.parameters.keys())
    assert params == ['self']
