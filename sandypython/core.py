import sys
from . import spec
from .fakemod import make_fake_mod
from .proxy import make_proxy

__all__ = ["restrict", "allow", "replace", "allow_builtin", "allow_defaults",
           "replace_builtin", "add_to_exec_globals", "start_sandbox",
           "end_sandbox", "exec_str", "detamper_builtins", "on_start",
           "on_end", "reset"]

restricted = {}
replaced = {}
begin_globals = {}
exec_globals = {}
exec_mod = None
added_to_execgs = []
started = False
env_name = "__sand__"

default_allow = ["ArithmeticError", "AssertionError", "AttributeError",
                 "BaseException", "BlockingIOError", "BrokenPipeError",
                 "BufferError", "BytesWarning", "ChildProcessError",
                 "ConnectionAbortedError", "ConnectionError",
                 "ConnectionRefusedError", "ConnectionResetError",
                 "DeprecationWarning", "EOFError", "Ellipsis",
                 "EnvironmentError", "Exception", "False", "FileExistsError",
                 "FileNotFoundError", "FloatingPointError", "FutureWarning",
                 "GeneratorExit", "IOError", "ImportError", "ImportWarning",
                 "IndentationError", "IndexError", "InterruptedError",
                 "IsADirectoryError", "KeyError", "KeyboardInterrupt",
                 "LookupError", "MemoryError", "NameError", "None",
                 "NotADirectoryError", "NotImplemented", "NotImplementedError",
                 "OSError", "OverflowError", "PendingDeprecationWarning",
                 "PermissionError", "ProcessLookupError", "ReferenceError",
                 "ResourceWarning", "RuntimeError", "RuntimeWarning",
                 "StopIteration", "SyntaxError", "SyntaxWarning",
                 "SystemError", "SystemExit", "TabError", "TimeoutError",
                 "True", "TypeError", "UnboundLocalError",
                 "UnicodeDecodeError", "UnicodeEncodeError", "UnicodeError",
                 "UnicodeTranslateError", "UnicodeWarning", "UserWarning",
                 "ValueError", "Warning", "ZeroDivisionError",
                 "__build_class__", "__debug__", "__doc__", "__name__",
                 "__package__", "abs", "all", "any", "ascii", "bin", "bool",
                 "bytearray", "bytes", "callable", "chr", "classmethod",
                 "complex", "delattr", "dict", "dir", "divmod", "enumerate",
                 "filter", "float", "format", "frozenset", "getattr",
                 "globals", "hasattr", "hash", "hex", "id", "int",
                 "isinstance", "issubclass", "iter", "len", "list", "locals",
                 "map", "max", "min", "next", "object", "oct", "ord", "pow",
                 "property", "range", "repr", "reversed", "round", "set",
                 "setattr", "slice", "sorted", "staticmethod", "str", "sum",
                 "super", "tuple", "type", "vars", "zip"]

_on_start = []
_on_end = []

sys.setrecursionlimit(500)


def add_to_exec_globals(name, obj):
    """
    Adds an object which can be accessed by the sandboxed code as a global.
    """
    begin_globals[name] = make_proxy(obj)
    added_to_execgs.append(name)


def get_from_exec_globals(name):
    """
    Gets an object which can be accessed by the sandboxed code as a global.
    """
    return begin_globals[name]


def add_builtin(name, obj=None):
    """
    Equivalent to :func:`allow`, with `module` being `builtins`

    Example::

        allow_builtin("type")
    """
    if obj is None:
        obj = __builtins__[name]
    if "__builtins__" not in begin_globals:
        add_to_exec_globals("__builtins__", {})
    get_from_exec_globals("__builtins__")[name] = make_proxy(obj)


def add_default_builtins():
    """
    Allow a default list of builtins that are considered to be safe
    """
    for i in default_allow:
        add_builtin(i)


def clean_exec_globals():
    global exec_globals, exec_mod
    exec_globals = begin_globals.copy()
    exec_globals["__name__"] = env_name
    exec_mod = make_fake_mod(exec_globals)
    sys.modules[env_name] = exec_mod
    exec_globals[env_name] = sys.modules[env_name]


def start_sandbox():
    """
    Start desertification! Causes great heat, and destroys all unadapted
    programs

    If the sandbox has not been started, start it. This function removes all
    special attributes, restricted module members, and does module member
    replacements.

    Also see :class:`sandypython.utils.ActivateSandbox`
    """
    global started
    if not started:
        if exec_globals == {}:
            clean_exec_globals()
        for i in _on_start:
            i()
        spec.remove_dangerous_attrs()
        # save_restricted()
        # replace_restricted()
        started = True


def end_sandbox():
    """
    Bring the rain! Effect -> desert to temperate climate, suitable for
    average python programs

    If the sandbox has been started, revert the interpreter state back to
    that before :func:`start_sandbox` was called.

    Also see :class:`sandypython.utils.DeactivateSandbox`
    """
    global started
    if started:
        # restore_restricted()
        spec.replace_dangerous_attrs()
        for i in _on_end:
            i()
        started = False


def exec_str(code_str):
    """
    Executes `code_str` under the sandbox. :func:`start_sandbox` is called
    before executing the string.
    """
    start_sandbox()
    find_builtin("exec")(code_str, exec_globals)


def find_builtin(name):
    return __builtins__[name]


def on_start(f):
    """
    Add a function to be called before the sandbox starts.
    """
    _on_start.append(f)


def on_end(f):
    """
    Add a function to be called once the sandbox ends.
    """
    _on_end.append(f)


def reset():
    """
    Resets the state of the sandbox, so that new code can be run without the
    effects of the old code.
    """
    global restricted, replaced, _on_start, _on_end
    restricted = {}
    replaced = {}
    _on_start = []
    _on_end = []
    clean_exec_globals()
