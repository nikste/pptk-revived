"""Tests for camera coordinate math conventions (issue #29).

The pptk viewer uses a right-handed coordinate system where:
- X points right (east)
- Y points forward (north)
- Z points up

Camera spherical coordinates:
- phi: azimuthal angle (rotation around Z axis, 0 = looking along +X)
- theta: elevation angle (0 = horizontal, pi/2 = looking straight down)
- r (d): distance from camera to look-at point

The view vector points FROM lookAt TOWARD the camera (i.e., the camera
looks along -view).  The right vector is always horizontal (z=0).
"""
import math

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Pure-Python mirrors of the C++ camera functions (camera.h)
# ---------------------------------------------------------------------------

def _compute_right(theta, phi):
    """Camera.computeRightVector"""
    return np.array([-math.sin(phi), math.cos(phi), 0.0])


def _compute_up(theta, phi):
    """Camera.computeUpVector"""
    return np.array([
        -math.sin(theta) * math.cos(phi),
        -math.sin(theta) * math.sin(phi),
        math.cos(theta),
    ])


def _compute_view(theta, phi):
    """Camera.computeViewVector — points FROM lookAt TOWARD the camera."""
    return np.array([
        math.cos(theta) * math.cos(phi),
        math.cos(theta) * math.sin(phi),
        math.sin(theta),
    ])


# Angles used across multiple tests
_ANGLE_COMBOS = [
    (0, 0),
    (0, math.pi / 4),
    (0, math.pi / 2),
    (0, math.pi),
    (math.pi / 6, 0),
    (math.pi / 6, math.pi / 4),
    (math.pi / 4, 0),
    (math.pi / 4, math.pi / 3),
    (math.pi / 3, math.pi),
]


class TestCameraFrame:
    """Validate the camera coordinate frame derived from (theta, phi)."""

    @pytest.mark.parametrize("theta,phi", _ANGLE_COMBOS)
    def test_orthonormal(self, theta, phi):
        """Camera frame vectors should be orthonormal."""
        r = _compute_right(theta, phi)
        u = _compute_up(theta, phi)
        v = _compute_view(theta, phi)

        # Mutual orthogonality
        np.testing.assert_allclose(np.dot(r, u), 0, atol=1e-6)
        np.testing.assert_allclose(np.dot(r, v), 0, atol=1e-6)
        np.testing.assert_allclose(np.dot(u, v), 0, atol=1e-6)

        # Unit length
        np.testing.assert_allclose(np.linalg.norm(r), 1, atol=1e-6)
        np.testing.assert_allclose(np.linalg.norm(u), 1, atol=1e-6)
        np.testing.assert_allclose(np.linalg.norm(v), 1, atol=1e-6)

    @pytest.mark.parametrize("theta,phi", _ANGLE_COMBOS)
    def test_right_handed(self, theta, phi):
        """right x up should equal view (right-handed frame)."""
        r = _compute_right(theta, phi)
        u = _compute_up(theta, phi)
        v = _compute_view(theta, phi)

        np.testing.assert_allclose(
            np.cross(r, u), v, atol=1e-6,
            err_msg=f"Frame not right-handed at phi={phi}, theta={theta}",
        )

    def test_default_orientation(self):
        """At phi=0, theta=0: right=+Y, up=+Z, view=+X."""
        r = _compute_right(0, 0)
        u = _compute_up(0, 0)
        v = _compute_view(0, 0)

        np.testing.assert_allclose(r, [0, 1, 0], atol=1e-6)
        np.testing.assert_allclose(u, [0, 0, 1], atol=1e-6)
        np.testing.assert_allclose(v, [1, 0, 0], atol=1e-6)

    def test_right_vector_horizontal(self):
        """The right vector should always lie in the XY plane (z=0)."""
        for theta, phi in _ANGLE_COMBOS:
            r = _compute_right(theta, phi)
            assert r[2] == 0.0, (
                f"Right vector z-component non-zero at theta={theta}, phi={phi}"
            )


class TestCameraPosition:
    """Validate camera position computation."""

    def test_distance(self):
        """Camera position = lookAt + d * view; distance should be d."""
        lookAt = np.array([1.0, 2.0, 3.0])
        d = 5.0
        theta, phi = math.pi / 4, math.pi / 3
        v = _compute_view(theta, phi)
        eye = lookAt + d * v
        np.testing.assert_allclose(np.linalg.norm(eye - lookAt), d, atol=1e-6)

    def test_camera_above_when_elevated(self):
        """When theta > 0 the camera should be above the lookAt point."""
        lookAt = np.zeros(3)
        d = 10.0
        theta = math.pi / 4  # 45 degrees elevation
        phi = 0.0
        v = _compute_view(theta, phi)
        eye = lookAt + d * v
        assert eye[2] > 0, "Camera should be above lookAt when theta > 0"


class TestPanConvention:
    """Validate the pan (grab-and-drag) convention from camera.h."""

    def test_pan_right_moves_lookat_left(self):
        """Panning right (positive dx) should move lookAt in -right direction.

        This implements the 'grab and drag' convention: dragging right moves
        the scene right, which means the lookAt moves in the -right direction.
        """
        phi, theta = 0, 0
        r = _compute_right(theta, phi)
        dx = 1.0  # mouse moves right
        # pan formula from camera.h: lookAt += panRate * (-right * dx + up * dy)
        delta_lookat = -r * dx
        assert delta_lookat[1] < 0, (
            "Panning right should move lookAt in -Y (left)"
        )

    def test_pan_up_moves_lookat_down(self):
        """Panning up (positive dy) should move lookAt in +up direction."""
        phi, theta = 0, 0
        u = _compute_up(theta, phi)
        dy = 1.0  # mouse moves up
        delta_lookat = u * dy
        assert delta_lookat[2] > 0, (
            "Panning up should move lookAt upward"
        )


class TestViewAxisPresets:
    """Validate the phi/theta values for the axis-aligned view presets.

    These match QtCamera::setViewAxis in qt_camera.h.
    """

    def test_x_axis_view(self):
        """X-axis view (phi=0, theta=0): camera on +X looking toward -X."""
        phi, theta = 0.0, 0.0
        v = _compute_view(theta, phi)
        np.testing.assert_allclose(v, [1, 0, 0], atol=1e-6)

    def test_y_axis_view(self):
        """Y-axis view (phi=-pi/2, theta=0): camera on -Y looking toward +Y."""
        phi, theta = -math.pi / 2, 0.0
        v = _compute_view(theta, phi)
        np.testing.assert_allclose(v, [0, -1, 0], atol=1e-6)

    def test_z_axis_view(self):
        """Z-axis view (phi=-pi/2, theta=pi/2): camera on +Z looking down."""
        phi, theta = -math.pi / 2, math.pi / 2
        v = _compute_view(theta, phi)
        np.testing.assert_allclose(v, [0, 0, 1], atol=1e-6)
