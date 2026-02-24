"""Dimensionality reduction for high-dimensional point clouds (issue #32)."""
import numpy

__all__ = ["reduce_dims"]


def reduce_dims(X, method="pca", n_components=3):
    """Reduce high-dimensional data to 3D using PCA or MDS.

    Requires scikit-learn.

    Args:
        X: (N, D) array-like of high-dimensional data.
        method (str): "pca" or "mds".
        n_components (int): Output dimensions (default 3).

    Returns:
        numpy.ndarray: (N, n_components) float32 array.

    Example::

        xyz = pptk.reduce_dims(features, method="pca")
        v = pptk.viewer(xyz)
    """
    try:
        from sklearn.decomposition import PCA
        from sklearn.manifold import MDS
    except ImportError:
        raise ImportError(
            "reduce_dims() requires scikit-learn: pip install scikit-learn")

    X = numpy.asarray(X, dtype=numpy.float64)
    if method == "pca":
        return PCA(n_components=n_components).fit_transform(X).astype(numpy.float32)
    elif method == "mds":
        return MDS(n_components=n_components).fit_transform(X).astype(numpy.float32)
    else:
        raise ValueError("method must be 'pca' or 'mds'")
