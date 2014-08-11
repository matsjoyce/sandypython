import unittest
import sandypython
from sandypython import *


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
        imap = {"default": ["a_mod", "__sand__"]}
        safe_dill.set_safe_modules(importing.import_filter_by_name(imap))

    def setup_globs(self):
        safe_dill.sandy_func_list = {}
        core.add_default_builtins()
        core.add_to_exec_globals("load",
                                 safe_dill.load)
        core.add_to_exec_globals("save",
                                 safe_dill.save)
        imap = {"default": ["a_mod", "__sand__"]}
        core.add_builtin("__import__",
                         importing.checked_importer(
                             importing.import_filter_by_name(imap)),
                         check_protected=False)
        core.clean_exec_globals()
        safe_dill.make_sandy_func_list(force=True)
        print(safe_dill.sandy_func_list)

    def test_save_load(self):
        self.setup_globs()
        with utils.ActivateSandbox():
            core.exec_str(prog)

            with utils.DeactivateSandbox():
                core.clean_exec_globals()
                self.setup_globs()

            core.exec_str(prog2)
            try:
                self.setUp.__globals__
            except:
                pass
            else:
                self.fail()

        self.assertEqual(core.exec_globals["c"], 5)
        self.assertEqual(core.exec_globals["a_mod"].a, 120)
        self.assertEqual(core.exec_globals["__sand__"].a,
                         core.exec_globals["a"])

    def tearDown(self):
        core.reset()


if __name__ == "__main__":
    tsl = TestSaveLoad()
    tsl.setUp()
    tsl.test_save_load()
    tsl.tearDown()
