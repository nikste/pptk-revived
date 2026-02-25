"""Tests for label_to_colors (issue #41)."""
import numpy as np
from pptk.colors import label_to_colors


def test_shape():
    colors = label_to_colors([0, 1, 2, 0, 1])
    assert colors.shape == (5, 4)
    assert colors.dtype == np.float32


def test_range():
    colors = label_to_colors(np.arange(10))
    assert colors.min() >= 0.0 and colors.max() <= 1.0


def test_same_label_same_color():
    colors = label_to_colors([0, 1, 0, 2, 1])
    np.testing.assert_array_equal(colors[0], colors[2])
    np.testing.assert_array_equal(colors[1], colors[4])


def test_different_labels_different_colors():
    colors = label_to_colors([0, 1, 2, 3])
    for i in range(4):
        for j in range(i + 1, 4):
            assert not np.array_equal(colors[i], colors[j]), \
                f"Labels {i} and {j} should have different colors"


def test_single_label():
    colors = label_to_colors([0, 0, 0])
    assert colors.shape == (3, 4)
    np.testing.assert_array_equal(colors[0], colors[1])
    np.testing.assert_array_equal(colors[1], colors[2])


def test_alpha_channel_is_one():
    colors = label_to_colors([0, 1, 2])
    np.testing.assert_array_equal(colors[:, 3], 1.0)


def test_accepts_numpy_array():
    labels = np.array([0, 1, 2, 1, 0], dtype=np.int64)
    colors = label_to_colors(labels)
    assert colors.shape == (5, 4)


def test_large_label_values():
    colors = label_to_colors([0, 100, 200])
    assert colors.shape == (3, 4)
    assert colors.dtype == np.float32
    assert colors.min() >= 0.0 and colors.max() <= 1.0


def test_many_classes():
    labels = list(range(50))
    colors = label_to_colors(labels)
    assert colors.shape == (50, 4)
    assert colors.dtype == np.float32


def test_fallback_without_matplotlib(monkeypatch):
    """Test the HSV fallback path when matplotlib is unavailable."""
    import builtins
    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name.startswith("matplotlib"):
            raise ImportError("mocked")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)
    colors = label_to_colors([0, 1, 2])
    assert colors.shape == (3, 4)
    assert colors.dtype == np.float32
    assert colors.min() >= 0.0 and colors.max() <= 1.0
    # Alpha should still be 1.0
    np.testing.assert_array_equal(colors[:, 3], 1.0)
