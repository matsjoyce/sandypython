from .dill_helper import save, load, set_getsattr, unset_getsattr
from .safe_dill import set_safe_modules, init
from .dill import loads, dumps, _trace as debug

init()

__all__ = ["save", "load", "set_safe_modules", "loads", "dumps", "debug"]

from sandbox import on_start, on_end
on_start(set_getsattr)
on_end(unset_getsattr)
