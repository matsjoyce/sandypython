import unittest
import sandbox

allowed = ["ArithmeticError", "AssertionError", "AttributeError",
           "BaseException", "BlockingIOError", "BrokenPipeError",
           "BufferError", "BytesWarning", "ChildProcessError",
           "ConnectionAbortedError", "ConnectionError",
           "ConnectionRefusedError", "ConnectionResetError",
           "DeprecationWarning", "EOFError", "Ellipsis",
           "EnvironmentError", "Exception", "False", "FileExistsError",
           "FileNotFoundError", "FloatingPointError", "FutureWarning",
           "GeneratorExit", "IOError", "ImportError", "ImportWarning",
           "IndentationError", "IndexError", "InterruptedError",
           "IsADirectoryError", "KeyError", "KeyboardInterrupt", "LookupError",
           "MemoryError", "NameError", "None", "NotADirectoryError",
           "NotImplemented", "NotImplementedError", "OSError", "OverflowError",
           "PendingDeprecationWarning", "PermissionError",
           "ProcessLookupError", "ReferenceError", "ResourceWarning",
           "RuntimeError", "RuntimeWarning", "StopIteration", "SyntaxError",
           "SyntaxWarning", "SystemError", "SystemExit", "TabError",
           "TimeoutError", "True", "TypeError", "UnboundLocalError",
           "UnicodeDecodeError", "UnicodeEncodeError", "UnicodeError",
           "UnicodeTranslateError", "UnicodeWarning", "UserWarning",
           "ValueError", "Warning", "ZeroDivisionError", "__build_class__",
           "__debug__", "__doc__", "__name__", "__package__",
           "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes",
           "callable", "chr", "classmethod", "complex",
           "delattr", "dict", "dir", "divmod", "enumerate", "filter", "float",
           "format", "frozenset", "getattr", "globals", "hasattr", "hash",
           "hex", "id", "int", "isinstance", "issubclass", "iter", "len",
           "list", "locals", "map", "max", "min", "next", "object",
           "oct", "ord", "pow", "property", "range", "repr", "reversed",
           "round", "set", "setattr", "slice", "sorted", "staticmethod", "str",
           "sum", "super", "tuple", "type", "vars", "zip"]


class TestAttrRm(unittest.TestCase):
    def setUp(self):
        for i in allowed:
            sandbox.allow_builtin(i)

    def test_func_globals(self):
        sandbox.spec.stats()
        with self.assertRaises(AttributeError):
            with sandbox.ActivateSandbox():
                self.setUp.__globals__

    def test_all(self):
        with sandbox.ActivateSandbox():
            pass
        for type, attr in sandbox.spec.saved:
            with self.subTest(type=type, attr=attr):
                with self.assertRaises(AttributeError):
                    with sandbox.ActivateSandbox():
                        getattr(type, attr)
