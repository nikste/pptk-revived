from . import _add_path
from .viewer.viewer import *
from .points.points import *
from .points.expr import *
from .kdtree import kdtree
from .processing.estimate_normals.estimate_normals import estimate_normals

from .dimreduce import reduce_dims
from .colors import label_to_colors

__version__ = '0.1.1'
