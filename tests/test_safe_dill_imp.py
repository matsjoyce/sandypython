import unittest
from sandypython.safe_dill import safe_dill
from sandypython.utils import *


class TestSafeDillImp(unittest.TestCase):
    def setUp(self):
        imap = {"default": ["sys", "os"]}
        safe_dill.set_safe_modules(import_filter_by_name(imap))

    def test_dill_imp(self):
        f = safe_dill._import_module
        f("os")
        f("sys.modules")
        with self.assertRaises(AttributeError):
            f("os.os")
        with self.assertRaises(ImportError):
            f("functools")
        with self.assertRaises(ImportError):
            f("safe_dill.dill.sys")
        self.assertEqual(f("functools", safe=True), None)
        self.assertEqual(f("os.os", safe=True), None)

    def tearDown(self):
        safe_dill.set_safe_modules(None)
