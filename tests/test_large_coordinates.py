"""Tests for large-coordinate auto-centering (issue #51).

Verifies that point clouds with large UTM-like coordinates don't suffer
from float32 precision loss, thanks to Python-side auto-centering.
"""

import time
import pytest
import numpy as np


@pytest.mark.requires_display
def test_lookat_roundtrip_large_coords():
    """set(lookat=...) / get('lookat') must round-trip at full precision."""
    import pptk

    # UTM-like coordinates: large absolute values
    center = np.array([317785.0, 5049158.0, 40.0])
    rng = np.random.default_rng(51)
    xyz = center + rng.random((500, 3)).astype(np.float64) * 10.0

    v = pptk.viewer(xyz)
    time.sleep(0.5)

    target = center + np.array([5.0, 5.0, 5.0])
    v.set(lookat=target)
    time.sleep(0.2)

    got = v.get('lookat')
    v.close()

    # The round-trip error must be small (sub-meter for UTM).
    # Without centering, float32 error at x~317785 is ~0.02;
    # at y~5049158 it's ~0.3.  With centering the residual is ~5
    # which fits in float32 with <0.001 error.
    np.testing.assert_allclose(got, target, atol=0.05,
                               err_msg="lookat round-trip failed for large coords")


@pytest.mark.requires_display
def test_eye_in_original_space():
    """get('eye') must return values in the original (large) coordinate space."""
    import pptk

    center = np.array([317785.0, 5049158.0, 40.0])
    rng = np.random.default_rng(512)
    xyz = center + rng.random((200, 3)).astype(np.float64) * 5.0

    v = pptk.viewer(xyz)
    time.sleep(0.5)

    eye = v.get('eye')
    v.close()

    # Eye should be near the center of the point cloud (in original space),
    # not near the origin.
    assert np.linalg.norm(eye[:2] - center[:2]) < 100.0, (
        f"eye={eye} is not in original coordinate space (expected near {center})"
    )


@pytest.mark.requires_display
def test_offset_stored_as_float64():
    """The internal _offset must be float64 to preserve full precision."""
    import pptk

    center = np.array([317785.0, 5049158.0, 40.0])
    xyz = center + np.random.default_rng(513).random((100, 3)) * 2.0

    v = pptk.viewer(xyz)
    assert v._offset.dtype == np.float64, (
        f"_offset dtype is {v._offset.dtype}, expected float64"
    )
    # Verify the offset is close to the centroid
    np.testing.assert_allclose(v._offset, xyz.mean(axis=0), atol=0.01)
    v.close()
