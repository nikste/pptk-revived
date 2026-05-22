# pptk-revived - Point Processing Toolkit

A fork of [heremaps/pptk](https://github.com/heremaps/pptk), updated to build and run on modern Python (3.12+) and CMake (3.28+).

The Point Processing Toolkit (pptk) is a Python package for visualizing and processing 2-d/3-d point clouds.

![pptk screenshots](/docs/source/tutorials/viewer/images/tutorial_banner.png)

## Features

* **3D point cloud viewer** — renders tens of millions of points interactively using octree-based level of detail
  - Accepts any 3-column NumPy array as input
  - Point selection (rectangular and polygon/lasso) for inspecting and annotating point data
  - Per-point sizes, colors (RGB or scalar colormap), and shapes (circle, square, diamond)
  - Line and edge rendering between points
  - Depth buffer export via `depth_capture()`
  - Camera animation with `play()` and `record()`
  - HiDPI / Retina display support
  - Auto-centering for large coordinates (e.g. UTM) to avoid float32 precision loss
  - Window resizing via `set(window_size=...)`
  - `preserve_camera` option for `viewer.load()` to keep the current viewpoint
  - `viewer.connect(port)` to attach to an already-running viewer process
  - `wait_async()` returning a `Future` for non-blocking wait
* **Jupyter notebook integration** — viewer objects render as interactive 3D visualizations inline via Three.js (drag to orbit, scroll to zoom, right-click to pan)
* **Parallelized k-d tree** — k-nearest neighbor and r-near range queries (both build and queries are parallelized via TBB)
* **Normal estimation** — PCA-based surface normal estimation using local point neighborhoods
* **PLY file loader** — `pptk.load_ply()` reads ASCII and binary PLY files
* **Sequence animation** — `pptk.sequence()` for animating through lists of point clouds

[Homepage](https://heremaps.github.io/pptk/index.html) · [Tutorials](https://heremaps.github.io/pptk/tutorial.html)

## License

Unless otherwise noted in `LICENSE` files for specific files or directories,
the [LICENSE](LICENSE) in the root applies to all content in this repository.

## Install

Install from PyPI:

```
pip install pptk-revived
```

or from a locally built wheel (see [Build](#build)):

```
pip install <.whl file>
```

## Quickstart

Both `import pptk` and `import pptk_revived` work and are identical:

```python
import numpy as np
import pptk  # or: import pptk_revived

x = np.random.rand(100, 3)
v = pptk.viewer(x)
v.set(point_size=0.01)
```

### Jupyter Notebooks

Viewer objects display as interactive 3D visualizations in Jupyter notebooks — drag to orbit, scroll to zoom, right-click to pan:

```python
v = pptk.viewer(xyz, rgb)
v  # renders inline via Three.js
```

### Examples

| Notebook | Description |
|---|---|
| [`examples/quickstart.ipynb`](examples/quickstart.ipynb) | Basic viewer usage, scalar and RGB coloring |
| [`examples/documentation_examples.ipynb`](examples/documentation_examples.ipynb) | k-NN queries, normal estimation, camera animation, Möbius strip |
| [`examples/jupyter_interactive_demo.ipynb`](examples/jupyter_interactive_demo.ipynb) | Inline Three.js viewer with colormaps and large point cloud subsampling |

For more examples, see the [tutorials](https://heremaps.github.io/pptk/tutorial.html).

## Build

pptk-revived contains C++ extensions (Qt viewer, k-d tree, normal estimator)
that are compiled with CMake. You don't run CMake yourself — the `setuptools`
build backend invokes it automatically while building the wheel (see the
`CMakeBuild` command in [`setup.py`](setup.py)), so a single `uv build`
produces a ready-to-install wheel.

### System requirements

* [Python](https://www.python.org/) 3.9+
* [Qt5](https://www.qt.io/)
* [TBB](https://github.com/oneapi-src/oneTBB) (libtbb-dev)
* [Eigen](http://eigen.tuxfamily.org) 3.x (libeigen3-dev)
* [Numpy](http://www.numpy.org/)
* CMake 3.5+
* patchelf (Linux only)

On Ubuntu/Debian:

```bash
sudo apt install build-essential cmake patchelf \
    libtbb-dev libeigen3-dev qtbase5-dev libqt5opengl5-dev libgl1-mesa-dev
```

### Build a wheel

```bash
uv build                                   # compiles the C++ + packages -> dist/
uv pip install dist/pptk_revived-*.whl
```

> **Run build/install commands from the repository root**, never from inside
> `_cmake_build/`. The CMake build copies a `setup.py` into `_cmake_build/`, so
> running `uv build` or `pip install .` from there builds a broken, stale
> package (you'll see CMake fail with *"source directory … does not appear to
> contain CMakeLists.txt"*).

This is exactly what the release CI runs (`.github/workflows/build-wheels.yml`).
Plain pip works the same way, since it uses the same backend:

```bash
pip install .          # build C++ and install
python -m build        # or only build the wheel + sdist into dist/
```

> **Forcing a recompile.** To avoid needless work, the build **skips CMake when
> the compiled artifacts already exist** in the source tree. After editing any
> C++ source, set `PPTK_FORCE_CMAKE=1` to clear the cached artifacts and rebuild
> from scratch:
>
> ```bash
> PPTK_FORCE_CMAKE=1 uv build
> ```

### Development install (editable)

```bash
uv sync                                    # set up the dev env + editable install
# after changing C++ sources, force a recompile:
PPTK_FORCE_CMAKE=1 uv pip install -e .
```

While iterating on C++ you can recompile a single target and refresh the
in-tree artifact the editable install loads, instead of rebuilding everything
(after an initial build has configured `_cmake_build/`):

```bash
cmake --build _cmake_build --target viewer -- -j$(nproc)
cp _cmake_build/pptk/viewer/viewer pptk/viewer/viewer
```

Available targets: `viewer`, `kdtree`, `vfuncs`, `estimate_normals` (for the
library modules, copy the resulting `.so` into the matching `pptk/<module>/`
directory).

### Windows

The same `uv build` command applies. Make sure Qt5, TBB, and Eigen are
discoverable by CMake (e.g. via `CMAKE_PREFIX_PATH`); CMake selects the Visual
Studio generator by default.

## Acknowledgements

Originally developed by [HERE Europe B.V.](https://github.com/heremaps) (Copyright 2011–2018).
This fork is maintained by [Nikolaas Steenbergen](https://github.com/nikste).
