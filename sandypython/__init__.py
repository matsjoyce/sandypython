from . import core, utils, spec, safe_dill

utils.clean_module(core)
utils.clean_module(utils)
utils.clean_module(spec)
utils.clean_module(safe_dill)

del __spec__
del __loader__
