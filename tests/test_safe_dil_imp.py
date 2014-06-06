import unittest
from safe_dill import safe_dill


class TestSafeDillImp(unittest.TestCase):
    def setUp(self):
        safe_dill.set_safe_modules(["os", "sys"])

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

    def tearDown(self):
        safe_dill.set_safe_modules([])
