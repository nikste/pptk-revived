"""Tests for PLY file loader (issues #57, #48)."""
import struct
import numpy as np
import pytest
import pptk


def _make_ascii_ply(vertices, colors=None):
    has_color = colors is not None
    lines = [b"ply", b"format ascii 1.0",
             "element vertex %d" % len(vertices)]
    lines[-1] = lines[-1].encode()
    for prop in ["x", "y", "z"]:
        lines.append(("property float %s" % prop).encode())
    if has_color:
        for prop in ["r", "g", "b"]:
            lines.append(("property uchar %s" % prop).encode())
    lines.append(b"end_header")
    for i, v in enumerate(vertices):
        if has_color:
            c = colors[i]
            lines.append(("%s %s %s %s %s %s" % (v[0], v[1], v[2], c[0], c[1], c[2])).encode())
        else:
            lines.append(("%s %s %s" % (v[0], v[1], v[2])).encode())
    return b"
".join(lines) + b"
"


def _make_binary_ply(vertices):
    header = (
        b"ply
"
        b"format binary_little_endian 1.0
"
        + ("element vertex %d
" % len(vertices)).encode()
        + b"property float x
"
        + b"property float y
"
        + b"property float z
"
        + b"end_header
"
    )
    body = struct.pack("%df" % (3*len(vertices)), *[v for row in vertices for v in row])
    return header + body


def test_load_ascii_ply(tmp_path):
    verts = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    data = _make_ascii_ply(verts)
    p = tmp_path / "test.ply"
    p.write_bytes(data)
    xyz, colors = pptk.load_ply(str(p))
    assert xyz.shape == (2, 3)
    assert colors is None
    np.testing.assert_allclose(xyz[0], [1.0, 2.0, 3.0], atol=1e-5)


def test_load_binary_ply(tmp_path):
    verts = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    data = _make_binary_ply(verts)
    p = tmp_path / "test.ply"
    p.write_bytes(data)
    xyz, colors = pptk.load_ply(str(p))
    assert xyz.shape == (2, 3)
    assert colors is None
    np.testing.assert_allclose(xyz[0], [1.0, 2.0, 3.0], atol=1e-5)


def test_load_ply_with_color(tmp_path):
    verts = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]
    rgb = [[255, 0, 0], [0, 255, 0]]
    data = _make_ascii_ply(verts, colors=rgb)
    p = tmp_path / "color.ply"
    p.write_bytes(data)
    xyz, colors = pptk.load_ply(str(p))
    assert colors is not None
    assert colors.shape == (2, 4)
    assert colors.dtype == np.float32
    np.testing.assert_allclose(colors[0, :3], [1.0, 0.0, 0.0], atol=1e-5)


def test_load_ply_invalid(tmp_path):
    p = tmp_path / "invalid.ply"
    p.write_bytes(b"not a ply file")
    with pytest.raises(ValueError, match="Not a PLY file"):
        pptk.load_ply(str(p))
