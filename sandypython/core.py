import sys
from . import spec
from .fakemod import make_fake_mod

__all__ = ["restrict", "allow", "replace", "allow_builtin", "allow_defaults",
           "replace_builtin", "add_to_exec_globals", "start_sandbox",
           "end_sandbox", "exec_str", "detamper_builtins", "on_start",
           "on_end", "reset"]

builtins_copy = __builtins__.copy()
restricted = {}
replaced = {}
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


def restrict(module, name):
    restricted[(module, name)] = None


def allow(module, name):
    if (module, name) in restricted:
        del restricted[(module, name)]


def replace(module, name, obj):
    replaced[(module, name)] = obj
    restrict(module, name)

for i in __builtins__:
    restrict("builtins", i)


def allow_builtin(name):
    allow("builtins", name)


def allow_defaults():
    for i in default_allow:
        allow_builtin(i)


def replace_builtin(name, obj):
    replace("builtins", name, obj)


def save_restricted():
    for module, name in restricted:
        restricted[(module, name)] = getattr(sys.modules[module], name)
        delattr(sys.modules[module], name)


def restore_restricted():
    for stuff, obj in restricted.items():
        module, name = stuff
        setattr(sys.modules[module], name, obj)


def replace_restricted():
    for stuff, obj in replaced.items():
        module, name = stuff
        setattr(sys.modules[module], name, obj)


def clean_exec_globals():
    global exec_globals, exec_mod
    exec_globals = {}
    exec_globals["__builtins__"] = __builtins__
    exec_globals["__name__"] = env_name
    exec_mod = make_fake_mod(exec_globals)
    sys.modules[env_name] = exec_mod
    exec_globals[env_name] = sys.modules[env_name]

clean_exec_globals()


def add_to_exec_globals(name, obj):
    exec_globals[name] = obj
    added_to_execgs.append(name)


def start_sandbox():
    global started
    if not started:
        for i in _on_start:
            i()
        spec.remove_dangerous_attrs()
        save_restricted()
        replace_restricted()
        started = True


def end_sandbox():
    global started
    if started:
        restore_restricted()
        spec.replace_dangerous_attrs()
        for i in _on_end:
            i()
        started = False


def exec_str(code_str):
    start_sandbox()
    find_builtin("exec")(code_str, exec_globals)

str_string = "str"
builtins_str = "__builtins__"


def detamper_builtins(force=False):
    if started or force:
        __builtins__[str_string] = builtins_copy[str_string]
        for i, j in list(__builtins__.items()):
            if i not in builtins_copy or ("builtins", i) in restricted \
               and ("builtins", i) not in replaced:
                del __builtins__[i]
            elif builtins_copy[i] is not j:
                if ("builtins", i) in replaced:
                    if replaced[("builtins", i)] is not j:
                        __builtins__[i] = replaced[("builtins", i)]
                else:
                    __builtins__[i] = builtins_copy[i]


def find_builtin(name):
    return builtins_copy[name]


def on_start(f):
    _on_start.append(f)


def on_end(f):
    _on_end.append(f)


def reset():
    global restricted, replaced, _on_start, _on_end
    restricted = {}
    replaced = {}
    _on_start = []
    _on_end = []
    for i in __builtins__:
        restrict("builtins", i)
    clean_exec_globals()
