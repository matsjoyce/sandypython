import unittest
import sandypython
from sandypython import safe_dill
from sandypython.utils import *


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
        sandypython.core.allow_defaults()
        imap = {"default": ["a_mod", "__sand__"]}
        safe_dill.set_safe_modules(import_filter_by_name(imap))

    def setup_globs(self):
        sandypython.core.add_to_exec_globals("load",
                                             sandypython.safe_dill.load)
        sandypython.core.add_to_exec_globals("save",
                                             sandypython.safe_dill.save)
        imap = {"default": ["a_mod", "__sand__"]}
        sandypython.core.replace_builtin("__import__",
                                         sandypython.utils.checked_importer(
                                             import_filter_by_name(imap)))

    def test_save_load(self):
        self.setup_globs()
        with sandypython.utils.ActivateSandbox():
            sandypython.core.exec_str(prog)

            with sandypython.utils.DeactivateSandbox():
                sandypython.core.clean_exec_globals()
                self.setup_globs()

            sandypython.core.exec_str(prog2)
            try:
                self.setUp.__globals__
            except:
                pass
            else:
                self.fail()

        self.assertEqual(sandypython.core.exec_globals["c"], 5)
        self.assertEqual(sandypython.core.exec_globals["a_mod"].a, 120)
        self.assertEqual(sandypython.core.exec_globals["__sand__"].a,
                         sandypython.core.exec_globals["a"])

    def tearDown(self):
        sandypython.core.reset()
