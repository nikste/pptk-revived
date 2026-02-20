# pptk-revived - Point Processing Toolkit

This is a fork of [heremaps/pptk](https://github.com/heremaps/pptk) maintained by [Nikolaas Steenbergen](https://github.com/nikste), updated to build and run on modern Python (3.12+) and CMake (3.28+).

Source: https://github.com/nikste/pptk_revived

Copyright (C) 2011-2018 HERE Europe B.V.

The Point Processing Toolkit (pptk) is a Python package for visualizing and processing 2-d/3-d point clouds.

At present, pptk consists of the following features.

* A 3-d point cloud viewer that
  - accepts any 3-column numpy array as input,
  - renders tens of millions of points interactively using an octree-based level of detail mechanism,
  - supports point selection for inspecting and annotating point data.
* A fully parallelized point k-d tree that supports k-nearest neighbor queries and r-near range queries
  (both build and queries have been parallelized).
* A normal estimation routine based on principal component analysis of point cloud neighborhoods.

[Homepage](https://heremaps.github.io/pptk/index.html)

![pptk screenshots](/docs/source/tutorials/viewer/images/tutorial_banner.png)

The screenshots above show various point datasets visualized using pptk.
The `bildstein1` Lidar point cloud from Semantic3D (left),
Beijing GPS trajectories from Geolife (middle left),
`DistrictofColumbia.geojson` 2-d polygons from US building footprints (middle right),
and a Mobius strip (right).
For details, see the [tutorials](https://heremaps.github.io/pptk/tutorial.html).

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
```

Set point size to 0.01.

```python
v.set(point_size=0.01)
```

For more advanced examples, see [tutorials](https://heremaps.github.io/pptk/tutorial.html).

## Build

### Requirements

* [Python](https://www.python.org/) 3.8+
* [Qt5](https://www.qt.io/)
* [TBB](https://github.com/oneapi-src/oneTBB) (libtbb-dev)
* [Eigen](http://eigen.tuxfamily.org) 3.x (libeigen3-dev)
* [Numpy](http://www.numpy.org/)
* CMake 3.5+
* patchelf (Linux only)

On Ubuntu/Debian, install dependencies with:

```bash
sudo apt install build-essential cmake patchelf libtbb-dev libeigen3-dev qtbase5-dev libqt5opengl5-dev
pip install numpy
```

### Linux / Mac

```bash
# Create a venv (optional but recommended)
python3 -m venv venv && source venv/bin/activate
pip install numpy

# Configure and build
mkdir build && cd build
cmake ..
make -j$(nproc)

# Package and install
python setup.py bdist_wheel
pip install dist/pptk_revived-*.whl --force-reinstall
```

### Windows

```
mkdir build && cd build
cmake -G "NMake Makefiles" ..
nmake
python setup.py bdist_wheel
pip install dist\pptk_revived-*.whl
```
