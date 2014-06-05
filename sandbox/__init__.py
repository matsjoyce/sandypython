from .core import restrict, allow, replace, allow_builtin, replace_builtin,\
    clean_exec_globals, add_to_exec_globals, start_sandbox,\
    end_sandbox, exec_str, detamper_builtins, find_builtin
from .utils import DeactivateSandbox, check_builtins, type_checker,\
    checked_importer, clean_module

__all__ = ["restrict", "allow", "replace", "allow_builtin", "replace_builtin",
           "clean_exec_globals", "add_to_exec_globals", "start_sandbox",
           "end_sandbox", "exec_str", "detamper_builtins", "find_builtin",
           "DeactivateSandbox", "check_builtins", "type_checker",
           "checked_importer", "clean_module"]

from . import core, utils

clean_module(core)
clean_module(utils)
del __spec__
del __loader__
