from .dill_helper import save, load
from .safe_dill import set_safe_modules, init
from .dill import loads, dumps, _trace as debug

init()

__all__ = ["save", "load", "set_safe_modules", "loads", "dumps", "debug"]
