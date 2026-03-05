"""Tests for polygon selection support (issue #28)."""
import pytest
import numpy as np


def test_point_in_polygon_logic():
    """Test ray-casting point-in-polygon algorithm."""
    # Simple square polygon: (-1,-1), (1,-1), (1,1), (-1,1)
    polygon = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

    def point_in_polygon(px, py, poly):
        inside = False
        n = len(poly)
        j = n - 1
        for i in range(n):
            yi, yj = poly[i][1], poly[j][1]
            xi, xj = poly[i][0], poly[j][0]
            if ((yi > py) != (yj > py)) and \
               (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    assert point_in_polygon(0, 0, polygon) == True
    assert point_in_polygon(0.5, 0.5, polygon) == True
    assert point_in_polygon(2, 0, polygon) == False
    assert point_in_polygon(0, 2, polygon) == False


def test_triangle_polygon():
    """Points inside/outside triangle."""
    triangle = [(0, 0), (4, 0), (2, 3)]

    def point_in_polygon(px, py, poly):
        inside = False
        n = len(poly)
        j = n - 1
        for i in range(n):
            yi, yj = poly[i][1], poly[j][1]
            xi, xj = poly[i][0], poly[j][0]
            if ((yi > py) != (yj > py)) and \
               (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    assert point_in_polygon(2, 1, triangle) == True
    assert point_in_polygon(0, 3, triangle) == False


def test_select_polygon_method_exists():
    """viewer should have select_polygon method."""
    from pptk.viewer.viewer import viewer
    assert hasattr(viewer, 'select_polygon')
    assert callable(viewer.select_polygon)


def test_select_polygon_validates_vertices():
    """select_polygon should require at least 3 vertices."""
    from pptk.viewer.viewer import viewer
    v = viewer.__new__(viewer)
    v._portNumber = 1
    v._process = None
    v._offset = np.zeros(3)
    with pytest.raises(ValueError, match='at least 3'):
        v.select_polygon([(0, 0), (1, 1)])
