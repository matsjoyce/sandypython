from .dill_helper import save, load, set_getsattr, unset_getsattr
from .safe_dill import set_safe_modules, init
from .dill import loads, dumps, _trace as debug, register, copy, \
    PicklingError, UnpicklingError

init()

__all__ = ["save", "load", "set_safe_modules", "loads", "dumps", "debug",
           "register", "copy", "PicklingError", "UnpicklingError"]

from sandypython.spec import getsattr
dill.getsattr = getsattr

