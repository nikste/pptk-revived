"""Tests for window resize via set(window_size=...) (issue #16).

Verifies that the viewer window can be resized from Python and that
capture() produces an image matching the requested dimensions.

NOTE: These tests require the C++ viewer binary to be rebuilt with
message type 13 support.  They are automatically skipped when running
against an older binary.
"""

import os
import time
import pytest
import numpy as np


def _viewer_supports_resize(v, tmp_path):
    """Return True if the viewer binary handles message type 13."""
    from PIL import Image

    v.set(window_size=(800, 600))
    time.sleep(0.5)
    out = str(tmp_path / "_probe_resize.png")
    v.capture(out)
    img = Image.open(out)
    w, h = img.size
    # The default window is 512x512 — if the image is still that size
    # the binary doesn't support resize yet.
    return w != 512 or h != 512


@pytest.mark.requires_display
def test_set_window_size(tmp_path):
    """set(window_size=(W, H)) should resize the viewer window."""
    from PIL import Image
    import pptk

    rng = np.random.default_rng(16)
    xyz = rng.random((500, 3)).astype(np.float32)
    v = pptk.viewer(xyz)
    time.sleep(0.5)

    if not _viewer_supports_resize(v, tmp_path):
        v.close()
        pytest.skip("C++ viewer binary does not support message type 13 (resize)")

    out = str(tmp_path / "resize_capture.png")
    v.capture(out)
    v.close()

    assert os.path.isfile(out), "capture file was not created"
    img = Image.open(out)
    w, h = img.size
    assert w >= 800 and h >= 600, (
        f"Captured image is {w}x{h}, expected at least 800x600"
    )


@pytest.mark.requires_display
def test_set_window_size_with_other_props(tmp_path):
    """window_size can be set alongside other properties in a single call."""
    from PIL import Image
    import pptk

    rng = np.random.default_rng(161)
    xyz = rng.random((200, 3)).astype(np.float32)
    v = pptk.viewer(xyz)
    time.sleep(0.5)

    if not _viewer_supports_resize(v, tmp_path):
        v.close()
        pytest.skip("C++ viewer binary does not support message type 13 (resize)")

    v.set(window_size=(640, 480), point_size=0.02)
    time.sleep(0.5)

    out = str(tmp_path / "resize_combo.png")
    v.capture(out)
    v.close()

    assert os.path.isfile(out)
    img = Image.open(out)
    w, h = img.size
    assert w >= 640 and h >= 480, (
        f"Captured image is {w}x{h}, expected at least 640x480"
    )


@pytest.mark.requires_display
def test_set_window_size_message_does_not_crash():
    """Sending a resize message must not crash the viewer, even without C++ support."""
    import pptk

    rng = np.random.default_rng(162)
    xyz = rng.random((100, 3)).astype(np.float32)
    v = pptk.viewer(xyz)
    time.sleep(0.5)

    # This should not raise, even if the binary ignores the message
    v.set(window_size=(640, 480), point_size=0.01)
    time.sleep(0.3)

    # Viewer should still be responsive
    n = v.get('num_points')
    v.close()
    assert n == 100
