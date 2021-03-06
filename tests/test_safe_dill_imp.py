import unittest
from sandypython.safe_dill import safe_dill
from sandypython.importing import *


class TestSafeDillImp(unittest.TestCase):
    def setUp(self):
        imap = {"default": ["sys", "gc"]}
        safe_dill.set_safe_modules(import_filter_by_name(imap))

    def test_dill_imp(self):
        f = safe_dill._import_module
        f("gc")
        f("sys.modules")
        with self.assertRaises(AttributeError):
            f("gc.gc")
        with self.assertRaises(ImportError):
            f("functools")
        with self.assertRaises(ImportError):
            f("safe_dill.dill.sys")
        self.assertEqual(f("functools", safe=True), None)
        self.assertEqual(f("gc.gc", safe=True), None)

    def tearDown(self):
        safe_dill.set_safe_modules(None)
