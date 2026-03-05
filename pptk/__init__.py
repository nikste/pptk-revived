from . import _add_path
from .viewer.viewer import *
from .points.points import *
from .points.expr import *
from .kdtree import kdtree
from .processing.estimate_normals.estimate_normals import estimate_normals

from .dimreduce import reduce_dims
from .colors import label_to_colors
from .ply import load_ply

__version__ = '0.1.1'

connect = viewer.connect


def set(*args, **kwargs):
    """Module-level set() is not supported (issue #64).

    You need a viewer instance first::

        v = pptk.viewer(xyz)
        v.set(point_size=0.01)   # correct

    """
    raise AttributeError(
        "pptk.set() is not a module-level function. "
        "Create a viewer first and call set() on it:\n"
        "    v = pptk.viewer(xyz)\n"
        "    v.set(point_size=0.01)"
    )
