import unittest
import sys
from sandypython.importing import *
from sandypython.core import add_builtin


class TestControlledImporter(unittest.TestCase):
    def test_controlled_importer_noise(self):
        imap = {"default": ["sys"],
                __file__: ["gc"]
                }
        f = checked_importer(import_filter_by_name(imap), noise=True)
        add_builtin("__import__", f, check_protected=False)
        f("sys")
        f("gc")
        with self.assertRaises(ImportError):
            f("functools")

    def test_controlled_importer(self):
        imap = {"default": ["./tests/a_mod*"],
                __file__: ["./tests/*.py"]
                }
        f = checked_importer(import_filter_by_path(imap))
        add_builtin("__import__", f, check_protected=False)
        f("a_mod")
        f("b_mod")
        with self.assertRaises(ImportError):
            f("sys")
        with self.assertRaises(ImportError):
            f("kivy")
