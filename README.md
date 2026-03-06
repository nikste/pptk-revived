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
that must be compiled before packaging. The build process is:

1. Compile C++ extensions with CMake
2. Package the compiled artifacts into a wheel

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
sudo apt install build-essential cmake patchelf libtbb-dev libeigen3-dev qtbase5-dev libqt5opengl5-dev
```

### Build with uv (recommended)

```bash
# 1. Compile C++ extensions
mkdir _cmake_build && cd _cmake_build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -- -j$(nproc)
cd ..

# 2. Package into a wheel (uv detects the pre-compiled .so files and skips cmake)
uv build

# 3. Install the wheel
uv pip install dist/pptk_revived-*.whl
```

### Build with pip / venv

```bash
# 1. Create a venv
python3 -m venv venv && source venv/bin/activate
pip install numpy

# 2. Compile C++ extensions
mkdir _cmake_build && cd _cmake_build
cmake .. -DCMAKE_BUILD_TYPE=Release -DPython3_EXECUTABLE=$(which python)
cmake --build . -- -j$(nproc)
cd ..

# 3. Package and install
python setup.py bdist_wheel
pip install dist/pptk_revived-*.whl --force-reinstall
```

### Windows

```bat
mkdir _cmake_build && cd _cmake_build
cmake -G "NMake Makefiles" ..
nmake
cd ..
python setup.py bdist_wheel
pip install dist\pptk_revived-*.whl
```

## Acknowledgements

Originally developed by [HERE Europe B.V.](https://github.com/heremaps) (Copyright 2011–2018).
This fork is maintained by [Nikolaas Steenbergen](https://github.com/nikste).
