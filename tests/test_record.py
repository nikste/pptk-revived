"""Tests for viewer.record() ConnectionRefusedError (issues #9, #18).

record() used to fire-and-forget the camera pose message, then
immediately open a new socket for capture(). If the viewer was still
processing the pose, the capture connection would be refused.  The fix
makes the pose send blocking (waits for ACK) before calling capture().
"""

import os
import time
import pytest
import numpy as np


@pytest.mark.requires_display
def test_record_multiple_frames(tmp_path):
    """record() must successfully capture every frame without errors."""
    import pptk

    rng = np.random.default_rng(9)
    xyz = rng.random((500, 3)).astype(np.float32)
    v = pptk.viewer(xyz)
    time.sleep(1)

    poses = [
        [0, 0, 0, 0 * np.pi / 4, np.pi / 4, 3],
        [0, 0, 0, 1 * np.pi / 4, np.pi / 4, 3],
        [0, 0, 0, 2 * np.pi / 4, np.pi / 4, 3],
        [0, 0, 0, 3 * np.pi / 4, np.pi / 4, 3],
    ]

    folder = str(tmp_path / "recording")
    os.makedirs(folder)
    v.record(folder, poses, ts=[0, 1, 2, 3], fps=2)
    v.close()

    frames = sorted(f for f in os.listdir(folder) if f.endswith(".png"))
    assert len(frames) >= 4, (
        f"Expected at least 4 frames, got {len(frames)}: {frames}"
    )
    for f in frames:
        path = os.path.join(folder, f)
        assert os.path.getsize(path) > 0, f"{f} is empty"


@pytest.mark.requires_display
def test_record_single_frame(tmp_path):
    """record() with a single-pose path should produce one frame."""
    import pptk

    rng = np.random.default_rng(18)
    xyz = rng.random((100, 3)).astype(np.float32)
    v = pptk.viewer(xyz)
    time.sleep(1)

    poses = [[0, 0, 0, 0, np.pi / 4, 3]]
    folder = str(tmp_path / "single")
    os.makedirs(folder)
    v.record(folder, poses, fps=1)
    v.close()

    frames = [f for f in os.listdir(folder) if f.endswith(".png")]
    assert len(frames) == 1, f"Expected 1 frame, got {len(frames)}"
