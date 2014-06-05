import sandbox
import safe_dill
import sys
import os

sys.path.insert(0, "./badcode")

allow = ['ArithmeticError', 'AssertionError', 'AttributeError',
         'BaseException', 'BlockingIOError', 'BrokenPipeError',
         'BufferError', 'BytesWarning', 'ChildProcessError',
         'ConnectionAbortedError', 'ConnectionError', 'ConnectionRefusedError',
         'ConnectionResetError', 'DeprecationWarning', 'EOFError', 'Ellipsis',
         'EnvironmentError', 'Exception', 'False', 'FileExistsError',
         'FileNotFoundError', 'FloatingPointError', 'FutureWarning',
         'GeneratorExit', 'IOError', 'ImportError', 'ImportWarning',
         'IndentationError', 'IndexError', 'InterruptedError',
         'IsADirectoryError', 'KeyError', 'KeyboardInterrupt', 'LookupError',
         'MemoryError', 'NameError', 'None', 'NotADirectoryError',
         'NotImplemented', 'NotImplementedError', 'OSError', 'OverflowError',
         'PendingDeprecationWarning', 'PermissionError', 'ProcessLookupError',
         'ReferenceError', 'ResourceWarning', 'RuntimeError', 'RuntimeWarning',
         'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError',
         'SystemExit', 'TabError', 'TimeoutError', 'True', 'TypeError',
         'UnboundLocalError', 'UnicodeDecodeError', 'UnicodeEncodeError',
         'UnicodeError', 'UnicodeTranslateError', 'UnicodeWarning',
         'UserWarning', 'ValueError', 'Warning', 'ZeroDivisionError',
         '__build_class__', '__debug__', '__doc__', '__name__', '__package__',
         'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
         'callable', 'chr', 'classmethod', 'complex',
         'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'filter', 'float',
         'format', 'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'hex',
         'id', 'int', 'isinstance', 'issubclass', 'iter', 'len',
         'list', 'locals', 'map', 'max', 'min', 'next', 'object',
         'oct', 'ord', 'pow', 'property', 'range', 'repr', 'reversed', 'round',
         'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum',
         'super', 'tuple', 'type', 'vars', 'zip']


@sandbox.check_builtins
def prnt():
    with sandbox.DeactivateSandbox():
        import sys
        print(sys.version)
        print("Hello from free, unsecure, non-sandboxed code!")
        print("getme.txt ==>", "'%s'" % open("getme.txt").read())


@sandbox.check_builtins
def printer(*args, **kwargs):
    s = " ".join([str(i) for i in args])
    kwargs["flush"] = True
    sandbox.find_builtin("print")(s, **kwargs)


cols = {i: j for i, j in zip(("black", "red", "green", "yellow", "blue",
                              "magenta", "cyan", "white"), range(30, 38))}


@sandbox.check_builtins
def colorfy(*args, color="green"):
    return "\033[1;{color}m{msg}\033[1;m".format(msg=" ".join(
        [str(i)for i in args]), color=cols[color])


@sandbox.type_checker(a=(int, dict, list, None), b=str, c=str)
def h(a, b, c=""):
    return str(a) + b + c


def loads(s):
    return safe_dill.loads(s)

for i in allow:
    sandbox.allow_builtin(i)

imp_map = {"default": ["a_mod", "bad_module"]}
bad_code = open("badcode/bad_code%s.py" % sys.argv[1]).read()

sandbox.add_to_exec_globals("prnt", prnt)
sandbox.add_to_exec_globals("h", h)
sandbox.add_to_exec_globals("colorfy", colorfy)
sandbox.add_to_exec_globals("save", safe_dill.save)
sandbox.add_to_exec_globals("load", safe_dill.load)
sandbox.add_to_exec_globals("loads", loads)
safe_dill.set_safe_modules(imp_map["default"])
sandbox.replace_builtin("__import__", sandbox.checked_importer(imp_map))
sandbox.replace_builtin("print", printer)
sandbox.start_sandbox()
sandbox.exec_str(bad_code)
sandbox.end_sandbox()
