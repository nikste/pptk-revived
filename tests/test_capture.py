"""Tests for v.capture() screenshot functionality (issue #53)."""

import os
import time
import pytest
import numpy as np
from PIL import Image
import pptk


@pytest.fixture
def xyz():
    rng = np.random.default_rng(0)
    return rng.random((1000, 3)).astype(np.float32)


@pytest.fixture
def viewer(xyz):
    v = pptk.viewer(xyz)
    # Give the viewer time to initialize OpenGL and render the first frame
    time.sleep(1)
    yield v
    v.close()


@pytest.mark.requires_display
def test_capture_creates_file(viewer, tmp_path):
    """capture() must block until the PNG file is written (ACK fix)."""
    out = str(tmp_path / 'capture.png')
    viewer.capture(out)
    assert os.path.isfile(out), 'capture() returned but file does not exist'
    assert os.path.getsize(out) > 0, 'capture() wrote an empty file'


@pytest.mark.requires_display
def test_capture_dimensions(viewer, tmp_path):
    """Screenshot must have non-zero dimensions."""
    out = str(tmp_path / 'dims.png')
    viewer.capture(out)
    img = Image.open(out)
    w, h = img.size
    assert w > 0 and h > 0, f'Image has invalid dimensions: {w}x{h}'


@pytest.mark.requires_display
def test_capture_repeated(viewer, tmp_path):
    """Three sequential captures must all succeed."""
    for i in range(3):
        out = str(tmp_path / f'capture_{i}.png')
        viewer.capture(out)
        assert os.path.isfile(out)
        img = Image.open(out)
        assert img.size[0] > 0 and img.size[1] > 0


@pytest.mark.requires_display
def test_capture_not_black(viewer, tmp_path):
    """Screenshot must contain non-black pixels (issue #53)."""
    out = str(tmp_path / 'capture.png')
    viewer.capture(out)
    img = Image.open(out)
    arr = np.array(img)
    non_black = np.any(arr[:, :, :3] != 0, axis=2).sum()
    assert non_black > 0, f'All {arr.shape[0] * arr.shape[1]} pixels are black — capture is broken'
