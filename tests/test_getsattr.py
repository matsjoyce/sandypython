import unittest
from sandypython.spec import getsattr
from sandypython.core import add_default_builtins, reset
from sandypython.utils import ActivateSandbox


class TestGetsattr(unittest.TestCase):
    def setUp(self):
        add_default_builtins()

    def test_getsattr(self):
        f = self.setUp.__class__
        with ActivateSandbox():
            x = getsattr(self.setUp, "__class__")
        self.assertEqual(f, x)
        self.assertEqual(f, getsattr(self.setUp, "__class__"))
        with self.assertRaises(AttributeError):
            self.assertEqual(f, getsattr(self.setUp, "_class__"))

    def tearDown(self):
        reset()
