"""Tests for viewer.animate() (issue #52)."""
import pytest
import numpy as np
import pptk


@pytest.mark.requires_display
def test_animate_updates_viewer():
    rng = np.random.default_rng(30)
    clouds = [rng.random((50, 3)).astype(np.float32) for _ in range(3)]
    v = pptk.viewer(clouds[0])
    v.animate(clouds, fps=100)
    v.close()


@pytest.mark.requires_display
def test_animate_empty_list():
    rng = np.random.default_rng(30)
    v = pptk.viewer(rng.random((10, 3)).astype(np.float32))
    v.animate([], fps=100)  # no-op, no error
    v.close()


@pytest.mark.requires_display
def test_animate_single_cloud():
    rng = np.random.default_rng(30)
    cloud = rng.random((50, 3)).astype(np.float32)
    v = pptk.viewer(cloud)
    v.animate([cloud], fps=100)
    v.close()


@pytest.mark.requires_display
def test_animate_accepts_generator():
    rng = np.random.default_rng(30)
    v = pptk.viewer(rng.random((10, 3)).astype(np.float32))
    gen = (rng.random((10, 3)).astype(np.float32) for _ in range(3))
    v.animate(gen, fps=100)
    v.close()
