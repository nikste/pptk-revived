"""2D projection from viewer camera (issue #6)."""
import numpy

__all__ = ["project"]


def project(v, points):
    """Project 3D points to 2D NDC using the viewer MVP matrix.

    Args:
        v: An open pptk viewer instance.
        points: (N, 3) array-like of 3D XYZ positions.

    Returns:
        numpy.ndarray: (N, 2) float32 array of (x, y) in NDC [-1, 1].

    Example::

        xy = pptk.project(v, xyz)
    """
    mvp = numpy.array(v.get("mvp"), dtype=numpy.float64).reshape(4, 4)
    pts = numpy.asarray(points, dtype=numpy.float64)
    ones = numpy.ones((len(pts), 1), dtype=numpy.float64)
    pts_h = numpy.hstack([pts, ones])
    clip = pts_h @ mvp.T
    w = clip[:, 3:4]
    ndc = clip[:, :2] / w
    return ndc.astype(numpy.float32)
