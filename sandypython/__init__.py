import sys

if sys.version_info[0] < 3:
    raise RuntimeError("SandyPython only works for python 3")

import warnings

if sys.version_info.minor < 4:
    warnings.warn("SandyPython has only been tested for python 3.4")

from . import core, utils, spec, safe_dill

utils.clean_module(core)
utils.clean_module(utils)
utils.clean_module(spec)
utils.clean_module(safe_dill)

del __spec__
del __loader__
