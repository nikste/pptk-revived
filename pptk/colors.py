"""Per-label color mapping for pptk (issue #41)."""
import numpy

__all__ = ["label_to_colors"]


def label_to_colors(labels, colormap="tab10"):
    """Map integer labels to RGBA colours.

    Args:
        labels: 1-D array-like of integer class labels.
        colormap (str): A matplotlib colormap name. Default "tab10".

    Returns:
        numpy.ndarray: (N, 4) float32 RGBA array in [0, 1].

    Example::

        colors = pptk.label_to_colors([0, 1, 2, 0])
        v.attributes(colors)
    """
    try:
        import matplotlib.cm as cm
        cmap = cm.get_cmap(colormap)
        labels = numpy.asarray(labels, dtype=numpy.int32)
        n_classes = int(labels.max()) + 1 if labels.size > 0 else 1
        palette = numpy.array(
            [cmap(i / max(n_classes - 1, 1)) for i in range(n_classes)],
            dtype=numpy.float32)
        return palette[labels % n_classes]
    except ImportError:
        labels = numpy.asarray(labels, dtype=numpy.int32)
        n_classes = max(int(labels.max()) + 1, 1) if labels.size > 0 else 1
        palette = []
        for i in range(n_classes):
            h = (i / n_classes) % 1.0
            i6 = int(h * 6)
            f = h * 6 - i6
            v, p, q, t = 0.9, 0.9 * (1 - 0.8), 0.9 * (1 - f * 0.8), 0.9 * (1 - (1 - f) * 0.8)
            rgb = [(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)][i6 % 6]
            palette.append([rgb[0], rgb[1], rgb[2], 1.0])
        palette = numpy.array(palette, dtype=numpy.float32)
        return palette[labels % n_classes]
