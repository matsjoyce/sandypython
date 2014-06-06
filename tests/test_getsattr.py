import unittest
import sandbox.spec as spec
from sandbox import ActivateSandbox


class TestGetsattr(unittest.TestCase):
    def a(self):
        pass

    def test_getsattr(self):
        f = self.a.__class__
        self.assertEqual(f, spec.getsattr(self.a, "__class__"))
        with ActivateSandbox():
            self.assertEqual(f, spec.getsattr(self.a, "__class__"))
        self.assertEqual(f, spec.getsattr(self.a, "__class__"))
        with self.assertRaises(AttributeError):
            self.assertEqual(f, spec.getsattr(self.a, "_class__"))
