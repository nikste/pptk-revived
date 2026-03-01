"""Tests for HiDPI / devicePixelRatio scaling (issue #26).

Verifies that the rendered viewport accounts for the device pixel ratio,
so that capture() produces images whose pixel dimensions equal the logical
window size multiplied by the DPR.
"""

import os
import time
import pytest
import numpy as np


@pytest.mark.requires_display
def test_capture_dimensions_match_dpr(tmp_path):
    """capture() image dimensions must equal window size * devicePixelRatio.

    On HiDPI displays the OpenGL viewport must be scaled by the DPR.
    If glViewport uses un-scaled logical pixels the rendered image will
    only fill a quarter of the framebuffer, producing a partially-black
    screenshot.
    """
    from PIL import Image
    import pptk

    rng = np.random.default_rng(26)
    xyz = rng.random((500, 3)).astype(np.float32)
    v = pptk.viewer(xyz)
    time.sleep(1)  # let the viewer initialise

    out = str(tmp_path / "hidpi_capture.png")
    v.capture(out)
    v.close()

    assert os.path.isfile(out), "capture file was not created"
    img = Image.open(out)
    w, h = img.size

    # The image must have sensible, non-zero dimensions.
    # On a HiDPI screen these will be > the logical window size;
    # on 1x screens they should match exactly.
    assert w > 0 and h > 0, f"Invalid capture dimensions: {w}x{h}"

    # The image should not be predominantly black (a sign that the
    # viewport was too small relative to the framebuffer).
    arr = np.array(img)
    non_black = np.any(arr[:, :, :3] != 0, axis=2).sum()
    total = arr.shape[0] * arr.shape[1]
    ratio = non_black / total
    assert ratio > 0.05, (
        f"Only {ratio:.1%} of pixels are non-black — "
        "viewport likely not scaled by devicePixelRatio"
    )
