"""PLY file loader for pptk (issues #57, #48).

Supports ASCII and binary little-endian PLY files with x, y, z vertex
properties and optional r/g/b (or red/green/blue) colour channels.
"""

import numpy


__all__ = ["load_ply"]


def load_ply(path):
    """Load a PLY file and return (xyz, colors_or_None).

    Args:
        path (str): Path to the PLY file.

    Returns:
        tuple: (xyz, colors) where xyz is an (N, 3) float32 array and colors
            is an (N, 4) float32 RGBA array in [0, 1] if colour properties
            are present, otherwise None.
    """
    with open(path, "rb") as f:
        _, is_binary, is_little_endian, num_vertices, props = _parse_ply_header(f)
        if is_binary:
            data = _read_ply_binary(f, num_vertices, props, is_little_endian)
        else:
            data = _read_ply_ascii(f, num_vertices, props)

    xyz = numpy.column_stack([data["x"], data["y"], data["z"]]).astype(numpy.float32)

    color_keys_rgb = [("r", "g", "b"), ("red", "green", "blue")]
    colors = None
    for rk, gk, bk in color_keys_rgb:
        if rk in data and gk in data and bk in data:
            r = data[rk].astype(numpy.float32)
            g = data[gk].astype(numpy.float32)
            b = data[bk].astype(numpy.float32)
            if r.max() > 1.0:
                r, g, b = r / 255.0, g / 255.0, b / 255.0
            a = numpy.ones(len(r), dtype=numpy.float32)
            colors = numpy.column_stack([r, g, b, a])
            break

    return xyz, colors


def _parse_ply_header(f):
    magic = f.readline().strip()
    if magic != b"ply":
        raise ValueError("Not a PLY file")

    is_binary = False
    is_little_endian = True
    num_vertices = 0
    props = []
    in_vertex_element = False

    _ply_type_map = {
        b"float": ("f", 4), b"float32": ("f", 4),
        b"double": ("d", 8), b"float64": ("d", 8),
        b"int": ("i", 4), b"int32": ("i", 4),
        b"uint": ("I", 4), b"uint32": ("I", 4),
        b"short": ("h", 2), b"int16": ("h", 2),
        b"ushort": ("H", 2), b"uint16": ("H", 2),
        b"char": ("b", 1), b"int8": ("b", 1),
        b"uchar": ("B", 1), b"uint8": ("B", 1),
    }

    while True:
        line = f.readline().strip()
        if line == b"end_header":
            break
        parts = line.split()
        if not parts:
            continue
        if parts[0] == b"format":
            if parts[1] == b"binary_little_endian":
                is_binary, is_little_endian = True, True
            elif parts[1] == b"binary_big_endian":
                is_binary, is_little_endian = True, False
        elif parts[0] == b"element":
            in_vertex_element = parts[1] == b"vertex"
            if in_vertex_element:
                num_vertices = int(parts[2])
        elif parts[0] == b"property" and in_vertex_element:
            if parts[1] == b"list":
                continue
            type_key = parts[1]
            prop_name = parts[2].decode("ascii")
            if type_key in _ply_type_map:
                props.append((prop_name, *_ply_type_map[type_key]))

    return None, is_binary, is_little_endian, num_vertices, props


def _read_ply_binary(f, num_vertices, props, is_little_endian):
    endian = "<" if is_little_endian else ">"
    row_size = sum(p[2] for p in props)
    raw = f.read(num_vertices * row_size)
    dt = numpy.dtype([(p[0], endian + p[1]) for p in props])
    arr = numpy.frombuffer(raw, dtype=dt)
    return {p[0]: arr[p[0]] for p in props}


def _read_ply_ascii(f, num_vertices, props):
    data = {p[0]: [] for p in props}
    for _ in range(num_vertices):
        line = f.readline().decode("ascii").split()
        for i, p in enumerate(props):
            data[p[0]].append(float(line[i]))
    return {k: numpy.array(v) for k, v in data.items()}
