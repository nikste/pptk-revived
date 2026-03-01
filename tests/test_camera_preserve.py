"""Tests for preserve_camera on viewer.load() (issue #50).

When loading new points with preserve_camera=True the camera should
keep its position instead of resetting to fit the new point cloud.
"""

import time
import pytest
import numpy as np


@pytest.mark.requires_display
def test_load_preserve_camera():
    """Camera params must survive load(preserve_camera=True)."""
    import pptk

    rng = np.random.default_rng(50)
    xyz1 = rng.random((200, 3)).astype(np.float32)
    xyz2 = rng.random((200, 3)).astype(np.float32) * 10  # very different scale

    v = pptk.viewer(xyz1)
    time.sleep(0.5)

    # Set a deliberate camera pose
    v.set(phi=1.0, theta=0.5, r=3.0, lookat=[0.1, 0.2, 0.3])
    time.sleep(0.3)

    phi_before = float(v.get('phi'))
    theta_before = float(v.get('theta'))
    r_before = float(v.get('r'))
    lookat_before = v.get('lookat').flatten()

    # Reload with different points but preserve the camera
    v.load(xyz2, preserve_camera=True)
    time.sleep(0.3)

    phi_after = float(v.get('phi'))
    theta_after = float(v.get('theta'))
    r_after = float(v.get('r'))
    lookat_after = v.get('lookat').flatten()

    v.close()

    assert abs(phi_after - phi_before) < 1e-3, \
        f"phi changed: {phi_before} -> {phi_after}"
    assert abs(theta_after - theta_before) < 1e-3, \
        f"theta changed: {theta_before} -> {theta_after}"
    assert abs(r_after - r_before) < 1e-3, \
        f"r changed: {r_before} -> {r_after}"
    assert np.allclose(lookat_after, lookat_before, atol=1e-3), \
        f"lookat changed: {lookat_before} -> {lookat_after}"


@pytest.mark.requires_display
def test_load_default_resets_camera():
    """Default load() (preserve_camera=False) must reset the camera."""
    import pptk

    rng = np.random.default_rng(50)
    xyz1 = rng.random((200, 3)).astype(np.float32)
    xyz2 = (rng.random((200, 3)).astype(np.float32) + 100) * 10

    v = pptk.viewer(xyz1)
    time.sleep(0.5)

    v.set(phi=2.0, theta=1.0, r=0.5)
    time.sleep(0.3)

    r_before = float(v.get('r'))

    # Default load should reset the camera to fit new data
    v.load(xyz2)
    time.sleep(0.3)

    r_after = float(v.get('r'))
    v.close()

    # The new points are at a very different scale, so r should change
    assert abs(r_after - r_before) > 0.1, \
        f"r barely changed ({r_before} -> {r_after}); camera was not reset"
