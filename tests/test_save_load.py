import unittest
import sandbox
import safe_dill

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

prog = """
import a_mod
from a_mod import b
a_mod.a = 120
a=1
b=2
c=a+b
d={}
save()"""

prog2 = """
load()
c += 2
"""


class TestSaveLoad(unittest.TestCase):
    def setUp(self):
        for i in allowed:
            sandbox.allow_builtin(i)
        safe_dill.set_safe_modules(["a_mod", "__sand__"])

    def setup_globs(self):
        sandbox.add_to_exec_globals("load", safe_dill.load)
        sandbox.add_to_exec_globals("save", safe_dill.save)
        imap = {"default": ["a_mod", "__sand__"]}
        sandbox.replace_builtin("__import__", sandbox.checked_importer(imap))

    def test_save_load(self):
        self.setup_globs()
        with sandbox.ActivateSandbox():
            sandbox.exec_str(prog)

            with sandbox.DeactivateSandbox():
                sandbox.clean_exec_globals()
                self.setup_globs()

            sandbox.exec_str(prog2)
            try:
                self.setUp.__globals__
            except:
                pass
            else:
                self.fail()

        self.assertEqual(sandbox.core.exec_globals["c"], 5)
        self.assertEqual(sandbox.core.exec_globals["a_mod"].a, 120)
        self.assertEqual(sandbox.core.exec_globals["__sand__"].a,
                         sandbox.core.exec_globals["a"])
