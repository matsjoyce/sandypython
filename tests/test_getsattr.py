import unittest
from sandypython.spec import getsattr
from sandypython.core import add_default_builtins, reset
from sandypython.utils import ActivateSandbox


class TestGetsattr(unittest.TestCase):
    def setUp(self):
        add_default_builtins()

    def test_getsattr(self):
        def f():
            pass
        F = f.__class__
        with ActivateSandbox():
            x = getsattr(f, "__class__")
        self.assertEqual(F, x)
        self.assertEqual(F, getsattr(f, "__class__"))
        with self.assertRaises(AttributeError):
            self.assertEqual(F, getsattr(f, "_class__"))
        with ActivateSandbox():
            print(type(f).__dict__)
            x = getsattr(f, "__code__")
        self.assertEqual(f.__code__, x)

    def tearDown(self):
        reset()

tg = TestGetsattr()
tg.setUp()
tg.test_getsattr()
