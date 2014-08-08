import unittest
import sandypython
from sandypython import safe_dill
from sandypython.importing import *


prog = """
import a_mod
from a_mod import b
a_mod.a = 120
#print(globals())
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
        imap = {"default": ["a_mod", "__sand__"]}
        safe_dill.set_safe_modules(import_filter_by_name(imap))

    def setup_globs(self):
        sandypython.core.add_default_builtins()
        sandypython.core.add_to_exec_globals("load",
                                             sandypython.safe_dill.load,
                                             check_protected=False)
        sandypython.core.add_to_exec_globals("save",
                                             sandypython.safe_dill.save,
                                             check_protected=False)
        imap = {"default": ["a_mod", "__sand__"]}
        sandypython.core.add_builtin("__import__",
                                     sandypython.importing.checked_importer(
                                         import_filter_by_name(imap)),
                                     check_protected=False)
        sandypython.core.clean_exec_globals()

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
