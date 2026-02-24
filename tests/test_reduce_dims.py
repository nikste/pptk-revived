"""Tests for PCA/MDS dimensionality reduction (issue #32)."""
import pytest
import numpy as np
from pptk.dimreduce import reduce_dims


@pytest.fixture
def high_dim():
    rng = np.random.default_rng(99)
    return rng.random((50, 10)).astype(np.float32)


def test_pca_shape(high_dim):
    sklearn = pytest.importorskip("sklearn")
    result = reduce_dims(high_dim, method="pca")
    assert result.shape == (50, 3)
    assert result.dtype == np.float32


def test_mds_shape(high_dim):
    sklearn = pytest.importorskip("sklearn")
    result = reduce_dims(high_dim, method="mds", n_components=2)
    assert result.shape == (50, 2)


def test_invalid_method(high_dim):
    pytest.importorskip("sklearn")
    with pytest.raises(ValueError):
        reduce_dims(high_dim, method="tsne")
